"""The public profile (ddd.md 4.1.7): work experience, education and certificates, the way a
LinkedIn profile lists them, plus the CV a student or graduate sends with an application.

Every row belongs to one user (ON DELETE CASCADE). The person adds, changes and deletes their own
rows on /me/profile; every signed-in member reads them on /users/{id}.
"""
import re
import secrets
from datetime import date, datetime
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy import TIMESTAMP, CheckConstraint, Date, ForeignKey, Index, Integer, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import get_engine
from app.models.base import Base

CV_DIR = Path(__file__).resolve().parents[2] / "uploads" / "cv"
MAX_CV_BYTES = 5 * 1024 * 1024
FMT = "%Y-%m-%d %H:%M"


# --------------------------------------------------------------------------- ORM models (tables of migration 0010)
class CvFile(Base):
    __tablename__ = "cv_files"
    __table_args__ = (UniqueConstraint("stored_name", name="uq_cv_files_stored_name"), Index("ix_cv_files_user_id", "user_id"))

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", name="fk_cv_files_user_id", ondelete="CASCADE"))
    original_name: Mapped[str] = mapped_column(String(200))
    stored_name: Mapped[str] = mapped_column(String(80))
    size_bytes: Mapped[int] = mapped_column(Integer())
    uploaded_at: Mapped[datetime] = mapped_column(TIMESTAMP(), server_default=text("CURRENT_TIMESTAMP"))
    # Set when a newer CV replaces it; the file stays while an application still points to it.
    replaced_at: Mapped[datetime | None] = mapped_column(TIMESTAMP())


class Experience(Base):
    __tablename__ = "experiences"
    __table_args__ = (
        CheckConstraint("end_date IS NULL OR end_date >= start_date", name="ck_experiences_dates"),
        Index("ix_experiences_user_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", name="fk_experiences_user_id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(120))
    company: Mapped[str] = mapped_column(String(150))
    city: Mapped[str | None] = mapped_column(String(100))
    start_date: Mapped[date] = mapped_column(Date())
    end_date: Mapped[date | None] = mapped_column(Date())  # empty: still working there
    description: Mapped[str | None] = mapped_column(String(1000))


class Education(Base):
    __tablename__ = "educations"
    __table_args__ = (
        CheckConstraint(
            "start_year BETWEEN 1950 AND 2100 AND (end_year IS NULL OR end_year BETWEEN start_year AND 2100)",
            name="ck_educations_years",
        ),
        Index("ix_educations_user_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", name="fk_educations_user_id", ondelete="CASCADE"))
    school: Mapped[str] = mapped_column(String(150))
    degree: Mapped[str | None] = mapped_column(String(100))
    field: Mapped[str | None] = mapped_column(String(150))
    start_year: Mapped[int] = mapped_column(Integer())
    end_year: Mapped[int | None] = mapped_column(Integer())  # empty: still studying
    description: Mapped[str | None] = mapped_column(String(1000))


class Certificate(Base):
    __tablename__ = "certificates"
    __table_args__ = (
        CheckConstraint("credential_url IS NULL OR credential_url LIKE 'https://%'", name="ck_certificates_credential_url_https"),
        Index("ix_certificates_user_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", name="fk_certificates_user_id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(150))
    issuer: Mapped[str] = mapped_column(String(150))
    issued_on: Mapped[date | None] = mapped_column(Date())
    credential_url: Mapped[str | None] = mapped_column(String(300))


# --------------------------------------------------------------------------- reading a profile
def _rows(sql: str, **params) -> list[dict]:
    with get_engine().connect() as conn:
        return [dict(r) for r in conn.execute(text(sql), params).mappings().all()]


def _month(d: date | None) -> str | None:
    return d.strftime("%Y-%m") if d else None


def sections(user_id: int) -> dict:
    """Experience (current jobs first, newest first), education and certificates of one user."""
    experiences = _rows(
        "SELECT id, title, company, city, start_date, end_date, description FROM experiences WHERE user_id = :id "
        "ORDER BY end_date IS NOT NULL, COALESCE(end_date, start_date) DESC, start_date DESC",
        id=user_id,
    )
    for e in experiences:
        e["start"], e["end"] = _month(e["start_date"]), _month(e["end_date"])
        e["months"] = _months(e["start_date"], e["end_date"] or date.today())
    educations = _rows(
        "SELECT id, school, degree, field, start_year, end_year, description FROM educations WHERE user_id = :id "
        "ORDER BY end_year IS NOT NULL, COALESCE(end_year, start_year) DESC",
        id=user_id,
    )
    certificates = _rows(
        "SELECT id, name, issuer, issued_on, credential_url FROM certificates WHERE user_id = :id "
        "ORDER BY issued_on DESC NULLS LAST, id DESC",
        id=user_id,
    )
    for c in certificates:
        c["issued"] = _month(c["issued_on"])
    return {"experiences": experiences, "educations": educations, "certificates": certificates}


def _months(start: date, end: date) -> int:
    return max(1, (end.year - start.year) * 12 + end.month - start.month + 1)


def activity(user_id: int) -> dict:
    """What the person did in the system, for their public profile."""
    postings = _rows(
        "SELECT id, title, company, is_active, deadline FROM job_postings WHERE posted_by_user_id = :id "
        "ORDER BY created_at DESC LIMIT 5",
        id=user_id,
    )
    announcements = _rows(
        "SELECT id, title, created_at FROM announcements WHERE author_id = :id ORDER BY created_at DESC LIMIT 5", id=user_id
    )
    for a in announcements:
        a["created_at"] = a["created_at"].strftime("%Y-%m-%d")
    for p in postings:
        p["deadline"] = p["deadline"].isoformat() if p["deadline"] else None
    return {"postings": postings, "announcements": announcements}


# --------------------------------------------------------------------------- checking a form
def _text(form: dict, key: str, limit: int, label: str, errors: dict, required: bool = False) -> str | None:
    raw = form.get(key) or ""
    value = raw.strip() if key == "description" else " ".join(raw.split())
    if required and not value:
        errors[key] = f"{label} is required."
    elif len(value) > limit:
        errors[key] = f"{label}: at most {limit} characters."
    return value or None


def _month_value(form: dict, key: str, label: str, errors: dict, required: bool) -> date | None:
    raw = (form.get(key) or "").strip()
    if not raw:
        if required:
            errors[key] = f"{label} is required."
        return None
    m = re.fullmatch(r"(\d{4})-(\d{2})", raw)
    if not m or not 1 <= int(m.group(2)) <= 12 or not 1950 <= int(m.group(1)) <= 2100:
        errors[key] = f"{label}: a month like 2024-09."
        return None
    return date(int(m.group(1)), int(m.group(2)), 1)


def _year_value(form: dict, key: str, label: str, errors: dict, required: bool) -> int | None:
    raw = (form.get(key) or "").strip()
    if not raw:
        if required:
            errors[key] = f"{label} is required."
        return None
    if not raw.isdigit() or not 1950 <= int(raw) <= 2100:
        errors[key] = f"{label}: a year between 1950 and 2100."
        return None
    return int(raw)


def _https(form: dict, key: str, label: str, errors: dict) -> str | None:
    value = _text(form, key, 300, label, errors)
    if value and not re.fullmatch(r"https://\S+\.\S+", value):
        errors[key] = f"{label}: an address starting with https://"
    return value


def clean(kind: str, form: dict) -> tuple[dict, dict]:
    """(values, errors) for one experience, education or certificate form."""
    e: dict = {}
    if kind == "experiences":
        v = {
            "title": _text(form, "title", 120, "Title", e, True),
            "company": _text(form, "company", 150, "Company", e, True),
            "city": _text(form, "city", 100, "City", e),
            "start_date": _month_value(form, "start_date", "Start", e, True),
            "end_date": None if form.get("current") else _month_value(form, "end_date", "End", e, True),
            "description": _text(form, "description", 1000, "Description", e),
        }
        if v["start_date"] and v["start_date"] > date.today():
            e["start_date"] = "Start cannot be in the future."
        if v["start_date"] and v["end_date"] and v["end_date"] < v["start_date"]:
            e["end_date"] = "End cannot be before the start."
    elif kind == "educations":
        v = {
            "school": _text(form, "school", 150, "School", e, True),
            "degree": _text(form, "degree", 100, "Degree", e),
            "field": _text(form, "field", 150, "Field of study", e),
            "start_year": _year_value(form, "start_year", "Start year", e, True),
            "end_year": _year_value(form, "end_year", "End year", e, False),
            "description": _text(form, "description", 1000, "Description", e),
        }
        if v["start_year"] and v["end_year"] and v["end_year"] < v["start_year"]:
            e["end_year"] = "End year cannot be before the start year."
    elif kind == "certificates":
        v = {
            "name": _text(form, "name", 150, "Name", e, True),
            "issuer": _text(form, "issuer", 150, "Issued by", e, True),
            "issued_on": _month_value(form, "issued_on", "Issued", e, False),
            "credential_url": _https(form, "credential_url", "Credential link", e),
        }
        if v["issued_on"] and v["issued_on"] > date.today():
            e["issued_on"] = "Issued cannot be in the future."
    else:
        raise HTTPException(status_code=404, detail="Unknown profile section")
    return v, e


TABLES = ("experiences", "educations", "certificates")


def add(user_id: int, kind: str, values: dict) -> None:
    if kind not in TABLES:
        raise HTTPException(status_code=404, detail="Unknown profile section")
    columns = ", ".join(values)  # keys come from clean(), never from the form
    marks = ", ".join(f":{k}" for k in values)
    with get_engine().begin() as conn:
        conn.execute(text(f"INSERT INTO {kind} (user_id, {columns}) VALUES (:uid, {marks})"), {**values, "uid": user_id})


def change(user_id: int, kind: str, item_id: int, values: dict) -> None:
    if kind not in TABLES:
        raise HTTPException(status_code=404, detail="Unknown profile section")
    sets = ", ".join(f"{k} = :{k}" for k in values)
    with get_engine().begin() as conn:
        done = conn.execute(
            text(f"UPDATE {kind} SET {sets} WHERE id = :iid AND user_id = :uid RETURNING id"),
            {**values, "iid": item_id, "uid": user_id},
        ).first()
    if done is None:
        raise HTTPException(status_code=404, detail="Not found on your profile")


def remove(user_id: int, kind: str, item_id: int) -> None:
    if kind not in TABLES:
        raise HTTPException(status_code=404, detail="Unknown profile section")
    with get_engine().begin() as conn:
        done = conn.execute(
            text(f"DELETE FROM {kind} WHERE id = :iid AND user_id = :uid RETURNING id"), {"iid": item_id, "uid": user_id}
        ).first()
    if done is None:
        raise HTTPException(status_code=404, detail="Not found on your profile")


# --------------------------------------------------------------------------- CVs
def current_cv(user_id: int) -> dict | None:
    rows = _rows(
        "SELECT id, original_name, size_bytes, uploaded_at FROM cv_files WHERE user_id = :id AND replaced_at IS NULL "
        "ORDER BY id DESC LIMIT 1",
        id=user_id,
    )
    if not rows:
        return None
    rows[0]["uploaded_at"] = rows[0]["uploaded_at"].strftime(FMT)
    return rows[0]


def _clean_name(name: str) -> str:
    base = re.sub(r"[^\w.\- ()]+", "_", Path(name or "cv.pdf").name).strip() or "cv.pdf"
    if not base.lower().endswith(".pdf"):
        base += ".pdf"
    return base[-200:]


def save_cv(user_id: int, filename: str, content: bytes) -> dict:
    """Store a new CV (PDF only, at most 5 MB) as the person's current one. The previous CV is
    marked replaced; its file is deleted unless an application was sent with it."""
    if not content:
        raise HTTPException(status_code=422, detail="Choose a PDF file for your CV.")
    if len(content) > MAX_CV_BYTES:
        raise HTTPException(status_code=422, detail="The CV can be at most 5 MB.")
    if not content.startswith(b"%PDF-"):
        raise HTTPException(status_code=422, detail="The CV must be a PDF file.")
    CV_DIR.mkdir(parents=True, exist_ok=True)
    stored = f"{secrets.token_hex(16)}.pdf"
    (CV_DIR / stored).write_bytes(content)
    try:
        with get_engine().begin() as conn:
            conn.execute(
                text("UPDATE cv_files SET replaced_at = CURRENT_TIMESTAMP WHERE user_id = :id AND replaced_at IS NULL"),
                {"id": user_id},
            )
            conn.execute(
                text("INSERT INTO cv_files (user_id, original_name, stored_name, size_bytes) VALUES (:id, :o, :s, :b)"),
                {"id": user_id, "o": _clean_name(filename), "s": stored, "b": len(content)},
            )
    except Exception:
        (CV_DIR / stored).unlink(missing_ok=True)
        raise
    _prune(user_id)
    return current_cv(user_id)


def remove_cv(user_id: int) -> None:
    with get_engine().begin() as conn:
        conn.execute(
            text("UPDATE cv_files SET replaced_at = CURRENT_TIMESTAMP WHERE user_id = :id AND replaced_at IS NULL"),
            {"id": user_id},
        )
    _prune(user_id)


def _prune(user_id: int) -> None:
    """Delete replaced CVs that no application points to (row and file)."""
    with get_engine().begin() as conn:
        gone = conn.execute(
            text(
                "DELETE FROM cv_files c WHERE c.user_id = :id AND c.replaced_at IS NOT NULL "
                "AND NOT EXISTS (SELECT 1 FROM applications a WHERE a.cv_file_id = c.id) RETURNING stored_name"
            ),
            {"id": user_id},
        ).scalars().all()
    for name in gone:
        (CV_DIR / name).unlink(missing_ok=True)


def delete_user_files(user_id: int) -> list[str]:
    """The stored names of every CV of a user (the caller deletes them after the user row is gone)."""
    return [r["stored_name"] for r in _rows("SELECT stored_name FROM cv_files WHERE user_id = :id", id=user_id)]


def cv_for_download(cv_id: int, viewer: dict) -> tuple[Path, str]:
    """(path, file name) of a CV the viewer may read: its owner, staff and admins, and the poster of a
    posting the CV was sent to. Anyone else gets 404, so a CV's existence is not revealed."""
    rows = _rows("SELECT user_id, original_name, stored_name FROM cv_files WHERE id = :c", c=cv_id)
    if not rows:
        raise HTTPException(status_code=404, detail="CV not found")
    cv = rows[0]
    allowed = viewer["id"] == cv["user_id"] or viewer["role"] in ("staff", "admin") or bool(_rows(
        "SELECT 1 FROM applications a JOIN job_postings j ON j.id = a.job_posting_id "
        "WHERE a.cv_file_id = :c AND j.posted_by_user_id = :v",
        c=cv_id, v=viewer["id"],
    ))
    path = CV_DIR / cv["stored_name"]
    if not allowed or not path.exists():
        raise HTTPException(status_code=404, detail="CV not found")
    return path, cv["original_name"]
