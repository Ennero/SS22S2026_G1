<div align="center">

# 🌪️ Data Engineering Pipeline with Apache Airflow & DBT (SS2)

**Pipeline analítico de datos de alto rendimiento: orquestación con Apache Airflow, transformaciones con DBT y Docker.**

[![Language](https://img.shields.io/badge/Language-Python,%20Docker,%20SQL-blue?style=for-the-badge)](https://github.com/Ennero/SS22S2026_G1)
[![Course](https://img.shields.io/badge/Course-Software%20Avanzado%202-003366?style=for-the-badge)](https://ingenieria.usac.edu.gt/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

</div>

---


## 📌 Contexto Académico

Proyecto desarrollado en el marco del curso **Software Avanzado 2** de la carrera de Ingeniería en Ciencias y Sistemas en la Universidad de San Carlos de Guatemala (USAC).

---

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
| Tarea 1 | [`Tarea1/`](Tarea1/) | Limpieza y análisis inicial con Python y Pandas sobre `dataset_sucio.csv` (clientes, gasto, ciudad y categoría): duplicados, nulos, estandarización, pivotes, gráficos y CSV depurado. |
| Proyecto 2 | [`Proyecto_2/`](Proyecto_2/) | Procesamiento masivo, optimización con particiones/clustering y BigQuery ML (Regresión Lineal y Boosted Trees) sobre NYC Taxi Trips 2022 (~39.6M registros), orquestado con Apache Airflow (Docker) y visualizado en Looker Studio. |

Otros archivos en la raíz:

- [`LICENSE`](LICENSE) — licencia MIT.
- [`.gitignore`](.gitignore) — entornos virtuales, `.env`, caches de Python, etc.

## Cómo empezar

1. Clonar el repositorio.
2. Entrar a la carpeta de la entrega que toque (`Practica1/`, `Tarea1/` o `Proyecto_2/`).
3. Seguir el README de esa carpeta (dependencias, Docker si aplica, y comando de ejecución).

```
SS22S2026_G1/
├── README.md              ← Este índice
├── LICENSE
├── Practica1/             ← ETL vuelos → SQL Server
├── Tarea1/                ← Limpieza y análisis con Pandas
└── Proyecto_2/            ← BigQuery, Optimización, BQML & Airflow
```

---

## 📄 Licencia

Este proyecto está bajo la Licencia **MIT**. Consulta el archivo [LICENSE](LICENSE) para más detalles.

---

## 👨‍💻 Autor

- **Enner Mendizabal** - [@Ennero](https://github.com/Ennero)  
- *Facultad de Ingeniería, Universidad de San Carlos de Guatemala.*
