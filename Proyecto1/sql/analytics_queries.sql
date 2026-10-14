-- ==============================================================================
-- Proyecto 1: SG-Food Data Warehouse
-- Consultas Analíticas y de Validación de Negocio
-- Base de datos: sgfood_dw (PostgreSQL)
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. VALIDACIÓN DE CARGA COMPLETA POR TABLA EN MARTS
-- ------------------------------------------------------------------------------
SELECT 'dim_sucursal' AS tabla, COUNT(*) AS total_filas FROM marts.dim_sucursal UNION ALL
SELECT 'dim_categoria', COUNT(*) FROM marts.dim_categoria UNION ALL
SELECT 'dim_marca', COUNT(*) FROM marts.dim_marca UNION ALL
SELECT 'dim_producto', COUNT(*) FROM marts.dim_producto UNION ALL
SELECT 'dim_cliente', COUNT(*) FROM marts.dim_cliente UNION ALL
SELECT 'dim_proveedor', COUNT(*) FROM marts.dim_proveedor UNION ALL
SELECT 'dim_promocion', COUNT(*) FROM marts.dim_promocion UNION ALL
SELECT 'dim_fecha', COUNT(*) FROM marts.dim_fecha UNION ALL
SELECT 'fct_ventas', COUNT(*) FROM marts.fct_ventas UNION ALL
SELECT 'fct_inventario', COUNT(*) FROM marts.fct_inventario UNION ALL
SELECT 'fct_devoluciones', COUNT(*) FROM marts.fct_devoluciones UNION ALL
SELECT 'fct_rendimiento_metas', COUNT(*) FROM marts.fct_rendimiento_metas
ORDER BY tabla;


-- ------------------------------------------------------------------------------
-- 2. DESEMPEÑO FINANCIERO POR SUCURSAL (INGRESOS, COSTOS Y MARGEN BRUTO)
-- ------------------------------------------------------------------------------
SELECT
    s.sucursal_nombre,
    s.ciudad,
    s.departamento,
    COUNT(DISTINCT v.id_venta) AS total_transacciones,
    SUM(v.cantidad) AS total_unidades_vendidas,
    SUM(v.importe_bruto) AS total_ventas_brutas,
    SUM(v.monto_descuento) AS total_descuentos_otorgados,
    SUM(v.importe_neto) AS total_ventas_netas,
    SUM(v.costo_total) AS total_costo,
    SUM(v.margen_ganancia) AS margen_bruto_total,
    ROUND((SUM(v.margen_ganancia) / NULLIF(SUM(v.importe_neto), 0)) * 100, 2) AS margen_porcentual
FROM marts.fct_ventas v
JOIN marts.dim_sucursal s ON v.dim_sucursal_sk = s.dim_sucursal_sk
WHERE v.estado_venta <> 'CANCELADA'
GROUP BY s.sucursal_nombre, s.ciudad, s.departamento
ORDER BY total_ventas_netas DESC;


-- ------------------------------------------------------------------------------
-- 3. TOP 10 PRODUCTOS MÁS VENDIDOS Y RENTABILIDAD
-- ------------------------------------------------------------------------------
SELECT
    p.sku,
    p.producto_nombre,
    p.categoria_nombre,
    p.marca_nombre,
    SUM(v.cantidad) AS unidades_vendidas,
    SUM(v.importe_neto) AS ingresos_netos,
    SUM(v.margen_ganancia) AS ganancia_generada,
    ROUND((SUM(v.margen_ganancia) / NULLIF(SUM(v.importe_neto), 0)) * 100, 2) AS margen_pct
FROM marts.fct_ventas v
JOIN marts.dim_producto p ON v.dim_producto_sk = p.dim_producto_sk
WHERE v.estado_venta <> 'CANCELADA'
GROUP BY p.sku, p.producto_nombre, p.categoria_nombre, p.marca_nombre
ORDER BY unidades_vendidas DESC
LIMIT 10;


-- ------------------------------------------------------------------------------
-- 4. EVALUACIÓN DE CUMPLIMIENTO DE METAS DE VENTAS MENSUALES
-- ------------------------------------------------------------------------------
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
JOIN marts.dim_sucursal s ON m.dim_sucursal_sk = s.dim_sucursal_sk
ORDER BY m.periodo_mes, s.sucursal_nombre;


-- ------------------------------------------------------------------------------
-- 5. ALERTAS DE INVENTARIO: PRODUCTOS AGOTADOS O EN ESTADO CRÍTICO
-- ------------------------------------------------------------------------------
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
JOIN marts.dim_sucursal s ON i.dim_sucursal_sk = s.dim_sucursal_sk
JOIN marts.dim_producto p ON i.dim_producto_sk = p.dim_producto_sk
WHERE i.estado_stock IN ('Agotado', 'Crítico')
ORDER BY i.fecha_corte DESC, i.stock_disponible ASC
LIMIT 20;


-- ------------------------------------------------------------------------------
-- 6. ALERTAS DE VENCIMIENTO DE PRODUCTOS EN BODEGA
-- ------------------------------------------------------------------------------
SELECT
    i.fecha_corte,
    s.sucursal_nombre,
    p.producto_nombre,
    i.lote,
    i.fecha_vencimiento,
    i.dias_para_vencer,
    i.alerta_vencimiento,
    i.stock_disponible,
    i.valor_inventario_costo
FROM marts.fct_inventario i
JOIN marts.dim_sucursal s ON i.dim_sucursal_sk = s.dim_sucursal_sk
JOIN marts.dim_producto p ON i.dim_producto_sk = p.dim_producto_sk
WHERE i.alerta_vencimiento IN ('Vencido', 'Próximo a Vencer')
ORDER BY i.fecha_vencimiento ASC
LIMIT 20;


-- ------------------------------------------------------------------------------
-- 7. ANÁLISIS DE DEVOLUCIONES POR MOTIVO
-- ------------------------------------------------------------------------------
SELECT
    d.motivo_devolucion,
    COUNT(*) AS total_eventos_devolucion,
    SUM(d.cantidad_devuelta) AS total_unidades_devueltas,
    SUM(d.monto_estimado_devolucion) AS monto_total_devuelto
FROM marts.fct_devoluciones d
GROUP BY d.motivo_devolucion
ORDER BY total_unidades_devueltas DESC;


-- ------------------------------------------------------------------------------
-- 8. COMPORTAMIENTO POR CANAL DE VENTA Y MÉTODO DE PAGO
-- ------------------------------------------------------------------------------
SELECT
    v.canal_venta,
    v.metodo_pago,
    COUNT(DISTINCT v.id_venta) AS total_pedidos,
    SUM(v.importe_neto) AS facturacion_total,
    ROUND(AVG(v.importe_neto), 2) AS ticket_promedio
FROM marts.fct_ventas v
WHERE v.estado_venta <> 'CANCELADA'
GROUP BY v.canal_venta, v.metodo_pago
ORDER BY facturacion_total DESC;
