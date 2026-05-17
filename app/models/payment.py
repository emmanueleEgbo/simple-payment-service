"""Defines the SQLAlchemy ORM model representing a Payment entity."""

import uuid
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from app.core.async_db import Base


# Payment status enum


class Payment(Base):
    __tablename__="payments"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )