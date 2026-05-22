from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from app.models.payment import PaymentStatus


class CreatePaymentRequest(BaseModel):
    user_id: str
    amount: int = Field(gt=0)
    currency: str
    provider: str
    reference: str | None   = None
    description: str | None = None


class PaymentResponse(BaseModel):
    id: UUID
    user_id: str
    amount: int
    currency: str
    status: PaymentStatus
    provider: str
    reference: str | None = None
    description: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )