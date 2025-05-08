import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Token(Base):
    __tablename__ = "jwt_token"

    jti: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[int] = mapped_column(index=True, nullable=False)
    fp: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)

    __table_args__ = (
        Index("ix_token_user_alive", "user_id", "revoked", "expires_at"),
    )
