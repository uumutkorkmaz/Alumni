from fastapi import APIRouter, HTTPException

from app import policy

from app.models import announcement as announcement_model
from app.models.announcement import AnnouncementCreate, AnnouncementUpdate


class ApiAnnouncementController:
    """Independent controller: JSON REST CRUD for announcements under /api/announcements."""

    def __init__(self) -> None:
        self.router = APIRouter(prefix="/api/announcements", tags=["ApiAnnouncement"])
        self.router.add_api_route("", self.create, methods=["POST"])
        self.router.add_api_route("", self.list, methods=["GET"])
        self.router.add_api_route("/{announcement_id}", self.get, methods=["GET"])
        self.router.add_api_route("/{announcement_id}", self.replace, methods=["PUT"])
        self.router.add_api_route("/{announcement_id}", self.update, methods=["PATCH"])
        self.router.add_api_route("/{announcement_id}", self.delete, methods=["DELETE"])

    def create(self, data: AnnouncementCreate) -> dict:
        data.author_id = policy.author_for(data.author_id)
        return announcement_model.create_announcement(data)

    def list(self) -> list[dict]:
        return announcement_model.get_announcements()

    def get(self, announcement_id: int) -> dict:
        return announcement_model.get_announcement(announcement_id)

    def replace(self, announcement_id: int, data: AnnouncementCreate) -> dict:
        if not policy.is_admin():  # the author stays; only an admin changes it
            data.author_id = announcement_model.get_announcement(announcement_id)["author_id"]
        return announcement_model.update_announcement(announcement_id, data)

    def update(self, announcement_id: int, data: AnnouncementUpdate) -> dict:
        if "author_id" in data.model_fields_set and not policy.is_admin():
            raise HTTPException(status_code=403, detail="Only an admin changes the author of an announcement")
        return announcement_model.partial_update_announcement(announcement_id, data)

    def delete(self, announcement_id: int) -> dict:
        announcement_model.delete_announcement(announcement_id)
        return {"message": "Announcement deleted", "id": announcement_id}
