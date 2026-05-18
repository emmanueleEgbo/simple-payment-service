from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Payment
from app.models.idempotency_record import IdempotencyRecord
from app.schemas.payment import CreatePaymentRequest
from app.core.idempotency_utility import generate_request_hash


class IdempotencyConflictError(Exception):
    pass


class PaymentService:

    async def create_payment(
        self,
        db: AsyncSession,
        payload: CreatePaymentRequest,
        idempotency_key: str,
    ):
        pass