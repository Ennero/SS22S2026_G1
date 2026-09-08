# Guía Universal para Generar Proyectos Power BI (PBIP) Code-First
### Cómo construir modelos semánticos (TMDL) y reportes (PBIR) mediante código para cualquier proyecto o base de datos

---

## 1. Introducción: ¿Qué es el formato PBIP?

Tradicionalmente, Power BI utilizaba el formato binario `.pbix`, el cual funcionaba como una "caja negra": no se podía versionar en Git, no permitía ver cambios línea por línea (*diffs*), ni tampoco permitía generar reportes automáticamente mediante scripts.

A partir de 2023–2024, Microsoft introdujo **Power BI Project (`.pbip`)**, el formato estándar para flujos de trabajo **DevOps y Code-First**. Un proyecto `.pbip` descompone todo el reporte en archivos de texto plano legibles y editables:

1. **TMDL (Tabular Model Definition Language):** Archivos con sintaxis limpia que definen la base de datos tabular: tablas, columnas, relaciones, jerarquías y medidas DAX.
2. **PBIR (Power BI Enhanced Report Format):** Archivos JSON estructurados que definen la capa visual: páginas, lienzo, gráficos, tamaños, posiciones y filtros.

Cualquier desarrollador puede generar estos archivos con Python, Bash, Node.js o a mano, y Power BI Desktop los abrirá directamente con un doble clic.

---

## 2. Estructura Obligatoria de Carpetas

Para que Power BI Desktop reconozca tu proyecto, debes crear la siguiente estructura exacta:

```text
MiProyecto/
├── MiReporte.pbip                         <-- Archivo raíz (apunta a la carpeta del reporte)
│
├── MiReporte.SemanticModel/               <-- Capa de Datos (TMDL)
│   ├── definition.pbism                   <-- Configuración del modelo (version 4.0)
│   ├── .pbi/
│   │   └── editorSettings.json            <-- Configuración del editor
│   └── definition/
│       ├── model.tmdl                     <-- Declaración de tablas y cultura
│       ├── relationships.tmdl             <-- Relaciones (1:N, N:1, etc.)
│       └── tables/                        <-- Un archivo .tmdl por cada tabla
│           ├── FactVentas.tmdl
│           ├── DimCliente.tmdl
│           └── DimFecha.tmdl
│
└── MiReporte.Report/                      <-- Capa Visual (PBIR)
    ├── definition.pbir                    <-- Apunta al SemanticModel (version 4.0)
    └── definition/
        ├── version.json                   <-- Versión SemVer (1.0.0)
        ├── report.json                    <-- Tema y configuración general
        └── pages/
            ├── pages.json                 <-- Lista y orden de las páginas
            └── pagina1/                   <-- Carpeta por cada página
                ├── page.json              <-- Tamaño y propiedades del lienzo
                └── visuals/               <-- Carpeta por cada gráfico
                    ├── visual_tarjeta/
                    │   └── visual.json    <-- Definición del gráfico
                    └── visual_barras/
                        └── visual.json
```

---

## 3. Prerequisito: Habilitar en Power BI Desktop

Antes de abrir cualquier archivo `.pbip`, la persona que abra el proyecto debe tener activadas estas casillas en Power BI Desktop:

1. Ir a **Archivo > Opciones y configuración > Opciones**.
2. Entrar a **Características de versión preliminar** (*Preview features*).
3. Activar las casillas:
   - ✅ **Opción de guardar el proyecto Power BI (.pbip)**
   - ✅ **Almacenar modelo semántico con formato TMDL**
   - ✅ **Almacenar informes utilizando un formato de metadatos mejorado (PBIR)**
4. Clic en **Aceptar** y **reiniciar Power BI Desktop**.

---

## 4. Plantillas Paso a Paso para Crear los Archivos

### 4.1 Archivo Raíz: `MiReporte.pbip`
```json
{
  "version": "1.0",
  "artifacts": [
    {
      "report": {
        "path": "MiReporte.Report"
      }
    }
  ],
  "settings": {
    "enableAutoRecovery": true
  }
}
```

---

### 4.2 Modelo Semántico: `MiReporte.SemanticModel`

#### A) `MiReporte.SemanticModel/definition.pbism`
```json
{
  "version": "4.0",
  "settings": {}
}
```

#### B) `MiReporte.SemanticModel/.pbi/editorSettings.json`
```json
{
  "version": "1.0"
}
```

#### C) `MiReporte.SemanticModel/definition/model.tmdl`
> **⚠️ REGLA DE ORO DE TMDL:** TMDL utiliza **tabulaciones reales (`\t`)** para la sangría/indentación, **NO espacios**.

```tmdl
model Model
	culture: es-MX
	defaultPowerBIDataSourceVersion: powerBI_V3
	sourceQueryCulture: es-MX

	ref table DimFecha
	ref table DimCliente
	ref table FactVentas

expression ServerConnection = "localhost,1433" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]
	lineageTag: a0000001-0000-0000-0000-000000000001

expression DatabaseName = "MiBaseDatosDW" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]
	lineageTag: a0000001-0000-0000-0000-000000000002
```

---

### 4.3 Definiendo Tablas y Medidas en TMDL (`tables/*.tmdl`)

#### Ejemplo 1: Tabla de Dimensión con Jerarquía (`DimFecha.tmdl`)
```tmdl
table DimFecha
	lineageTag: b0000001-0000-0000-0000-000000000001

	column id_fecha
		dataType: int64
		isHidden
		isKey
		isNullable: false
		sourceColumn: id_fecha
		summarizeBy: none
		lineageTag: b0000001-0001-0000-0000-000000000001

	column fecha
		dataType: dateTime
		isNullable: false
		formatString: dd/MM/yyyy
		sourceColumn: fecha
		summarizeBy: none
		lineageTag: b0000001-0002-0000-0000-000000000001

	column anio
		dataType: int64
		sourceColumn: anio
		summarizeBy: none
		lineageTag: b0000001-0003-0000-0000-000000000001

	column mes
		dataType: int64
		sourceColumn: mes
		summarizeBy: none
		lineageTag: b0000001-0004-0000-0000-000000000001

	column nombre_mes
		dataType: string
		sourceColumn: nombre_mes
		summarizeBy: none
		lineageTag: b0000001-0005-0000-0000-000000000001

	/// Jerarquía de fecha: Año -> Mes
	hierarchy 'Jerarquía Fecha'
		lineageTag: b0000001-h001-0000-0000-000000000001

		level Año
			column: anio
			lineageTag: b0000001-h001-0001-0000-000000000001

		level Mes
			column: nombre_mes
			lineageTag: b0000001-h001-0002-0000-000000000001

	partition DimFecha = m
		mode: import
		source =
			let
			    Origen = Sql.Database("localhost,1433", "MiBaseDatosDW"),
			    dbo_DimFecha = Origen{[Schema="dbo",Item="DimFecha"]}[Data]
			in
			    dbo_DimFecha
```

#### Ejemplo 2: Tabla de Hechos con Medidas DAX y KPI (`FactVentas.tmdl`)
```tmdl
table FactVentas
	lineageTag: b0000002-0000-0000-0000-000000000001

	column id_venta
		dataType: int64
		isKey
		sourceColumn: id_venta
		lineageTag: b0000002-0001-0000-0000-000000000001

	column id_fecha
		dataType: int64
		sourceColumn: id_fecha
		lineageTag: b0000002-0002-0000-0000-000000000001

	column monto_usd
		dataType: decimal
		sourceColumn: monto_usd
		formatString: $ #,##0.00
		lineageTag: b0000002-0003-0000-0000-000000000001

	measure 'Total Ventas' = COUNTROWS(FactVentas)
		formatString: #,##0
		displayFolder: Métricas Principales
		lineageTag: c0000001-0000-0000-0000-000000000001

	measure 'Ingresos Totales' = SUM(FactVentas[monto_usd])
		formatString: $ #,##0.00
		displayFolder: Métricas Principales
		lineageTag: c0000002-0000-0000-0000-000000000001

	/// Medida DAX Avanzada (Comparación mes a mes - Time Intelligence)
	measure 'Crecimiento MoM %' = 
			VAR Actual = [Ingresos Totales]
			VAR Anterior = CALCULATE([Ingresos Totales], DATEADD(DimFecha[fecha], -1, MONTH))
			RETURN
			    IF(ISBLANK(Anterior), BLANK(), DIVIDE(Actual - Anterior, Anterior, 0) * 100)
		formatString: +#,##0.0"%";-#,##0.0"%";#,##0.0"%"
		displayFolder: KPIs
		lineageTag: c0000003-0000-0000-0000-000000000001

	/// KPI con Semáforo condicional: 1 (Verde), 2 (Amarillo), 3 (Rojo)
	measure 'Semaforo Rendimiento' = 
			VAR Crecimiento = [Crecimiento MoM %]
			RETURN
			    SWITCH(
			        TRUE(),
			        Crecimiento >= 5, 1,
			        Crecimiento >= 0, 2,
			        3
			    )
		formatString: 0
		displayFolder: KPIs
		lineageTag: c0000004-0000-0000-0000-000000000001

	partition FactVentas = m
		mode: import
		source =
			let
			    Origen = Sql.Database("localhost,1433", "MiBaseDatosDW"),
			    dbo_FactVentas = Origen{[Schema="dbo",Item="FactVentas"]}[Data]
			in
			    dbo_FactVentas
```

---

### 4.4 Definiendo Relaciones: `relationships.tmdl`
```tmdl
relationship d0000001-0000-0000-0000-000000000001
	fromColumn: FactVentas.id_fecha
	toColumn: DimFecha.id_fecha

relationship d0000002-0000-0000-0000-000000000001
	fromColumn: FactVentas.id_cliente
	toColumn: DimCliente.id_cliente
```

---

## 5. Reporte Visual: `MiReporte.Report` (PBIR)

### 5.1 Configuración Base

#### A) `MiReporte.Report/definition.pbir`
```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
  "version": "4.0",
  "datasetReference": {
    "byPath": {
      "path": "../MiReporte.SemanticModel"
    }
  }
}
```

#### B) `MiReporte.Report/definition/version.json`
> **⚠️ REGLA DE VERSION:** El valor de `version` debe seguir el formato SemVer de tres componentes (por ejemplo: `"1.0.0"`), ya que el esquema exige la expresión regular `^[1-9][0-9]*\.(0|[1-9][0-9]*)\.0$`.

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/versionMetadata/1.0.0/schema.json",
  "version": "1.0.0"
}
```

#### C) `MiReporte.Report/definition/report.json`
```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/1.0.0/schema.json",
  "themeCollection": {
    "baseTheme": {
      "name": "CY24SU06",
      "reportVersionAtImport": "5.55",
      "type": "SharedResources"
    }
  },
  "layoutOptimization": 0
}
```

#### D) `MiReporte.Report/definition/pages/pages.json`
```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json",
  "pageOrder": [
    "pagina_principal"
  ],
  "activePageName": "pagina_principal"
}
```

---

### 5.2 Estructura de una Página: `pages/pagina_principal/`

#### `page.json`
```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/1.0.0/schema.json",
  "name": "pagina_principal",
  "displayName": "Vista General",
  "displayOption": "fitToPage",
  "height": 720,
  "width": 1280
}
```

---

### 5.3 Plantillas de Gráficos (`visuals/<nombre>/visual.json`)

#### 1. Tarjeta (Card)
```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/1.0.0/schema.json",
  "name": "card_ventas",
  "position": {
    "x": 20,
    "y": 20,
    "width": 250,
    "height": 120
  },
  "visual": {
    "visualType": "card",
    "query": {
      "queryState": {
        "Values": {
          "projections": [
            {
              "field": {
                "Measure": {
                  "Expression": { "SourceRef": { "Entity": "FactVentas" } },
                  "Property": "Ingresos Totales"
                }
              },
              "queryRef": "FactVentas.Ingresos Totales"
            }
          ]
        }
      }
    }
  }
}
```

#### 2. Gráfico de Barras Agrupadas
```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/1.0.0/schema.json",
  "name": "bar_clientes",
  "position": {
    "x": 20,
    "y": 160,
    "width": 450,
    "height": 350
  },
  "visual": {
    "visualType": "clusteredBarChart",
    "query": {
      "queryState": {
        "Category": {
          "projections": [
            {
              "field": {
                "Column": {
                  "Expression": { "SourceRef": { "Entity": "DimCliente" } },
                  "Property": "pais"
                }
              },
              "queryRef": "DimCliente.pais"
            }
          ]
        },
        "Y": {
          "projections": [
            {
              "field": {
                "Measure": {
                  "Expression": { "SourceRef": { "Entity": "FactVentas" } },
                  "Property": "Ingresos Totales"
                }
              },
              "queryRef": "FactVentas.Ingresos Totales"
            }
          ]
        }
      }
    }
  }
}
```

#### 3. Segmentador / Filtro (Slicer)
```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/1.0.0/schema.json",
  "name": "filtro_anio",
  "position": {
    "x": 1080,
    "y": 20,
    "width": 180,
    "height": 300
  },
  "visual": {
    "visualType": "slicer",
    "query": {
      "queryState": {
        "Values": {
          "projections": [
            {
              "field": {
                "Column": {
                  "Expression": { "SourceRef": { "Entity": "DimFecha" } },
                  "Property": "anio"
                }
              },
              "queryRef": "DimFecha.anio"
            }
          ]
        }
      }
    }
  }
}
```

---

## 6. Archivo `.gitignore` Recomendado

```gitignore
**/.pbi/localSettings.json
**/.pbi/cache.abf
**/.pbi/unappliedChanges.json
.env
*.log
Thumbs.db
.DS_Store
```
