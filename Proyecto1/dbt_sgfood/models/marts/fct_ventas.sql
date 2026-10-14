WITH ventas_enriquecidas AS (
    SELECT * FROM {{ ref('int_ventas_enriquecidas') }}
)

SELECT
    MD5(v.id_detalle::TEXT) AS fct_venta_sk,
    v.id_detalle,
    v.id_venta,
    TO_CHAR(v.fecha_venta, 'YYYYMMDD')::INTEGER AS fecha_id,
    v.fecha_venta,
    MD5(v.id_cliente::TEXT) AS dim_cliente_sk,
    v.id_cliente,
    MD5(v.id_sucursal::TEXT) AS dim_sucursal_sk,
    v.id_sucursal,
    MD5(v.id_producto::TEXT) AS dim_producto_sk,
    v.id_producto,
    v.canal_venta,
    v.metodo_pago,
    v.estado_venta,
    v.cantidad,
    v.precio_unitario,
    v.porcentaje_descuento,
    v.importe_bruto,
    v.monto_descuento,
    v.importe_neto,
    v.costo_total,
    v.margen_ganancia,
    v.porcentaje_margen
FROM ventas_enriquecidas v
