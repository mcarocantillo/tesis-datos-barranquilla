"""Clima horario de referencia (ERA5-Land, celda de Barranquilla) y contraste con la estación IDEAM 0029045190.

Fuentes de ERA5-Land, en este orden de preferencia:
  1. Archivo descargado por la usuaria del CDS con 01a_descargar_era5land_cds.py (datos/crudos/era5land_cds/).
  2. Copia provisional de ERA5-Land servida por Open-Meteo (archive-api.open-meteo.com, models=era5_land), sin
     credenciales. Open-Meteo no sirve viento ni radiación de ERA5-Land; esas dos variables se toman de ERA5
     (0,25°) y se marcan así en la columna 'fuente_viento_rad'.

Pasos: hora UTC -> hora local (UTC-5); radiación acumulada -> W/m² por hora (solo en el archivo del CDS);
humedad relativa (Magnus) e índice de calor (NOAA/Rothfusz); sesgo y RMSE frente a IDEAM por hora y por mes.

Uso:
  python 01_clima.py descargar      # Open-Meteo e IDEAM (datos.gov.co)
  python 01_clima.py procesar       # serie horaria y diaria + contraste con IDEAM
"""
import json
import sys
import zipfile

import numpy as np
import pandas as pd
import requests

from comun import (CRUDOS, ESTACION_IDEAM, INICIO, LAT, LON, PROC, SALIDAS, TZ_LOCAL, humedad_relativa,
                   indice_calor)

DIR_OM = CRUDOS / "openmeteo"
DIR_CDS = CRUDOS / "era5land_cds"
DIR_IDEAM = CRUDOS / "ideam"
for _d in (DIR_OM, DIR_CDS, DIR_IDEAM):
    _d.mkdir(parents=True, exist_ok=True)

IDEAM = {"temperatura": "sbwg-7ju4", "humedad": "uext-mhny"}


# ---------------------------------------------------------------- descargas
def descargar_openmeteo():
    hoy = pd.Timestamp.today().normalize()
    for anio in range(int(INICIO[:4]), hoy.year + 1):
        archivo = DIR_OM / f"om_{anio}.json"
        if archivo.exists() and anio < hoy.year:
            continue
        fin = min(pd.Timestamp(f"{anio}-12-31"), hoy - pd.Timedelta(days=7)).strftime("%Y-%m-%d")
        params = {
            "latitude": LAT, "longitude": LON, "start_date": f"{anio}-01-01", "end_date": fin,
            "hourly": "temperature_2m,dew_point_2m,wind_speed_10m,shortwave_radiation",
            "models": "era5_land,era5", "timezone": "GMT", "wind_speed_unit": "ms",
        }
        r = requests.get("https://archive-api.open-meteo.com/v1/archive", params=params, timeout=300)
        r.raise_for_status()
        archivo.write_text(r.text, encoding="utf-8")
        print(f"  Open-Meteo {anio}: ok")


def descargar_ideam():
    """Solo las observaciones en punto (minuto 00), que corresponden al dato instantáneo de ERA5."""
    for var, recurso in IDEAM.items():
        archivo = DIR_IDEAM / f"{var}.csv"
        filas, offset = [], 0
        while True:
            params = {
                "$select": "fechaobservacion,valorobservado",
                "$where": (f"codigoestacion='{ESTACION_IDEAM}' and fechaobservacion >= '{INICIO}T00:00:00' "
                           "and date_extract_mm(fechaobservacion)=0"),
                "$order": "fechaobservacion", "$limit": 50000, "$offset": offset,
            }
            r = requests.get(f"https://www.datos.gov.co/resource/{recurso}.json", params=params, timeout=300)
            r.raise_for_status()
            lote = r.json()
            filas += lote
            print(f"  IDEAM {var}: {len(filas)} registros")
            if len(lote) < 50000:
                break
            offset += 50000
        pd.DataFrame(filas).to_csv(archivo, index=False)


# ---------------------------------------------------------------- ERA5-Land
def leer_openmeteo():
    partes = []
    for f in sorted(DIR_OM.glob("om_*.json")):
        h = json.loads(f.read_text(encoding="utf-8"))["hourly"]
        partes.append(pd.DataFrame({
            "utc": pd.to_datetime(h["time"]),
            "t2m": h["temperature_2m_era5_land"],
            "td2m": h["dew_point_2m_era5_land"],
            "viento": h["wind_speed_10m_era5"],
            "rad": h["shortwave_radiation_era5"],
        }))
    df = pd.concat(partes).drop_duplicates("utc").set_index("utc").sort_index()
    df["fuente"] = "ERA5-Land vía Open-Meteo (provisional)"
    df["fuente_viento_rad"] = "ERA5 0,25° vía Open-Meteo"
    return df


def desacumular(ssrd_j_m2: pd.Series) -> pd.Series:
    """ERA5-Land acumula la radiación desde las 00 UTC; el valor de las 00 UTC es el total del día anterior.

    Flujo medio de la hora que termina en t: acc(t) si t es 01 UTC; si no, acc(t) - acc(t-1). Se pasa a W/m².
    """
    s = ssrd_j_m2.sort_index()
    previo = s.shift(1)
    paso = s - previo
    paso[s.index.hour == 1] = s[s.index.hour == 1]
    return (paso.clip(lower=0) / 3600.0)


def leer_cds():
    archivos = sorted(DIR_CDS.glob("*.zip")) + sorted(DIR_CDS.glob("*.nc"))
    if not archivos:
        return None
    import xarray as xr
    extraidos = DIR_CDS / "extraido"
    extraidos.mkdir(exist_ok=True)
    ncs = []
    for a in archivos:
        if a.suffix == ".zip":
            with zipfile.ZipFile(a) as z:
                z.extractall(extraidos)
            ncs += sorted(extraidos.glob("*.nc"))
        else:
            ncs.append(a)
    ds = xr.merge([xr.open_dataset(n) for n in ncs], compat="override")
    tiempo = "valid_time" if "valid_time" in ds.coords else "time"
    df = ds.to_dataframe().reset_index().set_index(tiempo).sort_index()
    df = df[~df.index.duplicated()]
    out = pd.DataFrame(index=pd.DatetimeIndex(df.index, name="utc"))
    out["t2m"] = df["t2m"] - 273.15
    out["td2m"] = df["d2m"] - 273.15
    out["viento"] = np.hypot(df["u10"], df["v10"])
    ssrd = df["ssrd"]
    # Detección: si es acumulada, a las 23 UTC (18 h local) vale más que a las 17 UTC (mediodía local)
    acumulada = ssrd[ssrd.index.hour == 23].median() > ssrd[ssrd.index.hour == 17].median()
    out["rad"] = desacumular(ssrd) if acumulada else ssrd / 3600.0
    out["fuente"] = "ERA5-Land (CDS, descarga de la usuaria)"
    out["fuente_viento_rad"] = "ERA5-Land (CDS)"
    print(f"  CDS: radiación {'desacumulada' if acumulada else 'ya horaria'}")
    return out


def clima_horario():
    df = leer_cds()
    if df is None:
        print("  No hay archivo del CDS: se usa la copia provisional de Open-Meteo.")
        df = leer_openmeteo()
    df.index = df.index.tz_localize("UTC").tz_convert(TZ_LOCAL).tz_localize(None)
    df.index.name = "hora_local"
    df["hr"] = humedad_relativa(df["t2m"], df["td2m"])
    df["hi"] = indice_calor(df["t2m"], df["hr"])
    return df


# ---------------------------------------------------------------- IDEAM
def leer_ideam():
    series = {}
    for var, col in [("temperatura", "t_ideam"), ("humedad", "hr_ideam")]:
        d = pd.read_csv(DIR_IDEAM / f"{var}.csv")
        d["hora_local"] = pd.to_datetime(d["fechaobservacion"]).dt.floor("h")
        d["v"] = pd.to_numeric(d["valorobservado"], errors="coerce")
        lim = (15, 45) if var == "temperatura" else (5, 100)
        d = d[d["v"].between(*lim)]
        series[col] = d.groupby("hora_local")["v"].mean()
    df = pd.DataFrame(series)
    df["hi_ideam"] = indice_calor(df["t_ideam"], df["hr_ideam"])
    return df


def contraste(era, ide):
    j = era[["t2m", "hr", "hi"]].join(ide, how="inner").dropna()
    filas = []
    for nombre, (a, b) in {"T (°C)": ("t2m", "t_ideam"), "HR (%)": ("hr", "hr_ideam"),
                           "HI (°C)": ("hi", "hi_ideam")}.items():
        e = j[a] - j[b]
        for clave, grupo in [("hora", j.index.hour), ("mes", j.index.month)]:
            g = e.groupby(grupo)
            t = pd.DataFrame({"sesgo": g.mean(), "rmse": g.apply(lambda x: np.sqrt((x ** 2).mean())),
                              "n": g.size()})
            t["variable"], t["agrupacion"] = nombre, clave
            filas.append(t.rename_axis("valor").reset_index())
        filas.append(pd.DataFrame([{"variable": nombre, "agrupacion": "total", "valor": 0, "sesgo": e.mean(),
                                    "rmse": np.sqrt((e ** 2).mean()), "n": len(e),
                                    "corr_diaria": j[a].resample("D").mean().corr(j[b].resample("D").mean())}]))
    tabla = pd.concat(filas, ignore_index=True)
    # Verificación de la hora: desfase (h) que minimiza el RMSE de la temperatura
    desfases = {s: np.sqrt(((j["t2m"] - ide["t_ideam"].shift(s).reindex(j.index)) ** 2).mean())
                for s in range(-3, 4)}
    return tabla, desfases, j


def main():
    if "descargar" in sys.argv:
        descargar_openmeteo()
        descargar_ideam()
    if "procesar" in sys.argv:
        era = clima_horario()
        era.to_parquet(PROC / "clima_horario.parquet")
        dia = pd.DataFrame({
            "hi_media": era["hi"].resample("D").mean(),
            "hi_max": era["hi"].resample("D").max(),
            "t_media": era["t2m"].resample("D").mean(),
            "hr_media": era["hr"].resample("D").mean(),
            "rad_media": era["rad"].resample("D").mean(),
            "n_horas": era["hi"].resample("D").count(),
        })
        dia = dia[dia["n_horas"] == 24]
        dia.to_parquet(PROC / "clima_diario.parquet")
        ide = leer_ideam()
        ide.to_parquet(PROC / "ideam_horario.parquet")
        tabla, desfases, j = contraste(era, ide)
        tabla.to_csv(SALIDAS / "contraste_era5land_ideam.csv", index=False, float_format="%.3f")
        print(tabla[tabla["agrupacion"] == "total"].to_string(index=False))
        print("RMSE de T según desfase de IDEAM (h):", {k: round(v, 3) for k, v in desfases.items()})
        # El índice diario que entra a la regresión, con ERA5-Land y con IDEAM (prueba de robustez)
        hi_ide = ide["hi_ideam"].resample("D").agg(["mean", "count"])
        dia_ide = hi_ide[hi_ide["count"] >= 20]["mean"].rename("hi_media_ideam")
        dia_ide.to_frame().to_parquet(PROC / "ideam_diario.parquet")
        jj = dia.join(dia_ide, how="inner")
        print(f"Correlación del HI diario ERA5-Land vs IDEAM: {jj['hi_media'].corr(jj['hi_media_ideam']):.3f} "
              f"(n = {len(jj)} días); sesgo medio {(jj['hi_media'] - jj['hi_media_ideam']).mean():.2f} °C")


if __name__ == "__main__":
    main()
