"""Lectura de la ECV del DANE (archivos comprimidos tal como se descargaron) y estimación con su diseño muestral."""
import io
import zipfile

import numpy as np
import pandas as pd

from .comun import DECISION, ML

ECV = ML.parent / "DANE" / "ECV"


def leer_zip(ruta, patron, columnas=None):
    """CSV de un archivo comprimido de la ECV, con los nombres de columna limpios (sin marca de orden de bytes)."""
    with zipfile.ZipFile(ECV / ruta) as zf:
        nombre = [x for x in zf.namelist() if x.lower().endswith(".csv") and patron in x.lower()][0]
        crudo = zf.read(nombre)
    try:
        texto = crudo.decode("utf-8-sig")
    except UnicodeDecodeError:
        texto = crudo.decode("latin-1")
    d = pd.read_csv(io.StringIO(texto), sep=";", dtype=str, low_memory=False)
    d.columns = [c.replace("ï»¿", "").strip("﻿").strip() for c in d.columns]
    return d[columnas] if columnas else d


def numero(s):
    return pd.to_numeric(s.astype(str).str.strip().str.replace(",", "."), errors="coerce")


def segmentos_2024():
    """Segmento (unidad primaria de muestreo) de cada vivienda de la ECV 2024, por DIRECTORIO."""
    seg = leer_zip("ECV 2024/BDF-ENCV-Variables_diseno_muestral-ENCV2024.zip", "muestral", ["DIRECTORIO", "SEGMENTO"])
    seg = seg.assign(DIRECTORIO=seg["DIRECTORIO"].str.strip()).drop_duplicates("DIRECTORIO")
    return seg.set_index("DIRECTORIO")["SEGMENTO"]


def hogares_2024(servicios, bienes):
    """Viviendas y hogares de Barranquilla en la ECV 2024 con estrato, tipo (casa o apartamento), bloque, peso y
    segmento, más las columnas pedidas de «Servicios del hogar» y de «Tenencia de bienes» (como texto)."""
    v = leer_zip("ECV 2024/DBF-ENCV-Datos_vivienda-2024 (2).zip", "vivienda")
    v = v[(v["P1_DEPARTAMENTO"].str.strip() == "08") & (v["P1_MUNICIPIO"].str.strip() == "001")]
    viv = pd.DataFrame({"DIRECTORIO": v["DIRECTORIO"].str.strip().to_numpy(),
                        "estrato": numero(v["P8520S1A1"]).to_numpy(), "w": numero(v["FEX_C"]).to_numpy(),
                        "tipo": np.where(v["P1070"].str.strip() == "2", "apartamento", "casa")})
    viv["segmento"] = viv["DIRECTORIO"].map(segmentos_2024())
    assert viv["segmento"].notna().all()
    bloque = {e: b for b, ests in DECISION["variables"]["bloques_estrato"].items() for e in ests}
    viv["bloque"] = viv["estrato"].map(bloque)

    llave = ["DIRECTORIO", "SECUENCIA_ENCUESTA"]
    s = leer_zip("ECV 2024/DBF-ENCV-Servicios_hogar-2024.zip", "servicios", llave + ["FEX_C"] + list(servicios))
    b = leer_zip("ECV 2024/DBF-ENCV-Condiciones_vida_hogar_tenencia_bienes-2024.zip", "bienes", llave + list(bienes))
    for d in (s, b):
        for c in llave:
            d[c] = d[c].str.strip()
    h = s.merge(b, on=llave, how="left").merge(viv.drop(columns="w"), on="DIRECTORIO")
    h["w"] = numero(h["FEX_C"])
    return viv, h


def razon(y, w, dominio, segmento):
    """Media (o proporción) ponderada de y en un dominio y su error estándar por linealización de Taylor, con el
    segmento como unidad primaria (con reemplazo), sobre toda la muestra."""
    y, w, dominio = (np.asarray(a, float) for a in (y, w, dominio))
    wd = w * dominio
    if wd.sum() == 0:
        return np.nan, np.nan
    r = (wd * np.nan_to_num(y)).sum() / wd.sum()
    z = pd.Series(wd * (np.nan_to_num(y) - r) / wd.sum()).groupby(np.asarray(segmento)).sum().to_numpy()
    c = len(z)
    return float(r), float(np.sqrt(c / (c - 1) * ((z - z.mean()) ** 2).sum()))
