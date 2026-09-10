# Guía de Configuración — Base de Datos, DBeaver y Power BI Desktop

## Prerrequisitos

- **Docker Desktop** instalado y en ejecución.
- **DBeaver** (o cualquier cliente SQL como Azure Data Studio / SSMS).
- **Microsoft Power BI Desktop** instalado.
- Base de datos **VuelosDW** cargada mediante el pipeline ETL.

---

## 1. Levantar SQL Server y Cargar los Datos

Desde una terminal en la carpeta `Practica2/`:

```bash
# 1. Iniciar SQL Server 2022 en Docker
docker compose up -d sqlserver

# 2. Esperar a que el contenedor esté 'healthy' (~30 segundos)
docker compose ps

# 3. Ejecutar el pipeline ETL (crea VuelosDW y carga las 7 tablas)
docker compose run --rm etl
```

### Verificar la carga desde la terminal:

```bash
docker exec -it ss2_sqlserver /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P "S2P1G1!2026" -C \
  -Q "USE VuelosDW; SELECT 'FactVuelos' AS Tabla, COUNT(*) AS Total FROM dbo.FactVuelos;"
```

---

## 2. Conexión a la Base de Datos con DBeaver

Para conectarte a `VuelosDW` desde DBeaver:

1. Abrir **DBeaver**.
2. Ir a **Base de datos → Nueva conexión**.
3. Seleccionar el controlador: **MS SQL Server / Microsoft SQL Server**.
4. Configurar los parámetros de conexión en la pestaña **General / Principal**:

| Parámetro | Valor |
|---|---|
| **Host / Servidor** | `localhost` |
| **Puerto** | `1433` |
| **Base de datos** | `VuelosDW` |
| **Autenticación** | `Autenticación de SQL Server` (Database Native) |
| **Nombre de usuario** | `sa` |
| **Contraseña** | `S2P1G1!2026` |

5. **Configuración de Certificado SSL (Muy Importante):**
   - Ir a la pestaña **Propiedades del controlador (Driver properties)**.
   - Buscar la propiedad `trustServerCertificate` y cambiar su valor a **`true`**.
   - (Alternativamente, en la pestaña **General**, activar la casilla *"Trust server certificate"* / *"Confiar en el certificado del servidor"*).
6. Presionar **Probar conexión (Test Connection)**. Debe mostrar `Conectado / Success`.
7. Hacer clic en **Finalizar**.

---

## 3. ¿Cómo demostrar que se manejan correctamente los NULLables? (Para la Evaluación)

Si el evaluador o docente te pregunta:  
> *"¿Cómo manejan los valores NULL en la base de datos y cómo garantizan que no afecten el modelo analítico ni las visualizaciones?"*

Puedes abrir un editor SQL en DBeaver y ejecutar las siguientes consultas de comprobación, explicando la justificación técnica de cada una:

### Prueba 1: Cero Llaves Foráneas Nulas (Integridad Referencial Absoluta)
En modelado dimensional (metodología Kimball), **las llaves foráneas de una tabla de hechos NUNCA deben ser NULL**, ya que provocarían registros huérfanos y relaciones rotas en Power BI.

```sql
USE [VuelosDW];
GO

-- Debe retornar 0 registros con FKs nulas
SELECT COUNT(*) AS total_fks_nulas
FROM dbo.FactVuelos
WHERE id_fecha IS NULL
   OR id_pasajero IS NULL
   OR id_aerolinea IS NULL
   OR id_origen IS NULL
   OR id_destino IS NULL
   OR id_clase IS NULL
   OR id_estado IS NULL;
```
> **Qué responder:** *"A nivel de DDL, todas las columnas FK en `FactVuelos` están definidas como `NOT NULL`. Además, en el ETL de Python se validó que si un registro no resolvía su llave foránea contra las dimensiones, se enviara al archivo de auditoría de rechazados para asegurar 100% de consistencia."*

---

### Prueba 2: Tratamiento de Nulos en Métricas Operativas (Cancelados y Desviados)
En el dataset crudo, los vuelos cancelados (`CANCELLED`) o desviados (`DIVERTED`) no registraban hora de llegada, duración ni retraso (`NaN`).

```sql
-- Demostrar que los vuelos cancelados tienen métricas consistentes en 0 en lugar de NULL descontrolado
SELECT 
    es.estado_vuelo,
    COUNT(*) AS total_vuelos,
    SUM(CASE WHEN fv.duracion_minutos IS NULL THEN 1 ELSE 0 END) AS nulos_duracion,
    SUM(CASE WHEN fv.retraso_minutos IS NULL THEN 1 ELSE 0 END) AS nulos_retraso,
    MIN(fv.duracion_minutos) AS min_duracion,
    MIN(fv.retraso_minutos) AS min_retraso
FROM dbo.FactVuelos fv
JOIN dbo.DimEstado es ON es.id_estado = fv.id_estado
GROUP BY es.estado_vuelo;
```
> **Qué responder:** *"En el proceso de limpieza (`cleaner.py`), los nulos en duración y retraso para vuelos cancelados/desviados se transformaron controladamente a `0`. Esto evita que las funciones de agregación fallen por tipos no homogéneos."*

---

### Prueba 3: Atributos Categóricos sin Nulos (Evitar '(En blanco)' en Power BI)
Si una dimensión contiene valores `NULL`, Power BI genera automáticamente la opción `(En blanco)` en filtros y segmentadores, lo cual perjudica la experiencia de usuario ejecutiva.

```sql
-- Verificar que las dimensiones usan 'DESCONOCIDO' en lugar de NULL
SELECT 'DimPasajero - Nacionalidad' AS campo, COUNT(*) AS total_desconocidos
FROM dbo.DimPasajero WHERE nacionalidad = 'DESCONOCIDO'
UNION ALL
SELECT 'FactVuelos - Canal Venta', COUNT(*)
FROM dbo.FactVuelos WHERE canal_venta = 'DESCONOCIDO';
```
> **Qué responder:** *"Para variables categóricas descriptivas donde faltaba información (como nacionalidad del pasajero o canal de venta), el ETL aplicó la regla de negocio de imputar el valor canónico `'DESCONOCIDO'`, eliminando etiquetas vacías en Power BI."*

---

### Prueba 4: Imputación Estadística en Datos Demográficos
```sql
-- Verificar que no hay pasajeros con edad nula tras la imputación por mediana
SELECT 
    COUNT(*) AS pasajeros_con_edad_nula,
    MIN(edad) AS edad_minima,
    MAX(edad) AS edad_maxima,
    AVG(edad) AS edad_promedio
FROM dbo.DimPasajero
WHERE edad IS NULL;
```
> **Qué responder:** *"Los registros que carecían de edad en el CSV no se descartaron; se imputaron utilizando la mediana de la población (evitando sesgar la media por valores extremos) y se clasificaron en rangos etarios coherentes."*

---

### Prueba 5: Validación de Completitud de Tablas
```sql
-- Estado global del modelo dimensional
SELECT 'DimFecha'      AS tabla, COUNT(*) AS total_filas FROM dbo.DimFecha      UNION ALL
SELECT 'DimPasajero'   AS tabla, COUNT(*) AS total_filas FROM dbo.DimPasajero   UNION ALL
SELECT 'DimAerolinea'  AS tabla, COUNT(*) AS total_filas FROM dbo.DimAerolinea  UNION ALL
SELECT 'DimAeropuerto' AS tabla, COUNT(*) AS total_filas FROM dbo.DimAeropuerto UNION ALL
SELECT 'DimClase'      AS tabla, COUNT(*) AS total_filas FROM dbo.DimClase      UNION ALL
SELECT 'DimEstado'     AS tabla, COUNT(*) AS total_filas FROM dbo.DimEstado     UNION ALL
SELECT 'FactVuelos'    AS tabla, COUNT(*) AS total_filas FROM dbo.FactVuelos;
```

---

## 4. Conexión y Construcción en Power BI Desktop (.pbix)

Como se trabajará directamente en Power BI Desktop:

### Paso 1: Conectar a SQL Server
1. Abrir **Power BI Desktop**.
2. En la cinta de inicio: **Obtener datos → SQL Server**.
3. En el diálogo de conexión:
   - **Servidor:** `localhost,1433`
   - **Base de datos:** `VuelosDW`
   - **Modo de conectividad:** **Importar** (recomendado para aprovechar el motor VertiPaq y funciones Time Intelligence de DAX).
4. Cuando solicite credenciales:
   - Seleccionar la pestaña **Base de datos** (Database).
   - **Nombre de usuario:** `sa`
   - **Contraseña:** `S2P1G1!2026`
   - Si advierte sobre soporte de cifrado / certificado: hacer clic en **Aceptar / Conectar**.
5. En el Navegador, marcar las 7 tablas:
   - `DimAerolinea`
   - `DimAeropuerto`
   - `DimClase`
   - `DimEstado`
   - `DimFecha`
   - `DimPasajero`
   - `FactVuelos`
6. Hacer clic en **Cargar**.

---

### Paso 2: Configurar las Relaciones del Modelo (Vista de Modelo)
En la pestaña **Modelo** de Power BI Desktop, verificar que las relaciones estén configuradas como **Muchos a Uno (N:1)** con **Dirección de filtro cruzado: Única**:

| Origen (Fact) | Destino (Dimensión) | Estado | Cardinalidad |
|---|---|:---:|:---:|
| `FactVuelos[id_fecha]` | `DimFecha[id_fecha]` | **Activa** | N:1 |
| `FactVuelos[id_pasajero]` | `DimPasajero[id_pasajero]` | **Activa** | N:1 |
| `FactVuelos[id_aerolinea]` | `DimAerolinea[id_aerolinea]` | **Activa** | N:1 |
| `FactVuelos[id_origen]` | `DimAeropuerto[id_aeropuerto]` | **Activa** | N:1 |
| `FactVuelos[id_destino]` | `DimAeropuerto[id_aeropuerto]` | **Inactiva** (Role-Playing) | N:1 |
| `FactVuelos[id_clase]` | `DimClase[id_clase]` | **Activa** | N:1 |
| `FactVuelos[id_estado]` | `DimEstado[id_estado]` | **Activa** | N:1 |

---

### Paso 3: Crear la Jerarquía de Fecha
1. En la tabla `DimFecha`, hacer clic derecho sobre la columna `anio`.
2. Seleccionar **Crear jerarquía** y nombrarla `Jerarquía Fecha`.
3. Hacer clic derecho sobre `trimestre` → **Agregar a la jerarquía** → `Jerarquía Fecha`.
4. Repetir agregando `nombre_mes` (o `mes`) y `dia`.
> Esto cumple con el requisito obligatorio de *"jerarquías en las dimensiones"* de la rúbrica.

---

### Paso 4: Crear las Medidas DAX
Crear una tabla para medidas o agregarlas en `FactVuelos`:

```dax
// 1. Total Vuelos
Total Vuelos = COUNTROWS(FactVuelos)

// 2. Ingresos Totales USD
Ingresos Totales USD = SUM(FactVuelos[precio_usd])

// 3. Precio Promedio USD
Precio Promedio USD = AVERAGE(FactVuelos[precio_usd])

// 4. Retraso Promedio Min (Filtrando cancelados para evitar sesgo)
Retraso Promedio Min = 
CALCULATE(
    AVERAGE(FactVuelos[retraso_minutos]),
    DimEstado[estado_vuelo] <> "CANCELLED"
)

// 5. Vuelos Cancelados
Vuelos Cancelados = 
CALCULATE(
    COUNTROWS(FactVuelos),
    DimEstado[estado_vuelo] = "CANCELLED"
)

// 6. Tasa Cancelación % (KPI Principal)
Tasa Cancelación % = 
DIVIDE(
    [Vuelos Cancelados],
    [Total Vuelos],
    0
) * 100

// 7. Crecimiento Mes a Mes (MoM % - Time Intelligence)
Crecimiento MoM % = 
VAR VuelosMesActual = [Total Vuelos]
VAR VuelosMesAnterior =
    CALCULATE(
        [Total Vuelos],
        DATEADD(DimFecha[fecha], -1, MONTH)
    )
RETURN
    IF(
        ISBLANK(VuelosMesAnterior),
        BLANK(),
        DIVIDE(
            VuelosMesActual - VuelosMesAnterior,
            VuelosMesAnterior,
            0
        ) * 100
    )

// 8. Vuelos Año Anterior (Comparación Interanual)
Vuelos Año Anterior = 
VAR AnioActual = SELECTEDVALUE(DimFecha[anio])
RETURN
CALCULATE(
    [Total Vuelos],
    REMOVEFILTERS(DimFecha[anio]),
    DimFecha[anio] = AnioActual - 1
)

// 9. Crecimiento Año a Año (YoY %)
Crecimiento YoY % = 
VAR VuelosActual = [Total Vuelos]
VAR VuelosAnterior = [Vuelos Año Anterior]
RETURN
IF(
    ISBLANK(VuelosAnterior) || VuelosAnterior = 0,
    BLANK(),
    DIVIDE(VuelosActual - VuelosAnterior, VuelosAnterior, 0)
)

// 10. Semáforo Cancelación (Indicador condicional)
Semáforo Cancelación = 
VAR Tasa = [Tasa Cancelación %]
RETURN
    SWITCH(
        TRUE(),
        Tasa <= 5, 1,   // Verde (Óptimo <= 5%)
        Tasa <= 10, 2,  // Amarillo (Alerta preventiva 5% a 10%)
        3               // Rojo (Crítico > 10%)
    )
```

---

### Paso 5: Guardar el Archivo y Capturas
1. Guardar el informe como:
   ```
   Practica2/VuelosDW.pbix
   ```
2. Tomar capturas claras del dashboard (Página 1 y Página 2).
3. Guardarlas en la carpeta:
   ```
   Practica2/img/
   ```
