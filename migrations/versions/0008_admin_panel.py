"""admin panel: audit log and the suspended status (ddd.md 4.1.4)

Revision ID: 0008
Revises: 0007
Create Date: 2026-11-25
"""
from alembic import op
import sqlalchemy as sa

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("ck_users_status", "users", type_="check")
    op.create_check_constraint(
        "ck_users_status", "users", "status IN ('pending', 'active', 'rejected', 'suspended')"
    )
    op.create_table(
        "admin_audit",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "admin_user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", name="fk_admin_audit_admin_user_id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("admin_name", sa.String(100), nullable=False),
        sa.Column("action", sa.String(40), nullable=False),
        sa.Column("target_type", sa.String(30), nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=True),
        sa.Column("details", sa.String(300), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_admin_audit_created_at", "admin_audit", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_admin_audit_created_at", table_name="admin_audit")
    op.drop_table("admin_audit")
    # suspended did not exist before 0008: those accounts become active again.
    op.execute("UPDATE users SET status = 'active' WHERE status = 'suspended'")
    op.drop_constraint("ck_users_status", "users", type_="check")
    op.create_check_constraint("ck_users_status", "users", "status IN ('pending', 'active', 'rejected')")
