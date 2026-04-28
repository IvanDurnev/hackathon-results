from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any


SOURCE_RCHB = "rchb"
SOURCE_AGREEMENTS = "agreements"
SOURCE_GZ_BUDGET_LINES = "gz_budget_lines"
SOURCE_GZ_CONTRACTS = "gz_contracts"
SOURCE_GZ_PAYMENTS = "gz_payments"
SOURCE_BUAU = "buau"


@dataclass
class ImportIssue:
    severity: str
    code: str
    message: str
    source_file_id: int | None = None
    row_number: int | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class SourceFile:
    id: int
    source_type: str
    path: Path
    original_name: str
    checksum: str
    period_date: date | None = None
    rows_total: int = 0
    rows_imported: int = 0
    warnings_count: int = 0
    errors_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class BudgetFact:
    id: int
    source_file_id: int
    source_type: str
    period_date: date | None
    budget_name: str
    posting_date: date | None
    kfsr_code: str | None = None
    kfsr_norm: str | None = None
    kfsr_name: str | None = None
    kcsr_code: str | None = None
    kcsr_norm: str | None = None
    kcsr_name: str | None = None
    kvr_code: str | None = None
    kvr_norm: str | None = None
    kvr_name: str | None = None
    kvsr_code: str | None = None
    kvsr_norm: str | None = None
    kvsr_name: str | None = None
    kesr_code: str | None = None
    kesr_norm: str | None = None
    purposefulgrant_code: str | None = None
    purposefulgrant_norm: str | None = None
    kdr_code: str | None = None
    kdr_norm: str | None = None
    kde_code: str | None = None
    kde_norm: str | None = None
    kdf_code: str | None = None
    kdf_norm: str | None = None
    limits_amount: Decimal = Decimal("0.00")
    accepted_bo_amount: Decimal = Decimal("0.00")
    accepted_without_bo_amount: Decimal = Decimal("0.00")
    remaining_limits_amount: Decimal = Decimal("0.00")
    cash_amount: Decimal = Decimal("0.00")
    buau_payment_amount: Decimal = Decimal("0.00")
    buau_execution_amount: Decimal = Decimal("0.00")
    buau_recovery_amount: Decimal = Decimal("0.00")
    buau_organization: str | None = None
    buau_grantor: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    def codes(self) -> dict[str, str | None]:
        return {
            "kfsr": self.kfsr_norm,
            "kcsr": self.kcsr_norm,
            "kvr": self.kvr_norm,
            "kvsr": self.kvsr_norm,
            "kesr": self.kesr_norm,
            "purposefulgrant": self.purposefulgrant_norm,
            "kdr": self.kdr_norm,
            "kde": self.kde_norm,
            "kdf": self.kdf_norm,
        }


@dataclass
class AgreementFact:
    id: int
    source_file_id: int
    period_date: date | None
    documentclass_id: str
    budget_id: str | None
    budget_caption: str | None
    document_id: str
    close_date: date | None
    reg_number: str | None
    main_close_date: date | None
    main_reg_number: str | None
    amount_1year: Decimal
    estimate_caption: str | None
    recipient_caption: str | None
    kadmr_code: str | None = None
    kadmr_norm: str | None = None
    kfsr_code: str | None = None
    kfsr_norm: str | None = None
    kcsr_code: str | None = None
    kcsr_norm: str | None = None
    kvr_code: str | None = None
    kvr_norm: str | None = None
    kesr_code: str | None = None
    kesr_norm: str | None = None
    purposefulgrant_code: str | None = None
    purposefulgrant_norm: str | None = None
    kdr_code: str | None = None
    kdr_norm: str | None = None
    kde_code: str | None = None
    kde_norm: str | None = None
    kdf_code: str | None = None
    kdf_norm: str | None = None
    grantinvestment_code: str | None = None
    grantinvestment_norm: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    def codes(self) -> dict[str, str | None]:
        return {
            "kfsr": self.kfsr_norm,
            "kcsr": self.kcsr_norm,
            "kvr": self.kvr_norm,
            "kvsr": self.kadmr_norm,
            "kesr": self.kesr_norm,
            "purposefulgrant": self.purposefulgrant_norm,
            "kdr": self.kdr_norm,
            "kde": self.kde_norm,
            "kdf": self.kdf_norm,
        }


@dataclass
class ContractFact:
    id: int
    source_file_id: int
    con_document_id: str
    con_number: str | None
    con_date: date | None
    con_amount: Decimal
    zakazchik_key: str | None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class ContractBudgetLine:
    id: int
    source_file_id: int
    con_document_id: str
    kfsr_code: str | None = None
    kfsr_norm: str | None = None
    kcsr_code: str | None = None
    kcsr_norm: str | None = None
    kvr_code: str | None = None
    kvr_norm: str | None = None
    kesr_code: str | None = None
    kesr_norm: str | None = None
    kvsr_code: str | None = None
    kvsr_norm: str | None = None
    kdf_code: str | None = None
    kdf_norm: str | None = None
    kde_code: str | None = None
    kde_norm: str | None = None
    kdr_code: str | None = None
    kdr_norm: str | None = None
    kif_code: str | None = None
    kif_norm: str | None = None
    purposefulgrant_code: str | None = None
    purposefulgrant_norm: str | None = None
    allocation_share: Decimal = Decimal("1.0")
    allocation_method: str = "single_line"
    raw: dict[str, Any] = field(default_factory=dict)

    def codes(self) -> dict[str, str | None]:
        return {
            "kfsr": self.kfsr_norm,
            "kcsr": self.kcsr_norm,
            "kvr": self.kvr_norm,
            "kvsr": self.kvsr_norm,
            "kesr": self.kesr_norm,
            "purposefulgrant": self.purposefulgrant_norm,
            "kdr": self.kdr_norm,
            "kde": self.kde_norm,
            "kdf": self.kdf_norm,
            "kif": self.kif_norm,
        }


@dataclass
class PaymentFact:
    id: int
    source_file_id: int
    con_document_id: str
    platezhka_paydate: date | None
    platezhka_key: str | None
    platezhka_num: str | None
    platezhka_amount: Decimal
    linked_to_budget_line: bool = False
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchHit:
    object_key: str
    object_type: str
    display_name: str
    matched_codes: dict[str, str | None]
    rank: int
    source_types: list[str] = field(default_factory=list)


@dataclass
class DrilldownRecord:
    source_type: str
    label: str
    amount: Decimal
    event_date: date | None
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class QueryRow:
    row_id: str
    object_key: str
    object_name: str
    metric_code: str
    metric_name: str
    amount: Decimal
    source_type: str
    codes: dict[str, str | None]
    warning_codes: list[str] = field(default_factory=list)
    drilldown_available: bool = False


@dataclass
class QueryResult:
    rows: list[QueryRow]
    totals: dict[str, Decimal]
    warnings: list[ImportIssue]
    drilldowns: dict[str, list[DrilldownRecord]]


@dataclass
class TimelinePoint:
    period: date
    metric_code: str
    metric_name: str
    amount: Decimal


@dataclass
class CompareRow:
    object_key: str
    object_name: str
    metric_code: str
    metric_name: str
    base_value: Decimal
    compare_value: Decimal
    delta: Decimal
    delta_percent: Decimal | None


@dataclass
class CompareResult:
    rows: list[CompareRow]


@dataclass
class AnalyticsDataset:
    source_files: list[SourceFile] = field(default_factory=list)
    budget_facts: list[BudgetFact] = field(default_factory=list)
    agreements: list[AgreementFact] = field(default_factory=list)
    contracts: list[ContractFact] = field(default_factory=list)
    contract_budget_lines: list[ContractBudgetLine] = field(default_factory=list)
    payments: list[PaymentFact] = field(default_factory=list)
    issues: list[ImportIssue] = field(default_factory=list)

    def source_by_id(self, source_file_id: int) -> SourceFile:
        for source in self.source_files:
            if source.id == source_file_id:
                return source
        raise KeyError(source_file_id)

    def add_issue(self, issue: ImportIssue) -> None:
        self.issues.append(issue)

    @property
    def contracts_by_document_id(self) -> dict[str, ContractFact]:
        return {contract.con_document_id: contract for contract in self.contracts}

    @property
    def contract_lines_by_document_id(self) -> dict[str, list[ContractBudgetLine]]:
        grouped: dict[str, list[ContractBudgetLine]] = {}
        for line in self.contract_budget_lines:
            grouped.setdefault(line.con_document_id, []).append(line)
        return grouped
