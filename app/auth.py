"""Login, logout and sessions (ddd.md 4.1.3).

A session is a random token in an HttpOnly cookie; the database keeps only its SHA-256, so the
table alone cannot be used to sign in. The auth middleware (app/middleware/auth.py) turns the
cookie into the signed-in user for each request and puts it in `current_user`, where the
controllers and the layout read it.
"""
import hashlib
import os
import secrets
import time
from contextvars import ContextVar
from datetime import datetime, timedelta

from sqlalchemy import text

from app.database.connection import get_engine
from app.security import verify_password

COOKIE_NAME = "alumni_session"
SHORT_SESSION = timedelta(hours=12)
LONG_SESSION = timedelta(days=30)  # "remember me"
COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "0") == "1"  # 1 once the site runs on HTTPS
MAX_FAILURES, FAILURE_WINDOW = 5, 15 * 60  # five wrong passwords per email in 15 minutes

# The signed-in user of the request being handled (None for a guest). Set by the auth middleware.
current_user: ContextVar[dict | None] = ContextVar("current_user", default=None)

USER_COLUMNS = "u.id, u.name, u.email, u.role, u.status, u.department"


class LoginError(Exception):
    """A refused login. `code` picks the message; `reason` carries a rejection reason."""

    def __init__(self, code: str, reason: str | None = None) -> None:
        super().__init__(code)
        self.code = code
        self.reason = reason


MESSAGES = {
    # code: (Turkish for the page, English for the API)
    "invalid": ("E-posta ya da şifre hatalı.", "Wrong email or password."),
    "pending": (
        "Hesabınız henüz onaylanmadı. Yönetici belgenizi inceledikten sonra giriş yapabilirsiniz.",
        "This account is waiting for approval.",
    ),
    "rejected": ("Kaydınız reddedildi.", "This registration was rejected."),
    "suspended": (
        "Hesabınız bir yönetici tarafından askıya alındı. Bölümle iletişime geçin.",
        "This account was suspended by an admin.",
    ),
    "throttled": (
        "Çok fazla hatalı deneme. 15 dakika sonra yeniden deneyin.",
        "Too many wrong passwords. Try again in 15 minutes.",
    ),
}

_failures: dict[str, list[float]] = {}


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode("ascii")).hexdigest()


def _throttled(email: str) -> bool:
    now = time.monotonic()
    recent = [t for t in _failures.get(email, []) if now - t < FAILURE_WINDOW]
    _failures[email] = recent
    return len(recent) >= MAX_FAILURES


def _failed(email: str) -> None:
    _failures.setdefault(email, []).append(time.monotonic())


def login(email: str, password: str, remember: bool, user_agent: str | None) -> tuple[str, dict, timedelta]:
    """Check the credentials and open a session. Returns (cookie token, user, lifetime) or raises
    LoginError. The same "invalid" answer for an unknown email and a wrong password."""
    email = (email or "").strip().lower()
    if _throttled(email):
        raise LoginError("throttled")
    with get_engine().connect() as conn:
        row = conn.execute(
            text(f"SELECT {USER_COLUMNS}, u.password_hash, u.rejection_reason FROM users u WHERE lower(u.email) = :e"),
            {"e": email},
        ).mappings().first()
    if row is None or not verify_password(password or "", row["password_hash"]):
        _failed(email)
        raise LoginError("invalid")
    if row["status"] == "pending":
        raise LoginError("pending")
    if row["status"] == "rejected":
        raise LoginError("rejected", row["rejection_reason"])
    if row["status"] == "suspended":
        raise LoginError("suspended")

    _failures.pop(email, None)
    token, lifetime = open_session(row["id"], remember, user_agent)
    user = {k: row[k] for k in ("id", "name", "email", "role", "status", "department")}
    return token, user, lifetime


def open_session(user_id: int, remember: bool, user_agent: str | None) -> tuple[str, timedelta]:
    """A new session for an account whose credentials were checked. Returns (cookie token, lifetime)."""
    token = secrets.token_urlsafe(32)
    lifetime = LONG_SESSION if remember else SHORT_SESSION
    with get_engine().begin() as conn:
        # Old sessions of this user that have expired are removed on the way.
        conn.execute(text("DELETE FROM sessions WHERE user_id = :id AND expires_at < CURRENT_TIMESTAMP"), {"id": user_id})
        conn.execute(
            text(
                "INSERT INTO sessions (user_id, token_hash, expires_at, user_agent) "
                "VALUES (:id, :hash, CURRENT_TIMESTAMP + make_interval(secs => :secs), :ua)"
            ),
            {"id": user_id, "hash": _hash(token), "secs": int(lifetime.total_seconds()), "ua": (user_agent or "")[:200]},
        )
        conn.execute(text("UPDATE users SET last_login_at = CURRENT_TIMESTAMP WHERE id = :id"), {"id": user_id})
    return token, lifetime


def user_for_token(token: str | None) -> dict | None:
    """The active user of a valid session, or None. Touches last_seen_at at most once a minute."""
    if not token or len(token) > 100:
        return None
    with get_engine().connect() as conn:
        row = conn.execute(
            text(
                f"SELECT s.id AS session_id, s.last_seen_at, {USER_COLUMNS} FROM sessions s "
                "JOIN users u ON u.id = s.user_id "
                "WHERE s.token_hash = :hash AND s.expires_at > CURRENT_TIMESTAMP AND u.status = 'active'"
            ),
            {"hash": _hash(token)},
        ).mappings().first()
    if row is None:
        return None
    if (datetime.now() - row["last_seen_at"]).total_seconds() > 60:
        with get_engine().begin() as conn:
            conn.execute(text("UPDATE sessions SET last_seen_at = CURRENT_TIMESTAMP WHERE id = :id"), {"id": row["session_id"]})
    return {k: row[k] for k in ("id", "name", "email", "role", "status", "department")}


def logout(token: str | None) -> None:
    if token:
        with get_engine().begin() as conn:
            conn.execute(text("DELETE FROM sessions WHERE token_hash = :hash"), {"hash": _hash(token)})


def set_cookie(response, token: str, lifetime: timedelta, remember: bool) -> None:
    response.set_cookie(
        COOKIE_NAME,
        token,
        max_age=int(lifetime.total_seconds()) if remember else None,  # no "remember": ends with the browser
        httponly=True,
        samesite="lax",
        secure=COOKIE_SECURE,
        path="/",
    )


def clear_cookie(response) -> None:
    response.delete_cookie(COOKIE_NAME, path="/", httponly=True, samesite="lax", secure=COOKIE_SECURE)


def me() -> dict | None:
    """The signed-in user of this request (None for a guest)."""
    return current_user.get()


def message(code: str, lang: str = "tr") -> str:
    return MESSAGES[code][0 if lang == "tr" else 1]
