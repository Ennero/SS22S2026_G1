# GUÍA DE CAPTURAS DE PANTALLA Y EVIDENCIAS TÉCNICAS
## Proyecto 2: Seminario de Sistemas 2 - Grupo 1

Para respaldar la calificación de los 100 puntos según la rúbrica oficial, colocar en esta carpeta las siguientes capturas tomadas de Google Cloud Console y Apache Airflow:

| Archivo de Imagen | Descripción de la Evidencia Técnica | Criterio de la Rúbrica |
|---|---|---|
| `01_bq_dataset_public_count.png` | Captura de BigQuery Console ejecutando el conteo de la tabla pública mostrando > 39M de registros (superando el requisito de > 1M). | 1.1 Conexión y comprensión (8 pts) |
| `02_bq_table_standard_details.png` | Panel de "Detalles" de `tbl_yellow_trips_standard` en BigQuery mostrando que NO posee particiones ni clusters. | 1.3 Optimización (12 pts) |
| `03_bq_table_optimized_details.png` | Panel de "Detalles" de `tbl_yellow_trips_optimized` mostrando: `Tipo de tabla: Con particiones (por día en tpep_pickup_datetime)` y `Clúster por: PULocationID, DOLocationID, payment_type`. | 1.3 Optimización (12 pts) |
| `04_benchmark_query_bytes_standard.png` | Captura del validador de BigQuery en la esquina superior derecha mostrando "Esta consulta procesará ~1.85 GB cuando se ejecute" en la tabla estándar. | 2.5 Comparación de consultas (5 pts) |
| `05_benchmark_query_bytes_optimized.png` | Captura del validador mostrando "Esta consulta procesará ~158 MB cuando se ejecute" en la tabla optimizada (demostrando la reducción > 90%). | 2.5 Comparación de consultas (5 pts) |
| `06_bqml_training_jobs.png` | Historial de trabajos de BigQuery ML mostrando el entrenamiento exitoso de `model_fare_linear_reg` y `model_fare_boosted_tree`. | 1.4 Implementación de modelos (8 pts) |
| `07_bqml_model_evaluation.png` | Resultados de `ML.EVALUATE` en la consola de BigQuery con las métricas de RMSE, MAE y R² de ambos modelos. | 1.5 Evaluación y métricas (12 pts) |
| `08_airflow_dag_success.png` | Vista Grid o Tree del DAG `dag_nyc_taxi_bigquery_pipeline` en Airflow con todas las tareas en verde (`success`). | Entregables técnicos |
| `09_looker_studio_dashboard.png` | Captura panorámica de las páginas del informe interactivo publicado en Looker Studio. | 2.2 Visualización (10 pts) |
