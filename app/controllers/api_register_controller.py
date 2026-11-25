from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app import policy
from app.models import admin as admin_model
from app.models import registration as registration_model


class RejectBody(BaseModel):
    reason: str


class ApiRegisterController:
    """Registration and its review as JSON (ddd.md 4.1.2). The registration is multipart/form-data,
    because it carries a file; the answers are JSON."""

    def __init__(self) -> None:
        self.router = APIRouter(prefix="/api", tags=["ApiRegister"])
        self.router.add_api_route("/register", self.register, methods=["POST"], status_code=201)
        self.router.add_api_route("/admin/registrations", self.pending, methods=["GET"])
        self.router.add_api_route("/admin/registrations/{user_id}/approve", self.approve, methods=["POST"])
        self.router.add_api_route("/admin/registrations/{user_id}/reject", self.reject, methods=["POST"])

    def register(
        self,
        role: str = Form(...),
        name: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        password_confirm: str = Form(...),
        department: str = Form(...),
        consent: str = Form(...),
        document: UploadFile = File(...),
        graduation_year: str = Form(""),
        student_number: str = Form(""),
        title: str = Form(""),
        position: str = Form(""),
    ):
        """201 with the pending account (never the password hash); 409 if the email or student number
        is taken; 422 with one message per wrong field otherwise."""
        form = {
            "role": role, "name": name, "email": email, "password": password,
            "password_confirm": password_confirm, "department": department,
            "graduation_year": graduation_year, "student_number": student_number,
            "title": title, "position": position, "consent": consent,
        }
        clean, errors = registration_model.check_registration(form)
        file, file_error = registration_model.read_document(document.file, document.filename)
        if file_error:
            errors["document"] = file_error
        if not errors:
            account, errors = registration_model.register(clean, file)
            if account:
                return JSONResponse(account, status_code=201)
        status = 409 if set(errors.values()) <= {"email_taken", "student_number_taken"} else 422
        detail = [{"field": f, "message": m} for f, m in registration_model.messages(errors, "en").items()]
        return JSONResponse({"detail": detail}, status_code=status)

    def pending(self) -> list[dict]:
        return registration_model.pending_registrations()

    def approve(self, user_id: int) -> dict:
        result = registration_model.approve(user_id)
        admin_model.audit(policy.actor(), "registration_approved", "user", user_id)
        return result

    def reject(self, user_id: int, body: RejectBody) -> dict:
        result = registration_model.reject(user_id, body.reason)
        admin_model.audit(policy.actor(), "registration_rejected", "user", user_id, body.reason)
        return result
