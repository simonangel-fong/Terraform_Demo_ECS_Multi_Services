-- 02_db.sql
\echo
\echo '######## Creating database ########'
\echo
     
CREATE DATABASE app_db
    OWNER app_owner
    ENCODING 'UTF8'
    TEMPLATE template1;

\connect app_db
\echo 'Connected to app_db'

-- Set DB-level settings
ALTER DATABASE app_db SET timezone = 'America/Toronto';
ALTER DATABASE app_db SET search_path = 'db_schema', 'public';

-- Confirm
SELECT datname
FROM pg_database
WHERE datname = 'app_db';

SHOW timezone;
SHOW search_path;
