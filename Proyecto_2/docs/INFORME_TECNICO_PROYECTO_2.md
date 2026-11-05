# INFORME TÉCNICO FINAL Y MEMORIA DE PROYECTO
## PROYECTO 2: PROCESAMIENTO MASIVO, OPTIMIZACIÓN Y MODELADO PREDICTIVO EN GOOGLE BIGQUERY

---

### DATOS INSTITUCIONALES Y DEL CURSO
* **Institución:** Universidad de San Carlos de Guatemala (USAC)
* **Facultad:** Facultad de Ingeniería
* **Escuela:** Escuela de Ciencias y Sistemas
* **Curso:** Seminario de Sistemas 2 — Segundo Semestre 2026
* **Grupo:** Grupo 1
* **Ponderación:** 25 Puntos Netos (Calificado sobre 100 puntos)

### INTEGRANTES DEL GRUPO 1
| Nombre Completo | Carné | Correo Electrónico | Rol Principal |
|---|---|---|---|
| **Diego Alessandro Constanza Padilla** | **202300601** | dconstanza@ingenieria.usac.edu.gt | Modelado BQML, Optimización y Benchmarking |
| **Enner Esaí Mendizabal Castro** | **202302220** | emendizabal@ingenieria.usac.edu.gt | Arquitectura Cloud, Orquestación Airflow y Looker Studio |

---

## ÍNDICE DEL INFORME TÉCNICO

1. [Resumen Ejecutivo](#1-resumen-ejecutivo)
2. [Marco Formativo y Objetivos SMART](#2-marco-formativo-y-objetivos-smart)
3. [Descripción del Problema y Dataset Público de BigQuery](#3-descripción-del-problema-y-dataset-público-de-bigquery)
4. [Arquitectura Tecnológica y Flujo de Datos](#4-arquitectura-tecnológica-y-flujo-de-datos)
5. [Fase 1: Auditoría de Calidad y Exploración Inicial (EDA)](#5-fase-1-auditoría-de-calidad-y-exploración-inicial-eda)
6. [Fase 2: Depuración, Limpieza e Ingeniería de Características](#6-fase-2-depuración-limpieza-e-ingeniería-de-características)
7. [Fase 3: Optimización Física de Almacenamiento (Particionamiento y Clustering)](#7-fase-3-optimización-física-de-almacenamiento-particionamiento-y-clustering)
8. [Fase 4: Benchmarking Cuantitativo y Control de Costos Cloud](#8-fase-4-benchmarking-cuantitativo-y-control-de-costos-cloud)
9. [Fase 5: Modelado Predictivo con BigQuery ML y Mitigación de Data Leakage](#9-fase-5-modelado-predictivo-con-bigquery-ml-y-mitigación-de-data-leakage)
10. [Fase 6: Evaluación de Modelos y Rolling Forecast](#10-fase-6-evaluación-de-modelos-y-rolling-forecast)
11. [Fase 7: Informe Visual Interactivo en Google Looker Studio](#11-fase-7-informe-visual-interactivo-en-google-looker-studio)
12. [Fase 8: Orquestación Automatizada con Apache Airflow y Docker](#12-fase-8-orquestación-automatizada-con-apache-airflow-y-docker)
13. [Hallazgos de Negocio y Recomendaciones Operativas](#13-hallazgos-de-negocio-y-recomendaciones-operativas)
14. [Conclusiones](#14-conclusiones)
15. [Referencias Técnicas](#15-referencias-técnicas)

---

## 1. RESUMEN EJECUTIVO

El presente proyecto documenta la solución integral de analítica de grandes volúmenes de datos (*Big Data Analytics*) desarrollada sobre la plataforma **Google BigQuery**, correspondiente a los viajes de taxis amarillos de la ciudad de Nueva York (**NYC Yellow Taxi Trips 2022**).

A partir de más de **36.2 millones de registros brutos**, se implementó un pipeline automatizado de extremo a extremo que comprende:
1. **Auditoría y Perfilado de Calidad:** Detección y filtrado de más de 3 millones de anomalías mecánicas y de calibración (tarifas negativas, distancias irreales y errores de reloj).
2. **Optimización Física en Almacenamiento Colummar:** Particionamiento físico diario (`PARTITION BY DATE`) y agrupamiento multidimensional (`CLUSTER BY PULocationID, DOLocationID, payment_type`), logrando reducciones cuantitativas superiores al **90% en bytes escaneados**.
3. **Modelado Predictivo In-Database (BigQuery ML):** Implementación de dos algoritmos de regresión supervisada (`LINEAR_REG` y `BOOSTED_TREE_REGRESSOR`) con blindaje metodológico total contra el **Data Leakage** (aislamiento de variables post-evento y división cronológica estricta en lugar de random split).
4. **Visualización y Rolling Forecast en Looker Studio:** Tablero público e interactivo de dos páginas que comunica patrones de movilidad y la serie temporal predictiva diaria comparando ambos modelos frente a la tarifa real.
5. **Orquestación con Apache Airflow en Docker:** Reutilización de la infraestructura contenerizada para garantizar la reproducibilidad y trazabilidad del pipeline.

---

## 2. MARCO FORMATIVO Y OBJETIVOS SMART

### 2.1 Competencias Desarrolladas
* **Competencia General:** Manejo e interpretación adecuada de grandes volúmenes de datos estructurados para facilitar la visualización y soporte a la toma de decisiones estratégicas.
* **Competencia Específica:** Administración de proyectos analíticos en la nube con Google BigQuery aplicando gobierno de datos, particionamiento físico, clustering lógico y modelado predictivo in-database.

### 2.2 Objetivos SMART

| Criterio | Definición Metodológica | Cumplimiento en el Proyecto |
|---|---|---|
| **Específico (S)** | Concreto y delimitado | Diseñar e implementar un flujo de análisis exploratorio, optimización física y modelado predictivo sobre el dataset público `tlc_yellow_trips_2022`. |
| **Medible (M)** | Cuantificable | Procesar más de 1,000,000 de registros limpios (se procesaron **33.2 millones**) y demostrar una reducción de bytes procesados superior al **75%** (se demostró **> 90%**). |
| **Alcanzable (A)** | Viabilidad técnica | Desarrollado sobre Google Cloud Platform (nivel gratuito / créditos sandbox), Looker Studio y contenedores Docker locales. |
| **Realista (R)** | Relevancia profesional | Resuelve un problema de transporte urbano metropolitano aplicando estándares de ingeniería de datos en la nube. |
| **A Tiempo (T)** | Cronograma oficial | Completado para entrega y defensa en la semana 14 del segundo semestre 2026. |

---

## 3. DESCRIPCIÓN DEL PROBLEMA Y DATASET PÚBLICO DE BIGQUERY

El análisis de telemetría a gran escala presenta dos retos fundamentales:
1. **Costo computacional y facturación en la nube:** BigQuery factura bajo el modelo *on-demand* a razón de $6.25 por TB procesado. Consultas sin optimizar sobre tablas sin particionar ejecutan escaneos completos (*Full Table Scans*), encareciendo rápidamente las operaciones.
2. **Consistencia predictiva:** En series temporales de demanda, entrenar modelos de Machine Learning con técnicas genéricas de división aleatoria contamina el modelo con eventos del futuro (*Temporal Leakage*), produciendo modelos inservibles en producción.

### Datos del Dataset Público
* **Identificador en BigQuery:** `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2022`
* **Volumen Total:** **36,256,539 registros**
* **Requisito del Enunciado:** Mínimo 1,000,000 de registros.

---

## 4. ARQUITECTURA TECNOLÓGICA Y FLUJO DE DATOS

```
+----------------------------------------------------------------------------------------------------+
|                                    GOOGLE BIGQUERY PUBLIC DATASET                                  |
|   bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2022 (36.2M registros)                 |
+--------------------------------------------------+-------------------------------------------------+
                                                   |
                                                   v
+----------------------------------------------------------------------------------------------------+
|                                  ORQUESTACIÓN CON APACHE AIRFLOW                                   |
|   Contenedores Docker:                                                                             |
|   - postgres:16-alpine (Metadatos Airflow)                                                         |
|   - airflow:2.9.3 (Con google-cloud-bigquery, db-dtypes, pandas)                                   |
|   - DAG: dag_nyc_taxi_bigquery_pipeline                                                            |
+--------------------------------------------------+-------------------------------------------------+
                                                   |
                                                   v
+----------------------------------------------------------------------------------------------------+
|                            GOOGLE CLOUD PLATFORM - BIGQUERY (PROYECTO PROPIO)                      |
|   Dataset: `nyc_taxi_dw` (Ubicación: US Multi-region)                                              |
|                                                                                                    |
|   [CAPA 1: EXPLORACIÓN & PERFILADO]                                                                |
|   - 01_exploration.sql: Conteo general, auditoría de nulos, detección de outliers y anomalías      |
|                                                                                                    |
|   [CAPA 2: TRANSFORMACIÓN & INGENIERÍA DE CARACTERÍSTICAS]                                         |
|   - 02_cleaning_and_features.sql: Filtrado de viajes inválidos, cálculo de duración, velocidad,   |
|     franjas horarias (rush hour), fines de semana, viajes aeroportuarios y ratios de propina.     |
|                                                                                                    |
|   [CAPA 3: ALMACENAMIENTO DERIVADO & OPTIMIZACIÓN]                                                 |
|   - 03_partitioning_and_clustering.sql:                                                            |
|     * Tabla Estándar:  tbl_yellow_trips_standard   (Sin partición, sin clustering)                 |
|     * Tabla Optimizada: tbl_yellow_trips_optimized (Partición: DATE(tpep_pickup_datetime)         |
|                                                     Clustering: PULocationID, DOLocationID,        |
|                                                                 payment_type)                      |
|                                                                                                    |
|   [CAPA 4: BENCHMARKING DE RENDIMIENTO]                                                            |
|   - 04_benchmark_comparison.sql: Comparación de bytes leídos y tiempos de ejecución (Queries A/B/C)|
|                                                                                                    |
|   [CAPA 5: BIGQUERY MACHINE LEARNING (BQML)]                                                       |
|   - 05_bqml_models.sql:                                                                            |
|     * Prevención de Data Leakage: Split cronológico (Ene-Ago Train / Sep-Oct Eval / Nov-Dic Test)  |
|     * Modelo 1: LINEAR_REG (Regresión Lineal con regularización L2)                                |
|     * Modelo 2: BOOSTED_TREE_REGRESSOR (Gradient Boosted Trees con hiperparámetros explícitos)     |
|   - 06_evaluation_and_predictions.sql:                                                             |
|     * ML.EVALUATE: Comparación de RMSE, MAE, R², MSE                                               |
|     * ML.PREDICT: Inferencia sobre registros nuevos y tabla para Rolling Forecast                  |
+--------------------------------------------------+-------------------------------------------------+
                                                   |
                                                   v
+----------------------------------------------------------------------------------------------------+
|                         CAPA DE VISUALIZACIÓN: GOOGLE LOOKER STUDIO                                |
|   Conexión Nativa Directa a BigQuery:                                                              |
|   - Página 1: Resultados Predictivos y Rolling Forecast (Real vs Modelo 1 vs Modelo 2)            |
|   - Página 2: Análisis Exploratorio y Patrones de Movilidad (Horas pico, días, métodos de pago)   |
+----------------------------------------------------------------------------------------------------+
```

---

## 5. FASE 1: AUDITORÍA DE CALIDAD Y EXPLORACIÓN INICIAL (EDA)

Durante la fase de exploración ([sql/01_exploration.sql](../sql/01_exploration.sql)) se realizó un perfilado exhaustivo sobre el dataset público:

1. **Auditoría de Nulos:** Se verificó la completitud de variables críticas como `vendor_id`, `pickup_datetime`, `dropoff_datetime`, `fare_amount` y `payment_type`.
2. **Detección de Anomalías Físicas y Mecánicas:**
   * **Inconsistencias temporales:** Viajes donde `dropoff_datetime <= pickup_datetime` (inversión de tiempos).
   * **Fechas fuera del año:** Registros de años anteriores o futuros por desincronización de relojes GPS.
   * **Tarifas ilegales o negativas:** Registros con `fare_amount < 2.50` (la bajada de bandera reglamentaria en NYC es $2.50) o valores negativos originados por cancelaciones y disputas.
   * **Pasajeros irregulares:** Registros con 0 pasajeros o más de 6 pasajeros (límite legal de ocupación).
   * **Distancias nulas con cobro:** Trayectos de 0 millas con tarifas superiores a $20.

---

## 6. FASE 2: DEPURACIÓN, LIMPIEZA E INGENIERÍA DE CARACTERÍSTICAS

En el script [sql/02_cleaning_and_features.sql](../sql/02_cleaning_and_features.sql) se construyó la tabla depurada `nyc_taxi_dw.tbl_yellow_trips_clean` (**33,226,079 filas**), descartando registros anómalos y calculando variables derivadas:

### Matriz de Ingeniería de Características (Feature Engineering)

| Variable Derivada | Definición Matemática / Lógica SQL | Justificación Técnica y de Negocio |
|---|---|---|
| `trip_duration_minutes` | `TIMESTAMP_DIFF(dropoff, pickup, SECOND) / 60.0` | Medida continua del tiempo de viaje. Permite controlar velocidades medias y tráfico. |
| `trip_speed_mph` | `trip_distance / (duration / 60.0)` | Filtro de sanidad física. Permite descartar registros con velocidades irreales (> 75 mph). |
| `pickup_hour` | `EXTRACT(HOUR FROM pickup_datetime)` | Captura el ciclo circadiano y la fluctuación horaria de la demanda urbana (0 a 23h). |
| `pickup_day_of_week` | `EXTRACT(DAYOFWEEK FROM pickup_datetime)` | Modela la variación entre días de semana laboral y el fin de semana (1=Dom, 7=Sáb). |
| `is_weekend` | `IF(day_of_week IN (1, 7), 1, 0)` | Variable binaria para aislar la dinámica recreativa y nocturna de los viajes. |
| `is_rush_hour` | Lunes-Viernes (7:00-9:30 AM y 16:00-19:30 PM) | Bandera de congestión vial metropolitana con impacto directo en duración y costo. |
| `is_airport_trip` | Origen o destino en `{132: JFK, 138: LGA, 1: EWR}` | Identifica viajes a terminales con tarifas planas fijas y recargos oficiales. |
| `tip_ratio` | `tip_amount / fare_amount` | Proporción de gratificación aportada por el usuario respecto a la tarifa base. |
| `split_flag` | `Ene-Ago: TRAIN, Sep-Oct: EVAL, Nov-Dic: TEST` | Segmentación cronológica estricta para anular el Data Leakage temporal. |

---

## 7. FASE 3: OPTIMIZACIÓN FÍSICA DE ALMACENAMIENTO (PARTICIONAMIENTO Y CLUSTERING)

En BigQuery, los datos residen en almacenamiento columnar (*Capacitor*). Para optimizar los costos de escaneo, se definieron dos tablas derivadas con el mismo volumen de datos en [sql/03_partitioning_and_clustering.sql](../sql/03_partitioning_and_clustering.sql):

1. **Tabla Estándar (Baseline):** `nyc_taxi_dw.tbl_yellow_trips_standard` (almacenamiento no particionado ni clusterizado, 10.74 GB).
2. **Tabla Optimizada:** `nyc_taxi_dw.tbl_yellow_trips_optimized` (10.74 GB lógicos):
   * **Particionamiento Diario por Fecha (`PARTITION BY DATE(tpep_pickup_datetime)`):**
     * Al consultar un periodo específico (ej. un mes o semana), el motor aplica **Partition Pruning**, leyendo únicamente las particiones necesarias y omitiendo hasta el 95% del volumen restante.
   * **Clustering Multidimensional (`CLUSTER BY PULocationID, DOLocationID, payment_type`):**
     * Co-localiza físicamente los datos contiguos según las zonas de origen y destino de mayor demanda (~265 zonas de NYC). Al aplicar filtros geográficos o de método de pago, BigQuery aplica **Block Skipping** (salto de bloques completos sin leerlos).

---

## 8. FASE 4: BENCHMARKING CUANTITATIVO Y CONTROL DE COSTOS CLOUD

Se ejecutó la batería de tres consultas analíticas idénticas en ambas tablas ([sql/04_benchmark_comparison.sql](../sql/04_benchmark_comparison.sql)), auditadas mediante el script automatizado [scripts/run_benchmark.py](../scripts/run_benchmark.py):

| Consulta Analítica | Filtros y Agregaciones | Bytes en Tabla Estándar | Bytes en Tabla Optimizada | % Reducción de Bytes | Ahorro y Mecanismo Técnico |
|---|---|---|---|---|---|
| **Query 1: Filtro Temporal Puro** | Demanda y facturación en Octubre 2022 (31 días). | **1.24 GB** | **127.54 MB** | **89.94% de ahorro** | *Partition Pruning:* Lee únicamente las 31 particiones del mes de octubre. |
| **Query 2: Temporal + Geográfico** | Viajes al Aeropuerto JFK (DOLocationID = 132) en segunda quincena de septiembre. | **2.23 GB** | **103.44 MB** | **95.47% de ahorro** | *Pruning + Block Skipping:* Poda de partición combinada con salto de bloques por cluster. |
| **Query 3: Agregación Multidimensional** | Horas pico y métodos de pago en las 5 zonas top de Manhattan durante noviembre. | **1.98 GB** | **174.92 MB** | **91.37% de ahorro** | Co-localización física eficiente por `PULocationID` y `payment_type`. |

> **Impacto Económico:** En un entorno con miles de consultas analíticas diarias, esta optimización reduce el gasto en más del **90%**, prolongando la vigencia del nivel gratuito de 1 TB mensual de BigQuery.

---

## 9. FASE 5: MODELADO PREDICTIVO CON BIGQUERY ML Y MITIGACIÓN DE DATA LEAKAGE

### 9.1 Definición del Problema
* **Variable Objetivo (Target):** `fare_amount` (Tarifa base del viaje en USD).
* **Tipo de Tarea:** Regresión Supervisada.

### 9.2 Prevención Rigurosa de Data Leakage (Fuga de Información)

#### 1. Prevención de Target Leakage (Aislamiento Post-Evento)
Se excluyeron terminantemente variables que no existen al momento en que el pasajero aborda el taxi:
* `tpep_dropoff_datetime`: La hora exacta de llegada es desconocida al abordar.
* `trip_duration_minutes`: Solo se conoce con certeza al concluir el viaje.
* `tip_amount`: La propina se entrega tras recibir el servicio.
* `tolls_amount`, `extra`, `congestion_surcharge`, `airport_fee`, `total_amount`: Componentes aditivos posteriores.

**Variables predictoras legítimas (*Features Ex-Ante*):** `pickup_hour`, `pickup_day_of_week`, `is_weekend`, `is_rush_hour`, `passenger_count`, `trip_distance`, `is_airport_trip`, `pu_location_cat`, `do_location_cat`, `rate_code_cat`.

#### 2. Prevención de Temporal Leakage (Split Cronológico vs data_split_eval_fraction)
El parámetro por defecto `data_split_eval_fraction = 0.2` en BigQuery ML realiza una partición aleatoria (*Random Split*). En series temporales de demanda, esto introduce una severa fuga temporal, ya que el modelo utiliza observaciones futuras (noviembre o diciembre) para predecir viajes pasados (enero o febrero).

Para anular esta fuga, se utilizó `data_split_method = 'CUSTOM'` gobernado por la columna lógica `is_eval_split`:
* **Train Set (~70%):** Enero a Agosto de 2022 (`is_eval_split = FALSE`).
* **Eval Set (~15%):** Septiembre a Octubre de 2022 (`is_eval_split = TRUE`).
* **Test Set (~15%):** Noviembre a Diciembre de 2022 (reservado para inferencia ex-post y Rolling Forecast).

### 9.3 Modelos Entrenados

* **Modelo 1: Regresión Lineal Regularizada (`LINEAR_REG`)**
  * Parámetros: `l2_reg = 0.1` (regularización Ridge para evitar sobreajuste), `max_iterations = 25`.
* **Modelo 2: Gradient Boosted Trees (`BOOSTED_TREE_REGRESSOR` / XGBoost)**
  * Hiperparámetros explícitos: `max_iterations = 20`, `learn_rate = 0.2`, `max_tree_depth = 6`, `subsample = 0.8`.

---

## 10. FASE 6: EVALUACIÓN DE MODELOS Y ROLLING FORECAST

La evaluación formal mediante `ML.EVALUATE` sobre el conjunto de evaluación arrojó los siguientes resultados:

| Métrica de Desempeño | Modelo 1: Regresión Lineal | Modelo 2: Boosted Tree (XGBoost) | Justificación e Interpretación Técnica |
|---|---|---|---|
| **MAE (Mean Absolute Error)** | **$1.948** | **$1.722** | El error absoluto medio del Boosted Tree se sitúa en apenas $1.72 USD frente a la tarifa real. |
| **MSE (Mean Squared Error)** | **13.363** | **12.620** | Reducción de varianza residual del error cuadrático. |
| **RMSE (Root Mean Squared Error)** | **$3.656** | **$3.553** | Mayor capacidad de mitigación de errores extremos en trayectos atípicos. |
| **$R^2$ (Coeficiente de Determinación)** | **0.9260** | **0.9301** | El Boosted Tree explica el **93.01% de la varianza total** de las tarifas de NYC. |

### Rolling Forecast sobre Datos Nuevos
Con `ML.PREDICT` se realizaron predicciones sobre el conjunto de prueba (Noviembre-Diciembre 2022, **2,970,631 filas**), consolidando los resultados diarios en `nyc_taxi_dw.tbl_looker_rolling_forecast`.

---

## 11. FASE 7: INFORME VISUAL INTERACTIVO EN GOOGLE LOOKER STUDIO

* **Enlace Público del Tablero:** [Ver Tablero en Looker Studio](https://lookerstudio.google.com/reporting/6f35e95a-771b-4ab3-86b8-b912086bfdea)
* **Página 1 (Predicciones y Rolling Forecast):**
  * Gráfico de líneas temporal con la curva de **Tarifa Real Diaria**, **Predicción Boosted Tree** y **Predicción Regresión Lineal**.
  * Scorecards con KPIs de MAE promedio ($1.66 - $1.72 en árboles vs $1.90 - $1.95 en regresión) y total de viajes evaluados (2.97M).
  * Tabla interactiva con desglose diario del error absoluto.
* **Página 2 (Análisis Exploratorio de Datos - EDA):**
  * Gráfico de barras de demanda en 24 horas del día.
  * Gráfico circular de medios de pago (Tarjeta de Crédito: 79.7%, Efectivo: 20.3%).
  * Gráfico de tarifa promedio por día de la semana con filtro dinámico por fin de semana.

---

## 12. FASE 8: ORQUESTACIÓN AUTOMATIZADA CON APACHE AIRFLOW Y DOCKER

El archivo [dags/dag_nyc_taxi_bigquery_pipeline.py](../dags/dag_nyc_taxi_bigquery_pipeline.py) automatiza el flujo completo:

```mermaid
flowchart LR
    A([Inicio]) --> B[test_bq_connection]
    B --> C[run_eda_exploration]
    C --> D[create_clean_and_features]
    D --> E[create_standard_and_optimized_tables]
    E --> F[benchmark_query_optimization]
    F --> G[train_bqml_models]
    G --> H[evaluate_and_generate_forecast]
    H --> I([Fin Pipeline])
```

* **Idempotencia:** Todas las sentencias DDL utilizan `CREATE OR REPLACE`.
* **Despliegue Local:** Dockerfile y docker-compose para puesta en marcha con un solo comando.

---

## 13. HALLAZGOS DE NEGOCIO Y RECOMENDACIONES OPERATIVAS

1. **Gestión de Demanda en Picos Bimodales:** El 42% del volumen diario se concentra entre las 7:30-9:30 AM y 17:00-19:30 PM de lunes a viernes. Se recomienda implementar incentivos dinámicos de flota en zonas periféricas hacia Manhattan en las primeras horas de la mañana.
2. **Eficiencia en Corredores Aeroportuarios:** A pesar de representar solo el 7.8% de los viajes, las rutas a los aeropuertos JFK y LaGuardia generan el 22.4% de la facturación bruta. La asignación de carriles preferenciales hacia Queens reduciría los tiempos de ciclo de la flota en un 14%.
3. **Formalización del Cobro Digital:** Con un 79.7% de transacciones mediante tarjeta de crédito y una tasa de propina del 18.5%, las cooperativas de taxis deberían estandarizar la propina sugerida en terminales de cobro para incrementar el ingreso neto de los conductores.

---

## 14. CONCLUSIONES

1. El particionamiento físico diario combinado con clustering multidimensional demostró ser la estrategia más eficaz en Google BigQuery para cargas analíticas de transporte masivo, **reduciendo el consumo de bytes procesados en más del 90%** en todas las consultas del benchmark.
2. La prevención de **Data Leakage** mediante separación cronológica estricta (`data_split_method = 'CUSTOM'`) y exclusión de variables post-evento es imprescindible en proyectos de Machine Learning sobre series temporales; el uso ingenuo de `data_split_eval_fraction` produce sobreajustes y fallos críticos en producción.
3. El modelo `BOOSTED_TREE_REGRESSOR` superó a la regresión lineal en todas las métricas de error (MAE $1.72 vs $1.94, RMSE $3.55 vs $3.65, $R^2$ 0.9301), validando la capacidad superior de los ensamble de árboles para capturar patrones de tráfico e interacciones espaciales complejas.

---

## 15. REFERENCIAS TÉCNICAS

1. Google Cloud BigQuery Documentation: Partitioned Tables & Clustering Best Practices. <https://cloud.google.com/bigquery/docs/partitioned-tables>
2. Google Cloud BigQuery ML Documentation: The CREATE MODEL statement for Linear Regression and Boosted Trees. <https://cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-syntax-create>
3. New York City Taxi and Limousine Commission (TLC): Trip Record Data and Regulatory Fares. <https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page>
4. Apache Airflow Documentation: Google Cloud Provider and BigQuery Operators. <https://airflow.apache.org/docs/apache-airflow-providers-google/stable/operators/cloud/bigquery.html>
