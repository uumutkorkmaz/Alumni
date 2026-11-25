"""The signed-in person's own data, for the pages under /me (ddd.md 4.1.6).

Every function takes the user's own id (or the user) and only reads or changes rows that belong to
them: their profile, password and sessions, their applications and saved postings, the postings they
published (and the applications those received), their announcements.
"""
import hashlib
import re

from fastapi import HTTPException
from sqlalchemy import text

from app.database.connection import get_engine
from app.models import user as user_model
from app.security import hash_password, verify_password

FMT = "%Y-%m-%d %H:%M"
# Career profile fields and their length limits: free to change (nothing here is checked at registration).
PROFILE_FIELDS = {"company": 150, "job_title": 120, "city": 100, "linkedin_url": 300, "bio": 500}
DECISIONS = ("submitted", "under_review", "interview", "accepted", "rejected")


def _rows(sql: str, **params) -> list[dict]:
    with get_engine().connect() as conn:
        return [dict(r) for r in conn.execute(text(sql), params).mappings().all()]


def _fmt(rows: list[dict], *keys: str) -> list[dict]:
    """Dates and timestamps as text, the way the other pages show them."""
    for r in rows:
        for k in keys:
            value = r.get(k)
            if value is not None and not isinstance(value, str):
                r[k] = value.strftime(FMT) if hasattr(value, "hour") else value.isoformat()
    return rows


def _owner_clause(with_department: bool) -> str:
    return "(j.posted_by_user_id = :id" + (" OR j.posted_by_user_id IS NULL)" if with_department else ")")


# --------------------------------------------------------------------------- profile
def profile(user_id: int) -> dict:
    user = user_model.get_user(user_id)
    extra = _rows(
        "SELECT created_at, last_login_at, password_hash IS NOT NULL AS has_password FROM users WHERE id = :id",
        id=user_id,
    )[0]
    return {**user, **_fmt([extra], "created_at", "last_login_at")[0]}


def clean_profile(form: dict) -> tuple[dict, dict]:
    """(values, errors) for the career profile form. Empty fields are stored as NULL."""
    values, errors = {}, {}
    for key, limit in PROFILE_FIELDS.items():
        raw = form.get(key) or ""
        value = raw.strip() if key == "bio" else " ".join(raw.split())
        if len(value) > limit:
            errors[key] = f"At most {limit} characters."
        values[key] = value or None
    url = values["linkedin_url"]
    if url and not re.fullmatch(r"https://([a-z0-9-]+\.)*linkedin\.com/\S*", url, re.I):
        errors["linkedin_url"] = "A LinkedIn address starting with https:// (e.g. https://www.linkedin.com/in/your-name)."
    return values, errors


def update_profile(user_id: int, values: dict) -> dict:
    fields = {k: values.get(k) for k in PROFILE_FIELDS}
    with get_engine().begin() as conn:
        conn.execute(
            text(
                "UPDATE users SET company = :company, job_title = :job_title, city = :city, "
                "linkedin_url = :linkedin_url, bio = :bio, updated_at = CURRENT_TIMESTAMP WHERE id = :id"
            ),
            {**fields, "id": user_id},
        )
    return profile(user_id)


# --------------------------------------------------------------------------- password and sessions
def token_hash(token: str | None) -> str:
    """The form the sessions table keeps a cookie token in (app/auth.py)."""
    return hashlib.sha256((token or "").encode("ascii", "ignore")).hexdigest()


def password_problem(password: str, confirm: str) -> str | None:
    """The registration rule (ddd.md 4.1.2): 8 to 128 characters with a letter and a digit."""
    if len(password) > 128:
        return "The password can be at most 128 characters."
    if len(password) < 8 or not re.search(r"[A-Za-zÇĞİÖŞÜçğıöşü]", password) or not re.search(r"\d", password):
        return "The new password needs at least 8 characters, with a letter and a digit."
    if password != confirm:
        return "The two new passwords do not match."
    return None


def change_password(user_id: int, current: str, new: str, confirm: str, keep_hash: str) -> int:
    """Set a new password and end every other session of the account (this one stays). An account
    with no password yet (made by an admin or the CLI) sets its first one without a current password.
    Returns how many other sessions were ended."""
    stored = _rows("SELECT password_hash FROM users WHERE id = :id", id=user_id)[0]["password_hash"]
    if stored is not None and not verify_password(current or "", stored):
        raise HTTPException(status_code=422, detail="The current password is not right.")
    problem = password_problem(new or "", confirm or "")
    if problem:
        raise HTTPException(status_code=422, detail=problem)
    with get_engine().begin() as conn:
        conn.execute(
            text("UPDATE users SET password_hash = :h, updated_at = CURRENT_TIMESTAMP WHERE id = :id"),
            {"h": hash_password(new), "id": user_id},
        )
        return conn.execute(
            text("DELETE FROM sessions WHERE user_id = :id AND token_hash <> :keep"), {"id": user_id, "keep": keep_hash}
        ).rowcount


def sessions(user_id: int, current_hash: str) -> list[dict]:
    rows = _rows(
        "SELECT id, created_at, last_seen_at, expires_at, user_agent, token_hash = :h AS current "
        "FROM sessions WHERE user_id = :id AND expires_at > CURRENT_TIMESTAMP "
        "ORDER BY (token_hash = :h) DESC, last_seen_at DESC",
        id=user_id, h=current_hash,
    )
    return _fmt(rows, "created_at", "last_seen_at", "expires_at")


def end_session(user_id: int, session_id: int) -> None:
    with get_engine().begin() as conn:
        gone = conn.execute(
            text("DELETE FROM sessions WHERE id = :sid AND user_id = :id RETURNING id"), {"sid": session_id, "id": user_id}
        ).first()
    if gone is None:
        raise HTTPException(status_code=404, detail="Session not found among yours")


def end_other_sessions(user_id: int, current_hash: str) -> int:
    with get_engine().begin() as conn:
        return conn.execute(
            text("DELETE FROM sessions WHERE user_id = :id AND token_hash <> :h"), {"id": user_id, "h": current_hash}
        ).rowcount


def delete_account(user: dict, password: str) -> None:
    """A person closes their own account, confirming with the password. An admin is removed by another
    admin in the panel, so the system never loses its last admin by accident."""
    if user["role"] == "admin":
        raise HTTPException(status_code=422, detail="An admin account is removed by another admin in the admin panel.")
    stored = _rows("SELECT password_hash FROM users WHERE id = :id", id=user["id"])[0]["password_hash"]
    if stored is None or not verify_password(password or "", stored):
        raise HTTPException(status_code=422, detail="Type your password to delete the account.")
    user_model.delete_user(user["id"])


# --------------------------------------------------------------------------- applications (student, graduate)
def my_applications(user_id: int) -> list[dict]:
    rows = _rows(
        "SELECT a.id, a.status, a.cover_letter, a.cv_file_id, a.created_at, a.updated_at, "
        "j.id AS posting_id, j.title, j.company, j.city, j.employment_type, j.deadline, j.is_active, "
        "COALESCE(u.name, 'Department') AS poster "
        "FROM applications a JOIN job_postings j ON j.id = a.job_posting_id "
        "LEFT JOIN users u ON u.id = j.posted_by_user_id "
        "WHERE a.user_id = :id ORDER BY a.updated_at DESC, a.id DESC",
        id=user_id,
    )
    return _fmt(rows, "created_at", "updated_at", "deadline")


def _own_application(user_id: int, application_id: int) -> dict:
    rows = _rows("SELECT id, status FROM applications WHERE id = :a AND user_id = :id", a=application_id, id=user_id)
    if not rows:
        raise HTTPException(status_code=404, detail="Application not found among yours")
    return rows[0]


def withdraw(user_id: int, application_id: int) -> None:
    current = _own_application(user_id, application_id)["status"]
    if current in ("withdrawn", "accepted", "rejected"):
        raise HTTPException(status_code=422, detail=f"This application is already {current}.")
    with get_engine().begin() as conn:
        conn.execute(
            text("UPDATE applications SET status = 'withdrawn', updated_at = CURRENT_TIMESTAMP WHERE id = :a"),
            {"a": application_id},
        )


def edit_cover_letter(user_id: int, application_id: int, cover_letter: str) -> None:
    """The applicant may change the letter until someone starts reviewing the application."""
    if _own_application(user_id, application_id)["status"] != "submitted":
        raise HTTPException(status_code=422, detail="The letter can be changed only while the application is submitted.")
    if len(cover_letter) > 5000:
        raise HTTPException(status_code=422, detail="The cover letter can be at most 5000 characters.")
    with get_engine().begin() as conn:
        conn.execute(
            text("UPDATE applications SET cover_letter = :c, updated_at = CURRENT_TIMESTAMP WHERE id = :a"),
            {"c": cover_letter.strip() or None, "a": application_id},
        )


# --------------------------------------------------------------------------- saved postings (student, graduate)
def saved(user_id: int) -> list[dict]:
    rows = _rows(
        "SELECT s.created_at AS saved_at, j.id, j.title, j.company, j.city, j.employment_type, j.deadline, "
        "j.is_active, a.status AS applied_status "
        "FROM saved_postings s JOIN job_postings j ON j.id = s.job_posting_id "
        "LEFT JOIN applications a ON a.job_posting_id = j.id AND a.user_id = s.user_id "
        "WHERE s.user_id = :id ORDER BY s.created_at DESC",
        id=user_id,
    )
    return _fmt(rows, "saved_at", "deadline")


def is_saved(user_id: int, posting_id: int) -> bool:
    return bool(_rows("SELECT 1 FROM saved_postings WHERE user_id = :id AND job_posting_id = :p", id=user_id, p=posting_id))


def save(user_id: int, posting_id: int) -> None:
    if not _rows("SELECT 1 FROM job_postings WHERE id = :p", p=posting_id):
        raise HTTPException(status_code=404, detail="Job posting not found")
    with get_engine().begin() as conn:
        conn.execute(
            text("INSERT INTO saved_postings (user_id, job_posting_id) VALUES (:id, :p) ON CONFLICT DO NOTHING"),
            {"id": user_id, "p": posting_id},
        )


def unsave(user_id: int, posting_id: int) -> None:
    with get_engine().begin() as conn:
        conn.execute(
            text("DELETE FROM saved_postings WHERE user_id = :id AND job_posting_id = :p"), {"id": user_id, "p": posting_id}
        )


def suggestions(user_id: int, limit: int = 4) -> list[dict]:
    """Open postings the person has neither applied to, saved nor posted, newest first."""
    rows = _rows(
        "SELECT j.id, j.title, j.company, j.city, j.employment_type, j.deadline FROM job_postings j "
        "WHERE j.is_active AND (j.deadline IS NULL OR j.deadline >= CURRENT_DATE) "
        "AND NOT EXISTS (SELECT 1 FROM applications a WHERE a.job_posting_id = j.id AND a.user_id = :id) "
        "AND NOT EXISTS (SELECT 1 FROM saved_postings s WHERE s.job_posting_id = j.id AND s.user_id = :id) "
        "AND j.posted_by_user_id IS DISTINCT FROM :id "
        "ORDER BY j.created_at DESC LIMIT :n",
        id=user_id, n=limit,
    )
    return _fmt(rows, "deadline")


# --------------------------------------------------------------------------- postings (graduate, academic, staff, admin)
def my_postings(user_id: int, with_department: bool) -> list[dict]:
    """The person's postings with their applications counted; staff and admins also get the
    department's postings (no poster), which they manage (ddd.md 4.1.1)."""
    rows = _rows(
        "SELECT j.id, j.title, j.company, j.city, j.employment_type, j.deadline, j.is_active, j.created_at, "
        "j.posted_by_user_id IS NULL AS department, COUNT(a.id) AS applications, "
        "COUNT(a.id) FILTER (WHERE a.status IN ('submitted', 'under_review')) AS waiting, "
        "COUNT(a.id) FILTER (WHERE a.status = 'interview') AS interviews, "
        "COUNT(a.id) FILTER (WHERE a.status = 'accepted') AS accepted "
        f"FROM job_postings j LEFT JOIN applications a ON a.job_posting_id = j.id WHERE {_owner_clause(with_department)} "
        "GROUP BY j.id ORDER BY j.is_active DESC, j.created_at DESC",
        id=user_id,
    )
    return _fmt(rows, "created_at", "deadline")


def received(user_id: int, with_department: bool) -> list[dict]:
    """Applications to those postings; the ones still waiting for a decision first."""
    rows = _rows(
        "SELECT a.id, a.status, a.cover_letter, a.cv_file_id, a.created_at, a.updated_at, a.job_posting_id, j.title, "
        "u.id AS applicant_id, u.name AS applicant, u.role AS applicant_role, u.department, u.graduation_year "
        "FROM applications a JOIN job_postings j ON j.id = a.job_posting_id JOIN users u ON u.id = a.user_id "
        f"WHERE {_owner_clause(with_department)} "
        "ORDER BY (a.status IN ('submitted', 'under_review')) DESC, a.created_at DESC",
        id=user_id,
    )
    return _fmt(rows, "created_at", "updated_at")


def manages_posting(user: dict, posting_id: int) -> bool:
    rows = _rows("SELECT posted_by_user_id FROM job_postings WHERE id = :p", p=posting_id)
    if not rows:
        raise HTTPException(status_code=404, detail="Job posting not found")
    owner = rows[0]["posted_by_user_id"]
    return owner == user["id"] or (owner is None and user["role"] in ("staff", "admin"))


def set_posting_active(user: dict, posting_id: int, active: bool) -> None:
    if not manages_posting(user, posting_id):
        raise HTTPException(status_code=403, detail="Only the posting's poster opens or closes it here.")
    with get_engine().begin() as conn:
        conn.execute(
            text("UPDATE job_postings SET is_active = :a, updated_at = CURRENT_TIMESTAMP WHERE id = :p"),
            {"a": active, "p": posting_id},
        )


def decide(user: dict, application_id: int, status: str) -> None:
    """The poster moves an application on ('withdrawn' is the applicant's own choice)."""
    if status not in DECISIONS:
        raise HTTPException(status_code=422, detail="Choose one of: " + ", ".join(s.replace("_", " ") for s in DECISIONS))
    rows = _rows("SELECT job_posting_id, status FROM applications WHERE id = :a", a=application_id)
    if not rows or not manages_posting(user, rows[0]["job_posting_id"]):
        raise HTTPException(status_code=404, detail="Application not found among those to your postings")
    if rows[0]["status"] == "withdrawn":
        raise HTTPException(status_code=422, detail="The applicant withdrew this application.")
    with get_engine().begin() as conn:
        conn.execute(
            text("UPDATE applications SET status = :s, updated_at = CURRENT_TIMESTAMP WHERE id = :a"),
            {"s": status, "a": application_id},
        )


# --------------------------------------------------------------------------- announcements (academic, staff, admin)
def my_announcements(user_id: int) -> list[dict]:
    rows = _rows(
        "SELECT id, title, content, created_at, updated_at FROM announcements WHERE author_id = :id ORDER BY created_at DESC",
        id=user_id,
    )
    return _fmt(rows, "created_at", "updated_at")
