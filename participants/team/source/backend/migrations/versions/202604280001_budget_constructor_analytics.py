"""budget constructor analytics tables

Revision ID: 202604280001
Revises: 202604250001
Create Date: 2026-04-28
"""

from alembic import op
import sqlalchemy as sa

revision = "202604280001"
down_revision = "202604250001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "analytics_source_files",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("original_name", sa.String(length=255), nullable=False),
        sa.Column("stored_path", sa.Text(), nullable=True),
        sa.Column("period_date", sa.Date(), nullable=True),
        sa.Column("checksum", sa.String(length=64), nullable=False),
        sa.Column("rows_total", sa.Integer(), nullable=False),
        sa.Column("rows_imported", sa.Integer(), nullable=False),
        sa.Column("warnings_count", sa.Integer(), nullable=False),
        sa.Column("errors_count", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_analytics_source_files_checksum"), "analytics_source_files", ["checksum"], unique=False)
    op.create_index(op.f("ix_analytics_source_files_period_date"), "analytics_source_files", ["period_date"], unique=False)
    op.create_index(op.f("ix_analytics_source_files_source_type"), "analytics_source_files", ["source_type"], unique=False)
    op.create_index(op.f("ix_analytics_source_files_status"), "analytics_source_files", ["status"], unique=False)

    op.create_table(
        "analytics_agreements",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_file_id", sa.Integer(), nullable=False),
        sa.Column("period_date", sa.Date(), nullable=True),
        sa.Column("documentclass_id", sa.String(length=32), nullable=True),
        sa.Column("budget_id", sa.String(length=128), nullable=True),
        sa.Column("budget_caption", sa.Text(), nullable=True),
        sa.Column("document_id", sa.String(length=128), nullable=True),
        sa.Column("close_date", sa.Date(), nullable=True),
        sa.Column("reg_number", sa.String(length=255), nullable=True),
        sa.Column("main_close_date", sa.Date(), nullable=True),
        sa.Column("main_reg_number", sa.String(length=255), nullable=True),
        sa.Column("amount_1year", sa.Numeric(20, 2), nullable=False),
        sa.Column("estimate_caption", sa.Text(), nullable=True),
        sa.Column("recipient_caption", sa.Text(), nullable=True),
        sa.Column("kadmr_code", sa.String(length=64), nullable=True),
        sa.Column("kadmr_norm", sa.String(length=64), nullable=True),
        sa.Column("kfsr_code", sa.String(length=64), nullable=True),
        sa.Column("kfsr_norm", sa.String(length=64), nullable=True),
        sa.Column("kcsr_code", sa.String(length=64), nullable=True),
        sa.Column("kcsr_norm", sa.String(length=64), nullable=True),
        sa.Column("kvr_code", sa.String(length=64), nullable=True),
        sa.Column("kvr_norm", sa.String(length=64), nullable=True),
        sa.Column("kesr_code", sa.String(length=64), nullable=True),
        sa.Column("kesr_norm", sa.String(length=64), nullable=True),
        sa.Column("purposefulgrant_code", sa.String(length=128), nullable=True),
        sa.Column("purposefulgrant_norm", sa.String(length=128), nullable=True),
        sa.Column("kdr_code", sa.String(length=64), nullable=True),
        sa.Column("kdr_norm", sa.String(length=64), nullable=True),
        sa.Column("kde_code", sa.String(length=64), nullable=True),
        sa.Column("kde_norm", sa.String(length=64), nullable=True),
        sa.Column("kdf_code", sa.String(length=64), nullable=True),
        sa.Column("kdf_norm", sa.String(length=64), nullable=True),
        sa.Column("grantinvestment_code", sa.String(length=128), nullable=True),
        sa.Column("grantinvestment_norm", sa.String(length=128), nullable=True),
        sa.Column("raw", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["source_file_id"], ["analytics_source_files.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    _index_many(
        "analytics_agreements",
        [
            "source_file_id",
            "period_date",
            "documentclass_id",
            "document_id",
            "close_date",
            "reg_number",
            "kadmr_norm",
            "kfsr_norm",
            "kcsr_norm",
            "kvr_norm",
            "kesr_norm",
            "purposefulgrant_norm",
            "kdr_norm",
            "kde_norm",
            "kdf_norm",
            "grantinvestment_norm",
        ],
    )

    op.create_table(
        "analytics_budget_facts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_file_id", sa.Integer(), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("period_date", sa.Date(), nullable=True),
        sa.Column("budget_name", sa.Text(), nullable=True),
        sa.Column("posting_date", sa.Date(), nullable=True),
        sa.Column("kfsr_code", sa.String(length=64), nullable=True),
        sa.Column("kfsr_norm", sa.String(length=64), nullable=True),
        sa.Column("kfsr_name", sa.Text(), nullable=True),
        sa.Column("kcsr_code", sa.String(length=64), nullable=True),
        sa.Column("kcsr_norm", sa.String(length=64), nullable=True),
        sa.Column("kcsr_name", sa.Text(), nullable=True),
        sa.Column("kvr_code", sa.String(length=64), nullable=True),
        sa.Column("kvr_norm", sa.String(length=64), nullable=True),
        sa.Column("kvr_name", sa.Text(), nullable=True),
        sa.Column("kvsr_code", sa.String(length=64), nullable=True),
        sa.Column("kvsr_norm", sa.String(length=64), nullable=True),
        sa.Column("kvsr_name", sa.Text(), nullable=True),
        sa.Column("kesr_code", sa.String(length=64), nullable=True),
        sa.Column("kesr_norm", sa.String(length=64), nullable=True),
        sa.Column("purposefulgrant_code", sa.String(length=128), nullable=True),
        sa.Column("purposefulgrant_norm", sa.String(length=128), nullable=True),
        sa.Column("kdr_code", sa.String(length=64), nullable=True),
        sa.Column("kdr_norm", sa.String(length=64), nullable=True),
        sa.Column("kde_code", sa.String(length=64), nullable=True),
        sa.Column("kde_norm", sa.String(length=64), nullable=True),
        sa.Column("kdf_code", sa.String(length=64), nullable=True),
        sa.Column("kdf_norm", sa.String(length=64), nullable=True),
        sa.Column("limits_amount", sa.Numeric(20, 2), nullable=False),
        sa.Column("accepted_bo_amount", sa.Numeric(20, 2), nullable=False),
        sa.Column("accepted_without_bo_amount", sa.Numeric(20, 2), nullable=False),
        sa.Column("remaining_limits_amount", sa.Numeric(20, 2), nullable=False),
        sa.Column("cash_amount", sa.Numeric(20, 2), nullable=False),
        sa.Column("buau_payment_amount", sa.Numeric(20, 2), nullable=False),
        sa.Column("buau_execution_amount", sa.Numeric(20, 2), nullable=False),
        sa.Column("buau_recovery_amount", sa.Numeric(20, 2), nullable=False),
        sa.Column("buau_organization", sa.Text(), nullable=True),
        sa.Column("buau_grantor", sa.Text(), nullable=True),
        sa.Column("raw", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["source_file_id"], ["analytics_source_files.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    _index_many(
        "analytics_budget_facts",
        [
            "source_file_id",
            "source_type",
            "period_date",
            "posting_date",
            "kfsr_norm",
            "kcsr_norm",
            "kvr_norm",
            "kvsr_norm",
            "kesr_norm",
            "purposefulgrant_norm",
            "kdr_norm",
            "kde_norm",
            "kdf_norm",
        ],
    )

    op.create_table(
        "analytics_contracts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_file_id", sa.Integer(), nullable=False),
        sa.Column("con_document_id", sa.String(length=128), nullable=False),
        sa.Column("con_number", sa.String(length=255), nullable=True),
        sa.Column("con_date", sa.Date(), nullable=True),
        sa.Column("con_amount", sa.Numeric(20, 2), nullable=False),
        sa.Column("zakazchik_key", sa.Text(), nullable=True),
        sa.Column("raw", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["source_file_id"], ["analytics_source_files.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    _index_many("analytics_contracts", ["source_file_id", "con_document_id", "con_number", "con_date"])

    op.create_table(
        "analytics_contract_budget_lines",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_file_id", sa.Integer(), nullable=False),
        sa.Column("con_document_id", sa.String(length=128), nullable=False),
        sa.Column("kfsr_code", sa.String(length=64), nullable=True),
        sa.Column("kfsr_norm", sa.String(length=64), nullable=True),
        sa.Column("kcsr_code", sa.String(length=64), nullable=True),
        sa.Column("kcsr_norm", sa.String(length=64), nullable=True),
        sa.Column("kvr_code", sa.String(length=64), nullable=True),
        sa.Column("kvr_norm", sa.String(length=64), nullable=True),
        sa.Column("kesr_code", sa.String(length=64), nullable=True),
        sa.Column("kesr_norm", sa.String(length=64), nullable=True),
        sa.Column("kvsr_code", sa.String(length=64), nullable=True),
        sa.Column("kvsr_norm", sa.String(length=64), nullable=True),
        sa.Column("kdf_code", sa.String(length=64), nullable=True),
        sa.Column("kdf_norm", sa.String(length=64), nullable=True),
        sa.Column("kde_code", sa.String(length=64), nullable=True),
        sa.Column("kde_norm", sa.String(length=64), nullable=True),
        sa.Column("kdr_code", sa.String(length=64), nullable=True),
        sa.Column("kdr_norm", sa.String(length=64), nullable=True),
        sa.Column("kif_code", sa.String(length=64), nullable=True),
        sa.Column("kif_norm", sa.String(length=64), nullable=True),
        sa.Column("purposefulgrant_code", sa.String(length=128), nullable=True),
        sa.Column("purposefulgrant_norm", sa.String(length=128), nullable=True),
        sa.Column("allocation_share", sa.Numeric(18, 10), nullable=False),
        sa.Column("allocation_method", sa.String(length=64), nullable=False),
        sa.Column("raw", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["source_file_id"], ["analytics_source_files.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    _index_many(
        "analytics_contract_budget_lines",
        [
            "source_file_id",
            "con_document_id",
            "kfsr_norm",
            "kcsr_norm",
            "kvr_norm",
            "kesr_norm",
            "kvsr_norm",
            "kdf_norm",
            "kde_norm",
            "kdr_norm",
            "kif_norm",
            "purposefulgrant_norm",
            "allocation_method",
        ],
    )

    op.create_table(
        "analytics_import_issues",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_file_id", sa.Integer(), nullable=True),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("row_number", sa.Integer(), nullable=True),
        sa.Column("raw", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["source_file_id"], ["analytics_source_files.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    _index_many("analytics_import_issues", ["source_file_id", "severity", "code"])

    op.create_table(
        "analytics_payments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_file_id", sa.Integer(), nullable=False),
        sa.Column("con_document_id", sa.String(length=128), nullable=False),
        sa.Column("platezhka_paydate", sa.Date(), nullable=True),
        sa.Column("platezhka_key", sa.String(length=128), nullable=True),
        sa.Column("platezhka_num", sa.String(length=128), nullable=True),
        sa.Column("platezhka_amount", sa.Numeric(20, 2), nullable=False),
        sa.Column("linked_to_budget_line", sa.Boolean(), nullable=False),
        sa.Column("raw", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["source_file_id"], ["analytics_source_files.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    _index_many(
        "analytics_payments",
        ["source_file_id", "con_document_id", "platezhka_paydate", "platezhka_key", "platezhka_num", "linked_to_budget_line"],
    )


def downgrade():
    op.drop_table("analytics_payments")
    op.drop_index(op.f("ix_analytics_import_issues_code"), table_name="analytics_import_issues")
    op.drop_index(op.f("ix_analytics_import_issues_severity"), table_name="analytics_import_issues")
    op.drop_index(op.f("ix_analytics_import_issues_source_file_id"), table_name="analytics_import_issues")
    op.drop_table("analytics_import_issues")
    op.drop_table("analytics_contract_budget_lines")
    op.drop_table("analytics_contracts")
    op.drop_table("analytics_budget_facts")
    op.drop_table("analytics_agreements")
    op.drop_index(op.f("ix_analytics_source_files_status"), table_name="analytics_source_files")
    op.drop_index(op.f("ix_analytics_source_files_source_type"), table_name="analytics_source_files")
    op.drop_index(op.f("ix_analytics_source_files_period_date"), table_name="analytics_source_files")
    op.drop_index(op.f("ix_analytics_source_files_checksum"), table_name="analytics_source_files")
    op.drop_table("analytics_source_files")


def _index_many(table_name: str, columns: list[str]) -> None:
    for column in columns:
        op.create_index(op.f(f"ix_{table_name}_{column}"), table_name, [column], unique=False)

