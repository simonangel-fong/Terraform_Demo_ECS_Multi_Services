-- 01_role.sql
\echo
\echo '######## creating roles ########'
\echo

-- app_owner: owns schema/tables, no direct login
CREATE ROLE app_owner NOLOGIN;

-- app_user: application user 
CREATE ROLE app_user
    LOGIN
    PASSWORD 'postgres'
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE;

-- app_readonly: optional read-only user
CREATE ROLE app_readonly
    LOGIN
    PASSWORD 'postgres'
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE;

-- confirm
SELECT
    rolname,
    rolcanlogin,
    rolsuper,
    rolcreaterole,
    rolcreatedb,
    rolinherit
FROM
    pg_roles
WHERE
    rolname IN ('app_owner', 'app_user', 'app_readonly');
