-- prod_init.sql
\echo
\echo '######## Prod init: tuning autovacuum on hot tables ########'
\echo

\connect app_db

SET ROLE app_owner;

-- device: moderate write volume
ALTER TABLE db_schema.device
    SET (
        autovacuum_vacuum_scale_factor  = 0.05,
        autovacuum_analyze_scale_factor = 0.05
    );

-- device_telemetry: write-heavy
ALTER TABLE db_schema.device_telemetry
    SET (
        autovacuum_vacuum_scale_factor  = 0.02,
        autovacuum_analyze_scale_factor = 0.02
    );
