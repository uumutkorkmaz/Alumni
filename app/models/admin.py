"""The admin panel's data (ddd.md 4.1.4): counts, user changes with their safety rules, sessions,
content actions, and the audit log that records every change made in the panel."""
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import TIMESTAMP, ForeignKey, Index, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import get_engine
from app.models.base import Base
from app.models.user import ROLE_LABELS, ROLES, ROLES_WITH_YEAR


class AdminAudit(Base):
    """ORM model for the admin_audit table (ddd.md 4.1.4)."""

    __tablename__ = "admin_audit"
    __table_args__ = (Index("ix_admin_audit_created_at", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    admin_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", name="fk_admin_audit_admin_user_id", ondelete="SET NULL")
    )
    admin_name: Mapped[str] = mapped_column(String(100))
    action: Mapped[str] = mapped_column(String(40))
    target_type: Mapped[str] = mapped_column(String(30))
    target_id: Mapped[int | None] = mapped_column(Integer())
    details: Mapped[str | None] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(), server_default=text("CURRENT_TIMESTAMP"))


# --------------------------------------------------------------------------- audit
def audit(admin: dict, action: str, target_type: str, target_id: int | None, details: str = "") -> None:
    with get_engine().begin() as conn:
        conn.execute(
            text(
                "INSERT INTO admin_audit (admin_user_id, admin_name, action, target_type, target_id, details) "
                "VALUES (:a, :n, :act, :tt, :tid, :d)"
            ),
            {"a": admin["id"], "n": admin["name"][:100], "act": action, "tt": target_type,
             "tid": target_id, "d": (details or None) and details[:300]},
        )


def audit_log(limit: int = 200) -> list[dict]:
    with get_engine().connect() as conn:
        rows = conn.execute(
            text("SELECT id, admin_user_id, admin_name, action, target_type, target_id, details, created_at "
                 "FROM admin_audit ORDER BY created_at DESC, id DESC LIMIT :limit"),
            {"limit": limit},
        ).mappings().all()
    return [{**r, "created_at": r["created_at"].strftime("%Y-%m-%d %H:%M")} for r in rows]


# --------------------------------------------------------------------------- overview
def overview() -> dict:
    with get_engine().connect() as conn:
        by_role = dict(conn.execute(text(
            "SELECT role, COUNT(*) FROM users WHERE status = 'active' GROUP BY role")).all())
        by_status = dict(conn.execute(text("SELECT status, COUNT(*) FROM users GROUP BY status")).all())
        counts = conn.execute(text(
            "SELECT (SELECT COUNT(*) FROM announcements) AS announcements, "
            "(SELECT COUNT(*) FROM job_postings) AS postings, "
            "(SELECT COUNT(*) FROM job_postings WHERE is_active AND (deadline IS NULL OR deadline >= CURRENT_DATE)) AS open_postings, "
            "(SELECT COUNT(*) FROM applications) AS applications, "
            "(SELECT COUNT(*) FROM sessions WHERE expires_at > CURRENT_TIMESTAMP) AS sessions"
        )).mappings().one()
    return {"by_role": {r: by_role.get(r, 0) for r in ROLES},
            "by_status": {s: by_status.get(s, 0) for s in ("pending", "active", "rejected", "suspended")},
            **dict(counts)}


# --------------------------------------------------------------------------- users
def all_users(role: str = "", status: str = "", q: str = "") -> list[dict]:
    """Every account in every status, newest last, with the last sign-in."""
    conditions, params = [], {}
    if role in ROLES:
        conditions.append("role = :role")
        params["role"] = role
    if status in ("pending", "active", "rejected", "suspended"):
        conditions.append("status = :status")
        params["status"] = status
    if q.strip():
        conditions.append("(lower(name) LIKE :q OR lower(email) LIKE :q)")
        params["q"] = f"%{q.strip().lower()}%"
    where = (" WHERE " + " AND ".join(conditions)) if conditions else ""
    with get_engine().connect() as conn:
        rows = conn.execute(text(
            "SELECT id, name, email, role, status, graduation_year, department, last_login_at, "
            "(password_hash IS NOT NULL) AS has_password, "
            "(SELECT COUNT(*) FROM sessions s WHERE s.user_id = users.id AND s.expires_at > CURRENT_TIMESTAMP) AS sessions "
            f"FROM users{where} ORDER BY id"
        ), params).mappings().all()
    return [{**r, "last_login_at": r["last_login_at"].strftime("%Y-%m-%d %H:%M") if r["last_login_at"] else None}
            for r in rows]


def _user(conn, user_id: int) -> dict:
    row = conn.execute(text("SELECT id, name, role, status, graduation_year FROM users WHERE id = :id FOR UPDATE"),
                       {"id": user_id}).mappings().first()
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")
    return dict(row)


def _other_active_admins(conn, user_id: int) -> int:
    return conn.execute(text(
        "SELECT COUNT(*) FROM users WHERE role = 'admin' AND status = 'active' AND id <> :id"), {"id": user_id}).scalar_one()


def set_role(admin: dict, user_id: int, role: str) -> dict:
    if role not in ROLES:
        raise HTTPException(status_code=422, detail=f"Unknown role: {role}")
    if user_id == admin["id"]:
        raise HTTPException(status_code=409, detail="You cannot change your own role")
    with get_engine().begin() as conn:
        user = _user(conn, user_id)
        if user["role"] == role:
            return user
        if user["role"] == "admin" and user["status"] == "active" and _other_active_admins(conn, user_id) == 0:
            raise HTTPException(status_code=409, detail="This is the last active admin; give another account the role first")
        if role in ROLES_WITH_YEAR and user["graduation_year"] is None:
            raise HTTPException(status_code=422, detail="A student or graduate needs a graduation year: add it on the user's edit page first")
        conn.execute(text("UPDATE users SET role = :r, updated_at = CURRENT_TIMESTAMP WHERE id = :id"),
                     {"r": role, "id": user_id})
        # New rights apply at once: the account signs in again.
        conn.execute(text("DELETE FROM sessions WHERE user_id = :id"), {"id": user_id})
    audit(admin, "role_changed", "user", user_id, f"{user['name']}: {ROLE_LABELS[user['role']]} → {ROLE_LABELS[role]}")
    return {**user, "role": role}


def set_status(admin: dict, user_id: int, status: str) -> dict:
    """Suspend an active account, or reactivate a suspended one (pending ones go through the review)."""
    if status not in ("active", "suspended"):
        raise HTTPException(status_code=422, detail="Status must be active or suspended")
    if user_id == admin["id"]:
        raise HTTPException(status_code=409, detail="You cannot suspend yourself")
    with get_engine().begin() as conn:
        user = _user(conn, user_id)
        if user["status"] == status:
            return user
        if user["status"] not in ("active", "suspended"):
            raise HTTPException(status_code=409, detail=f"This account is {user['status']}; review it under Registrations")
        if status == "suspended" and user["role"] == "admin" and _other_active_admins(conn, user_id) == 0:
            raise HTTPException(status_code=409, detail="This is the last active admin and cannot be suspended")
        conn.execute(text("UPDATE users SET status = :s, updated_at = CURRENT_TIMESTAMP WHERE id = :id"),
                     {"s": status, "id": user_id})
        if status == "suspended":
            conn.execute(text("DELETE FROM sessions WHERE user_id = :id"), {"id": user_id})
    audit(admin, "user_suspended" if status == "suspended" else "user_reactivated", "user", user_id, user["name"])
    return {**user, "status": status}


def delete_user(admin: dict, user_id: int) -> None:
    from app.models.user import delete_user as delete_account

    if user_id == admin["id"]:
        raise HTTPException(status_code=409, detail="You cannot delete your own account")
    with get_engine().begin() as conn:
        user = _user(conn, user_id)
        if user["role"] == "admin" and user["status"] == "active" and _other_active_admins(conn, user_id) == 0:
            raise HTTPException(status_code=409, detail="This is the last active admin and cannot be deleted")
    delete_account(user_id)
    audit(admin, "user_deleted", "user", user_id, f"{user['name']} ({ROLE_LABELS[user['role']]})")


# --------------------------------------------------------------------------- sessions
def sessions() -> list[dict]:
    with get_engine().connect() as conn:
        rows = conn.execute(text(
            "SELECT s.id, s.user_id, u.name, u.role, s.created_at, s.last_seen_at, s.expires_at, s.user_agent "
            "FROM sessions s JOIN users u ON u.id = s.user_id "
            "WHERE s.expires_at > CURRENT_TIMESTAMP ORDER BY s.last_seen_at DESC"
        )).mappings().all()
    fmt = "%Y-%m-%d %H:%M"
    return [{**r, "created_at": r["created_at"].strftime(fmt), "last_seen_at": r["last_seen_at"].strftime(fmt),
             "expires_at": r["expires_at"].strftime(fmt)} for r in rows]


def end_session(admin: dict, session_id: int) -> None:
    with get_engine().begin() as conn:
        row = conn.execute(text("DELETE FROM sessions WHERE id = :id RETURNING user_id"), {"id": session_id}).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Session not found")
    audit(admin, "sessions_ended", "session", session_id, f"one session of user #{row[0]}")


def end_user_sessions(admin: dict, user_id: int) -> int:
    with get_engine().begin() as conn:
        n = conn.execute(text("DELETE FROM sessions WHERE user_id = :id"), {"id": user_id}).rowcount
    audit(admin, "sessions_ended", "user", user_id, f"{n} session(s)")
    return n


# --------------------------------------------------------------------------- content
def set_posting_active(admin: dict, posting_id: int, active: bool) -> None:
    with get_engine().begin() as conn:
        row = conn.execute(text(
            "UPDATE job_postings SET is_active = :a, updated_at = CURRENT_TIMESTAMP WHERE id = :id RETURNING title"),
            {"a": active, "id": posting_id}).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Job posting not found")
    audit(admin, "posting_opened" if active else "posting_closed", "job_posting", posting_id, row[0])
