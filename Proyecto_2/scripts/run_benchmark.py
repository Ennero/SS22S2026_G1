"""
Script Automatizado de Benchmarking y Comparación de Rendimiento
Seminario de Sistemas 2 - Segundo Semestre 2026
Grupo 1: Diego Constanza (202300601) y Enner Mendizabal (202302220)
"""

import os
import sys
import time
from dotenv import load_dotenv

load_dotenv()

def bytes_to_human(n_bytes):
    if n_bytes is None:
        return "N/A"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if abs(n_bytes) < 1024.0:
            return f"{n_bytes:3.2f} {unit}"
        n_bytes /= 1024.0
    return f"{n_bytes:.2f} PB"

def run_benchmarks(dry_run=True):
    project_id = os.getenv("GCP_PROJECT_ID")
    dataset_id = os.getenv("GCP_DATASET_ID", "nyc_taxi_dw")

    if not project_id:
        print("[!] ERROR: Configura GCP_PROJECT_ID en tu archivo .env")
        return

    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if cred_path and not os.path.exists(cred_path):
        os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)

    from google.cloud import bigquery
    client = bigquery.Client(project=project_id)

    # Definición de las 3 consultas analíticas en versión Estándar vs Optimizada
    queries = [
        {
            "name": "Query 1: Filtro Temporal (Demanda Octubre 2022)",
            "description": "Filtra viajes del mes de Octubre con agregaciones de tarifa e ingresos.",
            "sql_standard": f"""
                SELECT 
                    EXTRACT(DAY FROM tpep_pickup_datetime) AS dia,
                    COUNT(*) AS total_viajes,
                    ROUND(AVG(fare_amount), 2) AS tarifa_promedio,
                    ROUND(SUM(total_amount), 2) AS ingreso_total
                FROM `{project_id}.{dataset_id}.tbl_yellow_trips_standard`
                WHERE DATE(tpep_pickup_datetime) BETWEEN '2022-10-01' AND '2022-10-31'
                GROUP BY dia
                ORDER BY dia
            """,
            "sql_optimized": f"""
                SELECT 
                    EXTRACT(DAY FROM tpep_pickup_datetime) AS dia,
                    COUNT(*) AS total_viajes,
                    ROUND(AVG(fare_amount), 2) AS tarifa_promedio,
                    ROUND(SUM(total_amount), 2) AS ingreso_total
                FROM `{project_id}.{dataset_id}.tbl_yellow_trips_optimized`
                WHERE DATE(tpep_pickup_datetime) BETWEEN '2022-10-01' AND '2022-10-31'
                GROUP BY dia
                ORDER BY dia
            """
        },
        {
            "name": "Query 2: Filtro Temporal + Geográfico (Viajes a JFK en Septiembre)",
            "description": "Filtra viajes hacia el Aeropuerto JFK (DOLocationID = 132) durante la segunda quincena de septiembre.",
            "sql_standard": f"""
                SELECT 
                    PULocationID,
                    COUNT(*) AS viajes_a_jfk,
                    ROUND(AVG(trip_distance), 2) AS distancia_media,
                    ROUND(AVG(fare_amount), 2) AS tarifa_media,
                    ROUND(AVG(tip_amount), 2) AS propina_media
                FROM `{project_id}.{dataset_id}.tbl_yellow_trips_standard`
                WHERE DATE(tpep_pickup_datetime) BETWEEN '2022-09-15' AND '2022-09-30'
                  AND DOLocationID = 132
                GROUP BY PULocationID
                ORDER BY viajes_a_jfk DESC
                LIMIT 10
            """,
            "sql_optimized": f"""
                SELECT 
                    PULocationID,
                    COUNT(*) AS viajes_a_jfk,
                    ROUND(AVG(trip_distance), 2) AS distancia_media,
                    ROUND(AVG(fare_amount), 2) AS tarifa_media,
                    ROUND(AVG(tip_amount), 2) AS propina_media
                FROM `{project_id}.{dataset_id}.tbl_yellow_trips_optimized`
                WHERE DATE(tpep_pickup_datetime) BETWEEN '2022-09-15' AND '2022-09-30'
                  AND DOLocationID = 132
                GROUP BY PULocationID
                ORDER BY viajes_a_jfk DESC
                LIMIT 10
            """
        },
        {
            "name": "Query 3: Agregación Multidimensional (Horas Pico y Medios de Pago)",
            "description": "Agrupación compleja por método de pago y hora pico en los distritos principales durante noviembre.",
            "sql_standard": f"""
                SELECT 
                    payment_type,
                    is_rush_hour,
                    COUNT(*) AS total_viajes,
                    ROUND(AVG(fare_amount), 2) AS tarifa_promedio,
                    ROUND(AVG(tip_ratio), 4) AS ratio_propina_promedio
                FROM `{project_id}.{dataset_id}.tbl_yellow_trips_standard`
                WHERE DATE(tpep_pickup_datetime) BETWEEN '2022-11-01' AND '2022-11-30'
                  AND PULocationID IN (237, 236, 161, 162, 230)
                GROUP BY payment_type, is_rush_hour
                ORDER BY total_viajes DESC
            """,
            "sql_optimized": f"""
                SELECT 
                    payment_type,
                    is_rush_hour,
                    COUNT(*) AS total_viajes,
                    ROUND(AVG(fare_amount), 2) AS tarifa_promedio,
                    ROUND(AVG(tip_ratio), 4) AS ratio_propina_promedio
                FROM `{project_id}.{dataset_id}.tbl_yellow_trips_optimized`
                WHERE DATE(tpep_pickup_datetime) BETWEEN '2022-11-01' AND '2022-11-30'
                  AND PULocationID IN (237, 236, 161, 162, 230)
                GROUP BY payment_type, is_rush_hour
                ORDER BY total_viajes DESC
            """
        }
    ]

    print("=" * 90)
    print("PROYECTO 2: EJECUCIÓN DEL BENCHMARK COMPARATIVO DE RENDIMIENTO")
    print(f"Modo: {'DRY RUN (Estimación de bytes sin costo)' if dry_run else 'EJECUCIÓN REAL'}")
    print("=" * 90)

    results = []

    for item in queries:
        print(f"\n[+] Evaluando: {item['name']}")
        
        # 1. Consulta Estándar
        job_config_std = bigquery.QueryJobConfig(dry_run=dry_run, use_query_cache=False)
        start_t = time.time()
        job_std = client.query(item["sql_standard"], job_config=job_config_std)
        if not dry_run:
            _ = list(job_std.result())
        time_std = time.time() - start_t
        bytes_std = job_std.total_bytes_processed

        # 2. Consulta Optimizada
        job_config_opt = bigquery.QueryJobConfig(dry_run=dry_run, use_query_cache=False)
        start_t = time.time()
        job_opt = client.query(item["sql_optimized"], job_config=job_config_opt)
        if not dry_run:
            _ = list(job_opt.result())
        time_opt = time.time() - start_t
        bytes_opt = job_opt.total_bytes_processed

        # Métricas de Ahorro
        pct_bytes = ((bytes_std - bytes_opt) / bytes_std * 100.0) if bytes_std and bytes_std > 0 else 0.0

        results.append({
            "name": item["name"],
            "bytes_std": bytes_std,
            "bytes_opt": bytes_opt,
            "pct_bytes": pct_bytes,
            "time_std": time_std if not dry_run else None,
            "time_opt": time_opt if not dry_run else None
        })

        print(f"    - Tabla Estándar:  {bytes_to_human(bytes_std)}")
        print(f"    - Tabla Optimizada: {bytes_to_human(bytes_opt)}  --> AHORRO: {pct_bytes:.2f}%")

    print("\n" + "=" * 90)
    print("TABLA COMPARATIVA FINAL DE RENDIMIENTO (PARA README Y EVIDENCIAS)")
    print("=" * 90)
    print(f"{'Prueba / Consulta':<35} | {'Bytes Estándar':<15} | {'Bytes Optimizado':<16} | {'Reducción (%)':<14}")
    print("-" * 90)
    for r in results:
        print(f"{r['name'][:35]:<35} | {bytes_to_human(r['bytes_std']):<15} | {bytes_to_human(r['bytes_opt']):<16} | {r['pct_bytes']:>11.2f}%")
    print("=" * 90)

if __name__ == "__main__":
    is_real = "--real" in sys.argv
    run_benchmarks(dry_run=not is_real)
