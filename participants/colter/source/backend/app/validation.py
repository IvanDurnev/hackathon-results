"""Document validation beyond pure Pydantic schema checks.

Pydantic already enforces required fields and discriminators. This module
adds cross-field rules: positive sizes, asset references, layout references,
and text-overflow checks.
"""

from __future__ import annotations

import re

from .models import (
    LayoutDocument,
    PresentationDocument,
    SlideDocument,
    TemplateDocument,
)

HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


class ValidationIssue(dict):
    """A lightweight dict-like issue record."""

    def __init__(self, level: str, code: str, message: str, path: str = ""):
        super().__init__(level=level, code=code, message=message, path=path)


def _check_color(color: str, path: str, issues: list[ValidationIssue]) -> None:
    if not HEX_RE.match(color):
        issues.append(
            ValidationIssue("error", "color.invalid", f"Invalid hex color: {color}", path)
        )


def _check_elements(
    elements,
    asset_ids: set[str],
    placeholder_ids: set[str] | None,
    base_path: str,
    issues: list[ValidationIssue],
) -> None:
    for idx, el in enumerate(elements):
        path = f"{base_path}/elements[{idx}]"
        f = el.frame
        if f.wEmu < 0 or f.hEmu < 0 or (f.wEmu == 0 and f.hEmu == 0):
            issues.append(
                ValidationIssue("error", "frame.size", "Element size must be non-negative", path)
            )
        if f.xEmu < 0 or f.yEmu < 0:
            issues.append(
                ValidationIssue(
                    "warning", "frame.position", "Element is positioned off-slide", path
                )
            )
        if el.type == "image" and el.assetId and el.assetId not in asset_ids:
            issues.append(
                ValidationIssue(
                    "error",
                    "asset.missing",
                    f"Image references unknown assetId={el.assetId}",
                    path,
                )
            )
        if el.type == "text":
            c = el.constraints
            if c and c.maxChars is not None and len(el.text or "") > c.maxChars:
                level = "error" if (c.overflow == "error") else "warning"
                issues.append(
                    ValidationIssue(
                        level,
                        "text.overflow.chars",
                        f"Text length {len(el.text)} exceeds maxChars={c.maxChars}",
                        path,
                    )
                )
            if c and c.maxLines is not None and (el.text or "").count("\n") + 1 > c.maxLines:
                level = "error" if (c.overflow == "error") else "warning"
                issues.append(
                    ValidationIssue(
                        level,
                        "text.overflow.lines",
                        "Text exceeds maxLines",
                        path,
                    )
                )
        if (
            placeholder_ids is not None
            and el.sourcePlaceholderId
            and el.sourcePlaceholderId not in placeholder_ids
        ):
            issues.append(
                ValidationIssue(
                    "warning",
                    "placeholder.missing",
                    f"sourcePlaceholderId={el.sourcePlaceholderId} not found in layout",
                    path,
                )
            )


def validate_template(doc: TemplateDocument) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    asset_ids = {a.id for a in doc.assets}
    for li, layout in enumerate(doc.layouts):
        _check_elements(layout.elements, asset_ids, None, f"/layouts[{li}]", issues)
    return issues


def validate_presentation(doc: PresentationDocument) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    asset_ids = {a.id for a in doc.assets}
    for ci, color in enumerate(
        [
            doc.theme.colors.background,
            doc.theme.colors.text,
            doc.theme.colors.primary,
            doc.theme.colors.secondary,
            doc.theme.colors.accent,
        ]
    ):
        _check_color(color, f"/theme/colors[{ci}]", issues)
    for si, slide in enumerate(doc.slides):
        _check_elements(slide.elements, asset_ids, None, f"/slides[{si}]", issues)
    return issues


def export_blocking_errors(issues: list[ValidationIssue]) -> list[ValidationIssue]:
    return [i for i in issues if i.get("level") == "error"]
