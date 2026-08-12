-- ============================================================
-- sql/queries/analytics.sql
-- Consultas Analíticas — VuelosDW (Esquema Estrella)
-- SQL Server 2022
--
-- Ejecutar contra la base de datos VuelosDW.
-- Cada consulta está numerada y comentada según los requerimientos
-- de la sección 10 del PROJECT_CONTEXT.md.
-- ============================================================

USE [VuelosDW];
GO

-- ============================================================
-- 1. VALIDACIÓN DE CARGA
--    Conteo total de registros en cada tabla del modelo estrella.
-- ============================================================
SELECT 'DimFecha'      AS tabla, COUNT(*) AS total_filas FROM dbo.DimFecha      UNION ALL
SELECT 'DimPasajero'   AS tabla, COUNT(*) AS total_filas FROM dbo.DimPasajero   UNION ALL
SELECT 'DimAerolinea'  AS tabla, COUNT(*) AS total_filas FROM dbo.DimAerolinea  UNION ALL
SELECT 'DimAeropuerto' AS tabla, COUNT(*) AS total_filas FROM dbo.DimAeropuerto UNION ALL
SELECT 'DimClase'      AS tabla, COUNT(*) AS total_filas FROM dbo.DimClase      UNION ALL
SELECT 'DimEstado'     AS tabla, COUNT(*) AS total_filas FROM dbo.DimEstado     UNION ALL
SELECT 'FactVuelos'    AS tabla, COUNT(*) AS total_filas FROM dbo.FactVuelos
ORDER BY tabla;
GO

-- ============================================================
-- 2. TOP 5 DESTINOS MÁS FRECUENTES
--    (excluye vuelos cancelados para reflejar destinos reales)
-- ============================================================
SELECT TOP 5
    ap.codigo_iata          AS destino,
    COUNT(fv.id_vuelo)      AS total_vuelos
FROM dbo.FactVuelos  fv
JOIN dbo.DimAeropuerto ap ON ap.id_aeropuerto = fv.id_destino
JOIN dbo.DimEstado     es ON es.id_estado     = fv.id_estado
WHERE es.estado_vuelo <> 'CANCELLED'
GROUP BY ap.codigo_iata
ORDER BY total_vuelos DESC;
GO

-- ============================================================
-- 3. DISTRIBUCIÓN DE PASAJEROS POR GÉNERO
-- ============================================================
SELECT
    p.genero,
    COUNT(DISTINCT fv.id_pasajero)  AS pasajeros_unicos,
    COUNT(fv.id_vuelo)              AS total_vuelos
FROM dbo.FactVuelos  fv
JOIN dbo.DimPasajero p ON p.id_pasajero = fv.id_pasajero
GROUP BY p.genero
ORDER BY total_vuelos DESC;
GO

-- ============================================================
-- 4. VUELOS AGRUPADOS POR MES Y AÑO
-- ============================================================
SELECT
    f.anio,
    f.mes,
    f.nombre_mes,
    COUNT(fv.id_vuelo)          AS total_vuelos,
    SUM(fv.precio_usd)          AS ingresos_usd,
    AVG(fv.duracion_minutos)    AS duracion_promedio_min
FROM dbo.FactVuelos fv
JOIN dbo.DimFecha   f  ON f.id_fecha = fv.id_fecha
GROUP BY f.anio, f.mes, f.nombre_mes
ORDER BY f.anio, f.mes;
GO

-- ============================================================
-- 5. AEROLÍNEA CON MAYOR NÚMERO DE VUELOS
-- ============================================================
SELECT TOP 10
    a.codigo_iata,
    a.nombre_aerolinea,
    COUNT(fv.id_vuelo)          AS total_vuelos,
    SUM(fv.precio_usd)          AS ingresos_totales_usd,
    AVG(fv.duracion_minutos)    AS duracion_promedio_min,
    SUM(CASE WHEN es.estado_vuelo = 'CANCELLED' THEN 1 ELSE 0 END) AS vuelos_cancelados
FROM dbo.FactVuelos   fv
JOIN dbo.DimAerolinea a  ON a.id_aerolinea = fv.id_aerolinea
JOIN dbo.DimEstado    es ON es.id_estado   = fv.id_estado
GROUP BY a.codigo_iata, a.nombre_aerolinea
ORDER BY total_vuelos DESC;
GO

-- ============================================================
-- 6. (OPCIONAL) PRECIO PROMEDIO POR RUTA
--    Ruta = origen → destino
-- ============================================================
SELECT TOP 20
    orig.codigo_iata        AS origen,
    dest.codigo_iata        AS destino,
    COUNT(fv.id_vuelo)      AS total_vuelos,
    ROUND(AVG(fv.precio_usd), 2)    AS precio_promedio_usd,
    ROUND(MIN(fv.precio_usd), 2)    AS precio_minimo_usd,
    ROUND(MAX(fv.precio_usd), 2)    AS precio_maximo_usd,
    AVG(fv.duracion_minutos)        AS duracion_promedio_min
FROM dbo.FactVuelos    fv
JOIN dbo.DimAeropuerto orig ON orig.id_aeropuerto = fv.id_origen
JOIN dbo.DimAeropuerto dest ON dest.id_aeropuerto = fv.id_destino
WHERE fv.precio_usd IS NOT NULL
GROUP BY orig.codigo_iata, dest.codigo_iata
HAVING COUNT(fv.id_vuelo) >= 5
ORDER BY total_vuelos DESC;
GO

-- ============================================================
-- 7. (OPCIONAL) PRECIO PROMEDIO POR AEROLÍNEA Y CLASE DE CABINA
-- ============================================================
SELECT
    a.nombre_aerolinea,
    c.clase_cabina,
    COUNT(fv.id_vuelo)              AS total_vuelos,
    ROUND(AVG(fv.precio_usd), 2)    AS precio_promedio_usd
FROM dbo.FactVuelos   fv
JOIN dbo.DimAerolinea a  ON a.id_aerolinea = fv.id_aerolinea
JOIN dbo.DimClase     c  ON c.id_clase     = fv.id_clase
GROUP BY a.nombre_aerolinea, c.clase_cabina
ORDER BY a.nombre_aerolinea, c.clase_cabina;
GO

-- ============================================================
-- 8. (OPCIONAL) TASA DE CANCELACIÓN POR AEROLÍNEA
-- ============================================================
SELECT
    a.codigo_iata,
    a.nombre_aerolinea,
    COUNT(fv.id_vuelo)                                              AS total_vuelos,
    SUM(CASE WHEN es.estado_vuelo = 'CANCELLED' THEN 1 ELSE 0 END) AS cancelados,
    ROUND(
        100.0 * SUM(CASE WHEN es.estado_vuelo = 'CANCELLED' THEN 1 ELSE 0 END)
        / NULLIF(COUNT(fv.id_vuelo), 0),
        2
    )                                                               AS tasa_cancelacion_pct
FROM dbo.FactVuelos   fv
JOIN dbo.DimAerolinea a  ON a.id_aerolinea = fv.id_aerolinea
JOIN dbo.DimEstado    es ON es.id_estado   = fv.id_estado
GROUP BY a.codigo_iata, a.nombre_aerolinea
ORDER BY tasa_cancelacion_pct DESC;
GO

-- ============================================================
-- 9. (OPCIONAL) DISTRIBUCIÓN POR RANGO ETARIO Y CLASE DE CABINA
-- ============================================================
SELECT
    p.rango_etario,
    c.clase_cabina,
    COUNT(fv.id_vuelo)  AS total_vuelos
FROM dbo.FactVuelos  fv
JOIN dbo.DimPasajero p ON p.id_pasajero = fv.id_pasajero
JOIN dbo.DimClase    c ON c.id_clase    = fv.id_clase
GROUP BY p.rango_etario, c.clase_cabina
ORDER BY p.rango_etario, c.clase_cabina;
GO

-- ============================================================
-- 10. RETRASO PROMEDIO POR ESTADO DE VUELO
-- ============================================================
SELECT
    es.estado_vuelo,
    COUNT(fv.id_vuelo)              AS total_vuelos,
    AVG(fv.retraso_minutos)         AS retraso_promedio_min,
    MAX(fv.retraso_minutos)         AS retraso_maximo_min
FROM dbo.FactVuelos fv
JOIN dbo.DimEstado  es ON es.id_estado = fv.id_estado
GROUP BY es.estado_vuelo
ORDER BY retraso_promedio_min DESC;
GO
