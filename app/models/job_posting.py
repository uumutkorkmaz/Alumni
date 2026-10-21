from datetime import date, datetime
from typing import TYPE_CHECKING, Literal

from fastapi import HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import TIMESTAMP, CheckConstraint, ForeignKey, String, Text, func, select, text
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.database.connection import get_engine
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.application import Application
    from app.models.user import User

EmploymentType = Literal["full_time", "part_time", "internship", "contract"]


class JobPosting(Base):
    """ORM model for the job_postings table (ddd.md section 4.3)."""

    __tablename__ = "job_postings"
    __table_args__ = (
        CheckConstraint(
            "employment_type IN ('full_time', 'part_time', 'internship', 'contract')",
            name="ck_job_postings_employment_type",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    company: Mapped[str] = mapped_column(String(150))
    location: Mapped[str] = mapped_column(String(150))
    employment_type: Mapped[str] = mapped_column(String(20))
    description: Mapped[str] = mapped_column(Text())
    application_url: Mapped[str | None] = mapped_column(String(500))
    deadline: Mapped[date | None]
    is_active: Mapped[bool] = mapped_column(server_default=text("TRUE"))
    posted_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", name="fk_job_postings_posted_by_user_id", ondelete="SET NULL"),
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(), server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(), server_default=text("CURRENT_TIMESTAMP"))

    # Many job postings -> one (optional) user.
    posted_by: Mapped["User | None"] = relationship(back_populates="job_postings")

    # One posting -> many applications (see User.applications for the cascade note).
    applications: Mapped[list["Application"]] = relationship(
        back_populates="job_posting", cascade="all, delete-orphan", passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<JobPosting id={self.id} title={self.title!r} company={self.company!r}>"


class JobPostingBase(BaseModel):
    """Fields of a posting that do not say who owns it (used as-is by the nested routes)."""

    title: str = Field(max_length=200)
    company: str = Field(max_length=150)
    location: str = Field(max_length=150)
    employment_type: EmploymentType
    description: str
    application_url: str | None = Field(default=None, max_length=500)
    deadline: date | None = None
    is_active: bool = True


class JobPostingCreate(JobPostingBase):
    """Direct routes: the owner (a user id, or null for a department posting) is part of the body."""

    posted_by_user_id: int | None = None


class JobPostingUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    company: str | None = Field(default=None, max_length=150)
    location: str | None = Field(default=None, max_length=150)
    employment_type: EmploymentType | None = None
    description: str | None = None
    application_url: str | None = Field(default=None, max_length=500)
    deadline: date | None = None
    is_active: bool | None = None
    posted_by_user_id: int | None = None


def _to_dict(posting: JobPosting) -> dict:
    return {
        "id": posting.id,
        "title": posting.title,
        "company": posting.company,
        "location": posting.location,
        "employment_type": posting.employment_type,
        "description": posting.description,
        "application_url": posting.application_url,
        "deadline": posting.deadline.isoformat() if posting.deadline else None,
        "is_active": posting.is_active,
        "posted_by_user_id": posting.posted_by_user_id,
        "created_at": posting.created_at.strftime("%Y-%m-%d %H:%M"),
    }


def _require_user(session: Session, user_id: int) -> None:
    from app.models.user import User

    if session.get(User, user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")


def _find(session: Session, posting_id: int, user_id: int | None = None) -> JobPosting:
    """Find a posting. With user_id (nested routes) a posting owned by someone else counts as missing."""
    posting = session.get(JobPosting, posting_id)
    if posting is None or (user_id is not None and posting.posted_by_user_id != user_id):
        raise HTTPException(status_code=404, detail="Job posting not found")
    return posting


def create_job_posting(data: JobPostingCreate) -> dict:
    with Session(get_engine()) as session:
        if data.posted_by_user_id is not None:
            _require_user(session, data.posted_by_user_id)
        posting = JobPosting(**data.model_dump())
        session.add(posting)
        session.commit()
        session.refresh(posting)
        return _to_dict(posting)


def get_job_postings(user_id: int | None = None) -> list[dict]:
    """All postings, or only the postings of one user (nested route)."""
    with Session(get_engine()) as session:
        if user_id is not None:
            _require_user(session, user_id)
        query = select(JobPosting).order_by(JobPosting.id)
        if user_id is not None:
            query = query.where(JobPosting.posted_by_user_id == user_id)
        return [_to_dict(posting) for posting in session.scalars(query)]


def get_job_posting(posting_id: int, user_id: int | None = None) -> dict:
    with Session(get_engine()) as session:
        if user_id is not None:
            _require_user(session, user_id)
        return _to_dict(_find(session, posting_id, user_id))


def create_job_posting_for_user(user_id: int, data: JobPostingBase) -> dict:
    return create_job_posting(JobPostingCreate(**data.model_dump(), posted_by_user_id=user_id))


def _update(posting_id: int, fields: dict) -> dict:
    with Session(get_engine()) as session:
        posting = _find(session, posting_id)
        if fields.get("posted_by_user_id") is not None:
            _require_user(session, fields["posted_by_user_id"])
        for key, value in fields.items():
            setattr(posting, key, value)
        posting.updated_at = func.current_timestamp()
        session.commit()
        session.refresh(posting)
        return _to_dict(posting)


def update_job_posting(posting_id: int, data: JobPostingCreate) -> dict:
    return _update(posting_id, data.model_dump())


def partial_update_job_posting(posting_id: int, data: JobPostingUpdate) -> dict:
    return _update(posting_id, data.model_dump(exclude_unset=True))


def delete_job_posting(posting_id: int, user_id: int | None = None) -> None:
    with Session(get_engine()) as session:
        if user_id is not None:
            _require_user(session, user_id)
        session.delete(_find(session, posting_id, user_id))
        session.commit()
