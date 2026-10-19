"""
Script de Validación de Conexión a Google Cloud Platform y BigQuery
Curso: Seminario de Sistemas 2 - Segundo Semestre 2026
Grupo 1: Diego Constanza (202300601) y Enner Mendizabal (202302220)
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def test_connection():
    project_id = os.getenv("GCP_PROJECT_ID")
    dataset_id = os.getenv("GCP_DATASET_ID", "nyc_taxi_dw")
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    print("=" * 70)
    print("PROYECTO 2: DIAGNÓSTICO DE CONEXIÓN A GOOGLE BIGQUERY")
    print("=" * 70)
    print(f"[*] GCP_PROJECT_ID: {project_id or 'NO CONFIGURADO'}")
    print(f"[*] GCP_DATASET_ID: {dataset_id}")
    print(f"[*] GOOGLE_APPLICATION_CREDENTIALS: {credentials_path}")

    if not project_id or project_id == "tu-id-de-proyecto-gcp":
        print("\n[!] ERROR: Debes configurar GCP_PROJECT_ID en el archivo .env")
        return False

    if credentials_path and not os.path.exists(credentials_path):
        print(f"\n[!] AVISO: El archivo de credenciales '{credentials_path}' no existe localmente.")
        print("    Si ejecutas en Cloud Shell o con 'gcloud auth login', se usará la autenticación por defecto.")

    try:
        from google.cloud import bigquery
        client = bigquery.Client(project=project_id)
        print("\n[+] Cliente BigQuery inicializado con éxito.")

        # 1. Validar acceso al dataset público
        print("[*] Consultando dataset público: bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2022...")
        query_public = """
            SELECT COUNT(*) AS total_records
            FROM `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2022`
        """
        job = client.query(query_public)
        result = list(job.result())
        count = result[0].total_records
        print(f"[+] Total de registros encontrados en el dataset público: {count:,}")

        if count >= 1_000_000:
            print(f"[OK] Requisito cumplido: Registros ({count:,}) >= 1,000,000 registros mínimos.")
        else:
            print(f"[ALERTA] Registros menores a 1M: {count}")

        # 2. Verificar o crear dataset personal
        dataset_ref = bigquery.DatasetReference(project_id, dataset_id)
        try:
            client.get_dataset(dataset_ref)
            print(f"[+] Dataset personal '{dataset_id}' ya existe en el proyecto '{project_id}'.")
        except Exception:
            print(f"[*] Dataset '{dataset_id}' no encontrado. Creándolo en ubicación US...")
            new_dataset = bigquery.Dataset(dataset_ref)
            new_dataset.location = "US"
            new_dataset.description = "Dataset para Proyecto 2 de Seminario de Sistemas 2 - Grupo 1"
            client.create_dataset(new_dataset)
            print(f"[+] Dataset '{dataset_id}' creado exitosamente en 'US'.")

        print("\n" + "=" * 70)
        print("[EXITO] Conexión y permisos verificados al 100%. Entorno listo para operar.")
        print("=" * 70)
        return True

    except Exception as e:
        print(f"\n[ERROR CRITICO] Falló la conexión con BigQuery: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
