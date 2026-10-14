WITH devoluciones AS (
    SELECT * FROM {{ ref('stg_devoluciones') }}
),

ventas AS (
    SELECT * FROM {{ ref('stg_ventas') }}
),

productos AS (
    SELECT * FROM {{ ref('stg_productos') }}
)

SELECT
    MD5(d.id_devolucion::TEXT) AS fct_devolucion_sk,
    d.id_devolucion,
    TO_CHAR(d.fecha_devolucion, 'YYYYMMDD')::INTEGER AS fecha_id,
    d.fecha_devolucion,
    d.id_venta,
    MD5(v.id_sucursal::TEXT) AS dim_sucursal_sk,
    v.id_sucursal,
    MD5(d.id_producto::TEXT) AS dim_producto_sk,
    d.id_producto,
    d.cantidad_devuelta,
    d.motivo_devolucion,
    ROUND(d.cantidad_devuelta * p.precio_lista, 2) AS monto_estimado_devolucion
FROM devoluciones d
LEFT JOIN ventas v ON d.id_venta = v.id_venta
LEFT JOIN productos p ON d.id_producto = p.id_producto
