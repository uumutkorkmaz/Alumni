"""job posting validation rules (ddd.md section 4.3.1)

Revision ID: 0004
Revises: 0003
Create Date: 2026-11-11
"""
from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "job_postings", "title", type_=sa.String(120), existing_type=sa.String(200), existing_nullable=False
    )
    op.alter_column("job_postings", "location", new_column_name="city")
    op.alter_column("job_postings", "description", nullable=True, existing_type=sa.Text())
    op.create_check_constraint(
        "ck_job_postings_description_or_url",
        "job_postings",
        "description IS NOT NULL OR application_url IS NOT NULL",
    )


def downgrade() -> None:
    op.drop_constraint("ck_job_postings_description_or_url", "job_postings", type_="check")
    # description becomes required again, so postings that only had a URL need a description first.
    op.execute("UPDATE job_postings SET description = application_url WHERE description IS NULL")
    op.alter_column("job_postings", "description", nullable=False, existing_type=sa.Text())
    op.alter_column("job_postings", "city", new_column_name="location")
    op.alter_column(
        "job_postings", "title", type_=sa.String(200), existing_type=sa.String(120), existing_nullable=False
    )
