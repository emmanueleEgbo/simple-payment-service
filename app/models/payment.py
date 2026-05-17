"""Defines the SQLAlchemy ORM model representing a Payment entity."""

import uuid
import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.async_db import Base


# Payment status enum
class PaymentStatus(str, enum.Enum):
    PENDING          = "PENDING"
    PROCESSING       = "PROCESSING"
    SUCCESS          = "SUCCESS"
    FAILED           = "FAILED"
    REQUIRES_ACTION  = "REQUIRES_ACTION"
    CANCELLED        = "CANCELLED"

class Payment(Base):
    __tablename__="payments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # Ownership
    user_id: Mapped[str] = mapped_column(String, nullable=False)

    # Money (minor units: cents/pence)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)

    # State machine
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus),
        default=PaymentStatus.PENDING,
        nullable=False
    )

    # Provider routing (stripe, etc.)
    provider: Mapped[str] = mapped_column(String, nullable=False)

    # Idempotency protection
    idempotency_key: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

