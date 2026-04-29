from __future__ import annotations

import os
import tempfile
from pathlib import Path, PurePosixPath
from typing import Iterable

from flask import current_app
from werkzeug.datastructures import FileStorage

from app.config import REPO_ROOT
from app.core.errors import ResourceNotFound, ValidationAppError
from app.modules.budget_constructor.engine import (
    METRICS,
    TEMPLATE_LABELS,
    compare_dataset,
    load_task_dataset,
    query_dataset,
    search_dataset,
    timeline_dataset,
)
from app.modules.budget_constructor.exporters import query_result_to_csv, query_result_to_xlsx
from app.modules.budget_constructor.storage import (
    clear_persisted_dataset,
    has_persisted_dataset,
    load_persisted_dataset,
    replace_persisted_dataset,
)
from app.modules.budget_constructor.types import AnalyticsDataset, QueryResult

_DATASET_CACHE: AnalyticsDataset | None = None

EXPECTED_TASK_DIRS = ("1. РЧБ", "2. Соглашения", "3. ГЗ", "4. Выгрузка БУАУ")


TEMPLATE_DESCRIPTIONS = {
    "kik": "КЦСР=*****978**. В предоставленных CSV может не быть строк для этого контрольного раздела.",
    "skk": "КЦСР=*****6105*. Сведения по специальным казначейским кредитам.",
    "two_three": "КЦСР=*****970**. Раздел 3 контрольного примера.",
    "okv": "ОКВ: ДопКР не равен 0.",
}


def analytics_task_dir(folder_path: str | Path | None = None) -> Path:
    if folder_path:
        path = Path(folder_path).expanduser()
        if not path.is_absolute():
            path = REPO_ROOT / path
        return path.resolve()

    configured = current_app.config.get("ANALYTICS_TASK_DIR") or os.getenv("ANALYTICS_TASK_DIR")
    if configured:
        return Path(configured).expanduser().resolve()
    return REPO_ROOT / "task"


def get_dataset(*, reload: bool = False) -> AnalyticsDataset:
    global _DATASET_CACHE
    if _DATASET_CACHE is not None and not reload:
        return _DATASET_CACHE

    if reload:
        return reload_dataset()

    if has_persisted_dataset():
        _DATASET_CACHE = load_persisted_dataset()
        return _DATASET_CACHE

    if current_app.config.get("ANALYTICS_AUTO_IMPORT", False):
        return reload_dataset()

    _DATASET_CACHE = AnalyticsDataset()
    return _DATASET_CACHE


def reload_dataset(folder_path: str | Path | None = None) -> AnalyticsDataset:
    global _DATASET_CACHE
    task_dir = analytics_task_dir(folder_path)
    if not task_dir.exists():
        raise ResourceNotFound(f"Папка с демонстрационными данными не найдена: {task_dir}")
    if not task_dir.is_dir():
        raise ValidationAppError(f"Путь импорта должен быть папкой: {task_dir}")

    parsed_dataset = load_task_dataset(task_dir)
    replace_persisted_dataset(parsed_dataset)
    _DATASET_CACHE = load_persisted_dataset()
    return _DATASET_CACHE


def reload_dataset_from_uploads(uploaded_files: Iterable[FileStorage]) -> AnalyticsDataset:
    files = [file for file in uploaded_files if file.filename]
    if not files:
        raise ValidationAppError("Выберите папку с файлами для импорта.")

    with tempfile.TemporaryDirectory(prefix="analytics-upload-") as temp_dir:
        staging_dir = Path(temp_dir)
        for file in files:
            relative_path = _safe_upload_relative_path(file.filename or "")
            destination = staging_dir / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            file.save(destination)

        task_dir = _find_uploaded_task_root(staging_dir)
        return reload_dataset(task_dir)


def reset_dataset() -> AnalyticsDataset:
    global _DATASET_CACHE
    clear_persisted_dataset()
    _DATASET_CACHE = AnalyticsDataset()
    return _DATASET_CACHE


def _safe_upload_relative_path(filename: str) -> Path:
    normalized = filename.replace("\\", "/").strip("/")
    parts = [part for part in PurePosixPath(normalized).parts if part not in ("", ".")]
    if not parts or any(part == ".." for part in parts):
        raise ValidationAppError("Имя загруженного файла содержит недопустимый путь.")
    return Path(*parts)


def _find_uploaded_task_root(staging_dir: Path) -> Path:
    candidates = [staging_dir, *(path for path in staging_dir.rglob("*") if path.is_dir())]

    def score(path: Path) -> int:
        return sum(1 for directory in EXPECTED_TASK_DIRS if (path / directory).is_dir())

    task_dir = max(candidates, key=score)
    if score(task_dir) == 0:
        expected = ", ".join(EXPECTED_TASK_DIRS)
        raise ValidationAppError(f"Выберите папку с подкаталогами источников: {expected}.")
    return task_dir


def list_metrics() -> list[dict[str, str]]:
    return [
        {"code": code, "name": meta["name"], "source_type": meta["source"]}
        for code, meta in METRICS.items()
    ]


def list_templates() -> list[dict[str, str]]:
    return [
        {"code": code, "name": name, "description": TEMPLATE_DESCRIPTIONS[code]}
        for code, name in TEMPLATE_LABELS.items()
    ]


def build_query_result(payload) -> QueryResult:
    if payload.date_mode != "range":
        raise ValidationAppError("Для табличной выборки используйте date_mode=range.")
    return query_dataset(
        get_dataset(),
        metrics=payload.metrics,
        date_from=payload.date_from,
        date_to=payload.date_to,
        query=payload.query,
        object_keys=payload.object_keys,
        template_code=payload.template_code if payload.mode == "template" else None,
    )


def build_timeline(payload):
    return timeline_dataset(
        get_dataset(),
        metrics=payload.metrics,
        date_from=payload.date_from,
        date_to=payload.date_to,
        query=payload.query,
        object_keys=payload.object_keys,
        template_code=payload.template_code if payload.mode == "template" else None,
    )


def build_compare(payload):
    if not payload.base_date or not payload.compare_date:
        raise ValidationAppError("Для сравнения нужны base_date и compare_date.")
    return compare_dataset(
        get_dataset(),
        metrics=payload.metrics,
        base_date=payload.base_date,
        compare_date=payload.compare_date,
        query=payload.query,
        object_keys=payload.object_keys,
        template_code=payload.template_code if payload.mode == "template" else None,
    )


def find_objects(query: str):
    return search_dataset(get_dataset(), query)


def get_drilldown(payload):
    result = build_query_result(payload)
    return result.drilldowns.get(payload.row_id, [])


def export_query(payload) -> tuple[bytes, str, str]:
    result = build_query_result(payload)
    if payload.format == "csv":
        return (
            query_result_to_csv(result).encode("utf-8-sig"),
            "analytics-selection.csv",
            "text/csv; charset=utf-8",
        )

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as temp:
        temp_path = Path(temp.name)
    try:
        query_result_to_xlsx(result, temp_path)
        return (
            temp_path.read_bytes(),
            "analytics-selection.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    finally:
        temp_path.unlink(missing_ok=True)
