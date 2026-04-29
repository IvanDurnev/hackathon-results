from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, Date, ForeignKey, Index, Numeric
from app.core.database import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship


class Agreement(Base):
    """Соглашения"""

    __tablename__ = "agreements"
    __table_args__ = (
        Index("ix_agreements_document_id", "document_id"),
        Index("ix_agreements_kcsr_period", "kcsr_code", "period_of_date"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    document_id: Mapped[int] = mapped_column(BigInteger, autoincrement=False)

    period_of_date: Mapped[Optional[date]] = mapped_column(Date, comment="Дата среза")
    documentclass_id: Mapped[Optional[int]] = mapped_column(comment="Тип документа")
    budget_id: Mapped[Optional[str]] = mapped_column(comment="ID бюджета")
    caption: Mapped[Optional[str]] = mapped_column(comment="Наименование бюджета")
    close_date: Mapped[Optional[date]] = mapped_column(Date, comment="Дата закрытия")
    reg_number: Mapped[Optional[str]] = mapped_column(comment="Рег. номер")
    kadmr_code: Mapped[Optional[str]] = mapped_column(comment="КАДМР")
    kfsr_code: Mapped[Optional[str]] = mapped_column(comment="КФСР")

    kcsr_code: Mapped[str] = mapped_column(
        ForeignKey("kcsr_classifier.kcsr_code"), comment="КЦСР"
    )

    kvr_code: Mapped[Optional[str]] = mapped_column(comment="КВР")
    kesr_code: Mapped[Optional[str]] = mapped_column(comment="КОСГУ")
    purposefulgrant_code: Mapped[Optional[str]] = mapped_column(comment="Код субсидии")
    amount_1year: Mapped[Optional[Decimal]] = mapped_column(
        Numeric, comment="Сумма (год)"
    )
    dd_recipient_caption: Mapped[Optional[str]] = mapped_column(comment="Получатель")
    dd_estimate_caption: Mapped[Optional[str]] = mapped_column(
        comment="Наименование сметы"
    )

    kcsr: Mapped["KcsrClassifier"] = relationship(back_populates="agreements")
