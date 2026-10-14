WITH source AS (
    SELECT * FROM {{ source('raw', 'proveedores_precios') }}
),

renamed AS (
    SELECT
        id_proveedor::INTEGER AS id_proveedor,
        TRIM(proveedor) AS proveedor_nombre,
        id_producto::INTEGER AS id_producto,
        costo_proveedor::NUMERIC(12,2) AS costo_proveedor,
        plazo_dias::INTEGER AS plazo_entrega_dias,
        fecha_vigencia::DATE AS fecha_vigencia
    FROM source
)

SELECT * FROM renamed
