import uuid
from datetime import datetime, timezone, timedelta

from sqlalchemy import (
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.async_db import Base


class IdempotencyRecord(Base):
    __tablename__="idempotency_records"

    __table_args__=(
        UniqueConstraint(
            "idempotency_key",
            name="uq_idempotency_key",
        )
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    idempotency_key: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True
    )

    request_hash: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    payment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payments.id"),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="PROCESSING",
    )

    response_payload: Mapped[dict | None] = mapped_column(
        String,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc) + timedelta(hours=24),
        nullable=False,
        index=True,
    )