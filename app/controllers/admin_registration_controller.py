from fastapi import APIRouter, Form
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

from app.models import registration as registration_model
from app.views.admin_registration_view import render_registrations


class AdminRegistrationController:
    """The admin's review queue of registrations (ddd.md 4.1.2), as HTML pages.

    Until the login task this page is open like the other management pages; afterwards only
    admins reach it, and reviewed_by_user_id records who decided.
    """

    def __init__(self) -> None:
        self.router = APIRouter(prefix="/admin/registrations", tags=["AdminRegistration"])
        self.router.add_api_route("", self.list, methods=["GET"])
        self.router.add_api_route("/{user_id}/document", self.document, methods=["GET"])
        self.router.add_api_route("/{user_id}/approve", self.approve, methods=["POST"])
        self.router.add_api_route("/{user_id}/reject", self.reject, methods=["POST"])

    def list(self, done: str = "", name: str = "") -> HTMLResponse:
        return HTMLResponse(render_registrations(registration_model.pending_registrations(), done, name))

    def document(self, user_id: int) -> FileResponse:
        """The uploaded document, opened in the browser (inline). Gone after the decision."""
        path, content_type, original_name = registration_model.document_file(user_id)
        return FileResponse(path, media_type=content_type, filename=original_name, content_disposition_type="inline")

    def approve(self, user_id: int, name: str = Form("")) -> RedirectResponse:
        registration_model.approve(user_id)
        return RedirectResponse(url=f"/admin/registrations?done=approved&name={_q(name)}", status_code=303)

    def reject(self, user_id: int, reason: str = Form(""), name: str = Form("")) -> RedirectResponse:
        registration_model.reject(user_id, reason)
        return RedirectResponse(url=f"/admin/registrations?done=rejected&name={_q(name)}", status_code=303)


def _q(value: str) -> str:
    from urllib.parse import quote

    return quote(value[:100])
