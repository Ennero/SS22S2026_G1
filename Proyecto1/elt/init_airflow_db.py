"""
elt/init_airflow_db.py
Verifica y asegura la existencia de la base de datos 'airflow' en PostgreSQL
antes de que Airflow ejecute las migraciones de metadatos.
"""

import os
import time
import psycopg2

def ensure_airflow_database_exists():
    host = os.getenv("POSTGRES_HOST", "postgres")
    port = int(os.getenv("POSTGRES_PORT", 5432))
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    default_db = os.getenv("POSTGRES_DB", "sgfood_dw")

    print(f"[INIT] Conectando a PostgreSQL en {host}:{port} para auditar BD 'airflow'...")
    for attempt in range(1, 16):
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                dbname=default_db
            )
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM pg_database WHERE datname = 'airflow';")
                if not cur.fetchone():
                    cur.execute("CREATE DATABASE airflow;")
                    print("[INIT] Base de datos 'airflow' creada exitosamente.")
                else:
                    print("[INIT] Base de datos 'airflow' ya existe.")
            conn.close()
            return True
        except Exception as exc:
            print(f"[INIT] Intento {attempt}/15 - Esperando a PostgreSQL: {exc}")
            time.sleep(2)
            
    raise RuntimeError("No se pudo conectar a PostgreSQL para inicializar la BD 'airflow'.")

if __name__ == "__main__":
    ensure_airflow_database_exists()
