from datetime import date, datetime
from typing import Literal

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import TIMESTAMP, CheckConstraint, ForeignKey, String, Text, UniqueConstraint, func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.database.connection import get_engine
from app.models.base import Base
from app.models.job_posting import JobPosting
from app.models.user import User

ApplicationStatus = Literal["submitted", "under_review", "interview", "accepted", "rejected", "withdrawn"]


class Application(Base):
    """ORM model for the applications table (ddd.md section 4.4).

    Join table between users and job_postings: one row = one user applying to one posting.
    """

    __tablename__ = "applications"
    __table_args__ = (
        UniqueConstraint("user_id", "job_posting_id", name="uq_applications_user_id_job_posting_id"),
        CheckConstraint(
            "status IN ('submitted', 'under_review', 'interview', 'accepted', 'rejected', 'withdrawn')",
            name="ck_applications_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", name="fk_applications_user_id", ondelete="CASCADE"))
    job_posting_id: Mapped[int] = mapped_column(
        ForeignKey("job_postings.id", name="fk_applications_job_posting_id", ondelete="CASCADE"),
        index=True,
    )
    status: Mapped[str] = mapped_column(String(20), server_default="submitted")
    cover_letter: Mapped[str | None] = mapped_column(Text())
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(), server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(), server_default=text("CURRENT_TIMESTAMP"))

    # Many applications -> one applicant, and many applications -> one posting.
    applicant: Mapped[User] = relationship(back_populates="applications")
    job_posting: Mapped[JobPosting] = relationship(back_populates="applications")

    def __repr__(self) -> str:
        return f"<Application id={self.id} user_id={self.user_id} job_posting_id={self.job_posting_id} status={self.status!r}>"


class ApplicationCreate(BaseModel):
    """Direct routes: both sides of the application are in the body."""

    user_id: int
    job_posting_id: int
    cover_letter: str | None = None


class UserApplicationCreate(BaseModel):
    """Nested under a user: the user is in the path, the posting is in the body."""

    job_posting_id: int
    cover_letter: str | None = None


class PostingApplicationCreate(BaseModel):
    """Nested under a posting: the posting is in the path, the applicant is in the body."""

    user_id: int
    cover_letter: str | None = None


class ApplicationUpdate(BaseModel):
    status: ApplicationStatus | None = None
    cover_letter: str | None = None


def _to_dict(application: Application) -> dict:
    return {
        "id": application.id,
        "user_id": application.user_id,
        "job_posting_id": application.job_posting_id,
        "status": application.status,
        "cover_letter": application.cover_letter,
        "created_at": application.created_at.strftime("%Y-%m-%d %H:%M"),
    }


def _require_user(session: Session, user_id: int) -> User:
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def _require_posting(session: Session, posting_id: int) -> JobPosting:
    posting = session.get(JobPosting, posting_id)
    if posting is None:
        raise HTTPException(status_code=404, detail="Job posting not found")
    return posting


def _find(session: Session, application_id: int, user_id: int | None, job_posting_id: int | None) -> Application:
    """Find an application. When a parent id comes from a nested route, an application of another parent counts as missing."""
    if user_id is not None:
        _require_user(session, user_id)
    if job_posting_id is not None:
        _require_posting(session, job_posting_id)
    application = session.get(Application, application_id)
    if (
        application is None
        or (user_id is not None and application.user_id != user_id)
        or (job_posting_id is not None and application.job_posting_id != job_posting_id)
    ):
        raise HTTPException(status_code=404, detail="Application not found")
    return application


def create_application(user_id: int, job_posting_id: int, cover_letter: str | None) -> dict:
    with Session(get_engine()) as session:
        _require_user(session, user_id)
        posting = _require_posting(session, job_posting_id)
        if not posting.is_active or (posting.deadline is not None and posting.deadline < date.today()):
            raise HTTPException(status_code=409, detail="This job posting is closed")
        application = Application(user_id=user_id, job_posting_id=job_posting_id, cover_letter=cover_letter)
        session.add(application)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise HTTPException(status_code=409, detail="This user has already applied to this job posting")
        session.refresh(application)
        return _to_dict(application)


def get_applications(user_id: int | None = None, job_posting_id: int | None = None) -> list[dict]:
    """All applications, or only those of one user, or only those to one posting."""
    with Session(get_engine()) as session:
        if user_id is not None:
            _require_user(session, user_id)
        if job_posting_id is not None:
            _require_posting(session, job_posting_id)
        query = select(Application).order_by(Application.id)
        if user_id is not None:
            query = query.where(Application.user_id == user_id)
        if job_posting_id is not None:
            query = query.where(Application.job_posting_id == job_posting_id)
        return [_to_dict(application) for application in session.scalars(query)]


def get_application(application_id: int, user_id: int | None = None, job_posting_id: int | None = None) -> dict:
    with Session(get_engine()) as session:
        return _to_dict(_find(session, application_id, user_id, job_posting_id))


def update_application(
    application_id: int, data: ApplicationUpdate, user_id: int | None = None, job_posting_id: int | None = None
) -> dict:
    with Session(get_engine()) as session:
        application = _find(session, application_id, user_id, job_posting_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(application, key, value)
        application.updated_at = func.current_timestamp()
        session.commit()
        session.refresh(application)
        return _to_dict(application)


def delete_application(application_id: int, user_id: int | None = None, job_posting_id: int | None = None) -> None:
    with Session(get_engine()) as session:
        session.delete(_find(session, application_id, user_id, job_posting_id))
        session.commit()
