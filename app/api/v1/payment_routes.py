from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.async_db import get_db
from app.schemas.payment import (
    CreatePaymentRequest, 
    PaymentResponse,
)
from app.services.payment_service import create_payment

v1_router = APIRouter(prefix="/v1", tags=["Payments"],)



@v1_router.post("/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_new_payment(
    payload: CreatePaymentRequest,
    db: AsyncSession =  Depends(get_db)
):
    """
    Create a new payment
    """
    try:
        return await create_payment(
            db=db,
            payload=payload
        )
    
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )