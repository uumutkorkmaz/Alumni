"""Who may do what, for the controllers and the views (ddd.md 4.1.1 Table 2 and 4.1.3).

The auth middleware already stops a request whose *address* is not allowed. These helpers cover what
only the controller sees (the form or JSON body) and what the pages show (which buttons appear), so
one rule is written once and used by both.
"""
from fastapi import HTTPException

from app.auth import me

MANAGERS = ("staff", "admin")


def actor() -> dict:
    user = me()
    if user is None:  # the middleware lets no guest reach a protected route
        raise HTTPException(status_code=401, detail="Sign in first")
    return user


def is_admin(user: dict | None = None) -> bool:
    user = user if user is not None else me()
    return bool(user) and user["role"] == "admin"


# --------------------------------------------------------------------------- who is the author / poster / applicant
def author_for(requested: int | None) -> int:
    """The author of a new announcement: the signed-in user; an admin may name another account."""
    user = actor()
    return requested if (is_admin(user) and requested) else user["id"]


def poster_for(requested: int | None) -> int | None:
    """The poster of a new job posting: graduates and academics post as themselves; staff post for
    the department (no user) or as themselves; an admin may choose anyone or the department."""
    user = actor()
    if is_admin(user):
        return requested
    if user["role"] == "staff":
        return None if requested is None else user["id"]
    return user["id"]


def applicant() -> int:
    """Applications are always made by the signed-in student or graduate."""
    return actor()["id"]


# --------------------------------------------------------------------------- checks on a change
def check_status_change(application: dict, posting_owner: int | None, new_status: str) -> None:
    """Staff and admins set any status; the posting's owner decides (not 'withdrawn'); the applicant
    may only withdraw."""
    user = actor()
    if user["role"] in MANAGERS:
        return
    if user["id"] == posting_owner and new_status != "withdrawn":
        return
    if user["id"] == application["user_id"] and new_status == "withdrawn":
        return
    raise HTTPException(
        status_code=403,
        detail="Only the posting's owner, staff or an admin decide; the applicant may only withdraw (status 'withdrawn')",
    )


def check_role_change(current_role: str | None, new_role: str | None) -> None:
    """Only an admin gives or changes a role. Staff add students and graduates."""
    user = actor()
    if new_role is None or new_role == current_role or is_admin(user):
        return
    if current_role is None and user["role"] == "staff" and new_role in ("student", "alumni"):
        return  # staff adding a student or a graduate
    raise HTTPException(status_code=403, detail="Only an admin gives or changes a role")


# --------------------------------------------------------------------------- what the pages show
def can_edit_user(target: dict) -> bool:
    user = me()
    if not user:
        return False
    # Not the user themself: name, year and department were checked at registration (ddd.md 4.1.6);
    # people change their career profile on /me/profile.
    return is_admin(user) or (
        user["role"] == "staff" and target["role"] in ("student", "alumni")
    )


def can_delete_user() -> bool:
    return is_admin()


def can_publish() -> bool:
    user = me()
    return bool(user) and user["role"] in ("academic", "staff", "admin")


def can_edit_announcement(announcement: dict) -> bool:
    user = me()
    return bool(user) and (is_admin(user) or announcement.get("author_id") == user["id"])


def can_post() -> bool:
    user = me()
    return bool(user) and user["role"] != "student"


def can_edit_posting(posting: dict) -> bool:
    user = me()
    return bool(user) and (user["role"] in MANAGERS or posting.get("posted_by_user_id") == user["id"])


def can_apply() -> bool:
    user = me()
    return bool(user) and user["role"] in ("student", "alumni")


def can_add_user() -> bool:
    user = me()
    return bool(user) and user["role"] in MANAGERS


def sees_emails(target_id: int | None = None) -> bool:
    """Students and graduates do not see other users' email addresses (Table 2)."""
    user = me()
    return bool(user) and (user["role"] not in ("student", "alumni") or user["id"] == target_id)


def hide_emails(users: list[dict]) -> list[dict]:
    return [u if sees_emails(u["id"]) else {**u, "email": None} for u in users]


def visible_applications(applications: list[dict], postings_by_id: dict[int, dict]) -> list[dict]:
    """Students and graduates see their own applications and those to their postings; others all."""
    user = me()
    if not user or user["role"] not in ("student", "alumni"):
        return applications
    return [
        a for a in applications
        if a["user_id"] == user["id"]
        or (postings_by_id.get(a["job_posting_id"]) or {}).get("posted_by_user_id") == user["id"]
    ]
