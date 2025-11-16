
\echo '\n######## Creating user, schema... ########\n'

\c app_db;

-- Create user, schema
CREATE USER app_user WITH PASSWORD 'postgres';
CREATE SCHEMA db_schema AUTHORIZATION app_user;
GRANT ALL PRIVILEGES ON SCHEMA db_schema TO app_user;

-- set timezone
ALTER DATABASE app_db SET timezone = 'America/Toronto';
SHOW timezone;   