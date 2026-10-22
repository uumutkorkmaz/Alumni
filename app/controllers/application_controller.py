from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import ValidationError

from app.models import application as application_model
from app.models import job_posting as job_posting_model
from app.models import user as user_model
from app.models.application import ApplicationUpdate
from app.views.application_view import render_application_list


class ApplicationController:
    """Independent controller: application pages under /applications, served as HTML."""

    def __init__(self) -> None:
        self.router = APIRouter(prefix="/applications", tags=["Application"])
        self.router.add_api_route("", self.list_all, methods=["GET"])
        self.router.add_api_route("", self.create, methods=["POST"])
        self.router.add_api_route("/{application_id}/status", self.update_status, methods=["POST"])
        self.router.add_api_route("/{application_id}/delete", self.delete, methods=["POST"])

    def list_all(self) -> HTMLResponse:
        return HTMLResponse(self._page())

    def create(
        self,
        user_id: int = Form(...),
        job_posting_id: int = Form(...),
        cover_letter: str = Form(""),
    ) -> HTMLResponse:
        """Apply. A refused application (duplicate, closed posting) shows a message above the table."""
        try:
            application_model.create_application(user_id, job_posting_id, cover_letter.strip() or None)
        except HTTPException as error:
            return HTMLResponse(self._page(error=str(error.detail)), status_code=error.status_code)
        return RedirectResponse(url="/applications", status_code=303)

    # HTML forms can only send GET/POST, so a status change and a delete use POST sub-routes.
    def update_status(self, application_id: int, status: str = Form(...)) -> RedirectResponse:
        try:
            data = ApplicationUpdate(status=status)
        except ValidationError as error:
            raise HTTPException(status_code=422, detail=error.errors(include_url=False, include_context=False))
        application_model.update_application(application_id, data)
        return RedirectResponse(url="/applications", status_code=303)

    def delete(self, application_id: int) -> RedirectResponse:
        application_model.delete_application(application_id)
        return RedirectResponse(url="/applications", status_code=303)

    def _page(self, error: str | None = None) -> str:
        return render_application_list(
            application_model.get_applications(),
            user_model.get_users(),
            job_posting_model.get_job_postings(),
            error,
        )
