-- ===================================================================================
-- PROYECTO 2: PROCESAMIENTO Y ANÁLISIS EXPLORATORIO DE DATOS MASIVOS EN BIGQUERY
-- SCRIPT 02: TRANSFORMACIONES, LIMPIEZA E INGENIERÍA DE CARACTERÍSTICAS
-- Curso: Seminario de Sistemas 2 - Segundo Semestre 2026
-- Grupo 1: Diego Alessandro Constanza Padilla (202300601) y Enner Esaí Mendizabal Castro (202302220)
-- ===================================================================================

CREATE OR REPLACE TABLE `nyc_taxi_dw.tbl_yellow_trips_clean` AS
WITH base_datos AS (
    SELECT
        vendor_id,
        pickup_datetime,
        pickup_datetime AS tpep_pickup_datetime,
        dropoff_datetime,
        dropoff_datetime AS tpep_dropoff_datetime,
        passenger_count,
        trip_distance,
        CAST(ROUND(SAFE_CAST(rate_code AS FLOAT64)) AS INT64) AS rate_code,
        CAST(ROUND(SAFE_CAST(rate_code AS FLOAT64)) AS INT64) AS RatecodeID,
        pickup_location_id,
        SAFE_CAST(pickup_location_id AS INT64) AS PULocationID,
        dropoff_location_id,
        SAFE_CAST(dropoff_location_id AS INT64) AS DOLocationID,
        SAFE_CAST(payment_type AS INT64) AS payment_type,
        fare_amount,
        extra,
        mta_tax,
        tip_amount,
        tolls_amount,
        imp_surcharge AS improvement_surcharge,
        total_amount,
        airport_fee,
        -- Duración calculada en minutos (precisión decimal)
        TIMESTAMP_DIFF(dropoff_datetime, pickup_datetime, SECOND) / 60.0 AS trip_duration_minutes
    FROM `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2022`
    WHERE
        -- 1. Filtro estricto del año de análisis 2022
        pickup_datetime >= TIMESTAMP('2022-01-01') AND pickup_datetime < TIMESTAMP('2023-01-01')
        AND dropoff_datetime > pickup_datetime
        -- 2. Filtro de distancias urbanas realistas
        AND trip_distance > 0.1 AND trip_distance <= 100.0
        -- 3. Filtro de importes reglamentarios en NYC (mínimo de bajada de bandera $2.50)
        AND fare_amount >= 2.50 AND fare_amount <= 500.0
        AND total_amount >= 2.50 AND total_amount <= 600.0
        -- 4. Pasajeros válidos según ley de taxis NYC
        AND passenger_count BETWEEN 1 AND 6
        -- 5. Métodos de pago comerciales estándar (1=Tarjeta, 2=Efectivo)
        AND payment_type IN ('1', '2')
        -- 6. Códigos de tarifa oficiales (incluyendo formato '1.0' presente en BigQuery)
        AND rate_code IN ('1.0', '2.0', '3.0', '4.0', '5.0', '1', '2', '3', '4', '5')
)
SELECT
    *,
    -- Velocidad promedio estimada en millas por hora (mph)
    ROUND(trip_distance / (trip_duration_minutes / 60.0), 2) AS trip_speed_mph,
    -- Variables temporales y de calendario
    EXTRACT(HOUR FROM pickup_datetime) AS pickup_hour,
    EXTRACT(DAYOFWEEK FROM pickup_datetime) AS pickup_day_of_week,
    EXTRACT(MONTH FROM pickup_datetime) AS pickup_month,
    -- Indicador de fin de semana (1 = Domingo, 7 = Sábado en BigQuery)
    IF(EXTRACT(DAYOFWEEK FROM pickup_datetime) IN (1, 7), 1, 0) AS is_weekend,
    -- Indicador de horas pico en días laborales (7:00-9:30 AM y 16:00-19:30 PM de Lunes a Viernes)
    IF(
        EXTRACT(DAYOFWEEK FROM pickup_datetime) BETWEEN 2 AND 6
        AND (
            (EXTRACT(HOUR FROM pickup_datetime) BETWEEN 7 AND 9)
            OR (EXTRACT(HOUR FROM pickup_datetime) BETWEEN 16 AND 19)
        ), 1, 0
    ) AS is_rush_hour,
    -- Indicador de viajes aeroportuarios (JFK: 132, LaGuardia: 138, Newark: 1)
    IF(pickup_location_id IN ('132', '138', '1') OR dropoff_location_id IN ('132', '138', '1'), 1, 0) AS is_airport_trip,
    -- Ratio de propina con respecto a la tarifa base
    ROUND(SAFE_DIVIDE(tip_amount, fare_amount), 4) AS tip_ratio,
    -- Bandera de partición cronológica estricta para evitar Data Leakage en BQML:
    -- TRAIN (Ene-Ago: ~70%), EVAL (Sep-Oct: ~15%), TEST (Nov-Dic: ~15%)
    CASE
        WHEN EXTRACT(MONTH FROM pickup_datetime) BETWEEN 1 AND 8 THEN 'TRAIN'
        WHEN EXTRACT(MONTH FROM pickup_datetime) BETWEEN 9 AND 10 THEN 'EVAL'
        ELSE 'TEST'
    END AS split_flag
FROM base_datos
WHERE
    -- Descartar registros con velocidades irreales producidas por congestión estática o errores de GPS
    (trip_distance / (trip_duration_minutes / 60.0)) <= 75.0
    AND trip_duration_minutes BETWEEN 1.0 AND 180.0;

-- -----------------------------------------------------------------------------------
-- VALIDACIÓN DEL RESULTADO LIMPIO Y CONTEO POR PARTICIÓN CRONOLÓGICA
-- -----------------------------------------------------------------------------------
SELECT 
    split_flag,
    COUNT(*) AS total_registros,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS porcentaje_split,
    ROUND(AVG(fare_amount), 2) AS tarifa_media,
    ROUND(AVG(trip_distance), 2) AS distancia_media,
    ROUND(AVG(trip_duration_minutes), 2) AS duracion_media_min
FROM `nyc_taxi_dw.tbl_yellow_trips_clean`
GROUP BY split_flag
ORDER BY 
    CASE split_flag
        WHEN 'TRAIN' THEN 1
        WHEN 'EVAL' THEN 2
        ELSE 3
    END;
