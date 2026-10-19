-- ===================================================================================
-- PROYECTO 2: PROCESAMIENTO Y ANÁLISIS EXPLORATORIO DE DATOS MASIVOS EN BIGQUERY
-- SCRIPT 03: IMPLEMENTACIÓN DE PARTICIONAMIENTO Y CLUSTERING EN BIGQUERY
-- Curso: Seminario de Sistemas 2 - Segundo Semestre 2026
-- Grupo 1: Diego Alessandro Constanza Padilla (202300601) y Enner Esaí Mendizabal Castro (202302220)
-- ===================================================================================

-- -----------------------------------------------------------------------------------
-- TABLA 1: DERIVADA ESTÁNDAR (BASELINE - SIN PARTICIÓN Y SIN CLUSTERING)
-- -----------------------------------------------------------------------------------
-- Esta tabla almacena los registros limpios en formato tabular convencional.
-- En cualquier consulta sobre esta tabla, BigQuery debe realizar un escaneo completo
-- de las columnas referenciadas (Full Columnar Scan), aumentando los bytes leídos.
CREATE OR REPLACE TABLE `nyc_taxi_dw.tbl_yellow_trips_standard` AS
SELECT * 
FROM `nyc_taxi_dw.tbl_yellow_trips_clean`;

-- -----------------------------------------------------------------------------------
-- TABLA 2: DERIVADA OPTIMIZADA (CON PARTICIONAMIENTO Y CLUSTERING FÍSICO)
-- -----------------------------------------------------------------------------------
-- JUSTIFICACIÓN DE LAS TÉCNICAS APLICADAS:
-- 1. PARTITION BY DATE(tpep_pickup_datetime):
--    - Particiona el almacenamiento por día calendario.
--    - Permite "Partition Pruning": BigQuery omite por completo los bloques de días
--      que no caen dentro del rango especificado en el filtro WHERE.
-- 2. CLUSTER BY PULocationID, DOLocationID, payment_type:
--    - Ordena y co-localiza físicamente los datos dentro de cada partición.
--    - PULocationID y DOLocationID son las variables geográficas de mayor cardinalidad y
--      frecuencia de filtro.
--    - payment_type complementa agrupaciones financieras habituales.
--    - Permite "Block Skipping" (omisión de bloques contiguos no coincidentes).
CREATE OR REPLACE TABLE `nyc_taxi_dw.tbl_yellow_trips_optimized`
PARTITION BY DATE(tpep_pickup_datetime)
CLUSTER BY PULocationID, DOLocationID, payment_type AS
SELECT * 
FROM `nyc_taxi_dw.tbl_yellow_trips_clean`;

-- -----------------------------------------------------------------------------------
-- VERIFICACIÓN DE METADATOS Y ESQUEMA FÍSICO EN INFORMATION_SCHEMA
-- -----------------------------------------------------------------------------------
SELECT 
    table_name,
    is_partitioning_column,
    clustering_ordinal_position
FROM `nyc_taxi_dw.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name IN ('tbl_yellow_trips_standard', 'tbl_yellow_trips_optimized')
  AND (is_partitioning_column = 'YES' OR clustering_ordinal_position IS NOT NULL);

-- -----------------------------------------------------------------------------------
-- AUDITORÍA DE CONTEO Y TAMAÑO ALMACENADO DE AMBAS TABLAS
-- -----------------------------------------------------------------------------------
SELECT 
    table_id,
    row_count,
    ROUND(size_bytes / (1024 * 1024 * 1024), 2) AS tamano_gb,
    TIMESTAMP_MILLIS(creation_time) AS fecha_creacion
FROM `nyc_taxi_dw.__TABLES__`
WHERE table_id IN ('tbl_yellow_trips_standard', 'tbl_yellow_trips_optimized');
