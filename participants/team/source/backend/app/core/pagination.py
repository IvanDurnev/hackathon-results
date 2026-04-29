from flask import current_app, request


def parse_positive_int(value: str | None, default: int) -> int:
    try:
        parsed = int(value or default)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def pagination_args() -> tuple[int, int]:
    default_per_page = current_app.config.get("ITEMS_PER_PAGE", 20)
    max_per_page = current_app.config.get("MAX_PER_PAGE", 100)
    page = parse_positive_int(request.args.get("page"), 1)
    per_page = parse_positive_int(request.args.get("per_page"), default_per_page)
    return page, min(per_page, max_per_page)


def pagination_meta(pagination) -> dict[str, int]:
    return {
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages,
    }
