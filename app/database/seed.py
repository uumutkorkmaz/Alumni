import argparse

from faker import Faker
from sqlalchemy import text

from app.database.connection import get_engine
from app.database.factories import AnnouncementFactory, UserFactory

INSERT_USER = text(
    "INSERT INTO users (name, email, graduation_year, department) "
    "VALUES (:name, :email, :graduation_year, :department)"
)
INSERT_ANNOUNCEMENT = text(
    "INSERT INTO announcements (title, content, author) VALUES (:title, :content, :author)"
)


def seed(users: int, announcements: int, fresh: bool, seed_value: int | None) -> None:
    fake = Faker("en_US")
    if seed_value is not None:
        Faker.seed(seed_value)

    engine = get_engine()
    with engine.begin() as conn:
        if fresh:
            conn.execute(text("TRUNCATE users, announcements RESTART IDENTITY"))
            print("Cleared users and announcements.")

        if users:
            conn.execute(INSERT_USER, UserFactory(fake).make_many(users))
        if announcements:
            conn.execute(INSERT_ANNOUNCEMENT, AnnouncementFactory(fake).make_many(announcements))

        total_users = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
        total_announcements = conn.execute(text("SELECT COUNT(*) FROM announcements")).scalar()

    print(f"Inserted {users} users and {announcements} announcements.")
    print(f"Table totals now: users={total_users}, announcements={total_announcements}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fill the database with fake data.")
    parser.add_argument("--users", type=int, default=20, help="number of users to create")
    parser.add_argument("--announcements", type=int, default=10, help="number of announcements to create")
    parser.add_argument("--fresh", action="store_true", help="empty both tables first (resets ids)")
    parser.add_argument("--seed", type=int, default=None, help="fixed random seed for repeatable data")
    args = parser.parse_args()
    seed(args.users, args.announcements, args.fresh, args.seed)
