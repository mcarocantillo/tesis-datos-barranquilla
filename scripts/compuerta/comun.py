"""Rutas y funciones compartidas de la compuerta horaria (Ec. 10 de la propuesta v4)."""
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent  # en el repositorio: scripts/compuerta/
CRUDOS = RAIZ / "datos" / "crudos"
PROC = RAIZ / "datos" / "procesados"
SALIDAS = RAIZ / "salidas"
for _p in (CRUDOS, PROC, SALIDAS):
    _p.mkdir(parents=True, exist_ok=True)

# Celda de Barranquilla y estación IDEAM del aeropuerto Ernesto Cortissoz
LAT, LON = 10.96, -74.80
ESTACION_IDEAM = "0029045190"
INICIO = "2015-01-01"
TZ_LOCAL = "America/Bogota"  # UTC-5 sin horario de verano


def humedad_relativa(t_c, td_c):
    """Humedad relativa (%) a partir de la temperatura y el punto de rocío (Magnus, Alduchov y Eskridge 1996)."""
    def es(x):
        return 6.1094 * np.exp(17.625 * x / (x + 243.04))
    return np.clip(100 * es(td_c) / es(t_c), 0, 100)


def indice_calor(t_c, hr):
    """Índice de calor (°C) de la NOAA: regresión de Rothfusz con los ajustes oficiales.

    Si la fórmula simple de Steadman da menos de 80 °F se usa esa; si no, Rothfusz con los ajustes
    por humedad baja (HR < 13 %) y alta (HR > 85 %).
    """
    t = np.asarray(t_c, dtype=float) * 9 / 5 + 32
    rh = np.asarray(hr, dtype=float)
    simple = 0.5 * (t + 61.0 + (t - 68.0) * 1.2 + rh * 0.094)
    hi = (-42.379 + 2.04901523 * t + 10.14333127 * rh - 0.22475541 * t * rh
          - 6.83783e-3 * t ** 2 - 5.481717e-2 * rh ** 2 + 1.22874e-3 * t ** 2 * rh
          + 8.5282e-4 * t * rh ** 2 - 1.99e-6 * t ** 2 * rh ** 2)
    aj_seco = ((13 - rh) / 4) * np.sqrt(np.clip((17 - np.abs(t - 95.0)) / 17, 0, None))
    hi = np.where((rh < 13) & (t >= 80) & (t <= 112), hi - aj_seco, hi)
    aj_humedo = ((rh - 85) / 10) * ((87 - t) / 5)
    hi = np.where((rh > 85) & (t >= 80) & (t <= 87), hi + aj_humedo, hi)
    hi = np.where((simple + t) / 2 < 80, simple, hi)
    return (hi - 32) * 5 / 9


def festivos_colombia(anios):
    import holidays
    return set(holidays.Colombia(years=list(anios)).keys())


def calendario(fechas):
    """Tipo de día (laboral, sábado, domingo o festivo) y periodos especiales para cada fecha."""
    f = pd.DatetimeIndex(pd.to_datetime(fechas)).normalize()
    fest = festivos_colombia(range(f.year.min(), f.year.max() + 1))
    df = pd.DataFrame(index=f)
    es_fest = np.array([d.date() in fest for d in f])
    df["festivo"] = es_fest
    df["tipo_dia"] = np.where(es_fest | (f.dayofweek == 6), "dom_fest",
                              np.where(f.dayofweek == 5, "sabado", "laboral"))
    df["dia_semana"] = f.dayofweek
    # Fin de año (24 dic a 6 ene): comercio y hogares cambian de rutina
    df["fin_anio"] = ((f.month == 12) & (f.day >= 24)) | ((f.month == 1) & (f.day <= 6))
    # Carnaval de Barranquilla: sábado a martes antes del miércoles de ceniza (Pascua - 46 días)
    from dateutil.easter import easter
    carnaval = set()
    for a in range(f.year.min(), f.year.max() + 1):
        ceniza = pd.Timestamp(easter(a)) - pd.Timedelta(days=46)
        carnaval |= {ceniza - pd.Timedelta(days=k) for k in range(1, 5)}
    df["carnaval"] = f.isin(list(carnaval))
    # Semana Santa (lunes a sábado santo)
    santa = set()
    for a in range(f.year.min(), f.year.max() + 1):
        p = pd.Timestamp(easter(a))
        santa |= {p - pd.Timedelta(days=k) for k in range(1, 7)}
    df["semana_santa"] = f.isin(list(santa))
    return df
