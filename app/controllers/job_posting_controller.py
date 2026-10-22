from datetime import date

from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import ValidationError

from app.models import application as application_model
from app.models import job_posting as job_posting_model
from app.models import user as user_model
from app.models.job_posting import JobPostingCreate
from app.views.job_posting_view import (
    render_job_posting_detail,
    render_job_posting_edit_form,
    render_job_posting_list,
)


def _build_posting(
    title: str,
    company: str,
    location: str,
    employment_type: str,
    description: str,
    application_url: str,
    deadline: str,
    is_active: str | None,
    posted_by_user_id: str,
) -> JobPostingCreate:
    """Turn the raw HTML form values into a validated posting (empty optional fields become None)."""
    try:
        return JobPostingCreate(
            title=title,
            company=company,
            location=location,
            employment_type=employment_type,
            description=description,
            application_url=application_url.strip() or None,
            deadline=date.fromisoformat(deadline) if deadline.strip() else None,
            is_active=is_active is not None,
            posted_by_user_id=int(posted_by_user_id) if posted_by_user_id.strip() else None,
        )
    except ValidationError as error:
        raise HTTPException(status_code=422, detail=error.errors(include_url=False, include_context=False))
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error))


class JobPostingController:
    """Independent controller: job posting pages under /job-postings, served as HTML."""

    def __init__(self) -> None:
        self.router = APIRouter(prefix="/job-postings", tags=["JobPosting"])
        self.router.add_api_route("", self.list_all, methods=["GET"])
        self.router.add_api_route("", self.create, methods=["POST"])
        self.router.add_api_route("/{posting_id}", self.get, methods=["GET"])
        self.router.add_api_route("/{posting_id}/edit", self.edit_form, methods=["GET"])
        self.router.add_api_route("/{posting_id}/edit", self.update, methods=["POST"])
        self.router.add_api_route("/{posting_id}/delete", self.delete, methods=["POST"])
        self.router.add_api_route("/{posting_id}/apply", self.apply, methods=["POST"])

    def list_all(self) -> HTMLResponse:
        postings = job_posting_model.get_job_postings()
        return HTMLResponse(render_job_posting_list(postings, user_model.get_users()))

    def create(
        self,
        title: str = Form(...),
        company: str = Form(...),
        location: str = Form(...),
        employment_type: str = Form(...),
        description: str = Form(...),
        application_url: str = Form(""),
        deadline: str = Form(""),
        is_active: str | None = Form(None),
        posted_by_user_id: str = Form(""),
    ) -> RedirectResponse:
        data = _build_posting(
            title, company, location, employment_type, description,
            application_url, deadline, is_active, posted_by_user_id,
        )
        job_posting_model.create_job_posting(data)
        return RedirectResponse(url="/job-postings", status_code=303)

    def get(self, posting_id: int) -> HTMLResponse:
        return HTMLResponse(self._detail(posting_id))

    def edit_form(self, posting_id: int) -> HTMLResponse:
        posting = job_posting_model.get_job_posting(posting_id)
        return HTMLResponse(render_job_posting_edit_form(posting, user_model.get_users()))

    # HTML forms can only send GET/POST, so update, delete and apply use POST sub-routes.
    def update(
        self,
        posting_id: int,
        title: str = Form(...),
        company: str = Form(...),
        location: str = Form(...),
        employment_type: str = Form(...),
        description: str = Form(...),
        application_url: str = Form(""),
        deadline: str = Form(""),
        is_active: str | None = Form(None),
        posted_by_user_id: str = Form(""),
    ) -> RedirectResponse:
        data = _build_posting(
            title, company, location, employment_type, description,
            application_url, deadline, is_active, posted_by_user_id,
        )
        job_posting_model.update_job_posting(posting_id, data)
        return RedirectResponse(url=f"/job-postings/{posting_id}", status_code=303)

    def delete(self, posting_id: int) -> RedirectResponse:
        job_posting_model.delete_job_posting(posting_id)
        return RedirectResponse(url="/job-postings", status_code=303)

    def apply(self, posting_id: int, user_id: int = Form(...), cover_letter: str = Form("")) -> HTMLResponse:
        """Apply from the posting's own page. A refused application (duplicate, closed) shows a message on the page."""
        try:
            application_model.create_application(user_id, posting_id, cover_letter.strip() or None)
        except HTTPException as error:
            if error.status_code == 404 and error.detail == "Job posting not found":
                raise
            return HTMLResponse(self._detail(posting_id, error=str(error.detail)), status_code=error.status_code)
        return RedirectResponse(url=f"/job-postings/{posting_id}", status_code=303)

    def _detail(self, posting_id: int, error: str | None = None) -> str:
        posting = job_posting_model.get_job_posting(posting_id)
        applications = application_model.get_applications(job_posting_id=posting_id)
        return render_job_posting_detail(posting, user_model.get_users(), applications, error)
