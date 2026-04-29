"""Case import fixes

Revision ID: b7f4d3c2a901
Revises: 1a5c96301b91
Create Date: 2026-04-28 16:45:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b7f4d3c2a901"
down_revision: Union[str, Sequence[str], None] = "1a5c96301b91"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("agreements", sa.Column("id", sa.BigInteger(), nullable=True))
    op.execute("CREATE SEQUENCE IF NOT EXISTS agreements_id_seq")
    op.execute(
        "UPDATE agreements SET id = nextval('agreements_id_seq') WHERE id IS NULL"
    )
    op.execute(
        "ALTER TABLE agreements ALTER COLUMN id SET DEFAULT nextval('agreements_id_seq')"
    )
    op.execute("ALTER TABLE agreements ALTER COLUMN id SET NOT NULL")
    op.execute("ALTER SEQUENCE agreements_id_seq OWNED BY agreements.id")
    op.execute("ALTER TABLE agreements DROP CONSTRAINT IF EXISTS agreements_pkey")
    op.create_primary_key("agreements_pkey", "agreements", ["id"])
    op.create_index("ix_agreements_document_id", "agreements", ["document_id"])
    op.create_index(
        "ix_agreements_kcsr_period",
        "agreements",
        ["kcsr_code", "period_of_date"],
    )

    op.execute(
        "ALTER TABLE gz_budget_lines "
        "DROP CONSTRAINT IF EXISTS gz_budget_lines_con_document_id_fkey"
    )
    op.execute(
        "ALTER TABLE gz_payments "
        "DROP CONSTRAINT IF EXISTS gz_payments_con_document_id_fkey"
    )
    op.alter_column(
        "gz_contracts",
        "con_document_id",
        existing_type=sa.Integer(),
        type_=sa.BigInteger(),
        existing_nullable=False,
    )
    op.alter_column(
        "gz_budget_lines",
        "con_document_id",
        existing_type=sa.Integer(),
        type_=sa.BigInteger(),
        existing_nullable=False,
    )
    op.alter_column(
        "gz_payments",
        "con_document_id",
        existing_type=sa.Integer(),
        type_=sa.BigInteger(),
        existing_nullable=False,
    )
    op.create_foreign_key(
        "gz_budget_lines_con_document_id_fkey",
        "gz_budget_lines",
        "gz_contracts",
        ["con_document_id"],
        ["con_document_id"],
    )
    op.create_foreign_key(
        "gz_payments_con_document_id_fkey",
        "gz_payments",
        "gz_contracts",
        ["con_document_id"],
        ["con_document_id"],
    )

    op.create_index(
        "ix_rcb_execution_period_kcsr",
        "rcb_execution",
        ["budget_period", "kcsr_code"],
    )
    op.create_index(
        "ix_buau_payments_period_kcsr",
        "buau_payments",
        ["budget_period", "kcsr_code"],
    )
    op.create_index(
        "ix_gz_budget_lines_contract_kcsr",
        "gz_budget_lines",
        ["con_document_id", "kcsr_code"],
    )
    op.create_index(
        "ix_gz_payments_contract_date",
        "gz_payments",
        ["con_document_id", "platezhka_paydate"],
    )


def downgrade() -> None:
    op.drop_index("ix_gz_payments_contract_date", table_name="gz_payments")
    op.drop_index("ix_gz_budget_lines_contract_kcsr", table_name="gz_budget_lines")
    op.drop_index("ix_buau_payments_period_kcsr", table_name="buau_payments")
    op.drop_index("ix_rcb_execution_period_kcsr", table_name="rcb_execution")

    op.execute(
        "ALTER TABLE gz_payments "
        "DROP CONSTRAINT IF EXISTS gz_payments_con_document_id_fkey"
    )
    op.execute(
        "ALTER TABLE gz_budget_lines "
        "DROP CONSTRAINT IF EXISTS gz_budget_lines_con_document_id_fkey"
    )
    op.alter_column(
        "gz_payments",
        "con_document_id",
        existing_type=sa.BigInteger(),
        type_=sa.Integer(),
        existing_nullable=False,
    )
    op.alter_column(
        "gz_budget_lines",
        "con_document_id",
        existing_type=sa.BigInteger(),
        type_=sa.Integer(),
        existing_nullable=False,
    )
    op.alter_column(
        "gz_contracts",
        "con_document_id",
        existing_type=sa.BigInteger(),
        type_=sa.Integer(),
        existing_nullable=False,
    )
    op.create_foreign_key(
        "gz_budget_lines_con_document_id_fkey",
        "gz_budget_lines",
        "gz_contracts",
        ["con_document_id"],
        ["con_document_id"],
    )
    op.create_foreign_key(
        "gz_payments_con_document_id_fkey",
        "gz_payments",
        "gz_contracts",
        ["con_document_id"],
        ["con_document_id"],
    )

    op.drop_index("ix_agreements_kcsr_period", table_name="agreements")
    op.drop_index("ix_agreements_document_id", table_name="agreements")
    op.execute("ALTER TABLE agreements DROP CONSTRAINT IF EXISTS agreements_pkey")
    op.create_primary_key("agreements_pkey", "agreements", ["document_id"])
    op.drop_column("agreements", "id")
    op.execute("DROP SEQUENCE IF EXISTS agreements_id_seq")
