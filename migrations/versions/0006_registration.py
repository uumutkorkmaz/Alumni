"""registration: account status, password hash, role fields, registration documents (ddd.md 4.1.2)

Revision ID: 0006
Revises: 0005
Create Date: 2026-11-25
"""
from alembic import op
import sqlalchemy as sa

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Existing and seeded users are active accounts; registrations start as pending.
    op.add_column(
        "users", sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'active'"))
    )
    op.create_check_constraint("ck_users_status", "users", "status IN ('pending', 'active', 'rejected')")
    op.create_index("ix_users_status", "users", ["status"])

    op.add_column("users", sa.Column("password_hash", sa.String(255), nullable=True))
    op.add_column("users", sa.Column("student_number", sa.String(20), nullable=True))
    op.create_unique_constraint("uq_users_student_number", "users", ["student_number"])
    op.add_column("users", sa.Column("title", sa.String(40), nullable=True))
    op.add_column("users", sa.Column("position", sa.String(100), nullable=True))
    op.add_column("users", sa.Column("consent_at", sa.TIMESTAMP(), nullable=True))
    op.add_column("users", sa.Column("reviewed_at", sa.TIMESTAMP(), nullable=True))
    op.add_column(
        "users",
        sa.Column(
            "reviewed_by_user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", name="fk_users_reviewed_by_user_id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.add_column("users", sa.Column("rejection_reason", sa.String(300), nullable=True))
    op.create_check_constraint(
        "ck_users_rejection_reason", "users", "status <> 'rejected' OR rejection_reason IS NOT NULL"
    )

    op.create_table(
        "registration_documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", name="fk_registration_documents_user_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("original_name", sa.String(255), nullable=False),
        sa.Column("stored_name", sa.String(64), nullable=False),
        sa.Column("content_type", sa.String(40), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("uploaded_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("file_deleted_at", sa.TIMESTAMP(), nullable=True),
        sa.UniqueConstraint("user_id", name="uq_registration_documents_user_id"),
        sa.UniqueConstraint("stored_name", name="uq_registration_documents_stored_name"),
        sa.CheckConstraint(
            "content_type IN ('application/pdf', 'image/jpeg', 'image/png')",
            name="ck_registration_documents_content_type",
        ),
        sa.CheckConstraint("size_bytes BETWEEN 1 AND 5242880", name="ck_registration_documents_size"),
    )


def downgrade() -> None:
    op.drop_table("registration_documents")
    # Accounts that were never approved did not exist before 0006.
    op.execute("DELETE FROM users WHERE status <> 'active'")
    op.drop_constraint("ck_users_rejection_reason", "users", type_="check")
    op.drop_column("users", "rejection_reason")
    op.drop_column("users", "reviewed_by_user_id")
    op.drop_column("users", "reviewed_at")
    op.drop_column("users", "consent_at")
    op.drop_column("users", "position")
    op.drop_column("users", "title")
    op.drop_constraint("uq_users_student_number", "users", type_="unique")
    op.drop_column("users", "student_number")
    op.drop_column("users", "password_hash")
    op.drop_index("ix_users_status", table_name="users")
    op.drop_constraint("ck_users_status", "users", type_="check")
    op.drop_column("users", "status")
