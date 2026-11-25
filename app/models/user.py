from datetime import datetime
from typing import TYPE_CHECKING, Literal

from fastapi import HTTPException
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import TIMESTAMP, CheckConstraint, Index, String, UniqueConstraint, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import get_engine
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.application import Application
    from app.models.job_posting import JobPosting

COLUMNS = "id, name, email, role, graduation_year, department"

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
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), server_default=text("'alumni'"))
    graduation_year: Mapped[int | None]
    department: Mapped[str] = mapped_column(String(100))
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


def get_users(role: str | None = None) -> list[dict]:
    """All users, or only those with one role (e.g. ?role=staff on the API)."""
    query = f"SELECT {COLUMNS} FROM users"
    params: dict = {}
    if role is not None:
        query += " WHERE role = :role"
        params["role"] = role
    with get_engine().connect() as conn:
        rows = conn.execute(text(query + " ORDER BY id"), params).mappings().all()
    return [dict(row) for row in rows]


def require_role(user_id: int, allowed: tuple[str, ...], action: str) -> dict:
    """The user, if their role may do `action`; 404 if they do not exist, 422 if the role may not.
    These are the data rules of ddd.md section 4.1.1 (they need no login: the role is in the data)."""
    user = get_user(user_id)
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
    with get_engine().begin() as conn:
        deleted = conn.execute(
            text("DELETE FROM users WHERE id = :id RETURNING id"), {"id": user_id}
        ).first()
    if deleted is None:
        raise HTTPException(status_code=404, detail="User not found")
