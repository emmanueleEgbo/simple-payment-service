from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.async_db import get_db
from app.schemas.payment import CreatePaymentRequest
from app.services.payment_service import (
    PaymentService,
    IdempotencyConflictError,
)

v1_router = APIRouter(prefix="/v1", tags=["Payments"],)


payment_service = PaymentService()


@v1_router.post("/payments")
async def create_payment(
    payload: CreatePaymentRequest,
    db: AsyncSession =  Depends(get_db),
    idempotent_key: str = Header(..., alias="Idempotency-Key"),
):
    pass