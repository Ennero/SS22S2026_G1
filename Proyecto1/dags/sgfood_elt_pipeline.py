"""
dags/sgfood_elt_pipeline.py
DAG orquestador principal del pipeline ELT para SG-Food.
Integra extracción en Python, carga a raw, transformaciones con dbt y pruebas de calidad.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Asegurar que el directorio raíz de la aplicación esté en el path
sys.path.insert(0, "/opt/airflow")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

from elt.db import test_connection, execute_sql, get_engine
from elt.extract_oltp import extract_and_load_oltp
from elt.extract_csv import extract_and_load_csvs
from elt.quality_checker import check_raw_tables_populated, evaluate_quality_rules

default_args = {
    "owner": "sgfood_data_team",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

def verify_and_seed_oltp_task():
    """Verifica que el schema oltp_sgfood esté creado y contenga datos."""
    from sqlalchemy import text
    engine = get_engine()
    with engine.connect() as conn:
        schema_exists = conn.execute(
            text("SELECT EXISTS (SELECT 1 FROM information_schema.schemata WHERE schema_name = 'oltp_sgfood');")
        ).scalar()
        if not schema_exists:
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS oltp_sgfood;"))
            
        count_sucursal = conn.execute(
            text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'oltp_sgfood';")
        ).scalar()
        if count_sucursal == 0:
            print("[SEED] Cargando sgfood_oltp.sql...")
            sql_path = Path("/opt/airflow/Data/sgfood_oltp.sql")
            if not sql_path.exists():
                sql_path = Path(__file__).resolve().parent.parent / "Data" / "sgfood_oltp.sql"
            with open(sql_path, "r", encoding="utf-8") as f:
                conn.execute(text(f.read()))
            print("[SEED] Datos de oltp_sgfood cargados exitosamente.")
        else:
            print(f"[SEED] Esquema oltp_sgfood ya contiene {count_sucursal} tablas.")

def apply_dw_constraints_task():
    """Aplica restricciones PK y FK al schema marts para navegabilidad en Adminer y optimizacion."""
    from sqlalchemy import text
    engine = get_engine()
    sql_path = Path("/opt/airflow/sql/apply_constraints.sql")
    if not sql_path.exists():
        sql_path = Path(__file__).resolve().parent.parent / "sql" / "apply_constraints.sql"
    with open(sql_path, "r", encoding="utf-8") as f:
        sql_content = f.read()
    with engine.begin() as conn:
        conn.execute(text(sql_content))
    print("[CONSTRAINTS] Restricciones PK y FK aplicadas con exito en schema marts.")

def log_completion_summary():
    """Genera un registro final de éxito del pipeline."""
    print("=" * 60)
    print("PIPELINE ELT SG-FOOD COMPLETADO CON ÉXITO")
    print("Extracción: OLTP + CSV -> RAW (Completa)")
    print("Modelos dbt: staging -> intermediate -> marts (Completa)")
    print("Restricciones Relacionales: PKs y FKs aplicadas en marts (Adminer/BI)")
    print("Validaciones de Calidad y Tests: APROBADOS")
    print("=" * 60)

with DAG(
    dag_id="sgfood_elt_pipeline",
    default_args=default_args,
    description="Pipeline ELT moderno: Python -> Raw -> dbt (Staging, Intermediate, Marts) -> Tests",
    schedule_interval=None, # Ejecución manual / parametrizable
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["sgfood", "elt", "dbt", "postgres", "proyecto1"],
) as dag:

    task_check_db = PythonOperator(
        task_id="check_database_connection",
        python_callable=test_connection,
    )

    task_seed_oltp = PythonOperator(
        task_id="verify_seed_oltp",
        python_callable=verify_and_seed_oltp_task,
    )

    task_extract_oltp = PythonOperator(
        task_id="extract_and_load_oltp_to_raw",
        python_callable=extract_and_load_oltp,
    )

    task_extract_csv = PythonOperator(
        task_id="extract_and_load_csv_to_raw",
        python_callable=extract_and_load_csvs,
    )

    task_verify_raw = PythonOperator(
        task_id="verify_raw_data_quality",
        python_callable=check_raw_tables_populated,
    )

    task_dbt_staging = BashOperator(
        task_id="dbt_run_staging",
        bash_command=(
            "dbt run --select staging "
            "--project-dir /opt/airflow/dbt_sgfood "
            "--profiles-dir /opt/airflow/dbt_sgfood"
        ),
    )

    task_dbt_intermediate = BashOperator(
        task_id="dbt_run_intermediate",
        bash_command=(
            "dbt run --select intermediate "
            "--project-dir /opt/airflow/dbt_sgfood "
            "--profiles-dir /opt/airflow/dbt_sgfood"
        ),
    )

    task_dbt_marts = BashOperator(
        task_id="dbt_run_marts",
        bash_command=(
            "dbt run --select marts "
            "--project-dir /opt/airflow/dbt_sgfood "
            "--profiles-dir /opt/airflow/dbt_sgfood"
        ),
    )

    task_apply_constraints = PythonOperator(
        task_id="apply_dw_constraints",
        python_callable=apply_dw_constraints_task,
    )

    task_dbt_test = BashOperator(
        task_id="dbt_test_quality_and_integrity",
        bash_command=(
            "dbt test "
            "--project-dir /opt/airflow/dbt_sgfood "
            "--profiles-dir /opt/airflow/dbt_sgfood"
        ),
    )

    task_summary = PythonOperator(
        task_id="pipeline_completion_summary",
        python_callable=log_completion_summary,
    )

    # Definición del flujo secuencial y paralelo del pipeline
    task_check_db >> task_seed_oltp >> [task_extract_oltp, task_extract_csv] >> task_verify_raw
    task_verify_raw >> task_dbt_staging >> task_dbt_intermediate >> task_dbt_marts >> task_apply_constraints >> task_dbt_test >> task_summary
