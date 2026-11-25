"""ORM model of the sessions table (ddd.md 4.1.3). The login logic is in app/auth.py."""
from datetime import datetime

from sqlalchemy import CHAR, TIMESTAMP, ForeignKey, Index, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SessionRow(Base):
    """ORM model for the sessions table (ddd.md 4.1.3)."""

    __tablename__ = "sessions"
    __table_args__ = (
        UniqueConstraint("token_hash", name="uq_sessions_token_hash"),
        Index("ix_sessions_user_id", "user_id"),
        Index("ix_sessions_expires_at", "expires_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", name="fk_sessions_user_id", ondelete="CASCADE"))
    token_hash: Mapped[str] = mapped_column(CHAR(64))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(), server_default=text("CURRENT_TIMESTAMP"))
    expires_at: Mapped[datetime] = mapped_column(TIMESTAMP())
    last_seen_at: Mapped[datetime] = mapped_column(TIMESTAMP(), server_default=text("CURRENT_TIMESTAMP"))
    user_agent: Mapped[str | None] = mapped_column(String(200))
