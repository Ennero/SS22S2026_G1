WITH ventas AS (
    SELECT * FROM {{ ref('stg_ventas') }}
),

detalles AS (
    SELECT * FROM {{ ref('stg_ventas_detalle') }}
),

productos AS (
    SELECT * FROM {{ ref('stg_productos') }}
)

SELECT
    d.id_detalle,
    v.id_venta,
    v.fecha_venta,
    v.id_cliente,
    v.id_sucursal,
    d.id_producto,
    p.id_categoria,
    p.id_marca,
    v.canal_venta,
    v.metodo_pago,
    v.estado_venta,
    d.cantidad,
    d.precio_unitario,
    d.porcentaje_descuento,
    ROUND(d.cantidad * d.precio_unitario, 2) AS importe_bruto,
    ROUND((d.cantidad * d.precio_unitario) * d.porcentaje_descuento, 2) AS monto_descuento,
    d.subtotal AS importe_neto,
    ROUND(d.cantidad * p.costo_base, 2) AS costo_total,
    ROUND(d.subtotal - (d.cantidad * p.costo_base), 2) AS margen_ganancia,
    CASE
        WHEN d.subtotal > 0 THEN ROUND((d.subtotal - (d.cantidad * p.costo_base)) / d.subtotal, 4)
        ELSE 0
    END AS porcentaje_margen
FROM detalles d
JOIN ventas v ON d.id_venta = v.id_venta
JOIN productos p ON d.id_producto = p.id_producto
