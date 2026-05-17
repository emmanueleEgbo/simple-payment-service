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

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )