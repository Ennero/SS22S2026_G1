-- ===================================================================================
-- PROYECTO 2: PROCESAMIENTO Y ANÁLISIS EXPLORATORIO DE DATOS MASIVOS EN BIGQUERY
-- SCRIPT 04: BATERÍA DE BENCHMARKING Y COMPARACIÓN DE RENDIMIENTO
-- Curso: Seminario de Sistemas 2 - Segundo Semestre 2026
-- Grupo 1: Diego Alessandro Constanza Padilla (202300601) y Enner Esaí Mendizabal Castro (202302220)
-- ===================================================================================

-- INSTRUCCIONES PARA LA GENERACIÓN DE EVIDENCIAS TÉCNICAS:
-- 1. Al abrir cada consulta en el editor de Google BigQuery, observar el mensaje en la
--    esquina superior derecha: "Esta consulta procesará X GB cuando se ejecute".
-- 2. Tomar captura de pantalla de la consulta estándar vs la consulta optimizada.
-- 3. Tras ejecutarla, revisar la pestaña "Detalles de la ejecución" para validar:
--    - Bytes leídos / procesados (Billed Bytes).
--    - Tiempo transcurrido (Elapsed Time) y Tiempo de slot (Slot Time).

-- ===================================================================================
-- PRUEBA 1: FILTRO TEMPORAL PURO (DEMOSTRACIÓN DE PARTITION PRUNING)
-- Objetivo: Evaluar el comportamiento de la consulta al filtrar por un mes específico
--           (Octubre 2022).
-- ===================================================================================

-- 1A: CONSULTA ESTÁNDAR (FULL TABLE SCAN)
SELECT 
    EXTRACT(DAY FROM tpep_pickup_datetime) AS dia_del_mes,
    COUNT(*) AS total_viajes,
    ROUND(AVG(fare_amount), 2) AS tarifa_promedio,
    ROUND(AVG(trip_distance), 2) AS distancia_promedio,
    ROUND(SUM(total_amount), 2) AS recaudacion_total
FROM `nyc_taxi_dw.tbl_yellow_trips_standard`
WHERE DATE(tpep_pickup_datetime) BETWEEN '2022-10-01' AND '2022-10-31'
GROUP BY dia_del_mes
ORDER BY dia_del_mes;

-- 1B: CONSULTA OPTIMIZADA (PARTITION PRUNING ACTIVO)
-- BigQuery lee ÚNICAMENTE los metadatos y bloques de almacenamiento de los 31 días de octubre.
SELECT 
    EXTRACT(DAY FROM tpep_pickup_datetime) AS dia_del_mes,
    COUNT(*) AS total_viajes,
    ROUND(AVG(fare_amount), 2) AS tarifa_promedio,
    ROUND(AVG(trip_distance), 2) AS distancia_promedio,
    ROUND(SUM(total_amount), 2) AS recaudacion_total
FROM `nyc_taxi_dw.tbl_yellow_trips_optimized`
WHERE DATE(tpep_pickup_datetime) BETWEEN '2022-10-01' AND '2022-10-31'
GROUP BY dia_del_mes
ORDER BY dia_del_mes;


-- ===================================================================================
-- PRUEBA 2: FILTRO TEMPORAL + CLUSTERING GEOGRÁFICO (PARTICIÓN + BLOCK SKIPPING)
-- Objetivo: Analizar trayectos dirigidos al Aeropuerto JFK (DOLocationID = 132) durante
--           la segunda quincena de septiembre de 2022.
-- ===================================================================================

-- 2A: CONSULTA ESTÁNDAR (ESCANEADO COMPLETO)
SELECT 
    PULocationID AS zona_origen,
    COUNT(*) AS total_viajes_a_jfk,
    ROUND(AVG(trip_distance), 2) AS distancia_media,
    ROUND(AVG(fare_amount), 2) AS tarifa_media,
    ROUND(AVG(tip_amount), 2) AS propina_media,
    ROUND(SUM(total_amount), 2) AS facturacion_total
FROM `nyc_taxi_dw.tbl_yellow_trips_standard`
WHERE DATE(tpep_pickup_datetime) BETWEEN '2022-09-15' AND '2022-09-30'
  AND DOLocationID = 132
GROUP BY zona_origen
ORDER BY total_viajes_a_jfk DESC
LIMIT 10;

-- 2B: CONSULTA OPTIMIZADA (PARTICIÓN POR FECHA + CLUSTER POR DOLocationID)
-- BigQuery solo escanea las particiones de la quincena y descarta bloques donde DOLocationID != 132.
SELECT 
    PULocationID AS zona_origen,
    COUNT(*) AS total_viajes_a_jfk,
    ROUND(AVG(trip_distance), 2) AS distancia_media,
    ROUND(AVG(fare_amount), 2) AS tarifa_media,
    ROUND(AVG(tip_amount), 2) AS propina_media,
    ROUND(SUM(total_amount), 2) AS facturacion_total
FROM `nyc_taxi_dw.tbl_yellow_trips_optimized`
WHERE DATE(tpep_pickup_datetime) BETWEEN '2022-09-15' AND '2022-09-30'
  AND DOLocationID = 132
GROUP BY zona_origen
ORDER BY total_viajes_a_jfk DESC
LIMIT 10;


-- ===================================================================================
-- PRUEBA 3: AGREGACIÓN MULTIDIMENSIONAL COMPLEJA (FECHA + CLUSTERING + NEGOCIO)
-- Objetivo: Evaluar transacciones por método de pago y condición de hora pico en las 5
--           zonas con mayor tráfico de Manhattan (237, 236, 161, 162, 230) durante noviembre.
-- ===================================================================================

-- 3A: CONSULTA ESTÁNDAR
SELECT 
    payment_type,
    is_rush_hour,
    COUNT(*) AS total_viajes,
    ROUND(AVG(fare_amount), 2) AS tarifa_promedio,
    ROUND(AVG(tip_ratio), 4) AS ratio_propina_medio,
    ROUND(SUM(total_amount), 2) AS total_recaudado
FROM `nyc_taxi_dw.tbl_yellow_trips_standard`
WHERE DATE(tpep_pickup_datetime) BETWEEN '2022-11-01' AND '2022-11-30'
  AND PULocationID IN (237, 236, 161, 162, 230)
GROUP BY payment_type, is_rush_hour
ORDER BY total_viajes DESC;

-- 3B: CONSULTA OPTIMIZADA
-- Aprovecha el particionamiento de noviembre y el cluster co-localizado en PULocationID y payment_type.
SELECT 
    payment_type,
    is_rush_hour,
    COUNT(*) AS total_viajes,
    ROUND(AVG(fare_amount), 2) AS tarifa_promedio,
    ROUND(AVG(tip_ratio), 4) AS ratio_propina_medio,
    ROUND(SUM(total_amount), 2) AS total_recaudado
FROM `nyc_taxi_dw.tbl_yellow_trips_optimized`
WHERE DATE(tpep_pickup_datetime) BETWEEN '2022-11-01' AND '2022-11-30'
  AND PULocationID IN (237, 236, 161, 162, 230)
GROUP BY payment_type, is_rush_hour
ORDER BY total_viajes DESC;
