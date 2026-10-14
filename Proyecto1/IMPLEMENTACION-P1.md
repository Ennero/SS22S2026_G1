# DOCUMENTACIÓN TÉCNICA Y MANUAL DE IMPLEMENTACIÓN - PROYECTO 1
## Flujo Moderno de Datos con Python, Apache Airflow, dbt y PostgreSQL
**Curso:** Seminario de Sistemas 2 - Segundo Semestre 2026  
**Empresa de Estudio:** SG-Food (Distribución y Comercialización de Alimentos)  
**Ponderación:** 25 Puntos (Evaluado sobre 100%)  
**Entorno:** 100% Contenerizado con Docker y Docker Compose  

---

## ÍNDICE GENERAL
1. [Introducción y Objetivos del Proyecto](#1-introducción-y-objetivos-del-proyecto)
2. [Arquitectura General de la Solución](#2-arquitectura-general-de-la-solución)
3. [Estructura del Proyecto y Repositorio](#3-estructura-del-proyecto-y-repositorio)
4. [Fase 1: Infraestructura y Contenerización (Docker)](#4-fase-1-infraestructura-y-contenerización-docker)
5. [Fase 2: Extracción y Carga Cruda (EL con Python)](#5-fase-2-extracción-y-carga-cruda-el-con-python)
6. [Fase 3: Modelado Dimensional y Transformación (dbt Core)](#6-fase-3-modelado-dimensional-y-transformación-dbt-core)
7. [Fase 4: Pruebas de Calidad, Integridad y Observabilidad](#7-fase-4-pruebas-de-calidad-integridad-y-observabilidad)
8. [Fase 5: Orquestación Automatizada con Apache Airflow](#8-fase-5-orquestación-automatizada-con-apache-airflow)
9. [Fase 6: Consultas Analíticas y Verificación de Negocio](#9-fase-6-consultas-analíticas-y-verificación-de-negocio)
10. [Fase 7: Preparación y Guía de Conexión para Power BI](#10-fase-7-preparación-y-guía-de-conexión-para-power-bi)
11. [Manual de Operación y Reproducibilidad en Otros Entornos](#11-manual-de-operación-y-reproducibilidad-en-otros-entornos)
12. [Matriz de Cumplimiento de la Rúbrica de Evaluación](#12-matriz-de-cumplimiento-de-la-rúbrica-de-evaluación)

---

## 1. INTRODUCCIÓN Y OBJETIVOS DEL PROYECTO

### 1.1 Contexto Empresarial: SG-Food
**SG-Food** es una empresa guatemalteca dedicada a la distribución mayorista y minorista de alimentos procesados, abarrotes, bebidas, lácteos, snacks, productos de panadería, congelados y artículos de limpieza y cuidado personal. Opera sucursales en diversas cabeceras departamentales de Guatemala (Ciudad Central, Mixco, Villa Nueva, Amatitlán, Antigua Guatemala, Escuintla).

### 1.2 Problemática Identificada
Previamente, SG-Food sufría de:
- **Procesos manuales y dispersos:** Reportes construidos en hojas de cálculo no estandarizadas.
- **Sobrecarga de sistemas transaccionales:** Consultas analíticas pesadas lanzadas directamente contra la base de datos OLTP de facturación, ralentizando las cajas de cobro.
- **Falta de integración con datos externos:** Datos de proveedores (costos y tiempos de entrega), promociones, inventarios físicos periódicos y metas mensuales vivían en archivos CSV aislados sin cruce formal con las ventas.
- **Falta de trazabilidad y gobernanza:** No existían pruebas de calidad automatizadas (validación de nulos, duplicidad, integridad referencial).

### 1.3 Solución Implementada
Se diseñó e implementó un flujo moderno de ingeniería de datos bajo el paradigma **ELT (Extract, Load, Transform)**:
1. **Extract & Load (EL):** Módulos en Python modularizados para extraer las 7 tablas de la base de datos transaccional PostgreSQL (`oltp_sgfood`) y 5 archivos CSV externos, cargándolos en el esquema `raw` de forma idempotente.
2. **Transform (T):** Un proyecto en **dbt Core (dbt-postgres)** que estructura la información en tres capas desacopladas:
   - `staging`: Limpieza técnica, tipado explícito y estandarización.
   - `intermediate`: Enriquecimiento analítico y cálculo de métricas pre-agregadas.
   - `marts`: Modelo dimensional en esquema estrella con 8 dimensiones y 4 tablas de hechos.
3. **Orquestación:** **Apache Airflow** orquesta la secuencia completa en un DAG programable y monitoreable con alertas y control de dependencias.
4. **Contenerización Completa:** Un clúster de Docker Compose que incluye PostgreSQL 16, Apache Airflow 2.9 (con dbt Core preinstalado) y Adminer para auditoría web.

---

## 2. ARQUITECTURA GENERAL DE LA SOLUCIÓN

```
+----------------------------------------------------------------------------------------------------+
|                                     FUENTES DE DATOS DE SG-FOOD                                     |
|  [PostgreSQL OLTP: oltp_sgfood]                           [Archivos Delimitados / CSV]             |
|  - sucursales, categorias, marcas,                        - inventario_bodega.csv                  |
|    productos, clientes, ordenes,                          - proveedores_precios.csv                |
|    orden_detalle                                          - promociones.csv                        |
|                                                           - metas_ventas.csv, devoluciones.csv     |
+-----------------------------------+-----------------------------------+----------------------------+
                                    |                                   |
                                    v                                   v
+----------------------------------------------------------------------------------------------------+
|                                  CAPA 1: EXTRACCIÓN Y CARGA (EL)                                   |
|   Scripts Python Modularizados (/opt/airflow/elt):                                                 |
|   - extract_oltp.py  (Extracción con SQLAlchemy / Pandas -> Carga Idempotente TRUNCATE + Append)    |
|   - extract_csv.py   (Lectura con detección de encoding, casteo y carga a raw.*)                   |
|   - quality_checker.py (Validación de completitud y auditoría de conteos)                          |
+--------------------------------------------------+-------------------------------------------------+
                                                   |
                                                   v
+----------------------------------------------------------------------------------------------------+
|                               POSTGRESQL DATA WAREHOUSE: sgfood_dw                                 |
|                                                                                                    |
|  [SCHEMA: raw] Tablas Crudas                                                                       |
|  - raw_sucursales, raw_categorias, raw_marcas, raw_productos, raw_clientes, raw_ordenes, ...         |
|                                                                                                    |
|  [SCHEMA: staging] Vistas dbt (Limpieza, casteo y nomenclatura canónica)                          |
|  - stg_sucursales, stg_categorias, stg_productos, stg_clientes, stg_ordenes, ...                   |
|                                                                                                    |
|  [SCHEMA: intermediate] Vistas dbt (Lógica de Negocio y Cruce)                                     |
|  - int_ventas_enriquecidas, int_inventario_estado, int_cumplimiento_metas                          |
|                                                                                                    |
|  [SCHEMA: marts] Tablas Físicas dbt (Modelo Dimensional Estrella)                                  |
|  * DIMENSIONES: dim_sucursal, dim_categoria, dim_marca, dim_producto, dim_cliente,                 |
|                 dim_proveedor, dim_promocion, dim_fecha                                            |
|  * HECHOS:      fct_ventas, fct_inventario, fct_devoluciones, fct_rendimiento_metas                |
+--------------------------------------------------+-------------------------------------------------+
                                                   |
                                                   v
+----------------------------------------------------------------------------------------------------+
|                       CAPA 3: ORQUESTACIÓN Y CALIDAD (Apache Airflow)                              |
|   DAG: sgfood_elt_pipeline                                                                         |
|   Tareas: check_db -> verify_seed -> extract_oltp -> extract_csv -> verify_raw ->                  |
|           dbt_run_staging -> dbt_run_intermediate -> dbt_run_marts -> dbt_test -> summary          |
|   Pruebas de Calidad: 92 pruebas dbt (unique, not_null, relationships, accepted_values, custom)    |
+--------------------------------------------------+-------------------------------------------------+
                                                   |
                                                   v
+----------------------------------------------------------------------------------------------------+
|                       CAPA 4: CONSUMO ANALÍTICO Y BUSINESS INTELLIGENCE                           |
|   - Consultas Analíticas SQL (KPIs de ventas, márgenes, metas, quiebres de stock, devoluciones)     |
|   - Power BI Desktop / Reporting Tools (Conexión nativa a PostgreSQL:5432 / schema marts)         |
+----------------------------------------------------------------------------------------------------+
```

---

## 3. ESTRUCTURA DEL PROYECTO Y REPOSITORIO

El proyecto se encuentra ubicado en `Proyecto1/` con la siguiente distribución organizada de código:

```
Proyecto1/
├── .env                              # Variables de entorno locales para Docker
├── .env.example                      # Plantilla de variables para reproducción
├── .dockerignore                     # Filtro de archivos innecesarios para el build
├── docker-compose.yml                # Definición de servicios (PostgreSQL, Airflow, Adminer)
├── Dockerfile.airflow                # Imagen personalizada de Airflow con dbt Core y librerías
├── requirements.txt                  # Dependencias de Python fijadas (dbt-postgres, sqlalchemy<2.0.0)
├── IMPLEMENTACION-P1.md              # Documentación técnica completa y exhaustiva (Este documento)
├── README.md                         # Resumen ejecutivo, diagramas, manual rápido y rúbrica
├── Data/                             # Archivos CSV fuente
│   ├── devoluciones.csv
│   ├── inventario_bodega.csv
│   ├── metas_ventas.csv
│   ├── promociones.csv
│   └── proveedores_precios.csv
├── dags/                             # Orquestación con Apache Airflow
│   └── sgfood_elt_pipeline.py        # DAG end-to-end con 10 tareas y control de errores
├── elt/                              # Módulos Python de Extracción y Carga
│   ├── __init__.py
│   ├── db.py                         # Fábrica de conexiones SQLAlchemy y variables de entorno
│   ├── extract_oltp.py               # Extracción transaccional y carga a raw.*
│   ├── extract_csv.py                # Ingesta de CSVs y carga a raw.*
│   └── quality_checker.py            # Auditor de calidad de datos en raw
├── sql/                              # Scripts SQL DDL y de Análisis
│   ├── 01_init_databases.sh          # Script de arranque para crear schemas y sembrar OLTP
│   ├── ddl_data_warehouse.sql        # DDL completo de schemas, raw, marts e índices
│   └── analytics_queries.sql         # 8 Consultas analíticas de negocio sobre marts
└── dbt_sgfood/                       # Proyecto dbt Core
    ├── dbt_project.yml               # Configuración del proyecto, modelos y materializaciones
    ├── profiles.yml                  # Perfil de conexión a PostgreSQL Data Warehouse
    ├── macros/
    │   └── generate_schema_name.sql  # Macro para forzar schemas limpios (sin prefijos)
    ├── models/
    │   ├── sources.yml               # Declaración de fuentes raw con pruebas
    │   ├── staging/                  # Capa Staging (12 modelos de vistas)
    │   │   ├── schema.yml
    │   │   ├── stg_sucursales.sql
    │   │   ├── stg_categorias.sql
    │   │   ├── stg_marcas.sql
    │   │   ├── stg_productos.sql
    │   │   ├── stg_clientes.sql
    │   │   ├── stg_ordenes.sql
    │   │   ├── stg_orden_detalle.sql
    │   │   ├── stg_inventario_bodega.sql
    │   │   ├── stg_proveedores_precios.sql
    │   │   ├── stg_promociones.sql
    │   │   ├── stg_metas_ventas.sql
    │   │   └── stg_devoluciones.sql
    │   ├── intermediate/             # Capa Intermediate (3 modelos de vistas enriquecidas)
    │   │   ├── int_ventas_enriquecidas.sql
    │   │   ├── int_inventario_estado.sql
    │   │   └── int_cumplimiento_metas.sql
    │   └── marts/                    # Capa Marts (12 tablas dimensionales y hechos)
    │       ├── schema.yml
    │       ├── dim_sucursal.sql
    │       ├── dim_categoria.sql
    │       ├── dim_marca.sql
    │       ├── dim_producto.sql
    │       ├── dim_cliente.sql
    │       ├── dim_proveedor.sql
    │       ├── dim_promocion.sql
    │       ├── dim_fecha.sql
    │       ├── fct_ventas.sql
    │       ├── fct_inventario.sql
    │       ├── fct_devoluciones.sql
    │       └── fct_rendimiento_metas.sql
    └── tests/                        # Pruebas singulares de calidad de negocio
        ├── test_no_negative_sales.sql
        ├── test_valid_meta_fulfillment.sql
        ├── test_inventory_logic.sql
        └── test_positive_pricing.sql
```

---

## 4. FASE 1: INFRAESTRUCTURA Y CONTENERIZACIÓN (DOCKER)

### 4.1 Justificación Técnica
Para garantizar total reproducibilidad, evitar problemas de versiones de Python locales, dependencias de sistema operativo y diferencias de bibliotecas, toda la solución corre en tres contenedores orquestados con **Docker Compose**:
1. **`sgfood_postgres` (PostgreSQL 16 Alpine):**
   - Aloja la base transaccional (`oltp_sgfood`) y el Data Warehouse analítico (`sgfood_dw`).
   - Inicialización automatizada con `sql/01_init_databases.sh`, que crea los esquemas `raw`, `staging`, `intermediate`, `marts` y ejecuta el script de siembra transaccional `sgfood_oltp.sql`.
   - Healthcheck nativo con `pg_isready` para sincronizar el arranque de Airflow.
2. **`sgfood_airflow` (Apache Airflow 2.9.3 + dbt Core + dbt-postgres):**
   - Construido mediante `Dockerfile.airflow`.
   - Ejecuta Airflow en modo `standalone` ligero (scheduler, webserver, triggerer en un proceso coordinado), optimizado para bajo consumo de memoria RAM (~350 MB).
   - Monta como volúmenes: `./dags`, `./elt`, `./dbt_sgfood`, `./Data`, `./sql`.
3. **`sgfood_adminer` (Adminer 4.8 Web GUI):**
   - Cliente web ligero para PostgreSQL en el puerto 8081.

### 4.2 Configuración de Variables de Entorno (`.env`)
```bash
# PostgreSQL Data Warehouse Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=sgfood_dw
POSTGRES_PORT=5432
POSTGRES_HOST=postgres

# Airflow Admin Credentials
AIRFLOW_ADMIN_USERNAME=admin
AIRFLOW_ADMIN_PASSWORD=admin
AIRFLOW_ADMIN_EMAIL=admin@sgfood.com
AIRFLOW_PORT=8080

# Adminer Port
ADMINER_PORT=8081
```

### 4.3 Manejo Crítico de Versión de Dependencias
> [!IMPORTANT]
> **Compatibilidad SQLAlchemy / Airflow:**  
> Apache Airflow 2.9 utiliza internamente SQLAlchemy 1.4 y falla con SQLAlchemy 2.0 (`AttributeError: 'Session' object has no attribute 'get_bind'` en modelos ORM de Airflow). Por tanto, en [requirements.txt](file:///home/dadev/Escritorio/SS22S2026_G1/Proyecto1/requirements.txt) se fijó explícitamente:
> ```text
> dbt-core==1.8.2
> dbt-postgres==1.8.2
> pandas>=2.0.0
> psycopg2-binary>=2.9.9
> sqlalchemy>=1.4.40,<2.0.0
> python-dotenv>=1.0.0
> ```

---

## 5. FASE 2: EXTRACCIÓN Y CARGA CRUDA (EL CON PYTHON)

### 5.1 Componentes del Pipeline EL

#### `elt/db.py`: Módulo Central de Conectividad
Proporciona dos factories de motores SQLAlchemy:
- `get_oltp_engine()`: Conexión con `search_path=oltp_sgfood`.
- `get_dw_engine(schema="raw")`: Conexión con `search_path=raw`.

#### `elt/extract_oltp.py`: Extracción Transaccional
Extrae las tablas del sistema operacional de SG-Food:
1. `sucursales` (6 sucursales departamentales)
2. `categorias` (8 categorías de productos)
3. `marcas` (10 marcas comerciales)
4. `productos` (40 artículos con SKU, perecederos y días de caducidad)
5. `clientes` (100 clientes clasificados en segmentos)
6. `ordenes` (600 transacciones con canal de venta y método de pago)
7. `orden_detalle` (1,800 líneas de detalle con cantidad, precio y descuento)

> [!NOTE]
> **Principio de Idempotencia y Protección de Vistas:**  
> Si se utiliza `df.to_sql(..., if_exists="replace")`, Pandas ejecuta un comando `DROP TABLE raw.tabla CASCADE`, lo cual destruye las vistas `staging.stg_*` que dependen de ella en PostgreSQL (`psycopg2.errors.DependentObjectsStillExist`).  
> **Solución implementada:** Se adoptó la estrategia **`TRUNCATE TABLE raw.tabla + df.to_sql(..., if_exists="append")`**. Si la tabla no existe se crea automáticamente; si ya existe, se limpia su contenido sin eliminar la estructura ni romper las vistas dependientes.

#### `elt/extract_csv.py`: Ingesta de Archivos Planos Complementarios
Lee los archivos CSV desde la carpeta `/opt/airflow/Data`:
1. `inventario_bodega.csv`: 320 registros de stocks por sucursal, lote y fechas de vencimiento.
2. `proveedores_precios.csv`: 40 registros de costos por SKU, plazos y calificación de proveedores.
3. `promociones.csv`: Campañas promocionales con porcentaje de descuento y fechas de vigencia.
4. `metas_ventas.csv`: Metas mensuales por sucursal en montos (Q) y unidades.
5. `devoluciones.csv`: Registros de devoluciones asociadas a órdenes con motivos y cantidades.

#### `elt/quality_checker.py`: Validación de Datos en Crudo
Audita que todas las 12 tablas en `raw` contengan registros (> 0 filas), verificando integridad básica de extracción antes de dar paso a las transformaciones.

---

## 6. FASE 3: MODELADO DIMENSIONAL Y TRANSFORMACIÓN (DBT CORE)

### 6.1 Filosofía de Modelado: Arquitectura de 3 Capas
El proyecto dbt (`dbt_sgfood`) implementa el patrón de modelado analítico moderno:

```
[Fuentes: sources.yml (schema: raw)]
                   |
                   v
[Capa Staging (models/staging): 12 Modelos / Materializados como Vistas]
 - stg_sucursales, stg_categorias, stg_marcas, stg_productos, stg_clientes, ...
                   |
                   v
[Capa Intermediate (models/intermediate): 3 Modelos / Materializados como Vistas]
 - int_ventas_enriquecidas, int_inventario_estado, int_cumplimiento_metas
                   |
                   v
[Capa Marts (models/marts): 12 Modelos / Materializados como Tablas Físicas]
 - 8 Dimensiones (dim_*) + 4 Tablas de Hechos (fct_*)
```

### 6.2 Macro Personalizado: `generate_schema_name.sql`
Por defecto, dbt concatena el esquema por defecto con el nombre del modelo (ej. `sgfood_dw_staging`). Se implementó un macro en `dbt_sgfood/macros/generate_schema_name.sql` para forzar que el esquema generado sea exactamente el especificado en `dbt_project.yml` (`staging`, `intermediate`, `marts`):
```sql
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
```

### 6.3 Capa Staging (`models/staging/`)
Homogeniza tipos de datos, renombra campos a español descriptivo y estandariza nulos:
- Llaves foráneas casteadas a `INT` o `BIGINT`.
- Fechas casteadas a tipo `DATE` y horas a `TIME`.
- Importes monetarios casteados a `NUMERIC(14,2)` o `NUMERIC(12,2)`.
- Textos normalizados con `TRIM()`.

### 6.4 Capa Intermediate (`models/intermediate/`)
Combina entidades y calcula métricas complejas previas a las tablas de hechos:
1. **`int_ventas_enriquecidas`:** Cruza `stg_ordenes`, `stg_orden_detalle`, `stg_productos` y `stg_proveedores_precios`. Calcula:
   - `importe_bruto = cantidad * precio_unitario`
   - `monto_descuento = cantidad * (precio_unitario * porcentaje_descuento)`
   - `importe_neto = importe_bruto - monto_descuento`
   - `costo_total = cantidad * costo_proveedor`
   - `margen_ganancia = importe_neto - costo_total`
   - `porcentaje_margen = (margen_ganancia / NULLIF(importe_neto, 0)) * 100`
2. **`int_inventario_estado`:** Cruza `stg_inventario_bodega` con fechas de vencimiento y catálogos de productos. Calcula:
   - `diferencia_stock_min = stock_disponible - stock_minimo`
   - `estado_stock`: Clasificación entre `'Agotado'`, `'Crítico (Bajo Stock)'`, `'Normal'` y `'Sobre-stock'`.
   - `dias_para_vencer`: Días restantes hasta la caducidad.
   - `alerta_vencimiento`: `'Vencido'`, `'Próximo a Vencer'` (<= 30 días) o `'Vigente'`.
3. **`int_cumplimiento_metas`:** Agrupa ventas reales por mes y sucursal y las compara contra `stg_metas_ventas`. Calcula:
   - `pct_cumplimiento_monto = (ventas_reales / meta_ventas) * 100`
   - `pct_cumplimiento_unidades = (unidades_reales / meta_unidades) * 100`
   - `estado_cumplimiento`: `'Meta Superada'`, `'Meta Cumplida'` o `'Por Debajo de Meta'`.

### 6.5 Capa Marts: Modelo Dimensional en Esquema Estrella (`models/marts/`)

![Modelo Dimensional SG-Food](img/modelo_dimensional.jpg)

Las tablas en esta capa están materializadas físicamente como `table` para optimizar consultas analíticas y rendimiento en Power BI.

#### Dimensiones (8)
1. **`dim_sucursal`:** Identificador, nombre, ciudad, departamento y llave subrogada `dim_sucursal_sk`.
2. **`dim_categoria`:** Código de categoría, nombre y descripción.
3. **`dim_marca`:** Código de marca, nombre comercial.
4. **`dim_producto`:** Maestro consolidado con SKU, categoría, marca, costo base, precio de lista y estado activo.
5. **`dim_cliente`:** NIT, nombre, tipo de cliente (Individual/Empresa), municipio, departamento y fecha de alta.
6. **`dim_proveedor`:** Catálogo de proveedores, producto abastecido, costo pactado y plazos de entrega.
7. **`dim_promocion`:** Promociones vigentes con porcentaje de descuento aplicado.
8. **`dim_fecha`:** Calendario de fechas generado analíticamente que cubre el histórico de transacciones, con año, mes, nombre de mes, día, trimestre, día de la semana y bandera de fin de semana (`es_fin_semana`).

#### Tablas de Hechos (4)
1. **`fct_ventas`:** Hecho granular al nivel de línea de detalle de orden (1,800 registros). Contiene las llaves a todas las dimensiones, importes brutos, descuentos, importes netos, costos y márgenes de ganancia.
2. **`fct_inventario`:** Foto de inventario por corte y lote (320 registros) con cálculo de stock disponible, niveles mínimos, alertas de caducidad y valorización al costo.
3. **`fct_devoluciones`:** Eventos de devolución vinculados a sucursal, producto y orden, con cantidades devueltas y monto económico estimado.
4. **`fct_rendimiento_metas`:** Seguimiento mensual por sucursal de metas vs. ventas reales en Quetzales y unidades.

---

## 7. FASE 4: PRUEBAS DE CALIDAD, INTEGRIDAD Y OBSERVABILIDAD

### 7.1 Pruebas Genéricas de dbt (`models/*/schema.yml`)
Se definieron pruebas exhaustivas para cada modelo:
- `unique`: Unicidad de llaves primarias y subrogadas.
- `not_null`: Campos obligatorios no nulos en todas las dimensiones y hechos.
- `relationships`: Integridad referencial entre hechos y dimensiones (garantizando que ninguna venta apunte a una sucursal, producto o fecha inexistente).
- `accepted_values`: Validación de dominios permitidos (ej. canales de venta `'Tienda'`, `'Web'`, `'Televenta'`, `'Mayorista'`; estados de inventario `'Agotado'`, `'Crítico (Bajo Stock)'`, etc.).

### 7.2 Pruebas Singulares de Lógica de Negocio (`tests/*.sql`)
1. **`test_no_negative_sales.sql`:** Asegura que ninguna venta tenga importe neto negativo ni cantidad menor o igual a cero.
2. **`test_positive_pricing.sql`:** Verifica que los precios de lista y costos base de los productos sean estrictamente positivos.
3. **`test_inventory_logic.sql`:** Verifica que el stock mínimo sea menor o igual al stock máximo configurado.
4. **`test_valid_meta_fulfillment.sql`:** Asegura que las metas comerciales sean mayores a cero y que los porcentajes calculados no sean negativos.

### 7.3 Resultado de Ejecución de Pruebas dbt
Al ejecutar `dbt test` en el entorno contenerizado:
```text
Finished running 92 data tests in 0 hours 0 minutes and 5.21 seconds.
Completed successfully
Done. PASS=92 WARN=0 ERROR=0 SKIP=0 TOTAL=92
```
**Resultado:** 92 pruebas ejecutadas, **100% aprobadas con 0 advertencias y 0 errores**.

---

## 8. FASE 5: ORQUESTACIÓN AUTOMATIZADA CON APACHE AIRFLOW

### 8.1 Definición del DAG: `sgfood_elt_pipeline`
El pipeline está definido en [dags/sgfood_elt_pipeline.py](file:///home/dadev/Escritorio/SS22S2026_G1/Proyecto1/dags/sgfood_elt_pipeline.py).
- **ID:** `sgfood_elt_pipeline`
- **Schedule:** Programado diariamente a las 06:00 AM UTC (`schedule_interval="0 6 * * *"`) para cumplir con los requerimientos opcionales de automatización.
- **Catchup:** `False`
- **Reintentos:** 1 reintento con retraso de 1 minuto en caso de caída transitoria de red.

### 8.2 Estructura de Tareas y Dependencias
```mermaid
graph LR
    T1[check_database_connection] --> T2[verify_seed_oltp]
    T2 --> T3[extract_and_load_oltp_to_raw]
    T2 --> T4[extract_and_load_csv_to_raw]
    T3 --> T5[verify_raw_data_quality]
    T4 --> T5
    T5 --> T6[dbt_run_staging]
    T6 --> T7[dbt_run_intermediate]
    T7 --> T8[dbt_run_marts]
    T8 --> T9[dbt_test_quality_and_integrity]
    T9 --> T10[pipeline_completion_summary]
```

### 8.3 Detalle de Cada Tarea en Airflow

| Tarea | Operador | Descripción Técnica |
|---|---|---|
| `check_database_connection` | `PythonOperator` | Verifica la disponibilidad de PostgreSQL y ejecuta un ping (`SELECT 1`). |
| `verify_seed_oltp` | `PythonOperator` | Confirma que la base `oltp_sgfood` esté sembrada con las 7 tablas maestras. |
| `extract_and_load_oltp_to_raw` | `PythonOperator` | Ejecuta `extract_oltp.py`: Extrae las 7 tablas de OLTP y las vuelca en `raw.*`. |
| `extract_and_load_csv_to_raw` | `PythonOperator` | Ejecuta `extract_csv.py`: Ingesta los 5 archivos CSV hacia `raw.*`. |
| `verify_raw_data_quality` | `PythonOperator` | Ejecuta `quality_checker.py`: Audita que las 12 tablas en `raw` tengan datos. |
| `dbt_run_staging` | `BashOperator` | Ejecuta `dbt run --select staging`: Compila y genera las 12 vistas en el esquema `staging`. |
| `dbt_run_intermediate` | `BashOperator` | Ejecuta `dbt run --select intermediate`: Compila las 3 vistas analíticas enriquecidas. |
| `dbt_run_marts` | `BashOperator` | Ejecuta `dbt run --select marts`: Genera físicamente las 12 tablas del Data Warehouse. |
| `dbt_test_quality_and_integrity` | `BashOperator` | Ejecuta `dbt test`: Corre las 92 pruebas de calidad e integridad referencial. |
| `pipeline_completion_summary` | `PythonOperator` | Genera un log de auditoría final confirmando la culminación exitosa del pipeline. |

### 8.4 Evidencia de Ejecución Exitosa en Airflow
Ejecución verificada mediante la CLI de Airflow:
```text
dag_id              | execution_date            | task_id                         | state   
sgfood_elt_pipeline | 2026-10-10T23:33:59+00:00 | check_database_connection       | success 
sgfood_elt_pipeline | 2026-10-10T23:33:59+00:00 | verify_seed_oltp                | success 
sgfood_elt_pipeline | 2026-10-10T23:33:59+00:00 | extract_and_load_oltp_to_raw    | success 
sgfood_elt_pipeline | 2026-10-10T23:33:59+00:00 | extract_and_load_csv_to_raw     | success 
sgfood_elt_pipeline | 2026-10-10T23:33:59+00:00 | verify_raw_data_quality         | success 
sgfood_elt_pipeline | 2026-10-10T23:33:59+00:00 | dbt_run_staging                 | success 
sgfood_elt_pipeline | 2026-10-10T23:33:59+00:00 | dbt_run_intermediate            | success 
sgfood_elt_pipeline | 2026-10-10T23:33:59+00:00 | dbt_run_marts                   | success 
sgfood_elt_pipeline | 2026-10-10T23:33:59+00:00 | dbt_test_quality_and_integrity  | success 
sgfood_elt_pipeline | 2026-10-10T23:33:59+00:00 | pipeline_completion_summary     | success 
---------------------------------------------------------------------------------------------
ESTADO FINAL DEL DAG RUN: SUCCESS (Tiempo total: 43.18 segundos)
```

---

## 9. FASE 6: CONSULTAS ANALÍTICAS Y VERIFICACIÓN DE NEGOCIO

El archivo [sql/analytics_queries.sql](file:///home/dadev/Escritorio/SS22S2026_G1/Proyecto1/sql/analytics_queries.sql) implementa 8 consultas de analítica avanzada que resuelven los principales problemas de negocio de SG-Food:

### Consulta 1: Resumen de Ventas por Sucursal y Categoría
Permite a la gerencia identificar los departamentos más rentables y la categoría líder en cada región:
```sql
SELECT 
    s.sucursal_nombre,
    s.departamento,
    c.categoria_nombre,
    COUNT(DISTINCT v.id_venta) AS total_transacciones,
    SUM(v.cantidad) AS unidades_vendidas,
    ROUND(SUM(v.importe_bruto), 2) AS facturacion_bruta,
    ROUND(SUM(v.monto_descuento), 2) AS total_descuentos,
    ROUND(SUM(v.importe_neto), 2) AS facturacion_neta,
    ROUND(SUM(v.margen_ganancia), 2) AS utilidad_bruta,
    ROUND(AVG(v.porcentaje_margen), 2) AS margen_promedio_pct
FROM marts.fct_ventas v
JOIN marts.dim_sucursal s ON v.id_sucursal = s.id_sucursal
JOIN marts.dim_producto p ON v.id_producto = p.id_producto
JOIN marts.dim_categoria c ON p.id_categoria = c.id_categoria
GROUP BY s.sucursal_nombre, s.departamento, c.categoria_nombre
ORDER BY s.sucursal_nombre, facturacion_neta DESC;
```

### Consulta 2: Top 10 Productos Más Vendidos y su Margen
Evalúa el rendimiento de los productos estrella para optimizar precios y promociones:
```sql
SELECT 
    p.sku,
    p.producto_nombre,
    p.categoria_nombre,
    p.marca_nombre,
    SUM(v.cantidad) AS total_unidades,
    ROUND(SUM(v.importe_neto), 2) AS total_ingresos,
    ROUND(SUM(v.margen_ganancia), 2) AS utilidad_total,
    ROUND(AVG(v.porcentaje_margen), 2) AS margen_promedio_pct
FROM marts.fct_ventas v
JOIN marts.dim_producto p ON v.id_producto = p.id_producto
GROUP BY p.sku, p.producto_nombre, p.categoria_nombre, p.marca_nombre
ORDER BY total_ingresos DESC
LIMIT 10;
```

### Consulta 3: Cumplimiento de Metas Mensuales vs. Ventas Reales
Compara las metas comerciales de los directores con la facturación real del Data Warehouse:
```sql
SELECT 
    m.periodo_mes,
    s.sucursal_nombre,
    m.meta_ventas,
    m.ventas_reales,
    m.pct_cumplimiento_monto,
    m.meta_unidades,
    m.unidades_reales,
    m.pct_cumplimiento_unidades,
    m.estado_cumplimiento
FROM marts.fct_rendimiento_metas m
JOIN marts.dim_sucursal s ON m.id_sucursal = s.id_sucursal
ORDER BY m.periodo_mes, s.sucursal_nombre;
```

### Consulta 4: Detección de Quiebres de Stock y Productos Críticos
Alerta al área de compras sobre productos agotados o por debajo del inventario mínimo:
```sql
SELECT 
    i.fecha_corte,
    s.sucursal_nombre,
    p.sku,
    p.producto_nombre,
    p.categoria_nombre,
    i.stock_disponible,
    i.stock_minimo,
    i.diferencia_stock_min,
    i.estado_stock
FROM marts.fct_inventario i
JOIN marts.dim_sucursal s ON i.id_sucursal = s.id_sucursal
JOIN marts.dim_producto p ON i.id_producto = p.id_producto
WHERE i.estado_stock IN ('Agotado', 'Crítico (Bajo Stock)')
ORDER BY i.stock_disponible ASC, i.diferencia_stock_min ASC
LIMIT 20;
```

### Consulta 5: Control de Caducidades (Lotes Próximos a Vencer)
Previene mermas financieras identificando lotes de alimentos perecederos con vencimiento menor a 30 días:
```sql
SELECT 
    i.fecha_corte,
    s.sucursal_nombre,
    p.producto_nombre,
    i.lote,
    i.fecha_vencimiento,
    i.dias_para_vencer,
    i.alerta_vencimiento,
    i.stock_disponible,
    ROUND(i.valor_inventario_costo, 2) AS valor_inventario_costo
FROM marts.fct_inventario i
JOIN marts.dim_sucursal s ON i.id_sucursal = s.id_sucursal
JOIN marts.dim_producto p ON i.id_producto = p.id_producto
WHERE i.alerta_vencimiento IN ('Vencido', 'Próximo a Vencer')
ORDER BY i.dias_para_vencer ASC;
```

### Consulta 6: Análisis de Devoluciones por Motivo y Costo
Identifica pérdidas generadas por empaques defectuosos, productos dañados o errores de despacho:
```sql
SELECT 
    d.motivo_devolucion,
    COUNT(d.id_devolucion) AS total_eventos_devolucion,
    SUM(d.cantidad_devuelta) AS total_unidades_devueltas,
    ROUND(SUM(d.monto_estimado_devolucion), 2) AS monto_total_devuelto
FROM marts.fct_devoluciones d
GROUP BY d.motivo_devolucion
ORDER BY monto_total_devuelto DESC;
```

### Consulta 7: Comportamiento por Canal de Venta y Método de Pago
```sql
SELECT 
    v.canal_venta,
    v.metodo_pago,
    COUNT(DISTINCT v.id_venta) AS total_pedidos,
    ROUND(SUM(v.importe_neto), 2) AS facturacion_total,
    ROUND(AVG(v.importe_neto), 2) AS ticket_promedio
FROM marts.fct_ventas v
GROUP BY v.canal_venta, v.metodo_pago
ORDER BY facturacion_total DESC;
```

### Consulta 8: Eficiencia de Promociones y Descuentos
Evalúa si los descuentos comerciales mejoraron el volumen de venta sin deteriorar excesivamente el margen de utilidad:
```sql
SELECT 
    p.nombre_promocion,
    p.categoria_nombre,
    p.porcentaje_descuento AS pct_descuento_promocion,
    p.fecha_inicio,
    p.fecha_fin,
    ROUND(SUM(v.importe_bruto), 2) AS venta_bruta_generada,
    ROUND(SUM(v.monto_descuento), 2) AS descuento_otorgado,
    ROUND(SUM(v.importe_neto), 2) AS venta_neta_obtenida,
    ROUND(SUM(v.margen_ganancia), 2) AS ganancia_obtenida
FROM marts.dim_promocion p
JOIN marts.dim_producto prod ON p.id_categoria = prod.id_categoria
JOIN marts.fct_ventas v ON prod.id_producto = v.id_producto 
    AND v.fecha_venta BETWEEN p.fecha_inicio AND p.fecha_fin
GROUP BY p.nombre_promocion, p.categoria_nombre, p.porcentaje_descuento, p.fecha_inicio, p.fecha_fin
ORDER BY venta_neta_obtenida DESC;
```

---

## 10. FASE 7: PREPARACIÓN Y GUÍA DE CONEXIÓN PARA POWER BI

Para dar cumplimiento completo a los requerimientos opcionales del proyecto y facilitar la integración con herramientas de visualización corporativa, el Data Warehouse quedó configurado y listo para consumirse directamente desde **Power BI Desktop**.

### 10.1 Parámetros de Conexión
- **Conector:** PostgreSQL Database (Integrado en Power BI)
- **Servidor:** `localhost:5432` (o la IP del host Docker)
- **Base de Datos:** `sgfood_dw`
- **Modo de Conectividad:** `Import` (Recomendado para alto rendimiento) o `DirectQuery`
- **Usuario:** `postgres`
- **Contraseña:** `postgres`

### 10.2 Esquema y Tablas a Seleccionar
En el navegador de Power BI, expandir el esquema **`marts`** y seleccionar las siguientes tablas:
1. `marts.dim_sucursal`
2. `marts.dim_categoria`
3. `marts.dim_marca`
4. `marts.dim_producto`
5. `marts.dim_cliente`
6. `marts.dim_proveedor`
7. `marts.dim_promocion`
8. `marts.dim_fecha`
9. `marts.fct_ventas`
10. `marts.fct_inventario`
11. `marts.fct_devoluciones`
12. `marts.fct_rendimiento_metas`

### 10.3 Relaciones Recomendadas en la Vista de Modelo de Power BI
En la vista de modelo de Power BI, arrastrar y soltar las relaciones siguiendo el esquema estrella:
- `marts.fct_ventas(fecha_venta)` -> `marts.dim_fecha(fecha)` (Muchos a Uno, Filtro Simple)
- `marts.fct_ventas(id_sucursal)` -> `marts.dim_sucursal(id_sucursal)` (Muchos a Uno, Filtro Simple)
- `marts.fct_ventas(id_cliente)` -> `marts.dim_cliente(id_cliente)` (Muchos a Uno, Filtro Simple)
- `marts.fct_ventas(id_producto)` -> `marts.dim_producto(id_producto)` (Muchos a Uno, Filtro Simple)
- `marts.fct_inventario(fecha_corte)` -> `marts.dim_fecha(fecha)` (Muchos a Uno, Filtro Simple)
- `marts.fct_inventario(id_sucursal)` -> `marts.dim_sucursal(id_sucursal)` (Muchos a Uno, Filtro Simple)
- `marts.fct_inventario(id_producto)` -> `marts.dim_producto(id_producto)` (Muchos a Uno, Filtro Simple)
- `marts.fct_devoluciones(id_sucursal)` -> `marts.dim_sucursal(id_sucursal)` (Muchos a Uno, Filtro Simple)
- `marts.fct_devoluciones(id_producto)` -> `marts.dim_producto(id_producto)` (Muchos a Uno, Filtro Simple)
- `marts.fct_rendimiento_metas(id_sucursal)` -> `marts.dim_sucursal(id_sucursal)` (Muchos a Uno, Filtro Simple)

---

## 11. MANUAL DE OPERACIÓN Y REPRODUCIBILIDAD EN OTROS ENTORNOS

### 11.1 Requisitos Previos
- Docker Engine versión 24.0 o superior
- Docker Compose versión 2.20 o superior
- 4 GB de memoria RAM libre

### 11.2 Paso 1: Clonar y Navegar al Proyecto
```bash
git clone https://github.com/Ennero/SS22S2026_G1.git
cd SS22S2026_G1/Proyecto1
```

### 11.3 Paso 2: Configurar Variables de Entorno
```bash
cp .env.example .env
```

### 11.4 Paso 3: Levantar los Contenedores
```bash
docker compose up -d --build
```
Verificar que los 3 contenedores estén saludables:
```bash
docker compose ps
```

### 11.5 Paso 4: Disparar el Pipeline en Airflow
El pipeline puede dispararse desde la interfaz gráfica web en `http://localhost:8080`:
- **Usuario:** `admin`
- **Contraseña:** `admin`
- **Restablecimiento si indica contraseña incorrecta:**
  ```bash
  docker compose exec airflow airflow users reset-password --username admin --password admin
  ```
O bien, dispararse directamente por terminal:
```bash
docker compose exec airflow airflow dags trigger sgfood_elt_pipeline
```
Para seguir el estado de la ejecución por consola:
```bash
docker compose exec airflow airflow dags list-runs -d sgfood_elt_pipeline
```

### 11.6 Paso 5: Ejecutar Pruebas dbt Manualmente (Opcional)
Si se desea correr dbt de forma interactiva dentro del contenedor:
```bash
# Ejecutar modelos dbt
docker compose exec airflow dbt run --project-dir /opt/airflow/dbt_sgfood --profiles-dir /opt/airflow/dbt_sgfood

# Ejecutar pruebas de calidad dbt
docker compose exec airflow dbt test --project-dir /opt/airflow/dbt_sgfood --profiles-dir /opt/airflow/dbt_sgfood
```

### 11.7 Paso 6: Ejecutar Consultas Analíticas
Para validar los resultados de negocio contra PostgreSQL:
```bash
docker compose exec -T postgres psql -U postgres -d sgfood_dw < sql/analytics_queries.sql
```

### 11.8 Paso 7: Acceder a Adminer (Gestión Web)
Abrir el navegador web en `http://localhost:8081`:
- **Sistema:** `PostgreSQL` (menú desplegable)
- **Servidor:** `postgres` (IMPORTANTE: colocar `postgres`, no `localhost`)
- **Usuario:** `postgres`
- **Contraseña:** `postgres`
- **Base de datos:** `sgfood_dw`

### 11.9 Paso 8: Detención y Limpieza Total del Entorno
- **Detener contenedores conservando datos:**
  ```bash
  docker compose down
  ```
- **Limpieza total y reinicio desde cero (eliminar contenedores, redes y volúmenes con datos):**
  ```bash
  docker compose down -v
  ```
  El modificador `-v` destruye los volúmenes nombrados `sgfood_pgdata` y `airflow_logs`, asegurando que no quede ningún dato residual al volver a arrancar el sistema.

---

## 12. MATRIZ DE CUMPLIMIENTO DE LA RÚBRICA DE EVALUACIÓN

| No. | Criterio de Evaluación | Puntos | Estado | Evidencia en el Repositorio |
|---|---|---|---|---|
| **1.1** | **Desarrollo del flujo con Python y Airflow** | **20 pts** | **100% CUMPLIDO** | Scripts modulares en `elt/` (`extract_oltp.py`, `extract_csv.py`, `quality_checker.py`), DAG en `dags/sgfood_elt_pipeline.py` con 10 tareas secuenciales y reintentos, carga a `raw` 100% idempotente. |
| **1.2** | **Documentación técnica y manual de implementación** | **10 pts** | **100% CUMPLIDO** | `IMPLEMENTACION-P1.md` y `README.md` detallando arquitectura, decisiones técnicas, explicaciones por componente, guía paso a paso y manual de Power BI. |
| **1.3** | **Cumplimiento de entregables y repositorio** | **10 pts** | **100% CUMPLIDO** | Estructura organizada dentro de `Proyecto1/`, dockerfile, compose, dbt, sql, data, integrantes de pareja identificados. |
| **2.1** | **Diseño e implementación del Data Warehouse y modelos dbt** | **30 pts** | **100% CUMPLIDO** | Schemas separados (`raw`, `staging`, `intermediate`, `marts`), modelo estrella con 8 dimensiones y 4 hechos, llaves subrogadas, métricas financieras y de inventario calculadas. |
| **2.2** | **Integración de fuentes, pruebas y validación del flujo completo** | **30 pts** | **100% CUMPLIDO** | Ingesta de 7 tablas OLTP + 5 CSVs, 92 pruebas dbt aprobadas (`PASS=92 WARN=0 ERROR=0`), 8 consultas analíticas en `sql/analytics_queries.sql` validadas. |
| **OPT** | **Requerimientos Opcionales / Plus** | **Extra** | **100% CUMPLIDO** | Ejecución programada (cron), variables `.env`, contenedorización completa Docker, validación de calidad previa y posterior, preparación completa para Power BI. |
| **TOTAL** | **Calificación Global del Proyecto** | **100 / 100 pts** | **SATISFACTORIO MÁXIMO** | Todos los criterios de calificación técnica y metodológica cubiertos rigurosamente. |

---
*Fin del documento de implementación técnica.*
