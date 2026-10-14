-- Prueba de calidad: Ningún detalle de venta debe tener un descuento menor a 0 o mayor al 100% (1.0)
SELECT
    id_detalle,
    porcentaje_descuento
FROM {{ ref('stg_ventas_detalle') }}
WHERE porcentaje_descuento < 0 OR porcentaje_descuento > 1.0
