"""Command line tasks.

Admins cannot register (ddd.md 4.1.2), so the first one is made here:

    docker compose exec api python -m app.cli create-admin --name "Ad Soyad" --email admin@istanbul.edu.tr

Users that existed before registration have no password; an admin gives them one (ddd.md 4.1.3):

    docker compose exec api python -m app.cli set-password --email someone@example.com

The password is asked twice without showing it; for scripts, set ADMIN_PASSWORD (create-admin) or
NEW_PASSWORD (set-password) in the environment of that one command instead.
"""
import argparse
import getpass
import os
import sys

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.database.connection import get_engine
from app.models.registration import EMAIL_RE
from app.security import hash_password


def _ask_password(env_name: str) -> str | None:
    """The new password: from the environment of this one command, or typed twice (not shown)."""
    password = os.environ.get(env_name)
    if password is None:
        password = getpass.getpass("Password (at least 8 characters, a letter and a digit): ")
        if getpass.getpass("Password again: ") != password:
            print("The passwords do not match.", file=sys.stderr)
            return None
    if len(password) < 8 or not any(c.isalpha() for c in password) or not any(c.isdigit() for c in password):
        print("The password needs at least 8 characters, with a letter and a digit.", file=sys.stderr)
        return None
    return password


def create_admin(name: str, email: str, department: str) -> int:
    email = email.strip().lower()
    if not EMAIL_RE.match(email):
        print("Not a valid email address.", file=sys.stderr)
        return 2
    password = _ask_password("ADMIN_PASSWORD")
    if password is None:
        return 2
    try:
        with get_engine().begin() as conn:
            new_id = conn.execute(
                text(
                    "INSERT INTO users (name, email, role, status, department, password_hash) "
                    "VALUES (:name, :email, 'admin', 'active', :department, :hash) RETURNING id"
                ),
                {"name": name.strip(), "email": email, "department": department, "hash": hash_password(password)},
            ).scalar_one()
    except IntegrityError:
        print("An account with this email already exists.", file=sys.stderr)
        return 1
    print(f"Admin account #{new_id} created for {email}.")
    return 0


def set_password(email: str) -> int:
    email = email.strip().lower()
    password = _ask_password("NEW_PASSWORD")
    if password is None:
        return 2
    with get_engine().begin() as conn:
        row = conn.execute(
            text("UPDATE users SET password_hash = :hash, updated_at = CURRENT_TIMESTAMP "
                 "WHERE lower(email) = :email RETURNING id, status"),
            {"hash": hash_password(password), "email": email},
        ).first()
        if row is not None:
            # A new password ends the sessions opened with the old one.
            conn.execute(text("DELETE FROM sessions WHERE user_id = :id"), {"id": row[0]})
    if row is None:
        print("No account with this email.", file=sys.stderr)
        return 1
    note = "" if row[1] == "active" else f" (the account is {row[1]}, so it cannot sign in yet)"
    print(f"Password set for account #{row[0]}{note}.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="python -m app.cli", description="Alumni Tracking command line tasks.")
    sub = parser.add_subparsers(dest="command", required=True)
    admin = sub.add_parser("create-admin", help="create an admin account (admins cannot register)")
    admin.add_argument("--name", required=True)
    admin.add_argument("--email", required=True)
    admin.add_argument("--department", default="System administration")
    password = sub.add_parser("set-password", help="give an existing account a (new) password")
    password.add_argument("--email", required=True)
    sub.add_parser("create-test-users", help="TEMPORARY: one test account per role, for the dev login")
    sub.add_parser("delete-test-users", help="remove the test accounts")
    sub.add_parser("purge-rejected", help="delete rejected accounts older than 30 days (also runs on its own)")
    args = parser.parse_args()
    if args.command == "create-test-users":
        from app import devlogin

        for role, user_id in devlogin.create_all():
            print(f"{role:9} test account #{user_id}")
        print("Sign in with one click on /login when DEV_LOGIN=1 is in .env.")
        return 0
    if args.command == "delete-test-users":
        from app import devlogin

        print(f"Deleted {devlogin.delete_all()} test account(s).")
        return 0
    if args.command == "purge-rejected":
        from app.models.registration import purge_rejected

        print(f"Deleted {purge_rejected()} rejected account(s) older than 30 days.")
        return 0
    if args.command == "create-admin":
        return create_admin(args.name, args.email, args.department)
    if args.command == "set-password":
        return set_password(args.email)
    return 1


if __name__ == "__main__":
    sys.exit(main())
