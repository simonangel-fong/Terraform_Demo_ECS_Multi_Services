-- 06_tb_account.sql
\echo
\echo '######## Creating table: account ########'
\echo

\connect app_db

SET ROLE app_owner;

-- ===========================
-- Table: account
-- ===========================
CREATE TABLE IF NOT EXISTS db_schema.account (
    id              BIGSERIAL                   PRIMARY KEY,
    name            TEXT                        NOT NULL,       
    account_type    db_schema.account_type      NOT NULL,
    email           citext                      NOT NULL,    
    is_active       BOOLEAN                     NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ                 NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ                 NOT NULL DEFAULT now(),

    CONSTRAINT uq_account_email UNIQUE (email)
);

CREATE INDEX IF NOT EXISTS idx_account_type
    ON db_schema.account (account_type);

-- trigger: set updated_at
-- DROP TRIGGER IF EXISTS trg_account_set_updated_at ON db_schema.account;
CREATE TRIGGER trg_account_set_updated_at
BEFORE UPDATE ON db_schema.account
FOR EACH ROW
EXECUTE FUNCTION db_schema.set_updated_at();

-- confirm
SELECT 
    table_schema,
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema = 'db_schema'
  AND table_name   = 'account';

SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'db_schema'
  AND tablename  = 'account'
ORDER BY indexname;
