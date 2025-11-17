-- 03_extension.sql
\echo
\echo '######## Creating Extension ########'
\echo

\connect app_db
\echo 'Connected to app_db'

CREATE EXTENSION IF NOT EXISTS citext WITH SCHEMA public;
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- confirm installed extensions
SELECT
    extname    AS extension_name,
    extversion AS version,
    n.nspname  AS schema_name
FROM pg_extension e
JOIN pg_namespace n
  ON n.oid = e.extnamespace
ORDER BY extension_name;

-- test pg_stat_statements
SELECT * FROM pg_stat_statements LIMIT 5;