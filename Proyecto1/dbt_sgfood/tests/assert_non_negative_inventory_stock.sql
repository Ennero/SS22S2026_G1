-- Prueba de calidad: El stock disponible en bodega no debe ser negativo
SELECT
    id_sucursal,
    id_producto,
    stock_disponible
FROM {{ ref('stg_inventario') }}
WHERE stock_disponible < 0
