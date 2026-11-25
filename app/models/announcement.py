from datetime import datetime

from fastapi import HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import TIMESTAMP, ForeignKey, Index, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import get_engine
from app.models.base import Base
from app.models.user import AUTHOR_ROLES, require_role

# Reads join the author's account, so pages keep showing a name ("By Department Office").
# An announcement whose author account was deleted (ON DELETE SET NULL) shows "Department".
SELECT = (
    "SELECT a.id, a.title, a.content, a.author_id, COALESCE(u.name, 'Department') AS author, a.created_at "
    "FROM announcements a LEFT JOIN users u ON u.id = a.author_id"
)


class Announcement(Base):
    """ORM model for the announcements table (ddd.md sections 4.2 and 4.1.1)."""

    __tablename__ = "announcements"
    __table_args__ = (Index("ix_announcements_author_id", "author_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text())
    # Who published it: an academic, staff or admin account (checked by the model, ddd.md 4.1.1).
    author_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", name="fk_announcements_author_id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(), server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(), server_default=text("CURRENT_TIMESTAMP"))

    def __repr__(self) -> str:
        return f"<Announcement id={self.id} title={self.title!r}>"


class AnnouncementCreate(BaseModel):
    title: str = Field(max_length=200)
    content: str
    # Filled by the controller with the signed-in user; only an admin may name another author.
    author_id: int | None = None


class AnnouncementUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    content: str | None = None
    author_id: int | None = None


def _to_dict(row) -> dict:
    announcement = dict(row)
    announcement["created_at"] = announcement["created_at"].strftime("%Y-%m-%d %H:%M")
    return announcement


def _check_author(author_id: int) -> None:
    require_role(author_id, AUTHOR_ROLES, "publish an announcement")


def create_announcement(data: AnnouncementCreate) -> dict:
    if data.author_id is None:
        raise HTTPException(status_code=422, detail="author_id is required")
    _check_author(data.author_id)
    with get_engine().begin() as conn:
        new_id = conn.execute(
            text(
                "INSERT INTO announcements (title, content, author_id) "
                "VALUES (:title, :content, :author_id) RETURNING id"
            ),
            data.model_dump(),
        ).scalar_one()
    return get_announcement(new_id)


def get_announcements() -> list[dict]:
    with get_engine().connect() as conn:
        rows = conn.execute(text(f"{SELECT} ORDER BY a.id")).mappings().all()
    return [_to_dict(row) for row in rows]


def get_announcement(announcement_id: int) -> dict:
    with get_engine().connect() as conn:
        row = conn.execute(text(f"{SELECT} WHERE a.id = :id"), {"id": announcement_id}).mappings().first()
    if row is None:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return _to_dict(row)


def _update(announcement_id: int, fields: dict) -> dict:
    if not fields:
        return get_announcement(announcement_id)
    for key in ("title", "content", "author_id"):
        if key in fields and fields[key] is None:
            raise HTTPException(status_code=422, detail=f"{key} cannot be empty")
    if "author_id" in fields:
        _check_author(fields["author_id"])
    # Keys come from the Pydantic model's own field names, never from user input.
    assignments = ", ".join(f"{key} = :{key}" for key in fields)
    with get_engine().begin() as conn:
        updated = conn.execute(
            text(
                f"UPDATE announcements SET {assignments}, updated_at = CURRENT_TIMESTAMP "
                "WHERE id = :id RETURNING id"
            ),
            {**fields, "id": announcement_id},
        ).first()
    if updated is None:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return get_announcement(announcement_id)


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
