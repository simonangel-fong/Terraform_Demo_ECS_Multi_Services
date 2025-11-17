-- 05_global_object.sql
\echo
\echo '######## Creating Global Objects ########'
\echo

\connect app_db

-- ENUM: account
CREATE TYPE db_schema.account_type AS ENUM ('individual', 'organization');

-- ENUM: user_role
CREATE TYPE db_schema.user_role AS ENUM ('owner', 'admin', 'operator', 'viewer');

-- ENUM: status
CREATE TYPE db_schema.device_status AS ENUM ('provisioned', 'active', 'suspended', 'retired');

-- ENUM: plan
CREATE TYPE db_schema.plan_code AS ENUM ('starter', 'pro', 'business', 'enterprise');

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

-- confirm
SELECT
    t.typname       AS type_name,
    e.enumlabel     AS enum_value,
    e.enumsortorder AS sort_order
FROM pg_type t
JOIN pg_enum e
  ON t.oid = e.enumtypid
JOIN pg_namespace n
  ON n.oid = t.typnamespace
WHERE n.nspname = 'db_schema'
  AND t.typname IN ('account_type', 'user_role', 'device_status', 'plan_code')
ORDER BY type_name, sort_order;

SELECT
    routine_schema,
    routine_name,
    routine_type,
    data_type
FROM information_schema.routines
WHERE routine_schema = 'db_schema'
  AND routine_name = 'set_updated_at';