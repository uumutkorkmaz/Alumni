"""user pages: career profile fields and saved job postings (ddd.md 4.1.6)

Revision ID: 0009
Revises: 0008
Create Date: 2026-11-25
"""
from alembic import op
import sqlalchemy as sa

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # The career profile a person fills in on /me/profile (none of it is checked at registration).
    op.add_column("users", sa.Column("company", sa.String(150), nullable=True))
    op.add_column("users", sa.Column("job_title", sa.String(120), nullable=True))
    op.add_column("users", sa.Column("city", sa.String(100), nullable=True))
    op.add_column("users", sa.Column("linkedin_url", sa.String(300), nullable=True))
    op.add_column("users", sa.Column("bio", sa.String(500), nullable=True))
    op.create_check_constraint(
        "ck_users_linkedin_url_https", "users", "linkedin_url IS NULL OR linkedin_url LIKE 'https://%'"
    )
    op.create_table(
        "saved_postings",
        sa.Column(
            "user_id", sa.Integer(),
            sa.ForeignKey("users.id", name="fk_saved_postings_user_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "job_posting_id", sa.Integer(),
            sa.ForeignKey("job_postings.id", name="fk_saved_postings_job_posting_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_saved_postings_job_posting_id", "saved_postings", ["job_posting_id"])


def downgrade() -> None:
    op.drop_index("ix_saved_postings_job_posting_id", table_name="saved_postings")
    op.drop_table("saved_postings")
    op.drop_constraint("ck_users_linkedin_url_https", "users", type_="check")
    for column in ("bio", "linkedin_url", "city", "job_title", "company"):
        op.drop_column("users", column)
