"""
DAG de Apache Airflow: Pipeline de Procesamiento, Optimización y BQML sobre NYC Taxi 2022
Curso: Seminario de Sistemas 2 - Segundo Semestre 2026
Grupo 1: Diego Alessandro Constanza Padilla (202300601) y Enner Esaí Mendizabal Castro (202302220)
"""

import os
import time
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator

# Variables de entorno de GCP
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCP_DATASET_ID = os.getenv("GCP_DATASET_ID", "nyc_taxi_dw")
SQL_BASE_PATH = os.path.join(os.getenv("AIRFLOW_HOME", "/opt/airflow"), "sql")

default_args = {
    "owner": "Diego_Enner_G1",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

def get_bq_client():
    from google.cloud import bigquery
    if not GCP_PROJECT_ID:
        raise ValueError("GCP_PROJECT_ID no esta configurado en las variables de entorno.")
    return bigquery.Client(project=GCP_PROJECT_ID)

def execute_sql_file(file_name):
    """Lee y ejecuta un archivo SQL reemplazando el placeholder del dataset."""
    client = get_bq_client()
    file_path = os.path.join(SQL_BASE_PATH, file_name)
    print(f"[AIRFLOW] Leyendo archivo SQL: {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Reemplazar nombre del dataset si es necesario
    formatted_sql = sql_content.replace("nyc_taxi_dw", GCP_DATASET_ID)
    
    # Separar sentencias por punto y coma (omitiendo bloques vacíos)
    statements = [stmt.strip() for stmt in formatted_sql.split(";") if stmt.strip()]
    
    print(f"[AIRFLOW] Ejecutando {len(statements)} sentencias SQL en BigQuery...")
    for idx, stmt in enumerate(statements, 1):
        # Omitir comentarios de bloque puro
        clean_stmt = "\n".join([line for line in stmt.split("\n") if not line.strip().startswith("--")]).strip()
        if not clean_stmt:
            continue
        print(f"[*] Ejecutando sentencia {idx}/{len(statements)}...")
        job = client.query(stmt)
        job.result()  # Esperar a que finalice la consulta
        print(f"[OK] Sentencia {idx} completada.")

def test_connection_task():
    client = get_bq_client()
    print("[+] Conectado a GCP BigQuery con el proyecto:", client.project)
    query = "SELECT COUNT(*) AS total FROM `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2022`"
    job = client.query(query)
    total = list(job.result())[0].total
    print(f"[+] Total registros publicos verificados: {total:,}")
    assert total >= 1_000_000, f"Error: Registros {total} menores al millón requerido."

def run_benchmarks_task():
    client = get_bq_client()
    from google.cloud import bigquery
    
    queries = [
        {
            "name": "Prueba 1: Filtro Temporal Octubre",
            "sql_std": f"SELECT COUNT(*), AVG(fare_amount) FROM `{GCP_PROJECT_ID}.{GCP_DATASET_ID}.tbl_yellow_trips_standard` WHERE DATE(tpep_pickup_datetime) BETWEEN '2022-10-01' AND '2022-10-31'",
            "sql_opt": f"SELECT COUNT(*), AVG(fare_amount) FROM `{GCP_PROJECT_ID}.{GCP_DATASET_ID}.tbl_yellow_trips_optimized` WHERE DATE(tpep_pickup_datetime) BETWEEN '2022-10-01' AND '2022-10-31'"
        },
        {
            "name": "Prueba 2: JFK Septiembre",
            "sql_std": f"SELECT PULocationID, COUNT(*) FROM `{GCP_PROJECT_ID}.{GCP_DATASET_ID}.tbl_yellow_trips_standard` WHERE DATE(tpep_pickup_datetime) BETWEEN '2022-09-15' AND '2022-09-30' AND DOLocationID = 132 GROUP BY 1",
            "sql_opt": f"SELECT PULocationID, COUNT(*) FROM `{GCP_PROJECT_ID}.{GCP_DATASET_ID}.tbl_yellow_trips_optimized` WHERE DATE(tpep_pickup_datetime) BETWEEN '2022-09-15' AND '2022-09-30' AND DOLocationID = 132 GROUP BY 1"
        }
    ]
    
    print("=" * 80)
    print("RESULTADOS DEL BENCHMARKING DE CONSULTAS (ESTÁNDAR VS OPTIMIZADA)")
    print("=" * 80)
    for q in queries:
        job_std = client.query(q["sql_std"], job_config=bigquery.QueryJobConfig(dry_run=True))
        job_opt = client.query(q["sql_opt"], job_config=bigquery.QueryJobConfig(dry_run=True))
        b_std = job_std.total_bytes_processed
        b_opt = job_opt.total_bytes_processed
        ahorro = ((b_std - b_opt) / b_std * 100.0) if b_std > 0 else 0
        print(f"[*] {q['name']}:")
        print(f"    - Estandar:   {b_std / (1024*1024):.2f} MB")
        print(f"    - Optimizado: {b_opt / (1024*1024):.2f} MB")
        print(f"    - REDUCCIÓN:  {ahorro:.2f} %")
    print("=" * 80)

with DAG(
    dag_id="dag_nyc_taxi_bigquery_pipeline",
    default_args=default_args,
    description="Pipeline ELT, Optimización y BQML para NYC Taxi Trips 2022",
    schedule_interval=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["bigquery", "seminario2", "grupo1", "bqml", "docker"],
) as dag:

    start_pipeline = EmptyOperator(task_id="start_pipeline")

    t1_test_connection = PythonOperator(
        task_id="test_bq_connection",
        python_callable=test_connection_task
    )

    t2_eda_exploration = PythonOperator(
        task_id="run_eda_exploration",
        python_callable=execute_sql_file,
        op_kwargs={"file_name": "01_exploration.sql"}
    )

    t3_cleaning_and_features = PythonOperator(
        task_id="create_clean_and_features",
        python_callable=execute_sql_file,
        op_kwargs={"file_name": "02_cleaning_and_features.sql"}
    )

    t4_partition_and_cluster = PythonOperator(
        task_id="create_standard_and_optimized_tables",
        python_callable=execute_sql_file,
        op_kwargs={"file_name": "03_partitioning_and_clustering.sql"}
    )

    t5_run_benchmarks = PythonOperator(
        task_id="benchmark_query_optimization",
        python_callable=run_benchmarks_task
    )

    t6_train_bqml_models = PythonOperator(
        task_id="train_bqml_models",
        python_callable=execute_sql_file,
        op_kwargs={"file_name": "05_bqml_models.sql"}
    )

    t7_evaluate_and_predict = PythonOperator(
        task_id="evaluate_and_generate_forecast",
        python_callable=execute_sql_file,
        op_kwargs={"file_name": "06_evaluation_and_predictions.sql"}
    )

    end_pipeline = EmptyOperator(task_id="end_pipeline")

    # Dependencias del DAG
    start_pipeline >> t1_test_connection >> t2_eda_exploration
    t2_eda_exploration >> t3_cleaning_and_features >> t4_partition_and_cluster
    t4_partition_and_cluster >> t5_run_benchmarks >> t6_train_bqml_models
    t6_train_bqml_models >> t7_evaluate_and_predict >> end_pipeline
