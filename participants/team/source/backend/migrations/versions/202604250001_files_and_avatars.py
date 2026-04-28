"""files and avatar linkage

Revision ID: 202604250001
Revises: 202604240001
Create Date: 2026-04-25
"""

from alembic import op
import sqlalchemy as sa

revision = "202604250001"
down_revision = "202604240001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "files",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=True),
        sa.Column("original_name", sa.String(length=255), nullable=False),
        sa.Column("stored_name", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=127), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("access_scope", sa.String(length=32), server_default=sa.text("'private'"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stored_name"),
    )
    op.create_index(op.f("ix_files_access_scope"), "files", ["access_scope"], unique=False)
    op.create_index(op.f("ix_files_owner_id"), "files", ["owner_id"], unique=False)
    op.create_index(op.f("ix_files_stored_name"), "files", ["stored_name"], unique=False)

    op.add_column("users", sa.Column("avatar_file_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_users_avatar_file_id"), "users", ["avatar_file_id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_users_avatar_file_id"), table_name="users")
    op.drop_column("users", "avatar_file_id")

    op.drop_index(op.f("ix_files_stored_name"), table_name="files")
    op.drop_index(op.f("ix_files_owner_id"), table_name="files")
    op.drop_index(op.f("ix_files_access_scope"), table_name="files")
    op.drop_table("files")

