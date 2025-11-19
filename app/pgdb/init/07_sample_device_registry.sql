-- 07_sample_device_registry.sql
\echo
\echo '######## Sample data: device_registry ########'
\echo

\connect app_db
SET ROLE app_owner;

INSERT INTO db_schema.device_registry (alias, device_uuid, api_key_hash)
VALUES
    ('device-001', 'e003031d-e441-4ece-ba5b-7d54d5b1da21', 'sample-hash-device-001'),
    ('device-002', 'd6a07ca5-0ce9-41c3-8dc8-eec41b47b47b', 'sample-hash-device-002'),
    ('device-003', 'aa1b41a2-c8f6-44c7-9644-4e9b719a66e9', 'sample-hash-device-003'),
    ('device-004', '637c72d6-8ed3-4bf1-b23a-8ec84204846f', 'sample-hash-device-004'),
    ('device-005', '199a53cd-1d9c-4b43-8e46-5f1e1e10c4f8', 'sample-hash-device-005'),
    ('device-006', '1992af01-6789-4072-a516-eb251fa66bd3', 'sample-hash-device-006'),
    ('device-007', '9ee2c87c-d990-44cc-a51f-fe3414daddd6', 'sample-hash-device-007'),
    ('device-008', '4b02cbb7-53ea-4dff-8d5d-b93db0dcb5c1', 'sample-hash-device-008'),
    ('device-009', '8ce6142d-28d5-4dcf-82a9-ef9326c93f03', 'sample-hash-device-009'),
    ('device-010', '03618450-a5c7-4bb4-a437-21e978a41c5e', 'sample-hash-device-010');

-- Confirm
SELECT *
FROM db_schema.device_registry
ORDER BY id
LIMIT 10;


