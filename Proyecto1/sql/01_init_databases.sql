-- 01_init_databases.sql
-- Inicialización de base de datos de Airflow y esquemas para SG-Food

SELECT 'CREATE DATABASE airflow' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'airflow')\gexec

CREATE SCHEMA IF NOT EXISTS oltp_sgfood;
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS intermediate;
CREATE SCHEMA IF NOT EXISTS marts;
