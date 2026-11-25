"""user roles and announcement authors (ddd.md section 4.1.1)

Revision ID: 0005
Revises: 0004
Create Date: 2026-11-25
"""
from alembic import op
import sqlalchemy as sa

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None

ROLES = "('student', 'alumni', 'academic', 'staff', 'admin')"
# Accounts created here for the authors that were free text; downgrade() finds them by this domain.
AUTHOR_EMAIL_DOMAIN = "staff.alumni-tracking.local"


def upgrade() -> None:
    # 1. users.role: every existing user is a graduate, so the default covers them all.
    op.add_column(
        "users", sa.Column("role", sa.String(20), nullable=False, server_default=sa.text("'alumni'"))
    )
    op.create_check_constraint("ck_users_role", "users", f"role IN {ROLES}")
    op.create_index("ix_users_role", "users", ["role"])

    # 2. graduation_year: required only for students and graduates.
    op.alter_column("users", "graduation_year", nullable=True, existing_type=sa.Integer())
    op.create_check_constraint(
        "ck_users_graduation_year_by_role",
        "users",
        "role NOT IN ('student', 'alumni') OR graduation_year IS NOT NULL",
    )

    # 3. One staff account for each author name already used by an announcement.
    op.execute(
        f"""
        INSERT INTO users (name, email, role, department)
        SELECT DISTINCT author,
               lower(regexp_replace(trim(author), '[^A-Za-z0-9]+', '-', 'g')) || '@{AUTHOR_EMAIL_DOMAIN}',
               'staff',
               'Faculty of Economics'
        FROM announcements
        """
    )

    # 4. announcements.author (text) -> author_id (a user).
    op.add_column(
        "announcements",
        sa.Column(
            "author_id",
            sa.Integer(),
            sa.ForeignKey("users.id", name="fk_announcements_author_id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index("ix_announcements_author_id", "announcements", ["author_id"])
    op.execute(
        f"""
        UPDATE announcements a SET author_id = u.id
        FROM users u
        WHERE u.name = a.author AND u.role = 'staff' AND u.email LIKE '%@{AUTHOR_EMAIL_DOMAIN}'
        """
    )
    op.drop_column("announcements", "author")


def downgrade() -> None:
    # announcements: put the author text back, from the users' names.
    op.add_column("announcements", sa.Column("author", sa.String(100), nullable=True))
    op.execute(
        "UPDATE announcements a SET author = COALESCE("
        "(SELECT u.name FROM users u WHERE u.id = a.author_id), 'Department')"
    )
    op.alter_column("announcements", "author", nullable=False, existing_type=sa.String(100))
    op.drop_index("ix_announcements_author_id", table_name="announcements")
    op.drop_column("announcements", "author_id")

    # users: remove the accounts made in upgrade(); everyone else needs a year again.
    op.execute(f"DELETE FROM users WHERE email LIKE '%@{AUTHOR_EMAIL_DOMAIN}'")
    op.drop_constraint("ck_users_graduation_year_by_role", "users", type_="check")
    op.execute("UPDATE users SET graduation_year = EXTRACT(YEAR FROM created_at) WHERE graduation_year IS NULL")
    op.alter_column("users", "graduation_year", nullable=False, existing_type=sa.Integer())
    op.drop_index("ix_users_role", table_name="users")
    op.drop_constraint("ck_users_role", "users", type_="check")
    op.drop_column("users", "role")
