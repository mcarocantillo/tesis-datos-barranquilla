"""Sensibilidad a la celda de ERA5-Land: el clima y la carga del Paso 3 en las celdas de 0,1° alrededor de Barranquilla.

La propuesta supone que el clima de una celda representa a toda la ciudad y prueba el supuesto en la sensibilidad
(isla de calor). Este script da una primera cota: repite el índice de calor, los grados-hora y la carga del Paso 3 de
la vivienda media en las celdas de tierra de una ventana de 3 × 3 (10,9–11,1° N; 74,7–74,9° O) en 2015–2025. ERA5-Land
no resuelve la isla de calor urbana (su cobertura del suelo no distingue la ciudad), así que la variación entre celdas
refleja la distancia al mar y al río, no el efecto de la ciudad.

Uso:  python scripts/05_celdas_vecinas.py [CARPETA_DE_DESCARGAS]   (por defecto, ~/Downloads)
Salida: salidas/celdas_vecinas.csv   por celda: medias de T, Td, HI e irradiancia, grados-hora (26,5 °C) y carga
                                     del Paso 3, con su diferencia frente a la celda de referencia (11,0 N; 74,8 O)
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

RAIZ = Path(__file__).resolve().parents[1]
BASE = RAIZ.parents[1]
sys.path.insert(0, str(BASE / "arquetipos"))
COMPUERTA = next(p for p in (BASE / "compuerta_horaria" / "scripts", BASE / "scripts" / "compuerta") if p.exists())
sys.path.insert(0, str(COMPUERTA))
from comun import humedad_relativa, indice_calor  # noqa: E402
from src import carga as cg  # noqa: E402

SALIDAS = RAIZ / "salidas"
TABLAS_ARQ = BASE / "arquetipos" / "salidas" / "tablas"
LATS, LONS = slice(11.15, 10.85), slice(285.05, 285.35)  # la latitud va de norte a sur en los archivos
REF = (11.0, 285.2)
VARIABLES = {"era5land_met": ["t2m", "d2m"], "era5land_rad_tp": ["ssrd"]}
COMPONENTES = {"cubierta": "c_t", "muros": "c_m", "ventanas": "c_v", "infiltracion_sensible": "c_V_sens",
               "latente": "c_V_lat"}


def leer(raiz):
    datos = {}
    for carpeta, variables in VARIABLES.items():
        for var in variables:
            partes = []
            for f in sorted((raiz / carpeta).glob(f"*.{var}.e5land.*.nc")):
                with xr.open_dataset(f) as ds:
                    partes.append(ds[var].sel(latitude=LATS, longitude=LONS).load())
            datos[var] = xr.concat(partes, dim="valid_time").sortby("valid_time")
            print(f"  {var}: {datos[var].sizes}", flush=True)
    return datos


def main():
    raiz = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "Downloads"
    d = leer(raiz)
    q = pd.read_csv(TABLAS_ARQ / "clima_gdex_carga.csv", index_col="clima").loc["gdex"]
    c0 = pd.read_csv(TABLAS_ARQ / "clima_gdex_coeficientes.csv", index_col="coeficiente")["gdex"]
    geo = {k: q[k] / c0[v] for k, v in COMPONENTES.items()}
    filas = []
    for lat in d["t2m"].latitude.values:
        for lon in d["t2m"].longitude.values:
            t = d["t2m"].sel(latitude=lat, longitude=lon).to_series()
            if t.isna().mean() > 0.5:
                continue  # mar
            td = d["d2m"].sel(latitude=lat, longitude=lon).to_series()
            acc = d["ssrd"].sel(latitude=lat, longitude=lon).to_series()
            s = pd.DataFrame({"T": t - 273.15, "Td": td - 273.15, "acc": acc})
            s = s[~s.index.duplicated()].sort_index()
            s["I"] = (np.where(s.index.hour == 1, s["acc"], s["acc"].diff()) / 3600).clip(min=0)
            s.index = s.index - pd.Timedelta(hours=5)  # hora local
            s = s[(s.index.year >= 2015) & (s.index.year <= 2025)].dropna()
            hr = humedad_relativa(s["T"], s["Td"])
            hi = pd.Series(np.asarray(indice_calor(s["T"], hr)), index=s.index)
            c = cg.coeficientes(c=pd.DataFrame({"anio": s.index.year, "T": s["T"].to_numpy(),
                                                "Td": s["Td"].to_numpy(), "I": s["I"].to_numpy()}))
            carga = sum(c[v] * geo[k] for k, v in COMPONENTES.items())
            filas.append({"lat": round(float(lat), 2), "lon": round(float(lon) - 360, 2), "horas": len(s),
                          "T": s["T"].mean(), "Td": s["Td"].mean(), "HI": hi.mean(), "I": s["I"].mean(),
                          "CDH_26.5_anual": (hi - 26.5).clip(lower=0).groupby(hi.index.year).sum().mean(),
                          "carga_kWh_anio": carga,
                          "referencia": bool(np.isclose(lat, REF[0]) and np.isclose(lon, REF[1]))})
    t = pd.DataFrame(filas)
    ref = t[t["referencia"]].iloc[0]
    for v in ["T", "Td", "HI", "I"]:
        t[f"dif_{v}"] = t[v] - ref[v]
    for v in ["CDH_26.5_anual", "carga_kWh_anio"]:
        t[f"dif_%_{v}"] = 100 * (t[v] / ref[v] - 1)
    SALIDAS.mkdir(parents=True, exist_ok=True)
    t.round(4).to_csv(SALIDAS / "celdas_vecinas.csv", index=False)
    print(t.round(2).to_string(index=False))


if __name__ == "__main__":
    main()
