-- 13_device_latest.sql
\echo
\echo '######## Creating table: device_latest ########'
\echo

\connect app_db

SET ROLE app_owner;

-- ===========================
-- Table: device_latest
-- ===========================
CREATE TABLE IF NOT EXISTS db_schema.device_latest (
    device_id   BIGINT                  PRIMARY KEY REFERENCES db_schema.device(id) ON DELETE CASCADE,
    recorded_at     TIMESTAMPTZ         NOT NULL,
    x_coord         DOUBLE PRECISION    NOT NULL,
    y_coord         DOUBLE PRECISION    NOT NULL,
    meta            JSONB               NOT NULL DEFAULT '{}'::jsonb
);

-- index: find devices updated in the last N minutes
CREATE INDEX IF NOT EXISTS idx_device_latest_recorded_at
    ON db_schema.device_latest (recorded_at);

-- confirm
SELECT
    table_schema,
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema = 'db_schema'
  AND table_name   = 'device_latest';
