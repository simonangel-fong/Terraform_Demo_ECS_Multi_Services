-- 07_tb_user.sql
\echo
\echo '######## Creating table: user ########'
\echo

\connect app_db

SET ROLE app_owner;

-- ===========================
-- Table: "user"
-- ===========================
CREATE TABLE IF NOT EXISTS db_schema."user" (
    id              BIGSERIAL               PRIMARY KEY,
    account_id      BIGINT                  NOT NULL REFERENCES db_schema.account(id) ON DELETE CASCADE,
    email           citext                  NOT NULL,
    password_hash   TEXT                    NOT NULL,  -- store hash, not plain pwd
    role            db_schema.user_role     NOT NULL DEFAULT 'viewer',
    is_active       BOOLEAN                 NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ             NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ             NOT NULL DEFAULT now(),

    CONSTRAINT uq_user_email_per_account UNIQUE (account_id, email)
);

-- index: account_id
CREATE INDEX IF NOT EXISTS idx_user_account_id
    ON db_schema."user"(account_id);

-- trigger: set updated_at
-- DROP TRIGGER IF EXISTS trg_user_set_updated_at ON db_schema."user";
CREATE TRIGGER trg_user_set_updated_at
BEFORE UPDATE ON db_schema."user"
FOR EACH ROW
EXECUTE FUNCTION db_schema.set_updated_at();