# ETL Vuelos — Modelo Multidimensional en SQL Server

> **Práctica 1 · Sistemas de Soporte a la Toma de Decisiones**  
> Grupo SS22S2026_G1

---

## Tabla de contenidos

1. [Descripción del proyecto](#1-descripción-del-proyecto)
2. [Análisis del dataset real y ajustes al modelo](#2-análisis-del-dataset-real-y-ajustes-al-modelo)
3. [Arquitectura del sistema (Diagrama de flujo)](#3-arquitectura-del-sistema-diagrama-de-flujo)
4. [Diseño del modelo dimensional](#4-diseño-del-modelo-dimensional)
5. [Stack tecnológico](#5-stack-tecnológico)
6. [Estructura del repositorio](#6-estructura-del-repositorio)
7. [Instalación y ejecución](#7-instalación-y-ejecución)
8. [Reglas de transformación aplicadas](#8-reglas-de-transformación-aplicadas)
9. [Consultas analíticas](#9-consultas-analíticas)
10. [Checklist de criterios de éxito (Sección 11 del contexto)](#10-checklist-de-criterios-de-éxito)

---

## 1. Descripción del proyecto

Este proyecto implementa un **pipeline ETL completo** en Python que:

1. **Extrae** un dataset crudo de ~10 000 registros de vuelos (CSV con 26 columnas y múltiples problemas de calidad).
2. **Transforma** los datos: limpieza, homologación, tipado correcto, y construcción de un **esquema estrella** con 6 dimensiones y una tabla de hechos.
3. **Carga** el modelo en **SQL Server 2022** corriendo en Docker.
4. Permite **consultas analíticas** de BI (rutas populares, distribución por género, volumen temporal, ranking de aerolíneas, precios, etc.).

El sistema es **modular**, **trazable** (logging a archivo y consola), **idempotente** (re-ejecución sin duplicados) y **reproducible** (levantable desde cero con Docker + venv).

---

## 2. Análisis del dataset real y ajustes al modelo

### 2.1 Hallazgos del dataset (`dataset_vuelos_crudo.csv`)

| Dimensión | Detalle |
|---|---|
| Filas | 10 000 |
| Columnas | 26 |
| Vuelos cancelados | ~560 (arrival_datetime, duration_min y delay_min nulos) |
| Formatos de fecha | Múltiples: `DD/MM/YYYY HH:MM`, `MM-DD-YYYY HH:MM AM/PM` |
| Variantes de género | 12 variantes (M, m, Masculino, masculino, F, f, Femenino, femenino, X, x, NoBinario, nobinario) |
| Variantes de aerolínea | 23 strings para solo 12 aerolíneas (capitalización inconsistente) |
| Aeropuertos en minúscula | Ej: `jfk` → normalizar a `JFK` |
| Precio con coma decimal | Ej: `77,60` → parsear correctamente |
| Monedas | 4 (USD, EUR, GTQ, MXN) → se usa `ticket_price_usd_est` |
| Estados de vuelo | 4: ON_TIME, CANCELLED, DELAYED, DIVERTED |

### 2.2 Adaptaciones al modelo propuesto

El modelo es el punto de partida. Los siguientes ajustes se hicieron al encontrar el dataset real:

| Cambio | Justificación |
|---|---|
| **`DimAeropuerto` sin ciudad/país** | El CSV solo contiene código IATA de aeropuerto, sin ciudad ni país. Se modela solo con `codigo_iata`. |
| **`DimClase` (nueva)** | `cabin_class` y `aircraft_type` están en el CSV y agregan valor analítico. Se crea dimensión separada en lugar de atributo degenerado. |
| **`DimEstado` (nueva)** | 4 estados de vuelo distintos (ON_TIME / CANCELLED / DELAYED / DIVERTED) ameritan dimensión para filtros eficientes. |
| **Métrica `retraso_minutos`** | `delay_min` disponible directamente en el dataset. Se agrega como métrica en FactVuelos. |
| **Métrica `total_equipaje`** | `bags_total` disponible. Se agrega como métrica. |
| **Atributos degenerados** | `canal_venta` y `metodo_pago` se conservan en FactVuelos (cardinalidad baja, no amerita dimensión propia). |

---

## 3. Arquitectura del sistema (Diagrama de flujo)

![Diagrama de flujo del ETL](./img/diagrama_flujo.png)

```mermaid
flowchart TD
    A[dataset_vuelos_crudo.csv] --> B[EXTRACT<br/>extract/extractor.py]
    B --> C[(data/raw/)]
    C --> D[TRANSFORM<br/>transform/cleaner.py<br/>transform/standardizer.py]
    D --> E[(data/processed/)]
    E --> F[LOAD<br/>load/loader.py]
    F --> G[(SQL Server<br/>VuelosDW — Esquema Estrella)]
    G --> H[Consultas Analíticas<br/>sql/queries/analytics.sql]
    H --> I[Indicadores de negocio]

    subgraph Orquestación
    K[main.py] --> B
    K --> D
    K --> F
    end

    L[logs/etl_YYYYMMDD.log] -.registra cada fase.-> B
    L -.-> D
    L -.-> F
```

**Flujo paso a paso:**

1. **Extract**: `main.py` invoca `extract/extractor.py`, que lee el CSV, valida el esquema mínimo y guarda un snapshot con timestamp en `data/raw/`.
2. **Transform (Limpieza)**: `transform/cleaner.py` elimina duplicados, normaliza texto, homologa géneros (12 variantes → M/F/OTRO), parsea fechas en múltiples formatos, convierte tipos y rechaza filas inválidas con log.
3. **Transform (Estandarización)**: `transform/standardizer.py` construye los 6 DataFrames de dimensión y `FactVuelos` con llaves subrogadas y FK resueltas.
4. **Load**: `load/loader.py` crea la BD si no existe, ejecuta el DDL, y carga en orden (dimensiones → hechos) con TRUNCATE + INSERT (idempotente).
5. **Logging**: cada fase escribe al mismo archivo `logs/etl_YYYYMMDD.log` y a consola con nivel configurable.

---

## 4. Diseño del modelo dimensional

### Diagrama del modelo estrella

![Modelo dimensional — Esquema Estrella](./img/modelo_dimensional.png)

### Descripción del grano

**Un registro por vuelo reservado/realizado.** Cada fila de `FactVuelos` corresponde a un vuelo único (identificado por `numero_vuelo` como atributo degenerado) con su pasajero asociado.

### Tablas de dimensión

| Tabla | PK | Columnas clave | Descripción |
|---|---|---|---|
| **DimFecha** | `id_fecha` | fecha, dia, mes, anio, trimestre, dia_semana, es_fin_semana | Calendario de fechas de salida |
| **DimPasajero** | `id_pasajero` | passenger_uuid, genero, edad, rango_etario, nacionalidad | Perfil del pasajero |
| **DimAerolinea** | `id_aerolinea` | codigo_iata, nombre_aerolinea | Aerolínea operadora |
| **DimAeropuerto** | `id_aeropuerto` | codigo_iata | Aeropuertos (rol-playing: origen y destino) |
| **DimClase** | `id_clase` | clase_cabina, tipo_aeronave | Clase de cabina × tipo de aeronave |
| **DimEstado** | `id_estado` | estado_vuelo, descripcion_estado | Estado del vuelo (ON_TIME/CANCELLED/DELAYED/DIVERTED) |

### Tabla de hechos

| Columna | Tipo | Descripción |
|---|---|---|
| `id_vuelo` | INT IDENTITY | PK surrogate |
| `id_fecha` | INT FK | → DimFecha |
| `id_pasajero` | INT FK | → DimPasajero |
| `id_aerolinea` | INT FK | → DimAerolinea |
| `id_origen` | INT FK | → DimAeropuerto (rol: origen) |
| `id_destino` | INT FK | → DimAeropuerto (rol: destino) |
| `id_clase` | INT FK | → DimClase |
| `id_estado` | INT FK | → DimEstado |
| `numero_vuelo` | VARCHAR | Atributo degenerado |
| `duracion_minutos` | INT | Métrica |
| `precio_usd` | DECIMAL(10,2) | Métrica |
| `retraso_minutos` | INT | Métrica |
| `total_equipaje` | TINYINT | Métrica |
| `canal_venta` | VARCHAR | Atributo degenerado |
| `metodo_pago` | VARCHAR | Atributo degenerado |

---

## 5. Stack tecnológico

| Elemento | Especificación |
|---|---|
| Lenguaje | Python 3.10+ |
| BD | Microsoft SQL Server 2022 (Docker) |
| ORM / Conexión | SQLAlchemy 2.0 + pyodbc |
| Manipulación datos | pandas 2.0 |
| Configuración | python-dotenv |
| Contenedor | Docker + docker-compose |
| Testing | pytest |

---

## 6. Estructura del repositorio

```
SS22S2026_G1/
└── Practica1/
    ├── README.md                    ← Este archivo
    ├── requirements.txt
    ├── .env.example                 ← Plantilla de variables de entorno
    ├── .gitignore
    ├── docker-compose.yml           ← SQL Server 2022 en Docker
    ├── main.py                      ← Orquestador del ETL
    ├── config/
    │   └── settings.py              ← Carga .env y construye connection strings
    ├── extract/
    │   └── extractor.py             ← Lectura y validación del CSV
    ├── transform/
    │   ├── cleaner.py               ← Limpieza y homologación
    │   └── standardizer.py          ← Construcción de dimensiones y hechos
    ├── load/
    │   └── loader.py                ← Carga a SQL Server (dims → hechos)
    ├── sql/
    │   ├── ddl/
    │   │   └── create_model.sql     ← DDL del esquema estrella
    │   └── queries/
    │       └── analytics.sql        ← 10 consultas analíticas
    ├── data/
    │   ├── raw/                     ← Snapshots del CSV original (trazabilidad)
    │   └── processed/               ← CSV limpio pre-carga (debug)
    ├── img/
    │   ├── diagrama_flujo.png
    │   ├── modelo_dimensional.png
    │   ├── consulta1.png
    │   ├── consulta2.png
    │   ├── consulta3.png
    │   ├── consulta4.png
    │   ├── consulta5.png
    │   ├── consulta6.png
    │   ├── consulta7.png
    │   ├── consulta8.png
    │   ├── consulta9.png
    │   └── consulta10.png
    ├── logs/
    │   └── etl_YYYYMMDD.log         ← Generado automáticamente
    └── tests/
        └── test_transform.py        ← Pruebas unitarias
```

---

## 7. Instalación y ejecución

### Requisitos previos

- Docker Desktop (o Docker Engine + docker-compose)
- Python 3.10 o superior
- ODBC Driver 18 for SQL Server ([Descarga Microsoft](https://learn.microsoft.com/es-es/sql/connect/odbc/download-odbc-driver-for-sql-server))

---

### Paso 1 — Clonar el repositorio

```bash
git clone <URL_DEL_REPO>
cd SS22S2026_G1/Practica1
```

---

### Paso 2 — Configurar variables de entorno

```bash
cp .env.example .env
```

Editar `.env` con los valores reales (la contraseña debe coincidir con la del `docker-compose.yml`):

```env
DB_SERVER=localhost,1433
DB_NAME=VuelosDW
DB_USER=sa
DB_PASSWORD=TuPasswordSegura123!
DB_DRIVER=ODBC Driver 18 for SQL Server
RAW_DATA_PATH=dataset_vuelos_crudo.csv
LOG_LEVEL=INFO
```

> **Nunca subas el archivo `.env` al repositorio.** Está en `.gitignore`.

---

### Paso 3 — Levantar SQL Server con Docker

```bash
docker compose up -d
```

Verificar que el contenedor esté saludable (esperar ~30-60 s):

```bash
docker compose ps
# Debe mostrar: ss2_sqlserver   Up (healthy)
```

> **Apple Silicon (M1/M2/M3)**: cambiar la imagen en `docker-compose.yml` a `mcr.microsoft.com/azure-sql-edge:latest`

---

### Paso 4 — Crear entorno virtual e instalar dependencias

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

---

### Paso 5 — Ejecutar el pipeline ETL

```bash
python main.py
```

El proceso realiza automáticamente:
1. Lee `dataset_vuelos_crudo.csv`
2. Limpia y transforma los datos
3. Crea la base de datos `VuelosDW` y el esquema estrella en SQL Server
4. Carga todas las tablas

El log completo se guarda en `logs/etl_YYYYMMDD.log`.

---

### Paso 6 — Ejecutar las consultas analíticas

Conectarse a SQL Server con cualquier cliente compatible (Azure Data Studio, DBeaver, SSMS) con:

| Campo | Valor |
|---|---|
| Servidor | `localhost,1433` |
| Usuario | `sa` |
| Contraseña | La definida en `.env` |
| Base de datos | `VuelosDW` |

Luego ejecutar `sql/queries/analytics.sql`.

---

### Paso 7 — Ejecutar pruebas unitarias (opcional)

```bash
pytest tests/ -v
```

---

### Reiniciar desde cero

```bash
# Detener y eliminar el contenedor y su volumen
docker compose down -v

# Volver a levantar
docker compose up -d

# Re-ejecutar el ETL
python main.py
```

---

## 8. Reglas de transformación aplicadas

| Regla | Implementación |
|---|---|
| Eliminar duplicados exactos | `df.drop_duplicates()` en `cleaner.py` |
| Normalizar texto (trim + uppercase) | Aeropuertos, status, clase, canal, moneda |
| Homologar género | 12 variantes → M / F / OTRO (`GENDER_MAP` dict) |
| Homologar nombre aerolínea | 23 strings → 12 nombres canónicos (Title Case) |
| Parseo de fechas múltiples formatos | `DD/MM/YYYY HH:MM`, `MM-DD-YYYY HH:MM AM/PM`, ISO 8601, etc. |
| Convertir precio con coma decimal | `77,60` → `77.60` |
| Usar precio USD estimado | Se usa `ticket_price_usd_est` (multi-moneda ya convertida) |
| Rellenar nulos en vuelos cancelados | `duration_min=0`, `delay_min=0` |
| Calcular `rango_etario` | Bins: <18, 18-25, 26-35, 36-50, 51-65, 65+ |
| Registrar rechazos en log | Motivo + conteo en `logs/etl_YYYYMMDD.log` |
| Validar FK antes de cargar | Filas con FK nulas excluidas de FactVuelos |

---

## 9. Consultas analíticas

El archivo `sql/queries/analytics.sql` incluye las 10 consultas siguientes:

| # | Consulta | Indicador |
|---|---|---|
| 1 | Conteo por tabla | Validación de carga completa |
| 2 | Top 5 destinos más frecuentes | (excluye CANCELLED) |
| 3 | Distribución por género | Pasajeros únicos + vuelos |
| 4 | Vuelos por mes/año | Volumen temporal + ingresos |
| 5 | Aerolíneas por volumen (Top 10) | Con ingresos y cancelaciones |
| 6 | Retraso promedio por estado de vuelo | Promedio y máximo |
| 7 | Precio promedio por ruta (Top 20) | Min/Avg/Max USD |
| 8 | Precio por aerolínea y clase de cabina | Análisis cruzado |
| 9 | Tasa de cancelación por aerolínea | Porcentaje de cancelados |
| 10 | Distribución rango etario × clase | Perfil de pasajero |

---

## 10. Resultados Obtenidos

A continuación se presentan los resultados obtenidos al ejecutar las 10 consultas analíticas especificadas en el archivo `sql/queries/analytics.sql`:

### 10.1 Consulta 1: Conteo por tabla
Esta consulta realiza un conteo del total de registros cargados en cada una de las tablas de dimensiones y en la tabla de hechos para verificar la consistencia del proceso de carga completa.
![Conteo por tabla](./img/consulta1.png)

### 10.2 Consulta 2: Top 5 destinos más frecuentes
Muestra los 5 aeropuertos de destino más populares (código IATA) basándose en el volumen total de vuelos (excluyendo vuelos cancelados).
![Top 5 destinos](./img/consulta2.png)

### 10.3 Consulta 3: Distribución por género
Analiza la cantidad de pasajeros únicos y el número total de vuelos realizados por cada género registrado (M, F, OTRO).
![Distribución por género](./img/consulta3.png)

### 10.4 Consulta 4: Vuelos por mes/año
Presenta un histórico mensual del volumen de vuelos y los ingresos totales acumulados, permitiendo identificar la evolución del negocio a lo largo del tiempo.
![Vuelos por mes/año](./img/consulta4.png)

### 10.5 Consulta 5: Aerolíneas por volumen (Top 10)
Lista el Top 10 de aerolíneas con mayor volumen de vuelos operados, desglosando sus ingresos totales generados y la cantidad de vuelos cancelados asociados.
![Aerolíneas por volumen](./img/consulta5.png)

### 10.6 Consulta 6: Retraso promedio por estado de vuelo
Calcula el promedio y el retraso máximo registrado en minutos para cada uno de los estados de vuelo posibles.
![Retraso promedio](./img/consulta6.png)

### 10.7 Consulta 7: Precio promedio por ruta (Top 20)
Identifica las 20 rutas aéreas (aeropuerto de origen a aeropuerto de destino) con mayor facturación promedio, mostrando además los límites mínimo y máximo de precio en USD.
![Precio promedio por ruta](./img/consulta7.png)

### 10.8 Consulta 8: Precio por aerolínea y clase de cabina
Realiza un cruce dimensional para evaluar los costos promedio y totales por tipo de boleto (clase y tipo de avión) para cada aerolínea.
![Precio por aerolínea y clase](./img/consulta8.png)

### 10.9 Consulta 9: Tasa de cancelación por aerolínea
Determina el porcentaje de vuelos cancelados para cada una de las aerolíneas con el fin de medir la tasa de cancelación general.
![Tasa de cancelación](./img/consulta9.png)

### 10.10 Consulta 10: Distribución rango etario × clase
Muestra el perfil demográfico de los viajeros mediante el cruce de los distintos rangos de edad con el tipo de clase en el que viajaron.
![Rango etario vs clase](./img/consulta10.png)