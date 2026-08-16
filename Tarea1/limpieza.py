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


def mostrar_grafico(fig: plt.Figure) -> None:
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
    print("Valores únicos de genero:", sorted(df["genero"].astype(str).str.strip().unique().tolist()))
    print("Valores únicos de categoria:", sorted(df["categoria"].astype(str).str.strip().unique().tolist()))
    print("Muestra de ciudades:", sorted(df["ciudad"].astype(str).str.strip().unique().tolist())[:15])
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
    # PASO 7 — Gráfico de gasto
    # ------------------------------------------------------------------
    paso(7, "Visualización: gasto por categoría", "07_grafico_gasto.png")

    fig1, axes = plt.subplots(1, 2, figsize=(12, 5))
    comparacion = pd.DataFrame({"Antes": nulos_antes, "Después": nulos_despues})
    comparacion.plot(kind="bar", ax=axes[0], color=["#c0392b", "#27ae60"])
    axes[0].set_title("Nulos por columna: antes vs después")
    axes[0].set_ylabel("Cantidad de nulos")
    axes[0].tick_params(axis="x", rotation=30)

    gasto_cat = (
        df.groupby("categoria", as_index=False)["gasto_q"]
        .sum()
        .sort_values("gasto_q", ascending=False)
    )
    sns.barplot(data=gasto_cat, x="categoria", y="gasto_q", ax=axes[1], color="#2980b9")
    axes[1].set_title("Gasto total (Q) por categoría")
    axes[1].set_xlabel("Categoría")
    axes[1].set_ylabel("Gasto total (Q)")
    fig1.tight_layout()
    mostrar_grafico(fig1)
    print("Gráfico 1: nulos antes/después y gasto total por categoría.")
    esperar()

    # ------------------------------------------------------------------
    # PASO 8 — Gráfico de género y ciudad
    # ------------------------------------------------------------------
    paso(8, "Visualización: género y ciudad", "08_grafico_genero.png")

    fig2, axes = plt.subplots(1, 2, figsize=(12, 5))
    orden_gen = df["genero"].value_counts()
    sns.barplot(x=orden_gen.index, y=orden_gen.values, ax=axes[0], color="#8e44ad")
    axes[0].set_title("Distribución de clientes por género")
    axes[0].set_xlabel("Género")
    axes[0].set_ylabel("Clientes")

    gasto_ciudad = (
        df.groupby("ciudad", as_index=False)["gasto_q"]
        .sum()
        .sort_values("gasto_q", ascending=False)
    )
    sns.barplot(data=gasto_ciudad, x="gasto_q", y="ciudad", ax=axes[1], color="#16a085")
    axes[1].set_title("Gasto total (Q) por ciudad")
    axes[1].set_xlabel("Gasto total (Q)")
    axes[1].set_ylabel("Ciudad")
    fig2.tight_layout()
    mostrar_grafico(fig2)
    print("Gráfico 2: distribución por género y gasto total por ciudad.")
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
