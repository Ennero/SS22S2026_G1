-- ===================================================================================
-- PROYECTO 2: PROCESAMIENTO Y ANÁLISIS EXPLORATORIO DE DATOS MASIVOS EN BIGQUERY
-- SCRIPT 01: EXPLORACIÓN INICIAL, AUDITORÍA DE CALIDAD Y DETECCIÓN DE ANOMALÍAS
-- Curso: Seminario de Sistemas 2 - Segundo Semestre 2026
-- Grupo 1: Diego Alessandro Constanza Padilla (202300601) y Enner Esaí Mendizabal Castro (202302220)
-- Dataset: bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2022
-- ===================================================================================

-- -----------------------------------------------------------------------------------
-- 1. VALIDACIÓN DE VOLUMEN TOTAL DE REGISTROS (REQUISITO: MÍNIMO 1,000,000 REGISTROS)
-- -----------------------------------------------------------------------------------
-- Este bloque demuestra que el dataset público excede ampliamente el requisito mínimo.
SELECT 
    COUNT(*) AS total_registros_publicos,
    COUNT(DISTINCT DATE(pickup_datetime)) AS dias_con_registros,
    MIN(pickup_datetime) AS fecha_minima_registrada,
    MAX(pickup_datetime) AS fecha_maxima_registrada
FROM `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2022`;

-- -----------------------------------------------------------------------------------
-- 2. AUDITORÍA DE VALORES NULOS Y COMPLETITUD POR VARIABLE CLAVE
-- -----------------------------------------------------------------------------------
SELECT 
    COUNT(*) AS total_filas,
    COUNTIF(vendor_id IS NULL) AS nulos_vendor,
    COUNTIF(pickup_datetime IS NULL) AS nulos_pickup_time,
    COUNTIF(dropoff_datetime IS NULL) AS nulos_dropoff_time,
    COUNTIF(passenger_count IS NULL) AS nulos_passenger_count,
    COUNTIF(trip_distance IS NULL) AS nulos_trip_distance,
    COUNTIF(rate_code IS NULL) AS nulos_ratecode,
    COUNTIF(pickup_location_id IS NULL) AS nulos_pu_location,
    COUNTIF(dropoff_location_id IS NULL) AS nulos_do_location,
    COUNTIF(payment_type IS NULL) AS nulos_payment_type,
    COUNTIF(fare_amount IS NULL) AS nulos_fare_amount,
    COUNTIF(tip_amount IS NULL) AS nulos_tip_amount,
    COUNTIF(total_amount IS NULL) AS nulos_total_amount
FROM `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2022`;

-- -----------------------------------------------------------------------------------
-- 3. DETECCIÓN DE ANOMALÍAS Y OUTLIERS EN EL DATASET CRUDO
-- -----------------------------------------------------------------------------------
-- Los datasets públicos de telemetría de taxis contienen ruidos comunes de calibración:
-- a) Fechas fuera del año 2022 (errores de reloj del taxímetro).
-- b) Tarifas negativas o cero (devoluciones, anulaciones o errores de captura).
-- c) Pasajeros en cero o superiores a la capacidad máxima legal (6 pasajeros).
-- d) Distancias cero con cobros elevados o distancias superiores a 150 millas.
-- e) Viajes donde la llegada ocurre antes que la partida.
SELECT
    COUNTIF(EXTRACT(YEAR FROM pickup_datetime) != 2022) AS viajes_fuera_de_2022,
    COUNTIF(dropoff_datetime <= pickup_datetime) AS dropoff_invalido_menor_pickup,
    COUNTIF(fare_amount < 2.50) AS tarifas_menores_base_minima,
    COUNTIF(fare_amount < 0) AS tarifas_negativas,
    COUNTIF(total_amount < 0) AS montos_totales_negativos,
    COUNTIF(trip_distance <= 0) AS distancias_cero_o_negativas,
    COUNTIF(trip_distance > 150) AS distancias_extremas_gt_150mi,
    COUNTIF(passenger_count = 0) AS pasajeros_cero,
    COUNTIF(passenger_count > 6) AS pasajeros_exceso_capacidad,
    COUNTIF(trip_distance = 0 AND fare_amount > 20) AS cobro_alto_sin_recorrido
FROM `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2022`;

-- -----------------------------------------------------------------------------------
-- 4. ESTADÍSTICAS DESCRIPTIVAS DE VARIABLES MÉTRICAS
-- -----------------------------------------------------------------------------------
SELECT
    'fare_amount' AS variable,
    ROUND(MIN(fare_amount), 2) AS minimo,
    ROUND(AVG(fare_amount), 2) AS promedio,
    ROUND(MAX(fare_amount), 2) AS maximo,
    ROUND(STDDEV(fare_amount), 2) AS desviacion_estandar
FROM `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2022`
UNION ALL
SELECT
    'trip_distance' AS variable,
    ROUND(MIN(trip_distance), 2) AS minimo,
    ROUND(AVG(trip_distance), 2) AS promedio,
    ROUND(MAX(trip_distance), 2) AS maximo,
    ROUND(STDDEV(trip_distance), 2) AS desviacion_estandar
FROM `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2022`
UNION ALL
SELECT
    'tip_amount' AS variable,
    ROUND(MIN(tip_amount), 2) AS minimo,
    ROUND(AVG(tip_amount), 2) AS promedio,
    ROUND(MAX(tip_amount), 2) AS maximo,
    ROUND(STDDEV(tip_amount), 2) AS desviacion_estandar
FROM `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2022`
UNION ALL
SELECT
    'total_amount' AS variable,
    ROUND(MIN(total_amount), 2) AS minimo,
    ROUND(AVG(total_amount), 2) AS promedio,
    ROUND(MAX(total_amount), 2) AS maximo,
    ROUND(STDDEV(total_amount), 2) AS desviacion_estandar
FROM `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2022`;

-- -----------------------------------------------------------------------------------
-- 5. DISTRIBUCIÓN POR MÉTODO DE PAGO (1=Tarjeta, 2=Efectivo, 3=Sin cargo, 4=Disputa)
-- -----------------------------------------------------------------------------------
SELECT
    payment_type,
    CASE payment_type
        WHEN '1' THEN 'Tarjeta de Crédito'
        WHEN '2' THEN 'Efectivo'
        WHEN '3' THEN 'Sin Cargo'
        WHEN '4' THEN 'Disputa'
        WHEN '5' THEN 'Desconocido'
        ELSE 'Otro / Nulo'
    END AS descripcion_pago,
    COUNT(*) AS total_viajes,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS porcentaje,
    ROUND(AVG(fare_amount), 2) AS tarifa_promedio,
    ROUND(AVG(tip_amount), 2) AS propina_promedio
FROM `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2022`
GROUP BY payment_type
ORDER BY total_viajes DESC;

-- -----------------------------------------------------------------------------------
-- 6. DISTRIBUCIÓN TEMPORAL DE DEMANDA POR MES DE 2022
-- -----------------------------------------------------------------------------------
SELECT
    EXTRACT(MONTH FROM pickup_datetime) AS mes_numero,
    FORMAT_DATE('%B', DATE(pickup_datetime)) AS nombre_mes,
    COUNT(*) AS total_viajes,
    ROUND(SUM(total_amount), 2) AS recaudacion_total,
    ROUND(AVG(fare_amount), 2) AS tarifa_media,
    ROUND(AVG(trip_distance), 2) AS distancia_media
FROM `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2022`
WHERE EXTRACT(YEAR FROM pickup_datetime) = 2022
GROUP BY mes_numero, nombre_mes
ORDER BY mes_numero;
