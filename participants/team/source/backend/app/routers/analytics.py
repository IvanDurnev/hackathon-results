from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.repositories.analytics_repository import AnalyticsRepository
from app.schemas.analytics import BudgetAnalyticsDTO
from app.services.analyse import AnalyticsService
from app.services.import_service import DataImportService, ImportValidationError


router = APIRouter(prefix="/analytics", tags=["budget analytics"])


@router.get("/report", response_model=list[BudgetAnalyticsDTO])
async def get_budget_analytics(
    kcsr_mask: str | None = Query("", description="KCSR mask, e.g. *****6105*"),
    budget_name: str | None = Query("", description="Budget name part"),
    period_from: str = Query(..., description="Period start YYYY-MM"),
    period_to: str = Query(..., description="Period end YYYY-MM"),
    fund_source: str | None = Query(None, description="Fund source"),
    min_amount: Decimal = Query(Decimal("0"), description="Minimum PBS limit"),
    db: AsyncSession = Depends(get_session),
):
    try:
        if not (kcsr_mask and kcsr_mask.strip()) and not (
            budget_name and budget_name.strip()
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Необходимо указать хотя бы один из параметров: kcsr_mask или budget_name",
            )
        service = AnalyticsService(AnalyticsRepository())
        return await service.get_constructor_report(
            db=db,
            kcsr_mask=kcsr_mask,
            budget_name=budget_name,
            period_from=period_from,
            period_to=period_to,
            fund_source=fund_source,
            min_amount=min_amount,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при формировании аналитики: {e}",
        ) from e


@router.post("/batch")
async def batch_upload(
    file_rcb: UploadFile | None = None,
    file_agr: UploadFile | None = None,
    file_gz_budget_line: UploadFile | None = None,
    file_gz_contracts: UploadFile | None = None,
    file_gz_payments: UploadFile | None = None,
    file_buau: UploadFile | None = None,
    db: AsyncSession = Depends(get_session),
):
    import_service = DataImportService(db)
    try:
        return await import_service.import_all_data(
            rcb_file=file_rcb,
            agr_file=file_agr,
            gz_budget_line_file=file_gz_budget_line,
            gz_contract_file=file_gz_contracts,
            gz_payment_file=file_gz_payments,
            buau_file=file_buau,
        )
    except ImportValidationError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка импорта: {e}") from e
