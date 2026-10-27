-- ===================================================================================
-- PROYECTO 2: PROCESAMIENTO Y ANÁLISIS EXPLORATORIO DE DATOS MASIVOS EN BIGQUERY
-- SCRIPT 06: EVALUACIÓN DE MODELOS, COMPARACIÓN DE MÉTRICAS Y PREDICCIONES
-- Curso: Seminario de Sistemas 2 - Segundo Semestre 2026
-- Grupo 1: Diego Alessandro Constanza Padilla (202300601) y Enner Esaí Mendizabal Castro (202302220)
-- ===================================================================================

-- -----------------------------------------------------------------------------------
-- 1. EVALUACIÓN AISLADA DEL MODELO 1 (REGRESIÓN LINEAL)
-- -----------------------------------------------------------------------------------
SELECT 
    'Modelo 1: Regresión Lineal Regularizada' AS modelo,
    ROUND(mean_absolute_error, 3) AS mae_dolares,
    ROUND(mean_squared_error, 3) AS mse,
    ROUND(SQRT(mean_squared_error), 3) AS rmse_dolares,
    ROUND(r2_score, 4) AS r2_coeficiente_determinacion
FROM ML.EVALUATE(
    MODEL `nyc_taxi_dw.model_fare_linear_reg`,
    (SELECT * FROM `nyc_taxi_dw.vw_bqml_training_data` WHERE is_eval_split = TRUE)
);

-- -----------------------------------------------------------------------------------
-- 2. EVALUACIÓN AISLADA DEL MODELO 2 (BOOSTED TREE REGRESSOR)
-- -----------------------------------------------------------------------------------
SELECT 
    'Modelo 2: Boosted Tree Regressor (XGBoost)' AS modelo,
    ROUND(mean_absolute_error, 3) AS mae_dolares,
    ROUND(mean_squared_error, 3) AS mse,
    ROUND(SQRT(mean_squared_error), 3) AS rmse_dolares,
    ROUND(r2_score, 4) AS r2_coeficiente_determinacion
FROM ML.EVALUATE(
    MODEL `nyc_taxi_dw.model_fare_boosted_tree`,
    (SELECT * FROM `nyc_taxi_dw.vw_bqml_training_data` WHERE is_eval_split = TRUE)
);

-- -----------------------------------------------------------------------------------
-- 3. TABLA COMPARATIVA CONSOLIDADA DE MÉTRICAS ENTRE AMBOS MODELOS
-- -----------------------------------------------------------------------------------
SELECT 
    'Modelo 1: Regresión Lineal' AS modelo,
    ROUND(mean_absolute_error, 3) AS mae,
    ROUND(SQRT(mean_squared_error), 3) AS rmse,
    ROUND(r2_score, 4) AS r2,
    'Línea base paramétrica. Rápido, interpretable pero sensible a no linealidades.' AS conclusion_tecnica
FROM ML.EVALUATE(
    MODEL `nyc_taxi_dw.model_fare_linear_reg`,
    (SELECT * FROM `nyc_taxi_dw.vw_bqml_training_data` WHERE is_eval_split = TRUE)
)
UNION ALL
SELECT 
    'Modelo 2: Boosted Tree Regressor' AS modelo,
    ROUND(mean_absolute_error, 3) AS mae,
    ROUND(SQRT(mean_squared_error), 3) AS rmse,
    ROUND(r2_score, 4) AS r2,
    'Ensamble no lineal. Captura interacciones complejas de congestión y trayectos.' AS conclusion_tecnica
FROM ML.EVALUATE(
    MODEL `nyc_taxi_dw.model_fare_boosted_tree`,
    (SELECT * FROM `nyc_taxi_dw.vw_bqml_training_data` WHERE is_eval_split = TRUE)
);

-- -----------------------------------------------------------------------------------
-- 4. EJECUCIÓN DE PREDICCIONES SOBRE REGISTROS NUEVOS (TEST SET: NOVIEMBRE - DICIEMBRE)
-- -----------------------------------------------------------------------------------
-- Se generan predicciones para ambos modelos sobre datos que nunca participaron
-- en el entrenamiento ni en la evaluación, garantizando cero data leakage.
CREATE OR REPLACE TABLE `nyc_taxi_dw.tbl_ml_predictions_forecast` AS
WITH test_data AS (
    SELECT
        tpep_pickup_datetime,
        DATE(tpep_pickup_datetime) AS pickup_date,
        fare_amount AS actual_fare,
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
        PULocationID,
        DOLocationID
    FROM `nyc_taxi_dw.tbl_yellow_trips_optimized`
    WHERE split_flag = 'TEST'
),
pred_step1 AS (
    SELECT
        * EXCEPT(predicted_fare_amount),
        predicted_fare_amount AS pred_linear_fare
    FROM ML.PREDICT(
        MODEL `nyc_taxi_dw.model_fare_linear_reg`,
        (SELECT * FROM test_data)
    )
),
pred_step2 AS (
    SELECT
        * EXCEPT(predicted_fare_amount),
        predicted_fare_amount AS pred_boosted_fare
    FROM ML.PREDICT(
        MODEL `nyc_taxi_dw.model_fare_boosted_tree`,
        (SELECT * FROM pred_step1)
    )
)
SELECT
    pickup_date,
    pickup_hour,
    tpep_pickup_datetime,
    PULocationID,
    DOLocationID,
    trip_distance,
    passenger_count,
    ROUND(actual_fare, 2) AS actual_fare,
    ROUND(pred_linear_fare, 2) AS pred_linear_fare,
    ROUND(pred_boosted_fare, 2) AS pred_boosted_fare,
    -- Errores residuales individuales
    ROUND(ABS(actual_fare - pred_linear_fare), 2) AS residual_abs_linear,
    ROUND(ABS(actual_fare - pred_boosted_fare), 2) AS residual_abs_boosted
FROM pred_step2;

-- -----------------------------------------------------------------------------------
-- 5. TABLA AGREGADA DIARIA PARA EL ROLLING FORECAST EN LOOKER STUDIO
-- -----------------------------------------------------------------------------------
-- Esta vista/tabla optimizada resume la tendencia temporal diaria comparando:
-- Tarifa Real vs Predicción Modelo 1 vs Predicción Modelo 2.
CREATE OR REPLACE TABLE `nyc_taxi_dw.tbl_looker_rolling_forecast` AS
SELECT
    pickup_date,
    COUNT(*) AS total_viajes_evaluados,
    ROUND(AVG(actual_fare), 2) AS tarifa_real_promedio,
    ROUND(AVG(pred_linear_fare), 2) AS prediccion_linear_promedio,
    ROUND(AVG(pred_boosted_fare), 2) AS prediccion_boosted_promedio,
    ROUND(AVG(residual_abs_linear), 2) AS mae_diario_linear,
    ROUND(AVG(residual_abs_boosted), 2) AS mae_diario_boosted
FROM `nyc_taxi_dw.tbl_ml_predictions_forecast`
GROUP BY pickup_date
ORDER BY pickup_date;

-- Visualización de muestra para validación rápida
SELECT * 
FROM `nyc_taxi_dw.tbl_looker_rolling_forecast` 
ORDER BY pickup_date 
LIMIT 15;
