# Seminario de Sistemas 2

## 2. Enunciado de la Práctica

### 2.1 Descripción del problema a resolver

Las organizaciones necesitan transformar sus datos transaccionales en información útil para la toma de decisiones.

En esta práctica, el estudiante deberá conectar Power BI a una base de datos relacional (SQL Server) creada en la Práctica 1, construir un modelo tabular y diseñar un dashboard que permite visualizar indicadores clave de desempeño (KPIs).

El análisis deberá demostrar cómo las medidas y visualizaciones ayudan a interpretar resultados y apoyar decisiones estratégicas dentro de un entorno de inteligencia empresarial.

### 2.2 Alcance de la práctica

**Obligatorio:**

- Conectar Power BI al motor de base de datos (SQL Server).
- Diseñar un modelo tabular con relaciones entre tablas y jerarquías en las dimensiones.
- Crear al menos tres medidas DAX y un KPI con semáforo o indicador visual.
- Construir un dashboard con mínimo tres visualizaciones interactivas (barras, líneas, KPI, etc.) y filtros/segmentadores.
- Elaborar un informe breve que explique el diseño del modelo, los KPIs implementados y su relevancia estratégica.

**Opcional / Recomendado:**

- Implementar medidas DAX avanzadas (porcentaje de crecimiento, comparación año a año).
- Incluir botones de navegación o paneles personalizados en Power BI.
- Exportar el informe a formato PDF para presentación ejecutiva.

### 2.3 Requerimientos técnicos

- **Fuente de datos:** Base de datos relacional generada en la Práctica 1 (SQL Server).
- **Herramienta de análisis:** Microsoft Power BI Desktop.
- **Lenguaje de expresiones:** DAX (Data Analysis Expressions).
- **Hardware/entorno:** Computadora personal con Power BI Desktop instalado y conexión al motor de base de datos.
- **Conocimientos aplicados:** modelado tabular, relaciones, jerarquías, medidas DAX, visualización de datos y KPIs.

---

## 3. Entregables

| Tipo | Descripción |
|---|---|
| **Archivo Power BI (.pbix)** | Contiene conexión a la base de datos, modelo tabular, relaciones, medidas DAX y dashboard interactivo. |
| **Informe técnico (PDF o README.md)** | Explica la estructura del modelo, las medidas creadas, la interpretación de los KPIs y las decisiones de diseño. |
| **Capturas del dashboard** | Imágenes de las visualizaciones y KPIs implementados. |
| **Repositorio del curso** | Carpeta **Practica2** dentro de **SS22S2026_G#** con todos los archivos organizados conforme a los lineamientos. |

---

## 4. Material de apoyo

- Documentación oficial de Power BI: https://learn.microsoft.com/power-bi/
- Guía de relaciones y modelado de datos en Power BI: https://learn.microsoft.com/power-bi/transform-model/desktop-modeling-view
- Referencia oficial de DAX: https://learn.microsoft.com/dax/
- Tutorial de creación de KPIs en Power BI: https://learn.microsoft.com/power-bi/visuals/power-bi-visualization-kpi

---

## 5. Recursos y herramientas a utilizar

**Software:**

- Microsoft Power BI Desktop
- SQL Server (como fuente de datos)

**Plataformas:**

- GitHub (para repositorio)
- UEDI (para entrega oficial)

**Lecturas recomendadas:**

- Guías de modelado tabular y jerarquías en Power BI
- Manual de DAX para creación de medidas y KPIs
- Artículos sobre inteligencia empresarial y visualización estratégica de datos


## 7. Rúbrica de Calificación

### 7.1 Requisitos para optar a la calificación

| Tema | Descripción | Cumple (Sí/No) |
|---|---|---|
| Cumplimiento de la tecnología establecida | El modelo debe desarrollarse en Power BI con conexión a SQL Server | |
| Uso de herramientas requeridas | Se debe evidenciar la conexión a la base de datos, creación de relaciones, medidas DAX y KPIs. | |
| Gestión y entregas de práctica | El repositorio **SS22S2026_#carnet** debe incluir la carpeta **Practica2** con archivo .pbix, informe técnico y README.md. | |
| Documentación obligatoria | Incluir informe técnico o README que detalle el diseño, medidas DAX y justificación de KPIs. | |
| Pruebas y funcionalidad mínima | El dashboard debe mostrar visualizaciones interactivas, KPIs funcionales y filtros activos. | |

### 7.2 Resumen de Puntuaciones

| Área | Puntos Totales | Puntos Obtenidos |
|---|---|---|
| **1. Habilidades** | | |
| Conexión y modelado tabular | 15 | |
| Documentación e interpretación del modelo | 15 | |
| Cumplimiento de entregables (estructura, claridad, puntualidad) | 10 | |
| **Sub-Total Habilidades** | **40** | |
| **2. Conocimientos** | | |
| Creación de medidas y KPIs con DAX | 25 | |
| Diseño y funcionalidad del dashboard | 35 | |
| **Sub-Total Conocimientos** | **60** | |
| **TOTAL** | **100** | |



### Detalle de la Calificación

| No. | Criterio de evaluación | Punteo máximo | Satisfactorio (100%–61%) | Necesita mejorar (60%–0%) | Punteo obtenido |
|---|---|---|---|---|---|
| **1** | **Habilidades** | **40** | | | |
| 1.1 | Conexión y modelado tabular | 15 | Conecta Power BI correctamente al motor de base de datos (SQL Server o MySQL), establece relaciones coherentes y define jerarquías funcionales.<br>**Rango del punteo: 15/15–9** | No logra la conexión o las relaciones son incompletas o incorrectas, impidiendo el funcionamiento del modelo.<br>**Rango del punteo: 15/8–0** | |
| 1.2 | Documentación e interpretación | 15 | La documentación describe con claridad el diseño del modelo, las medidas DAX y los KPIs, comunicando resultados e interpretaciones relevantes.<br>**Rango del punteo: 15/15–9** | La documentación es incompleta, desorganizada o sin interpretación del modelo y los indicadores.<br>**Rango del punteo: 15/8–0** | |
| 1.3 | Cumplimiento de entregables | 10 | Entrega completa con repositorio estructurado, archivo .pbix, informe técnico y README detallado según los lineamientos.<br>**Rango del punteo: 10/10–6** | Faltan archivos, el repositorio no sigue el formato solicitado o hay errores en la presentación.<br>**Rango del punteo: 10/5–0** | |
| | **Sub-total Habilidades** | **40** | | | |
| **2** | **Conocimientos** | **60** | | | |
| 2.1 | Creación de medidas y KPIs con DAX | 25 | Crea medidas DAX funcionales y KPIs que representan correctamente los indicadores de desempeño definidos.<br>**Rango del punteo: 25/25–15** | Las medidas DAX o KPIs son incorrectas, incompletas o sin relación con los objetivos analíticos.<br>**Rango del punteo: 25/14–0** | |
| 2.2 | Diseño y funcionalidad del dashboard | 35 | El dashboard presenta visualizaciones estratégicas, interactivas y coherentes con los KPIs, usando filtros y segmentadores funcionales.<br>**Rango del punteo: 35/35–21** | El dashboard es incompleto, con errores en las visualizaciones o sin interactividad funcional.<br>**Rango del punteo: 35/20–0** | |
| | **Sub-total Conocimientos** | **60** | | | |
| | **Total General** | **100** | | | |