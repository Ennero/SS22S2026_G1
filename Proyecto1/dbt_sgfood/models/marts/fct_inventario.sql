WITH inventario_estado AS (
    SELECT * FROM {{ ref('int_inventario_estado') }}
)

SELECT
    MD5(CONCAT(i.fecha_corte::TEXT, '-', i.id_sucursal::TEXT, '-', i.id_producto::TEXT, '-', i.lote)) AS fct_inventario_sk,
    TO_CHAR(i.fecha_corte, 'YYYYMMDD')::INTEGER AS fecha_id,
    i.fecha_corte,
    MD5(i.id_sucursal::TEXT) AS dim_sucursal_sk,
    i.id_sucursal,
    MD5(i.id_producto::TEXT) AS dim_producto_sk,
    i.id_producto,
    i.lote,
    i.fecha_vencimiento,
    i.stock_disponible,
    i.stock_minimo,
    i.stock_maximo,
    i.diferencia_stock_min,
    i.estado_stock,
    i.dias_para_vencer,
    i.alerta_vencimiento,
    i.valor_inventario_costo
FROM inventario_estado i
