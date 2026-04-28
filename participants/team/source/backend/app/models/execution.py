from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import Date, ForeignKey, Index, Numeric
from app.core.database import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship


class RcbExecution(Base):
    """Исполнение бюджета (РКБ)"""

    __tablename__ = "rcb_execution"
    __table_args__ = (
        Index("ix_rcb_execution_period_kcsr", "budget_period", "kcsr_code"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    budget_name: Mapped[Optional[str]] = mapped_column(comment="Наименование бюджета")
    posting_date: Mapped[Optional[date]] = mapped_column(Date, comment="Дата проводки")
    kfsr_code: Mapped[Optional[str]] = mapped_column(comment="КФСР")
    kfsr_name: Mapped[Optional[str]] = mapped_column(comment="Наименование КФСР")

    kcsr_code: Mapped[str] = mapped_column(
        ForeignKey("kcsr_classifier.kcsr_code"), comment="КЦСР"
    )
    kcsr_name: Mapped[Optional[str]] = mapped_column(comment="Наименование КЦСР")

    kvr_code: Mapped[Optional[str]] = mapped_column(comment="КВР")
    kvr_name: Mapped[Optional[str]] = mapped_column(comment="Наименование КВР")
    kvsr_code: Mapped[Optional[str]] = mapped_column(comment="КВСР")
    kosgu_code: Mapped[Optional[str]] = mapped_column(comment="КОСГУ")
    fund_source: Mapped[Optional[str]] = mapped_column(comment="Источник средств")

    limit_pbs_cur_year: Mapped[Optional[Decimal]] = mapped_column(
        Numeric, comment="Лимиты ПБС"
    )
    limit_confirmed: Mapped[Optional[Decimal]] = mapped_column(
        Numeric, comment="Подтв. лимиты по БО"
    )
    limit_remaining: Mapped[Optional[Decimal]] = mapped_column(
        Numeric, comment="Остаток лимитов"
    )
    total_payments: Mapped[Optional[Decimal]] = mapped_column(
        Numeric, comment="Всего выбытий"
    )
    budget_period: Mapped[Optional[str]] = mapped_column(
        comment="Отчётный период (месяц-год)"
    )

    kcsr: Mapped["KcsrClassifier"] = relationship(back_populates="rcb_executions")


class BuauPayment(Base):
    """Выплаты БУ/АУ (Бюджетные и автономные учреждения)"""

    __tablename__ = "buau_payments"
    __table_args__ = (
        Index("ix_buau_payments_period_kcsr", "budget_period", "kcsr_code"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    budget_name: Mapped[Optional[str]] = mapped_column(comment="Наименование бюджета")
    posting_date: Mapped[Optional[date]] = mapped_column(Date, comment="Дата проводки")
    kfsr_code: Mapped[Optional[str]] = mapped_column(comment="КФСР")

    kcsr_code: Mapped[str] = mapped_column(
        ForeignKey("kcsr_classifier.kcsr_code"), comment="КЦСР"
    )

    kvr_code: Mapped[Optional[str]] = mapped_column(comment="КВР")
    kosgu_code: Mapped[Optional[str]] = mapped_column(comment="КОСГУ")
    subsidy_code: Mapped[Optional[str]] = mapped_column(comment="Код субсидии")
    branch_code: Mapped[Optional[str]] = mapped_column(comment="Отраслевой код")
    kvfo_code: Mapped[Optional[str]] = mapped_column(comment="КВФО")
    organization_name: Mapped[Optional[str]] = mapped_column(comment="Организация")
    grantor_name: Mapped[Optional[str]] = mapped_column(comment="Орган-грантодатель")

    payments_net: Mapped[Optional[Decimal]] = mapped_column(
        Numeric, comment="Выплаты с учётом возвратов"
    )
    payments_execution: Mapped[Optional[Decimal]] = mapped_column(
        Numeric, comment="Выплаты — исполнение"
    )
    payments_restore: Mapped[Optional[Decimal]] = mapped_column(
        Numeric, comment="Восстановление выплат"
    )
    budget_period: Mapped[Optional[str]] = mapped_column(comment="Отчётный период")

    kcsr: Mapped["KcsrClassifier"] = relationship(back_populates="buau_payments")
