"""create job_postings table

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-21
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "job_postings",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("company", sa.String(150), nullable=False),
        sa.Column("location", sa.String(150), nullable=False),
        sa.Column("employment_type", sa.String(20), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("application_url", sa.String(500), nullable=True),
        sa.Column("deadline", sa.Date(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("TRUE")),
        sa.Column(
            "posted_by_user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", name="fk_job_postings_posted_by_user_id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.CheckConstraint(
            "employment_type IN ('full_time', 'part_time', 'internship', 'contract')",
            name="ck_job_postings_employment_type",
        ),
    )
    op.create_index("ix_job_postings_posted_by_user_id", "job_postings", ["posted_by_user_id"])


def downgrade() -> None:
    op.drop_index("ix_job_postings_posted_by_user_id", table_name="job_postings")
    op.drop_table("job_postings")
