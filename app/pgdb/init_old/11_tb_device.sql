-- 11_tb_device.sql
\echo
\echo '######## Creating table: device ########'
\echo

\connect app_db
SET ROLE app_owner;

-- ===========================
-- Table: device
-- ===========================
CREATE TABLE IF NOT EXISTS db_schema.device (
    id                  BIGSERIAL                   PRIMARY KEY,
    account_id          BIGINT                      NOT NULL REFERENCES db_schema.account(id) ON DELETE CASCADE,
    name                VARCHAR(255)                NOT NULL,
    type                VARCHAR(100)                NOT NULL,
    model               VARCHAR(100),
    status              db_schema.device_status     NOT NULL DEFAULT 'provisioned',
    firmware_version    TEXT,
    tags                JSONB,
    last_seen_at        TIMESTAMPTZ,
    created_at          TIMESTAMPTZ                 NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ                 NOT NULL DEFAULT now(),

    -- unique device name per account
    CONSTRAINT uq_device_name_per_account UNIQUE (account_id, name)
);

-- Index: account_id, type, name
CREATE INDEX IF NOT EXISTS idx_device_account_type_name
    ON db_schema.device (account_id, type, name);

-- Index: account_id, status
CREATE INDEX IF NOT EXISTS idx_device_account_status
    ON db_schema.device (account_id, status);

CREATE INDEX IF NOT EXISTS idx_device_account_status_active
    ON db_schema.device (account_id, type, name)
    WHERE status = 'active';

-- trigger: set updated_at
-- DROP TRIGGER IF EXISTS trg_device_set_updated_at ON db_schema.device;
CREATE TRIGGER trg_device_set_updated_at
BEFORE UPDATE ON db_schema.device
FOR EACH ROW
EXECUTE FUNCTION db_schema.set_updated_at();
