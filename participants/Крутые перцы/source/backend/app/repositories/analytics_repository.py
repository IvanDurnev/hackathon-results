import re
from decimal import Decimal
from typing import Optional

from sqlalchemy import and_, case, cast, func, literal, select, true, distinct
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agreements import Agreement
from app.models.classifiers import KcsrClassifier
from app.models.execution import BuauPayment, RcbExecution
from app.models.procurement import GzBudgetLine, GzContract, GzPayment


class AnalyticsRepository:
    @staticmethod
    def _mask_token(mask: str) -> str:
        cleaned = re.sub(r"[%*_]", "", mask or "")
        return re.sub(r"[^0-9A-Za-zА-Яа-яЁё]", "", cleaned).upper()

    @staticmethod
    def _compact_code(column):
        return func.upper(func.regexp_replace(column, r"[^0-9A-Za-zА-Яа-яЁё]", "", "g"))

    @classmethod
    def _match_key(cls, column, token: str):
        return literal(token) if token else cls._compact_code(column)

    @classmethod
    def _token_filter(cls, column, token: str):
        if not token:
            return true()
        return cls._compact_code(column).like(f"%{token}%")

    async def get_budget_names(self, db: AsyncSession) -> str:
        query = select(distinct(RcbExecution.budget_name)).where(
            RcbExecution.budget_name.isnot(None)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_kcsrs(self, db: AsyncSession) -> str:
        query = select(distinct(RcbExecution.kcsr_code)).where(
            RcbExecution.kcsr_code.isnot(None)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_budget_constructor_data(
        self,
        db: AsyncSession,
        p_kcsr_mask: str,
        p_budget_name: str,
        p_period_from: str,
        p_period_to: str,
        p_fund_source: Optional[str] = None,
        p_min_amount: Decimal = Decimal("0"),
    ) -> list[dict]:
        token = AnalyticsRepository._mask_token(p_kcsr_mask)
        zero = Decimal("0")

        # 1. CTE для РКБ (Базовая выборка)
        rcb_key = AnalyticsRepository._match_key(RcbExecution.kcsr_code, token)
        rcb_conditions = [
            RcbExecution.budget_period.between(p_period_from, p_period_to),
            AnalyticsRepository._token_filter(RcbExecution.kcsr_code, token),
        ]
        if p_budget_name:
            rcb_conditions.append(RcbExecution.budget_name.ilike(f"%{p_budget_name}%"))
        if p_fund_source:
            rcb_conditions.append(RcbExecution.fund_source.ilike(f"%{p_fund_source}%"))

        rcb_base = (
            select(
                rcb_key.label("kcsr_match_key"),
                RcbExecution.kcsr_code,
                RcbExecution.kcsr_name,
                RcbExecution.budget_name,
                RcbExecution.kfsr_code,
                RcbExecution.kfsr_name,
                RcbExecution.fund_source,
                RcbExecution.budget_period,
                func.sum(func.coalesce(RcbExecution.limit_pbs_cur_year, zero)).label(
                    "limit_pbs"
                ),
                func.sum(func.coalesce(RcbExecution.limit_confirmed, zero)).label(
                    "budget_obligations"
                ),
                func.sum(func.coalesce(RcbExecution.limit_remaining, zero)).label(
                    "limit_remaining"
                ),
                func.sum(func.coalesce(RcbExecution.total_payments, zero)).label(
                    "rcb_payments"
                ),
                func.sum(
                    case(
                        (
                            RcbExecution.kvr_code.like("2%"),
                            func.coalesce(RcbExecution.total_payments, zero),
                        ),
                        else_=zero,
                    )
                ).label("rcb_payments_kvr2"),
                func.sum(
                    case(
                        (
                            RcbExecution.kvr_code.like("5%"),
                            func.coalesce(RcbExecution.total_payments, zero),
                        ),
                        else_=zero,
                    )
                ).label("rcb_payments_kvr5"),
                func.sum(
                    case(
                        (
                            RcbExecution.kvr_code.like("6%"),
                            func.coalesce(RcbExecution.total_payments, zero),
                        ),
                        else_=zero,
                    )
                ).label("rcb_payments_kvr6"),
            )
            .where(and_(*rcb_conditions))
            .group_by(
                rcb_key,
                RcbExecution.kcsr_code,
                RcbExecution.kcsr_name,
                RcbExecution.budget_name,
                RcbExecution.kfsr_code,
                RcbExecution.kfsr_name,
                RcbExecution.fund_source,
                RcbExecution.budget_period,
            )
            .cte("rcb_base")
        )

        # 2. CTE для БУАУ
        buau_key = AnalyticsRepository._match_key(BuauPayment.kcsr_code, token)
        buau_agg = (
            select(
                buau_key.label("kcsr_match_key"),
                BuauPayment.budget_period,
                func.sum(func.coalesce(BuauPayment.payments_net, zero)).label(
                    "buau_payments"
                ),
            )
            .where(
                and_(
                    BuauPayment.budget_period.between(p_period_from, p_period_to),
                    AnalyticsRepository._token_filter(BuauPayment.kcsr_code, token),
                )
            )
            .group_by(buau_key, BuauPayment.budget_period)
            .cte("buau_agg")
        )

        # 3. CTE для Соглашений
        agr_key = AnalyticsRepository._match_key(Agreement.kcsr_code, token)
        agr_period = func.to_char(Agreement.period_of_date, "YYYY-MM")
        agr_amount = func.coalesce(Agreement.amount_1year, zero)

        agr_agg = (
            select(
                agr_key.label("kcsr_match_key"),
                agr_period.label("budget_period"),
                func.sum(
                    case((Agreement.documentclass_id == 273, agr_amount), else_=zero)
                ).label("agr_mbt_amount"),
                func.sum(
                    case(
                        (Agreement.documentclass_id.in_([272, 278, 313]), agr_amount),
                        else_=zero,
                    )
                ).label("agr_subsidy_amount"),
                func.sum(agr_amount).label("agr_amount"),
            )
            .where(
                and_(
                    agr_period.between(p_period_from, p_period_to),
                    AnalyticsRepository._token_filter(Agreement.kcsr_code, token),
                )
            )
            .group_by(agr_key, agr_period)
            .cte("agr_agg")
        )

        agr_details_agg = (
            select(
                agr_key.label("kcsr_match_key"),
                agr_period.label("budget_period"),
                cast(
                    func.jsonb_agg(
                        func.jsonb_build_object(
                            "date",
                            Agreement.close_date,
                            "number",
                            Agreement.reg_number,
                            "recipient",
                            Agreement.dd_recipient_caption,
                            "amount",
                            Agreement.amount_1year,
                            "documentclass_id",
                            Agreement.documentclass_id,
                        )
                    ),
                    JSONB,
                ).label("agreement_details"),
            )
            .where(
                and_(
                    agr_period.between(p_period_from, p_period_to),
                    AnalyticsRepository._token_filter(Agreement.kcsr_code, token),
                )
            )
            .group_by(agr_key, agr_period)
            .cte("agr_details_agg")
        )

        # 4. CTE для Госзакупок (Контракты)
        gz_key = AnalyticsRepository._match_key(GzBudgetLine.kcsr_code, token)
        gz_contract_period = func.to_char(GzContract.con_date, "YYYY-MM")

        # Исправленный подзапрос с select_from
        uniq_contracts_subq = (
            select(
                gz_key.label("kcsr_match_key"),
                GzContract.con_document_id,
                GzContract.con_number,
                GzContract.con_date,
                GzContract.con_amount,
                GzContract.zakazchik_key,
                gz_contract_period.label("budget_period"),
            )
            .select_from(GzBudgetLine)
            .join(
                GzContract, GzContract.con_document_id == GzBudgetLine.con_document_id
            )
            .where(
                and_(
                    gz_contract_period.between(p_period_from, p_period_to),
                    AnalyticsRepository._token_filter(GzBudgetLine.kcsr_code, token),
                )
            )
            .distinct()
            .subquery()
        )

        gz_contracts_agg = (
            select(
                uniq_contracts_subq.c.kcsr_match_key,
                uniq_contracts_subq.c.budget_period,
                func.sum(func.coalesce(uniq_contracts_subq.c.con_amount, zero)).label(
                    "gz_contracts_amount"
                ),
            )
            .group_by(
                uniq_contracts_subq.c.kcsr_match_key,
                uniq_contracts_subq.c.budget_period,
            )
            .cte("gz_contracts_agg")
        )

        gz_contract_details_agg = (
            select(
                uniq_contracts_subq.c.kcsr_match_key,
                uniq_contracts_subq.c.budget_period,
                cast(
                    func.jsonb_agg(
                        func.jsonb_build_object(
                            "date",
                            uniq_contracts_subq.c.con_date,
                            "number",
                            uniq_contracts_subq.c.con_number,
                            "counterparty",
                            uniq_contracts_subq.c.zakazchik_key,
                            "amount",
                            uniq_contracts_subq.c.con_amount,
                        )
                    ),
                    JSONB,
                ).label("gz_contract_details"),
            )
            .group_by(
                uniq_contracts_subq.c.kcsr_match_key,
                uniq_contracts_subq.c.budget_period,
            )
            .cte("gz_contract_details_agg")
        )

        # 5. CTE для Госзакупок (Платежи)
        # Исправленный подзапрос с select_from
        gz_lines_subq = (
            select(
                gz_key.label("kcsr_match_key"),
                GzBudgetLine.con_document_id,
            )
            .select_from(GzBudgetLine)
            .where(AnalyticsRepository._token_filter(GzBudgetLine.kcsr_code, token))
            .distinct()
            .subquery()
        )

        gz_payment_period = func.to_char(GzPayment.platezhka_paydate, "YYYY-MM")
        gz_payments_agg = (
            select(
                gz_lines_subq.c.kcsr_match_key,
                gz_payment_period.label("budget_period"),
                func.sum(func.coalesce(GzPayment.platezhka_amount, zero)).label(
                    "gz_paid"
                ),
            )
            .select_from(gz_lines_subq)
            .join(
                GzPayment, GzPayment.con_document_id == gz_lines_subq.c.con_document_id
            )
            .where(gz_payment_period.between(p_period_from, p_period_to))
            .group_by(gz_lines_subq.c.kcsr_match_key, gz_payment_period)
            .cte("gz_payments_agg")
        )

        gz_payment_details_agg = (
            select(
                gz_lines_subq.c.kcsr_match_key,
                gz_payment_period.label("budget_period"),
                cast(
                    func.jsonb_agg(
                        func.jsonb_build_object(
                            "date",
                            GzPayment.platezhka_paydate,
                            "number",
                            GzPayment.platezhka_num,
                            "payment_key",
                            GzPayment.platezhka_key,
                            "amount",
                            GzPayment.platezhka_amount,
                        )
                    ),
                    JSONB,
                ).label("gz_payment_details"),
            )
            .select_from(gz_lines_subq)
            .join(
                GzPayment, GzPayment.con_document_id == gz_lines_subq.c.con_document_id
            )
            .where(gz_payment_period.between(p_period_from, p_period_to))
            .group_by(gz_lines_subq.c.kcsr_match_key, gz_payment_period)
            .cte("gz_payment_details_agg")
        )

        # --- ИТОГОВЫЙ ЗАПРОС ---
        stmt = (
            select(
                rcb_base.c.kcsr_code,
                func.coalesce(KcsrClassifier.kcsr_name, rcb_base.c.kcsr_name).label(
                    "kcsr_name"
                ),
                rcb_base.c.budget_name,
                rcb_base.c.kfsr_code,
                rcb_base.c.kfsr_name,
                rcb_base.c.fund_source,
                rcb_base.c.budget_period,
                rcb_base.c.limit_pbs,
                rcb_base.c.budget_obligations,
                rcb_base.c.limit_remaining,
                rcb_base.c.rcb_payments,
                rcb_base.c.rcb_payments_kvr2,
                rcb_base.c.rcb_payments_kvr5,
                rcb_base.c.rcb_payments_kvr6,
                func.coalesce(buau_agg.c.buau_payments, zero).label("buau_payments"),
                func.coalesce(agr_agg.c.agr_amount, zero).label("agr_amount"),
                func.coalesce(agr_agg.c.agr_mbt_amount, zero).label("agr_mbt_amount"),
                func.coalesce(agr_agg.c.agr_subsidy_amount, zero).label(
                    "agr_subsidy_amount"
                ),
                func.coalesce(gz_contracts_agg.c.gz_contracts_amount, zero).label(
                    "gz_contracts_amount"
                ),
                func.coalesce(gz_payments_agg.c.gz_paid, zero).label("gz_paid"),
                agr_details_agg.c.agreement_details,
                gz_contract_details_agg.c.gz_contract_details,
                gz_payment_details_agg.c.gz_payment_details,
            )
            .select_from(rcb_base)
            .outerjoin(KcsrClassifier, KcsrClassifier.kcsr_code == rcb_base.c.kcsr_code)
            .outerjoin(
                buau_agg,
                and_(
                    buau_agg.c.kcsr_match_key == rcb_base.c.kcsr_match_key,
                    buau_agg.c.budget_period == rcb_base.c.budget_period,
                ),
            )
            .outerjoin(
                agr_agg,
                and_(
                    agr_agg.c.kcsr_match_key == rcb_base.c.kcsr_match_key,
                    agr_agg.c.budget_period == rcb_base.c.budget_period,
                ),
            )
            .outerjoin(
                gz_contracts_agg,
                and_(
                    gz_contracts_agg.c.kcsr_match_key == rcb_base.c.kcsr_match_key,
                    gz_contracts_agg.c.budget_period == rcb_base.c.budget_period,
                ),
            )
            .outerjoin(
                gz_payments_agg,
                and_(
                    gz_payments_agg.c.kcsr_match_key == rcb_base.c.kcsr_match_key,
                    gz_payments_agg.c.budget_period == rcb_base.c.budget_period,
                ),
            )
            .outerjoin(
                agr_details_agg,
                and_(
                    agr_details_agg.c.kcsr_match_key == rcb_base.c.kcsr_match_key,
                    agr_details_agg.c.budget_period == rcb_base.c.budget_period,
                ),
            )
            .outerjoin(
                gz_contract_details_agg,
                and_(
                    gz_contract_details_agg.c.kcsr_match_key
                    == rcb_base.c.kcsr_match_key,
                    gz_contract_details_agg.c.budget_period == rcb_base.c.budget_period,
                ),
            )
            .outerjoin(
                gz_payment_details_agg,
                and_(
                    gz_payment_details_agg.c.kcsr_match_key
                    == rcb_base.c.kcsr_match_key,
                    gz_payment_details_agg.c.budget_period == rcb_base.c.budget_period,
                ),
            )
            .where(rcb_base.c.limit_pbs >= func.coalesce(p_min_amount, zero))
            .order_by(rcb_base.c.limit_pbs.desc())
        )

        result = await db.execute(stmt)
        rows = []
        for row in result.mappings().all():
            item = dict(row)
            # Гарантируем, что JSON-поля вернут пустой список вместо None
            item["agreement_details"] = item.get("agreement_details") or []
            item["gz_contract_details"] = item.get("gz_contract_details") or []
            item["gz_payment_details"] = item.get("gz_payment_details") or []
            rows.append(item)

        return rows
