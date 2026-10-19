-- ===================================================================================
-- PROYECTO 2: PROCESAMIENTO Y ANÁLISIS EXPLORATORIO DE DATOS MASIVOS EN BIGQUERY
-- SCRIPT 05: MODELADO PREDICTIVO CON BIGQUERY ML (BQML) Y PREVENCIÓN DE DATA LEAKAGE
-- Curso: Seminario de Sistemas 2 - Segundo Semestre 2026
-- Grupo 1: Diego Alessandro Constanza Padilla (202300601) y Enner Esaí Mendizabal Castro (202302220)
-- ===================================================================================

-- ===================================================================================
-- MARCO TEÓRICO: PREVENCIÓN DE DATA LEAKAGE (FUGA DE INFORMACIÓN)
-- ===================================================================================
-- El Data Leakage ocurre cuando el modelo tiene acceso a información que no existiría
-- al momento de realizar la predicción en el mundo real. En este proyecto se aplican
-- dos defensas rigurosas:
--
-- 1. PREVENCIÓN DE TARGET LEAKAGE (FUGA POR VARIABLES POST-EVENTO):
--    - Variable Objetivo (Target / Output): `fare_amount` (Tarifa base del viaje en USD).
--    - Variables Excluidas (PROHIBIDAS durante el entrenamiento):
--      * `tpep_dropoff_datetime`: La hora exacta de llegada es desconocida al abordar el taxi.
--      * `trip_duration_minutes`: Calculada a partir del dropoff; solo se conoce tras finalizar.
--      * `tip_amount`: La propina la decide el cliente al momento de pagar tras el viaje.
--      * `tolls_amount`, `extra`, `congestion_surcharge`, `airport_fee`, `total_amount`:
--        Son recargos post-viaje o componentes aditivos de la tarifa total.
--    - Variables Predictoras Válidas (Input Features Ex-Ante):
--      * `pickup_hour`: Hora del día (0-23) al abordar.
--      * `pickup_day_of_week`: Día de la semana (1-7).
--      * `is_weekend`: Indicador binario de fin de semana.
--      * `is_rush_hour`: Bandera de congestión por horario pico laboral.
--      * `CAST(PULocationID AS STRING)`: Zona de inicio (tratada como categórica).
--      * `CAST(DOLocationID AS STRING)`: Zona de destino esperada (categórica).
--      * `passenger_count`: Número de ocupantes.
--      * `trip_distance`: Distancia estimada de la ruta en millas.
--      * `is_airport_trip`: Indicador de origen/destino en JFK, LaGuardia o Newark.
--      * `CAST(RatecodeID AS STRING)`: Tarifa negociada/fija oficial.
--
-- 2. PREVENCIÓN DE TEMPORAL LEAKAGE (FUGA POR CONTAMINACIÓN TEMPORAL):
--    - En series temporales y movilidad urbana, el split aleatorio tradicional (RANDOM)
--      provoca que el modelo aprenda del "futuro" para predecir el "pasado".
--    - Solución: Split cronológico estricto:
--      * TRAIN SET (Enero - Agosto 2022): split_flag = 'TRAIN' (~70% de datos).
--      * EVAL SET (Septiembre - Octubre 2022): split_flag = 'EVAL' (~15% de datos).
--      * TEST SET (Noviembre - Diciembre 2022): split_flag = 'TEST' (~15% de datos para predicción).
-- ===================================================================================

-- -----------------------------------------------------------------------------------
-- VISTA DE DATOS PREPARADA PARA BQML (CON FLAG BOOLEANO PARA SPLIT PERSONALIZADO)
-- -----------------------------------------------------------------------------------
CREATE OR REPLACE VIEW `nyc_taxi_dw.vw_bqml_training_data` AS
SELECT
    -- Variable objetivo
    fare_amount,
    -- Variables predictoras ex-ante
    trip_distance,
    passenger_count,
    pickup_hour,
    pickup_day_of_week,
    is_weekend,
    is_rush_hour,
    is_airport_trip,
    CAST(PULocationID AS STRING) AS pu_location_cat,
    CAST(DOLocationID AS STRING) AS do_location_cat,
    CAST(RatecodeID AS STRING) AS rate_code_cat,
    -- Booleano para BigQuery ML CUSTOM split: FALSE = Train (Ene-Ago), TRUE = Eval (Sep-Oct)
    (split_flag = 'EVAL') AS is_eval_split
FROM `nyc_taxi_dw.tbl_yellow_trips_optimized`
WHERE split_flag IN ('TRAIN', 'EVAL');


-- ===================================================================================
-- MODELO 1: REGRESIÓN LINEAL CON REGULARIZACIÓN L2 (RIDGE REGRESSION)
-- ===================================================================================
-- Modelo paramétrico lineal que establece la línea base (baseline).
-- Hiperparámetros explícitos:
-- - `l2_reg = 0.1`: Penaliza pesos excesivos para evitar sobreajuste (overfitting).
-- - `max_iterations = 25`: Límite de épocas del optimizador de gradiente.
-- - `data_split_method = 'CUSTOM'`: Control determinista del conjunto de evaluación.
CREATE OR REPLACE MODEL `nyc_taxi_dw.model_fare_linear_reg`
OPTIONS(
    model_type = 'LINEAR_REG',
    input_label_cols = ['fare_amount'],
    l2_reg = 0.1,
    max_iterations = 25,
    data_split_method = 'CUSTOM',
    data_split_col = 'is_eval_split'
) AS
SELECT * 
FROM `nyc_taxi_dw.vw_bqml_training_data`;


-- ===================================================================================
-- MODELO 2: ÁRBOLES POTENCIADOS POR GRADIENTE (BOOSTED TREE REGRESSOR / XGBOOST)
-- ===================================================================================
-- Modelo no lineal basado en ensamble de árboles que captura interacciones complejas
-- no lineales entre la hora, el tráfico, la distancia y las zonas de origen y destino.
-- Hiperparámetros explícitos:
-- - `max_iterations = 20`: Número de árboles potenciados a construir.
-- - `learn_rate = 0.2`: Tasa de aprendizaje que pondera la contribución de cada árbol.
-- - `tree_depth = 6`: Profundidad máxima de cada árbol de decisión.
-- - `subsample = 0.8`: Fracción de filas sub-muestreadas aleatoriamente por árbol.
-- - `data_split_method = 'CUSTOM'`: Split cronológico idéntico al Modelo 1.
CREATE OR REPLACE MODEL `nyc_taxi_dw.model_fare_boosted_tree`
OPTIONS(
    model_type = 'BOOSTED_TREE_REGRESSOR',
    input_label_cols = ['fare_amount'],
    max_iterations = 20,
    learn_rate = 0.2,
    tree_depth = 6,
    subsample = 0.8,
    data_split_method = 'CUSTOM',
    data_split_col = 'is_eval_split'
) AS
SELECT * 
FROM `nyc_taxi_dw.vw_bqml_training_data`;
