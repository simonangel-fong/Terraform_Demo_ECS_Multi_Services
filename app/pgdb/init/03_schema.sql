-- 03_schema.sql
\echo
\echo '######## Creating schema and setting privileges ########'
\echo

\connect app_db

-- create shcema: app_db owned by app_owner
CREATE SCHEMA IF NOT EXISTS db_schema AUTHORIZATION app_owner;

-- --- GLOBAL PERMISSIONS ---

-- access
GRANT CONNECT ON DATABASE app_db TO app_user, app_readonly;
-- public
REVOKE CONNECT ON DATABASE app_db FROM PUBLIC;

-- schema privilege:
GRANT USAGE ON SCHEMA db_schema TO app_user, app_readonly;
-- public
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO app_user, app_readonly;

-- --- EXISTING OBJECTS PRIVILEGES ---
-- app_user
GRANT SELECT, INSERT, UPDATE, DELETE 
ON ALL TABLES IN SCHEMA db_schema 
TO app_user;

-- app_readonly
GRANT SELECT 
ON ALL TABLES IN SCHEMA db_schema 
TO app_readonly;

-- app_user, app_readonly
GRANT USAGE, SELECT 
ON ALL SEQUENCES IN SCHEMA db_schema 
TO app_user, app_readonly;

-- --- DEFAULT PRIVILEGES (Future Objects) ---

-- app_user: SELECT, INSERT, UPDATE, DELETE
ALTER DEFAULT PRIVILEGES FOR ROLE app_owner IN SCHEMA db_schema
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;

-- app_readonly: SELECT TABLES
ALTER DEFAULT PRIVILEGES FOR ROLE app_owner IN SCHEMA db_schema
    GRANT SELECT ON TABLES TO app_readonly;

-- app_user, app_readonly: USAGE, SELECT ON SEQUENCES
ALTER DEFAULT PRIVILEGES FOR ROLE app_owner IN SCHEMA db_schema
    GRANT USAGE, SELECT ON SEQUENCES TO app_user, app_readonly;

SET ROLE app_owner;
-- function: set the updated_at column
CREATE OR REPLACE FUNCTION db_schema.set_updated_at()
RETURNS trigger
LANGUAGE plpgsql
VOLATILE
AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;

RESET ROLE;

-- confirm schema
SELECT 
    schema_name,
    schema_owner
FROM information_schema.schemata
WHERE schema_name = 'db_schema';

SELECT
    routine_schema,
    routine_name,
    routine_type,
    data_type
FROM information_schema.routines
WHERE routine_schema = 'db_schema'
  AND routine_name = 'set_updated_at';