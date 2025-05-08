from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


if TYPE_CHECKING:
    from .user import User


class Note(Base):
    __tablename__ = "note"

    note_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now(UTC), onupdate=datetime.now(UTC)
    )

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.user_id"), nullable=False
    )
    user: Mapped["User"] = relationship("User", back_populates="notes")
