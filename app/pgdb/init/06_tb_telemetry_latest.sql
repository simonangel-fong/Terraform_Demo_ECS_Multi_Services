-- 06_tb_telemetry_latest.sql
\echo
\echo '######## Creating table: telemetry_latest ########'
\echo

\connect app_db

SET ROLE app_owner;

-- ===========================
-- Table: telemetry_latest
-- Latest valid position per device, for fast lookup
-- ===========================
CREATE TABLE IF NOT EXISTS db_schema.telemetry_latest  (
    device_uuid       UUID                PRIMARY KEY REFERENCES db_schema.device_registry(device_uuid) ON DELETE CASCADE,
    alias             VARCHAR(64),        -- for debug
    x_coord           DOUBLE PRECISION    NOT NULL,
    y_coord           DOUBLE PRECISION    NOT NULL,
    device_time       TIMESTAMPTZ         NOT NULL,
    system_time_utc   TIMESTAMPTZ         NOT NULL DEFAULT now()
);

-- Index: find devices updated in the last N minutes
CREATE INDEX IF NOT EXISTS idx_telemetry_latest_system_time_utc
    ON db_schema.telemetry_latest (system_time_utc);


-- ==========================================
-- Function: fn_upsert_telemetry_latest
-- On each new telemetry_event, update the latest snapshot.
-- ==========================================
CREATE OR REPLACE FUNCTION db_schema.fn_upsert_telemetry_latest()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO db_schema.telemetry_latest (
        device_uuid,
        alias,
        x_coord,
        y_coord,
        device_time,
        system_time_utc
    )
    SELECT
        NEW.device_uuid,
        dr.alias,
        NEW.x_coord,
        NEW.y_coord,
        NEW.device_time,
        NEW.system_time_utc
    FROM db_schema.device_registry AS dr
    WHERE dr.device_uuid = NEW.device_uuid
    ON CONFLICT (device_uuid) DO UPDATE
    SET
        alias       = EXCLUDED.alias,
        x_coord     = EXCLUDED.x_coord,
        y_coord     = EXCLUDED.y_coord,
        device_time = EXCLUDED.device_time,
        system_time_utc = EXCLUDED.system_time_utc
    WHERE db_schema.telemetry_latest.system_time_utc < EXCLUDED.system_time_utc;

    RETURN NEW;
END;
$$;

-- ==========================================
-- Trigger: after insert on telemetry_event
-- ==========================================
CREATE TRIGGER trg_telemetry_event_upsert_latest
AFTER INSERT ON db_schema.telemetry_event
FOR EACH ROW
EXECUTE FUNCTION db_schema.fn_upsert_telemetry_latest();


-- Confirm
SELECT
    table_schema,
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema = 'db_schema'
  AND table_name   = 'telemetry_latest';

SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'db_schema'
  AND tablename  = 'telemetry_latest'
ORDER BY indexname;