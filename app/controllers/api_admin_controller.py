from fastapi import APIRouter
from pydantic import BaseModel

from app import policy
from app.models import admin as admin_model


class UserChange(BaseModel):
    role: str | None = None
    status: str | None = None  # active or suspended


class ApiAdminController:
    """The admin panel's data and actions as JSON (ddd.md 4.1.4). Admins only (auth middleware)."""

    def __init__(self) -> None:
        self.router = APIRouter(prefix="/api/admin", tags=["ApiAdmin"])
        r = self.router.add_api_route
        r("/overview", self.overview, methods=["GET"])
        r("/users", self.users, methods=["GET"])
        r("/users/{user_id}", self.change_user, methods=["PATCH"])
        r("/users/{user_id}", self.delete_user, methods=["DELETE"])
        r("/sessions", self.sessions, methods=["GET"])
        r("/sessions/{session_id}", self.end_session, methods=["DELETE"])
        r("/audit", self.audit, methods=["GET"])

    def overview(self) -> dict:
        return admin_model.overview()

    def users(self, role: str = "", status: str = "", q: str = "") -> list[dict]:
        return admin_model.all_users(role, status, q)

    def change_user(self, user_id: int, body: UserChange) -> dict:
        """{"role": "admin"} and/or {"status": "suspended" | "active"}."""
        admin = policy.actor()
        result = {"id": user_id}
        if body.role is not None:
            result.update(admin_model.set_role(admin, user_id, body.role))
        if body.status is not None:
            result.update(admin_model.set_status(admin, user_id, body.status))
        return result

    def delete_user(self, user_id: int) -> dict:
        admin_model.delete_user(policy.actor(), user_id)
        return {"message": "User deleted", "id": user_id}

    def sessions(self) -> list[dict]:
        return admin_model.sessions()

    def end_session(self, session_id: int) -> dict:
        admin_model.end_session(policy.actor(), session_id)
        return {"message": "Session ended", "id": session_id}

    def audit(self) -> list[dict]:
        return admin_model.audit_log()
