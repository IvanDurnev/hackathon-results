from app.extensions import db
from app.modules.shared.models import TimestampMixin


class AnalyticsSourceFile(TimestampMixin, db.Model):
    __tablename__ = "analytics_source_files"

    id = db.Column(db.Integer, primary_key=True)
    source_type = db.Column(db.String(50), nullable=False, index=True)
    original_name = db.Column(db.String(255), nullable=False)
    stored_path = db.Column(db.Text, nullable=True)
    period_date = db.Column(db.Date, nullable=True, index=True)
    checksum = db.Column(db.String(64), nullable=False, index=True)
    rows_total = db.Column(db.Integer, default=0, nullable=False)
    rows_imported = db.Column(db.Integer, default=0, nullable=False)
    warnings_count = db.Column(db.Integer, default=0, nullable=False)
    errors_count = db.Column(db.Integer, default=0, nullable=False)
    status = db.Column(db.String(32), default="imported", nullable=False, index=True)
    metadata_json = db.Column("metadata", db.JSON, default=dict, nullable=False)


class AnalyticsBudgetFact(db.Model):
    __tablename__ = "analytics_budget_facts"

    id = db.Column(db.Integer, primary_key=True)
    source_file_id = db.Column(
        db.Integer,
        db.ForeignKey("analytics_source_files.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_type = db.Column(db.String(50), nullable=False, index=True)
    period_date = db.Column(db.Date, nullable=True, index=True)
    budget_name = db.Column(db.Text, nullable=True)
    posting_date = db.Column(db.Date, nullable=True, index=True)
    kfsr_code = db.Column(db.String(64), nullable=True)
    kfsr_norm = db.Column(db.String(64), nullable=True, index=True)
    kfsr_name = db.Column(db.Text, nullable=True)
    kcsr_code = db.Column(db.String(64), nullable=True)
    kcsr_norm = db.Column(db.String(64), nullable=True, index=True)
    kcsr_name = db.Column(db.Text, nullable=True)
    kvr_code = db.Column(db.String(64), nullable=True)
    kvr_norm = db.Column(db.String(64), nullable=True, index=True)
    kvr_name = db.Column(db.Text, nullable=True)
    kvsr_code = db.Column(db.String(64), nullable=True)
    kvsr_norm = db.Column(db.String(64), nullable=True, index=True)
    kvsr_name = db.Column(db.Text, nullable=True)
    kesr_code = db.Column(db.String(64), nullable=True)
    kesr_norm = db.Column(db.String(64), nullable=True, index=True)
    purposefulgrant_code = db.Column(db.String(128), nullable=True)
    purposefulgrant_norm = db.Column(db.String(128), nullable=True, index=True)
    kdr_code = db.Column(db.String(64), nullable=True)
    kdr_norm = db.Column(db.String(64), nullable=True, index=True)
    kde_code = db.Column(db.String(64), nullable=True)
    kde_norm = db.Column(db.String(64), nullable=True, index=True)
    kdf_code = db.Column(db.String(64), nullable=True)
    kdf_norm = db.Column(db.String(64), nullable=True, index=True)
    limits_amount = db.Column(db.Numeric(20, 2), default=0, nullable=False)
    accepted_bo_amount = db.Column(db.Numeric(20, 2), default=0, nullable=False)
    accepted_without_bo_amount = db.Column(db.Numeric(20, 2), default=0, nullable=False)
    remaining_limits_amount = db.Column(db.Numeric(20, 2), default=0, nullable=False)
    cash_amount = db.Column(db.Numeric(20, 2), default=0, nullable=False)
    buau_payment_amount = db.Column(db.Numeric(20, 2), default=0, nullable=False)
    buau_execution_amount = db.Column(db.Numeric(20, 2), default=0, nullable=False)
    buau_recovery_amount = db.Column(db.Numeric(20, 2), default=0, nullable=False)
    buau_organization = db.Column(db.Text, nullable=True)
    buau_grantor = db.Column(db.Text, nullable=True)
    raw = db.Column(db.JSON, default=dict, nullable=False)


class AnalyticsAgreement(db.Model):
    __tablename__ = "analytics_agreements"

    id = db.Column(db.Integer, primary_key=True)
    source_file_id = db.Column(
        db.Integer,
        db.ForeignKey("analytics_source_files.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    period_date = db.Column(db.Date, nullable=True, index=True)
    documentclass_id = db.Column(db.String(32), nullable=True, index=True)
    budget_id = db.Column(db.String(128), nullable=True)
    budget_caption = db.Column(db.Text, nullable=True)
    document_id = db.Column(db.String(128), nullable=True, index=True)
    close_date = db.Column(db.Date, nullable=True, index=True)
    reg_number = db.Column(db.String(255), nullable=True, index=True)
    main_close_date = db.Column(db.Date, nullable=True)
    main_reg_number = db.Column(db.String(255), nullable=True)
    amount_1year = db.Column(db.Numeric(20, 2), default=0, nullable=False)
    estimate_caption = db.Column(db.Text, nullable=True)
    recipient_caption = db.Column(db.Text, nullable=True)
    kadmr_code = db.Column(db.String(64), nullable=True)
    kadmr_norm = db.Column(db.String(64), nullable=True, index=True)
    kfsr_code = db.Column(db.String(64), nullable=True)
    kfsr_norm = db.Column(db.String(64), nullable=True, index=True)
    kcsr_code = db.Column(db.String(64), nullable=True)
    kcsr_norm = db.Column(db.String(64), nullable=True, index=True)
    kvr_code = db.Column(db.String(64), nullable=True)
    kvr_norm = db.Column(db.String(64), nullable=True, index=True)
    kesr_code = db.Column(db.String(64), nullable=True)
    kesr_norm = db.Column(db.String(64), nullable=True, index=True)
    purposefulgrant_code = db.Column(db.String(128), nullable=True)
    purposefulgrant_norm = db.Column(db.String(128), nullable=True, index=True)
    kdr_code = db.Column(db.String(64), nullable=True)
    kdr_norm = db.Column(db.String(64), nullable=True, index=True)
    kde_code = db.Column(db.String(64), nullable=True)
    kde_norm = db.Column(db.String(64), nullable=True, index=True)
    kdf_code = db.Column(db.String(64), nullable=True)
    kdf_norm = db.Column(db.String(64), nullable=True, index=True)
    grantinvestment_code = db.Column(db.String(128), nullable=True)
    grantinvestment_norm = db.Column(db.String(128), nullable=True, index=True)
    raw = db.Column(db.JSON, default=dict, nullable=False)


class AnalyticsContract(db.Model):
    __tablename__ = "analytics_contracts"

    id = db.Column(db.Integer, primary_key=True)
    source_file_id = db.Column(
        db.Integer,
        db.ForeignKey("analytics_source_files.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    con_document_id = db.Column(db.String(128), nullable=False, index=True)
    con_number = db.Column(db.String(255), nullable=True, index=True)
    con_date = db.Column(db.Date, nullable=True, index=True)
    con_amount = db.Column(db.Numeric(20, 2), default=0, nullable=False)
    zakazchik_key = db.Column(db.Text, nullable=True)
    raw = db.Column(db.JSON, default=dict, nullable=False)


class AnalyticsContractBudgetLine(db.Model):
    __tablename__ = "analytics_contract_budget_lines"

    id = db.Column(db.Integer, primary_key=True)
    source_file_id = db.Column(
        db.Integer,
        db.ForeignKey("analytics_source_files.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    con_document_id = db.Column(db.String(128), nullable=False, index=True)
    kfsr_code = db.Column(db.String(64), nullable=True)
    kfsr_norm = db.Column(db.String(64), nullable=True, index=True)
    kcsr_code = db.Column(db.String(64), nullable=True)
    kcsr_norm = db.Column(db.String(64), nullable=True, index=True)
    kvr_code = db.Column(db.String(64), nullable=True)
    kvr_norm = db.Column(db.String(64), nullable=True, index=True)
    kesr_code = db.Column(db.String(64), nullable=True)
    kesr_norm = db.Column(db.String(64), nullable=True, index=True)
    kvsr_code = db.Column(db.String(64), nullable=True)
    kvsr_norm = db.Column(db.String(64), nullable=True, index=True)
    kdf_code = db.Column(db.String(64), nullable=True)
    kdf_norm = db.Column(db.String(64), nullable=True, index=True)
    kde_code = db.Column(db.String(64), nullable=True)
    kde_norm = db.Column(db.String(64), nullable=True, index=True)
    kdr_code = db.Column(db.String(64), nullable=True)
    kdr_norm = db.Column(db.String(64), nullable=True, index=True)
    kif_code = db.Column(db.String(64), nullable=True)
    kif_norm = db.Column(db.String(64), nullable=True, index=True)
    purposefulgrant_code = db.Column(db.String(128), nullable=True)
    purposefulgrant_norm = db.Column(db.String(128), nullable=True, index=True)
    allocation_share = db.Column(db.Numeric(18, 10), default=1, nullable=False)
    allocation_method = db.Column(db.String(64), default="single_line", nullable=False, index=True)
    raw = db.Column(db.JSON, default=dict, nullable=False)


class AnalyticsPayment(db.Model):
    __tablename__ = "analytics_payments"

    id = db.Column(db.Integer, primary_key=True)
    source_file_id = db.Column(
        db.Integer,
        db.ForeignKey("analytics_source_files.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    con_document_id = db.Column(db.String(128), nullable=False, index=True)
    platezhka_paydate = db.Column(db.Date, nullable=True, index=True)
    platezhka_key = db.Column(db.String(128), nullable=True, index=True)
    platezhka_num = db.Column(db.String(128), nullable=True, index=True)
    platezhka_amount = db.Column(db.Numeric(20, 2), default=0, nullable=False)
    linked_to_budget_line = db.Column(db.Boolean, default=False, nullable=False, index=True)
    raw = db.Column(db.JSON, default=dict, nullable=False)


class AnalyticsImportIssue(db.Model):
    __tablename__ = "analytics_import_issues"

    id = db.Column(db.Integer, primary_key=True)
    source_file_id = db.Column(
        db.Integer,
        db.ForeignKey("analytics_source_files.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    severity = db.Column(db.String(16), nullable=False, index=True)
    code = db.Column(db.String(80), nullable=False, index=True)
    message = db.Column(db.Text, nullable=False)
    row_number = db.Column(db.Integer, nullable=True)
    raw = db.Column(db.JSON, default=dict, nullable=False)

