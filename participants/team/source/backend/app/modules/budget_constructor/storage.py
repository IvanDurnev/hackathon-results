from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from app.extensions import db
from app.modules.budget_constructor.models import (
    AnalyticsAgreement,
    AnalyticsBudgetFact,
    AnalyticsContract,
    AnalyticsContractBudgetLine,
    AnalyticsImportIssue,
    AnalyticsPayment,
    AnalyticsSourceFile,
)
from app.modules.budget_constructor.types import (
    AgreementFact,
    AnalyticsDataset,
    BudgetFact,
    ContractBudgetLine,
    ContractFact,
    ImportIssue,
    PaymentFact,
    SourceFile,
)


def has_persisted_dataset() -> bool:
    return db.session.query(AnalyticsSourceFile.id).first() is not None


def replace_persisted_dataset(dataset: AnalyticsDataset) -> None:
    _clear_persisted_dataset()
    _persist_sources(dataset)
    _persist_budget_facts(dataset)
    _persist_agreements(dataset)
    _persist_contracts(dataset)
    _persist_contract_budget_lines(dataset)
    _persist_payments(dataset)
    _persist_import_issues(dataset)
    db.session.commit()


def load_persisted_dataset() -> AnalyticsDataset:
    dataset = AnalyticsDataset()

    dataset.source_files = [
        SourceFile(
            id=source.id,
            source_type=source.source_type,
            path=Path(source.stored_path or source.original_name),
            original_name=source.original_name,
            checksum=source.checksum,
            period_date=source.period_date,
            rows_total=source.rows_total,
            rows_imported=source.rows_imported,
            warnings_count=source.warnings_count,
            errors_count=source.errors_count,
            metadata=source.metadata_json or {},
        )
        for source in AnalyticsSourceFile.query.order_by(AnalyticsSourceFile.id).all()
    ]

    dataset.budget_facts = [
        BudgetFact(
            id=fact.id,
            source_file_id=fact.source_file_id,
            source_type=fact.source_type,
            period_date=fact.period_date,
            budget_name=fact.budget_name,
            posting_date=fact.posting_date,
            kfsr_code=fact.kfsr_code,
            kfsr_norm=fact.kfsr_norm,
            kfsr_name=fact.kfsr_name,
            kcsr_code=fact.kcsr_code,
            kcsr_norm=fact.kcsr_norm,
            kcsr_name=fact.kcsr_name,
            kvr_code=fact.kvr_code,
            kvr_norm=fact.kvr_norm,
            kvr_name=fact.kvr_name,
            kvsr_code=fact.kvsr_code,
            kvsr_norm=fact.kvsr_norm,
            kvsr_name=fact.kvsr_name,
            kesr_code=fact.kesr_code,
            kesr_norm=fact.kesr_norm,
            purposefulgrant_code=fact.purposefulgrant_code,
            purposefulgrant_norm=fact.purposefulgrant_norm,
            kdr_code=fact.kdr_code,
            kdr_norm=fact.kdr_norm,
            kde_code=fact.kde_code,
            kde_norm=fact.kde_norm,
            kdf_code=fact.kdf_code,
            kdf_norm=fact.kdf_norm,
            limits_amount=_decimal(fact.limits_amount),
            accepted_bo_amount=_decimal(fact.accepted_bo_amount),
            accepted_without_bo_amount=_decimal(fact.accepted_without_bo_amount),
            remaining_limits_amount=_decimal(fact.remaining_limits_amount),
            cash_amount=_decimal(fact.cash_amount),
            buau_payment_amount=_decimal(fact.buau_payment_amount),
            buau_execution_amount=_decimal(fact.buau_execution_amount),
            buau_recovery_amount=_decimal(fact.buau_recovery_amount),
            buau_organization=fact.buau_organization,
            buau_grantor=fact.buau_grantor,
            raw=fact.raw or {},
        )
        for fact in AnalyticsBudgetFact.query.order_by(AnalyticsBudgetFact.id).all()
    ]

    dataset.agreements = [
        AgreementFact(
            id=agreement.id,
            source_file_id=agreement.source_file_id,
            period_date=agreement.period_date,
            documentclass_id=agreement.documentclass_id,
            budget_id=agreement.budget_id,
            budget_caption=agreement.budget_caption,
            document_id=agreement.document_id,
            close_date=agreement.close_date,
            reg_number=agreement.reg_number,
            main_close_date=agreement.main_close_date,
            main_reg_number=agreement.main_reg_number,
            amount_1year=_decimal(agreement.amount_1year),
            estimate_caption=agreement.estimate_caption,
            recipient_caption=agreement.recipient_caption,
            kadmr_code=agreement.kadmr_code,
            kadmr_norm=agreement.kadmr_norm,
            kfsr_code=agreement.kfsr_code,
            kfsr_norm=agreement.kfsr_norm,
            kcsr_code=agreement.kcsr_code,
            kcsr_norm=agreement.kcsr_norm,
            kvr_code=agreement.kvr_code,
            kvr_norm=agreement.kvr_norm,
            kesr_code=agreement.kesr_code,
            kesr_norm=agreement.kesr_norm,
            purposefulgrant_code=agreement.purposefulgrant_code,
            purposefulgrant_norm=agreement.purposefulgrant_norm,
            kdr_code=agreement.kdr_code,
            kdr_norm=agreement.kdr_norm,
            kde_code=agreement.kde_code,
            kde_norm=agreement.kde_norm,
            kdf_code=agreement.kdf_code,
            kdf_norm=agreement.kdf_norm,
            grantinvestment_code=agreement.grantinvestment_code,
            grantinvestment_norm=agreement.grantinvestment_norm,
            raw=agreement.raw or {},
        )
        for agreement in AnalyticsAgreement.query.order_by(AnalyticsAgreement.id).all()
    ]

    dataset.contracts = [
        ContractFact(
            id=contract.id,
            source_file_id=contract.source_file_id,
            con_document_id=contract.con_document_id,
            con_number=contract.con_number,
            con_date=contract.con_date,
            con_amount=_decimal(contract.con_amount),
            zakazchik_key=contract.zakazchik_key,
            raw=contract.raw or {},
        )
        for contract in AnalyticsContract.query.order_by(AnalyticsContract.id).all()
    ]

    dataset.contract_budget_lines = [
        ContractBudgetLine(
            id=line.id,
            source_file_id=line.source_file_id,
            con_document_id=line.con_document_id,
            kfsr_code=line.kfsr_code,
            kfsr_norm=line.kfsr_norm,
            kcsr_code=line.kcsr_code,
            kcsr_norm=line.kcsr_norm,
            kvr_code=line.kvr_code,
            kvr_norm=line.kvr_norm,
            kesr_code=line.kesr_code,
            kesr_norm=line.kesr_norm,
            kvsr_code=line.kvsr_code,
            kvsr_norm=line.kvsr_norm,
            kdf_code=line.kdf_code,
            kdf_norm=line.kdf_norm,
            kde_code=line.kde_code,
            kde_norm=line.kde_norm,
            kdr_code=line.kdr_code,
            kdr_norm=line.kdr_norm,
            kif_code=line.kif_code,
            kif_norm=line.kif_norm,
            purposefulgrant_code=line.purposefulgrant_code,
            purposefulgrant_norm=line.purposefulgrant_norm,
            allocation_share=_decimal(line.allocation_share),
            allocation_method=line.allocation_method,
            raw=line.raw or {},
        )
        for line in AnalyticsContractBudgetLine.query.order_by(AnalyticsContractBudgetLine.id).all()
    ]

    dataset.payments = [
        PaymentFact(
            id=payment.id,
            source_file_id=payment.source_file_id,
            con_document_id=payment.con_document_id,
            platezhka_paydate=payment.platezhka_paydate,
            platezhka_key=payment.platezhka_key,
            platezhka_num=payment.platezhka_num,
            platezhka_amount=_decimal(payment.platezhka_amount),
            linked_to_budget_line=payment.linked_to_budget_line,
            raw=payment.raw or {},
        )
        for payment in AnalyticsPayment.query.order_by(AnalyticsPayment.id).all()
    ]

    dataset.issues = [
        ImportIssue(
            severity=issue.severity,
            code=issue.code,
            message=issue.message,
            source_file_id=issue.source_file_id,
            row_number=issue.row_number,
            raw=issue.raw or {},
        )
        for issue in AnalyticsImportIssue.query.order_by(AnalyticsImportIssue.id).all()
    ]

    return dataset


def _clear_persisted_dataset() -> None:
    for model in (
        AnalyticsImportIssue,
        AnalyticsPayment,
        AnalyticsContractBudgetLine,
        AnalyticsContract,
        AnalyticsAgreement,
        AnalyticsBudgetFact,
        AnalyticsSourceFile,
    ):
        db.session.query(model).delete(synchronize_session=False)
    db.session.flush()


def _persist_sources(dataset: AnalyticsDataset) -> None:
    for source in dataset.source_files:
        db.session.add(
            AnalyticsSourceFile(
                id=source.id,
                source_type=source.source_type,
                original_name=source.original_name,
                stored_path=str(source.path),
                period_date=source.period_date,
                checksum=source.checksum,
                rows_total=source.rows_total,
                rows_imported=source.rows_imported,
                warnings_count=source.warnings_count,
                errors_count=source.errors_count,
                status="error" if source.errors_count else "imported",
                metadata_json=source.metadata or {},
            )
        )
    db.session.flush()


def _persist_budget_facts(dataset: AnalyticsDataset) -> None:
    db.session.bulk_save_objects(
        [
            AnalyticsBudgetFact(
                id=fact.id,
                source_file_id=fact.source_file_id,
                source_type=fact.source_type,
                period_date=fact.period_date,
                budget_name=fact.budget_name,
                posting_date=fact.posting_date,
                kfsr_code=fact.kfsr_code,
                kfsr_norm=fact.kfsr_norm,
                kfsr_name=fact.kfsr_name,
                kcsr_code=fact.kcsr_code,
                kcsr_norm=fact.kcsr_norm,
                kcsr_name=fact.kcsr_name,
                kvr_code=fact.kvr_code,
                kvr_norm=fact.kvr_norm,
                kvr_name=fact.kvr_name,
                kvsr_code=fact.kvsr_code,
                kvsr_norm=fact.kvsr_norm,
                kvsr_name=fact.kvsr_name,
                kesr_code=fact.kesr_code,
                kesr_norm=fact.kesr_norm,
                purposefulgrant_code=fact.purposefulgrant_code,
                purposefulgrant_norm=fact.purposefulgrant_norm,
                kdr_code=fact.kdr_code,
                kdr_norm=fact.kdr_norm,
                kde_code=fact.kde_code,
                kde_norm=fact.kde_norm,
                kdf_code=fact.kdf_code,
                kdf_norm=fact.kdf_norm,
                limits_amount=fact.limits_amount,
                accepted_bo_amount=fact.accepted_bo_amount,
                accepted_without_bo_amount=fact.accepted_without_bo_amount,
                remaining_limits_amount=fact.remaining_limits_amount,
                cash_amount=fact.cash_amount,
                buau_payment_amount=fact.buau_payment_amount,
                buau_execution_amount=fact.buau_execution_amount,
                buau_recovery_amount=fact.buau_recovery_amount,
                buau_organization=fact.buau_organization,
                buau_grantor=fact.buau_grantor,
                raw=fact.raw or {},
            )
            for fact in dataset.budget_facts
        ]
    )


def _persist_agreements(dataset: AnalyticsDataset) -> None:
    db.session.bulk_save_objects(
        [
            AnalyticsAgreement(
                id=agreement.id,
                source_file_id=agreement.source_file_id,
                period_date=agreement.period_date,
                documentclass_id=agreement.documentclass_id,
                budget_id=agreement.budget_id,
                budget_caption=agreement.budget_caption,
                document_id=agreement.document_id,
                close_date=agreement.close_date,
                reg_number=agreement.reg_number,
                main_close_date=agreement.main_close_date,
                main_reg_number=agreement.main_reg_number,
                amount_1year=agreement.amount_1year,
                estimate_caption=agreement.estimate_caption,
                recipient_caption=agreement.recipient_caption,
                kadmr_code=agreement.kadmr_code,
                kadmr_norm=agreement.kadmr_norm,
                kfsr_code=agreement.kfsr_code,
                kfsr_norm=agreement.kfsr_norm,
                kcsr_code=agreement.kcsr_code,
                kcsr_norm=agreement.kcsr_norm,
                kvr_code=agreement.kvr_code,
                kvr_norm=agreement.kvr_norm,
                kesr_code=agreement.kesr_code,
                kesr_norm=agreement.kesr_norm,
                purposefulgrant_code=agreement.purposefulgrant_code,
                purposefulgrant_norm=agreement.purposefulgrant_norm,
                kdr_code=agreement.kdr_code,
                kdr_norm=agreement.kdr_norm,
                kde_code=agreement.kde_code,
                kde_norm=agreement.kde_norm,
                kdf_code=agreement.kdf_code,
                kdf_norm=agreement.kdf_norm,
                grantinvestment_code=agreement.grantinvestment_code,
                grantinvestment_norm=agreement.grantinvestment_norm,
                raw=agreement.raw or {},
            )
            for agreement in dataset.agreements
        ]
    )


def _persist_contracts(dataset: AnalyticsDataset) -> None:
    db.session.bulk_save_objects(
        [
            AnalyticsContract(
                id=contract.id,
                source_file_id=contract.source_file_id,
                con_document_id=contract.con_document_id,
                con_number=contract.con_number,
                con_date=contract.con_date,
                con_amount=contract.con_amount,
                zakazchik_key=contract.zakazchik_key,
                raw=contract.raw or {},
            )
            for contract in dataset.contracts
        ]
    )


def _persist_contract_budget_lines(dataset: AnalyticsDataset) -> None:
    db.session.bulk_save_objects(
        [
            AnalyticsContractBudgetLine(
                id=line.id,
                source_file_id=line.source_file_id,
                con_document_id=line.con_document_id,
                kfsr_code=line.kfsr_code,
                kfsr_norm=line.kfsr_norm,
                kcsr_code=line.kcsr_code,
                kcsr_norm=line.kcsr_norm,
                kvr_code=line.kvr_code,
                kvr_norm=line.kvr_norm,
                kesr_code=line.kesr_code,
                kesr_norm=line.kesr_norm,
                kvsr_code=line.kvsr_code,
                kvsr_norm=line.kvsr_norm,
                kdf_code=line.kdf_code,
                kdf_norm=line.kdf_norm,
                kde_code=line.kde_code,
                kde_norm=line.kde_norm,
                kdr_code=line.kdr_code,
                kdr_norm=line.kdr_norm,
                kif_code=line.kif_code,
                kif_norm=line.kif_norm,
                purposefulgrant_code=line.purposefulgrant_code,
                purposefulgrant_norm=line.purposefulgrant_norm,
                allocation_share=line.allocation_share,
                allocation_method=line.allocation_method,
                raw=line.raw or {},
            )
            for line in dataset.contract_budget_lines
        ]
    )


def _persist_payments(dataset: AnalyticsDataset) -> None:
    db.session.bulk_save_objects(
        [
            AnalyticsPayment(
                id=payment.id,
                source_file_id=payment.source_file_id,
                con_document_id=payment.con_document_id,
                platezhka_paydate=payment.platezhka_paydate,
                platezhka_key=payment.platezhka_key,
                platezhka_num=payment.platezhka_num,
                platezhka_amount=payment.platezhka_amount,
                linked_to_budget_line=payment.linked_to_budget_line,
                raw=payment.raw or {},
            )
            for payment in dataset.payments
        ]
    )


def _persist_import_issues(dataset: AnalyticsDataset) -> None:
    db.session.bulk_save_objects(
        [
            AnalyticsImportIssue(
                source_file_id=issue.source_file_id,
                severity=issue.severity,
                code=issue.code,
                message=issue.message,
                row_number=issue.row_number,
                raw=issue.raw or {},
            )
            for issue in dataset.issues
        ]
    )


def _decimal(value: Decimal | int | float | str | None) -> Decimal:
    if value is None:
        return Decimal("0.00")
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))

