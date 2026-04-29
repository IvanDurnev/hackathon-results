from __future__ import annotations

import csv
import hashlib
import re
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path


CODE_RE = re.compile(r"[^0-9A-Za-zА-Яа-я]")
RCHB_PERIOD_RE = re.compile(r"\bна\s+(\d{2})\.(\d{2})\.(\d{4})\s*г?", re.IGNORECASE)
FILENAME_DATE_RE = re.compile(r"(\d{2})(\d{2})(\d{4})")

RU_MONTHS = {
    "январь": 1,
    "февраль": 2,
    "март": 3,
    "апрель": 4,
    "май": 5,
    "июнь": 6,
    "июль": 7,
    "август": 8,
    "сентябрь": 9,
    "октябрь": 10,
    "ноябрь": 11,
    "декабрь": 12,
}


@dataclass(frozen=True)
class CsvProfile:
    encoding: str
    delimiter: str
    header_row: int
    columns: list[str]
    sha256: str


def normalize_code(value: object | None) -> str | None:
    if value is None:
        return None
    code = CODE_RE.sub("", str(value).strip()).upper()
    return code or None


def kcsr_slice(value: object | None, start: int, length: int) -> str | None:
    code = normalize_code(value)
    if not code or start < 1 or length < 1:
        return None
    begin = start - 1
    end = begin + length
    if len(code) < end:
        return None
    return code[begin:end]


def parse_date(value: object | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    text = str(value).strip().strip('"')
    if not text:
        return None
    for fmt in ("%d.%m.%Y", "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Неизвестный формат даты: {value!r}")


def parse_money(value: object | None) -> Decimal:
    if value is None:
        return Decimal("0.00")
    text = str(value).strip().strip('"').replace("\xa0", " ").replace(" ", "")
    if not text:
        return Decimal("0.00")
    text = re.sub(r"[^0-9,.-]", "", text)
    if "," in text and "." in text:
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    else:
        text = text.replace(",", ".")
    try:
        return Decimal(text).quantize(Decimal("0.01"))
    except InvalidOperation as exc:
        raise ValueError(f"Некорректная сумма: {value!r}") from exc


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def decode_bytes(data: bytes) -> tuple[str, str]:
    for encoding in ("utf-8-sig", "utf-8", "cp1251", "cp866"):
        try:
            return data.decode(encoding), encoding
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace"), "utf-8-replace"


def detect_delimiter(lines: list[str]) -> str:
    candidates = [",", ";", "\t", "|"]
    return max(candidates, key=lambda delimiter: max((line.count(delimiter) for line in lines[:30]), default=0))


def header_score(row: list[str]) -> int:
    text = " ".join(cell.lower() for cell in row if cell.strip())
    required_terms = (
        "бюджет",
        "дата проводки",
        "кфср",
        "кцср",
        "con_document_id",
        "document_id",
        "platezhka",
        "лимиты",
    )
    return sum(1 for cell in row if cell.strip()) + 10 * sum(term in text for term in required_terms)


def read_csv_smart(path: Path) -> tuple[CsvProfile, list[dict[str, str]]]:
    data = path.read_bytes()
    text, encoding = decode_bytes(data)
    lines = text.splitlines()
    delimiter = detect_delimiter(lines)
    parsed = list(csv.reader(lines, delimiter=delimiter))
    if not parsed:
        profile = CsvProfile(encoding, delimiter, 1, [], hashlib.sha256(data).hexdigest())
        return profile, []

    header_index, header = max(
        ((index, row) for index, row in enumerate(parsed[:50])),
        key=lambda item: header_score(item[1]),
    )
    columns = [column.strip().replace("\ufeff", "") for column in header]
    rows: list[dict[str, str]] = []
    for row in parsed[header_index + 1 :]:
        if not any(cell.strip() for cell in row):
            continue
        normalized = list(row)
        if len(normalized) < len(columns):
            normalized += [""] * (len(columns) - len(normalized))
        rows.append(dict(zip(columns, normalized[: len(columns)])))

    profile = CsvProfile(
        encoding=encoding,
        delimiter=delimiter,
        header_row=header_index + 1,
        columns=columns,
        sha256=hashlib.sha256(data).hexdigest(),
    )
    return profile, rows


def extract_rchb_period_date(path: Path) -> date | None:
    text, _ = decode_bytes(path.read_bytes())
    for line in text.splitlines()[:12]:
        match = RCHB_PERIOD_RE.search(line)
        if match:
            day, month, year = match.groups()
            return date(int(year), int(month), int(day))
    return infer_period_date_from_filename(path)


def infer_period_date_from_filename(path: Path) -> date | None:
    stem = path.stem.lower()
    dates = FILENAME_DATE_RE.findall(stem)
    if dates:
        day, month, year = dates[-1]
        return date(int(year), int(month), int(day))

    for month_name, month in RU_MONTHS.items():
        if month_name in stem:
            year_match = re.search(r"(20\d{2})", stem)
            if year_match:
                return date(int(year_match.group(1)), month, 1)
    return None


def extract_period_end(value: object | None) -> date | None:
    if value is None:
        return None
    text = str(value)
    parts = re.findall(r"\d{4}-\d{2}-\d{2}", text)
    if parts:
        return parse_date(parts[-1])
    return parse_date(text)


def is_total_row(row: dict[str, str]) -> bool:
    for key in ("Бюджет", "budget", "caption"):
        value = row.get(key)
        if value and value.strip().lower().startswith("итого"):
            return True
    return False
