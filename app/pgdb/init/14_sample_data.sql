-- 13_sample_data.sql
\echo
\echo '######## Sample data (Dev) ########'
\echo

\connect app_db
SET ROLE app_owner;

-- ============================================================
-- Accounts (10 accounts, mixed types)
-- ============================================================
INSERT INTO db_schema.account (name, account_type, email, is_active)
VALUES
    -- Individuals
    ('Alice Chen',              'individual',  'alice.chen@example.com',           TRUE),
    ('Bob Smith',               'individual',  'bob.smith@example.com',            TRUE),
    ('Carla Robotics',          'individual',  'carla.robodev@example.com',        TRUE),
    ('David Fleet',             'individual',  'david.fleet@example.com',          TRUE),

    -- Organizations (SaaS customers)
    ('Acme Robotics Inc.',      'organization','contact@acme-robotics.example',    TRUE),
    ('Northwind Logistics Ltd', 'organization','ops@northwind-logistics.example',  TRUE),
    ('SkyTrack Drones Co.',     'organization','support@skytrack-drones.example',  TRUE),
    ('WarehouseIQ Systems',     'organization','admin@warehouseiq.example',        TRUE),
    ('Urban Sensors Lab',       'organization','info@urbansensors.example',        TRUE),
    ('FleetOps Analytics',      'organization','hello@fleetops-analytics.example', TRUE)
ON CONFLICT (email) DO NOTHING;

-- ============================================================
-- Users
-- ============================================================
INSERT INTO db_schema."user" (
    account_id,
    email,
    password_hash,
    role,
    is_active
)
VALUES
    -- Individual accounts
    (
        (SELECT id FROM db_schema.account WHERE email = 'alice.chen@example.com'),
        'alice.chen@example.com',
        'dev_hash_alice_owner',
        'owner',
        TRUE
    ),
    (
        (SELECT id FROM db_schema.account WHERE email = 'bob.smith@example.com'),
        'bob.smith@example.com',
        'dev_hash_bob_owner',
        'owner',
        TRUE
    ),
    (
        (SELECT id FROM db_schema.account WHERE email = 'carla.robodev@example.com'),
        'carla.robodev@example.com',
        'dev_hash_carla_owner',
        'owner',
        TRUE
    ),
    (
        (SELECT id FROM db_schema.account WHERE email = 'david.fleet@example.com'),
        'david.fleet@example.com',
        'dev_hash_david_owner',
        'owner',
        TRUE
    ),

    -- Acme Robotics Inc.
    (
        (SELECT id FROM db_schema.account WHERE email = 'contact@acme-robotics.example'),
        'owner@acme-robotics.example',
        'dev_hash_acme_owner',
        'owner',
        TRUE
    ),
    (
        (SELECT id FROM db_schema.account WHERE email = 'contact@acme-robotics.example'),
        'ops@acme-robotics.example',
        'dev_hash_acme_operator',
        'operator',
        TRUE
    ),

    -- Northwind Logistics Ltd
    (
        (SELECT id FROM db_schema.account WHERE email = 'ops@northwind-logistics.example'),
        'admin@northwind-logistics.example',
        'dev_hash_northwind_admin',
        'admin',
        TRUE
    ),
    (
        (SELECT id FROM db_schema.account WHERE email = 'ops@northwind-logistics.example'),
        'viewer@northwind-logistics.example',
        'dev_hash_northwind_viewer',
        'viewer',
        TRUE
    ),

    -- SkyTrack Drones Co.
    (
        (SELECT id FROM db_schema.account WHERE email = 'support@skytrack-drones.example'),
        'owner@skytrack-drones.example',
        'dev_hash_skytrack_owner',
        'owner',
        TRUE
    ),

    -- WarehouseIQ Systems
    (
        (SELECT id FROM db_schema.account WHERE email = 'admin@warehouseiq.example'),
        'admin@warehouseiq.example',
        'dev_hash_warehouse_admin',
        'admin',
        TRUE
    ),
    (
        (SELECT id FROM db_schema.account WHERE email = 'admin@warehouseiq.example'),
        'ops@warehouseiq.example',
        'dev_hash_warehouse_operator',
        'operator',
        TRUE
    ),

    -- Urban Sensors Lab
    (
        (SELECT id FROM db_schema.account WHERE email = 'info@urbansensors.example'),
        'owner@urbansensors.example',
        'dev_hash_urban_owner',
        'owner',
        TRUE
    ),

    -- FleetOps Analytics
    (
        (SELECT id FROM db_schema.account WHERE email = 'hello@fleetops-analytics.example'),
        'owner@fleetops-analytics.example',
        'dev_hash_fleetops_owner',
        'owner',
        TRUE
    )
ON CONFLICT (account_id, email) DO NOTHING;

-- ============================================================
-- Plans (starter / pro / business)
-- ============================================================
INSERT INTO db_schema.plan (
    code,
    name,
    max_devices,
    min_sample_interval_seconds,
    retention_days,
    monthly_price_usd
)
VALUES
    ('starter',   'Starter',   10,    60,  7,   9.00),    -- 60s interval
    ('pro',       'Pro',       500,   30,  30,  99.00),   -- 30s interval
    ('business',  'Business',  5000,  10,  90,  499.00)   -- 10s interval
ON CONFLICT (code) DO NOTHING;

-- ============================================================
-- Subscriptions
-- ============================================================
INSERT INTO db_schema.subscription (
    account_id,
    plan_code,
    started_at,
    auto_renew,
    created_at,
    updated_at
)
VALUES
    -- Starter
    (
        (SELECT id FROM db_schema.account WHERE email = 'alice.chen@example.com'),
        'starter', now(), TRUE, now(), now()
    ),
    (
        (SELECT id FROM db_schema.account WHERE email = 'bob.smith@example.com'),
        'starter', now(), TRUE, now(), now()
    ),
    (
        (SELECT id FROM db_schema.account WHERE email = 'carla.robodev@example.com'),
        'starter', now(), TRUE, now(), now()
    ),

    -- Pro
    (
        (SELECT id FROM db_schema.account WHERE email = 'contact@acme-robotics.example'),
        'pro', now(), TRUE, now(), now()
    ),
    (
        (SELECT id FROM db_schema.account WHERE email = 'ops@northwind-logistics.example'),
        'pro', now(), TRUE, now(), now()
    ),
    (
        (SELECT id FROM db_schema.account WHERE email = 'support@skytrack-drones.example'),
        'pro', now(), TRUE, now(), now()
    ),

    -- Business
    (
        (SELECT id FROM db_schema.account WHERE email = 'admin@warehouseiq.example'),
        'business', now(), TRUE, now(), now()
    ),
    (
        (SELECT id FROM db_schema.account WHERE email = 'info@urbansensors.example'),
        'business', now(), TRUE, now(), now()
    ),
    (
        (SELECT id FROM db_schema.account WHERE email = 'hello@fleetops-analytics.example'),
        'business', now(), TRUE, now(), now()
    ),
    (
        (SELECT id FROM db_schema.account WHERE email = 'david.fleet@example.com'),
        'business', now(), TRUE, now(), now()
    )
ON CONFLICT (account_id) DO NOTHING;

-- ============================================================
-- API keys
-- ============================================================
INSERT INTO db_schema.api_key (
    account_id,
    name,
    key_hash,
    created_at,
    is_active
)
VALUES
    -- Individuals
    (
        (SELECT id FROM db_schema.account WHERE email = 'alice.chen@example.com'),
        'alice-personal-key',
        'dev_hash_api_alice_personal',
        now(),
        TRUE
    ),
    (
        (SELECT id FROM db_schema.account WHERE email = 'bob.smith@example.com'),
        'bob-personal-key',
        'dev_hash_api_bob_personal',
        now(),
        TRUE
    ),
    (
        (SELECT id FROM db_schema.account WHERE email = 'carla.robodev@example.com'),
        'carla-dev-key',
        'dev_hash_api_carla_dev',
        now(),
        TRUE
    ),
    (
        (SELECT id FROM db_schema.account WHERE email = 'david.fleet@example.com'),
        'david-legacy-key',
        'dev_hash_api_david_legacy',
        now(),
        FALSE  -- inactive example
    ),

    -- Organizations
    (
        (SELECT id FROM db_schema.account WHERE email = 'contact@acme-robotics.example'),
        'device-ingest',
        'dev_hash_api_acme_ingest',
        now(),
        TRUE
    ),
    (
        (SELECT id FROM db_schema.account WHERE email = 'contact@acme-robotics.example'),
        'dashboard-readonly',
        'dev_hash_api_acme_dashboard',
        now(),
        TRUE
    ),
    (
        (SELECT id FROM db_schema.account WHERE email = 'ops@northwind-logistics.example'),
        'backend-service',
        'dev_hash_api_northwind_backend',
        now(),
        TRUE
    ),
    (
        (SELECT id FROM db_schema.account WHERE email = 'support@skytrack-drones.example'),
        'telemetry-pipeline',
        'dev_hash_api_skytrack_telemetry',
        now(),
        TRUE
    ),
    (
        (SELECT id FROM db_schema.account WHERE email = 'admin@warehouseiq.example'),
        'staging-integration',
        'dev_hash_api_warehouse_staging',
        now(),
        TRUE
    ),
    (
        (SELECT id FROM db_schema.account WHERE email = 'info@urbansensors.example'),
        'lab-experiments',
        'dev_hash_api_urban_lab',
        now(),
        TRUE
    ),
    (
        (SELECT id FROM db_schema.account WHERE email = 'hello@fleetops-analytics.example'),
        'analytics-service',
        'dev_hash_api_fleetops_analytics',
        now(),
        TRUE
    )
ON CONFLICT (account_id, name) DO UPDATE
SET
    key_hash   = EXCLUDED.key_hash,
    is_active  = EXCLUDED.is_active,
    created_at = LEAST(db_schema.api_key.created_at, EXCLUDED.created_at);

-- ============================================================
-- Devices: 5 per account = 50
-- ============================================================
WITH target_accounts AS (
    SELECT id, email
    FROM db_schema.account
    WHERE email IN (
        'alice.chen@example.com',
        'bob.smith@example.com',
        'carla.robodev@example.com',
        'david.fleet@example.com',
        'contact@acme-robotics.example',
        'ops@northwind-logistics.example',
        'support@skytrack-drones.example',
        'admin@warehouseiq.example',
        'info@urbansensors.example',
        'hello@fleetops-analytics.example'
    )
),
devices_per_account AS (
    SELECT
        a.id AS account_id,
        format('%s-dev-%02s', split_part(a.email, '@', 1), d.dev_seq) AS device_name,
        CASE (d.dev_seq % 3)
            WHEN 0 THEN 'sensor'
            WHEN 1 THEN 'robot'
            ELSE 'tracker'
        END AS device_type,
        format('model-%s', (d.dev_seq % 5)) AS model,
        format('v1.%s.%s', d.dev_seq % 3, d.dev_seq % 10) AS fw_version
    FROM target_accounts a
    CROSS JOIN generate_series(1, 5) AS d(dev_seq)   -- 5 devices per account
)
INSERT INTO db_schema.device (
    account_id,
    name,
    type,
    model,
    status,
    firmware_version,
    tags,
    last_seen_at,
    created_at,
    updated_at
)
SELECT
    account_id,
    device_name,
    device_type,
    model,
    'active'::db_schema.device_status,
    fw_version,
    jsonb_build_object('env', 'dev', 'sample_level', 'L1'),
    now(),
    now(),
    now()
FROM devices_per_account
ON CONFLICT (account_id, name) DO NOTHING;

-- ============================================================
-- Telemetry: 50 devices, 30s interval, 30 minutes
-- Time range: 2025-11-01
-- ============================================================
WITH devs AS (
    SELECT id
    FROM db_schema.device
    ORDER BY id
    LIMIT 50
),
time_points AS (
    SELECT
        generate_series(
            timestamp '2025-11-01 10:00:00',
            timestamp '2025-11-01 10:29:30',
            interval '30 seconds'
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
    d.id AS device_id,
    t.ts AS recorded_at,
    (random() * 1000)::double precision AS x_coord,
    (random() * 1000)::double precision AS y_coord,
    jsonb_build_object(
        'battery', (80 + random() * 20)::int,
        'temp',    (20 + random() * 10)::int,
        'source',  'dev-seed'
    ) AS meta
FROM devs d
CROSS JOIN time_points t;

-- ============================================================
-- Confirm: counts for key tables
-- ============================================================
SELECT
    (SELECT count(*) FROM db_schema.account)           AS account_count,
    (SELECT count(*) FROM db_schema."user")           AS user_count,
    (SELECT count(*) FROM db_schema.plan)             AS plan_count,
    (SELECT count(*) FROM db_schema.subscription)     AS subscription_count,
    (SELECT count(*) FROM db_schema.api_key)          AS api_key_count,
    (SELECT count(*) FROM db_schema.device)           AS device_count,
    (SELECT count(*) FROM db_schema.device_telemetry) AS device_telemetry_count;
