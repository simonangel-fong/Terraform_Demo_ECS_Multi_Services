\echo '\n######## Creating tables... ########\n'

\c app_db;

SET ROLE app_user;

-- ==============================
-- Table: device
-- ==============================
CREATE TABLE IF NOT EXISTS db_schema.device (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255)    NOT NULL,
    type            VARCHAR(100)    NOT NULL,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- index: device.type
CREATE INDEX IF NOT EXISTS idx_device_type
    ON db_schema.device (type);

-- ==============================
-- Table: device_position
-- ==============================
CREATE TABLE IF NOT EXISTS db_schema.device_position (
    device_id       UUID            NOT NULL,
    ts              TIMESTAMPTZ     NOT NULL DEFAULT now(),
    x               NUMERIC(4,2)    NOT NULL,
    y               NUMERIC(4,2)    NOT NULL,

    CONSTRAINT pk_device_position PRIMARY KEY (device_id, ts),

    CONSTRAINT chk_xy_range
        CHECK (x >= 0 AND x <= 10 AND y >= 0 AND y <= 10),

    CONSTRAINT fk_device_position_device
        FOREIGN KEY (device_id)
        REFERENCES db_schema.device (id)
        ON DELETE CASCADE
);

-- index: device_id query
CREATE INDEX IF NOT EXISTS idx_device_position_device_id
    ON db_schema.device_position (device_id);

-- index: time query
CREATE INDEX IF NOT EXISTS idx_device_position_ts
    ON db_schema.device_position (ts DESC);

RESET ROLE;

-- Confirm
SELECT 
    schemaname,
    tablename,
    tablespace
FROM pg_tables 
WHERE schemaname = 'db_schema'
ORDER BY tablename;
