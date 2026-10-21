import argparse

from faker import Faker
from sqlalchemy import text

from app.database.connection import get_engine
from app.database.factories import AnnouncementFactory, JobPostingFactory, UserFactory

INSERT_USER = text(
    "INSERT INTO users (name, email, graduation_year, department) "
    "VALUES (:name, :email, :graduation_year, :department)"
)
INSERT_ANNOUNCEMENT = text(
    "INSERT INTO announcements (title, content, author) VALUES (:title, :content, :author)"
)
INSERT_JOB_POSTING = text(
    "INSERT INTO job_postings (title, company, location, employment_type, description, "
    "application_url, deadline, is_active, posted_by_user_id) "
    "VALUES (:title, :company, :location, :employment_type, :description, "
    ":application_url, :deadline, :is_active, :posted_by_user_id)"
)


def seed(users: int, announcements: int, job_postings: int, fresh: bool, seed_value: int | None) -> None:
    fake = Faker("en_US")
    if seed_value is not None:
        Faker.seed(seed_value)

    engine = get_engine()
    with engine.begin() as conn:
        if fresh:
            # One statement: PostgreSQL refuses to truncate a table that others point to unless
            # those tables are truncated in the same command. This also empties applications.
            conn.execute(text("TRUNCATE users, announcements, job_postings, applications RESTART IDENTITY"))
            print("Cleared users, announcements, job_postings and applications.")

        if users:
            conn.execute(INSERT_USER, UserFactory(fake).make_many(users))
        if announcements:
            conn.execute(INSERT_ANNOUNCEMENT, AnnouncementFactory(fake).make_many(announcements))
        if job_postings:
            # Job postings point to users, so users must exist first; they are picked from the table.
            user_ids = list(conn.execute(text("SELECT id FROM users ORDER BY id")).scalars())
            conn.execute(INSERT_JOB_POSTING, JobPostingFactory(fake, user_ids).make_many(job_postings))

        totals = {
            table: conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            for table in ("users", "announcements", "job_postings", "applications")
        }

    print(f"Inserted {users} users, {announcements} announcements and {job_postings} job postings.")
    print("Table totals now: " + ", ".join(f"{table}={count}" for table, count in totals.items()))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fill the database with fake data.")
    parser.add_argument("--users", type=int, default=20, help="number of users to create")
    parser.add_argument("--announcements", type=int, default=10, help="number of announcements to create")
    parser.add_argument("--job-postings", type=int, default=15, help="number of job postings to create")
    parser.add_argument("--fresh", action="store_true", help="empty all tables first (resets ids)")
    parser.add_argument("--seed", type=int, default=None, help="fixed random seed for repeatable data")
    args = parser.parse_args()
    seed(args.users, args.announcements, args.job_postings, args.fresh, args.seed)
