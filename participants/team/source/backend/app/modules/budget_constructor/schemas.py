from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class AnalyticsQueryRequest(BaseModel):
    mode: Literal["search", "template"] = "search"
    template_code: str | None = None
    query: str | None = None
    object_keys: list[str] = Field(default_factory=list)
    metrics: list[str] = Field(default_factory=list, min_length=1)
    date_mode: Literal["range", "compare"] = "range"
    date_from: date | None = None
    date_to: date | None = None
    base_date: date | None = None
    compare_date: date | None = None

    @field_validator("metrics")
    @classmethod
    def metrics_are_unique(cls, values: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for value in values:
            if value not in seen:
                seen.add(value)
                result.append(value)
        return result


class AnalyticsDrilldownRequest(AnalyticsQueryRequest):
    row_id: str = Field(min_length=1)


class AnalyticsExportRequest(AnalyticsQueryRequest):
    format: Literal["csv", "xlsx"] = "csv"


class AnalyticsImportRequest(BaseModel):
    folder_path: str | None = None


class MetricResponse(BaseModel):
    code: str
    name: str
    source_type: str


class TemplateResponse(BaseModel):
    code: str
    name: str
    description: str


class SourceResponse(BaseModel):
    id: int
    source_type: str
    original_name: str
    checksum: str
    period_date: date | None
    rows_total: int
    rows_imported: int
    warnings_count: int
    errors_count: int
    metadata: dict


class ImportIssueResponse(BaseModel):
    severity: str
    code: str
    message: str
    source_file_id: int | None = None
    row_number: int | None = None


class SearchHitResponse(BaseModel):
    object_key: str
    object_type: str
    display_name: str
    matched_codes: dict[str, str | None]
    rank: int
    source_types: list[str]


class QueryColumnResponse(BaseModel):
    key: str
    title: str


class QueryRowResponse(BaseModel):
    row_id: str
    object_key: str
    object_name: str
    metric_code: str
    metric_name: str
    amount: float
    source_type: str
    codes: dict[str, str | None]
    warning_codes: list[str]
    drilldown_available: bool


class AnalyticsQueryResponse(BaseModel):
    columns: list[QueryColumnResponse]
    rows: list[QueryRowResponse]
    totals: dict[str, float]
    warnings: list[ImportIssueResponse]


class TimelinePointResponse(BaseModel):
    period: date
    metric_code: str
    metric_name: str
    amount: float


class CompareRowResponse(BaseModel):
    object_key: str
    object_name: str
    metric_code: str
    metric_name: str
    base_value: float
    compare_value: float
    delta: float
    delta_percent: float | None


class DrilldownRecordResponse(BaseModel):
    source_type: str
    label: str
    amount: float
    event_date: date | None
    details: dict
