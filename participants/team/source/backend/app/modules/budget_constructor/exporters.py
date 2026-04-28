from __future__ import annotations

import csv
from io import StringIO
from pathlib import Path

from app.modules.budget_constructor.types import QueryResult


CSV_COLUMNS = [
    ("object_name", "Объект"),
    ("metric_name", "Показатель"),
    ("amount", "Сумма"),
    ("source_type", "Источник"),
    ("warning_codes", "Предупреждения"),
]


def query_result_to_csv(result: QueryResult) -> str:
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([caption for _, caption in CSV_COLUMNS])
    for row in result.rows:
        writer.writerow(
            [
                row.object_name,
                row.metric_name,
                f"{row.amount:.2f}",
                row.source_type,
                ", ".join(row.warning_codes),
            ]
        )
    return output.getvalue()


def query_result_to_xlsx(result: QueryResult, path: Path | str) -> Path:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    output_path = Path(path)
    wb = Workbook()
    ws = wb.active
    ws.title = "Выборка"
    ws.append([caption for _, caption in CSV_COLUMNS])

    header_fill = PatternFill("solid", fgColor="D9EAF7")
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")

    for row in result.rows:
        ws.append(
            [
                row.object_name,
                row.metric_name,
                float(row.amount),
                row.source_type,
                ", ".join(row.warning_codes),
            ]
        )

    for col_idx in range(1, len(CSV_COLUMNS) + 1):
        width = max(len(str(ws.cell(row_idx, col_idx).value or "")) for row_idx in range(1, ws.max_row + 1))
        ws.column_dimensions[get_column_letter(col_idx)].width = min(max(width + 2, 12), 70)

    for cell in ws["C"][1:]:
        cell.number_format = '# ##0.00'

    if result.warnings:
        issues_ws = wb.create_sheet("Предупреждения")
        issues_ws.append(["Уровень", "Код", "Сообщение"])
        for issue in result.warnings:
            issues_ws.append([issue.severity, issue.code, issue.message])
        for cell in issues_ws[1]:
            cell.font = Font(bold=True)
            cell.fill = header_fill
        for col_idx in range(1, 4):
            width = max(len(str(issues_ws.cell(row_idx, col_idx).value or "")) for row_idx in range(1, issues_ws.max_row + 1))
            issues_ws.column_dimensions[get_column_letter(col_idx)].width = min(max(width + 2, 12), 100)

    wb.save(output_path)
    return output_path
