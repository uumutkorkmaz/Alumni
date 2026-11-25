from datetime import date, datetime
from typing import TYPE_CHECKING, Literal

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from sqlalchemy import TIMESTAMP, CheckConstraint, ForeignKey, String, Text, func, select, text
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.database.connection import get_engine
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.application import Application
    from app.models.user import User

EmploymentType = Literal["full_time", "part_time", "internship", "contract"]

# ddd.md 4.3.1: a posting must say what the job is or where to apply (at least one, both allowed).
DESCRIPTION_OR_URL_MESSAGE = "A job posting needs a description or an application URL (at least one of the two)."
REQUIRED_FIELDS = ("title", "company", "city", "employment_type", "is_active")


def _blank_to_none(value: object) -> object:
    """An empty or spaces-only text counts as missing."""
    if isinstance(value, str) and not value.strip():
        return None
    return value


class JobPosting(Base):
    """ORM model for the job_postings table (ddd.md section 4.3)."""

    __tablename__ = "job_postings"
    __table_args__ = (
        CheckConstraint(
            "employment_type IN ('full_time', 'part_time', 'internship', 'contract')",
            name="ck_job_postings_employment_type",
        ),
        CheckConstraint(
            "description IS NOT NULL OR application_url IS NOT NULL",
            name="ck_job_postings_description_or_url",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120))
    company: Mapped[str] = mapped_column(String(150))
    city: Mapped[str] = mapped_column(String(150))
    employment_type: Mapped[str] = mapped_column(String(20))
    description: Mapped[str | None] = mapped_column(Text())
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
    """Fields of a posting that do not say who owns it (used as-is by the nested routes).

    Validation rules: ddd.md section 4.3.1.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=120)
    company: str = Field(min_length=1, max_length=150)
    city: str = Field(min_length=1, max_length=150)
    employment_type: EmploymentType
    description: str | None = None
    application_url: str | None = Field(default=None, max_length=500)
    deadline: date | None = None
    is_active: bool = True

    @field_validator("description", "application_url", mode="before")
    @classmethod
    def blank_optional_to_none(cls, value: object) -> object:
        return _blank_to_none(value)

    @model_validator(mode="after")
    def check_description_or_url(self) -> "JobPostingBase":
        if self.description is None and self.application_url is None:
            raise ValueError(DESCRIPTION_OR_URL_MESSAGE)
        return self


class JobPostingCreate(JobPostingBase):
    """Direct routes: the owner (a user id, or null for a department posting) is part of the body."""

    posted_by_user_id: int | None = None


class JobPostingUpdate(BaseModel):
    """PATCH: every field is optional. The description-or-URL rule is checked in _update,
    on the posting as it will be after the change."""

    model_config = ConfigDict(str_strip_whitespace=True)

    title: str | None = Field(default=None, min_length=1, max_length=120)
    company: str | None = Field(default=None, min_length=1, max_length=150)
    city: str | None = Field(default=None, min_length=1, max_length=150)
    employment_type: EmploymentType | None = None
    description: str | None = None
    application_url: str | None = Field(default=None, max_length=500)
    deadline: date | None = None
    is_active: bool | None = None
    posted_by_user_id: int | None = None

    @field_validator("description", "application_url", mode="before")
    @classmethod
    def blank_optional_to_none(cls, value: object) -> object:
        return _blank_to_none(value)


def _to_dict(posting: JobPosting) -> dict:
    return {
        "id": posting.id,
        "title": posting.title,
        "company": posting.company,
        "city": posting.city,
        "employment_type": posting.employment_type,
        "description": posting.description,
        "application_url": posting.application_url,
        "deadline": posting.deadline.isoformat() if posting.deadline else None,
        "is_active": posting.is_active,
        "posted_by_user_id": posting.posted_by_user_id,
        "created_at": posting.created_at.strftime("%Y-%m-%d %H:%M"),
    }


def _require_user(session: Session, user_id: int) -> None:
    """The poster must exist (404) and may not be a student (422): ddd.md section 4.1.1."""
    from app.models.user import POSTER_ROLES, User, require_role

    if session.get(User, user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    require_role(user_id, POSTER_ROLES, "open a job posting")


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
        missing = [key for key in REQUIRED_FIELDS if key in fields and fields[key] is None]
        if missing:
            raise HTTPException(status_code=422, detail=f"These fields cannot be empty: {', '.join(missing)}")
        for key, value in fields.items():
            setattr(posting, key, value)
        # The rule is checked on the result: clearing the only filled one of the two is refused.
        if posting.description is None and posting.application_url is None:
            raise HTTPException(status_code=422, detail=DESCRIPTION_OR_URL_MESSAGE)
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
