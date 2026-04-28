from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterable

from app.modules.budget_constructor.parsing import (
    extract_period_end,
    extract_rchb_period_date,
    infer_period_date_from_filename,
    is_total_row,
    kcsr_slice,
    normalize_code,
    parse_date,
    parse_money,
    read_csv_smart,
)
from app.modules.budget_constructor.types import (
    SOURCE_AGREEMENTS,
    SOURCE_BUAU,
    SOURCE_GZ_BUDGET_LINES,
    SOURCE_GZ_CONTRACTS,
    SOURCE_GZ_PAYMENTS,
    SOURCE_RCHB,
    AgreementFact,
    AnalyticsDataset,
    BudgetFact,
    CompareResult,
    CompareRow,
    ContractBudgetLine,
    ContractFact,
    DrilldownRecord,
    ImportIssue,
    PaymentFact,
    QueryResult,
    QueryRow,
    SearchHit,
    SourceFile,
    TimelinePoint,
)


METRICS: dict[str, dict[str, str]] = {
    "LIMITS": {"name": "Доведенные лимиты", "source": SOURCE_RCHB},
    "BO": {"name": "Принятые бюджетные обязательства", "source": SOURCE_RCHB},
    "BO_FREE": {"name": "Подтверждено лимитов без БО", "source": SOURCE_RCHB},
    "REST_LIMITS": {"name": "Остаток лимитов", "source": SOURCE_RCHB},
    "CASH_RCHB": {"name": "Кассовые выплаты", "source": SOURCE_RCHB},
    "AGREEMENT_MBT": {"name": "Соглашения МБТ", "source": SOURCE_AGREEMENTS},
    "AGREEMENT_SUBSIDY": {"name": "Соглашения по субсидиям", "source": SOURCE_AGREEMENTS},
    "CONTRACT_AMOUNT": {"name": "Договоры и контракты", "source": SOURCE_GZ_CONTRACTS},
    "CONTRACT_PAYMENT": {"name": "Оплаты по контрактам", "source": SOURCE_GZ_PAYMENTS},
    "BUAU_PAYMENT": {"name": "Выплаты БУАУ", "source": SOURCE_BUAU},
}

TEMPLATE_LABELS = {
    "kik": "Раздел 1. КИК",
    "skk": "Раздел 2. СКК",
    "two_three": "Раздел 3. 2/3",
    "okv": "Раздел 4. ОКВ",
}

OKV_KVR_CODES = {"400", "406", "407", "408", "460", "461", "462", "463", "464", "465", "466"}

RCHB_REQUIRED_COLUMNS = {
    "Бюджет",
    "Дата проводки",
    "КФСР",
    "КЦСР",
    "КВР",
    "Всего выбытий (бух.уч.)",
}

RCHB_REQUIRED_AMOUNT_PREFIXES = {
    "Лимиты ПБС": "Лимиты ПБС * год",
    "Подтв. лимитов по БО": "Подтв. лимитов по БО * год",
}


@dataclass
class _Aggregate:
    object_key: str
    object_name: str
    metric_code: str
    metric_name: str
    source_type: str
    codes: dict[str, str | None]
    amount: Decimal = Decimal("0.00")
    warning_codes: set[str] = field(default_factory=set)
    drilldowns: list[DrilldownRecord] = field(default_factory=list)


def load_task_dataset(task_dir: Path | str) -> AnalyticsDataset:
    task_path = Path(task_dir)
    dataset = AnalyticsDataset()
    if not task_path.exists():
        raise FileNotFoundError(task_path)

    _load_rchb(dataset, task_path / "1. РЧБ")
    _load_agreements(dataset, task_path / "2. Соглашения")
    _load_gz(dataset, task_path / "3. ГЗ")
    _load_buau(dataset, task_path / "4. Выгрузка БУАУ")
    _finalize_quality(dataset)
    _refresh_source_issue_counts(dataset)
    return dataset


def search_dataset(dataset: AnalyticsDataset, query: str, limit: int = 20) -> list[SearchHit]:
    query_text = query.strip().lower()
    query_code = normalize_code(query)
    if len(query_text) < 2 and not query_code:
        return []

    candidates: dict[str, SearchHit] = {}

    def add_candidate(
        object_key: str,
        display_name: str,
        object_type: str,
        codes: dict[str, str | None],
        source_type: str,
        search_parts: Iterable[str | None],
    ) -> None:
        search_text = " ".join(part for part in search_parts if part).lower()
        code_hit = bool(query_code and any(value and query_code in value for value in codes.values()))
        text_hit = any(variant in search_text for variant in _query_text_variants(query_text))
        if not code_hit and not text_hit:
            return
        rank = (100 if code_hit else 0) + (50 if display_name.lower().find(query_text) >= 0 else 0) + len(query_text)
        existing = candidates.get(object_key)
        if existing:
            existing.rank = max(existing.rank, rank)
            if source_type not in existing.source_types:
                existing.source_types.append(source_type)
            return
        candidates[object_key] = SearchHit(
            object_key=object_key,
            object_type=object_type,
            display_name=display_name,
            matched_codes=codes,
            rank=rank,
            source_types=[source_type],
        )

    for fact in dataset.budget_facts:
        codes = fact.codes()
        object_key, display_name = _object_identity(dataset, codes, fact.kcsr_name or fact.buau_organization or fact.budget_name)
        add_candidate(
            object_key,
            display_name,
            "budget_code",
            codes,
            fact.source_type,
            (
                display_name,
                fact.budget_name,
                fact.kfsr_name,
                fact.kcsr_name,
                fact.kvr_name,
                fact.kvsr_name,
                fact.buau_organization,
                fact.buau_grantor,
                *codes.values(),
            ),
        )

    for agreement in dataset.agreements:
        codes = agreement.codes()
        object_key, display_name = _object_identity(dataset, codes, agreement.recipient_caption or agreement.reg_number)
        add_candidate(
            object_key,
            display_name,
            "agreement",
            codes,
            SOURCE_AGREEMENTS,
            (
                display_name,
                agreement.budget_caption,
                agreement.recipient_caption,
                agreement.reg_number,
                agreement.document_id,
                *codes.values(),
            ),
        )

    contracts = dataset.contracts_by_document_id
    for line in dataset.contract_budget_lines:
        contract = contracts.get(line.con_document_id)
        codes = line.codes()
        object_key, display_name = _object_identity(dataset, codes, contract.con_number if contract else line.con_document_id)
        add_candidate(
            object_key,
            display_name,
            "contract",
            codes,
            SOURCE_GZ_CONTRACTS,
            (
                display_name,
                line.con_document_id,
                contract.con_number if contract else None,
                contract.zakazchik_key if contract else None,
                *codes.values(),
            ),
        )

    return sorted(candidates.values(), key=lambda item: (-item.rank, item.display_name))[:limit]


def query_dataset(
    dataset: AnalyticsDataset,
    *,
    metrics: list[str],
    date_from: date | None = None,
    date_to: date | None = None,
    query: str | None = None,
    object_keys: list[str] | None = None,
    template_code: str | None = None,
) -> QueryResult:
    requested_metrics = [metric for metric in metrics if metric in METRICS]
    if not requested_metrics:
        return QueryResult(rows=[], totals={}, warnings=[], drilldowns={})

    effective_date_to = date_to or _max_available_date(dataset)
    effective_date_from = date_from or date(1, 1, 1)
    object_key_set = set(object_keys or [])
    aggregate: dict[tuple[str, str], _Aggregate] = {}
    warnings: list[ImportIssue] = []

    if any(metric in requested_metrics for metric in ("LIMITS", "BO", "BO_FREE", "REST_LIMITS", "CASH_RCHB")):
        source = _latest_source(dataset, SOURCE_RCHB, effective_date_to)
        if source:
            for fact in dataset.budget_facts:
                if fact.source_file_id != source.id or fact.source_type != SOURCE_RCHB:
                    continue
                if not _fact_matches(fact.codes(), template_code, query, object_key_set, dataset, fact.kcsr_name or fact.budget_name):
                    continue
                for metric in requested_metrics:
                    amount = _budget_metric_value(fact, metric)
                    if amount is None:
                        continue
                    _add_amount(
                        dataset,
                        aggregate,
                        metric,
                        SOURCE_RCHB,
                        fact.codes(),
                        fact.kcsr_name or fact.budget_name,
                        amount,
                        DrilldownRecord(
                            source_type=SOURCE_RCHB,
                            label=fact.kcsr_name or fact.budget_name,
                            amount=amount,
                            event_date=fact.posting_date,
                            details={
                                "budget_name": fact.budget_name,
                                "source_file": source.original_name,
                                "posting_date": fact.posting_date.isoformat() if fact.posting_date else None,
                            },
                        ),
                    )

    if "BUAU_PAYMENT" in requested_metrics:
        source = _latest_source(dataset, SOURCE_BUAU, effective_date_to)
        if source:
            for fact in dataset.budget_facts:
                if fact.source_file_id != source.id or fact.source_type != SOURCE_BUAU:
                    continue
                if not _fact_matches(fact.codes(), template_code, query, object_key_set, dataset, fact.buau_organization):
                    continue
                _add_amount(
                    dataset,
                    aggregate,
                    "BUAU_PAYMENT",
                    SOURCE_BUAU,
                    fact.codes(),
                    fact.buau_organization or fact.kcsr_name or fact.budget_name,
                    fact.buau_payment_amount,
                    DrilldownRecord(
                        source_type=SOURCE_BUAU,
                        label=fact.buau_organization or fact.budget_name,
                        amount=fact.buau_payment_amount,
                        event_date=fact.posting_date,
                        details={"grantor": fact.buau_grantor, "source_file": source.original_name},
                    ),
                )

    if any(metric in requested_metrics for metric in ("AGREEMENT_MBT", "AGREEMENT_SUBSIDY")):
        source = _latest_source(dataset, SOURCE_AGREEMENTS, effective_date_to)
        if source:
            for agreement in dataset.agreements:
                if agreement.source_file_id != source.id:
                    continue
                if not _date_in_range(agreement.close_date, effective_date_from, effective_date_to):
                    continue
                metric = _agreement_metric(agreement)
                if metric not in requested_metrics:
                    continue
                if not _fact_matches(agreement.codes(), template_code, query, object_key_set, dataset, agreement.recipient_caption):
                    continue
                _add_amount(
                    dataset,
                    aggregate,
                    metric,
                    SOURCE_AGREEMENTS,
                    agreement.codes(),
                    agreement.recipient_caption or agreement.reg_number or agreement.document_id,
                    agreement.amount_1year,
                    DrilldownRecord(
                        source_type=SOURCE_AGREEMENTS,
                        label=agreement.reg_number or agreement.document_id,
                        amount=agreement.amount_1year,
                        event_date=agreement.close_date,
                        details={
                            "document_id": agreement.document_id,
                            "reg_number": agreement.reg_number,
                            "recipient": agreement.recipient_caption or agreement.budget_caption,
                            "documentclass_id": agreement.documentclass_id,
                            "source_file": source.original_name,
                        },
                    ),
                )

    if "CONTRACT_AMOUNT" in requested_metrics:
        contracts = dataset.contracts_by_document_id
        for line in dataset.contract_budget_lines:
            contract = contracts.get(line.con_document_id)
            if not contract or not _date_in_range(contract.con_date, effective_date_from, effective_date_to):
                continue
            if not _fact_matches(line.codes(), template_code, query, object_key_set, dataset, contract.con_number):
                continue
            amount = (contract.con_amount * line.allocation_share).quantize(Decimal("0.01"))
            warning_code = None if line.allocation_method == "single_line" else line.allocation_method
            _add_amount(
                dataset,
                aggregate,
                "CONTRACT_AMOUNT",
                SOURCE_GZ_CONTRACTS,
                line.codes(),
                contract.con_number or contract.con_document_id,
                amount,
                DrilldownRecord(
                    source_type=SOURCE_GZ_CONTRACTS,
                    label=contract.con_number or contract.con_document_id,
                    amount=amount,
                    event_date=contract.con_date,
                    details={
                        "con_document_id": contract.con_document_id,
                        "zakazchik_key": contract.zakazchik_key,
                        "allocation_method": line.allocation_method,
                    },
                ),
                warning_code=warning_code,
            )

    if "CONTRACT_PAYMENT" in requested_metrics:
        lines_by_contract = dataset.contract_lines_by_document_id
        for payment in dataset.payments:
            if not payment.linked_to_budget_line or not _date_in_range(payment.platezhka_paydate, effective_date_from, effective_date_to):
                continue
            for line in lines_by_contract.get(payment.con_document_id, []):
                if not _fact_matches(line.codes(), template_code, query, object_key_set, dataset, payment.platezhka_num):
                    continue
                amount = (payment.platezhka_amount * line.allocation_share).quantize(Decimal("0.01"))
                warning_code = None if line.allocation_method == "single_line" else line.allocation_method
                _add_amount(
                    dataset,
                    aggregate,
                    "CONTRACT_PAYMENT",
                    SOURCE_GZ_PAYMENTS,
                    line.codes(),
                    payment.platezhka_num or payment.platezhka_key or payment.con_document_id,
                    amount,
                    DrilldownRecord(
                        source_type=SOURCE_GZ_PAYMENTS,
                        label=payment.platezhka_num or payment.platezhka_key or payment.con_document_id,
                        amount=amount,
                        event_date=payment.platezhka_paydate,
                        details={
                            "con_document_id": payment.con_document_id,
                            "platezhka_key": payment.platezhka_key,
                            "allocation_method": line.allocation_method,
                        },
                    ),
                    warning_code=warning_code,
                )

    rows, drilldowns = _build_query_rows(aggregate)
    totals = _build_totals(rows)
    if template_code and template_code not in TEMPLATE_LABELS:
        warnings.append(ImportIssue("warning", "unknown_template", f"Неизвестный шаблон: {template_code}"))
    warnings.extend(_query_quality_warnings(dataset, rows, drilldowns, query))
    return QueryResult(rows=rows, totals=totals, warnings=warnings, drilldowns=drilldowns)


def timeline_dataset(
    dataset: AnalyticsDataset,
    *,
    metrics: list[str],
    date_from: date | None = None,
    date_to: date | None = None,
    query: str | None = None,
    object_keys: list[str] | None = None,
    template_code: str | None = None,
) -> list[TimelinePoint]:
    requested_metrics = [metric for metric in metrics if metric in METRICS]
    start = date_from or date(1, 1, 1)
    end = date_to or _max_available_date(dataset)
    object_key_set = set(object_keys or [])
    totals: dict[tuple[date, str], Decimal] = defaultdict(lambda: Decimal("0.00"))

    for source in sorted(dataset.source_files, key=lambda item: item.period_date or date.min):
        if source.source_type != SOURCE_RCHB or source.period_date is None or not (start <= source.period_date <= end):
            continue
        for fact in dataset.budget_facts:
            if fact.source_file_id != source.id or fact.source_type != SOURCE_RCHB:
                continue
            if not _fact_matches(fact.codes(), template_code, query, object_key_set, dataset, fact.kcsr_name or fact.budget_name):
                continue
            for metric in requested_metrics:
                amount = _budget_metric_value(fact, metric)
                if amount is not None:
                    totals[(source.period_date, metric)] += amount

    if "BUAU_PAYMENT" in requested_metrics:
        for source in dataset.source_files:
            if source.source_type != SOURCE_BUAU or source.period_date is None or not (start <= source.period_date <= end):
                continue
            for fact in dataset.budget_facts:
                if fact.source_file_id != source.id or fact.source_type != SOURCE_BUAU:
                    continue
                if _fact_matches(fact.codes(), template_code, query, object_key_set, dataset, fact.buau_organization):
                    totals[(source.period_date, "BUAU_PAYMENT")] += fact.buau_payment_amount

    for agreement in dataset.agreements:
        metric = _agreement_metric(agreement)
        if metric not in requested_metrics or agreement.close_date is None:
            continue
        period = date(agreement.close_date.year, agreement.close_date.month, 1)
        if not (start <= agreement.close_date <= end):
            continue
        if _fact_matches(agreement.codes(), template_code, query, object_key_set, dataset, agreement.recipient_caption):
            totals[(period, metric)] += agreement.amount_1year

    contracts = dataset.contracts_by_document_id
    if "CONTRACT_AMOUNT" in requested_metrics:
        for line in dataset.contract_budget_lines:
            contract = contracts.get(line.con_document_id)
            if not contract or contract.con_date is None or not (start <= contract.con_date <= end):
                continue
            period = date(contract.con_date.year, contract.con_date.month, 1)
            if _fact_matches(line.codes(), template_code, query, object_key_set, dataset, contract.con_number):
                totals[(period, "CONTRACT_AMOUNT")] += (contract.con_amount * line.allocation_share).quantize(Decimal("0.01"))

    if "CONTRACT_PAYMENT" in requested_metrics:
        lines_by_contract = dataset.contract_lines_by_document_id
        for payment in dataset.payments:
            if not payment.linked_to_budget_line or payment.platezhka_paydate is None:
                continue
            if not (start <= payment.platezhka_paydate <= end):
                continue
            period = date(payment.platezhka_paydate.year, payment.platezhka_paydate.month, 1)
            for line in lines_by_contract.get(payment.con_document_id, []):
                if _fact_matches(line.codes(), template_code, query, object_key_set, dataset, payment.platezhka_num):
                    totals[(period, "CONTRACT_PAYMENT")] += (payment.platezhka_amount * line.allocation_share).quantize(Decimal("0.01"))

    return [
        TimelinePoint(period=period, metric_code=metric, metric_name=METRICS[metric]["name"], amount=amount)
        for (period, metric), amount in sorted(totals.items())
        if amount != 0
    ]


def compare_dataset(
    dataset: AnalyticsDataset,
    *,
    metrics: list[str],
    base_date: date,
    compare_date: date,
    query: str | None = None,
    object_keys: list[str] | None = None,
    template_code: str | None = None,
) -> CompareResult:
    base = query_dataset(
        dataset,
        metrics=metrics,
        date_to=base_date,
        query=query,
        object_keys=object_keys,
        template_code=template_code,
    )
    compare = query_dataset(
        dataset,
        metrics=metrics,
        date_to=compare_date,
        query=query,
        object_keys=object_keys,
        template_code=template_code,
    )
    base_map = {(row.object_key, row.metric_code): row for row in base.rows}
    compare_map = {(row.object_key, row.metric_code): row for row in compare.rows}
    keys = sorted(set(base_map) | set(compare_map))
    rows: list[CompareRow] = []
    for key in keys:
        base_row = base_map.get(key)
        compare_row = compare_map.get(key)
        base_value = base_row.amount if base_row else Decimal("0.00")
        compare_value = compare_row.amount if compare_row else Decimal("0.00")
        delta = compare_value - base_value
        delta_percent = None
        if base_value != 0:
            delta_percent = (delta / base_value * Decimal("100")).quantize(Decimal("0.01"))
        source = compare_row or base_row
        if source is None:
            continue
        rows.append(
            CompareRow(
                object_key=source.object_key,
                object_name=source.object_name,
                metric_code=source.metric_code,
                metric_name=source.metric_name,
                base_value=base_value,
                compare_value=compare_value,
                delta=delta,
                delta_percent=delta_percent,
            )
        )
    return CompareResult(rows=rows)


def _load_rchb(dataset: AnalyticsDataset, directory: Path) -> None:
    for path in sorted(directory.glob("*.csv")):
        profile, rows = read_csv_smart(path)
        source = _add_source(dataset, SOURCE_RCHB, path, extract_rchb_period_date(path), len(rows), profile)
        missing = _missing_rchb_columns(profile.columns)
        if missing:
            dataset.add_issue(
                ImportIssue("error", "missing_columns", f"Нет обязательных колонок: {', '.join(sorted(missing))}", source.id)
            )
            continue
        for offset, row in enumerate(rows, start=profile.header_row + 1):
            if is_total_row(row):
                continue
            try:
                dataset.budget_facts.append(
                    BudgetFact(
                        id=len(dataset.budget_facts) + 1,
                        source_file_id=source.id,
                        source_type=SOURCE_RCHB,
                        period_date=source.period_date,
                        budget_name=_s(row.get("Бюджет")),
                        posting_date=parse_date(row.get("Дата проводки")),
                        kfsr_code=_s(row.get("КФСР")),
                        kfsr_norm=normalize_code(row.get("КФСР")),
                        kfsr_name=_s(row.get("Наименование КФСР")),
                        kcsr_code=_s(row.get("КЦСР")),
                        kcsr_norm=normalize_code(row.get("КЦСР")),
                        kcsr_name=_s(row.get("Наименование КЦСР")),
                        kvr_code=_s(row.get("КВР")),
                        kvr_norm=normalize_code(row.get("КВР")),
                        kvr_name=_s(row.get("Наименование КВР")),
                        kvsr_code=_s(row.get("КВСР")),
                        kvsr_norm=normalize_code(row.get("КВСР")),
                        kvsr_name=_s(row.get("Наименование КВСР")),
                        kesr_code=_s(row.get("КОСГУ")),
                        kesr_norm=normalize_code(row.get("КОСГУ")),
                        purposefulgrant_code=_s(row.get("Код цели")),
                        purposefulgrant_norm=normalize_code(row.get("Код цели")),
                        limits_amount=parse_money(_rchb_value(row, "Лимиты ПБС")),
                        accepted_bo_amount=parse_money(_rchb_value(row, "Подтв. лимитов по БО")),
                        accepted_without_bo_amount=parse_money(_rchb_value(row, "Подтв. лимитов без БО")),
                        remaining_limits_amount=parse_money(_rchb_value(row, "Остаток лимитов")),
                        cash_amount=parse_money(row.get("Всего выбытий (бух.уч.)")),
                        raw=row,
                    )
                )
            except ValueError as exc:
                dataset.add_issue(ImportIssue("error", "row_parse_error", str(exc), source.id, offset, row))


def _load_agreements(dataset: AnalyticsDataset, directory: Path) -> None:
    for path in sorted(directory.glob("*.csv")):
        profile, rows = read_csv_smart(path)
        period = infer_period_date_from_filename(path)
        if not period and rows:
            period = extract_period_end(rows[0].get("period_of_date"))
        source = _add_source(dataset, SOURCE_AGREEMENTS, path, period, len(rows), profile)
        for offset, row in enumerate(rows, start=profile.header_row + 1):
            if is_total_row(row):
                continue
            try:
                dataset.agreements.append(
                    AgreementFact(
                        id=len(dataset.agreements) + 1,
                        source_file_id=source.id,
                        period_date=source.period_date,
                        documentclass_id=_s(row.get("documentclass_id")),
                        budget_id=_s(row.get("budget_id")),
                        budget_caption=_s(row.get("caption")),
                        document_id=_s(row.get("document_id")),
                        close_date=parse_date(row.get("close_date")),
                        reg_number=_s(row.get("reg_number")),
                        main_close_date=parse_date(row.get("main_close_date")),
                        main_reg_number=_s(row.get("main_reg_number")),
                        amount_1year=parse_money(row.get("amount_1year")),
                        estimate_caption=_s(row.get("dd_estimate_caption")),
                        recipient_caption=_s(row.get("dd_recipient_caption")),
                        kadmr_code=_s(row.get("kadmr_code")),
                        kadmr_norm=normalize_code(row.get("kadmr_code")),
                        kfsr_code=_s(row.get("kfsr_code")),
                        kfsr_norm=normalize_code(row.get("kfsr_code")),
                        kcsr_code=_s(row.get("kcsr_code")),
                        kcsr_norm=normalize_code(row.get("kcsr_code")),
                        kvr_code=_s(row.get("kvr_code")),
                        kvr_norm=normalize_code(row.get("kvr_code")),
                        kesr_code=_s(row.get("kesr_code")),
                        kesr_norm=normalize_code(row.get("kesr_code")),
                        purposefulgrant_code=_s(row.get("dd_purposefulgrant_code")),
                        purposefulgrant_norm=normalize_code(row.get("dd_purposefulgrant_code")),
                        kdr_code=_s(row.get("kdr_code")),
                        kdr_norm=normalize_code(row.get("kdr_code")),
                        kde_code=_s(row.get("kde_code")),
                        kde_norm=normalize_code(row.get("kde_code")),
                        kdf_code=_s(row.get("kdf_code")),
                        kdf_norm=normalize_code(row.get("kdf_code")),
                        grantinvestment_code=_s(row.get("dd_grantinvestment_code")),
                        grantinvestment_norm=normalize_code(row.get("dd_grantinvestment_code")),
                        raw=row,
                    )
                )
            except ValueError as exc:
                dataset.add_issue(ImportIssue("error", "row_parse_error", str(exc), source.id, offset, row))


def _load_gz(dataset: AnalyticsDataset, directory: Path) -> None:
    contracts_path = directory / "Контракты и договора.csv"
    budget_lines_path = directory / "Бюджетные строки.csv"
    payments_path = directory / "Платежки.csv"

    if contracts_path.exists():
        profile, rows = read_csv_smart(contracts_path)
        source = _add_source(dataset, SOURCE_GZ_CONTRACTS, contracts_path, None, len(rows), profile)
        for offset, row in enumerate(rows, start=profile.header_row + 1):
            try:
                dataset.contracts.append(
                    ContractFact(
                        id=len(dataset.contracts) + 1,
                        source_file_id=source.id,
                        con_document_id=_s(row.get("con_document_id")),
                        con_number=_s(row.get("con_number")),
                        con_date=parse_date(row.get("con_date")),
                        con_amount=parse_money(row.get("con_amount")),
                        zakazchik_key=_s(row.get("zakazchik_key")),
                        raw=row,
                    )
                )
            except ValueError as exc:
                dataset.add_issue(ImportIssue("error", "row_parse_error", str(exc), source.id, offset, row))

    if budget_lines_path.exists():
        profile, rows = read_csv_smart(budget_lines_path)
        source = _add_source(dataset, SOURCE_GZ_BUDGET_LINES, budget_lines_path, None, len(rows), profile)
        for row in rows:
            dataset.contract_budget_lines.append(
                ContractBudgetLine(
                    id=len(dataset.contract_budget_lines) + 1,
                    source_file_id=source.id,
                    con_document_id=_s(row.get("con_document_id")),
                    kfsr_code=_s(row.get("kfsr_code")),
                    kfsr_norm=normalize_code(row.get("kfsr_code")),
                    kcsr_code=_s(row.get("kcsr_code")),
                    kcsr_norm=normalize_code(row.get("kcsr_code")),
                    kvr_code=_s(row.get("kvr_code")),
                    kvr_norm=normalize_code(row.get("kvr_code")),
                    kesr_code=_s(row.get("kesr_code")),
                    kesr_norm=normalize_code(row.get("kesr_code")),
                    kvsr_code=_s(row.get("kvsr_code")),
                    kvsr_norm=normalize_code(row.get("kvsr_code")),
                    kdf_code=_s(row.get("kdf_code")),
                    kdf_norm=normalize_code(row.get("kdf_code")),
                    kde_code=_s(row.get("kde_code")),
                    kde_norm=normalize_code(row.get("kde_code")),
                    kdr_code=_s(row.get("kdr_code")),
                    kdr_norm=normalize_code(row.get("kdr_code")),
                    kif_code=_s(row.get("kif_code")),
                    kif_norm=normalize_code(row.get("kif_code")),
                    purposefulgrant_code=_s(row.get("purposefulgrant")),
                    purposefulgrant_norm=normalize_code(row.get("purposefulgrant")),
                    raw=row,
                )
            )

    if payments_path.exists():
        profile, rows = read_csv_smart(payments_path)
        source = _add_source(dataset, SOURCE_GZ_PAYMENTS, payments_path, None, len(rows), profile)
        for offset, row in enumerate(rows, start=profile.header_row + 1):
            try:
                dataset.payments.append(
                    PaymentFact(
                        id=len(dataset.payments) + 1,
                        source_file_id=source.id,
                        con_document_id=_s(row.get("con_document_id")),
                        platezhka_paydate=parse_date(row.get("platezhka_paydate")),
                        platezhka_key=_s(row.get("platezhka_key")),
                        platezhka_num=_s(row.get("platezhka_num")),
                        platezhka_amount=parse_money(row.get("platezhka_amount")),
                        raw=row,
                    )
                )
            except ValueError as exc:
                dataset.add_issue(ImportIssue("error", "row_parse_error", str(exc), source.id, offset, row))


def _load_buau(dataset: AnalyticsDataset, directory: Path) -> None:
    for path in sorted(directory.glob("*.csv")):
        profile, rows = read_csv_smart(path)
        source = _add_source(dataset, SOURCE_BUAU, path, infer_period_date_from_filename(path), len(rows), profile)
        for offset, row in enumerate(rows, start=profile.header_row + 1):
            if is_total_row(row):
                continue
            try:
                dataset.budget_facts.append(
                    BudgetFact(
                        id=len(dataset.budget_facts) + 1,
                        source_file_id=source.id,
                        source_type=SOURCE_BUAU,
                        period_date=source.period_date,
                        budget_name=_s(row.get("Бюджет")),
                        posting_date=parse_date(row.get("Дата проводки")),
                        kfsr_code=_s(row.get("КФСР")),
                        kfsr_norm=normalize_code(row.get("КФСР")),
                        kcsr_code=_s(row.get("КЦСР")),
                        kcsr_norm=normalize_code(row.get("КЦСР")),
                        kvr_code=_s(row.get("КВР")),
                        kvr_norm=normalize_code(row.get("КВР")),
                        kesr_code=_s(row.get("КОСГУ")),
                        kesr_norm=normalize_code(row.get("КОСГУ")),
                        purposefulgrant_code=_s(row.get("Код субсидии")),
                        purposefulgrant_norm=normalize_code(row.get("Код субсидии")),
                        buau_payment_amount=parse_money(row.get("Выплаты с учетом возврата")),
                        buau_execution_amount=parse_money(row.get("Выплаты - Исполнение")),
                        buau_recovery_amount=parse_money(row.get("Выплаты - Восстановление выплат - год")),
                        buau_organization=_s(row.get("Организация")),
                        buau_grantor=_s(row.get("Орган, предоставляющий субсидии")),
                        raw=row,
                    )
                )
            except ValueError as exc:
                dataset.add_issue(ImportIssue("error", "row_parse_error", str(exc), source.id, offset, row))


def _finalize_quality(dataset: AnalyticsDataset) -> None:
    lines_by_contract = dataset.contract_lines_by_document_id
    for contract_id, lines in lines_by_contract.items():
        if len(lines) == 1:
            lines[0].allocation_share = Decimal("1.0")
            lines[0].allocation_method = "single_line"
            continue
        share = (Decimal("1.0") / Decimal(len(lines))).quantize(Decimal("0.0000000001"))
        for line in lines:
            line.allocation_share = share
            line.allocation_method = "equal_by_line_no_amount"
        dataset.add_issue(
            ImportIssue(
                "warning",
                "contract_amount_allocated_equally",
                f"Договор {contract_id} имеет {len(lines)} бюджетных строк без сумм строк, сумма распределена поровну.",
            )
        )

    contracts = dataset.contracts_by_document_id
    for contract in dataset.contracts:
        if contract.con_document_id not in lines_by_contract:
            dataset.add_issue(
                ImportIssue(
                    "warning",
                    "contract_budget_line_missing",
                    f"У договора {contract.con_document_id} нет бюджетной строки.",
                    contract.source_file_id,
                    raw=contract.raw,
                )
            )

    for payment in dataset.payments:
        has_contract = payment.con_document_id in contracts
        has_budget_line = payment.con_document_id in lines_by_contract
        payment.linked_to_budget_line = has_contract and has_budget_line
        if not has_contract:
            dataset.add_issue(
                ImportIssue(
                    "warning",
                    "payment_contract_missing",
                    f"Платежка {payment.platezhka_key} ссылается на отсутствующий договор {payment.con_document_id}.",
                    payment.source_file_id,
                    raw=payment.raw,
                )
            )
        elif not has_budget_line:
            dataset.add_issue(
                ImportIssue(
                    "warning",
                    "payment_budget_line_missing",
                    f"Платежка {payment.platezhka_key} не связана с бюджетной строкой договора {payment.con_document_id}.",
                    payment.source_file_id,
                    raw=payment.raw,
                )
            )


def _refresh_source_issue_counts(dataset: AnalyticsDataset) -> None:
    rows_by_source = defaultdict(int)
    for fact in dataset.budget_facts:
        rows_by_source[fact.source_file_id] += 1
    for fact in dataset.agreements:
        rows_by_source[fact.source_file_id] += 1
    for fact in dataset.contracts:
        rows_by_source[fact.source_file_id] += 1
    for fact in dataset.contract_budget_lines:
        rows_by_source[fact.source_file_id] += 1
    for fact in dataset.payments:
        rows_by_source[fact.source_file_id] += 1

    for source in dataset.source_files:
        source.rows_imported = rows_by_source[source.id]
        source.warnings_count = sum(1 for issue in dataset.issues if issue.source_file_id == source.id and issue.severity == "warning")
        source.errors_count = sum(1 for issue in dataset.issues if issue.source_file_id == source.id and issue.severity == "error")


def _missing_rchb_columns(columns: list[str]) -> set[str]:
    available = set(columns)
    missing = set(RCHB_REQUIRED_COLUMNS - available)
    for prefix, label in RCHB_REQUIRED_AMOUNT_PREFIXES.items():
        if not _column_by_prefix(columns, prefix):
            missing.add(label)
    return missing


def _rchb_value(row: dict[str, str], prefix: str) -> str | None:
    column = _column_by_prefix(list(row.keys()), prefix)
    return row.get(column) if column else None


def _column_by_prefix(columns: list[str], prefix: str) -> str | None:
    normalized_prefix = prefix.strip().lower()
    for column in columns:
        normalized_column = column.strip().lower()
        if normalized_column == normalized_prefix or normalized_column.startswith(f"{normalized_prefix} "):
            return column
    return None


def _add_source(
    dataset: AnalyticsDataset,
    source_type: str,
    path: Path,
    period_date: date | None,
    rows_total: int,
    profile: Any,
) -> SourceFile:
    source = SourceFile(
        id=len(dataset.source_files) + 1,
        source_type=source_type,
        path=path,
        original_name=path.name,
        checksum=profile.sha256,
        period_date=period_date,
        rows_total=rows_total,
        metadata={"encoding": profile.encoding, "delimiter": profile.delimiter, "header_row": profile.header_row},
    )
    dataset.source_files.append(source)
    return source


def _budget_metric_value(fact: BudgetFact, metric_code: str) -> Decimal | None:
    return {
        "LIMITS": fact.limits_amount,
        "BO": fact.accepted_bo_amount,
        "BO_FREE": fact.accepted_without_bo_amount,
        "REST_LIMITS": fact.remaining_limits_amount,
        "CASH_RCHB": fact.cash_amount,
    }.get(metric_code)


def _agreement_metric(agreement: AgreementFact) -> str | None:
    if agreement.documentclass_id == "273":
        return "AGREEMENT_MBT"
    if agreement.documentclass_id in {"278", "272", "313"}:
        return "AGREEMENT_SUBSIDY"
    return None


def _fact_matches(
    codes: dict[str, str | None],
    template_code: str | None,
    query: str | None,
    object_keys: set[str],
    dataset: AnalyticsDataset,
    fallback_name: str | None,
) -> bool:
    if template_code and not _matches_template(codes, template_code):
        return False
    object_key, display_name = _object_identity(dataset, codes, fallback_name)
    if object_keys and object_key not in object_keys:
        return False
    if not query:
        return True
    query_text = query.strip().lower()
    query_code = normalize_code(query)
    search_text = " ".join(
        str(part)
        for part in [display_name, fallback_name, *[value for value in codes.values() if value]]
        if part
    ).lower()
    return query_text in search_text or bool(query_code and any(value and query_code in value for value in codes.values()))


def _matches_template(codes: dict[str, str | None], template_code: str | None) -> bool:
    if not template_code:
        return True
    kcsr = codes.get("kcsr")
    if template_code == "kik":
        return kcsr_slice(kcsr, 6, 3) == "978"
    if template_code == "skk":
        return kcsr_slice(kcsr, 6, 4) == "6105"
    if template_code == "two_three":
        return kcsr_slice(kcsr, 6, 3) == "970"
    if template_code == "okv":
        kdr = codes.get("kdr")
        kvr = codes.get("kvr")
        return bool(kdr and kdr != "000") or bool(kvr in OKV_KVR_CODES)
    return False


def _object_identity(dataset: AnalyticsDataset, codes: dict[str, str | None], fallback_name: str | None) -> tuple[str, str]:
    kcsr = codes.get("kcsr")
    if kcsr:
        return f"kcsr:{kcsr}", _kcsr_display_name(dataset, kcsr) or fallback_name or kcsr
    kdr = codes.get("kdr")
    if kdr and kdr != "000":
        return f"kdr:{kdr}", fallback_name or f"ДопКР {kdr}"
    joined_codes = "|".join(value or "" for value in (codes.get("kfsr"), codes.get("kvr"), codes.get("kvsr"), codes.get("kdr")))
    return f"codes:{joined_codes}", fallback_name or joined_codes or "Без кода"


def _kcsr_display_name(dataset: AnalyticsDataset, kcsr_norm: str) -> str | None:
    for fact in dataset.budget_facts:
        if fact.kcsr_norm == kcsr_norm and fact.kcsr_name:
            return fact.kcsr_name
    return None


def _add_amount(
    dataset: AnalyticsDataset,
    aggregate: dict[tuple[str, str], _Aggregate],
    metric_code: str,
    source_type: str,
    codes: dict[str, str | None],
    fallback_name: str | None,
    amount: Decimal,
    drilldown: DrilldownRecord,
    warning_code: str | None = None,
) -> None:
    if amount == 0:
        return
    object_key, object_name = _object_identity(dataset, codes, fallback_name)
    key = (object_key, metric_code)
    item = aggregate.get(key)
    if item is None:
        item = _Aggregate(
            object_key=object_key,
            object_name=object_name,
            metric_code=metric_code,
            metric_name=METRICS[metric_code]["name"],
            source_type=source_type,
            codes=codes,
        )
        aggregate[key] = item
    item.amount += amount
    if warning_code:
        item.warning_codes.add(warning_code)
    item.drilldowns.append(drilldown)


def _build_query_rows(aggregate: dict[tuple[str, str], _Aggregate]) -> tuple[list[QueryRow], dict[str, list[DrilldownRecord]]]:
    rows: list[QueryRow] = []
    drilldowns: dict[str, list[DrilldownRecord]] = {}
    for item in sorted(aggregate.values(), key=lambda value: (value.object_name, value.metric_code)):
        row_id = f"{item.object_key}:{item.metric_code}"
        rows.append(
            QueryRow(
                row_id=row_id,
                object_key=item.object_key,
                object_name=item.object_name,
                metric_code=item.metric_code,
                metric_name=item.metric_name,
                amount=item.amount.quantize(Decimal("0.01")),
                source_type=item.source_type,
                codes=item.codes,
                warning_codes=sorted(item.warning_codes),
                drilldown_available=bool(item.drilldowns),
            )
        )
        drilldowns[row_id] = item.drilldowns
    return rows, drilldowns


def _build_totals(rows: list[QueryRow]) -> dict[str, Decimal]:
    totals: dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
    for row in rows:
        totals[row.metric_code] += row.amount
    return dict(totals)


def _latest_source(dataset: AnalyticsDataset, source_type: str, date_to: date | None) -> SourceFile | None:
    sources = [
        source
        for source in dataset.source_files
        if source.source_type == source_type and (source.period_date is None or date_to is None or source.period_date <= date_to)
    ]
    if not sources:
        return None
    usable_sources = [source for source in sources if source.rows_imported > 0 and source.errors_count == 0]
    if usable_sources:
        sources = usable_sources

    def sort_key(source: SourceFile) -> tuple[date, int, str]:
        period = source.period_date or date.min
        preferred_snapshot = 1 if source.original_name.startswith("на") else 0
        return period, preferred_snapshot, source.original_name

    return max(sources, key=sort_key)


def _max_available_date(dataset: AnalyticsDataset) -> date:
    candidates: list[date] = []
    candidates.extend(source.period_date for source in dataset.source_files if source.period_date)
    candidates.extend(fact.posting_date for fact in dataset.budget_facts if fact.posting_date)
    candidates.extend(agreement.close_date for agreement in dataset.agreements if agreement.close_date)
    candidates.extend(contract.con_date for contract in dataset.contracts if contract.con_date)
    candidates.extend(payment.platezhka_paydate for payment in dataset.payments if payment.platezhka_paydate)
    return max(candidates) if candidates else date.today()


def _date_in_range(value: date | None, start: date, end: date) -> bool:
    return bool(value and start <= value <= end)


def _query_quality_warnings(
    dataset: AnalyticsDataset,
    rows: list[QueryRow],
    drilldowns: dict[str, list[DrilldownRecord]],
    query: str | None,
) -> list[ImportIssue]:
    warning_methods = {code for row in rows for code in row.warning_codes}
    relevant_contract_ids = {
        str(record.details.get("con_document_id"))
        for records in drilldowns.values()
        for record in records
        if record.details.get("con_document_id")
    }
    query_text = query.strip().lower() if query else ""
    result: list[ImportIssue] = []
    seen: set[tuple[str, str, int | None]] = set()

    for issue in dataset.issues:
        relevant = False
        if issue.code == "contract_amount_allocated_equally":
            relevant = (
                "equal_by_line_no_amount" in warning_methods
                and any(contract_id in issue.message for contract_id in relevant_contract_ids)
            )
        elif issue.code in {"payment_contract_missing", "payment_budget_line_missing"} and query_text:
            raw_text = " ".join(str(value) for value in issue.raw.values()).lower()
            relevant = query_text in raw_text

        if not relevant:
            continue

        key = (issue.code, issue.message, issue.source_file_id)
        if key in seen:
            continue
        seen.add(key)
        result.append(issue)

    return result[:20]


def _s(value: object | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip().strip('"')
    return text or None


def _query_text_variants(query_text: str) -> set[str]:
    variants = {query_text}
    # Practical fuzzy case for common place-name inflection in the provided data:
    # user types "Тында", while budgets and recipients often contain "Тынды".
    if len(query_text) > 2 and query_text.endswith("а"):
        variants.add(f"{query_text[:-1]}ы")
    return variants
