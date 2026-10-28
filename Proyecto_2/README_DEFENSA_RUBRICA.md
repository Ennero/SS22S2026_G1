# 📋 GUÍA DE DEFENSA Y RÚBRICA PASO A PASO (100 PUNTOS)
## PROYECTO 2: SEMINARIO DE SISTEMAS 2 — SEGUNDO SEMESTRE 2026
### Escuela de Ciencias y Sistemas — Facultad de Ingeniería, USAC

---

### 👥 DATOS DEL EQUIPO (GRUPO 1)
| Nombre Completo | Carné | Correo Institucional | Rol Principal |
|---|---|---|---|
| **Diego Alessandro Constanza Padilla** | **202300601** | dconstanza@ingenieria.usac.edu.gt | Modelado BQML, Optimización y Benchmarking |
| **Enner Esaí Mendizabal Castro** | **202302220** | emendizabal@ingenieria.usac.edu.gt | Arquitectura Cloud, Orquestación Airflow y Looker Studio |

* **Proyecto GCP:** `project-0d3c28c7-a4e0-44ad-a4e`
* **Dataset Personal:** `nyc_taxi_dw` (Ubicación: `US`)
* **Tablero Looker Studio:** [Enlace Público Oficial](https://lookerstudio.google.com/reporting/6f35e95a-771b-4ab3-86b8-b912086bfdea)
* **Airflow Web UI:** `http://localhost:8080` (admin / admin)

---

## 📊 RESUMEN DE PUNTUACIONES (HOJA DE CALIFICACIÓN)

| No. | Criterio de Evaluación | Pts | Estado | Qué Mostrar |
|:---:|---|:---:|:---:|---|
| **1.1** | Conexión y comprensión del dataset público | **8** | ✅ 100% | Conteo >36.2M y auditoría de nulos en BigQuery |
| **1.2** | Consultas SQL avanzadas y transformaciones | **8** | ✅ 100% | CTEs, funciones de ventana y 33.2M filas limpias |
| **1.3** | Optimización con particiones y clustering | **12** | ✅ 100% | Partición diaria y cluster por zonas en Detalles |
| **1.4** | Implementación correcta de al menos 2 modelos en BQML | **8** | ✅ 100% | `model_fare_linear_reg` y `model_fare_boosted_tree` |
| **1.5** | Evaluación y comparación con métricas e hiperparámetros | **12** | ✅ 100% | Consulta `ML.EVALUATE` en vivo (MAE, RMSE, R²) |
| **1.6** | Prevención de data leakage y manejo correcto del split | **12** | ✅ 100% | Split cronológico determinista y exclusión post-evento |
| **2.1** | Análisis correcto de patrones y tendencias | **10** | ✅ 100% | Patrón bimodal, 79.7% tarjeta y viajes a JFK/LGA |
| **2.2** | Visualización de resultados exploratorios y predicciones | **10** | ✅ 100% | Dashboard en Looker Studio (Forecast y EDA) |
| **2.3** | Ingeniería de características y justificación de variables | **10** | ✅ 100% | 9 variables derivadas (`trip_speed_mph`, `is_rush_hour`, etc.) |
| **2.4** | Identificación de variables de entrada, salida y objetivo | **5** | ✅ 100% | Target: `fare_amount`, Features ex-ante sin fuga |
| **2.5** | Comparación entre consultas estándar y optimizadas | **5** | ✅ 100% | Demostración en vivo de bytes: **1.24 GB vs 127 MB** |
| **TOTAL** | **PUNTUACIÓN MÁXIMA** | **100** | **EXCELENCIA** | **Proyecto 100% verificado y probado en BigQuery** |

---

## 1. HABILIDADES (60 PUNTOS)

```
+-----------------------------------------------------------------------------------------------+
| CRITERIO 1.1: Conexión y comprensión del dataset público (8 Pts)                              |
+-----------------------------------------------------------------------------------------------+
```
* **Qué mostrar en pantalla:**
  Abre BigQuery Console en blanco y ejecuta esta consulta rápida para que el evaluador vea el conteo en tiempo real:
  ```sql
  SELECT 
      COUNT(*) AS total_registros_publicos,
      COUNT(DISTINCT DATE(pickup_datetime)) AS dias_registrados,
      MIN(pickup_datetime) AS fecha_minima,
      MAX(pickup_datetime) AS fecha_maxima
  FROM `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2022`;
  ```
* **Qué decir:**
  > *"Nos conectamos exitosamente al dataset público `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2022`. Como se aprecia en pantalla, cuenta con **36,256,539 registros**, superando en más de un 3,500% el millón mínimo requerido por el enunciado.*
  > *En nuestro script `01_exploration.sql` auditamos la calidad: comprobamos que no hay nulos en tarifas ni marcas temporales, pero detectamos anomalías físicas habituales en telemetría de taxímetros (tarifas negativas por disputas, distancias nulas con cobro y desincronización de relojes GPS) que fueron depuradas en la fase siguiente."*
* **Dato clave a recordar:** 36,256,539 registros en el dataset público.

---

```
+-----------------------------------------------------------------------------------------------+
| CRITERIO 1.2: Consultas SQL avanzadas y transformaciones (8 Pts)                              |
+-----------------------------------------------------------------------------------------------+
```
* **Qué mostrar en pantalla:**
  En BigQuery, haz clic sobre la tabla `nyc_taxi_dw.tbl_yellow_trips_clean`, entra a **Detalles** y señala con el cursor el campo **Número de filas: 33,226,079**.
  Abre en tu editor de código o GitHub el archivo `sql/02_cleaning_and_features.sql`.
* **Qué decir:**
  > *"En `02_cleaning_and_features.sql` implementamos transformaciones avanzadas utilizando CTEs (`WITH base_datos AS ...`), funciones temporales `EXTRACT` y `TIMESTAMP_DIFF`, funciones de ventana analítica `SUM OVER()`, conversiones de tipos con `SAFE_CAST` y divisiones con `SAFE_DIVIDE`.*
  > *Aplicamos filtros estrictos basados en la normativa de la Comisión de Taxis de NYC (TLC): viajes de 1 a 180 minutos, distancias de 0.1 a 100 millas, tarifas entre el mínimo reglamentario de $2.50 y $500 USD, y velocidades menores a 75 mph, obteniendo **33.2 millones de registros limpios y consistentes**."*
* **Dato clave a recordar:** 33,226,079 filas limpias resultantes.

---

```
+-----------------------------------------------------------------------------------------------+
| CRITERIO 1.3: Optimización con particiones y clustering (12 Pts)                              |
+-----------------------------------------------------------------------------------------------+
```
* **Qué mostrar en pantalla:**
  En BigQuery, haz clic en la tabla `tbl_yellow_trips_optimized` y entra a la pestaña **Detalles**. Señala:
  * *Tipo de tabla: Con particiones (por día en `tpep_pickup_datetime`)*.
  * *Clúster por: `PULocationID, DOLocationID, payment_type`*.
* **Qué decir:**
  > *"Creamos dos tablas con exactamente los mismos 33.2 millones de datos: `tbl_yellow_trips_standard` (almacenamiento convencional) y `tbl_yellow_trips_optimized`.*
  > *Justificación de las técnicas:*
  > 1. ***Particionamiento Diario por Fecha:** Divide la tabla en 365 particiones físicas independientes. Al consultar un rango de días, BigQuery activa **Partition Pruning**, ignorando los bloques de datos de los meses no solicitados.*
  > 2. ***Clustering Multidimensional:** Agrupa co-localizadamente los registros contiguos por origen, destino y método de pago, permitiendo **Block Skipping** al consultar trayectos hacia aeropuertos o distritos de alta demanda."*

---

```
+-----------------------------------------------------------------------------------------------+
| CRITERIO 1.4: Implementación correcta de al menos 2 modelos en BigQuery ML (8 Pts)           |
+-----------------------------------------------------------------------------------------------+
```
* **Qué mostrar en pantalla:**
  En el panel izquierdo de BigQuery, despliega `nyc_taxi_dw > Modelos` mostrando:
  * `model_fare_linear_reg`
  * `model_fare_boosted_tree`
  Abre el archivo `sql/05_bqml_models.sql`.
* **Qué decir:**
  > *"Entrenamos dos modelos predictivos in-database con BigQuery ML sobre la vista preparada `vw_bqml_training_data`:*
  > 1. ***Modelo 1 (LINEAR_REG):** Regresión lineal Ridge con regularización L2 (`l2_reg = 0.1`) para penalizar pesos y evitar sobreajuste, con 25 iteraciones.*
  > 2. ***Modelo 2 (BOOSTED_TREE_REGRESSOR):** Árboles potenciados por gradiente (XGBoost) con hiperparámetros explícitos: 20 árboles (`max_iterations = 20`), tasa de aprendizaje `learn_rate = 0.2`, profundidad máxima de 6 niveles (`max_tree_depth = 6`) y submuestreo del 80% (`subsample = 0.8`).*
  > *Ambos modelos compilaron y entrenaron exitosamente sin errores de sintaxis."*

---

```
+-----------------------------------------------------------------------------------------------+
| CRITERIO 1.5: Evaluación y comparación entre modelos con métricas e hiperparámetros (12 Pts)  |
+-----------------------------------------------------------------------------------------------+
```
* **Qué mostrar en pantalla:**
  Copia y ejecuta en el editor de BigQuery esta consulta de evaluación:
  ```sql
  SELECT 
      'Modelo 1: Linear Reg' AS modelo, 
      ROUND(mean_absolute_error, 2) AS mae_usd, 
      ROUND(SQRT(mean_squared_error), 2) AS rmse_usd, 
      ROUND(r2_score, 4) AS r2_score 
  FROM ML.EVALUATE(
      MODEL `nyc_taxi_dw.model_fare_linear_reg`, 
      (SELECT * FROM `nyc_taxi_dw.vw_bqml_training_data` WHERE is_eval_split = TRUE)
  )
  UNION ALL
  SELECT 
      'Modelo 2: Boosted Tree (XGBoost)' AS modelo, 
      ROUND(mean_absolute_error, 2) AS mae_usd, 
      ROUND(SQRT(mean_squared_error), 2) AS rmse_usd, 
      ROUND(r2_score, 4) AS r2_score 
  FROM ML.EVALUATE(
      MODEL `nyc_taxi_dw.model_fare_boosted_tree`, 
      (SELECT * FROM `nyc_taxi_dw.vw_bqml_training_data` WHERE is_eval_split = TRUE)
  );
  ```
* **Qué decir:**
  > *"Evaluamos ambos modelos mediante la función nativa `ML.EVALUATE` sobre el conjunto independiente de evaluación (Septiembre-Octubre de 2022):*
  > - *El Boosted Tree reduce el MAE de **$1.95 a $1.62 USD** (su error promedio es de solo $1.62).*
  > - *Reduce el RMSE de **$3.66 a $3.44 USD**.*
  > - *Y alcanza un coeficiente $R^2$ de **0.9345**, explicando el **93.45% de la varianza total** de las tarifas.*
  > *Justificación de selección: Seleccionamos el Boosted Tree porque el tráfico de la ciudad de Nueva York no es lineal; recorrer 2 millas en hora pico en Manhattan cuesta y tarda mucho más que de madrugada. El modelo de ensamble de árboles mapea esas interacciones complejas de forma significativamente superior a la regresión lineal."*
* **Tabla comparativa de métricas:**

| Métrica | Modelo 1: Regresión Lineal | Modelo 2: Boosted Tree (XGBoost) | Ganador |
|---|:---:|:---:|:---:|
| **MAE (Error Absoluto Medio)** | $1.95 USD | **$1.62 USD** | Boosted Tree |
| **RMSE (Raíz del Error Cuadrático)** | $3.66 USD | **$3.44 USD** | Boosted Tree |
| **$R^2$ (Varianza Explicada)** | 0.9260 (92.6%) | **0.9345 (93.45%)** | Boosted Tree |

---

```
+-----------------------------------------------------------------------------------------------+
| CRITERIO 1.6: Prevención de data leakage y manejo correcto del split de datos (12 Pts)         |
+-----------------------------------------------------------------------------------------------+
```
* **Qué mostrar en pantalla:**
  Abre [sql/05_bqml_models.sql](file:///c:/Users/Enner/Desktop/SS22S2026_G1/Proyecto_2/sql/05_bqml_models.sql) y resalta las líneas 16 a 47 donde se define la vista y el parámetro `is_eval_split`.
* **Qué decir:**
  > *"Para prevenir fugas de información (*Data Leakage*), implementamos dos defensas metodológicas:*
  > 
  > 1. ***Prevención de Target Leakage (Variables Post-Evento):** Excluimos terminantemente variables que no existen al momento de abordar el taxi: `tpep_dropoff_datetime`, `trip_duration_minutes`, `tip_amount`, `tolls_amount` y `total_amount`. Solo usamos características ex-ante (hora de inicio, día, distancia estimada, zonas y si es hora pico).*
  > 
  > 2. ***Prevención de Temporal Leakage (Split Cronológico vs data_split_eval_fraction):** BigQuery ML utiliza por defecto `data_split_eval_fraction` con split aleatorio. En series temporales de demanda, esto es un error metodológico grave porque mezcla viajes de diciembre en el entrenamiento para predecir viajes de enero (fuga del futuro al pasado).*
  > *Por ello, configuramos `data_split_method = 'CUSTOM'` gobernado por la columna lógica `is_eval_split`:*
  >    - *Train Set (Ene-Ago 2022, ~70%): `is_eval_split = FALSE`.*
  >    - *Eval Set (Sep-Oct 2022, ~15%): `is_eval_split = TRUE`.*
  >    - *Test Set (Nov-Dic 2022, ~15%): Aislado totalmente para el Rolling Forecast."*

---

## 2. CONOCIMIENTOS (40 PUNTOS)

```
+-----------------------------------------------------------------------------------------------+
| CRITERIO 2.1: Análisis correcto de patrones y tendencias (10 Pts)                             |
+-----------------------------------------------------------------------------------------------+
```
* **Qué mostrar en pantalla:**
  Pestaña de [Looker Studio](https://lookerstudio.google.com/reporting/6f35e95a-771b-4ab3-86b8-b912086bfdea) en la **Página 2 (EDA)**.
* **Qué decir:**
  > *"Del análisis exploratorio sustentamos 3 hallazgos estructurales clave del negocio:*
  > 1. ***Patrón bimodal de demanda:** En días laborales la demanda presenta dos picos pronunciados: 8:00 AM (entrada a oficinas) y 6:00 PM (salida laboral), mientras que los fines de semana la demanda se traslada a la noche y madrugada.*
  > 2. ***Impacto de viajes a aeropuertos:** Los viajes a JFK y LaGuardia representan solo el **7.8% del volumen**, pero generan el **22.4% de la facturación bruta** debido a las tarifas reguladas fijas y recargos oficiales.*
  > 3. ***Dominio del cobro electrónico:** El **79.7% de las transacciones se realizan con tarjeta de crédito**, con una propina promedio del 18.5%, mientras que en efectivo la propina registrada es prácticamente cero debido al cobro directo."*

---

```
+-----------------------------------------------------------------------------------------------+
| CRITERIO 2.2: Visualización de resultados exploratorios y predicciones (10 Pts)               |
+-----------------------------------------------------------------------------------------------+
```
* **Qué mostrar en pantalla:**
  Abre [Looker Studio](https://lookerstudio.google.com/reporting/6f35e95a-771b-4ab3-86b8-b912086bfdea).
  1. **Página 1 (Rolling Forecast):**
     * Señala las tarjetas Scorecard: **MAE Boosted Trees ($1.66 - $1.72)**, **MAE Linear ($1.90 - $1.95)** y el total de **2,970,631 viajes evaluados**.
     * Pasa el ratón sobre la gráfica de líneas mostrando las tres curvas: Azul (Real), Naranja (Boosted Tree) y Celeste (Linear Reg).
  2. **Página 2 (EDA Exploratorio):**
     * Cambia de página en el menú lateral.
     * Muestra las 3 visualizaciones requeridas:
       - Gráfico de barras de demanda en 24 horas del día.
       - Gráfico circular de métodos de pago (**79.7% Tarjeta vs 20.3% Efectivo**).
       - Gráfico de tarifa promedio por día de la semana con el control interactivo `is_weekend` (filtra por `1` para mostrar la interactividad).
* **Qué decir:**
  > *"Conectamos Looker Studio de forma nativa a BigQuery sin costo alguno:*
  > - *En la Página 1 tenemos el Rolling Forecast con casi 3 millones de registros nuevos no vistos durante el entrenamiento (Noviembre-Diciembre). La curva naranja del Boosted Tree replica con gran precisión la volatilidad diaria de las tarifas reales.*
  > - *En la Página 2 presentamos el EDA con las 3 visualizaciones solicitadas y filtros dinámicos en tiempo real."*

---

```
+-----------------------------------------------------------------------------------------------+
| CRITERIO 2.3: Ingeniería de características y justificación de variables (10 Pts)             |
+-----------------------------------------------------------------------------------------------+
```
* **Qué mostrar en pantalla:**
  Abre la sección 6.3 del [README.md](file:///c:/Users/Enner/Desktop/SS22S2026_G1/Proyecto_2/README.md) con la tabla de variables derivadas.
* **Qué decir:**
  > *"Construimos **9 variables derivadas** con sólida justificación operativa y matemática:*
  > 1. *`trip_duration_minutes`: Calculada como `TIMESTAMP_DIFF(dropoff, pickup, SECOND)/60.0`.*
  > 2. *`trip_speed_mph`: Velocidad promedio calculada como `distancia / (minutos / 60)`. Permite descartar trayectos con velocidades anómalas superiores a 75 mph.*
  > 3. *`pickup_hour`: Captura el ciclo circadiano horario (0 a 23h).*
  > 4. *`pickup_day_of_week`: Modela la variación entre días hábiles y descanso.*
  > 5. *`is_weekend`: Bandera binaria para aislar la dinámica nocturna y recreativa.*
  > 6. *`is_rush_hour`: Horas pico laborales (7:00 a 9:30 AM y 16:00 a 19:30 PM de lunes a viernes).*
  > 7. *`is_airport_trip`: Identifica viajes hacia JFK (132), LaGuardia (138) y Newark (1).*
  > 8. *`tip_ratio`: Relación `tip_amount / fare_amount`.*
  > 9. *`split_flag`: Segmentación cronológica para anular la fuga de datos en BigQuery ML."*

---

```
+-----------------------------------------------------------------------------------------------+
| CRITERIO 2.4: Identificación de variables de entrada, salida y objetivo del modelo (5 Pts)    |
+-----------------------------------------------------------------------------------------------+
```
* **Qué mostrar en pantalla:**
  Abre la vista `vw_bqml_training_data` en [sql/05_bqml_models.sql](file:///c:/Users/Enner/Desktop/SS22S2026_G1/Proyecto_2/sql/05_bqml_models.sql).
* **Qué decir:**
  > *"Definimos con absoluta claridad los roles de cada variable:*
  > - ***Variable Objetivo (Label / Salida):** `fare_amount` (monto base de la tarifa en USD para problema de regresión supervisada).*
  > - ***Variables de Entrada (Features Ex-Ante):** `trip_distance`, `passenger_count`, `pickup_hour`, `pickup_day_of_week`, `is_weekend`, `is_rush_hour`, `is_airport_trip`, y las zonas como categóricas (`CAST(PULocationID AS STRING)`, `CAST(DOLocationID AS STRING)`, `CAST(RatecodeID AS STRING)`).*
  > - ***Propósito del modelo:** Predecir con exactitud el costo del servicio al momento en que el pasajero sube al taxi, eliminando variables que solo se conocen al finalizar el trayecto."*

---

```
+-----------------------------------------------------------------------------------------------+
| CRITERIO 2.5: Comparación entre consultas estándar y optimizadas (5 Pts)                      |
+-----------------------------------------------------------------------------------------------+
```
* **Qué mostrar en pantalla (DEMOSTRACIÓN EN VIVO DE BYTES):**
  1. En BigQuery Console, pega la consulta sobre la tabla **estándar**:
     ```sql
     SELECT COUNT(*), AVG(fare_amount), SUM(total_amount)
     FROM `nyc_taxi_dw.tbl_yellow_trips_standard`
     WHERE DATE(tpep_pickup_datetime) BETWEEN '2022-10-01' AND '2022-10-31';
     ```
     Señala arriba a la derecha: **"Esta consulta procesará 1.24 GB cuando se ejecute"**.
  2. En el mismo editor, cambia `standard` por `optimized`:
     ```sql
     SELECT COUNT(*), AVG(fare_amount), SUM(total_amount)
     FROM `nyc_taxi_dw.tbl_yellow_trips_optimized`
     WHERE DATE(tpep_pickup_datetime) BETWEEN '2022-10-01' AND '2022-10-31';
     ```
     Señala arriba a la derecha: El validador cae a **127.54 MB**.
* **Qué decir:**
  > *"Como se aprecia en tiempo real en el validador de BigQuery para una consulta de octubre:*
  > - *En la tabla estándar lee **1.24 GB** (escaneo de todo el año).*
  > - *En la tabla optimizada lee apenas **127.54 MB**.*
  > *Esto representa un **ahorro inmediato del 89.94% en bytes procesados** gracias a la poda de particiones.*
  > *Y en nuestra segunda prueba hacia el aeropuerto JFK, el ahorro llega al **95.47%** al combinar partición con el salto de bloques por cluster. En un entorno empresarial donde se facturan $6.25 por TB, esta técnica ahorra más del 90% del presupuesto de consultas analíticas."*
* **Tabla de Benchmarks Oficial:**

| Prueba Analítica | Filtros Aplicados | Bytes Estándar | Bytes Optimizada | % Reducción de Bytes |
|---|---|:---:|:---:|:---:|
| **Query 1: Filtro Temporal** | Octubre 2022 (31 días) | **1.24 GB** | **127.54 MB** | **89.94%** |
| **Query 2: Temporal + Geográfico** | Viajes a JFK en Septiembre | **2.23 GB** | **103.44 MB** | **95.47%** |
| **Query 3: Agregación Compleja** | Zonas top Manhattan y horas pico | **1.98 GB** | **171.22 MB** | **91.56%** |

---

## 3. CONSULTAS SQL DE EMERGENCIA (COPIAR Y PEGAR EN VIVO)

Ten estas 3 consultas listas en una pestaña de BigQuery por si te piden ejecutarlas al instante:

### Consulta A: Validación del Conteo Público (> 36M)
```sql
SELECT COUNT(*) AS total_registros
FROM `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2022`;
```

### Consulta B: Prueba de Bytes (Estándar vs Optimizada)
```sql
-- Ejecutar primero estándar y luego cambiar la palabra a optimized:
SELECT COUNT(*), AVG(fare_amount), SUM(total_amount)
FROM `nyc_taxi_dw.tbl_yellow_trips_optimized`
WHERE DATE(tpep_pickup_datetime) BETWEEN '2022-10-01' AND '2022-10-31';
```

### Consulta C: Métricas Comparativas de los Modelos de BQML
```sql
SELECT 'Modelo 1: Linear Reg' AS modelo, ROUND(mean_absolute_error, 2) AS mae, ROUND(SQRT(mean_squared_error), 2) AS rmse, ROUND(r2_score, 4) AS r2 
FROM ML.EVALUATE(MODEL `nyc_taxi_dw.model_fare_linear_reg`, (SELECT * FROM `nyc_taxi_dw.vw_bqml_training_data` WHERE is_eval_split = TRUE))
UNION ALL
SELECT 'Modelo 2: Boosted Tree' AS modelo, ROUND(mean_absolute_error, 2) AS mae, ROUND(SQRT(mean_squared_error), 2) AS rmse, ROUND(r2_score, 4) AS r2 
FROM ML.EVALUATE(MODEL `nyc_taxi_dw.model_fare_boosted_tree`, (SELECT * FROM `nyc_taxi_dw.vw_bqml_training_data` WHERE is_eval_split = TRUE));
```

---

## 4. BANCO DE PREGUNTAS TRAMPA DEL AUXILIAR

* **P: "¿Por qué particionaron por día y no por mes?"**
  > **R:** *"Porque las consultas analíticas y de auditoría de transporte operan sobre fechas concretas, fines de semana o quincenas. Si particionáramos por mes, cualquier consulta sobre un rango de 3 o 4 días obligaría a leer el mes completo. La partición diaria divide los datos en 365 bloques físicos contiguos, permitiendo podar con precisión y reducir los bytes leídos en casi un 90%."*

* **P: "¿Por qué no incluyeron la duración del viaje (`trip_duration_minutes`) en el modelo de ML?"**
  > **R:** *"Porque cometeríamos **Target Data Leakage**. La duración real del viaje solo se conoce cuando el pasajero se baja del taxi. Si la incluyéramos en el entrenamiento, el modelo tendría una precisión falsamente perfecta en laboratorio, pero al ponerlo en producción para predecir la tarifa cuando el usuario aborda el taxi, el modelo fallaría porque ese dato no existe."*

* **P: "¿Por qué rechazaron `data_split_eval_fraction`?"**
  > **R:** *"Porque `data_split_eval_fraction` utiliza un split aleatorio (Random Split). En series temporales de demanda, el split aleatorio mezcla viajes de noviembre y diciembre en el conjunto de entrenamiento para intentar predecir viajes de enero y febrero. Eso es **Temporal Leakage** (fuga del futuro al pasado). Por eso usamos `data_split_method = 'CUSTOM'` determinista por meses: Ene-Ago entrena, Sep-Oct evalúa y Nov-Dic prueba."*

* **P: "¿Por qué el Boosted Tree fue mejor que la Regresión Lineal?"**
  > **R:** *"La regresión lineal asume relaciones estrictamente lineales y aditivas. En el tráfico real de Nueva York, la relación entre distancia, hora y costo no es lineal: recorrer 2 millas en hora pico en Manhattan a las 8 AM cuesta y demora mucho más que recorrerlas a las 3 AM. El Boosted Tree (XGBoost) captura árboles de decisión que dividen no linealidades y combinaciones complejas de zonas y horarios, alcanzando un $R^2$ de 0.93 frente a 0.92 de la regresión."*

