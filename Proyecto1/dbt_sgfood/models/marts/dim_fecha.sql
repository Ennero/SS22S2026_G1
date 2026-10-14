WITH date_spine AS (
    SELECT
        generate_series('2025-01-01'::DATE, '2027-12-31'::DATE, '1 day'::INTERVAL)::DATE AS fecha
)

SELECT
    TO_CHAR(fecha, 'YYYYMMDD')::INTEGER AS fecha_id,
    fecha,
    EXTRACT(YEAR FROM fecha)::INTEGER AS anio,
    EXTRACT(MONTH FROM fecha)::INTEGER AS mes,
    TO_CHAR(fecha, 'TMMonth') AS nombre_mes,
    EXTRACT(DAY FROM fecha)::INTEGER AS dia,
    EXTRACT(DOW FROM fecha)::INTEGER AS dia_semana, -- 0=Domingo ... 6=Sabado
    TO_CHAR(fecha, 'TMDay') AS nombre_dia,
    EXTRACT(QUARTER FROM fecha)::INTEGER AS trimestre,
    CASE
        WHEN EXTRACT(DOW FROM fecha) IN (0, 6) THEN TRUE
        ELSE FALSE
    END AS es_fin_semana
FROM date_spine
ORDER BY fecha
