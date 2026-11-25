from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse

from app.models import registration as registration_model
from app.views.register_view import render_register_done, render_register_page


class RegisterController:
    """Registration through the HTML pages under /register (ddd.md 4.1.2). Public, in Turkish."""

    def __init__(self) -> None:
        self.router = APIRouter(prefix="/register", tags=["Register"])
        self.router.add_api_route("", self.form, methods=["GET"])
        self.router.add_api_route("", self.create, methods=["POST"])
        self.router.add_api_route("/done", self.done, methods=["GET"])

    def form(self, role: str = "") -> HTMLResponse:
        """GET /register: the empty form (?role=student preselects a role card)."""
        values = {"role": role} if role in registration_model.REGISTER_ROLES else {}
        return HTMLResponse(render_register_page(values, {}))

    def create(
        self,
        role: str = Form(""),
        name: str = Form(""),
        email: str = Form(""),
        password: str = Form(""),
        password_confirm: str = Form(""),
        department: str = Form(""),
        graduation_year: str = Form(""),
        student_number: str = Form(""),
        title: str = Form(""),
        position: str = Form(""),
        consent: str = Form(""),
        document: UploadFile | None = File(None),
    ) -> HTMLResponse:
        """POST /register: every field is checked here (not by FastAPI), so a wrong field shows its
        message on the page instead of a raw 422."""
        form = {
            "role": role, "name": name, "email": email, "password": password,
            "password_confirm": password_confirm, "department": department,
            "graduation_year": graduation_year, "student_number": student_number,
            "title": title, "position": position, "consent": consent,
        }
        clean, errors = registration_model.check_registration(form)
        file, file_error = registration_model.read_document(
            document.file if document else None, document.filename if document else None
        )
        if file_error:
            errors["document"] = file_error
        if not errors:
            account, errors = registration_model.register(clean, file)
            if account:
                return RedirectResponse(url="/register/done", status_code=303)
        # Show the form again: what was typed stays, the passwords and the file do not.
        kept = {k: v for k, v in form.items() if k not in ("password", "password_confirm")}
        return HTMLResponse(render_register_page(kept, registration_model.messages(errors)), status_code=422)

    def done(self) -> HTMLResponse:
        return HTMLResponse(render_register_done())
