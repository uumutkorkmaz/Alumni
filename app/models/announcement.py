from fastapi import HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.database.connection import get_engine

COLUMNS = "id, title, content, author, created_at"


class AnnouncementCreate(BaseModel):
    title: str = Field(max_length=200)
    content: str
    author: str = Field(max_length=100)


class AnnouncementUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    content: str | None = None
    author: str | None = Field(default=None, max_length=100)


def _to_dict(row) -> dict:
    announcement = dict(row)
    announcement["created_at"] = announcement["created_at"].strftime("%Y-%m-%d %H:%M")
    return announcement


def create_announcement(data: AnnouncementCreate) -> dict:
    with get_engine().begin() as conn:
        row = conn.execute(
            text(
                "INSERT INTO announcements (title, content, author) "
                f"VALUES (:title, :content, :author) RETURNING {COLUMNS}"
            ),
            data.model_dump(),
        ).mappings().one()
    return _to_dict(row)


def get_announcements() -> list[dict]:
    with get_engine().connect() as conn:
        rows = conn.execute(text(f"SELECT {COLUMNS} FROM announcements ORDER BY id")).mappings().all()
    return [_to_dict(row) for row in rows]


def get_announcement(announcement_id: int) -> dict:
    with get_engine().connect() as conn:
        row = conn.execute(
            text(f"SELECT {COLUMNS} FROM announcements WHERE id = :id"), {"id": announcement_id}
        ).mappings().first()
    if row is None:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return _to_dict(row)


def _update(announcement_id: int, fields: dict) -> dict:
    if not fields:
        return get_announcement(announcement_id)
    # Keys come from the Pydantic model's own field names, never from user input.
    assignments = ", ".join(f"{key} = :{key}" for key in fields)
    with get_engine().begin() as conn:
        row = conn.execute(
            text(
                f"UPDATE announcements SET {assignments}, updated_at = CURRENT_TIMESTAMP "
                f"WHERE id = :id RETURNING {COLUMNS}"
            ),
            {**fields, "id": announcement_id},
        ).mappings().first()
    if row is None:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return _to_dict(row)


def update_announcement(announcement_id: int, data: AnnouncementCreate) -> dict:
    return _update(announcement_id, data.model_dump())


def partial_update_announcement(announcement_id: int, data: AnnouncementUpdate) -> dict:
    return _update(announcement_id, data.model_dump(exclude_unset=True))


def delete_announcement(announcement_id: int) -> None:
    with get_engine().begin() as conn:
        deleted = conn.execute(
            text("DELETE FROM announcements WHERE id = :id RETURNING id"), {"id": announcement_id}
        ).first()
    if deleted is None:
        raise HTTPException(status_code=404, detail="Announcement not found")
