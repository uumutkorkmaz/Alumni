from datetime import datetime

from sqlalchemy import TIMESTAMP, ForeignKey, Index, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SavedPosting(Base):
    """ORM model for the saved_postings table (ddd.md 4.1.6): a student or graduate keeps a job
    posting to come back to. One row per (user, posting); both sides are removed with their row."""

    __tablename__ = "saved_postings"
    __table_args__ = (Index("ix_saved_postings_job_posting_id", "job_posting_id"),)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", name="fk_saved_postings_user_id", ondelete="CASCADE"), primary_key=True
    )
    job_posting_id: Mapped[int] = mapped_column(
        ForeignKey("job_postings.id", name="fk_saved_postings_job_posting_id", ondelete="CASCADE"), primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(), server_default=text("CURRENT_TIMESTAMP"))
