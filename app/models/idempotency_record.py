"""Stores idempotency state for safe request deduplication, retry handling,
and race-condition-safe payment processing."""

import uuid
import enum
from datetime import datetime, timezone, timedelta

from sqlalchemy import (
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Enum,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.async_db import Base

class IdempotencyStatus(str, enum.Enum):
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class IdempotencyRecord(Base):
    __tablename__="idempotency_records"

    __table_args__=(
        UniqueConstraint(
            "user_id",
            "idempotency_key",
            name="uq_user_idempotency_key",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True
    )


    idempotency_key: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    request_hash: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    payment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payments.id", ondelete="CASCADE"),
        nullable=True,
    )

    status: Mapped[IdempotencyStatus] = mapped_column(
        Enum(IdempotencyStatus),
        nullable=False,
        default="PROCESSING",
    )

    response_payload: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc) + timedelta(hours=24),
        nullable=False,
        index=True,
    )