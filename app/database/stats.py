from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database.connection import get_engine

COUNTS_SQL = text(
    "SELECT (SELECT COUNT(*) FROM users WHERE role = 'alumni') AS users, "
    "(SELECT COUNT(*) FROM announcements) AS announcements, "
    "(SELECT COUNT(*) FROM job_postings) AS job_postings, "
    "(SELECT COUNT(*) FROM job_postings "
    "  WHERE is_active AND (deadline IS NULL OR deadline >= CURRENT_DATE)) AS open_job_postings, "
    "(SELECT COUNT(*) FROM applications) AS applications"
)

# Same "open" rule as the job posting pages and the applications: active and not past its deadline.
OPEN_POSTINGS_SQL = text(
    "SELECT id, title, company, city, employment_type, deadline FROM job_postings "
    "WHERE is_active AND (deadline IS NULL OR deadline >= CURRENT_DATE) "
    "ORDER BY created_at DESC, id DESC LIMIT :limit"
)

# The author is a user now (ddd.md 4.1.1); an announcement whose author account is gone shows "Department".
LATEST_ANNOUNCEMENTS_SQL = text(
    "SELECT a.id, a.title, COALESCE(u.name, 'Department') AS author, a.created_at "
    "FROM announcements a LEFT JOIN users u ON u.id = a.author_id "
    "ORDER BY a.created_at DESC, a.id DESC LIMIT :limit"
)


def get_home_data(postings: int = 4, announcements: int = 3) -> dict | None:
    """Everything the home page shows (counters, newest open postings, latest announcements), read in
    one connection. None if the database cannot be read: the home page is the entry point of the
    site, so it must still open when the database is down."""
    try:
        with get_engine().connect() as conn:
            return {
                "counts": dict(conn.execute(COUNTS_SQL).mappings().one()),
                "postings": [dict(r) for r in conn.execute(OPEN_POSTINGS_SQL, {"limit": postings}).mappings()],
                "announcements": [
                    dict(r) for r in conn.execute(LATEST_ANNOUNCEMENTS_SQL, {"limit": announcements}).mappings()
                ],
            }
    except (SQLAlchemyError, RuntimeError):
        return None
