"""reapplying after a rejection: count the applications of an account (ddd.md 4.1.2)

Revision ID: 0011
Revises: 0010
Create Date: 2026-11-25
"""
from alembic import op
import sqlalchemy as sa

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1 for every existing account; a rejected person may apply again, at most 3 times in all.
    op.add_column(
        "users", sa.Column("application_count", sa.Integer(), nullable=False, server_default=sa.text("1"))
    )
    op.create_check_constraint("ck_users_application_count", "users", "application_count BETWEEN 1 AND 3")


def downgrade() -> None:
    op.drop_constraint("ck_users_application_count", "users", type_="check")
    op.drop_column("users", "application_count")
