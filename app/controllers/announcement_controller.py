from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse, RedirectResponse

from app.models import announcement as announcement_model
from app.models.announcement import AnnouncementCreate, AnnouncementUpdate
from app.views.announcement_view import (
    render_announcement_detail,
    render_announcement_edit_form,
    render_announcement_list,
)


class AnnouncementController:
    """Independent controller: full CRUD for announcements under /announcements, via HTML pages."""

    def __init__(self) -> None:
        self.router = APIRouter(prefix="/announcements", tags=["Announcement"])
        self.router.add_api_route("", self.list, methods=["GET"])
        self.router.add_api_route("", self.create, methods=["POST"])
        self.router.add_api_route("/{announcement_id}", self.get, methods=["GET"])
        self.router.add_api_route("/{announcement_id}/edit", self.edit_form, methods=["GET"])
        self.router.add_api_route("/{announcement_id}/edit", self.update, methods=["POST"])
        self.router.add_api_route("/{announcement_id}/delete", self.delete, methods=["POST"])

    def list(self) -> HTMLResponse:
        return HTMLResponse(render_announcement_list(announcement_model.get_announcements()))

    def create(
        self,
        title: str = Form(...),
        content: str = Form(...),
        author: str = Form(...),
    ) -> RedirectResponse:
        data = AnnouncementCreate(title=title, content=content, author=author)
        announcement_model.create_announcement(data)
        return RedirectResponse(url="/announcements", status_code=303)

    def get(self, announcement_id: int) -> HTMLResponse:
        announcement = announcement_model.get_announcement(announcement_id)
        return HTMLResponse(render_announcement_detail(announcement))

    def edit_form(self, announcement_id: int) -> HTMLResponse:
        announcement = announcement_model.get_announcement(announcement_id)
        return HTMLResponse(render_announcement_edit_form(announcement))

    # HTML forms can only send GET/POST, so update and delete use POST sub-routes.
    def update(
        self,
        announcement_id: int,
        title: str = Form(...),
        content: str = Form(...),
        author: str = Form(...),
    ) -> RedirectResponse:
        data = AnnouncementUpdate(title=title, content=content, author=author)
        announcement_model.partial_update_announcement(announcement_id, data)
        return RedirectResponse(url=f"/announcements/{announcement_id}", status_code=303)

    def delete(self, announcement_id: int) -> RedirectResponse:
        announcement_model.delete_announcement(announcement_id)
        return RedirectResponse(url="/announcements", status_code=303)
