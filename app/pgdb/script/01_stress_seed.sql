-- 01_sample_data.sql
\echo
\echo '######## Add sample data ########'
\echo

\connect app_db

SET ROLE app_owner;

-- accounts
INSERT INTO db_schema.account (name, account_type, email, is_active)
SELECT
    format('Stress Org %s', g)                        AS name,
    'organization'::db_schema.account_type            AS account_type,
    format('stress-org-%s@example.com', g)            AS email,
    TRUE                                              AS is_active
FROM generate_series(1, 1000) AS g
ON CONFLICT (email) DO NOTHING;

-- devices - 50 devices per stress org
INSERT INTO db_schema.device (
    account_id,
    name,
    type,
    model,
    status,
    firmware_version,
    tags,
    created_at,
    updated_at
)
SELECT
    a.id                                         AS account_id,
    format('device-%04s', d.device_seq)          AS name,
    CASE (d.device_seq % 3)
        WHEN 0 THEN 'sensor'
        WHEN 1 THEN 'robot'
        ELSE 'tracker'
    END                                          AS type,
    format('model-%s', (d.device_seq % 10))      AS model,
    'active'::db_schema.device_status            AS status,
    format('v1.%s.%s', d.device_seq % 3, d.device_seq % 10) AS firmware_version,
    jsonb_build_object('env', 'stress')          AS tags,
    now()                                        AS created_at,
    now()                                        AS updated_at
FROM db_schema.account a
JOIN LATERAL generate_series(1, 50) AS d(device_seq) ON TRUE
WHERE a.email LIKE 'stress-org-%@example.com'
ON CONFLICT (account_id, name) DO NOTHING;

-- telemetry
-- First 1000 stress devices
-- 1 day at 1 sample / 10 seconds => ~8.64M rows
WITH target_devices AS (
    SELECT id
    FROM db_schema.device
    WHERE tags ->> 'env' = 'stress'
    ORDER BY id
    LIMIT 1000
),
time_points AS (
    SELECT
        generate_series(
            timestamp '2025-11-01 00:00:00',
            timestamp '2026-02-01 23:59:50',
            interval '10 seconds'
        ) AS ts
)
INSERT INTO db_schema.device_telemetry (
    device_id,
    recorded_at,
    x_coord,
    y_coord,
    meta
)
SELECT
    d.id       AS device_id,
    t.ts       AS recorded_at,
    (random() * 1000)::double precision   AS x_coord,
    (random() * 1000)::double precision   AS y_coord,
    jsonb_build_object(
        'battery', (80 + random() * 20)::int,
        'temp',    (20 + random() * 10)::int
    ) AS meta
FROM target_devices d
CROSS JOIN time_points t;

-- Confirm
SELECT
    (SELECT count(*) FROM db_schema.account   WHERE email LIKE 'stress-org-%@example.com') AS stress_accounts,
    (SELECT count(*) FROM db_schema.device    WHERE tags ->> 'env' = 'stress')             AS stress_devices,
    (SELECT count(*) FROM db_schema.device_telemetry)                                      AS telemetry_rows;
