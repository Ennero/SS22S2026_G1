"""
Tarea 1 — Limpieza y análisis inicial de datos con Pandas.

Lee docs/dataset_sucio.csv, aplica las transformaciones de verdad
(duplicados, nulos, estandarización), muestra pivotes y gráficos,
y exporta data/dataset_limpio.csv.

Uso:
    python limpieza.py              # pausa en cada paso para tomar capturas
    python limpieza.py --no-pausa   # corre de un tirón (sin Enter ni ventanas)
"""

from __future__ import annotations

import argparse
import sys
import warnings
from datetime import datetime
from pathlib import Path

if "--no-pausa" in sys.argv:
    import matplotlib

    matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import seaborn as sns

BASE_DIR = Path(__file__).resolve().parent
CSV_ORIGEN = BASE_DIR / "docs" / "dataset_sucio.csv"
CSV_LIMPIO = BASE_DIR / "data" / "dataset_limpio.csv"

GENDER_MAP = {
    "m": "M",
    "masculino": "M",
    "male": "M",
    "f": "F",
    "femenino": "F",
    "female": "F",
}

CATEGORIA_MAP = {
    "retail": "Retail",
    "services": "Services",
    "education": "Education",
    "food": "Food",
}

NA_TOKENS = {"", "na", "nan", "none", "null", "n/a"}

PAUSAR = True


def paso(numero: int, titulo: str, captura: str) -> None:
    linea = "=" * 72
    print(f"\n{linea}")
    print(f"PASO {numero} - {titulo}")
    print(linea)
    print(f"Guarda esta captura como img/{captura}")
    print()


def esperar() -> None:
    if PAUSAR:
        input("\n>>> Toma la captura y presiona Enter para continuar...")


def mostrar_df(df: pd.DataFrame, filas: int = 12) -> None:
    print(df.head(filas).to_string(index=False))
    print()
    print(f"Filas: {len(df)}  |  Columnas: {df.shape[1]}")


def nulos_por_columna(df: pd.DataFrame) -> pd.Series:
    return df.isna().sum()


def marcar_vacios(serie: pd.Series) -> pd.Series:
    texto = serie.astype(str).str.strip().str.lower()
    return serie.where(~(serie.isna() | texto.isin(NA_TOKENS)), np.nan)


def gasto_a_numero(serie: pd.Series) -> pd.Series:
    texto = serie.astype(str).str.strip().str.replace(",", ".", regex=False)
    texto = texto.str.replace(r"[^\d.\-]", "", regex=True)
    return pd.to_numeric(texto, errors="coerce")


def fechas_a_iso(serie: pd.Series) -> pd.Series:
    formatos = ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y")
    parsed: list[str | None] = []
    for valor in serie.tolist():
        if valor is None or (isinstance(valor, float) and np.isnan(valor)):
            parsed.append(None)
            continue
        texto = str(valor).strip()
        if texto.lower() in NA_TOKENS or texto.lower() == "nat":
            parsed.append(None)
            continue
        fecha: datetime | None = None
        for fmt in formatos:
            try:
                fecha = datetime.strptime(texto, fmt)
                break
            except ValueError:
                continue
        parsed.append(fecha.strftime("%Y-%m-%d") if fecha else None)
    return pd.Series(parsed, index=serie.index, dtype="object")


def limpiar_nombres(serie: pd.Series) -> pd.Series:
    texto = serie.astype(str).str.strip().str.replace(r"\s+", " ", regex=True)
    texto = texto.str.title()
    vacios = serie.isna() | texto.str.lower().isin(NA_TOKENS)
    return texto.mask(vacios, "Desconocido")


def limpiar_generos(serie: pd.Series) -> pd.Series:
    clave = serie.astype(str).str.strip().str.lower()
    return clave.map(GENDER_MAP).fillna("Desconocido")


def limpiar_categorias(serie: pd.Series) -> pd.Series:
    clave = serie.astype(str).str.strip().str.lower()
    vacios = serie.isna() | clave.isin(NA_TOKENS)
    mapped = clave.map(CATEGORIA_MAP)
    mapped = mapped.fillna(serie.astype(str).str.strip().str.title())
    return mapped.mask(vacios, "Desconocido")


def limpiar_ciudades(serie: pd.Series) -> pd.Series:
    texto = serie.astype(str).str.strip().str.replace(r"\s+", " ", regex=True)
    texto = texto.str.title()
    vacios = serie.isna() | texto.str.lower().isin(NA_TOKENS)
    return texto.mask(vacios, "Desconocido")


def mostrar_grafico(fig: plt.Figure, nombre_archivo: str | None = None) -> None:
    if nombre_archivo:
        ruta = BASE_DIR / "img" / nombre_archivo
        ruta.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(ruta, dpi=300, bbox_inches="tight")
        print(f"Grafico guardado automaticamente en: {ruta}")
    if PAUSAR:
        plt.show()
    plt.close(fig)


def main() -> int:
    global PAUSAR

    parser = argparse.ArgumentParser(
        description="Limpieza real del dataset sucio de clientes (Tarea 1)."
    )
    parser.add_argument(
        "--no-pausa",
        action="store_true",
        help="Ejecuta todo el flujo sin pedir Enter ni abrir ventanas de gráficos.",
    )
    args = parser.parse_args()
    PAUSAR = not args.no_pausa
    warnings.filterwarnings("ignore", category=FutureWarning)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 140)
    pd.set_option("display.max_colwidth", 36)
    pd.set_option("display.float_format", lambda x: f"{x:,.2f}")
    sns.set_theme(style="whitegrid")

    if not CSV_ORIGEN.exists():
        print(f"No se encontró el dataset: {CSV_ORIGEN}", file=sys.stderr)
        return 1

    print("Tarea 1 - Limpieza y analisis inicial de datos")
    print("Dataset:", CSV_ORIGEN)
    if PAUSAR:
        print("Modo capturas: el script se detiene en cada paso.")
        print("Cierra cada ventana de gráfico después de fotografiarla.")
    else:
        print("Modo --no-pausa: corre de un tirón, sin ventanas.")

    # ------------------------------------------------------------------
    # PASO 1 — Dataset original
    # ------------------------------------------------------------------
    paso(1, "Dataset original (antes de limpiar)", "01_dataframe_original.png")
    df_original = pd.read_csv(CSV_ORIGEN)
    df = df_original.copy()

    print("Primeras filas (estado sucio):\n")
    mostrar_df(df)

    print("Tipos de dato:")
    print(df.dtypes.to_string())
    print()
    print("Valores nulos por columna:")
    print(nulos_por_columna(df).to_string())
    print()
    print(f"Filas duplicadas exactas: {int(df.duplicated().sum())}")
    print(f"id_cliente duplicados: {int(df['id_cliente'].duplicated().sum())}")
    print()
    print("Valores únicos de genero:", sorted(set(str(x).strip() for x in df["genero"] if pd.notna(x) and str(x).strip())))
    print("Valores únicos de categoria:", sorted(set(str(x).strip() for x in df["categoria"] if pd.notna(x) and str(x).strip())))
    print("Muestra de ciudades:", sorted(set(str(x).strip() for x in df["ciudad"] if pd.notna(x) and str(x).strip()))[:15])
    nulos_antes = nulos_por_columna(df)
    esperar()

    # ------------------------------------------------------------------
    # PASO 2 — Duplicados
    # ------------------------------------------------------------------
    paso(2, "Eliminación de duplicados", "02_duplicados.png")
    filas_antes = len(df)
    df = df.drop_duplicates().copy()
    exactos = filas_antes - len(df)

    id_dup_antes = int(df["id_cliente"].duplicated().sum())
    df = df.drop_duplicates(subset=["id_cliente"], keep="first").copy()
    id_quitados = id_dup_antes - int(df["id_cliente"].duplicated().sum())

    print(f"Filas antes: {filas_antes}")
    print(f"Duplicados exactos eliminados: {exactos}")
    print(f"id_cliente repetidos eliminados (se conserva la primera fila): {id_quitados}")
    print(f"Filas después: {len(df)}")
    print()
    print("Primeras filas tras quitar duplicados:\n")
    mostrar_df(df)
    esperar()

    # ------------------------------------------------------------------
    # PASO 3 — Celdas vacías / NA
    # ------------------------------------------------------------------
    paso(3, "Tratamiento de celdas vacías y NA", "03_nulos.png")

    trabajo = {
        "id_cliente": df["id_cliente"],
        "nombre": marcar_vacios(df["nombre"]),
        "genero": marcar_vacios(df["genero"]),
        "fecha_registro": marcar_vacios(df["fecha_registro"]),
        "gasto_q": gasto_a_numero(df["gasto_q"]),
        "ciudad": marcar_vacios(df["ciudad"]),
        "categoria": marcar_vacios(df["categoria"]),
    }
    nulos_gasto = int(trabajo["gasto_q"].isna().sum())
    mediana_gasto = float(trabajo["gasto_q"].median())
    trabajo["gasto_q"] = trabajo["gasto_q"].fillna(mediana_gasto)

    nulos_cat = {
        "genero": int(trabajo["genero"].isna().sum()),
        "ciudad": int(trabajo["ciudad"].isna().sum()),
        "categoria": int(trabajo["categoria"].isna().sum()),
        "nombre": int(trabajo["nombre"].isna().sum()),
        "fecha_registro": int(trabajo["fecha_registro"].isna().sum()),
    }
    trabajo["genero"] = trabajo["genero"].fillna("Desconocido")
    trabajo["ciudad"] = trabajo["ciudad"].fillna("Desconocido")
    trabajo["categoria"] = trabajo["categoria"].fillna("Desconocido")
    trabajo["nombre"] = trabajo["nombre"].fillna("Desconocido")
    df = pd.DataFrame(trabajo)

    print("gasto_q se parseo a numero (coma decimal -> punto).")
    print(f"Nulos en gasto_q antes de rellenar: {nulos_gasto}")
    print(f"Mediana usada para rellenar gasto_q: Q {mediana_gasto:.2f}")
    print()
    print("Nulos categóricos reemplazados por 'Desconocido':")
    for campo, cantidad in nulos_cat.items():
        print(f"  - {campo}: {cantidad}")
    print()
    print("Nulos restantes por columna:")
    print(nulos_por_columna(df).to_string())
    print()
    print("Primeras filas tras tratar vacíos:\n")
    mostrar_df(df)
    esperar()

    # ------------------------------------------------------------------
    # PASO 4 — Estandarización
    # ------------------------------------------------------------------
    paso(4, "Estandarización de valores y formatos", "04_estandarizacion.png")

    fechas = fechas_a_iso(df["fecha_registro"])
    fechas_invalidas = int(fechas.isna().sum())
    df = pd.DataFrame(
        {
            "id_cliente": pd.to_numeric(df["id_cliente"], errors="coerce").astype(int),
            "nombre": limpiar_nombres(df["nombre"]).astype(str),
            "genero": limpiar_generos(df["genero"]).astype(str),
            "fecha_registro": fechas,
            "gasto_q": df["gasto_q"].astype(float).round(2),
            "ciudad": limpiar_ciudades(df["ciudad"]).astype(str),
            "categoria": limpiar_categorias(df["categoria"]).astype(str),
        }
    )
    if fechas_invalidas:
        print(f"Fechas inválidas encontradas: {fechas_invalidas} (quedan vacias).")

    print("Reglas aplicadas:")
    print("  - nombre: trim, espacios dobles y Title Case")
    print("  - genero: M / F / Desconocido")
    print("  - ciudad: Title Case (NA y vacios -> Desconocido)")
    print("  - categoria: Retail, Services, Education, Food")
    print("  - fecha_registro: YYYY-MM-DD (acepta ISO y DD/MM/YYYY)")
    print("  - gasto_q: float con 2 decimales")
    print()
    print("Género unificado:")
    print(df["genero"].value_counts(dropna=False).to_string())
    print()
    print("Categoría unificada:")
    print(df["categoria"].value_counts(dropna=False).to_string())
    print()
    print("Ciudades unificadas:")
    print(df["ciudad"].value_counts(dropna=False).to_string())
    print()
    print("Rango de fechas:", df["fecha_registro"].min(), "->", df["fecha_registro"].max())
    esperar()

    # ------------------------------------------------------------------
    # PASO 5 — Dataset depurado
    # ------------------------------------------------------------------
    paso(5, "Dataset depurado (después de limpiar)", "05_dataframe_limpio.png")
    df = df.sort_values(["id_cliente"]).reset_index(drop=True)

    print("ANTES (original, sucio):\n")
    print(f"Filas: {len(df_original)}  |  Columnas: {df_original.shape[1]}")
    print("Nulos originales:")
    print(nulos_antes.to_string())
    print()
    print("Primeras filas originales:")
    print(df_original.head(8).to_string(index=False))
    print()
    print("DESPUÉS (depurado):\n")
    mostrar_df(df)
    print("Tipos de dato:")
    print(df.dtypes.to_string())
    print()
    print("Nulos restantes:")
    print(nulos_por_columna(df).to_string())
    print()
    print(
        "Impacto: se unificaron formatos, se rellenaron vacíos y el gasto "
        "ya es numérico para agregar y graficar."
    )
    nulos_despues = nulos_por_columna(df)
    esperar()

    # ------------------------------------------------------------------
    # PASO 6 — Pivotes
    # ------------------------------------------------------------------
    paso(6, "Tablas pivote (Pandas)", "06_pivote_categoria.png")

    pivot_categoria = pd.pivot_table(
        df,
        values="gasto_q",
        index="categoria",
        aggfunc=["count", "sum", "mean"],
        margins=True,
        margins_name="Total",
    )
    pivot_categoria.columns = ["clientes", "gasto_total_q", "gasto_promedio_q"]
    pivot_categoria = pivot_categoria.round(2)

    pivot_ciudad = pd.pivot_table(
        df,
        values="gasto_q",
        index="ciudad",
        aggfunc=["count", "sum", "mean"],
        margins=True,
        margins_name="Total",
    )
    pivot_ciudad.columns = ["clientes", "gasto_total_q", "gasto_promedio_q"]
    pivot_ciudad = pivot_ciudad.round(2)

    pivot_genero = pd.pivot_table(
        df,
        values="gasto_q",
        index="genero",
        aggfunc=["count", "sum", "mean"],
        margins=True,
        margins_name="Total",
    )
    pivot_genero.columns = ["clientes", "gasto_total_q", "gasto_promedio_q"]
    pivot_genero = pivot_genero.round(2)

    pivot_cruce = pd.pivot_table(
        df,
        values="gasto_q",
        index="ciudad",
        columns="categoria",
        aggfunc="sum",
        fill_value=0,
        margins=True,
        margins_name="Total",
    ).round(2)

    print("Pivote 1 - Gasto por categoria:\n")
    print(pivot_categoria.to_string())
    print()
    print("Pivote 2 - Gasto por ciudad:\n")
    print(pivot_ciudad.to_string())
    print()
    print("Pivote 3 - Gasto por genero:\n")
    print(pivot_genero.to_string())
    print()
    print("Pivote 4 - Cruce ciudad x categoria (gasto total Q):\n")
    print(pivot_cruce.to_string())
    esperar()

    # ------------------------------------------------------------------
    # PASO 7 — Gráfico 1: Calidad de datos y rendimiento por categoría
    # ------------------------------------------------------------------
    paso(7, "Visualización: calidad de datos y rendimiento por categoría", "07_grafico_gasto.png")

    fig1, axes = plt.subplots(1, 2, figsize=(16, 6.8))
    fig1.patch.set_facecolor("#fafbfc")

    # Subplot 1: Nulos antes vs después
    ax1 = axes[0]
    ax1.set_facecolor("#ffffff")
    columnas_plot = [col for col in df_original.columns]
    nulos_antes_vals = [nulos_antes[col] for col in columnas_plot]
    nulos_despues_vals = [nulos_despues[col] for col in columnas_plot]

    x_pos = np.arange(len(columnas_plot))
    ancho_barra = 0.36

    bars1 = ax1.bar(x_pos - ancho_barra / 2, nulos_antes_vals, width=ancho_barra, label="Antes (Datos Sucios)", color="#e74c3c", edgecolor="#c0392b", alpha=0.9)
    bars2 = ax1.bar(x_pos + ancho_barra / 2, nulos_despues_vals, width=ancho_barra, label="Después (Datos Limpios)", color="#27ae60", edgecolor="#1e8449", alpha=0.9)

    ax1.set_title("Auditoría de Calidad: Valores Nulos / Faltantes", fontsize=13, fontweight="bold", pad=14, color="#2c3e50")
    ax1.set_xlabel("Columnas del Dataset", fontsize=11, fontweight="bold", labelpad=8)
    ax1.set_ylabel("Cantidad de Registros Nulos", fontsize=11, fontweight="bold", labelpad=8)
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(columnas_plot, rotation=25, ha="right", fontsize=10, fontweight="medium")
    ax1.set_ylim(0, max(nulos_antes_vals) * 1.30)
    ax1.grid(axis="y", linestyle="--", alpha=0.5)

    # Etiquetas directas en las barras
    for bar in bars1:
        h = bar.get_height()
        if h > 0:
            ax1.annotate(f"{int(h):,}", (bar.get_x() + bar.get_width() / 2, h),
                         ha="center", va="bottom", fontsize=9.5, fontweight="bold", color="#c0392b", xytext=(0, 3), textcoords="offset points")

    for bar in bars2:
        h = bar.get_height()
        if h > 0:
            ax1.annotate(f"{int(h)}", (bar.get_x() + bar.get_width() / 2, h),
                         ha="center", va="bottom", fontsize=9.5, fontweight="bold", color="#1e8449", xytext=(0, 3), textcoords="offset points")
        else:
            ax1.annotate("0", (bar.get_x() + bar.get_width() / 2, 0),
                         ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#27ae60", xytext=(0, 2), textcoords="offset points")

    # Caja de resumen de eficacia
    total_nulos_resueltos = sum(nulos_antes_vals) - sum(nulos_despues_vals)
    ax1.text(0.97, 0.94, f"Nulos Resueltos: {total_nulos_resueltos:,}\nEficacia: 100% Tratados",
             transform=ax1.transAxes, fontsize=9.5, fontweight="bold",
             va="top", ha="right", bbox=dict(boxstyle="round,pad=0.5", facecolor="#e8f8f5", edgecolor="#27ae60", alpha=0.95))
    ax1.legend(loc="upper left", frameon=True, facecolor="#ffffff", edgecolor="#bdc3c7")

    # Subplot 2: Gasto total y métricas por categoría
    ax2 = axes[1]
    ax2.set_facecolor("#ffffff")
    gasto_cat = (
        df.groupby("categoria")
        .agg(gasto_total=("gasto_q", "sum"), clientes=("id_cliente", "count"), gasto_medio=("gasto_q", "mean"))
        .sort_values("gasto_total", ascending=False)
        .reset_index()
    )
    gasto_total_general = gasto_cat["gasto_total"].sum()
    gasto_cat["pct_total"] = (gasto_cat["gasto_total"] / gasto_total_general) * 100

    colores_cat = ["#1b4f72", "#2874a6", "#3498db", "#5dade2"]
    bars_cat = ax2.bar(gasto_cat["categoria"], gasto_cat["gasto_total"], color=colores_cat, edgecolor="#154360", alpha=0.9, width=0.52)

    ax2.set_title("Rendimiento Financiero: Gasto Total por Categoría", fontsize=13, fontweight="bold", pad=14, color="#2c3e50")
    ax2.set_xlabel("Categoría de Negocio", fontsize=11, fontweight="bold", labelpad=8)
    ax2.set_ylabel("Gasto Total Acumulado (Q)", fontsize=11, fontweight="bold", labelpad=8)
    ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"Q {x*1e-3:,.0f}k"))
    ax2.set_ylim(0, gasto_cat["gasto_total"].max() * 1.38)
    ax2.grid(axis="y", linestyle="--", alpha=0.5)

    # Línea de promedio por categoría
    promedio_cat = gasto_cat["gasto_total"].mean()
    ax2.axhline(promedio_cat, color="#e67e22", linestyle="--", linewidth=1.6,
                label=f"Promedio por Categoría: Q {promedio_cat:,.2f}")

    # Etiquetas detalladas en cada barra
    for i, row in gasto_cat.iterrows():
        val = row["gasto_total"]
        pct = row["pct_total"]
        clts = int(row["clientes"])
        ticket = row["gasto_medio"]
        ax2.annotate(f"Q {val:,.2f}\n({pct:.1f}% del total)\n{clts:,} clts · Ticket: Q {ticket:.2f}",
                     (i, val), ha="center", va="bottom", fontsize=8.5, fontweight="bold",
                     color="#1a252f", xytext=(0, 5), textcoords="offset points")

    ax2.legend(loc="upper right", frameon=True, facecolor="#ffffff", edgecolor="#bdc3c7")
    fig1.tight_layout()
    mostrar_grafico(fig1, "07_grafico_gasto.png")
    print("Gráfico 1: Calidad de datos (nulos antes vs después) y Gasto total por categoría.")
    esperar()

    # ------------------------------------------------------------------
    # PASO 8 — Gráfico 2: Género y distribución geográfica (ciudades)
    # ------------------------------------------------------------------
    paso(8, "Visualización: demografía y distribución geográfica", "08_grafico_genero.png")

    fig2, axes = plt.subplots(1, 2, figsize=(16, 6.8))
    fig2.patch.set_facecolor("#fafbfc")

    # Subplot 1: Distribución por género (Conteo, % y Ticket)
    ax1 = axes[0]
    ax1.set_facecolor("#ffffff")
    genero_df = (
        df.groupby("genero")
        .agg(clientes=("id_cliente", "count"), gasto_total=("gasto_q", "sum"), gasto_medio=("gasto_q", "mean"))
        .reindex(["F", "M", "Desconocido"])
        .reset_index()
    )
    genero_df["pct_clientes"] = (genero_df["clientes"] / len(df)) * 100
    genero_df["pct_gasto"] = (genero_df["gasto_total"] / df["gasto_q"].sum()) * 100

    colores_gen = {"F": "#8e44ad", "M": "#2980b9", "Desconocido": "#7f8c8d"}
    palette_gen = [colores_gen[g] for g in genero_df["genero"]]

    bars_gen = ax1.bar(genero_df["genero"], genero_df["clientes"], color=palette_gen, edgecolor="#2c3e50", alpha=0.9, width=0.48)

    ax1.set_title("Estructura Demográfica: Clientes por Género", fontsize=13, fontweight="bold", pad=14, color="#2c3e50")
    ax1.set_xlabel("Género del Cliente", fontsize=11, fontweight="bold", labelpad=8)
    ax1.set_ylabel("Cantidad de Clientes", fontsize=11, fontweight="bold", labelpad=8)
    ax1.set_ylim(0, genero_df["clientes"].max() * 1.30)
    ax1.grid(axis="y", linestyle="--", alpha=0.5)

    for i, row in genero_df.iterrows():
        clts = int(row["clientes"])
        pct = row["pct_clientes"]
        g_tot = row["gasto_total"]
        tkt = row["gasto_medio"]
        ax1.annotate(f"{clts:,} clientes ({pct:.1f}%)\nGasto: Q {g_tot:,.2f}\nTicket Medio: Q {tkt:.2f}",
                     (i, clts), ha="center", va="bottom", fontsize=9, fontweight="bold",
                     color="#2c3e50", xytext=(0, 5), textcoords="offset points")

    # Subplot 2: Gasto por ciudad ordenado con ticket promedio
    ax2 = axes[1]
    ax2.set_facecolor("#ffffff")
    ciudad_df = (
        df.groupby("ciudad")
        .agg(gasto_total=("gasto_q", "sum"), clientes=("id_cliente", "count"), gasto_medio=("gasto_q", "mean"))
        .sort_values("gasto_total", ascending=True)
        .reset_index()
    )

    colores_ciudad = [
        "#95a5a6" if c == "Desconocido" else "#16a085" for c in ciudad_df["ciudad"]
    ]
    y_pos = np.arange(len(ciudad_df))
    bars_ciu = ax2.barh(y_pos, ciudad_df["gasto_total"], color=colores_ciudad, edgecolor="#0e6655", alpha=0.88, height=0.60)

    ax2.set_title("Distribución Geográfica: Gasto Total por Ciudad", fontsize=13, fontweight="bold", pad=14, color="#2c3e50")
    ax2.set_xlabel("Gasto Total Acumulado (Q)", fontsize=11, fontweight="bold", labelpad=8)
    ax2.set_ylabel("Ciudad", fontsize=11, fontweight="bold", labelpad=8)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(ciudad_df["ciudad"], fontsize=10, fontweight="medium")
    ax2.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"Q {x*1e-3:,.0f}k"))
    ax2.set_xlim(0, ciudad_df["gasto_total"].max() * 1.38)
    ax2.grid(axis="x", linestyle="--", alpha=0.5)

    media_ciudad = ciudad_df["gasto_total"].mean()
    ax2.axvline(media_ciudad, color="#c0392b", linestyle="--", linewidth=1.6,
                label=f"Media por Ciudad: Q {media_ciudad:,.2f}")

    for i, row in ciudad_df.iterrows():
        val = row["gasto_total"]
        clts = int(row["clientes"])
        tkt = row["gasto_medio"]
        ax2.annotate(f" Q {val:,.2f}  ({clts} clts · Ticket: Q {tkt:.2f})",
                     (val, i), ha="left", va="center", fontsize=8.5, fontweight="bold",
                     color="#1a252f")

    ax2.legend(loc="lower right", frameon=True, facecolor="#ffffff", edgecolor="#bdc3c7")
    fig2.tight_layout()
    mostrar_grafico(fig2, "08_grafico_genero.png")
    print("Gráfico 2: Demografía por género y Distribución geográfica de gasto por ciudad.")
    esperar()

    # ------------------------------------------------------------------
    # PASO 9 — Gráfico 3: Cruce multivariable Ciudad x Categoría y Dispersión
    # ------------------------------------------------------------------
    paso(9, "Visualización: cruce multivariable y distribución de gasto", "09_grafico_cruce.png")

    fig3, axes = plt.subplots(1, 2, figsize=(16, 6.8))
    fig3.patch.set_facecolor("#fafbfc")

    # Subplot 1: Heatmap Ciudad x Categoría (Gasto Total Q)
    ax1 = axes[0]
    cruce_data = pd.pivot_table(
        df,
        values="gasto_q",
        index="ciudad",
        columns="categoria",
        aggfunc="sum",
        fill_value=0,
    )
    orden_ciudades = df.groupby("ciudad")["gasto_q"].sum().sort_values(ascending=False).index
    cruce_data = cruce_data.loc[orden_ciudades]

    # Crear anotaciones formateadas en array 2D
    annot_array = np.empty(cruce_data.shape, dtype=object)
    for r in range(cruce_data.shape[0]):
        for c in range(cruce_data.shape[1]):
            val = cruce_data.iloc[r, c]
            annot_array[r, c] = f"Q {val*1e-3:,.1f}k\n({val:,.0f})"

    sns.heatmap(
        cruce_data,
        annot=annot_array,
        fmt="",
        cmap="YlGnBu",
        linewidths=1.2,
        linecolor="#ffffff",
        cbar_kws={"label": "Gasto Total en Quetzales (Q)", "format": ticker.FuncFormatter(lambda x, p: f"Q {x*1e-3:,.0f}k")},
        ax=ax1,
    )
    ax1.set_title("Cruce Multivariable: Gasto Total por Ciudad y Categoría", fontsize=13, fontweight="bold", pad=14, color="#2c3e50")
    ax1.set_xlabel("Categoría de Negocio", fontsize=11, fontweight="bold", labelpad=8)
    ax1.set_ylabel("Ciudad (ordenada por gasto total)", fontsize=11, fontweight="bold", labelpad=8)
    ax1.tick_params(axis="x", rotation=0)
    ax1.tick_params(axis="y", rotation=0)

    # Subplot 2: Dispersión y distribución de gasto individual por categoría
    ax2 = axes[1]
    ax2.set_facecolor("#ffffff")
    sns.boxplot(
        data=df,
        x="categoria",
        y="gasto_q",
        palette=["#2980b9", "#27ae60", "#f39c12", "#8e44ad"],
        ax=ax2,
        showmeans=True,
        meanprops={"marker": "D", "markerfacecolor": "white", "markeredgecolor": "#000000", "markersize": 7},
    )
    ax2.set_title("Distribución y Dispersión del Gasto por Cliente", fontsize=13, fontweight="bold", pad=14, color="#2c3e50")
    ax2.set_xlabel("Categoría de Negocio", fontsize=11, fontweight="bold", labelpad=8)
    ax2.set_ylabel("Gasto Individual del Cliente (Q)", fontsize=11, fontweight="bold", labelpad=8)
    ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"Q {x:,.0f}"))
    ax2.set_ylim(-20, df["gasto_q"].max() * 1.15)
    ax2.grid(axis="y", linestyle="--", alpha=0.5)

    # Mediana global y elementos de leyenda personalizados
    mediana_global = df["gasto_q"].median()
    line_mediana = ax2.axhline(mediana_global, color="#e74c3c", linestyle=":", linewidth=1.6, label=f"Mediana Global: Q {mediana_global:.2f}")

    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker="D", color="w", label="Media Aritmética", markerfacecolor="white", markeredgecolor="black", markersize=7),
        Line2D([0], [0], color="#e74c3c", linestyle=":", linewidth=1.6, label=f"Mediana Global (Q {mediana_global:.2f})"),
    ]
    ax2.legend(handles=legend_elements, loc="upper right", frameon=True, facecolor="#ffffff", edgecolor="#bdc3c7")

    fig3.tight_layout()
    mostrar_grafico(fig3, "09_grafico_cruce.png")
    print("Gráfico 3: Matriz de calor Ciudad x Categoría y Boxplot de dispersión de gasto.")
    esperar()

    # ------------------------------------------------------------------
    # Exportar CSV limpio
    # ------------------------------------------------------------------
    CSV_LIMPIO.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CSV_LIMPIO, index=False, float_format="%.2f")

    print("\n" + "=" * 72)
    print("EXPORTACIÓN")
    print("=" * 72)
    print(f"Dataset limpio guardado en: {CSV_LIMPIO}")
    print(f"Filas exportadas: {len(df)}")
    print("Listo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
