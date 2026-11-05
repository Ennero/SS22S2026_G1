# GUÍA DE DEFENSA TÉCNICA Y GUION DE PRESENTACIÓN EN VIVO
## PROYECTO 2: SEMINARIO DE SISTEMAS 2 — SEGUNDO SEMESTRE 2026
### Escuela de Ciencias y Sistemas — Facultad de Ingeniería, USAC

---

### DATOS DEL EQUIPO (GRUPO 1)
| Integrante | Carné | Rol en la Presentación |
|---|---|---|
| **Diego Alessandro Constanza Padilla** | **202300601** | Bloque Técnico: Optimización Física, Benchmarking y Modelado BQML |
| **Enner Esaí Mendizabal Castro** | **202302220** | Bloque Arquitectura: Introducción, Limpieza, Looker Studio y Airflow |

* **Tiempo Total Estimado:** 10 a 12 Minutos
* **Objetivo:** Demostrar el cumplimiento del 100% de la rúbrica oficial mediante una defensa práctica y reproducible en vivo.

---

## 📑 ÍNDICE DE LA GUÍA

1. [Preparación Previa (Checklist de 5 Minutos)](#1-preparación-previa-checklist-de-5-minutos)
2. [Cronograma General de la Defensa (12 Minutos)](#2-cronograma-general-de-la-defensa-12-minutos)
3. [Guion Detallado Paso a Paso (Qué Mostrar, Qué Clics Hacer y Qué Decir)](#3-guion-detallado-paso-a-paso)
   - [Paso 1: Introducción, Dataset Público y Volumen (Min 0-2)](#paso-1-introducción-dataset-público-y-volumen-min-0000---0200)
   - [Paso 2: Limpieza e Ingeniería de Características (Min 2-4)](#paso-2-limpieza-e-ingeniería-de-características-min-0200---0400)
   - [Paso 3: Optimización Física y Demostración en Vivo de Bytes (Min 4-6)](#paso-3-optimización-física-y-demostración-en-vivo-de-bytes-min-0400---0630)
   - [Paso 4: BigQuery ML y Prevención de Data Leakage (Min 6-9)](#paso-4-bigquery-ml-y-prevención-de-data-leakage-min-0630---0900)
   - [Paso 5: Tablero Interactivo en Looker Studio (Min 9-11)](#paso-5-tablero-interactivo-en-looker-studio-min-0900---1100)
   - [Paso 6: Orquestación con Airflow y Conclusiones (Min 11-12)](#paso-6-orquestación-con-airflow-y-conclusiones-min-1100---1200)
4. [Banco de Preguntas Trampa del Auxiliar / Docente](#4-banco-de-preguntas-trampa-del-auxiliar--docente)
5. [Plan de Contingencia (¿Qué hacer si algo falla?)](#5-plan-de-contingencia-qué-hacer-si-algo-falla)

---

## 1. PREPARACIÓN PREVIA (CHECKLIST DE 5 MINUTOS)

Antes de entrar a la sala de Meet/Teams o pasar al frente con el auxiliar, abre estas **4 pestañas en tu navegador** en este orden exacto:

* [ ] **Pestaña 1 (BigQuery Console):**
  * URL: `https://console.cloud.google.com/bigquery?project=project-0d3c28c7-a4e0-44ad-a4e`
  * Despliega en el panel izquierdo: `project-0d3c28c7-a4e0-44ad-a4e > nyc_taxi_dw` para que se vean todas las tablas y los 2 modelos.
  * Ten una pestaña de consulta SQL en blanco lista para escribir.
* [ ] **Pestaña 2 (Google Looker Studio):**
  * URL: `https://lookerstudio.google.com/reporting/6f35e95a-771b-4ab3-86b8-b912086bfdea`
  * Asegúrate de que cargue la Página 1 (*Rolling Forecast & Modelos*).
* [ ] **Pestaña 3 (Repositorio en GitHub):**
  * URL: `https://github.com/Ennero/SS22S2026_G1/tree/main/Proyecto_2`
  * Abierto en el archivo `README.md` mostrando los nombres de la pareja.
* [ ] **Pestaña 4 (Airflow Web UI - Opcional):**
  * URL: `http://localhost:8080` (si levantaste Docker) o deja lista la vista de arquitectura en el README.

---

## 2. CRONOGRAMA GENERAL DE LA DEFENSA (12 MINUTOS)

```
00:00 - 02:00 | Enner | Introducción, Dataset Público (>36M) y Cumplimiento Inicial
02:00 - 04:00 | Enner | Limpieza de datos (33.2M) y las 9 Variables Derivadas
04:00 - 06:30 | Diego | Demostración en vivo: 1.24 GB vs 127 MB (Ahorro > 89%)
06:30 - 09:00 | Diego | Modelos BQML, prevención de Data Leakage y Métricas (R² 93%)
09:00 - 11:00 | Enner | Looker Studio interactivo (Rolling Forecast y EDA de 24h)
11:00 - 12:00 | Enner | Orquestación con Airflow (Docker), Conclusiones y Cierre
```

---

## 3. GUION DETALLADO PASO A PASO

### PASO 1: Introducción, Dataset Público y Volumen (Min 00:00 - 02:00)
* **Responsable:** Enner Mendizabal.
* **Qué proyectar:** Pestaña 3 (GitHub README) y luego pasar a Pestaña 1 (BigQuery).
* **Acción en pantalla:** Señalar en el README los integrantes del Grupo 1 y luego mostrar el panel de BigQuery.
* **Guion textual a decir:**
  > *"Buenas tardes. Somos el Grupo 1, integrado por Diego Constanza y Enner Mendizabal. El día de hoy presentamos la defensa del Proyecto 2: Procesamiento Masivo, Optimización y Machine Learning en Google BigQuery.*
  > 
  > *Para cumplir con el primer requisito obligatorio de la rúbrica, nos conectamos al dataset público de telemetría urbana `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2022`.*
  > 
  > *Como pueden observar en nuestra consola de Google Cloud, el dataset público cuenta con más de **36.2 millones de registros**, superando por mucho el millón mínimo exigido por el enunciado.*
  > 
  > *En nuestro script inicial de exploración auditamos la calidad de la información: identificamos que no existían registros nulos en campos esenciales como el monto de la tarifa o las marcas de tiempo, pero detectamos ruidos habituales de calibración en taxímetros que debían ser saneados antes de modelar."*

---

### PASO 2: Limpieza e Ingeniería de Características (Min 02:00 - 04:00)
* **Responsable:** Enner Mendizabal.
* **Qué proyectar:** Pestaña 1 (BigQuery Console), hacer clic en la tabla `tbl_yellow_trips_clean` y abrir la pestaña **Detalles**.
* **Acción en pantalla:** Mostrar que la tabla tiene **33,226,079 filas**.
* **Guion textual a decir:**
  > *"En el script `02_cleaning_and_features.sql` aplicamos las reglas de negocio y física urbana:*
  > 1. *Descartamos tarifas negativas o menores a la bajada de bandera reglamentaria de NYC ($2.50).*
  > 2. *Filtramos trayectos con distancias nulas pero con cobros mayores a $20, y descartamos viajes con duración menor a 1 minuto o mayor a 3 horas.*
  > 3. *Limitamos la velocidad a un máximo realista de 75 mph.*
  > 
  > *Esto consolidó **33.2 millones de registros limpios** en nuestra tabla `tbl_yellow_trips_clean`.*
  > 
  > *Asimismo, implementamos ingeniería de características construyendo **9 variables derivadas clave**: la duración en minutos, la velocidad promedio en mph, franjas horarias y días de la semana, banderas booleanas para **fin de semana** y **horas pico** laborales, indicador de **viajes aeroportuarios** a JFK y LaGuardia, el **ratio de propina**, y la segmentación cronológica para evitar fuga de información en Machine Learning."*

---

### PASO 3: Optimización Física y Demostración en Vivo de Bytes (Min 04:00 - 06:30)
* **Responsable:** Diego Constanza.
* **Qué proyectar:** Pestaña 1 (BigQuery Console).
* **Acción en pantalla (EL MOMENTO CLAVE):**
  1. Haz clic en la tabla `tbl_yellow_trips_optimized` y entra a la pestaña **Detalles**. Señala con el cursor:
     * *Tipo de tabla: Con particiones (por día en tpep_pickup_datetime)*.
     * *Clúster por: PULocationID, DOLocationID, payment_type*.
  2. Abre el editor de consultas en blanco y pega esta consulta sobre la tabla **estándar**:
     ```sql
     SELECT COUNT(*), AVG(fare_amount), SUM(total_amount)
     FROM `nyc_taxi_dw.tbl_yellow_trips_standard`
     WHERE DATE(tpep_pickup_datetime) BETWEEN '2022-10-01' AND '2022-10-31';
     ```
  3. **Pausa dramática:** Señala la esquina superior derecha donde dice: **"Esta consulta procesará 1.24 GB cuando se ejecute"**.
  4. En el mismo editor, cambia la palabra `standard` por `optimized`:
     ```sql
     SELECT COUNT(*), AVG(fare_amount), SUM(total_amount)
     FROM `nyc_taxi_dw.tbl_yellow_trips_optimized`
     WHERE DATE(tpep_pickup_datetime) BETWEEN '2022-10-01' AND '2022-10-31';
     ```
  5. Señala nuevamente la esquina superior derecha: el validador cae a **127.54 MB**.
* **Guion textual a decir:**
  > *"Para cumplir con el criterio de optimización y reducción de costos cloud, creamos dos tablas con exactamente los mismos 33.2 millones de filas:*
  > - *La tabla estándar (`tbl_yellow_trips_standard`), sin optimizar.*
  > - *La tabla optimizada (`tbl_yellow_trips_optimized`), particionada diariamente por fecha de abordaje y clusterizada por origen, destino y método de pago.*
  > 
  > *Como pueden ver en vivo en el validador de BigQuery para una consulta analítica sobre el mes de octubre:*
  > - *En la tabla estándar escanea **1.24 GB**, realizando un escaneo completo de 11 meses que no necesitamos.*
  > - *En la tabla optimizada el escaneo se reduce a **127.54 MB**.*
  > 
  > *Esto representa un **ahorro inmediato del 89.94% en bytes procesados**, gracias al mecanismo de **Partition Pruning**.*
  > 
  > *Y cuando agregamos filtros geográficos hacia el aeropuerto JFK (Query 2 del benchmark), el ahorro sube al **95.47%** debido al **Block Skipping** que salta los bloques que no corresponden a la zona 132. En un entorno empresarial donde se cobran $6.25 por TB, esta técnica ahorra más del 90% del presupuesto mensual de analítica."*

---

### PASO 4: BigQuery ML y Prevención de Data Leakage (Min 06:30 - 09:00)
* **Responsable:** Diego Constanza.
* **Qué proyectar:** Pestaña 1 (BigQuery Console), despliega la sección **Modelos (2)** en el panel izquierdo y muestra `model_fare_linear_reg` y `model_fare_boosted_tree`.
* **Acción en pantalla:** Abre una pestaña de consulta y ejecuta rápidamente la evaluación comparativa:
  ```sql
  SELECT 'Modelo 1: Linear Reg' AS modelo, ROUND(mean_absolute_error, 2) AS mae, ROUND(SQRT(mean_squared_error), 2) AS rmse, ROUND(r2_score, 4) AS r2 
  FROM ML.EVALUATE(MODEL `nyc_taxi_dw.model_fare_linear_reg`, (SELECT * FROM `nyc_taxi_dw.vw_bqml_training_data` WHERE is_eval_split = TRUE))
  UNION ALL
  SELECT 'Modelo 2: Boosted Tree' AS modelo, ROUND(mean_absolute_error, 2) AS mae, ROUND(SQRT(mean_squared_error), 2) AS rmse, ROUND(r2_score, 4) AS r2 
  FROM ML.EVALUATE(MODEL `nyc_taxi_dw.model_fare_boosted_tree`, (SELECT * FROM `nyc_taxi_dw.vw_bqml_training_data` WHERE is_eval_split = TRUE));
  ```
* **Guion textual a decir:**
  > *"En la sección de Machine Learning, nuestro objetivo predictivo es estimar la tarifa base del viaje (`fare_amount`). La rúbrica penaliza fuertemente el Data Leakage, por lo que aplicamos dos defensas metodológicas estrictas:*
  > 
  > *1. **Prevención de Target Leakage:** Excluimos completamente variables post-evento como la duración del viaje, la hora de llegada (`dropoff_datetime`), propinas y peajes. Al momento en que un usuario sube al taxi, esa información es desconocida. Solo utilizamos features ex-ante (hora de abordaje, día, distancia estimada, zonas y si es hora pico).*
  > 
  > *2. **Prevención de Temporal Leakage:** BigQuery ML utiliza por defecto `data_split_eval_fraction` con split aleatorio. En series temporales de demanda urbana, esto es un error grave porque entrena el modelo con datos de diciembre para predecir enero. Descartamos el random split y configuramos `data_split_method = 'CUSTOM'` cronológico:*
  >    - *Entrenamiento (70%): Enero a Agosto de 2022.*
  >    - *Evaluación (15%): Septiembre a Octubre de 2022.*
  >    - *Prueba (15%): Noviembre a Diciembre de 2022, aislado para inferencia futura.*
  > 
  > *Entrenamos dos modelos:*
  > - *Modelo 1: Regresión Lineal Ridge con regularización L2 (`l2_reg = 0.1`).*
  > - *Modelo 2: Gradient Boosted Trees (`BOOSTED_TREE_REGRESSOR` / XGBoost).*
  > 
  > *Al ver los resultados en pantalla, el Boosted Tree es ampliamente superior: reduce el MAE de **$1.95 a $1.72**, reduce el RMSE a **$3.55** y alcanza un coeficiente de determinación $R^2$ de **0.9301**, explicando el **93% de la varianza total** de las tarifas gracias a su capacidad de capturar interacciones no lineales de congestión y rutas complejas."*

---

### PASO 5: Tablero Interactivo en Looker Studio (Min 09:00 - 11:00)
* **Responsable:** Enner Mendizabal.
* **Qué proyectar:** Pestaña 2 (Looker Studio).
* **Acción en pantalla:**
  1. En la **Página 1 (Rolling Forecast)**: Señala los scorecards de MAE y la gráfica temporal interactiva. Pasa el mouse sobre las líneas azul, naranja y celeste para mostrar los valores emergentes diarios.
  2. Haz clic en el menú lateral izquierdo y cambia a la **Página 2 (Análisis Exploratorio - EDA)**.
  3. Despliega el filtro interactivo `is_weekend` y selecciona el valor `1` para mostrar cómo los gráficos se recalculan en tiempo real.
* **Guion textual a decir:**
  > *"Para la comunicación de resultados, implementamos un tablero interactivo en Google Looker Studio conectado directamente a las tablas de BigQuery sin costos intermedios:*
  > 
  > *- **En la Página 1 tenemos el Rolling Forecast:** Evaluamos **2,970,631 viajes** del conjunto de prueba independiente (Noviembre y Diciembre de 2022). La gráfica diaria compara la curva de tarifa real en azul, la predicción del Boosted Tree en naranja y la regresión lineal en celeste. Como pueden notar, el modelo de árboles sigue fielmente la volatilidad diaria con un MAE promedio de **$1.66 a $1.72 USD**.*
  > 
  > *- **En la Página 2 presentamos el Análisis Exploratorio:** Demostramos los patrones clave de movilidad de NYC:*
  >   1. *La distribución en 24 horas evidencia un patrón bimodal de lunes a viernes, con picos marcados a las 8:00 AM y 6:00 PM.*
  >   2. *El gráfico circular confirma que el **79.7% de los pagos se realizan con tarjeta de crédito** y el 20.3% en efectivo.*
  >   3. *Y mediante este control interactivo de fin de semana podemos observar cómo los días sábado y domingo la demanda se traslada hacia horarios nocturnos y de ocio."*

---

### PASO 6: Orquestación con Airflow y Conclusiones (Min 11:00 - 12:00)
* **Responsable:** Enner Mendizabal.
* **Qué proyectar:** Pestaña 3 (GitHub README, sección 11 de arquitectura Airflow) o Pestaña 4 (`http://localhost:8080`).
* **Acción en pantalla:** Mostrar el diagrama de flujo del DAG con las 7 tareas secuenciales.
* **Guion textual a decir:**
  > *"Finalmente, para garantizar calidad de ingeniería y reproducibilidad, todo este flujo fue orquestado mediante **Apache Airflow 2.9 contenerizado en Docker**.*
  > 
  > *El DAG `dag_nyc_taxi_bigquery_pipeline` ejecuta de forma secuencial y automatizada: la validación de conexión y conteo de más de 1 millón de registros, las transformaciones SQL idempotentes mediante sentencias `CREATE OR REPLACE`, el cálculo programático del benchmark y el reentrenamiento y evaluación de los modelos de BigQuery ML.*
  > 
  > *En conclusión:*
  > - *Demostramos que el particionamiento y clustering reduce más del 90% del costo en la nube.*
  > - *Comprobamos que un split cronológico personalizado es vital para no engañar al modelo con fugas temporales.*
  > - *Y entregamos una solución end-to-end completa, documentada y desplegable en producción.*
  > 
  > *Muchas gracias, quedamos atentos a sus preguntas."*

---

## 4. BANCO DE PREGUNTAS TRAMPA DEL AUXILIAR / DOCENTE

Ten preparadas estas respuestas directas y seguras:

#### 1. "¿Por qué particionaron por día y no por mes?"
> **Respuesta:** *"Porque los análisis y auditorías de transporte urbano operan a nivel de fechas específicas, fines de semana o eventos particulares. Si particionáramos por mes, cualquier consulta sobre un rango de 3 o 4 días obligaría a BigQuery a leer el mes completo (Full Scan mensual). La partición diaria divide los datos en 365 bloques físicos contiguos, permitiendo podar con precisión y reducir los bytes leídos en casi un 90%."*

#### 2. "¿Por qué eligieron esas 3 columnas para el Clustering (`PULocationID`, `DOLocationID`, `payment_type`)?"
> **Respuesta:** *"Las zonas de origen y destino tienen una cardinalidad alta (~265 distritos de NYC) y son los filtros geográficos más frecuentes en el negocio de transporte. Al clusterizar por ellas, BigQuery almacena juntos los registros de la misma zona dentro de cada partición, activando el **Block Skipping**. Añadimos `payment_type` porque los reportes financieros casi siempre filtran o agrupan entre tarjeta y efectivo."*

#### 3. "¿Por qué no incluyeron la duración del viaje (`trip_duration_minutes`) en el modelo de ML?"
> **Respuesta:** *"Porque cometeríamos **Target Data Leakage**. La duración real del viaje solo se conoce cuando el pasajero se baja del taxi. Si la incluyéramos en el entrenamiento, el modelo tendría una precisión falsamente perfecta en laboratorio, pero al ponerlo en producción para predecir la tarifa cuando el usuario aborda el taxi, el modelo fallaría porque ese dato no existe."*

#### 4. "¿Por qué rechazaron `data_split_eval_fraction`?"
> **Respuesta:** *"Porque `data_split_eval_fraction` utiliza un split aleatorio (Random Split). En series temporales, el split aleatorio mezcla viajes de diciembre y noviembre en el conjunto de entrenamiento para intentar predecir viajes de enero y febrero. Eso es **Temporal Leakage** (fuga del futuro al pasado). Por eso usamos `data_split_method = 'CUSTOM'` determinista por meses: Ene-Ago entrena, Sep-Oct evalúa y Nov-Dic prueba."*

#### 5. "¿Por qué el Boosted Tree fue mejor que la Regresión Lineal?"
> **Respuesta:** *"La regresión lineal asume relaciones estrictamente lineales y aditivas. En el tráfico real de Nueva York, la relación entre distancia, hora y costo no es lineal: recorrer 2 millas en hora pico en Manhattan a las 8 AM cuesta y demora mucho más que recorrerlas a las 3 AM. El Boosted Tree (XGBoost) captura árboles de decisión que dividen no linealidades y combinaciones complejas de zonas y horarios, alcanzando un $R^2$ de 0.93 frente a 0.92 de la regresión."*

---

## 5. PLAN DE CONTINGENCIA (¿QUÉ HACER SI ALGO FALLA?)

* **Si la conexión a internet en el laboratorio es lenta o falla:**
  * No entres en pánico. Abre la carpeta `Proyecto_2/img/` localmente:
    * `01_bq_dataset_tables.png`: Demuestra tus tablas y modelos en BigQuery.
    * `looker_forecast_dashboard.png`: Demuestra tu gráfica de Rolling Forecast y KPIs.
    * `looker_eda_dashboard.png`: Demuestra tus 3 gráficos de EDA.
* **Si el validador de BigQuery no carga los bytes en vivo:**
  * Corre en la terminal: `python scripts/run_benchmark.py` y muéstrale la tabla impresa en consola que lee directamente de la API de BigQuery.
* **Si te piden el informe formal:**
  * Abre el archivo [docs/INFORME_TECNICO_PROYECTO_2.md](INFORME_TECNICO_PROYECTO_2.md) que contiene los 15 capítulos académicos detallados.
