-- ============================================================================
-- PostgreSQL Database Setup Script
-- نص إعداد قاعدة البيانات PostgreSQL
-- ============================================================================
-- Khalifa Pharmacy Conversation Management System
-- نظام إدارة محادثات صيدليات خليفة
-- ============================================================================

-- Instructions:
-- 1. Install PostgreSQL 15+ on your system
-- 2. Open PostgreSQL command line (psql) or pgAdmin
-- 3. Run this script as postgres superuser
-- 4. Update .env file with the credentials
-- ============================================================================

-- Create Database
DROP DATABASE IF EXISTS khalifa_pharmacy_db;
CREATE DATABASE khalifa_pharmacy_db
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    TEMPLATE template0;

COMMENT ON DATABASE khalifa_pharmacy_db IS 'Khalifa Pharmacy WhatsApp Management System';

-- Connect to the database
\c khalifa_pharmacy_db;

-- Create dedicated user (optional - recommended for production)
-- DROP USER IF EXISTS khalifa_user;
-- CREATE USER khalifa_user WITH PASSWORD 'your_secure_password_here';

-- Grant privileges to the user
-- GRANT ALL PRIVILEGES ON DATABASE khalifa_pharmacy_db TO khalifa_user;
-- GRANT ALL ON SCHEMA public TO khalifa_user;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO khalifa_user;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO khalifa_user;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search optimization

-- Configure database for optimal performance
ALTER DATABASE khalifa_pharmacy_db SET timezone TO 'Africa/Cairo';
ALTER DATABASE khalifa_pharmacy_db SET client_encoding TO 'UTF8';

-- Create schema if needed (optional)
-- CREATE SCHEMA IF NOT EXISTS conversations;
-- GRANT USAGE ON SCHEMA conversations TO khalifa_user;

-- ============================================================================
-- Performance Tuning (adjust based on your server specs)
-- ============================================================================

-- Increase shared buffers (25% of RAM recommended)
-- ALTER SYSTEM SET shared_buffers = '256MB';

-- Increase work memory for complex queries
-- ALTER SYSTEM SET work_mem = '16MB';

-- Increase maintenance work memory
-- ALTER SYSTEM SET maintenance_work_mem = '128MB';

-- Enable query logging for debugging (disable in production)
-- ALTER SYSTEM SET log_statement = 'all';
-- ALTER SYSTEM SET log_duration = on;

-- Reload configuration
-- SELECT pg_reload_conf();

-- ============================================================================
-- Verify Setup
-- ============================================================================

-- Show database encoding
SELECT 
    datname as "Database",
    pg_encoding_to_char(encoding) as "Encoding",
    datcollate as "Collate",
    datctype as "CType"
FROM pg_database 
WHERE datname = 'khalifa_pharmacy_db';

-- Show current timezone
SHOW timezone;

-- List installed extensions
SELECT * FROM pg_extension;

-- ============================================================================
-- Next Steps:
-- ============================================================================
-- 1. Update .env file:
--    DB_ENGINE=postgresql
--    DB_NAME=khalifa_pharmacy_db
--    DB_USER=postgres
--    DB_PASSWORD=your_password
--    DB_HOST=localhost
--    DB_PORT=5432
--
-- 2. Install psycopg2-binary:
--    pip install psycopg2-binary==2.9.9
--
-- 3. Run Django migrations:
--    python manage.py migrate
--
-- 4. Load backed up data:
--    python manage.py loaddata backups/data_backup_TIMESTAMP.json
--
-- 5. Verify migration:
--    python verify_database.py
-- ============================================================================
