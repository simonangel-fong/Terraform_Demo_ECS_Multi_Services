\echo '\n######## Inserting sample data... ########\n'

\c app_db;

SET ROLE app_user;

-- =========================================
-- 10 sample devices
-- =========================================
INSERT INTO db_schema.device (id, name, type)
VALUES
    (1,  'device-001', 'sensor'),
    (2,  'device-002', 'sensor'),
    (3,  'device-003', 'sensor'),
    (4,  'device-004', 'camera'),
    (5,  'device-005', 'camera'),
    (6,  'device-006', 'camera'),
    (7,  'device-007', 'gateway'),
    (8,  'device-008', 'gateway'),
    (9,  'device-009', 'gateway'),
    (10, 'device-010', 'sensor')
ON CONFLICT (id) DO NOTHING;


-- =========================================
-- Insert continuous random positions
-- =========================================
DO $$
DECLARE
    d_id      BIGINT;
    i         INT;
    t         TIMESTAMPTZ;
    x_val     DOUBLE PRECISION;
    y_val     DOUBLE PRECISION;
    start_ts  TIMESTAMPTZ := now() - interval '60 seconds';
BEGIN
    FOR d_id IN 1..10 LOOP
        -- random starting point within [0,10]
        x_val := random() * 10.0;
        y_val := random() * 10.0;
        t := start_ts;

        FOR i IN 1..60 LOOP
            INSERT INTO db_schema.device_position (device_id, ts, x, y)
            VALUES (d_id, t, x_val, y_val);

            -- next timestamp (1 second later)
            t := t + interval '1 second';

            -- small random movement, clamped to [0,10]
            x_val := GREATEST(0.0, LEAST(10.0, x_val + (random() - 0.5)));
            y_val := GREATEST(0.0, LEAST(10.0, y_val + (random() - 0.5)));
        END LOOP;
    END LOOP;
END;
$$;

RESET ROLE;

-- confirm
SELECT *
FROM db_schema.device;

SELECT *
FROM db_schema.device_position
WHERE ts >= now() - interval '5 seconds'
ORDER BY ts DESC;