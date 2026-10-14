-- Prueba de calidad: Ningún producto debe tener precio de lista o costo base negativo
SELECT
    id_producto,
    precio_lista,
    costo_base
FROM {{ ref('stg_productos') }}
WHERE precio_lista < 0 OR costo_base < 0
