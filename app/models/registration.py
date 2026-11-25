"""Registration (ddd.md 4.1.2): rules by role, the uploaded document, and the admin review.

The page and the API share one checker. It returns error *codes* per field; the page shows them in
Turkish and the API in English, so the rule itself is written once.
"""
import os
import re
import uuid
from datetime import date, datetime
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy import TIMESTAMP, CheckConstraint, ForeignKey, Integer, String, UniqueConstraint, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import get_engine
from app.models.base import Base
from app.security import hash_password

# --------------------------------------------------------------------------- settings
STUDENT_EMAIL_DOMAIN = os.environ.get("STUDENT_EMAIL_DOMAIN", "ogr.iu.edu.tr").lower()
STAFF_EMAIL_DOMAIN = os.environ.get("STAFF_EMAIL_DOMAIN", "istanbul.edu.tr").lower()
# uploads/registration/ next to app/: outside app/static, so no URL serves these files.
UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads" / "registration"
MAX_DOCUMENT_BYTES = 5 * 1024 * 1024

REGISTER_ROLES = ("student", "alumni", "academic", "staff")  # admin cannot register
ACADEMIC_TITLES = ("Prof. Dr.", "Doç. Dr.", "Dr. Öğr. Üyesi", "Öğr. Gör.", "Arş. Gör.")
# What each role uploads (shown on the page).
DOCUMENTS = {
    "student": "Öğrenci belgesi (e-Devlet)",
    "alumni": "Mezun belgesi ya da diploma",
    "academic": "Personel kimlik kartı ya da görev belgesi",
    "staff": "Personel kimlik kartı ya da görev belgesi",
}
# First bytes of the allowed files: the type is decided from the content, not the file name.
SIGNATURES = (
    (b"%PDF-", "application/pdf", "pdf"),
    (b"\xff\xd8\xff", "image/jpeg", "jpg"),
    (b"\x89PNG\r\n\x1a\n", "image/png", "png"),
)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# --------------------------------------------------------------------------- messages
MESSAGES = {
    # code: (Turkish for the page, English for the API)
    "required": ("Bu alan zorunlu.", "This field is required."),
    "name_length": ("Ad soyad 3 ile 100 karakter arasında olmalı.", "Name must be 3 to 100 characters."),
    "email_invalid": ("Geçerli bir e-posta adresi yazın.", "Enter a valid email address."),
    "email_student": (
        f"Öğrenciler @{STUDENT_EMAIL_DOMAIN} uzantılı öğrenci e-postasıyla kayıt olur.",
        f"Students register with their @{STUDENT_EMAIL_DOMAIN} address.",
    ),
    "email_staff": (
        f"Akademik ve idari personel @{STAFF_EMAIL_DOMAIN} uzantılı kurumsal e-postayla kayıt olur.",
        f"Academic and administrative staff register with their @{STAFF_EMAIL_DOMAIN} address.",
    ),
    "email_taken": ("Bu e-posta ile bir hesap zaten var.", "An account with this email already exists."),
    "password_weak": (
        "Şifre en az 8 karakter olmalı ve en az bir harf ile bir rakam içermeli.",
        "The password needs at least 8 characters, with a letter and a digit.",
    ),
    "password_long": ("Şifre en fazla 128 karakter olabilir.", "The password can be at most 128 characters."),
    "password_mismatch": ("Şifreler aynı değil.", "The two passwords do not match."),
    "role_invalid": ("Bir rol seçin.", "Choose one of: student, alumni, academic, staff."),
    "department_length": ("En fazla 100 karakter.", "At most 100 characters."),
    "year_invalid": ("Geçerli bir yıl yazın.", "Enter a valid year."),
    "year_student": (
        "Öğrenciler için beklenen mezuniyet yılı bu yıl ya da sonrası olmalı.",
        "A student's expected graduation year is this year or later.",
    ),
    "year_alumni": ("Mezuniyet yılı bu yıl ya da öncesi olmalı.", "A graduation year is this year or earlier."),
    "student_number_invalid": ("Öğrenci numarası 5-20 rakamdan oluşmalı.", "A student number is 5 to 20 digits."),
    "student_number_taken": (
        "Bu öğrenci numarasıyla bir hesap zaten var.",
        "An account with this student number already exists.",
    ),
    "title_invalid": ("Listeden bir unvan seçin.", "Choose an academic title from the list."),
    "position_length": ("Görev 2 ile 100 karakter arasında olmalı.", "Position must be 2 to 100 characters."),
    "consent_required": (
        "Devam etmek için aydınlatma metnini onaylamanız gerekiyor.",
        "Consent to the data processing text is required.",
    ),
    "document_required": ("Belgenizi yükleyin.", "Upload your document."),
    "document_type": ("Belge PDF, JPG ya da PNG olmalı.", "The document must be a PDF, JPG or PNG file."),
    "document_size": ("Belge en fazla 5 MB olabilir.", "The document can be at most 5 MB."),
}


def messages(errors: dict[str, str], lang: str = "tr") -> dict[str, str]:
    i = 0 if lang == "tr" else 1
    return {field: MESSAGES[code][i] for field, code in errors.items()}


# --------------------------------------------------------------------------- ORM
class RegistrationDocument(Base):
    """ORM model for the registration_documents table (ddd.md 4.1.2)."""

    __tablename__ = "registration_documents"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_registration_documents_user_id"),
        UniqueConstraint("stored_name", name="uq_registration_documents_stored_name"),
        CheckConstraint(
            "content_type IN ('application/pdf', 'image/jpeg', 'image/png')",
            name="ck_registration_documents_content_type",
        ),
        CheckConstraint("size_bytes BETWEEN 1 AND 5242880", name="ck_registration_documents_size"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", name="fk_registration_documents_user_id", ondelete="CASCADE")
    )
    original_name: Mapped[str] = mapped_column(String(255))
    stored_name: Mapped[str] = mapped_column(String(64))
    content_type: Mapped[str] = mapped_column(String(40))
    size_bytes: Mapped[int] = mapped_column(Integer())
    uploaded_at: Mapped[datetime] = mapped_column(TIMESTAMP(), server_default=text("CURRENT_TIMESTAMP"))
    file_deleted_at: Mapped[datetime | None] = mapped_column(TIMESTAMP())


# --------------------------------------------------------------------------- checks
def _clean(value) -> str:
    return (value or "").strip() if isinstance(value, str) or value is None else str(value).strip()


def check_registration(form: dict) -> tuple[dict, dict[str, str]]:
    """Check the typed fields (not the file). Returns (clean values, {field: error code})."""
    errors: dict[str, str] = {}
    role = _clean(form.get("role"))
    name = " ".join(_clean(form.get("name")).split())
    email = _clean(form.get("email")).lower()
    password = form.get("password") or ""
    password_confirm = form.get("password_confirm") or ""
    department = " ".join(_clean(form.get("department")).split())
    year_text = _clean(form.get("graduation_year"))
    student_number = _clean(form.get("student_number"))
    title = _clean(form.get("title"))
    position = " ".join(_clean(form.get("position")).split())
    consent = _clean(form.get("consent")).lower() in ("1", "on", "true", "yes", "evet")

    if role not in REGISTER_ROLES:
        errors["role"] = "role_invalid"

    if not name:
        errors["name"] = "required"
    elif not 3 <= len(name) <= 100:
        errors["name"] = "name_length"

    if not email:
        errors["email"] = "required"
    elif len(email) > 255 or not EMAIL_RE.match(email):
        errors["email"] = "email_invalid"
    elif role == "student" and not email.endswith("@" + STUDENT_EMAIL_DOMAIN):
        errors["email"] = "email_student"
    elif role in ("academic", "staff") and not email.endswith("@" + STAFF_EMAIL_DOMAIN):
        errors["email"] = "email_staff"

    if len(password) > 128:
        errors["password"] = "password_long"
    elif len(password) < 8 or not re.search(r"[A-Za-zÇĞİÖŞÜçğıöşü]", password) or not re.search(r"\d", password):
        errors["password"] = "password_weak"
    if not password_confirm:
        errors["password_confirm"] = "required"
    elif password_confirm != password:
        errors["password_confirm"] = "password_mismatch"

    if not department:
        errors["department"] = "required"
    elif len(department) > 100:
        errors["department"] = "department_length"

    year = None
    if role in ("student", "alumni"):
        this_year = date.today().year
        if not year_text:
            errors["graduation_year"] = "required"
        elif not year_text.isdigit():
            errors["graduation_year"] = "year_invalid"
        else:
            year = int(year_text)
            if role == "student" and not this_year <= year <= this_year + 8:
                errors["graduation_year"] = "year_student"
            elif role == "alumni" and not 1950 <= year <= this_year:
                errors["graduation_year"] = "year_alumni"

    if role == "student" and not student_number:
        errors["student_number"] = "required"
    elif role in ("student", "alumni") and student_number and not re.fullmatch(r"\d{5,20}", student_number):
        errors["student_number"] = "student_number_invalid"

    if role == "academic" and title not in ACADEMIC_TITLES:
        errors["title"] = "required" if not title else "title_invalid"

    if role == "staff":
        if not position:
            errors["position"] = "required"
        elif not 2 <= len(position) <= 100:
            errors["position"] = "position_length"

    if not consent:
        errors["consent"] = "consent_required"

    clean = {
        "name": name,
        "email": email,
        "role": role,
        "department": department,
        "graduation_year": year if role in ("student", "alumni") else None,
        "student_number": (student_number or None) if role in ("student", "alumni") else None,
        "title": title if role == "academic" else None,
        "position": position if role == "staff" else None,
        "password": password,
    }
    return clean, errors


def read_document(stream, filename: str | None) -> tuple[dict | None, str | None]:
    """Read an uploaded file (at most 5 MB) and recognise it by its first bytes.
    Returns ({content, content_type, ext, original_name, size}, None) or (None, error code)."""
    if stream is None or not filename:
        return None, "document_required"
    content = stream.read(MAX_DOCUMENT_BYTES + 1)
    if not content:
        return None, "document_required"
    if len(content) > MAX_DOCUMENT_BYTES:
        return None, "document_size"
    for magic, content_type, ext in SIGNATURES:
        if content.startswith(magic):
            name = os.path.basename(filename.replace("\\", "/"))[:255] or f"document.{ext}"
            return {"content": content, "content_type": content_type, "ext": ext,
                    "original_name": name, "size": len(content)}, None
    return None, "document_type"


# --------------------------------------------------------------------------- register
def _taken(conn, clean: dict) -> dict[str, str]:
    errors = {}
    if conn.execute(text("SELECT 1 FROM users WHERE lower(email) = :e"), {"e": clean["email"]}).first():
        errors["email"] = "email_taken"
    if clean["student_number"] and conn.execute(
        text("SELECT 1 FROM users WHERE student_number = :n"), {"n": clean["student_number"]}
    ).first():
        errors["student_number"] = "student_number_taken"
    return errors


def register(clean: dict, document: dict) -> tuple[dict | None, dict[str, str]]:
    """Create a pending account and its document. Returns (account, {}) or (None, {field: code})."""
    with get_engine().connect() as conn:
        errors = _taken(conn, clean)
    if errors:
        return None, errors

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}.{document['ext']}"
    path = UPLOAD_DIR / stored_name
    path.write_bytes(document["content"])
    try:
        with get_engine().begin() as conn:
            user = conn.execute(
                text(
                    "INSERT INTO users (name, email, role, status, graduation_year, department, "
                    "student_number, title, position, password_hash, consent_at) "
                    "VALUES (:name, :email, :role, 'pending', :graduation_year, :department, "
                    ":student_number, :title, :position, :password_hash, CURRENT_TIMESTAMP) "
                    "RETURNING id, name, email, role, status, graduation_year, department, "
                    "student_number, title, position, created_at"
                ),
                {**{k: v for k, v in clean.items() if k != "password"},
                 "password_hash": hash_password(clean["password"])},
            ).mappings().one()
            conn.execute(
                text(
                    "INSERT INTO registration_documents (user_id, original_name, stored_name, content_type, size_bytes) "
                    "VALUES (:user_id, :original_name, :stored_name, :content_type, :size)"
                ),
                {"user_id": user["id"], "original_name": document["original_name"],
                 "stored_name": stored_name, "content_type": document["content_type"], "size": document["size"]},
            )
    except IntegrityError:
        # Someone took the email or number between the check and the insert.
        path.unlink(missing_ok=True)
        with get_engine().connect() as conn:
            return None, _taken(conn, clean) or {"email": "email_taken"}
    except Exception:
        path.unlink(missing_ok=True)
        raise
    account = dict(user)
    account["created_at"] = account["created_at"].strftime("%Y-%m-%d %H:%M")
    return account, {}


# --------------------------------------------------------------------------- review (admin)
PENDING_SQL = text(
    "SELECT u.id, u.name, u.email, u.role, u.status, u.graduation_year, u.department, u.student_number, "
    "u.title, u.position, u.created_at, d.original_name, d.content_type, d.size_bytes, d.file_deleted_at "
    "FROM users u LEFT JOIN registration_documents d ON d.user_id = u.id "
    "WHERE u.status = 'pending' ORDER BY u.created_at, u.id"
)


def _row(row) -> dict:
    item = dict(row)
    item["created_at"] = item["created_at"].strftime("%Y-%m-%d %H:%M")
    item["has_file"] = item["original_name"] is not None and item["file_deleted_at"] is None
    item.pop("file_deleted_at", None)
    return item


def pending_registrations() -> list[dict]:
    with get_engine().connect() as conn:
        return [_row(r) for r in conn.execute(PENDING_SQL).mappings()]


def pending_count() -> int:
    with get_engine().connect() as conn:
        return conn.execute(text("SELECT COUNT(*) FROM users WHERE status = 'pending'")).scalar_one()


def document_file(user_id: int) -> tuple[Path, str, str]:
    """(path, content type, original name) of a pending registration's document, or 404."""
    with get_engine().connect() as conn:
        row = conn.execute(
            text(
                "SELECT d.stored_name, d.content_type, d.original_name, d.file_deleted_at "
                "FROM registration_documents d WHERE d.user_id = :id"
            ),
            {"id": user_id},
        ).mappings().first()
    if row is None or row["file_deleted_at"] is not None:
        raise HTTPException(status_code=404, detail="Document not found (it is deleted after the review)")
    path = UPLOAD_DIR / row["stored_name"]
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Document file is missing")
    return path, row["content_type"], row["original_name"]


def _decide(user_id: int, status: str, reason: str | None) -> dict:
    with get_engine().begin() as conn:
        current = conn.execute(
            text("SELECT status FROM users WHERE id = :id FOR UPDATE"), {"id": user_id}
        ).scalar_one_or_none()
        if current is None:
            raise HTTPException(status_code=404, detail="User not found")
        if current != "pending":
            raise HTTPException(status_code=409, detail=f"This account is already {current}")
        conn.execute(
            text(
                "UPDATE users SET status = :status, rejection_reason = :reason, reviewed_at = CURRENT_TIMESTAMP, "
                "updated_at = CURRENT_TIMESTAMP WHERE id = :id"
            ),
            {"status": status, "reason": reason, "id": user_id},
        )
        stored = conn.execute(
            text(
                "UPDATE registration_documents SET file_deleted_at = CURRENT_TIMESTAMP "
                "WHERE user_id = :id AND file_deleted_at IS NULL RETURNING stored_name"
            ),
            {"id": user_id},
        ).scalar_one_or_none()
    # The document is not needed after the decision (KVKK): remove the file, keep the record.
    if stored:
        (UPLOAD_DIR / stored).unlink(missing_ok=True)
    return {"id": user_id, "status": status, "rejection_reason": reason}


def approve(user_id: int) -> dict:
    return _decide(user_id, "active", None)


def reject(user_id: int, reason: str) -> dict:
    reason = " ".join((reason or "").split())
    if not 3 <= len(reason) <= 300:
        raise HTTPException(status_code=422, detail="A rejection needs a reason of 3 to 300 characters")
    return _decide(user_id, "rejected", reason)
