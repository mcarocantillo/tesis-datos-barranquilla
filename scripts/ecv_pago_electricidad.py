"""Hogares de Barranquilla que no pagan la electricidad y su tenencia de A/C, ECV 2024 y ECV 2019.

ECV 2024: P791 «¿Pagan en este hogar por la electricidad que consumen?» (1 sí, 2 sí, con el arriendo, 3 no pagan
pero tienen el servicio, 4 no tienen el servicio), según el diccionario del catálogo 861. Los intervalos usan el
diseño muestral: varianza por conglomerados (SEGMENTO = unidad primaria de muestreo, linealización de Taylor para
una razón, con reemplazo), como en deff_ecv24.py.
ECV 2019: no tiene P791; se toma como «no pagan» el pago de 0 pesos el mes pasado (P5018), sin intervalos.
Solo cabecera (CLASE 1) y estratos 1 a 6. Los microdatos se leen de los archivos del DANE tal como se descargaron,
en Downloads/DANE/ECV; la salida es agregada. Correr desde la raíz del repositorio:
python scripts/ecv_pago_electricidad.py"""
import io
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ECV = Path(__file__).resolve().parents[2].parent / "DANE" / "ECV"
LLAVE = ["DIRECTORIO", "SECUENCIA_ENCUESTA"]


def leer_zip(ruta, patron, columnas=None):
    with zipfile.ZipFile(ECV / ruta) as zf:
        nombre = [x for x in zf.namelist() if x.lower().endswith(".csv") and patron in x.lower()][0]
        crudo = zf.read(nombre)
    try:
        texto = crudo.decode("utf-8-sig")
    except UnicodeDecodeError:
        texto = crudo.decode("latin-1")
    d = pd.read_csv(io.StringIO(texto), sep=";", dtype=str, low_memory=False)
    d.columns = [c.replace("ï»¿", "").strip("﻿").strip() for c in d.columns]
    d = d[columnas] if columnas else d
    return d.apply(lambda s: s.str.strip())


def numero(s):
    return pd.to_numeric(s.astype(str).str.strip().str.replace(",", "."), errors="coerce")


def hogares_2024():
    v = leer_zip("ECV 2024/DBF-ENCV-Datos_vivienda-2024 (2).zip", "vivienda")
    v = v[(v.P1_DEPARTAMENTO == "08") & (v.P1_MUNICIPIO == "001") & (v.CLASE == "1")]
    seg = leer_zip("ECV 2024/BDF-ENCV-Variables_diseno_muestral-ENCV2024.zip", "muestral", ["DIRECTORIO", "SEGMENTO"])
    seg = seg.drop_duplicates("DIRECTORIO").set_index("DIRECTORIO").SEGMENTO
    s = leer_zip("ECV 2024/DBF-ENCV-Servicios_hogar-2024.zip", "servicios", LLAVE + ["FEX_C", "P791"])
    b = leer_zip("ECV 2024/DBF-ENCV-Condiciones_vida_hogar_tenencia_bienes-2024.zip", "bienes", LLAVE + ["P1077S11"])
    h = s[s.DIRECTORIO.isin(v.DIRECTORIO)].merge(b, on=LLAVE, how="left")
    h = h.merge(v[["DIRECTORIO", "P8520S1A1"]], on="DIRECTORIO")
    h["segmento"] = h.DIRECTORIO.map(seg)
    assert h.segmento.notna().all()
    return pd.DataFrame({"estrato": numero(h.P8520S1A1), "w": numero(h.FEX_C), "segmento": h.segmento,
                         "no_paga": (h.P791 == "3").astype(float), "ac": (h.P1077S11 == "1").astype(float)})


def hogares_2019():
    c = pd.read_csv(ECV / "ECV 2019" / "ECV2019_Barranquilla_consolidado.csv", sep=";", dtype=str, encoding="utf-8-sig")
    c = c[c.CLASE.str.strip() == "1"]
    return pd.DataFrame({"estrato": numero(c.ESTRATO), "w": numero(c.FEX_C), "segmento": np.nan,
                         "no_paga": (numero(c.PAGO_ELEC_P5018) == 0).astype(float), "ac": numero(c.TIENE_AC).fillna(0)})


def razon(h, y, dom):
    """Proporción ponderada de y en el dominio, con su error estándar por conglomerados (None sin diseño)."""
    wd = h.w * dom
    if wd.sum() == 0:
        return np.nan, np.nan
    p = (wd * y).sum() / wd.sum()
    if h.segmento.isna().all():
        return p, np.nan
    tc = (wd * (y - p) / wd.sum()).groupby(h.segmento).sum()
    C = h.segmento.nunique()
    return p, np.sqrt(C / (C - 1) * ((tc - tc.mean()) ** 2).sum())


def diferencia(h, y, d1, d2):
    """p(d1) − p(d2) con su error estándar por conglomerados; los dos dominios comparten segmentos."""
    w1, w2 = h.w * d1, h.w * d2
    if w1.sum() == 0 or w2.sum() == 0:
        return np.nan, np.nan
    p1, p2 = (w1 * y).sum() / w1.sum(), (w2 * y).sum() / w2.sum()
    if h.segmento.isna().all():
        return p1 - p2, np.nan
    z = w1 * (y - p1) / w1.sum() - w2 * (y - p2) / w2.sum()
    tc = z.groupby(h.segmento).sum()
    C = h.segmento.nunique()
    return p1 - p2, np.sqrt(C / (C - 1) * ((tc - tc.mean()) ** 2).sum())


def tabla(h, anio, pregunta):
    h = h[h.estrato.between(1, 6)]
    filas = []
    for e, dom in [(str(int(e)), (h.estrato == e).astype(float)) for e in range(1, 7)] + [("ciudad", pd.Series(1.0, index=h.index))]:
        p, ee = razon(h, h.no_paga, dom)
        a_no, ee_no = razon(h, h.ac, dom * h.no_paga)
        a_si, ee_si = razon(h, h.ac, dom * (1 - h.no_paga))
        dif, ee_dif = diferencia(h, h.ac, dom * (1 - h.no_paga), dom * h.no_paga)
        filas.append(dict(anio=anio, pregunta=pregunta, estrato=e, hogares_muestra=int(dom.sum()),
                          hogares_no_pagan=int((dom * h.no_paga).sum()), no_pagan_pct=100 * p, no_pagan_ic95=196 * ee,
                          AC_no_pagan_pct=100 * a_no, AC_no_pagan_ic95=196 * ee_no,
                          AC_pagan_pct=100 * a_si, AC_pagan_ic95=196 * ee_si,
                          AC_dif_puntos=100 * dif, AC_dif_ic95=196 * ee_dif))
    return pd.DataFrame(filas)


t = pd.concat([tabla(hogares_2024(), 2024, "P791 = 3 (no pagan, pero tienen el servicio)"),
               tabla(hogares_2019(), 2019, "P5018 = 0 (pagaron 0 pesos el mes pasado)")], ignore_index=True)
print(t.drop(columns="pregunta").round(1).to_string(index=False))
t.round(2).to_csv(Path(__file__).resolve().parents[1] / "tablas" / "ECV_pago_electricidad_Barranquilla.csv",
                  sep=";", index=False, encoding="utf-8-sig")
