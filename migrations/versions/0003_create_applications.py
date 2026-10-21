"""create applications table

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-21
"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "applications",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", name="fk_applications_user_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "job_posting_id",
            sa.Integer(),
            sa.ForeignKey("job_postings.id", name="fk_applications_job_posting_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(20), nullable=False, server_default="submitted"),
        sa.Column("cover_letter", sa.Text(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("user_id", "job_posting_id", name="uq_applications_user_id_job_posting_id"),
        sa.CheckConstraint(
            "status IN ('submitted', 'under_review', 'interview', 'accepted', 'rejected', 'withdrawn')",
            name="ck_applications_status",
        ),
    )
    op.create_index("ix_applications_job_posting_id", "applications", ["job_posting_id"])


def downgrade() -> None:
    op.drop_index("ix_applications_job_posting_id", table_name="applications")
    op.drop_table("applications")
