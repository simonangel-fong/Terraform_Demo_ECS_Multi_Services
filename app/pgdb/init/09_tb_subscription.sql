-- 09_tb_subscription.sql
\echo
\echo '######## Creating table: subscription ########'
\echo

\connect app_db
SET ROLE app_owner;

-- ===========================
-- Table: subscription
-- ===========================
CREATE TABLE IF NOT EXISTS db_schema.subscription (
    id              BIGSERIAL               PRIMARY KEY,
    account_id      BIGINT                  NOT NULL UNIQUE REFERENCES db_schema.account(id) ON DELETE CASCADE,
    plan_code       db_schema.plan_code     NOT NULL REFERENCES db_schema.plan(code),
    started_at      TIMESTAMPTZ             NOT NULL DEFAULT now(),
    canceled_at     TIMESTAMPTZ,
    auto_renew      BOOLEAN                 NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ             NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ             NOT NULL DEFAULT now(),
    
    CHECK (canceled_at IS NULL OR canceled_at >= started_at)
);

-- index: plan_code
CREATE INDEX IF NOT EXISTS idx_subscription_plan_code
    ON db_schema.subscription(plan_code);

-- trigger: set_updated_at
-- DROP TRIGGER IF EXISTS trg_subscription_set_updated_at ON db_schema.subscription;
CREATE TRIGGER trg_subscription_set_updated_at
BEFORE UPDATE ON db_schema.subscription
FOR EACH ROW
EXECUTE FUNCTION db_schema.set_updated_at();
