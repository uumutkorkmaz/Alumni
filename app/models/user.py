from fastapi import HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.database.connection import get_engine

COLUMNS = "id, name, email, graduation_year, department"


class UserCreate(BaseModel):
    name: str = Field(max_length=100)
    email: str = Field(max_length=255)
    graduation_year: int = Field(ge=1950, le=2100)
    department: str = Field(max_length=100)


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    email: str | None = Field(default=None, max_length=255)
    graduation_year: int | None = Field(default=None, ge=1950, le=2100)
    department: str | None = Field(default=None, max_length=100)


def _email_taken() -> HTTPException:
    return HTTPException(status_code=409, detail="A user with this email already exists")


def create_user(data: UserCreate) -> dict:
    try:
        with get_engine().begin() as conn:
            row = conn.execute(
                text(
                    "INSERT INTO users (name, email, graduation_year, department) "
                    "VALUES (:name, :email, :graduation_year, :department) "
                    f"RETURNING {COLUMNS}"
                ),
                data.model_dump(),
            ).mappings().one()
    except IntegrityError:
        raise _email_taken()
    return dict(row)


def get_users() -> list[dict]:
    with get_engine().connect() as conn:
        rows = conn.execute(text(f"SELECT {COLUMNS} FROM users ORDER BY id")).mappings().all()
    return [dict(row) for row in rows]


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
