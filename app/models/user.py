from fastapi import HTTPException
from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    email: str
    graduation_year: int
    department: str


class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    graduation_year: int | None = None
    department: str | None = None


# In-memory data store (no database connection yet).
users: list[dict] = []


def create_user(data: UserCreate) -> dict:
    new_user = {"id": len(users) + 1, **data.model_dump()}
    users.append(new_user)
    return new_user


def get_users() -> list[dict]:
    return users


def get_user(user_id: int) -> dict:
    for user in users:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")


def update_user(user_id: int, data: UserCreate) -> dict:
    existing = get_user(user_id)
    existing.update(data.model_dump())
    return existing


def partial_update_user(user_id: int, data: UserUpdate) -> dict:
    existing = get_user(user_id)
    existing.update(data.model_dump(exclude_unset=True))
    return existing


def delete_user(user_id: int) -> None:
    existing = get_user(user_id)
    users.remove(existing)
