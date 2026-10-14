# Guía de Configuración — Business Intelligence con Power BI Desktop
## Proyecto 1: Data Warehouse SG-Food (PostgreSQL)
**Curso:** Seminario de Sistemas 2 — Facultad de Ingeniería, USAC  
**Equipo:** Grupo 1 (Diego Alessandro Constanza Padilla / Enner Esaí Mendizabal Castro)  

---

## 1. Prerrequisitos

Para conectar Power BI Desktop al Data Warehouse analítico de SG-Food:
- **Docker Desktop:** Contenedor `sgfood_postgres` en ejecución y saludable (puerto `5432`).
- **Pipeline ELT ejecutado:** El esquema `marts` debe contener las 8 dimensiones y 4 tablas de hechos pobladas con restricciones físicas PK/FK aplicadas.
- **Microsoft Power BI Desktop:** Instalado en Windows.
- **Conector Npgsql (PostgreSQL):** Si Power BI solicita componentes adicionales para PostgreSQL, instalar el cliente oficial de Npgsql o permitir la conexión nativa de Power BI.

---

## 2. Parámetros de Conexión a PostgreSQL

| Parámetro | Valor Exacto |
|---|---|
| **Motor** | `PostgreSQL Database` |
| **Servidor (Host)** | `localhost:5432` (o `localhost`) |
| **Base de Datos** | `sgfood_dw` |
| **Modo de Conectividad** | **Importar** (*Recomendado para DAX de alto rendimiento y Time Intelligence*) |
| **Tipo de Autenticación** | `Base de datos` (Database credentials) |
| **Usuario** | `postgres` |
| **Contraseña** | `postgres` |
| **Nivel de Cifrado** | En caso de advertencia sobre soporte de cifrado (SSL), seleccionar **"Aceptar / Conectar sin cifrado"** para entornos locales de desarrollo Docker. |

---

## 3. Selección y Carga de Tablas (Esquema `marts`)

En el Navegador de Power BI, expandir la base de datos `sgfood_dw` y seleccionar **únicamente** las tablas correspondientes al esquema analítico **`marts`**:

### Tablas Dimensionales (8 Dimensiones - Contexto del Negocio):
1. `dim_sucursal` — Catálogo de sucursales (Central, Mixco, Villa Nueva, Amatitlán, Antigua, Escuintla).
2. `dim_categoria` — Familias comerciales (Abarrotes, Bebidas, Lácteos, Snacks, etc.).
3. `dim_marca` — Fabricantes comerciales (SaborMax, FrescaVida, etc.).
4. `dim_producto` — Catálogo maestro de 80 artículos con SKU, unidad, costos y precios.
5. `dim_cliente` — 250 clientes registrados con segmento y ubicación departamental.
6. `dim_proveedor` — Red externa de suministro, costos pactados y plazos de entrega.
7. `dim_promocion` — Acuerdos comerciales de descuento y ventanas de fechas de vigencia.
8. `dim_fecha` — Calendario analítico maestro (año, mes, trimestre, nombre de día, fin de semana).

### Tablas de Hechos (4 Fact Tables - Métricas Cuantitativas):
1. `fct_ventas` — Transacciones de venta a nivel detalle (unidades, precio, importes, márgenes).
2. `fct_inventario` — Snapshots periódicos de bodega (existencias, lotes, estados y alertas de vencimiento).
3. `fct_devoluciones` — Incidentes operativos post-venta (motivo, cantidad e impacto financiero).
4. `fct_rendimiento_metas` — Evaluación mensual de metas vs ventas reales por sucursal.

---

## 4. Arquitectura del Modelo Tabular (Esquema Estrella Kimball)

Al cargar las tablas en Power BI, dirígete a la pestaña **Vista de Modelo (Model View)**. Gracias al script `sql/apply_constraints.sql` aplicado por el pipeline, las relaciones se mapean de forma natural con cardinalidad **1 a Varios (1:*)** y dirección de filtro **Única (Single)**:

```
                          ┌──────────────┐
                          │  dim_fecha   │
                          └──────┬───────┘
                                 │ 1:N
        ┌────────────────────────┼────────────────────────┐
        │ 1:N                    │ 1:N                    │ 1:N
 ┌──────▼──────┐          ┌──────▼───────┐         ┌──────▼────────┐
 │ dim_cliente │          │  fct_ventas  │         │fct_inventario │
 └─────────────┘          └──────┬───────┘         └──────┬────────┘
                                 │                        │
        ┌────────────────────────┼────────────────────────┤
        │ 1:N                    │ 1:N                    │ 1:N
 ┌──────▼──────┐          ┌──────▼───────┐         ┌──────▼────────┐
 │dim_sucursal │◄─────────┤fct_rend_metas│         │fct_devolución │
 └──────┬──────┘   1:N    └──────────────┘         └───────────────┘
        │
        │ 1:N
 ┌──────▼──────┐
 │dim_producto │◄──────── (dim_categoria, dim_marca, dim_proveedor)
 └─────────────┘
```

### Relaciones Clave a Verificar:
- `dim_sucursal[id_sucursal]` (1) ───► `fct_ventas[id_sucursal]` (*)
- `dim_cliente[id_cliente]` (1) ───► `fct_ventas[id_cliente]` (*)
- `dim_producto[id_producto]` (1) ───► `fct_ventas[id_producto]` (*)
- `dim_fecha[fecha_id]` (1) ───► `fct_ventas[fecha_id]` (*)
- `dim_sucursal[id_sucursal]` (1) ───► `fct_inventario[id_sucursal]` (*)
- `dim_producto[id_producto]` (1) ───► `fct_inventario[id_producto]` (*)
- `dim_fecha[fecha_id]` (1) ───► `fct_inventario[fecha_id]` (*)
- `dim_sucursal[id_sucursal]` (1) ───► `fct_devoluciones[id_sucursal]` (*)
- `dim_producto[id_producto]` (1) ───► `fct_devoluciones[id_producto]` (*)
- `dim_fecha[fecha_id]` (1) ───► `fct_devoluciones[fecha_id]` (*)
- `dim_sucursal[id_sucursal]` (1) ───► `fct_rendimiento_metas[id_sucursal]` (*)
- `dim_categoria[id_categoria]` (1) ───► `dim_producto[id_categoria]` (*)
- `dim_marca[id_marca]` (1) ───► `dim_producto[id_marca]` (*)

---

## 5. Medidas DAX Oficiales de SG-Food (Tabla Dedicada `_Medidas`)

Crea una tabla vacía llamada `_Medidas` mediante **Modelado → Nueva tabla** (`_Medidas = ROW("Init", 1)`) y agrega las siguientes medidas analíticas formuladas con DAX:

### A. Indicadores Financieros y Comerciales (Fact Ventas)
```dax
// 1. Facturación Neta Total
Ventas Netas = SUM(fct_ventas[importe_neto])

// 2. Facturación Bruta
Ventas Brutas = SUM(fct_ventas[importe_bruto])

// 3. Monto Total de Descuentos Otorgados
Descuentos Totales = SUM(fct_ventas[monto_descuento])

// 4. Costo Total de Ventas
Costo Total = SUM(fct_ventas[costo_total])

// 5. Utilidad Bruta en Quetzales
Margen Bruto Q = SUM(fct_ventas[margen_ganancia])

// 6. Rentabilidad Porcentual
Margen Bruto % = DIVIDE([Margen Bruto Q], [Ventas Netas], 0)

// 7. Cantidad Total de Unidades Vendidas
Unidades Vendidas = SUM(fct_ventas[cantidad])

// 8. Total de Pedidos Únicos
Total Pedidos = DISTINCTCOUNT(fct_ventas[id_venta])

// 9. Ticket Promedio por Pedido
Ticket Promedio = DIVIDE([Ventas Netas], [Total Pedidos], 0)
```

### B. Indicadores de Logística y Caducidad (Fact Inventario)
```dax
// 10. Total de Existencias Físicas en Bodegas
Stock Total Bodega = SUM(fct_inventario[stock_disponible])

// 11. Valor Monetario del Inventario al Costo
Valorización Inventario = SUM(fct_inventario[valor_inventario_costo])

// 12. Conteo de Lotes Próximos a Vencer (<= 30 días restantes)
Lotes Proximos a Vencer = 
CALCULATE(
    COUNT(fct_inventario[lote]),
    fct_inventario[alerta_vencimiento] = "Próximo a Vencer"
)

// 13. Conteo de SKUs en Estado Crítico (por debajo del stock mínimo)
SKUs Estado Critico = 
CALCULATE(
    DISTINCTCOUNT(fct_inventario[id_producto]),
    fct_inventario[estado_stock] = "Crítico"
)

// 14. Conteo de SKUs Agotados (Stock disponible = 0)
SKUs Agotados = 
CALCULATE(
    DISTINCTCOUNT(fct_inventario[id_producto]),
    fct_inventario[estado_stock] = "Agotado"
)
```

### C. Cumplimiento de Metas Mensuales (Fact Rendimiento Metas)
```dax
// 15. Meta Comercial Presupuestada en Quetzales
Meta Ventas Q = SUM(fct_rendimiento_metas[meta_ventas])

// 16. Ventas Reales Logradas en el Período
Ventas Reales Q = SUM(fct_rendimiento_metas[ventas_reales])

// 17. Porcentaje de Cumplimiento de Meta
Pct Cumplimiento Meta = DIVIDE([Ventas Reales Q], [Meta Ventas Q], 0)

// 18. Semáforo Dinámico de Cumplimiento
Semaforo Cumplimiento = 
SWITCH(
    TRUE(),
    [Pct Cumplimiento Meta] >= 1.0, "🟢 Meta Lograda",
    [Pct Cumplimiento Meta] >= 0.85, "🟡 Alerta Moderada",
    "🔴 Déficit Crítico"
)
```

### D. Indicadores de Calidad Post-Venta (Fact Devoluciones)
```dax
// 19. Unidades Retornadas por Clientes
Unidades Devueltas = SUM(fct_devoluciones[cantidad_devuelta])

// 20. Pérdida Monetaria Estimada por Devolución
Monto Total Devoluciones = SUM(fct_devoluciones[monto_estimado_devolucion])

// 21. Tasa Porcentual de Devolución
Tasa Devolucion % = DIVIDE([Unidades Devueltas], [Unidades Vendidas], 0)
```

---

## 6. Diseño Recomendado de Dashboards Ejecutivos (3 Páginas)

### Página 1: Dashboard Ejecutivo y Financiero (Visión 360°)
- **Fila Superior (Tarjetas KPI):**
  - Tarjeta 1: `[Ventas Netas]` (Formato Moneda Q).
  - Tarjeta 2: `[Margen Bruto Q]` (Formato Moneda Q).
  - Tarjeta 3: `[Margen Bruto %]` (Formato Porcentaje `0.0%`).
  - Tarjeta 4: `[Ticket Promedio]` (Formato Moneda Q).
- **Cuerpo Principal:**
  - **Gráfico de Barras Agrupadas:** Ventas Netas y Margen por `dim_sucursal[sucursal_nombre]`.
  - **Gráfico de Columnas Clúster:** Facturación mensual a lo largo del tiempo con `dim_fecha[nombre_mes]`.
  - **Gráfico de Anillo (Donut):** Ventas por canal de distribución (`Mayorista`, `Tienda`, `Web`, `Televenta`).
- **Segmentadores (Slicers):**
  - Segmentador por `dim_sucursal[departamento]`.
  - Segmentador por `dim_categoria[categoria_nombre]`.
  - Segmentador por `dim_fecha[anio]` / `dim_fecha[mes]`.

### Página 2: Logística, Almacén y Control de Caducidades
- **Tarjetas KPI:**
  - `[Stock Total Bodega]` | `[Valorización Inventario]` | `[Lotes Proximos a Vencer]` | `[SKUs Estado Critico]`.
- **Gráfico de Columnas:**
  - Estado de Stock por Sucursal (`Normal`, `Crítico`, `Sobrestock`, `Agotado`).
- **Tabla Detallada de Auditoría de Vencimientos:**
  - Columnas: `fecha_corte`, `sucursal_nombre`, `producto_nombre`, `lote`, `fecha_vencimiento`, `dias_para_vencer`, `alerta_vencimiento`.
  - Filtro visual aplicado: `alerta_vencimiento = 'Próximo a Vencer'`.

### Página 3: Desempeño Comercial y Control de Calidad
- **Gráfico de Indicador (Gauge / Tacómetro):**
  - Valor: `[Pct Cumplimiento Meta]` con meta al 100%.
- **Gráfico de Columnas y Líneas:**
  - Columnas: `[Ventas Reales Q]`, Línea: `[Meta Ventas Q]` por Sucursal.
- **Gráfico de Barras Horizontales:**
  - `[Unidades Devueltas]` y `[Monto Total Devoluciones]` categorizadas por `motivo_devolucion` (`Producto dañado`, `Error de despacho`, `Cliente desistió`, `Empaque defectuoso`, `Vencimiento cercano`).

---

## 7. Preguntas Frecuentes y Argumentación para la Evaluación

Si el docente o evaluador consulta durante la calificación:

1. **¿Por qué conectar Power BI al esquema `marts` y no directamente a `raw` o a la base transaccional?**
   > *"Conectarse a `marts` protege el rendimiento del sistema transaccional de producción y aprovecha el modelado dimensional Kimball. En `marts`, los datos ya fueron limpiados, tipados y desduplicados en dbt, con llaves subrogadas e integridad referencial garantizada por 92 pruebas automáticas, facilitando cálculos DAX directos y optimizados."*

2. **¿Cómo garantizan que las relaciones funcionen en Power BI sin ambigüedad?**
   > *"El esquema estrella desacopla claramente las entidades de contexto (Dimensiones) de los eventos cuantitativos (Hechos). Al aplicar llaves foráneas físicas mediante el script `apply_constraints.sql`, Power BI identifica unívocamente las relaciones de 1 a varios, evitando relaciones muchos a muchos o filtros bidireccionales innecesarios."*

3. **¿Cómo se sincroniza el tablero cuando Airflow ejecuta una nueva corrida?**
   > *"Al ejecutarse el DAG de Airflow de forma programada a las 11:00 AM o mediante el autorun, las cargas idempotentes en `raw` y las materializaciones en tabla de `marts` actualizan el Data Warehouse. En Power BI basta con presionar el botón 'Actualizar' (Refresh) para incorporar inmediatamente la última corrida sin inconsistencias."*
