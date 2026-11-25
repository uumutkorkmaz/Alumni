"""TEMPORARY: test accounts and one-click login, for trying the roles (ddd.md 4.1.4).

Only active when DEV_LOGIN=1 in the local .env (default 0): then POST /dev-login/{role} signs in as
that role's test account and the login page shows one button per role. Remove it (and run
`python -m app.cli delete-test-users`) when testing is over; never enable it where others can reach.
"""
import os

from sqlalchemy import text

from app.database.connection import get_engine

ENABLED = os.environ.get("DEV_LOGIN", "0") == "1"

# role: (name, email, graduation year, department). The order is the order of the buttons.
TEST_ACCOUNTS = {
    "admin": ("Test Yönetici", "test.admin@istanbul.edu.tr", None, "System administration"),
    "academic": ("Test Akademisyen", "test.akademisyen@istanbul.edu.tr", None, "Yönetim Bilişim Sistemleri"),
    "student": ("Test Öğrenci", "test.ogrenci@ogr.iu.edu.tr", 2028, "Yönetim Bilişim Sistemleri"),
    "staff": ("Test Personel", "test.personel@istanbul.edu.tr", None, "Bölüm Sekreterliği"),
    "alumni": ("Test Mezun", "test.mezun@example.com", 2022, "Yönetim Bilişim Sistemleri"),
}
BUTTON_LABELS = {"admin": "Admin", "academic": "Akademisyen", "student": "Öğrenci", "staff": "Personel", "alumni": "Mezun"}


def ensure_test_account(role: str) -> int:
    """The id of the role's test account, created (active, no password) if it is missing."""
    name, email, year, department = TEST_ACCOUNTS[role]
    with get_engine().begin() as conn:
        row = conn.execute(text("SELECT id FROM users WHERE email = :e"), {"e": email}).first()
        if row:
            # Keep it usable: active and with its role, even after someone changed it in the panel.
            conn.execute(text("UPDATE users SET status = 'active', role = :r WHERE id = :id"), {"r": role, "id": row[0]})
            return row[0]
        return conn.execute(
            text(
                "INSERT INTO users (name, email, role, status, graduation_year, department) "
                "VALUES (:n, :e, :r, 'active', :y, :d) RETURNING id"
            ),
            {"n": name, "e": email, "r": role, "y": year, "d": department},
        ).scalar_one()


def create_all() -> list[tuple[str, int]]:
    return [(role, ensure_test_account(role)) for role in TEST_ACCOUNTS]


def delete_all() -> int:
    from app.models.user import delete_user

    emails = [a[1] for a in TEST_ACCOUNTS.values()]
    with get_engine().connect() as conn:
        ids = [r[0] for r in conn.execute(text("SELECT id FROM users WHERE email = ANY(:e)"), {"e": emails})]
    for user_id in ids:
        delete_user(user_id)  # also removes a registration document file, if any
    return len(ids)
