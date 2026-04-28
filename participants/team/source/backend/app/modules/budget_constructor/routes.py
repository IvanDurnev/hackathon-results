from __future__ import annotations

from flask import Blueprint, Response, request

from app.core.permissions import admin_required, auth_required
from app.core.responses import json_response
from app.core.security import json_payload
from app.modules.budget_constructor.schemas import (
    AnalyticsDrilldownRequest,
    AnalyticsExportRequest,
    AnalyticsImportRequest,
    AnalyticsQueryRequest,
    AnalyticsQueryResponse,
    CompareRowResponse,
    DrilldownRecordResponse,
    ImportIssueResponse,
    MetricResponse,
    QueryColumnResponse,
    QueryRowResponse,
    SearchHitResponse,
    SourceResponse,
    TemplateResponse,
    TimelinePointResponse,
)
from app.modules.budget_constructor.services import (
    build_compare,
    build_query_result,
    build_timeline,
    export_query,
    find_objects,
    get_dataset,
    get_drilldown,
    list_metrics,
    list_templates,
    reload_dataset,
)

bp = Blueprint("analytics", __name__)


@bp.get("/sources")
@auth_required
def sources_index():
    dataset = get_dataset()
    return json_response({"items": [SourceResponse(**source.__dict__) for source in dataset.source_files]})


@bp.post("/import-demo")
@admin_required
def import_demo():
    payload = AnalyticsImportRequest.model_validate(json_payload())
    dataset = reload_dataset(payload.folder_path)
    return json_response(
        {
            "sources": len(dataset.source_files),
            "issues": len(dataset.issues),
            "message": "Демонстрационные данные импортированы в БД.",
        }
    )


@bp.get("/import-issues")
@auth_required
def import_issues():
    dataset = get_dataset()
    return json_response({"items": [ImportIssueResponse(**_issue_payload(issue)) for issue in dataset.issues]})


@bp.get("/metrics")
@auth_required
def metrics_index():
    return json_response({"items": [MetricResponse(**metric) for metric in list_metrics()]})


@bp.get("/templates")
@auth_required
def templates_index():
    return json_response({"items": [TemplateResponse(**template) for template in list_templates()]})


@bp.get("/search")
@auth_required
def search_index():
    query = request.args.get("q", "")
    return json_response({"items": [SearchHitResponse(**hit.__dict__) for hit in find_objects(query)]})


@bp.post("/query")
@auth_required
def query_create():
    payload = AnalyticsQueryRequest.model_validate(json_payload())
    result = build_query_result(payload)
    return json_response(_query_response(result))


@bp.post("/timeline")
@auth_required
def timeline_create():
    payload = AnalyticsQueryRequest.model_validate(json_payload())
    points = build_timeline(payload)
    return json_response({"items": [TimelinePointResponse(**point.__dict__) for point in points]})


@bp.post("/compare")
@auth_required
def compare_create():
    payload = AnalyticsQueryRequest.model_validate(json_payload())
    result = build_compare(payload)
    return json_response({"items": [CompareRowResponse(**row.__dict__) for row in result.rows]})


@bp.post("/drilldown")
@auth_required
def drilldown_create():
    payload = AnalyticsDrilldownRequest.model_validate(json_payload())
    records = get_drilldown(payload)
    return json_response({"items": [DrilldownRecordResponse(**record.__dict__) for record in records]})


@bp.post("/export")
@auth_required
def export_create():
    payload = AnalyticsExportRequest.model_validate(json_payload())
    content, filename, content_type = export_query(payload)
    return Response(
        content,
        mimetype=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _query_response(result) -> AnalyticsQueryResponse:
    return AnalyticsQueryResponse(
        columns=[
            QueryColumnResponse(key="object_name", title="Объект"),
            QueryColumnResponse(key="metric_name", title="Показатель"),
            QueryColumnResponse(key="amount", title="Сумма"),
            QueryColumnResponse(key="source_type", title="Источник"),
        ],
        rows=[QueryRowResponse(**row.__dict__) for row in result.rows],
        totals=result.totals,
        warnings=[ImportIssueResponse(**_issue_payload(issue)) for issue in result.warnings],
    )


def _issue_payload(issue) -> dict:
    return {
        "severity": issue.severity,
        "code": issue.code,
        "message": issue.message,
        "source_file_id": issue.source_file_id,
        "row_number": issue.row_number,
    }
