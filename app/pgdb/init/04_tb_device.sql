-- 04_tb_device.sql
\echo
\echo '######## Creating table: device (telemetry) ########'
\echo

\connect app_db
SET ROLE app_owner;

-- ===========================
-- Table: device
-- ===========================
CREATE TABLE IF NOT EXISTS db_schema.device (
    
    id                  BIGSERIAL       PRIMARY KEY,        -- surrogate key
    name                varchar(64)     NOT NULL,
    device_uuid         UUID            NOT NULL,
    api_key_hash        CHAR(64)        NOT NULL,           -- Hashed API key
    tracking_enabled    BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT now(),

    -- Each device_uuid must be unique
    CONSTRAINT uq_device_uuid UNIQUE (device_uuid)
);

-- Index: enabled devices
CREATE INDEX IF NOT EXISTS idx_device_tracking_enabled
    ON db_schema.device (tracking_enabled)
    WHERE tracking_enabled = TRUE;


-- Trigger: maintain updated_at on change
-- DROP TRIGGER IF EXISTS trg_device_set_updated_at ON db_schema.device;
CREATE TRIGGER trg_device_set_updated_at
BEFORE UPDATE ON db_schema.device
FOR EACH ROW
EXECUTE FUNCTION db_schema.set_updated_at();
