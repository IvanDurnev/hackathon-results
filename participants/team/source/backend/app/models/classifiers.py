from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime
from app.core.database import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship


class KcsrClassifier(Base):
    """Справочник КЦСР (Код целевой статьи расходов)"""

    __tablename__ = "kcsr_classifier"

    kcsr_code: Mapped[str] = mapped_column(
        primary_key=True, comment="КЦСР (ключ связи)"
    )
    kcsr_name: Mapped[Optional[str]] = mapped_column(
        comment="Наименование целевой статьи"
    )
    program_code: Mapped[Optional[str]] = mapped_column(comment="Код программы")
    subprogram_code: Mapped[Optional[str]] = mapped_column(comment="Код подпрограммы")
    direction_code: Mapped[Optional[str]] = mapped_column(
        comment="Код направления расходов"
    )
    kcsr_level: Mapped[Optional[str]] = mapped_column(comment="Уровень (фед/рег/муниц)")
    valid_from: Mapped[Optional[datetime]] = mapped_column(DateTime)
    valid_to: Mapped[Optional[datetime]] = mapped_column(DateTime)

    rcb_executions: Mapped[list["RcbExecution"]] = relationship(back_populates="kcsr")
    agreements: Mapped[list["Agreement"]] = relationship(back_populates="kcsr")
    gz_budget_lines: Mapped[list["GzBudgetLine"]] = relationship(back_populates="kcsr")
    buau_payments: Mapped[list["BuauPayment"]] = relationship(back_populates="kcsr")
