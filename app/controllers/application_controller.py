from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import ValidationError

from app import policy
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
        job_posting_id: int = Form(...),
        cover_letter: str = Form(""),
    ) -> HTMLResponse:
        """Apply as the signed-in student or graduate. A refused application (duplicate, closed
        posting) shows a message above the table."""
        try:
            application_model.create_application(policy.applicant(), job_posting_id, cover_letter.strip() or None)
        except HTTPException as error:
            return HTMLResponse(self._page(error=str(error.detail)), status_code=error.status_code)
        return RedirectResponse(url="/applications", status_code=303)

    # HTML forms can only send GET/POST, so a status change and a delete use POST sub-routes.
    def update_status(self, application_id: int, status: str = Form(...)) -> RedirectResponse:
        try:
            data = ApplicationUpdate(status=status)
        except ValidationError as error:
            raise HTTPException(status_code=422, detail=error.errors(include_url=False, include_context=False))
        _check_status(application_id, data.status)
        application_model.update_application(application_id, data)
        return RedirectResponse(url="/applications", status_code=303)

    def delete(self, application_id: int) -> RedirectResponse:
        application_model.delete_application(application_id)
        return RedirectResponse(url="/applications", status_code=303)

    def _page(self, error: str | None = None) -> str:
        postings = job_posting_model.get_job_postings()
        visible = policy.visible_applications(
            application_model.get_applications(), {p["id"]: p for p in postings}
        )
        return render_application_list(visible, user_model.get_users(), postings, error)


def _check_status(application_id: int, new_status: str) -> None:
    """Who may set this status (ddd.md 4.1.3): staff, admin, the posting's owner, or the applicant
    withdrawing."""
    application = application_model.get_application(application_id)
    owner = job_posting_model.get_job_posting(application["job_posting_id"])["posted_by_user_id"]
    policy.check_status_change(application, owner, new_status)
