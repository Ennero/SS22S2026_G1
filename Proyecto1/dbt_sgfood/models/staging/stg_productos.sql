WITH source AS (
    SELECT * FROM {{ source('raw', 'producto') }}
),

renamed AS (
    SELECT
        id_producto::INTEGER AS id_producto,
        TRIM(sku) AS sku,
        TRIM(nombre) AS producto_nombre,
        id_categoria::INTEGER AS id_categoria,
        id_marca::INTEGER AS id_marca,
        TRIM(unidad_medida) AS unidad_medida,
        costo_base::NUMERIC(12,2) AS costo_base,
        precio_lista::NUMERIC(12,2) AS precio_lista,
        activo::BOOLEAN AS es_activo
    FROM source
)

SELECT * FROM renamed
