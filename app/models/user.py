from datetime import datetime
from typing import TYPE_CHECKING, Literal

from fastapi import HTTPException
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import TIMESTAMP, CheckConstraint, ForeignKey, Index, String, UniqueConstraint, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import get_engine
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.application import Application
    from app.models.job_posting import JobPosting

# password_hash is never selected here: it never leaves the database through the pages or the API.
COLUMNS = (
    "id, name, email, role, status, graduation_year, department, student_number, title, position, "
    "company, job_title, city, linkedin_url, bio"
)
# Account status (ddd.md 4.1.2): a registration is pending until an admin reviews it.
STATUSES = ("pending", "active", "rejected", "suspended")  # suspended: closed by an admin (4.1.4)

# Roles (ddd.md section 4.1.1). One role per user; the order is the order of the pages and forms.
ROLES = ("student", "alumni", "academic", "staff", "admin")
Role = Literal["student", "alumni", "academic", "staff", "admin"]
ROLE_LABELS = {
    "student": "Student",
    "alumni": "Graduate",
    "academic": "Academic",
    "staff": "Staff",
    "admin": "Admin",
}
# How a role reads inside a sentence ("A staff member cannot apply ...").
ROLE_NOUNS = {
    "student": "student",
    "alumni": "graduate",
    "academic": "academic",
    "staff": "staff member",
    "admin": "admin",
}
# Students and graduates must have a graduation year (the expected one for students).
ROLES_WITH_YEAR = ("student", "alumni")
# Who may publish an announcement, open a job posting, apply to one (ddd.md section 4.1.1).
AUTHOR_ROLES = ("academic", "staff", "admin")
POSTER_ROLES = ("alumni", "academic", "staff", "admin")
APPLICANT_ROLES = ("student", "alumni")
YEAR_REQUIRED = "A student or graduate needs a graduation year"


class User(Base):
    """ORM model for the users table (ddd.md section 4.1)."""

    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
        CheckConstraint("graduation_year BETWEEN 1950 AND 2100", name="ck_users_graduation_year"),
        CheckConstraint(f"role IN {ROLES}", name="ck_users_role"),
        CheckConstraint(
            "role NOT IN ('student', 'alumni') OR graduation_year IS NOT NULL",
            name="ck_users_graduation_year_by_role",
        ),
        Index("ix_users_role", "role"),
        CheckConstraint("status IN ('pending', 'active', 'rejected', 'suspended')", name="ck_users_status"),
        Index("ix_users_status", "status"),
        UniqueConstraint("student_number", name="uq_users_student_number"),
        CheckConstraint(
            "status <> 'rejected' OR rejection_reason IS NOT NULL", name="ck_users_rejection_reason"
        ),
        CheckConstraint("linkedin_url IS NULL OR linkedin_url LIKE 'https://%'", name="ck_users_linkedin_url_https"),
        CheckConstraint("application_count BETWEEN 1 AND 3", name="ck_users_application_count"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), server_default=text("'alumni'"))
    graduation_year: Mapped[int | None]
    department: Mapped[str] = mapped_column(String(100))
    # Registration (ddd.md 4.1.2)
    status: Mapped[str] = mapped_column(String(20), server_default=text("'active'"))
    password_hash: Mapped[str | None] = mapped_column(String(255))
    student_number: Mapped[str | None] = mapped_column(String(20))
    title: Mapped[str | None] = mapped_column(String(40))
    position: Mapped[str | None] = mapped_column(String(100))
    consent_at: Mapped[datetime | None] = mapped_column(TIMESTAMP())
    reviewed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP())
    reviewed_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", name="fk_users_reviewed_by_user_id", ondelete="SET NULL")
    )
    rejection_reason: Mapped[str | None] = mapped_column(String(300))
    last_login_at: Mapped[datetime | None] = mapped_column(TIMESTAMP())
    # How many times this person applied (a rejected person may apply again, at most 3 times, ddd.md 4.1.2)
    application_count: Mapped[int] = mapped_column(server_default=text("1"))
    # Career profile, filled in by the person on /me/profile (ddd.md 4.1.6)
    company: Mapped[str | None] = mapped_column(String(150))
    job_title: Mapped[str | None] = mapped_column(String(120))
    city: Mapped[str | None] = mapped_column(String(100))
    linkedin_url: Mapped[str | None] = mapped_column(String(300))
    bio: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(), server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(), server_default=text("CURRENT_TIMESTAMP"))

    # One user -> many job postings. passive_deletes lets PostgreSQL's ON DELETE SET NULL
    # clear posted_by_user_id instead of the ORM loading every posting first.
    job_postings: Mapped[list["JobPosting"]] = relationship(back_populates="posted_by", passive_deletes=True)

    # One user -> many applications. ON DELETE CASCADE removes them in the database; the ORM
    # cascade is declared too so deleting a User object never tries to null the NOT NULL user_id.
    applications: Mapped[list["Application"]] = relationship(
        back_populates="applicant", cascade="all, delete-orphan", passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"


class UserCreate(BaseModel):
    name: str = Field(max_length=100)
    email: str = Field(max_length=255)
    role: Role = "alumni"
    graduation_year: int | None = Field(default=None, ge=1950, le=2100)
    department: str = Field(max_length=100)

    @model_validator(mode="after")
    def year_for_students_and_graduates(self) -> "UserCreate":
        if self.role in ROLES_WITH_YEAR and self.graduation_year is None:
            raise ValueError(YEAR_REQUIRED)
        return self


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    email: str | None = Field(default=None, max_length=255)
    role: Role | None = None
    graduation_year: int | None = Field(default=None, ge=1950, le=2100)
    department: str | None = Field(default=None, max_length=100)


def _email_taken() -> HTTPException:
    return HTTPException(status_code=409, detail="A user with this email already exists")


def create_user(data: UserCreate) -> dict:
    try:
        with get_engine().begin() as conn:
            row = conn.execute(
                text(
                    "INSERT INTO users (name, email, role, graduation_year, department) "
                    "VALUES (:name, :email, :role, :graduation_year, :department) "
                    f"RETURNING {COLUMNS}"
                ),
                data.model_dump(),
            ).mappings().one()
    except IntegrityError:
        raise _email_taken()
    return dict(row)


def get_users(role: str | None = None, status: str | None = "active") -> list[dict]:
    """Active users (pending and rejected registrations are left out, ddd.md 4.1.2), optionally
    with one role (e.g. ?role=staff on the API). status=None returns every account."""
    conditions, params = [], {}
    if role is not None:
        conditions.append("role = :role")
        params["role"] = role
    if status is not None:
        conditions.append("status = :status")
        params["status"] = status
    query = f"SELECT {COLUMNS} FROM users"
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    with get_engine().connect() as conn:
        rows = conn.execute(text(query + " ORDER BY id"), params).mappings().all()
    return [dict(row) for row in rows]


def require_role(user_id: int, allowed: tuple[str, ...], action: str) -> dict:
    """The user, if their role may do `action`; 404 if they do not exist, 422 if the role may not.
    These are the data rules of ddd.md section 4.1.1 (they need no login: the role is in the data)."""
    user = get_user(user_id)
    if user["status"] != "active":
        raise HTTPException(
            status_code=422, detail=f"This account is {user['status']}, so it cannot {action} yet"
        )
    if user["role"] not in allowed:
        names = ", ".join(ROLE_NOUNS[r] for r in allowed)
        noun = ROLE_NOUNS[user["role"]]
        article = "An" if noun[0] in "aeiou" else "A"
        raise HTTPException(status_code=422, detail=f"{article} {noun} cannot {action} (allowed: {names})")
    return user


def get_user(user_id: int) -> dict:
    with get_engine().connect() as conn:
        row = conn.execute(
            text(f"SELECT {COLUMNS} FROM users WHERE id = :id"), {"id": user_id}
        ).mappings().first()
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")
    return dict(row)


def _update(user_id: int, fields: dict) -> dict:
    if not fields:
        return get_user(user_id)
    # Required columns cannot be cleared, and the year rule is checked on the user as it will be.
    for key in ("name", "email", "role", "department"):
        if key in fields and fields[key] is None:
            raise HTTPException(status_code=422, detail=f"{key} cannot be empty")
    if "role" in fields or "graduation_year" in fields:
        merged = {**get_user(user_id), **fields}
        if merged["role"] in ROLES_WITH_YEAR and merged["graduation_year"] is None:
            raise HTTPException(status_code=422, detail=YEAR_REQUIRED)
    # Keys come from the Pydantic model's own field names, never from user input.
    assignments = ", ".join(f"{key} = :{key}" for key in fields)
    try:
        with get_engine().begin() as conn:
            row = conn.execute(
                text(
                    f"UPDATE users SET {assignments}, updated_at = CURRENT_TIMESTAMP "
                    f"WHERE id = :id RETURNING {COLUMNS}"
                ),
                {**fields, "id": user_id},
            ).mappings().first()
    except IntegrityError:
        raise _email_taken()
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")
    return dict(row)


def update_user(user_id: int, data: UserCreate) -> dict:
    return _update(user_id, data.model_dump())


def partial_update_user(user_id: int, data: UserUpdate) -> dict:
    return _update(user_id, data.model_dump(exclude_unset=True))


def delete_user(user_id: int) -> None:
    from app.models.profile import CV_DIR, delete_user_files
    from app.models.registration import UPLOAD_DIR

    cvs = delete_user_files(user_id)  # their rows go with the account (ON DELETE CASCADE)

    with get_engine().begin() as conn:
        # A registration document still on disk goes with the account (its row is removed by
        # ON DELETE CASCADE; the file is the app's job, ddd.md 4.1.2).
        stored = conn.execute(
            text(
                "SELECT stored_name FROM registration_documents "
                "WHERE user_id = :id AND file_deleted_at IS NULL"
            ),
            {"id": user_id},
        ).scalar_one_or_none()
        deleted = conn.execute(
            text("DELETE FROM users WHERE id = :id RETURNING id"), {"id": user_id}
        ).first()
    if deleted is None:
        raise HTTPException(status_code=404, detail="User not found")
    if stored:
        (UPLOAD_DIR / stored).unlink(missing_ok=True)
    for name in cvs:
        (CV_DIR / name).unlink(missing_ok=True)
