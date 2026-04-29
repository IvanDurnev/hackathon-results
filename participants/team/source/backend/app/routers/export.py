from datetime import datetime
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.repositories.analytics_repository import AnalyticsRepository
from app.services.export import BudgetExportService
from app.services.analyse import AnalyticsService

router = APIRouter()


@router.get("/analytics/export-excel")
async def export_budget_report(
    kcsr_mask: str | None = Query("", description="KCSR mask, e.g. *****6105*"),
    budget_name: str | None = Query("", description="Budget name part"),
    period_from: str = Query(..., description="Period start YYYY-MM"),
    period_to: str = Query(..., description="Period end YYYY-MM"),
    fund_source: str | None = Query(None, description="Fund source"),
    min_amount: Decimal = Query(Decimal("0"), description="Minimum PBS limit"),
    db: AsyncSession = Depends(get_session),
):
    """
    Экспорт аналитического отчета в формат Excel.
    Использует те же фильтры, что и основной конструктор.
    """
    if not (kcsr_mask and kcsr_mask.strip()) and not (
        budget_name and budget_name.strip()
    ):
        raise HTTPException(
            status_code=400, # Используйте число или status.HTTP_400_BAD_REQUEST
            detail="Необходимо указать хотя бы один из параметров: kcsr_mask или budget_name",
        )

    # 1. Инициализируем сервис, передавая в него экземпляр репозитория
    analytics_service = AnalyticsService(AnalyticsRepository())


    data = await analytics_service.get_constructor_report(
        db=db,
        kcsr_mask=kcsr_mask or "",
        budget_name=budget_name or "",
        period_from=period_from,
        period_to=period_to,
        fund_source=fund_source,
        min_amount=min_amount,
    )

    excel_file = await BudgetExportService.export_to_excel(data)

    current_time = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"budget_report_{current_time}.xlsx"

    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )