-- 10_tb_api_key.sql
\echo
\echo '######## Creating table: api_key ########'
\echo

\connect app_db

SET ROLE app_owner;

-- ===========================
-- Table: api_key
-- ===========================
CREATE TABLE IF NOT EXISTS db_schema.api_key (
    id              BIGSERIAL       PRIMARY KEY,
    account_id      BIGINT          NOT NULL REFERENCES db_schema.account(id) ON DELETE CASCADE,
    name            TEXT            NOT NULL,
    key_hash        TEXT            NOT NULL,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT now(),
    last_used_at    TIMESTAMPTZ,
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,

    -- unique name per account
    CONSTRAINT uq_api_key_name_per_account UNIQUE (account_id, name),

    -- unique hash
    CONSTRAINT uq_api_key_hash UNIQUE (key_hash)
);

-- index: account_id
CREATE INDEX IF NOT EXISTS idx_api_key_account_id
    ON db_schema.api_key(account_id);
