from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, Date, ForeignKey, Index, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class GzContract(Base):
    __tablename__ = "gz_contracts"

    con_document_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    con_number: Mapped[Optional[str]] = mapped_column()
    con_date: Mapped[Optional[date]] = mapped_column(Date)
    con_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric)
    zakazchik_key: Mapped[Optional[str]] = mapped_column()

    budget_lines: Mapped[list["GzBudgetLine"]] = relationship(back_populates="contract")
    payments: Mapped[list["GzPayment"]] = relationship(back_populates="contract")


class GzBudgetLine(Base):
    __tablename__ = "gz_budget_lines"
    __table_args__ = (
        Index("ix_gz_budget_lines_contract_kcsr", "con_document_id", "kcsr_code"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    con_document_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("gz_contracts.con_document_id"),
        nullable=False,
    )
    kfsr_code: Mapped[Optional[str]] = mapped_column()
    kcsr_code: Mapped[str] = mapped_column(ForeignKey("kcsr_classifier.kcsr_code"))
    kvr_code: Mapped[Optional[str]] = mapped_column()
    kesr_code: Mapped[Optional[str]] = mapped_column()
    kvsr_code: Mapped[Optional[str]] = mapped_column()
    purposefulgrant: Mapped[Optional[str]] = mapped_column()

    contract: Mapped["GzContract"] = relationship(back_populates="budget_lines")
    kcsr: Mapped["KcsrClassifier"] = relationship(back_populates="gz_budget_lines")


class GzPayment(Base):
    __tablename__ = "gz_payments"
    __table_args__ = (
        Index("ix_gz_payments_contract_date", "con_document_id", "platezhka_paydate"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    con_document_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("gz_contracts.con_document_id"),
        nullable=False,
    )
    platezhka_paydate: Mapped[Optional[date]] = mapped_column(Date)
    platezhka_key: Mapped[Optional[str]] = mapped_column()
    platezhka_num: Mapped[Optional[str]] = mapped_column()
    platezhka_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric)

    contract: Mapped["GzContract"] = relationship(back_populates="payments")
