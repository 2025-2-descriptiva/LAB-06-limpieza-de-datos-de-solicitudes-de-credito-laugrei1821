"""
Escriba el codigo que ejecute la accion solicitada en la pregunta.
"""
"""
    Realice la limpieza del archivo "files/input/solicitudes_de_credito.csv".
    El archivo tiene problemas como registros duplicados y datos faltantes.
    Tenga en cuenta todas las verificaciones discutidas en clase para
    realizar la limpieza de los datos.

    El archivo limpio debe escribirse en "files/output/solicitudes_de_credito.csv"

"""

import os
import re
import unicodedata
import pandas as pd

# Lista de columnas requeridas

COLS = [
    "sexo",
    "tipo_de_emprendimiento",
    "idea_negocio",
    "barrio",
    "estrato",
    "comuna_ciudadano",
    "fecha_de_beneficio",
    "monto_del_credito",
    "línea_credito",
]

# Funciones auxiliares

def validar_directorios():
    os.makedirs("files/input", exist_ok=True)
    os.makedirs("files/output", exist_ok=True)


def limpiar_texto(s: pd.Series) -> pd.Series:
    s = s.astype(str).str.strip().str.lower()
    s = s.str.replace(r"[-_]+", " ", regex=True)
    s = s.str.replace(r"\s+", " ", regex=True).str.strip()
    s = _strip_accents_series(s)
    return s

def convertir_montos(s: pd.Series) -> pd.Series:
    """
    Convierte montos tipo '$ 7.000.000', '7,000,000', '7000000' a int.
    """
    s = s.astype(str).str.strip()
    s = s.str.replace(r"([.,]0+)$", "", regex=True)
    s = s.str.replace(r"[^0-9]", "", regex=True)    
    s = pd.to_numeric(s, errors="coerce").astype("Int64")
    return s

def normalizar_fecha_ddyymm(df, col="fecha_de_beneficio"):
    s = df[col].astype(str).str.strip()

    s = s.str.replace(r"[.\-]", "/", regex=True)
    mask_year_first = s.str.match(r"^\d{4}/\d{1,2}/\d{1,2}$")

    s_year_first = pd.to_datetime(s.where(mask_year_first), format="%Y/%m/%d", errors="coerce")
    s_day_first  = pd.to_datetime(s.where(~mask_year_first), dayfirst=True, errors="coerce")

    dt = s_year_first.fillna(s_day_first)
    return dt.dt.strftime("%d/%m/%Y")


def _strip_accents_series(s: pd.Series) -> pd.Series:
    s = s.astype(str)
    return (s.apply(lambda x: unicodedata.normalize("NFKD", x)
                             .encode("ascii","ignore").decode("utf-8")))



def pregunta_01():


    validar_directorios()

    #  Carga data
    input_file = "files/input/solicitudes_de_credito.csv"
    df = pd.read_csv(input_file, sep=";")

    df["fecha_de_beneficio"] = normalizar_fecha_ddyymm(df, "fecha_de_beneficio")

    # Eliminación de valores nulos 
    required_cols = [
        "sexo",
        "tipo_de_emprendimiento",
        "idea_negocio",
        "barrio",
        "estrato",
        "comuna_ciudadano",
        "fecha_de_beneficio",
        "monto_del_credito",
        "línea_credito",
    ]
    keep_cols = [c for c in required_cols if c in df.columns]
    df = df.dropna(subset=keep_cols)



    # Normalización de columnas
    text_cols = [
        "sexo",
        "tipo_de_emprendimiento",
        "idea_negocio",
        "barrio",
        "línea_credito",
    ]
    for c in text_cols:
        if c in df.columns:
            df[c] = limpiar_texto(df[c])   

        
    #  Convertir montos_del:credito a entero

    if "monto_del_credito" in df.columns:
        df["monto_del_credito"] = convertir_montos(df["monto_del_credito"])

    if "estrato" in df.columns:
        df["estrato"] = pd.to_numeric(df["estrato"], errors="coerce").astype("Int64")

    # Borrar Duplicados

    cols = [
    "sexo",
    "tipo_de_emprendimiento",
    "idea_negocio",
    "barrio",
    "estrato",
    "comuna_ciudadano",
    "fecha_de_beneficio",
    "monto_del_credito",
    "línea_credito",
    ]

    df = df.drop_duplicates(subset=cols, keep="first")
    
    present = [c for c in COLS if c in df.columns]
    df = df.drop_duplicates(subset=present, keep="first").reset_index(drop=True)

    # Exportar
    output_file = "files/output/solicitudes_de_credito.csv"
    df.to_csv(output_file, sep=";", index=False)


if __name__ == "__main__":
    pregunta_01()
