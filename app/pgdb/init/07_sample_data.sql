-- 07_sample_data.sql
\echo
\echo '######## Sample data (telemetry service - Dev) ########'
\echo

\connect app_db
SET ROLE app_owner;

-- ============================================================
-- Devices for telemetry service (DEV)
--
-- Plaintext API keys (for your test clients / k6 / FastAPI):
--   dev-alpha   -> dev-device-001-key
--   dev-bravo   -> dev-device-002-key
--   dev-charlie -> dev-device-003-key (tracking disabled)
--
-- SHA-256 hashes (hex) of those keys (example values):
--   dev-device-001-key -> 826d07e3815eba4f09dd0388fff5fdce270c3d39c436b34f874d3c463ce21f42
--   dev-device-002-key -> aa2200f2caeb4c7eb11486531f9bb065a6e48f7a64ac3b5cb53a52a058b1bfde
--   dev-device-003-key -> fcc47efd7b6121e9cc8b8c7e7daadb335e88d2116df09a1c189a016b6a11213e
-- ============================================================

INSERT INTO db_schema.device (
    name,
    device_uuid,
    api_key_hash,
    tracking_enabled,
    created_at,
    updated_at
)
VALUES
    (
        'dev-alpha',
        'a5124a19-2725-4e07-9fdf-cb54a451204a',
        '826d07e3815eba4f09dd0388fff5fdce270c3d39c436b34f874d3c463ce21f42',
        TRUE,
        now(),
        now()
    ),
    (
        'dev-bravo',
        '35dec641-554b-446f-9092-6652cb6fe3c0',
        'aa2200f2caeb4c7eb11486531f9bb065a6e48f7a64ac3b5cb53a52a058b1bfde',
        TRUE,
        now(),
        now()
    ),
    (
        'dev-charlie',
        'd5a7fe62-28fb-49d9-906b-abed453d1cd4',
        'fcc47efd7b6121e9cc8b8c7e7daadb335e88d2116df09a1c189a016b6a11213e',
        FALSE,  -- tracking disabled: good for testing privacy gate
        now(),
        now()
    )
ON CONFLICT (device_uuid) DO UPDATE
SET
    name             = EXCLUDED.name,
    api_key_hash     = EXCLUDED.api_key_hash,
    tracking_enabled = EXCLUDED.tracking_enabled,
    updated_at       = now();

-- ============================================================
-- Clean existing telemetry & latest rows for these devices
-- so the script is roughly idempotent for dev
-- ============================================================

DELETE FROM db_schema.device_latest dl
USING db_schema.device d
WHERE dl.device_id = d.id
  AND d.name IN ('dev-alpha', 'dev-bravo', 'dev-charlie');

DELETE FROM db_schema.telemetry t
USING db_schema.device d
WHERE t.device_id = d.id
  AND d.name IN ('dev-alpha', 'dev-bravo', 'dev-charlie');

-- ============================================================
-- Telemetry: few rows for dev-alpha & dev-bravo (relative to NOW)
-- ============================================================

WITH dev_ids AS (
    SELECT id, name
    FROM db_schema.device
    WHERE name IN ('dev-alpha', 'dev-bravo')
),
alpha AS (
    SELECT id AS device_id
    FROM dev_ids
    WHERE name = 'dev-alpha'
),
bravo AS (
    SELECT id AS device_id
    FROM dev_ids
    WHERE name = 'dev-bravo'
),
base AS (
    -- Use current time in UTC as base; stable within this statement
    SELECT now() AS base_ts
)
INSERT INTO db_schema.telemetry (
    device_id,
    x_coord,
    y_coord,
    recorded_at,
    device_time
)
-- dev-alpha: 3 points in the last ~5 minutes
SELECT
    a.device_id,
    100.0 + EXTRACT(EPOCH FROM (b.base_ts - del.delta)) * 0.001 AS x_coord,
    200.0 + EXTRACT(EPOCH FROM (b.base_ts - del.delta)) * 0.001 AS y_coord,
    b.base_ts - del.delta                           AS recorded_at,
    b.base_ts - del.delta - interval '10 seconds'   AS device_time
FROM alpha a
CROSS JOIN base b
CROSS JOIN (
    VALUES
        (interval '5 minutes'),
        (interval '3 minutes'),
        (interval '1 minute')
) AS del(delta)

UNION ALL

-- dev-bravo: 3 points in the last ~6 minutes
SELECT
    br.device_id,
    300.0 + EXTRACT(EPOCH FROM (b.base_ts - del.delta)) * 0.001 AS x_coord,
    400.0 + EXTRACT(EPOCH FROM (b.base_ts - del.delta)) * 0.001 AS y_coord,
    b.base_ts - del.delta                           AS recorded_at,
    b.base_ts - del.delta - interval '5 seconds'    AS device_time
FROM bravo br
CROSS JOIN base b
CROSS JOIN (
    VALUES
        (interval '6 minutes'),
        (interval '4 minutes'),
        (interval '2 minutes')
) AS del(delta);

-- ============================================================
-- device_latest: derive latest per device from telemetry
-- ============================================================

INSERT INTO db_schema.device_latest (
    device_id,
    recorded_at,
    device_time,
    x_coord,
    y_coord
)
SELECT DISTINCT ON (t.device_id)
    t.device_id,
    t.recorded_at,
    t.device_time,
    t.x_coord,
    t.y_coord
FROM db_schema.telemetry t
JOIN db_schema.device d
  ON d.id = t.device_id
WHERE d.name IN ('dev-alpha', 'dev-bravo')
ORDER BY t.device_id, t.recorded_at DESC;

-- ============================================================
-- Confirm
-- ============================================================

\echo '--------- Dev sample telemetry summary ---------'

SELECT
    (SELECT count(*) FROM db_schema.device)            AS total_devices,
    (SELECT count(*) FROM db_schema.telemetry)  AS total_telemetry_rows,
    (SELECT count(*) FROM db_schema.device_latest)     AS total_device_latest_rows;

SELECT
    d.name,
    d.device_uuid,
    d.tracking_enabled,
    dl.recorded_at AS latest_recorded_at,
    dl.device_time AS latest_device_time,
    dl.x_coord,
    dl.y_coord
FROM db_schema.device d
LEFT JOIN db_schema.device_latest dl
  ON dl.device_id = d.id
WHERE d.name IN ('dev-alpha', 'dev-bravo', 'dev-charlie')
ORDER BY d.name;
