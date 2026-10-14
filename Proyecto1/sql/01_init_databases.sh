#!/bin/bash
set -e

echo "[INIT] Inicializando bases de datos y schemas para SG-Food..."

# Crear base de datos de metadatos de Airflow y Data Warehouse si no existen
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    SELECT 'CREATE DATABASE airflow' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'airflow')\gexec
    SELECT 'CREATE DATABASE sgfood_dw' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'sgfood_dw')\gexec
EOSQL

# Crear esquemas en la base de datos sgfood_dw
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "sgfood_dw" <<-EOSQL
    CREATE SCHEMA IF NOT EXISTS oltp_sgfood;
    CREATE SCHEMA IF NOT EXISTS raw;
    CREATE SCHEMA IF NOT EXISTS staging;
    CREATE SCHEMA IF NOT EXISTS intermediate;
    CREATE SCHEMA IF NOT EXISTS marts;
EOSQL

# Cargar el esquema OLTP transaccional de SG-Food
if [ -f "/docker-entrypoint-initdb.d/sgfood_oltp.sql" ]; then
    echo "[INIT] Ejecutando sgfood_oltp.sql en sgfood_dw..."
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "sgfood_dw" -f /docker-entrypoint-initdb.d/sgfood_oltp.sql
fi

echo "[INIT] Base de datos y schemas listos exitosamente."
