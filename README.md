# Seminario de Sistemas 2 — Grupo 1

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

Otros archivos en la raíz:

- [`LICENSE`](LICENSE) — licencia MIT.
- [`.gitignore`](.gitignore) — entornos virtuales, `.env`, caches de Python, etc.

## Cómo empezar

1. Clonar el repositorio.
2. Entrar a la carpeta de la entrega que toque (`Practica1/` o `Tarea1/`).
3. Seguir el README de esa carpeta (dependencias, Docker si aplica, y comando de ejecución).

```
SS22S2026_G1/
├── README.md              ← Este índice
├── LICENSE
├── Practica1/             ← ETL vuelos → SQL Server
└── Tarea1/                ← Limpieza y análisis con Pandas
```
