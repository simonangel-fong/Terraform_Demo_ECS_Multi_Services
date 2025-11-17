-- 05_tb_telemetry.sql
\echo
\echo '######## Creating table: device_telemetry ########'
\echo

\connect app_db
SET ROLE app_owner;

-- ===========================
-- Table: device_telemetry
-- ===========================
CREATE TABLE IF NOT EXISTS db_schema.device_telemetry (
    id              BIGSERIAL               NOT NULL,
    device_id       BIGINT                  NOT NULL REFERENCES db_schema.device(id) ON DELETE CASCADE,
    x_coord         DOUBLE PRECISION        NOT NULL,
    y_coord         DOUBLE PRECISION        NOT NULL,
    recorded_at     TIMESTAMPTZ             NOT NULL,
    device_time     TIMESTAMPTZ,
    
    -- Composite primary key
    PRIMARY KEY (id, recorded_at)
)
PARTITION BY RANGE (recorded_at);

-- Index: last location query
CREATE INDEX IF NOT EXISTS idx_device_telemetry_device_time
    ON db_schema.device_telemetry (device_id, recorded_at DESC);

-- Index: Time-range queries across devices
CREATE INDEX IF NOT EXISTS idx_device_telemetry_time_device
    ON db_schema.device_telemetry (recorded_at, device_id);

-- partition
CREATE TABLE IF NOT EXISTS db_schema.device_telemetry_2025_11
    PARTITION OF db_schema.device_telemetry
    FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');

CREATE TABLE IF NOT EXISTS db_schema.device_telemetry_2025_12
    PARTITION OF db_schema.device_telemetry
    FOR VALUES FROM ('2025-12-01') TO ('2026-01-01');

CREATE TABLE IF NOT EXISTS db_schema.device_telemetry_2026_01
    PARTITION OF db_schema.device_telemetry
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

CREATE TABLE IF NOT EXISTS db_schema.device_telemetry_2026_02
    PARTITION OF db_schema.device_telemetry
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

-- confirm
SELECT
    table_schema,
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema = 'db_schema'
  AND table_name   = 'device_telemetry';

SELECT
    inhrelid::regclass  AS partition_name,
    inhparent::regclass AS parent_name
FROM pg_inherits
WHERE inhparent = 'db_schema.device_telemetry'::regclass
ORDER BY partition_name;