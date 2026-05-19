from pydantic import BaseModel, Field


class CreatePaymentRequest(BaseModel):
    user_id: str
    amount: int = Field(gt=0)
    currency: str
    provider: str
    reference: str | None   = None
    description: str | None = None


class PaymentResponse(BaseModel):
    pass