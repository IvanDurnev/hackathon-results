from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, Field


class BudgetAnalyticsDTO(BaseModel):
    kcsr_code: str
    kcsr_name: Optional[str] = None
    budget_name: Optional[str] = None
    kfsr_code: Optional[str] = None
    kfsr_name: Optional[str] = None
    fund_source: Optional[str] = None
    budget_period: str
    limit_pbs: Decimal = Decimal("0")
    budget_obligations: Decimal = Decimal("0")
    limit_remaining: Decimal = Decimal("0")
    rcb_payments: Decimal = Decimal("0")
    rcb_payments_kvr2: Decimal = Decimal("0")
    rcb_payments_kvr5: Decimal = Decimal("0")
    rcb_payments_kvr6: Decimal = Decimal("0")
    buau_payments: Decimal = Decimal("0")
    agr_amount: Decimal = Decimal("0")
    agr_mbt_amount: Decimal = Decimal("0")
    agr_subsidy_amount: Decimal = Decimal("0")
    gz_contracts_amount: Decimal = Decimal("0")
    gz_paid: Decimal = Decimal("0")
    agreement_details: list[dict[str, Any]] = Field(default_factory=list)
    gz_contract_details: list[dict[str, Any]] = Field(default_factory=list)
    gz_payment_details: list[dict[str, Any]] = Field(default_factory=list)
