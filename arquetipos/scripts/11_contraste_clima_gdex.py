"""Contraste del clima del Paso 3 con ERA5-Land completo descargado de GDEX (NCAR), pedidos 953933 y 953943.

La Fase 1 usa temperatura y punto de rocío de ERA5-Land (copia de Open-Meteo) y la irradiancia de ERA5 a 0,25°,
porque esa copia no trae la radiación de ERA5-Land (supuesto S17). Este script extrae la celda de ERA5-Land más
cercana al punto de Open-Meteo (11,0 N; 74,8 O), compara las series hora a hora y recalcula los coeficientes
climáticos del Paso 3 con tres climas. Es una prueba de robustez: no cambia la solución de la Fase 1.

  base       el de la Fase 1 (Open-Meteo)
  gdex_era5  T y Td de GDEX con la irradiancia de ERA5 (debe reproducir la base)
  gdex       T, Td e irradiancia de ERA5-Land de GDEX
  gdex_p     igual a gdex, con la presión superficial horaria en la humedad específica (la Fase 1 usa 101,325 kPa)

Las variables acumuladas (ssrd, strd) se suman desde las 00 UTC; el valor horario es la diferencia con la hora
anterior, salvo a la 01 UTC, que es la primera hora acumulada. Todas las horas están en UTC, como en Open-Meteo.

Uso: python scripts/11_contraste_clima_gdex.py [--gdex CARPETA_DESCARGAS] [--extraer]
     (si ya existe la serie del punto, la de compuerta_horaria/scripts/01b_extraer_era5land_gdex.py, la reutiliza)
Salidas:
  compuerta_horaria/datos/crudos/era5land_gdex/era5land_horario_11.0N_74.8W.csv.gz  serie horaria 2015–2026-09
  salidas/tablas/clima_gdex_contraste.csv     sesgo, RMSE y correlación hora a hora de T, Td e irradiancia
  salidas/tablas/clima_gdex_coeficientes.csv  coeficientes del Paso 3 con cada clima y diferencia frente a la base
  salidas/tablas/clima_gdex_carga.csv         carga media por vivienda y por componente con cada clima, y R² de los
                                              arquetipos finales (por vivienda y por m²) con esa carga
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src import carga as cg  # noqa: E402
from src.comun import CLIMA, INTERNOS, ML, TABLAS, cargar_viviendas  # noqa: E402

LAT, LON = 11.0, -74.8 + 360  # punto de Open-Meteo; la malla de GDEX va en 0–360
SERIE = ML / "compuerta_horaria" / "datos" / "crudos" / "era5land_gdex" / "era5land_horario_11.0N_74.8W.csv.gz"
CARPETAS = {"era5land_met": ["t2m", "d2m", "sp", "u10", "v10"], "era5land_rad_tp": ["ssrd", "strd", "tp"]}
ACUMULADAS = ["ssrd", "strd", "tp"]


def extraer(raiz):
    """Serie horaria de la celda más cercana al punto, con las acumuladas pasadas a valores horarios."""
    cols = {}
    for carpeta, variables in CARPETAS.items():
        for var in variables:
            archivos = sorted((raiz / carpeta).glob(f"*.{var}.e5land.*.nc"))
            partes = []
            for f in archivos:
                with xr.open_dataset(f) as ds:
                    p = ds[var].sel(latitude=LAT, longitude=LON, method="nearest")
                    partes.append(p.to_series())
            cols[var] = pd.concat(partes).sort_index()
            print(f"  {var}: {len(archivos)} archivos, {len(cols[var])} horas", flush=True)
    s = pd.DataFrame(cols)
    s.index = pd.to_datetime(s.index).rename("tiempo_utc")
    s = s[~s.index.duplicated()]
    for var in ACUMULADAS:
        dif = s[var].diff()
        s[var] = np.where(s.index.hour == 1, s[var], dif)
    s = s.iloc[1:]  # la primera hora (00 UTC del 1-ene-2015) no tiene la anterior para desacumular
    return pd.DataFrame({"T": s["t2m"] - 273.15, "Td": s["d2m"] - 273.15, "p_kPa": s["sp"] / 1000,
                         "I": (s["ssrd"] / 3600).clip(lower=0), "L": s["strd"] / 3600,
                         "viento": np.hypot(s["u10"], s["v10"]), "lluvia_mm": (s["tp"] * 1000).clip(lower=0)})


def openmeteo():
    filas = []
    for a in cg.ANIOS:
        h = json.loads((CLIMA / f"om_{a}.json").read_text(encoding="utf-8"))["hourly"]
        filas.append(pd.DataFrame({"T": h["temperature_2m_era5_land"], "Td": h["dew_point_2m_era5_land"],
                                   "I": h["shortwave_radiation_era5"]}, index=pd.to_datetime(h["time"])))
    return pd.concat(filas)


def contraste(om, g):
    j = om.join(g, lsuffix="_om", rsuffix="_gdex", how="inner")
    filas = []
    for var, ref in [("T", "T_om"), ("Td", "Td_om"), ("I", "I_om")]:
        d = j[f"{var}_gdex"] - j[ref]
        filas.append({"variable": var, "fuente_fase1": "ERA5 0,25°" if var == "I" else "ERA5-Land (Open-Meteo)",
                      "horas": len(d), "media_fase1": j[ref].mean(), "media_gdex": j[f"{var}_gdex"].mean(),
                      "sesgo": d.mean(), "rmse": np.sqrt((d ** 2).mean()), "dif_abs_max": d.abs().max(),
                      "correlacion": j[ref].corr(j[f"{var}_gdex"])})
    return pd.DataFrame(filas)


def coeficientes_con_presion(c):
    """Coeficientes del Paso 3 con la presión horaria en la humedad específica del aire exterior."""
    base = cg.coeficientes(c=c)
    p = cg.DECISION["carga"]
    wc = cg._w(p["humedad_relativa_consigna"] * cg._pv(p["consigna_C"]))
    pv = cg._pv(c["Td"])
    w = 0.622 * pv / (c["p_kPa"] - pv)
    s_w = (w - wc).clip(lower=0).groupby(c["anio"]).sum().mean()
    base["c_V_lat"] = cg.RHO * p["renovaciones_h"] / 3600 * cg.HFG * s_w / 1000
    base["w_h"] = s_w
    return base


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gdex", type=Path, default=Path.home() / "Downloads")
    ap.add_argument("--extraer", action="store_true", help="vuelve a leer los NetCDF aunque exista la serie")
    args = ap.parse_args()

    if SERIE.exists() and not args.extraer:
        g = pd.read_csv(SERIE, index_col="tiempo_utc", parse_dates=True)
    else:
        print("Extrayendo la celda de ERA5-Land...", flush=True)
        g = extraer(args.gdex)
        SERIE.parent.mkdir(parents=True, exist_ok=True)
        g.round(4).to_csv(SERIE)
    print(f"  celda más cercana a {LAT} N, {360 - LON:.1f} O; {g.index.min()} a {g.index.max()}")

    om = openmeteo()
    TABLAS.mkdir(parents=True, exist_ok=True)
    tc = contraste(om, g)
    tc.to_csv(TABLAS / "clima_gdex_contraste.csv", index=False)
    print(tc.round(3).to_string(index=False))

    g11 = g[(g.index.year >= cg.ANIOS.start) & (g.index.year < cg.ANIOS.stop)]
    climas = {
        "base": None,
        "gdex_era5": pd.DataFrame({"T": g11["T"], "Td": g11["Td"]}).join(om["I"], how="inner"),
        "gdex": g11[["T", "Td", "I"]],
        "gdex_p": g11[["T", "Td", "I", "p_kPa"]],
    }
    coefs = {}
    for nombre, c in climas.items():
        if c is not None:
            c = c.assign(anio=c.index.year).reset_index(drop=True)
        coefs[nombre] = coeficientes_con_presion(c) if nombre == "gdex_p" else cg.coeficientes(c=c)
    tco = pd.DataFrame(coefs)
    for nombre in climas:
        if nombre != "base":
            tco[f"dif_%_{nombre}"] = 100 * (tco[nombre] / tco["base"] - 1)
    tco.index.name = "coeficiente"
    tco.to_csv(TABLAS / "clima_gdex_coeficientes.csv")
    print(tco.round(3).to_string())

    v = cargar_viviendas()
    geo = cg.geometria(v)
    arq = pd.read_parquet(INTERNOS / "arquetipos_final.parquet").reindex(v.index)
    filas = []
    for nombre, c in coefs.items():
        q = cg.carga(geo, c)
        tot = q.sum(axis=1)
        fila = {"clima": nombre, **q.mean().to_dict(), "total": tot.mean(),
                "R2_por_vivienda": cg.r2(tot, arq["por_vivienda"]),
                "R2_por_m2": cg.r2(tot / v["area_construida"], arq["por_m2"])}
        filas.append(fila)
    tq = pd.DataFrame(filas).set_index("clima")
    tq["dif_%_total"] = 100 * (tq["total"] / tq.loc["base", "total"] - 1)
    tq.to_csv(TABLAS / "clima_gdex_carga.csv")
    print("Carga media por vivienda (kWh/año):")
    print(tq.round(1).to_string())


if __name__ == "__main__":
    main()
