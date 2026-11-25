"""public profiles (experience, education, certificates) and CVs on applications (ddd.md 4.1.7)

Revision ID: 0010
Revises: 0009
Create Date: 2026-11-25
"""
from alembic import op
import sqlalchemy as sa

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def _owner(table: str) -> sa.Column:
    return sa.Column(
        "user_id", sa.Integer(),
        sa.ForeignKey("users.id", name=f"fk_{table}_user_id", ondelete="CASCADE"), nullable=False,
    )


def upgrade() -> None:
    op.create_table(
        "cv_files",
        sa.Column("id", sa.Integer(), primary_key=True),
        _owner("cv_files"),
        sa.Column("original_name", sa.String(200), nullable=False),
        sa.Column("stored_name", sa.String(80), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("uploaded_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("replaced_at", sa.TIMESTAMP(), nullable=True),
        sa.UniqueConstraint("stored_name", name="uq_cv_files_stored_name"),
    )
    op.create_index("ix_cv_files_user_id", "cv_files", ["user_id"])
    op.add_column(
        "applications",
        sa.Column("cv_file_id", sa.Integer(),
                  sa.ForeignKey("cv_files.id", name="fk_applications_cv_file_id", ondelete="SET NULL"), nullable=True),
    )

    op.create_table(
        "experiences",
        sa.Column("id", sa.Integer(), primary_key=True),
        _owner("experiences"),
        sa.Column("title", sa.String(120), nullable=False),
        sa.Column("company", sa.String(150), nullable=False),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("description", sa.String(1000), nullable=True),
        sa.CheckConstraint("end_date IS NULL OR end_date >= start_date", name="ck_experiences_dates"),
    )
    op.create_index("ix_experiences_user_id", "experiences", ["user_id"])

    op.create_table(
        "educations",
        sa.Column("id", sa.Integer(), primary_key=True),
        _owner("educations"),
        sa.Column("school", sa.String(150), nullable=False),
        sa.Column("degree", sa.String(100), nullable=True),
        sa.Column("field", sa.String(150), nullable=True),
        sa.Column("start_year", sa.Integer(), nullable=False),
        sa.Column("end_year", sa.Integer(), nullable=True),
        sa.Column("description", sa.String(1000), nullable=True),
        sa.CheckConstraint(
            "start_year BETWEEN 1950 AND 2100 AND (end_year IS NULL OR end_year BETWEEN start_year AND 2100)",
            name="ck_educations_years",
        ),
    )
    op.create_index("ix_educations_user_id", "educations", ["user_id"])

    op.create_table(
        "certificates",
        sa.Column("id", sa.Integer(), primary_key=True),
        _owner("certificates"),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("issuer", sa.String(150), nullable=False),
        sa.Column("issued_on", sa.Date(), nullable=True),
        sa.Column("credential_url", sa.String(300), nullable=True),
        sa.CheckConstraint(
            "credential_url IS NULL OR credential_url LIKE 'https://%'", name="ck_certificates_credential_url_https"
        ),
    )
    op.create_index("ix_certificates_user_id", "certificates", ["user_id"])


def downgrade() -> None:
    for table in ("certificates", "educations", "experiences"):
        op.drop_index(f"ix_{table}_user_id", table_name=table)
        op.drop_table(table)
    op.drop_column("applications", "cv_file_id")
    op.drop_index("ix_cv_files_user_id", table_name="cv_files")
    op.drop_table("cv_files")
    # The CV files stay in uploads/cv; remove that folder by hand after a downgrade.
