from urllib.parse import quote

from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse

from app import policy
from app.models import admin as admin_model
from app.models import announcement as announcement_model
from app.models import application as application_model
from app.models import job_posting as job_posting_model
from app.models import registration as registration_model
from app.models import user as user_model
from app.models.application import ApplicationUpdate
from app.views.admin_view import (
    render_admin_audit,
    render_admin_content,
    render_admin_overview,
    render_admin_sessions,
    render_admin_users,
)


def _back(path: str, done: str = "", error: str = "") -> RedirectResponse:
    """Back to a panel page with a one-line result (or the reason it was refused)."""
    path, _, fragment = path.partition("#")  # the query goes before a #section, or it is lost
    sep = "&" if "?" in path else "?"
    query = f"error={quote(error[:200])}" if error else f"done={quote(done[:200])}"
    return RedirectResponse(url=f"{path}{sep}{query}" + (f"#{fragment}" if fragment else ""), status_code=303)


def _do(path: str, done: str, action) -> RedirectResponse:
    try:
        action()
    except HTTPException as error:
        return _back(path, error=str(error.detail))
    return _back(path, done=done)


class AdminController:
    """The admin panel under /admin (ddd.md 4.1.4). Only admins reach it (auth middleware)."""

    def __init__(self) -> None:
        self.router = APIRouter(prefix="/admin", tags=["Admin"])
        r = self.router.add_api_route
        r("", self.overview, methods=["GET"])
        r("/users", self.users, methods=["GET"])
        r("/users/{user_id}/role", self.set_role, methods=["POST"])
        r("/users/{user_id}/status", self.set_status, methods=["POST"])
        r("/users/{user_id}/sessions/end", self.end_user_sessions, methods=["POST"])
        r("/users/{user_id}/delete", self.delete_user, methods=["POST"])
        r("/content", self.content, methods=["GET"])
        r("/content/postings/{posting_id}/active", self.set_posting_active, methods=["POST"])
        r("/content/applications/{application_id}/status", self.set_application_status, methods=["POST"])
        r("/content/{kind}/{item_id}/delete", self.delete_content, methods=["POST"])
        r("/sessions", self.sessions, methods=["GET"])
        r("/sessions/{session_id}/end", self.end_session, methods=["POST"])
        r("/audit", self.audit, methods=["GET"])

    # ------------------------------------------------------------------ pages
    def overview(self, done: str = "", error: str = "") -> HTMLResponse:
        registration_model.purge_rejected()
        return HTMLResponse(render_admin_overview(
            admin_model.overview(), registration_model.pending_count(), admin_model.audit_log(8), done, error))

    def users(self, role: str = "", status: str = "", q: str = "", done: str = "", error: str = "") -> HTMLResponse:
        return HTMLResponse(render_admin_users(
            admin_model.all_users(role, status, q), {"role": role, "status": status, "q": q},
            policy.actor(), registration_model.pending_count(), done, error))

    def content(self, done: str = "", error: str = "") -> HTMLResponse:
        return HTMLResponse(render_admin_content(
            announcement_model.get_announcements(), job_posting_model.get_job_postings(),
            application_model.get_applications(), user_model.get_users(status=None),
            registration_model.pending_count(), done, error))

    def sessions(self, done: str = "", error: str = "") -> HTMLResponse:
        return HTMLResponse(render_admin_sessions(admin_model.sessions(), policy.actor(),
                                                  registration_model.pending_count(), done, error))

    def audit(self) -> HTMLResponse:
        return HTMLResponse(render_admin_audit(admin_model.audit_log(), registration_model.pending_count()))

    # ------------------------------------------------------------------ users
    def set_role(self, user_id: int, role: str = Form(...), back: str = Form("/admin/users")) -> RedirectResponse:
        return _do(_safe(back), "Role changed; the account signs in again with its new rights.",
                   lambda: admin_model.set_role(policy.actor(), user_id, role))

    def set_status(self, user_id: int, status: str = Form(...), back: str = Form("/admin/users")) -> RedirectResponse:
        done = "Account suspended; its sessions were ended." if status == "suspended" else "Account reactivated."
        return _do(_safe(back), done, lambda: admin_model.set_status(policy.actor(), user_id, status))

    def end_user_sessions(self, user_id: int, back: str = Form("/admin/users")) -> RedirectResponse:
        return _do(_safe(back), "Sessions ended.", lambda: admin_model.end_user_sessions(policy.actor(), user_id))

    def delete_user(self, user_id: int, back: str = Form("/admin/users")) -> RedirectResponse:
        return _do(_safe(back), "Account deleted.", lambda: admin_model.delete_user(policy.actor(), user_id))

    # ------------------------------------------------------------------ content
    def set_posting_active(self, posting_id: int, active: str = Form(...)) -> RedirectResponse:
        on = active == "1"
        return _do("/admin/content#postings", "Posting opened." if on else "Posting closed.",
                   lambda: admin_model.set_posting_active(policy.actor(), posting_id, on))

    def set_application_status(self, application_id: int, status: str = Form(...)) -> RedirectResponse:
        def action():
            try:
                data = ApplicationUpdate(status=status)
            except Exception:
                raise HTTPException(status_code=422, detail=f"Unknown status: {status}")
            application_model.update_application(application_id, data)
            admin_model.audit(policy.actor(), "application_status", "application", application_id, status)
        return _do("/admin/content#applications", "Application status changed.", action)

    def delete_content(self, kind: str, item_id: int) -> RedirectResponse:
        deleters = {
            "announcements": (announcement_model.delete_announcement, "announcement_deleted", "announcement"),
            "postings": (job_posting_model.delete_job_posting, "posting_deleted", "job_posting"),
            "applications": (application_model.delete_application, "application_deleted", "application"),
        }
        if kind not in deleters:
            raise HTTPException(status_code=404, detail="Nothing to delete here")
        delete, action_name, target = deleters[kind]

        def action():
            delete(item_id)
            admin_model.audit(policy.actor(), action_name, target, item_id)
        return _do(f"/admin/content#{kind}", "Deleted.", action)

    # ------------------------------------------------------------------ sessions
    def end_session(self, session_id: int) -> RedirectResponse:
        return _do("/admin/sessions", "Session ended.", lambda: admin_model.end_session(policy.actor(), session_id))


def _safe(back: str) -> str:
    """Only panel pages as the place to go back to."""
    return back if back.startswith("/admin") and not back.startswith("//") else "/admin/users"
