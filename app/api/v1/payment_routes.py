from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.async_db import get_db
from app.schemas.payment import (
    CreatePaymentRequest, 
    PaymentResponse,
)
from app.services.payment_service import (
    PaymentService,
    IdempotencyConflictError,
    IdempotencyInProgressError,
)

v1_router = APIRouter(prefix="/v1", tags=["Payments"],)


payment_service = PaymentService()


@v1_router.post("/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payload: CreatePaymentRequest,
    db: AsyncSession =  Depends(get_db),
    idempotent_key: str = Header(..., alias="Idempotency-Key"),
):
    """
    Create a new payment in an idempotent and race-condition-safe manner.

    Repeated requests with the same Idempotency-Key and identical payload
    will return the original response without creating duplicate payments.
    """
    try:
        return await payment_service.create_payment(
            db=db,
            payload=payload,
            idempotency_key=idempotent_key,
        )
    
    except IdempotencyConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )