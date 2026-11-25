"""Auth middleware (ddd.md 4.1.3): who is signed in, and may they reach this address?

1. The session cookie becomes the signed-in user (only active accounts), stored in
   app.auth.current_user for the controllers and the layout.
2. The address is checked against RULES (the first match decides). Public addresses are open to
   everyone; every other address needs a signed-in user. A guest is sent to /login (pages) or gets
   401 (API); a signed-in user without the right gets 403.

The rules that depend on a record (whose announcement, whose posting) look the owner up here. What
only a controller can see (the body of a form) is checked there: see ddd.md 4.1.3.
"""
import re
from collections.abc import Callable
from urllib.parse import quote

from fastapi import Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy import text
from starlette.routing import Match

from app.auth import COOKIE_NAME, current_user, user_for_token
from app.database.connection import get_engine
from app.models.user import ROLE_NOUNS

PUBLIC_EXACT = {
    "/", "/about", "/login", "/logout", "/register", "/register/done", "/404", "/favicon.ico",
    "/api/health", "/api/login", "/api/logout", "/api/register",
    "/docs", "/docs/oauth2-redirect", "/redoc", "/openapi.json", "/api/swagger", "/hello", "/api/debug/error",
}
PUBLIC_PREFIXES = ("/static/", "/hello/", "/sum/")

ANY = {"GET", "POST", "PUT", "PATCH", "DELETE"}
EDITORS = ("academic", "staff", "admin")
POSTERS = ("alumni", "academic", "staff", "admin")
APPLICANTS = ("student", "alumni")
MANAGERS = ("staff", "admin")


# --------------------------------------------------------------------------- owners
def _one(sql: str, **params):
    with get_engine().connect() as conn:
        return conn.execute(text(sql), params).first()


def _posting_owner(posting_id: int) -> int | None:
    row = _one("SELECT posted_by_user_id FROM job_postings WHERE id = :id", id=posting_id)
    return row[0] if row else None


def _user_role(user_id: int) -> str | None:
    row = _one("SELECT role FROM users WHERE id = :id", id=user_id)
    return row[0] if row else None


def _application(application_id: int) -> tuple[int, int | None] | None:
    row = _one(
        "SELECT a.user_id, j.posted_by_user_id FROM applications a "
        "JOIN job_postings j ON j.id = a.job_posting_id WHERE a.id = :id",
        id=application_id,
    )
    return (row[0], row[1]) if row else None


# --------------------------------------------------------------------------- checks
# Each check gets (user, match) and returns None when allowed, or a short "who may" text.
Check = Callable[[dict, re.Match], str | None]


def roles(*allowed: str) -> Check:
    def check(user: dict, _m: re.Match) -> str | None:
        return None if user["role"] in allowed else " or ".join(ROLE_NOUNS[r] + "s" for r in allowed)
    return check


def edit_user(user: dict, m: re.Match) -> str | None:
    target = int(m.group(1))
    if user["id"] == target or user["role"] == "admin":
        return None
    if user["role"] == "staff" and _user_role(target) in ("student", "alumni", None):
        return None
    return "the user themself, staff (students and graduates only) or an admin"


def announcement_owner(user: dict, m: re.Match) -> str | None:
    if user["role"] == "admin":
        return None
    row = _one("SELECT author_id FROM announcements WHERE id = :id", id=int(m.group(1)))
    if row is None:
        return None  # the controller answers 404
    return None if row[0] == user["id"] else "its author or an admin"


def posting_owner(group: int) -> Check:
    def check(user: dict, m: re.Match) -> str | None:
        if user["role"] in MANAGERS:
            return None
        posting_id = int(m.group(group))
        if _one("SELECT 1 FROM job_postings WHERE id = :id", id=posting_id) is None:
            return None  # the controller answers 404
        return None if _posting_owner(posting_id) == user["id"] else "its poster, staff or an admin"
    return check


def self_in_path(*allowed: str) -> Check:
    """Nested routes like /api/users/{id}/applications: the {id} must be the signed-in user."""
    def check(user: dict, m: re.Match) -> str | None:
        if user["role"] not in allowed:
            return " or ".join(ROLE_NOUNS[r] + "s" for r in allowed)
        return None if int(m.group(1)) == user["id"] or user["role"] == "admin" else "only for yourself"
    return check


def application_status(group: int) -> Check:
    def check(user: dict, m: re.Match) -> str | None:
        if user["role"] in MANAGERS:
            return None
        found = _application(int(m.group(group)))
        if found is None:
            return None  # the controller answers 404
        applicant, owner = found
        # The applicant may withdraw (the controller allows nothing else); the poster decides.
        return None if user["id"] in (applicant, owner) else "the posting's owner, the applicant, staff or an admin"
    return check


RULES: list[tuple[set[str], re.Pattern, Check]] = [
    (ANY, re.compile(r"^/(api/)?admin(/|$)"), roles("admin")),
    # users
    ({"POST"}, re.compile(r"^/(api/)?users/?$"), roles(*MANAGERS)),
    ({"POST"}, re.compile(r"^/users/(\d+)/delete$"), roles("admin")),
    ({"DELETE"}, re.compile(r"^/api/users/(\d+)$"), roles("admin")),
    ({"GET", "POST"}, re.compile(r"^/users/(\d+)/edit$"), edit_user),
    ({"PUT", "PATCH"}, re.compile(r"^/api/users/(\d+)$"), edit_user),
    # announcements
    ({"POST"}, re.compile(r"^/(api/)?announcements/?$"), roles(*EDITORS)),
    ({"GET", "POST"}, re.compile(r"^/announcements/(\d+)/(edit|delete)$"), announcement_owner),
    ({"PUT", "PATCH", "DELETE"}, re.compile(r"^/api/announcements/(\d+)$"), announcement_owner),
    # applications (before the job posting rules: /job-postings/{id}/apply is an application)
    ({"POST"}, re.compile(r"^/job-postings/(\d+)/apply$"), roles(*APPLICANTS)),
    ({"POST"}, re.compile(r"^/(api/)?applications/?$"), roles(*APPLICANTS)),
    ({"POST"}, re.compile(r"^/api/users/(\d+)/applications/?$"), self_in_path(*APPLICANTS)),
    ({"POST"}, re.compile(r"^/api/job-postings/(\d+)/applications/?$"), roles(*APPLICANTS)),
    ({"POST"}, re.compile(r"^/applications/(\d+)/status$"), application_status(1)),
    ({"PATCH"}, re.compile(r"^/api/applications/(\d+)$"), application_status(1)),
    ({"PATCH"}, re.compile(r"^/api/job-postings/(\d+)/applications/(\d+)$"), application_status(2)),
    ({"POST"}, re.compile(r"^/applications/(\d+)/delete$"), roles("admin")),
    ({"DELETE"}, re.compile(r"^/api/applications/(\d+)$"), roles("admin")),
    ({"DELETE"}, re.compile(r"^/api/users/(\d+)/applications/(\d+)$"), roles("admin")),
    # job postings
    ({"POST"}, re.compile(r"^/(api/)?job-postings/?$"), roles(*POSTERS)),
    ({"POST"}, re.compile(r"^/api/users/(\d+)/job-postings/?$"), self_in_path(*POSTERS)),
    ({"GET", "POST"}, re.compile(r"^/job-postings/(\d+)/(edit|delete)$"), posting_owner(1)),
    ({"PUT", "PATCH", "DELETE"}, re.compile(r"^/api/job-postings/(\d+)$"), posting_owner(1)),
    ({"DELETE"}, re.compile(r"^/api/users/(\d+)/job-postings/(\d+)$"), posting_owner(2)),
]


def _is_public(path: str) -> bool:
    return path in PUBLIC_EXACT or path.startswith(PUBLIC_PREFIXES)


def _route_exists(request: Request) -> bool:
    """Unknown addresses are left to the 404 guardian (a guest gets a 404, not a login page)."""
    return any(route.matches(request.scope)[0] != Match.NONE for route in request.app.routes)


def _is_page(request: Request) -> bool:
    return not request.url.path.startswith("/api/")


def _unauthorized(request: Request):
    if _is_page(request):
        target = request.url.path + (f"?{request.url.query}" if request.url.query else "")
        # After a refused POST, come back to the page, not to the action.
        if request.method != "GET":
            target = request.headers.get("referer", "/") or "/"
            target = re.sub(r"^https?://[^/]+", "", target) or "/"
        return RedirectResponse(url=f"/login?next={quote(target)}", status_code=303)
    return JSONResponse(
        {"status": 401, "error": "Unauthorized", "reason": "Sign in first: POST /api/login with email and password.",
         "method": request.method, "path": request.url.path},
        status_code=401,
    )


def _forbidden(request: Request, user: dict, who: str):
    reason = f"Only {who} may do this; you are signed in as a {ROLE_NOUNS[user['role']]}."
    if _is_page(request):
        from app.views.error_view import render_forbidden_page

        return HTMLResponse(render_forbidden_page(request.method, request.url.path, reason), status_code=403)
    return JSONResponse(
        {"status": 403, "error": "Forbidden", "reason": reason, "method": request.method, "path": request.url.path},
        status_code=403,
    )


async def auth_middleware(request: Request, call_next):
    user = user_for_token(request.cookies.get(COOKIE_NAME))
    token = current_user.set(user)
    try:
        path = request.url.path
        if not _is_public(path) and _route_exists(request):
            if user is None:
                return _unauthorized(request)
            for methods, pattern, check in RULES:
                m = pattern.match(path)
                if m and request.method in methods:
                    who = check(user, m)
                    if who:
                        return _forbidden(request, user, who)
                    break
        return await call_next(request)
    finally:
        current_user.reset(token)
