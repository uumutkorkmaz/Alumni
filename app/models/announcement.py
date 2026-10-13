from datetime import datetime

from fastapi import HTTPException
from pydantic import BaseModel


class AnnouncementCreate(BaseModel):
    title: str
    content: str
    author: str


class AnnouncementUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    author: str | None = None


# In-memory data store (no database connection yet).
announcements: list[dict] = []
_next_id = 1


def create_announcement(data: AnnouncementCreate) -> dict:
    global _next_id
    new_announcement = {
        "id": _next_id,
        **data.model_dump(),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    _next_id += 1
    announcements.append(new_announcement)
    return new_announcement


def get_announcements() -> list[dict]:
    return announcements


def get_announcement(announcement_id: int) -> dict:
    for announcement in announcements:
        if announcement["id"] == announcement_id:
            return announcement
    raise HTTPException(status_code=404, detail="Announcement not found")


def update_announcement(announcement_id: int, data: AnnouncementCreate) -> dict:
    existing = get_announcement(announcement_id)
    existing.update(data.model_dump())
    return existing


def partial_update_announcement(announcement_id: int, data: AnnouncementUpdate) -> dict:
    existing = get_announcement(announcement_id)
    existing.update(data.model_dump(exclude_unset=True))
    return existing


def delete_announcement(announcement_id: int) -> None:
    existing = get_announcement(announcement_id)
    announcements.remove(existing)
