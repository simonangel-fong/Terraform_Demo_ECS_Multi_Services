-- 08_tb_plan.sql
\echo
\echo '######## Creating table: plan ########'
\echo

\connect app_db

SET ROLE app_owner;

-- ===========================
-- Table: plan
-- ===========================
CREATE TABLE IF NOT EXISTS db_schema.plan (
    code                            db_schema.plan_code     PRIMARY KEY,
    name                            TEXT                    NOT NULL,
    max_devices                     INTEGER                 NOT NULL CHECK (max_devices > 0),
    min_sample_interval_seconds     INTEGER                 NOT NULL CHECK (min_sample_interval_seconds > 0),
    retention_days                  INTEGER                 NOT NULL CHECK (retention_days >= 0),
    monthly_price_usd               NUMERIC(10,2)           NOT NULL CHECK (monthly_price_usd >= 0)
);
