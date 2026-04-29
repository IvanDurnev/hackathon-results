from datetime import datetime
from typing import Optional
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.analytics_repository import AnalyticsRepository


class AnalyticsService:
    def __init__(self, repository: AnalyticsRepository):
        self.repository = repository

    async def get_budget_names(self, db: AsyncSession):
        return await self.repository.get_budget_names(db=db)

    async def get_kcsrs(self, db: AsyncSession):
        return await self.repository.get_kcsrs(db=db)

    async def get_constructor_report(
        self,
        db: AsyncSession,
        kcsr_mask: str,
        budget_name: str,
        period_from: str,
        period_to: str,
        fund_source: Optional[str] = None,
        min_amount: Decimal = Decimal("0"),
    ):

        # 1. Валидация логики периодов
        self._validate_periods(period_from, period_to)

        # 2. Очистка входных данных (trimming)
        kcsr_mask = kcsr_mask.strip()
        budget_name = budget_name.strip()
        fund_source = fund_source.strip() if fund_source else None

        # 3. Вызов репозитория
        raw_data = await self.repository.get_budget_constructor_data(
            db=db,
            p_kcsr_mask=kcsr_mask,
            p_budget_name=budget_name,
            p_period_from=period_from,
            p_period_to=period_to,
            p_fund_source=fund_source,
            p_min_amount=min_amount,
        )

        # 4. Сериализация в Pydantic модели
        # Это гарантирует, что на выход пойдут только разрешенные поля
        return raw_data

    def _validate_periods(self, start: str, end: str):
        """Внутренняя валидация: дата начала не может быть позже даты конца"""
        try:
            dt_start = datetime.strptime(start, "%Y-%m")
            dt_end = datetime.strptime(end, "%Y-%m")
            if dt_start > dt_end:
                raise ValueError("Начальный период не может быть больше конечного")
        except ValueError as e:
            raise ValueError(f"Некорректный формат периода: {str(e)}")
