"""Extrae la celda de Barranquilla de ERA5-Land descargado de GDEX (NCAR), pedidos 953933 y 953943.

GDEX distribuye el mismo ERA5-Land del ECMWF que el Climate Data Store, en archivos NetCDF de cinco días sobre una
malla de 0,1° (10,0–11,9° N; 74,0–74,9° O). La usuaria los descarga con los scripts gdex-download que genera
GDEX para cada pedido, en dos carpetas: era5land_met (t2m, d2m, sp, u10, v10) y era5land_rad_tp (ssrd, strd, tp).

Las variables acumuladas (ssrd, strd, tp) se suman desde las 00 UTC; el valor horario es la diferencia con la hora
anterior, salvo a la 01 UTC, que es la primera hora acumulada. Las horas quedan en UTC.

Uso:  python 01b_extraer_era5land_gdex.py [CARPETA_DE_DESCARGAS]   (por defecto, ~/Downloads)
Salida: datos/crudos/era5land_gdex/era5land_horario_11.0N_74.8W.csv.gz
        T y Td (°C), p_kPa, I y L (W/m², onda corta y larga), viento, u10 y v10 (m/s) y lluvia_mm, por hora UTC.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

from comun import CRUDOS, LAT, LON

SALIDA = CRUDOS / "era5land_gdex" / "era5land_horario_11.0N_74.8W.csv.gz"
CARPETAS = {"era5land_met": ["t2m", "d2m", "sp", "u10", "v10"], "era5land_rad_tp": ["ssrd", "strd", "tp"]}
ACUMULADAS = ["ssrd", "strd", "tp"]


def extraer(raiz):
    """Serie horaria de la celda más cercana a (LAT, LON), con las acumuladas pasadas a valores horarios."""
    cols = {}
    for carpeta, variables in CARPETAS.items():
        for var in variables:
            archivos = sorted((raiz / carpeta).glob(f"*.{var}.e5land.*.nc"))
            partes = []
            for f in archivos:
                with xr.open_dataset(f) as ds:
                    p = ds[var].sel(latitude=LAT, longitude=LON % 360, method="nearest")
                    partes.append(p.to_series())
            cols[var] = pd.concat(partes).sort_index()
            print(f"  {var}: {len(archivos)} archivos, {len(cols[var])} horas", flush=True)
    s = pd.DataFrame(cols)
    s.index = pd.to_datetime(s.index).rename("tiempo_utc")
    s = s[~s.index.duplicated()]
    for var in ACUMULADAS:
        s[var] = np.where(s.index.hour == 1, s[var], s[var].diff())
    s = s.iloc[1:]  # la primera hora (00 UTC del 1-ene-2015) no tiene la anterior para desacumular
    return pd.DataFrame({"T": s["t2m"] - 273.15, "Td": s["d2m"] - 273.15, "p_kPa": s["sp"] / 1000,
                         "I": (s["ssrd"] / 3600).clip(lower=0), "L": s["strd"] / 3600,
                         "viento": np.hypot(s["u10"], s["v10"]), "u10": s["u10"], "v10": s["v10"],
                         "lluvia_mm": (s["tp"] * 1000).clip(lower=0)})


if __name__ == "__main__":
    raiz = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "Downloads"
    g = extraer(raiz)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    g.round(4).to_csv(SALIDA)
    print(f"  {SALIDA.name}: {g.index.min()} a {g.index.max()}")
