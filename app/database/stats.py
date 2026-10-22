from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database.connection import get_engine

COUNTS_SQL = text(
    "SELECT (SELECT COUNT(*) FROM users) AS users, "
    "(SELECT COUNT(*) FROM announcements) AS announcements, "
    "(SELECT COUNT(*) FROM job_postings) AS job_postings, "
    "(SELECT COUNT(*) FROM applications) AS applications"
)


def get_counts() -> dict[str, int] | None:
    """Row counts of the main tables for the home page, or None if the database cannot be read.

    The home page is the entry point of the site, so it must still open when the database is down.
    """
    try:
        with get_engine().connect() as conn:
            return dict(conn.execute(COUNTS_SQL).mappings().one())
    except (SQLAlchemyError, RuntimeError):
        return None
