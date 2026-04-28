import io
import re
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any, Iterable, Optional, Sequence

import pandas as pd
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agreements import Agreement
from app.models.classifiers import KcsrClassifier
from app.models.execution import BuauPayment, RcbExecution
from app.models.procurement import GzBudgetLine, GzContract, GzPayment


class ImportValidationError(ValueError):
    pass


class DataImportService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self._known_kcsr: set[str] = set()
        self._known_gz_contracts: dict[int, GzContract] = {}

    @staticmethod
    def _clean_value(value: Any) -> Optional[str]:
        if pd.isna(value):
            return None
        text = str(value).strip()
        if not text or text.lower() in {"nan", "none", "null"}:
            return None
        return text

    @classmethod
    def _clean_decimal(
        cls,
        value: Any,
        *,
        column: str,
        row_no: int,
        default: Decimal = Decimal("0"),
    ) -> Decimal:
        text = cls._clean_value(value)
        if text is None:
            return default

        cleaned = (
            text.replace("\xa0", "")
            .replace(" ", "")
            .replace(",", ".")
            .replace("−", "-")
        )
        if cleaned in {"", "-"}:
            return default
        try:
            return Decimal(cleaned)
        except InvalidOperation as exc:
            raise ImportValidationError(
                f"Invalid decimal in column '{column}', row {row_no}: {value!r}"
            ) from exc

    @classmethod
    def _clean_bigint(cls, value: Any, *, column: str, row_no: int) -> int:
        text = cls._clean_value(value)
        if text is None:
            raise ImportValidationError(
                f"Required id '{column}' is empty at row {row_no}"
            )

        cleaned = text.replace("\xa0", "").replace(" ", "")
        if cleaned.endswith(".0"):
            cleaned = cleaned[:-2]
        if not re.fullmatch(r"\d+", cleaned):
            raise ImportValidationError(
                f"Invalid bigint in column '{column}', row {row_no}: {value!r}"
            )
        return int(cleaned)

    @staticmethod
    def _clean_int(value: Any) -> Optional[int]:
        text = DataImportService._clean_value(value)
        if text is None:
            return None
        if text.endswith(".0"):
            text = text[:-2]
        return int(text)

    @staticmethod
    def _parse_date(value: Any, *, column: str, row_no: int) -> Optional[date]:
        text = DataImportService._clean_value(value)
        if text is None:
            return None

        # Agreements contain ranges like "2025-01-01 - 2025-02-01".
        if " - " in text:
            text = text.split(" - ", 1)[0]
        if " " in text:
            text = text.split(" ", 1)[0]

        for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(text, fmt).date()
            except ValueError:
                pass
        raise ImportValidationError(
            f"Invalid date in column '{column}', row {row_no}: {value!r}"
        )

    @staticmethod
    def _parse_period_date(value: Any, *, column: str, row_no: int) -> Optional[date]:
        text = DataImportService._clean_value(value)
        if text is None:
            return None
        if " - " not in text:
            return DataImportService._parse_date(value, column=column, row_no=row_no)

        end_text = text.split(" - ", 1)[1]
        end_date = DataImportService._parse_date(end_text, column=column, row_no=row_no)
        if end_date is None:
            return None
        return end_date - timedelta(days=1)

    @staticmethod
    def _find_column(df: pd.DataFrame, prefix: str) -> str:
        matches = [column for column in df.columns if str(column).startswith(prefix)]
        if not matches:
            raise ImportValidationError(f"Missing required column prefix: {prefix}")
        return matches[0]

    @staticmethod
    async def _read_upload(file: UploadFile) -> bytes:
        await file.seek(0)
        return await file.read()

    async def _read_csv(
        self,
        file: UploadFile,
        *,
        sep: str = ",",
        skiprows: int = 0,
    ) -> pd.DataFrame:
        content = await self._read_upload(file)
        df = pd.read_csv(
            io.BytesIO(content),
            sep=sep,
            skiprows=skiprows,
            dtype=str,
            keep_default_na=False,
        )
        df.columns = [str(column).strip() for column in df.columns]
        return df

    @staticmethod
    def _iter_files(files: Optional[Sequence[UploadFile]]) -> Iterable[UploadFile]:
        return files or ()

    async def _ensure_kcsr_exists(
        self, kcsr_code: Any, kcsr_name: Optional[Any] = None
    ) -> Optional[str]:
        code = self._clean_value(kcsr_code)
        if not code:
            return None

        if code in self._known_kcsr:
            return code

        exists = await self.db.get(KcsrClassifier, code)
        if exists is None:
            self.db.add(
                KcsrClassifier(
                    kcsr_code=code,
                    kcsr_name=self._clean_value(kcsr_name) or "Не указано",
                )
            )
        self._known_kcsr.add(code)
        return code

    async def _get_or_create_gz_contract(self, con_id: int) -> GzContract:
        cached = self._known_gz_contracts.get(con_id)
        if cached is not None:
            return cached

        exists = await self.db.get(GzContract, con_id)
        if exists is not None:
            self._known_gz_contracts[con_id] = exists
            return exists

        contract = GzContract(con_document_id=con_id, con_amount=Decimal("0"))
        self.db.add(contract)
        self._known_gz_contracts[con_id] = contract
        return contract

    async def _ensure_gz_contract_exists(self, con_id: int) -> None:
        await self._get_or_create_gz_contract(con_id)

    async def process_rcb_file(self, file: UploadFile) -> int:
        df = await self._read_csv(file, sep=";", skiprows=10)

        limit_col = self._find_column(df, "Лимиты ПБС")
        confirmed_col = self._find_column(df, "Подтв. лимитов по БО")
        remaining_col = self._find_column(df, "Остаток лимитов")
        payments_col = "Всего выбытий (бух.уч.)"
        if payments_col not in df.columns:
            raise ImportValidationError(f"Missing required column: {payments_col}")

        inserted = 0
        for row_no, row in enumerate(df.to_dict("records"), start=2):
            k_code = await self._ensure_kcsr_exists(
                row.get("КЦСР"), row.get("Наименование КЦСР")
            )
            if not k_code:
                continue

            posting_date = self._parse_date(
                row.get("Дата проводки"), column="Дата проводки", row_no=row_no
            )
            if posting_date is None:
                continue

            self.db.add(
                RcbExecution(
                    budget_name=self._clean_value(row.get("Бюджет")),
                    posting_date=posting_date,
                    kfsr_code=self._clean_value(row.get("КФСР")),
                    kfsr_name=self._clean_value(row.get("Наименование КФСР")),
                    kcsr_code=k_code,
                    kcsr_name=self._clean_value(row.get("Наименование КЦСР")),
                    kvr_code=self._clean_value(row.get("КВР")),
                    kvr_name=self._clean_value(row.get("Наименование КВР")),
                    kvsr_code=self._clean_value(row.get("КВСР")),
                    kosgu_code=self._clean_value(row.get("КОСГУ")),
                    fund_source=self._clean_value(row.get("Источник средств")),
                    limit_pbs_cur_year=self._clean_decimal(
                        row.get(limit_col), column=limit_col, row_no=row_no
                    ),
                    limit_confirmed=self._clean_decimal(
                        row.get(confirmed_col), column=confirmed_col, row_no=row_no
                    ),
                    limit_remaining=self._clean_decimal(
                        row.get(remaining_col), column=remaining_col, row_no=row_no
                    ),
                    total_payments=self._clean_decimal(
                        row.get(payments_col), column=payments_col, row_no=row_no
                    ),
                    budget_period=posting_date.strftime("%Y-%m"),
                )
            )
            inserted += 1
        return inserted

    async def process_agreements_file(self, file: UploadFile) -> int:
        df = await self._read_csv(file)

        inserted = 0
        for row_no, row in enumerate(df.to_dict("records"), start=2):
            k_code = await self._ensure_kcsr_exists(row.get("kcsr_code"))
            if not k_code:
                continue

            self.db.add(
                Agreement(
                    period_of_date=self._parse_period_date(
                        row.get("period_of_date"),
                        column="period_of_date",
                        row_no=row_no,
                    ),
                    documentclass_id=self._clean_int(row.get("documentclass_id")),
                    budget_id=self._clean_value(row.get("budget_id")),
                    caption=self._clean_value(row.get("caption")),
                    document_id=self._clean_bigint(
                        row.get("document_id"), column="document_id", row_no=row_no
                    ),
                    close_date=self._parse_date(
                        row.get("close_date"), column="close_date", row_no=row_no
                    ),
                    reg_number=self._clean_value(row.get("reg_number")),
                    kadmr_code=self._clean_value(row.get("kadmr_code")),
                    kfsr_code=self._clean_value(row.get("kfsr_code")),
                    kcsr_code=k_code,
                    kvr_code=self._clean_value(row.get("kvr_code")),
                    kesr_code=self._clean_value(row.get("kesr_code")),
                    purposefulgrant_code=self._clean_value(
                        row.get("dd_purposefulgrant_code")
                    ),
                    amount_1year=self._clean_decimal(
                        row.get("amount_1year"),
                        column="amount_1year",
                        row_no=row_no,
                    ),
                    dd_recipient_caption=self._clean_value(
                        row.get("dd_recipient_caption")
                    ),
                    dd_estimate_caption=self._clean_value(
                        row.get("dd_estimate_caption")
                    ),
                )
            )
            inserted += 1
        return inserted

    async def process_gz_contracts_file(self, file: UploadFile) -> int:
        df = await self._read_csv(file)

        upserted = 0
        for row_no, row in enumerate(df.to_dict("records"), start=2):
            con_id = self._clean_bigint(
                row.get("con_document_id"), column="con_document_id", row_no=row_no
            )
            contract = await self._get_or_create_gz_contract(con_id)

            contract.con_number = self._clean_value(row.get("con_number"))
            contract.con_date = self._parse_date(
                row.get("con_date"), column="con_date", row_no=row_no
            )
            contract.con_amount = self._clean_decimal(
                row.get("con_amount"), column="con_amount", row_no=row_no
            )
            contract.zakazchik_key = self._clean_value(row.get("zakazchik_key"))
            upserted += 1
        return upserted

    async def process_gz_budget_lines_file(self, file: UploadFile) -> int:
        df = await self._read_csv(file)

        inserted = 0
        for row_no, row in enumerate(df.to_dict("records"), start=2):
            k_code = await self._ensure_kcsr_exists(row.get("kcsr_code"))
            if not k_code:
                continue

            con_id = self._clean_bigint(
                row.get("con_document_id"), column="con_document_id", row_no=row_no
            )
            await self._ensure_gz_contract_exists(con_id)
            self.db.add(
                GzBudgetLine(
                    con_document_id=con_id,
                    kfsr_code=self._clean_value(row.get("kfsr_code")),
                    kcsr_code=k_code,
                    kvr_code=self._clean_value(row.get("kvr_code")),
                    kesr_code=self._clean_value(row.get("kesr_code")),
                    kvsr_code=self._clean_value(row.get("kvsr_code")),
                    purposefulgrant=self._clean_value(row.get("purposefulgrant")),
                )
            )
            inserted += 1
        return inserted

    async def process_gz_payments_file(self, file: UploadFile) -> int:
        df = await self._read_csv(file)

        inserted = 0
        for row_no, row in enumerate(df.to_dict("records"), start=2):
            con_id = self._clean_bigint(
                row.get("con_document_id"), column="con_document_id", row_no=row_no
            )
            await self._ensure_gz_contract_exists(con_id)
            self.db.add(
                GzPayment(
                    con_document_id=con_id,
                    platezhka_paydate=self._parse_date(
                        row.get("platezhka_paydate"),
                        column="platezhka_paydate",
                        row_no=row_no,
                    ),
                    platezhka_key=self._clean_value(row.get("platezhka_key")),
                    platezhka_num=self._clean_value(row.get("platezhka_num")),
                    platezhka_amount=self._clean_decimal(
                        row.get("platezhka_amount"),
                        column="platezhka_amount",
                        row_no=row_no,
                    ),
                )
            )
            inserted += 1
        return inserted

    async def process_gz_file(self, file: UploadFile) -> int:
        return await self.process_gz_budget_lines_file(file)

    async def process_buau_file(self, file: UploadFile) -> int:
        df = await self._read_csv(file, sep=";")

        inserted = 0
        for row_no, row in enumerate(df.to_dict("records"), start=2):
            budget_name = self._clean_value(row.get("Бюджет"))
            if not budget_name or budget_name.lower() == "итого":
                continue

            k_code = await self._ensure_kcsr_exists(row.get("КЦСР"))
            if not k_code:
                continue

            posting_date = self._parse_date(
                row.get("Дата проводки"), column="Дата проводки", row_no=row_no
            )
            if posting_date is None:
                continue

            self.db.add(
                BuauPayment(
                    budget_name=budget_name,
                    posting_date=posting_date,
                    kfsr_code=self._clean_value(row.get("КФСР")),
                    kcsr_code=k_code,
                    kvr_code=self._clean_value(row.get("КВР")),
                    kosgu_code=self._clean_value(row.get("КОСГУ")),
                    subsidy_code=self._clean_value(row.get("Код субсидии")),
                    branch_code=self._clean_value(row.get("Отраслевой код")),
                    kvfo_code=self._clean_value(row.get("КВФО")),
                    organization_name=self._clean_value(row.get("Организация")),
                    grantor_name=self._clean_value(
                        row.get("Орган, предоставляющий субсидии")
                    ),
                    payments_net=self._clean_decimal(
                        row.get("Выплаты с учетом возврата"),
                        column="Выплаты с учетом возврата",
                        row_no=row_no,
                    ),
                    payments_execution=self._clean_decimal(
                        row.get("Выплаты - Исполнение"),
                        column="Выплаты - Исполнение",
                        row_no=row_no,
                    ),
                    payments_restore=self._clean_decimal(
                        row.get("Выплаты - Восстановление выплат - год"),
                        column="Выплаты - Восстановление выплат - год",
                        row_no=row_no,
                    ),
                    budget_period=posting_date.strftime("%Y-%m"),
                )
            )
            inserted += 1
        return inserted

    async def import_all_data(
        self,
        rcb_file: Optional[UploadFile] = None,
        agr_file: Optional[UploadFile] = None,
        gz_budget_line_file: Optional[UploadFile] = None,
        gz_contract_file: Optional[UploadFile] = None,
        gz_payment_file: Optional[UploadFile] = None,
        buau_file: Optional[UploadFile] = None,
    ) -> dict[str, Any]:
        stats: dict[str, int] = {
            "rcb_rows": 0,
            "agreement_rows": 0,
            "gz_contract_rows": 0,
            "gz_budget_line_rows": 0,
            "gz_payment_rows": 0,
            "buau_rows": 0,
        }

        try:
            if rcb_file:
                stats["rcb_rows"] += await self.process_rcb_file(rcb_file)
            if agr_file:
                stats["agreement_rows"] += await self.process_agreements_file(agr_file)
            if gz_contract_file:
                stats["gz_contract_rows"] += await self.process_gz_contracts_file(
                    gz_contract_file
                )
            if gz_budget_line_file:
                stats["gz_budget_line_rows"] += await self.process_gz_budget_lines_file(
                    gz_budget_line_file
                )
            if gz_payment_file:
                stats["gz_payment_rows"] += await self.process_gz_payments_file(
                    gz_payment_file
                )
            if buau_file:
                stats["buau_rows"] += await self.process_buau_file(buau_file)

            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise

        return {"message": "Импорт завершен успешно", "stats": stats}
