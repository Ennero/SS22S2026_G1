# Guía de Configuración — Power BI con PBIP

## Prerequisitos

- **Power BI Desktop** versión reciente (2023 o posterior)
- **Docker Desktop** instalado y en ejecución
- Base de datos **VuelosDW** cargada con los datos del ETL de la Práctica 1

---

## Paso 1: Levantar SQL Server con datos

Desde la carpeta `Practica2`, ejecutar:

```bash
# Levantar SQL Server en Docker
docker compose up -d sqlserver

# Esperar a que esté healthy (~30s), luego ejecutar el ETL
docker compose run --rm etl
```

Esto levanta SQL Server en `localhost:1433` y carga la base de datos `VuelosDW` con el esquema estrella completo.

### Verificar la carga

```bash
docker exec -it ss2_sqlserver /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P "S2P1G1!2026" -C \
  -Q "USE VuelosDW; SELECT 'FactVuelos' AS Tabla, COUNT(*) AS Total FROM dbo.FactVuelos;"
```

---

## Paso 2: Habilitar Preview Features en Power BI Desktop

Abrir Power BI Desktop y navegar a:

**File → Options and settings → Options → Preview features**

Activar las siguientes opciones:

1. ✅ `Power BI Project (.pbip) save option`
2. ✅ `Store semantic model using TMDL format`
3. ✅ `Store reports using enhanced metadata format (PBIR)`

> **Reiniciar Power BI Desktop** después de habilitar estas opciones.

---

## Paso 3: Abrir el proyecto PBIP

1. Abrir Power BI Desktop
2. **File → Open → Browse**
3. Navegar a `Practica2/` y seleccionar `VuelosDW.pbip`
4. Power BI cargará automáticamente:
   - El **modelo semántico** (7 tablas, relaciones, medidas DAX)
   - El **reporte** (2 páginas con visualizaciones)

---

## Paso 4: Configurar la conexión a SQL Server

Cuando Power BI solicite las credenciales:

| Campo | Valor |
|---|---|
| **Servidor** | `localhost,1433` |
| **Base de datos** | `VuelosDW` |
| **Autenticación** | Database (SQL Server Authentication) |
| **Usuario** | `sa` |
| **Contraseña** | `S2P1G1!2026` |

> Si aparece advertencia de certificado, seleccionar "Aceptar" (el certificado Docker es auto-firmado).

---

## Paso 5: Actualizar datos

Una vez conectado, hacer clic en **Refresh** (⟳) en la barra de herramientas para cargar los datos desde SQL Server.

---

## Paso 6: Capturas del dashboard

Para los entregables, tomar capturas de:

1. **Página "Vista General"** — muestra KPIs, tendencia temporal, distribución por género y aerolíneas
2. **Página "Detalle Analítico"** — muestra matriz de precios, rango etario y rutas

Guardar las capturas en la carpeta `img/`.

---

## Solución de problemas

### Error al abrir el PBIP
- Verificar que las 3 preview features estén habilitadas
- Reiniciar Power BI Desktop

### Error de conexión a SQL Server
- Verificar que Docker está corriendo: `docker compose ps`
- Verificar que el puerto 1433 está expuesto: `docker port ss2_sqlserver`

### Las visualizaciones no muestran datos
- Hacer clic en **Refresh** para cargar los datos
- Verificar las credenciales de SQL Server
