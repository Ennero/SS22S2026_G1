-- Prueba de calidad: Ninguna venta debe tener cantidad vendida menor o igual a cero
SELECT
    id_detalle,
    cantidad
FROM {{ ref('stg_ventas_detalle') }}
WHERE cantidad <= 0
