# Seminario de Sistemas 2 — pipelines y análisis de datos

Entregas de ingeniería de datos con Python, SQL Server, Airflow y BigQuery ML. Cada carpeta documenta una práctica o proyecto independiente.

Repositorio del **Grupo 1** del curso **Seminario de Sistemas 2** (ciclo 2026). Aquí se entregan las prácticas y tareas del semestre: pipelines de datos, calidad de información y análisis para soporte a la toma de decisiones.

Nombre del repositorio: **SS22S2026_G1**.

## Integrantes

| Nombre | Carné |
|---|---|
| Diego Alessandro Constanza Padilla | 202300601 |
| Enner Esaí Mendizabal Castro | 202302220 |

## Qué hay en este repo

Cada carpeta es una entrega independiente, con su propio README, datos y código.

| Carpeta | Ruta | Qué contiene |
|---|---|---|
| Práctica 1 | [`Practica1/`](Practica1/) | ETL de un dataset crudo de vuelos (~10 000 registros): limpieza, modelo estrella (6 dimensiones + hechos), carga a SQL Server 2022 en Docker y 10 consultas analíticas. |
| Práctica 2 | [`Practica2/`](Practica2/) | Continuación del pipeline de vuelos, consultas y visualización; reutiliza componentes de Practica1. |
| Proyecto 1 | [`Proyecto1/`](Proyecto1/) | Pipeline ELT de SGFood con Airflow y documentación de implementación. |
| Tarea 1 | [`Tarea1/`](Tarea1/) | Limpieza y análisis inicial con Python y Pandas sobre `dataset_sucio.csv` (clientes, gasto, ciudad y categoría): duplicados, nulos, estandarización, pivotes, gráficos y CSV depurado. |
| Proyecto 2 | [`Proyecto_2/`](Proyecto_2/) | Procesamiento masivo, optimización con particiones/clustering y BigQuery ML (Regresión Lineal y Boosted Trees) sobre NYC Taxi Trips 2022 (~39.6M registros), orquestado con Apache Airflow (Docker) y visualizado en Looker Studio. |

Otros archivos en la raíz:

- [`LICENSE`](LICENSE) — licencia MIT.
- [`.gitignore`](.gitignore) — entornos virtuales, `.env`, caches de Python, etc.

## Cómo empezar

1. Clonar el repositorio.
2. Entrar a la carpeta de la entrega que toque (`Practica1/`, `Practica2/`, `Proyecto1/`, `Proyecto_2/` o `Tarea1/`).
3. Seguir el README de esa carpeta (dependencias, Docker si aplica, y comando de ejecución).

```
SS22S2026_G1/
├── README.md              ← Este índice
├── LICENSE
├── Practica1/             ← ETL vuelos → SQL Server
├── Practica2/             ← Continuación ETL y visualización
├── Proyecto1/             ← ELT SGFood con Airflow
├── Tarea1/                ← Limpieza y análisis con Pandas
└── Proyecto_2/            ← BigQuery, Optimización, BQML & Airflow
```


## Configuración por entrega

Crear el `.env` de la carpeta elegida a partir de su `.env.example`, antes de usar Docker Compose. Las prácticas SQL Server requieren DB_PASSWORD; Proyecto1 configura su entorno Airflow y Proyecto_2 necesita además un proyecto GCP y credenciales propios para BigQuery. Usar datos y recursos de prueba: las consultas cloud dependen de permisos y pueden consumir recursos facturables.

No hay un proyecto dbt identificado en esta entrega. Los pasos, volúmenes de datos y resultados deben leerse dentro del alcance de cada práctica; no representan una medición del último commit.
