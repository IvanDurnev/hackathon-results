BEGIN;

CREATE TABLE IF NOT EXISTS dim_budget (
    budget_id SERIAL PRIMARY KEY,
    budget_name VARCHAR(255) UNIQUE NOT NULL,
    budget_level VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dim_organization (
    org_id SERIAL PRIMARY KEY,
    org_name VARCHAR(500) UNIQUE NOT NULL,
    org_type VARCHAR(50) DEFAULT 'recipient',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dim_classification (
    class_id SERIAL PRIMARY KEY,
    kfsr_code VARCHAR(20),
    kcsr_code VARCHAR(50) NOT NULL,
    kvr_code VARCHAR(20),
    kosgu_code VARCHAR(10),
    kvsr_code VARCHAR(20),
    purpose_code VARCHAR(50),
    kvfo_code VARCHAR(10),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(kcsr_code, kvr_code, kosgu_code, purpose_code)
);

CREATE TABLE IF NOT EXISTS dim_document (
    document_id VARCHAR(100) PRIMARY KEY,
    document_class VARCHAR(50),
    reg_number VARCHAR(100),
    close_date DATE,
    main_document_id VARCHAR(100),
    budget_id INT REFERENCES dim_budget(budget_id),
    org_id INT REFERENCES dim_organization(org_id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fact_planning (
    id BIGSERIAL PRIMARY KEY,
    posting_date DATE NOT NULL,
    budget_id INT REFERENCES dim_budget(budget_id),
    org_id INT REFERENCES dim_organization(org_id),
    class_id INT REFERENCES dim_classification(class_id),
    source_funds VARCHAR(100),
    limits_pbs DECIMAL(18,2),
    limits_confirmed_bo DECIMAL(18,2),
    limits_confirmed_no_bo DECIMAL(18,2),
    limits_remainder DECIMAL(18,2),
    total_withdrawals DECIMAL(18,2),
    snapshot_period VARCHAR(7) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(budget_id, org_id, class_id, posting_date, snapshot_period)
);

CREATE TABLE IF NOT EXISTS fact_execution (
    id BIGSERIAL PRIMARY KEY,
    posting_date DATE NOT NULL,
    budget_id INT REFERENCES dim_budget(budget_id),
    org_id INT REFERENCES dim_organization(org_id),
    class_id INT REFERENCES dim_classification(class_id),
    subsidy_code VARCHAR(50),
    industry_code VARCHAR(50),
    kvfo_code VARCHAR(10),
    payments_total DECIMAL(18,2),
    payments_execution DECIMAL(18,2),
    payments_recovery DECIMAL(18,2),
    snapshot_period VARCHAR(7) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(budget_id, org_id, class_id, posting_date, snapshot_period)
);

CREATE TABLE IF NOT EXISTS fact_agreements (
    id BIGSERIAL PRIMARY KEY,
    document_id VARCHAR(100) REFERENCES dim_document(document_id),
    class_id INT REFERENCES dim_classification(class_id),
    recipient_org_id INT REFERENCES dim_organization(org_id),
    amount_current_year DECIMAL(18,2),
    estimate_caption TEXT,
    kadmr_code VARCHAR(20),
    kfsr_code VARCHAR(20),
    kcsr_code VARCHAR(50),
    kvr_code VARCHAR(20),
    purpose_code VARCHAR(50),
    kesr_code VARCHAR(10),
    snapshot_period VARCHAR(7) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(document_id, snapshot_period)
);

CREATE TABLE IF NOT EXISTS fact_procurement (
    id BIGSERIAL PRIMARY KEY,
    con_document_id VARCHAR(100) NOT NULL,
    con_number VARCHAR(100),
    con_date DATE,
    con_amount DECIMAL(18,2),
    zakazchik_key VARCHAR(50),
    payment_date DATE,
    payment_key VARCHAR(100),
    payment_number VARCHAR(100),
    payment_amount DECIMAL(18,2),
    kfsr_code VARCHAR(20),
    kcsr_code VARCHAR(50),
    kvr_code VARCHAR(20),
    kesr_code VARCHAR(10),
    kvsr_code VARCHAR(20),
    purposefulgrant VARCHAR(50),
    snapshot_period VARCHAR(7) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(con_document_id, payment_key, snapshot_period)
);

-- Индексы
CREATE INDEX IF NOT EXISTS idx_fact_planning_date ON fact_planning(posting_date);
CREATE INDEX IF NOT EXISTS idx_fact_planning_org ON fact_planning(org_id);
CREATE INDEX IF NOT EXISTS idx_fact_planning_class ON fact_planning(class_id);
CREATE INDEX IF NOT EXISTS idx_fact_planning_snapshot ON fact_planning(snapshot_period);

CREATE INDEX IF NOT EXISTS idx_fact_execution_date ON fact_execution(posting_date);
CREATE INDEX IF NOT EXISTS idx_fact_execution_org ON fact_execution(org_id);
CREATE INDEX IF NOT EXISTS idx_fact_execution_class ON fact_execution(class_id);

CREATE INDEX IF NOT EXISTS idx_fact_procurement_con ON fact_procurement(con_document_id);
CREATE INDEX IF NOT EXISTS idx_fact_procurement_date ON fact_procurement(payment_date);

COMMIT;