"""Production-grade payment orchestration service with idempotent payment creation,
provider abstraction, and reliable payment state management that prevents race condition."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Payment, PaymentStatus
from app.models.idempotency_record import IdempotencyRecord
from app.schemas.payment import CreatePaymentRequest
from app.core.idempotency_utility import generate_request_hash


class IdempotencyConflictError(Exception):
    pass


class IdempotencyInProgressError(Exception):
    pass


class PaymentService:

    async def create_payment(
        self,
        db: AsyncSession,
        payload: CreatePaymentRequest,
        idempotency_key: str,
    ):
        request_hash = generate_request_hash(payload.model_dump())

        # ----------------------------------------------------------
        # Idempotency-first lookup (prevents race duplication)
        # ----------------------------------------------------------
        result = await db.execute(
            select(IdempotencyRecord).where(
                IdempotencyRecord.idempotency_key == idempotency_key
            )
        )
        existing_record = result.scalar_one_or_none()

        # ----------------------------------------------------------
        # Handle replay cases
        # ----------------------------------------------------------
        if existing_record:
            # Check against payload mismatch for same idempotency key 
            if existing_record.request_hash != request_hash:
                raise IdempotencyConflictError(
                    "Idempotency key reused with different payload"
                )
            
            # Request still processing
            if existing_record.status == "PROCESSING":
                raise IdempotencyInProgressError(
                    "payment is already being processed"
                )
            
            # Completed request -> return cached response
            if existing_record.status == "COMPLETED":
                return existing_record.response_payload
        
        # ----------------------------------------------------------
        #  Create new idempotency record + payment atomically
        # ----------------------------------------------------------
        try:
            async with db.begin():

                # Reserve idempotency key
                idem_record = IdempotencyRecord(
                    idempotency_key=idempotency_key,
                    request_hash=request_hash,
                    status="PROCESSING",
                )

                db.add(idem_record)

                await db.flush()

                # Create payment
                payment = Payment(
                    user_id=payload.user_id,
                    amount=payload.amount,
                    currency=payload.currency.upper(),
                    status=PaymentStatus.PENDING,
                    provider=payload.provider,
                    reference=payload.reference,
                    description=payload.description,
                )

                db.add(payment)

                await db.flush()

                response_payload = {
                    "payment_id": str(payment.id),
                    "status": payment.status.value,
                }

                idem_record.payment_id = payment.id
                idem_record.status = "COMPLETED"
                idem_record.response_payload = response_payload
            return response_payload
        
        # ----------------------------------------------------------
        #  Safety net for true race-condition collisions
        # ---------------------------------------------------------- 
        except IntegrityError:
            
            await db.rollback()

            result = await db.execute(
                select(IdempotencyRecord).where(
                    IdempotencyRecord.idempotency_key == idempotency_key
                )
            )

            existing_payment_record = result.scalar_one()

            # Validate request response consistency
            if existing_payment_record.request_hash != request_hash:
                raise IdempotencyConflictError(
                    "Idempotency key reused with different payload"
                )
            
            # Return cached response
            return existing_payment_record.response_payload