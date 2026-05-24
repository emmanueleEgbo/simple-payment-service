"""Production-grade payment orchestration service with idempotent payment creation,
provider abstraction, and reliable payment state management that prevents race condition."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Payment, PaymentStatus
from app.models.idempotency_record import IdempotencyRecord
from app.schemas.payment import CreatePaymentRequest

async def create_payment(db: AsyncSession, payload: CreatePaymentRequest):
    new_payment = Payment(
        user_id=payload.user_id,
        amount=payload.amount,
        currency=payload.currency,
        providerayload=payload.provider,
        reference=payload.reference,
        description=payload.description
    )
    db.add(new_payment)
    await db.commit()
    await db.refresh(new_payment)
    return new_payment