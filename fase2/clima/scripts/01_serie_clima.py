"""Fase 2, Paso 1: serie horaria de clima y calendario para el modelo de simulación (5R1C).

Parte de ERA5-Land de GDEX (NCAR) en la celda de Barranquilla (11,0 N; 74,8 O), extraído por
compuerta_horaria/scripts/01b_extraer_era5land_gdex.py, de enero de 2015 a septiembre de 2026.

Cada fila es la hora que termina en `hora_local` (UTC−5), la convención de ERA5 para las variables acumuladas y la
de los archivos EPW. Las instantáneas (temperatura, punto de rocío, presión y viento) son las del final de la hora.

Pasos:
  1. Huecos: el punto de rocío falta en 608 horas sueltas de 2019, 2022 y 2023 y se rellena con la copia de
     Open-Meteo, que es el mismo ERA5-Land desplazado por una constante (+0,175 K; desviación estándar 0,03 K). La
     presión falta en 8 horas de 2026 y se interpola en el tiempo.
  2. Humedad: humedad relativa (Magnus), humedad específica con la presión horaria e índice de calor (Rothfusz,
     NOAA), con las mismas funciones de la compuerta horaria.
  3. Radiación: posición del sol a mitad de la hora (NREL SPA en pvlib), separación de la irradiancia horizontal en
     directa normal y difusa con el modelo de Erbs y proyección en muros verticales al norte, sur, este y oeste con
     cielo isótropo y albedo de 0,2. La cubierta horizontal recibe la irradiancia global horizontal.
  4. Cielo: temperatura del cielo a partir de la onda larga descendente de ERA5-Land, T_cielo = (L/σ)^¼, y su
     diferencia con el aire, que reemplaza en la Fase 2 los 11 K por defecto de la ISO 13790 y los 3,9 K del Paso 3.
  5. Calendario: tipo de día, festivos, Carnaval, Semana Santa, fin de año y vacaciones escolares aproximadas
     (supuesto declarado, ver `vacaciones_escolares`). 2020 queda marcado; la calibración lo excluye.

Uso:  python scripts/01_serie_clima.py
Salidas (salidas/):
  clima_horario_barranquilla.parquet y .csv.gz   serie horaria
  comprobaciones_clima.json                       cierre de la radiación, cielo despejado, mediodía solar y huecos
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pvlib

RAIZ = Path(__file__).resolve().parents[1]
BASE = RAIZ.parents[1]
# Scripts de la compuerta horaria: compuerta_horaria/scripts en la carpeta de trabajo, scripts/compuerta en el repositorio
COMPUERTA = next(p for p in (BASE / "compuerta_horaria" / "scripts", BASE / "scripts" / "compuerta") if p.exists())
sys.path.insert(0, str(COMPUERTA))
from comun import CRUDOS, calendario, humedad_relativa, indice_calor  # noqa: E402

GDEX = CRUDOS / "era5land_gdex" / "era5land_horario_11.0N_74.8W.csv.gz"
OPENMETEO = CRUDOS / "openmeteo"
SALIDAS = RAIZ / "salidas"

LAT, LON, ALTURA = 11.0, -74.8, 50.0  # centro de la celda; altura del modelo de terreno que reporta Open-Meteo
ALBEDO = 0.2
SIGMA = 5.670374419e-8
MUROS = {"N": 0.0, "E": 90.0, "S": 180.0, "O": 270.0}


def punto_rocio_openmeteo(indice_utc):
    partes = []
    for f in sorted(OPENMETEO.glob("om_*.json")):
        h = json.loads(f.read_text(encoding="utf-8"))["hourly"]
        partes.append(pd.Series(h["dew_point_2m_era5_land"], index=pd.to_datetime(h["time"])))
    s = pd.concat(partes)
    return s[~s.index.duplicated()].reindex(indice_utc)


def vacaciones_escolares(fechas):
    """Receso escolar aproximado del calendario A de Colombia (supuesto, no las resoluciones de cada año).

    Fin de año: del 1 de diciembre al 25 de enero. Semana Santa: de lunes a sábado. Mitad de año: tres semanas desde el
    lunes siguiente al 15 de junio. Octubre: la semana del festivo del Día de la Raza (lunes).
    """
    f = pd.DatetimeIndex(fechas).normalize()
    v = (f.month == 12) | ((f.month == 1) & (f.day <= 25))
    for a in range(f.year.min(), f.year.max() + 1):
        junio = pd.Timestamp(a, 6, 16)
        inicio = junio + pd.Timedelta(days=(7 - junio.dayofweek) % 7)
        v |= (f >= inicio) & (f < inicio + pd.Timedelta(days=21))
        octubre = pd.Timestamp(a, 10, 12)
        lunes = octubre + pd.Timedelta(days=(7 - octubre.dayofweek) % 7)
        v |= (f >= lunes) & (f < lunes + pd.Timedelta(days=5))
    return v


def main():
    g = pd.read_csv(GDEX, index_col="tiempo_utc", parse_dates=True)
    comp = {}

    # 1. Huecos
    hueco_td = g["Td"].isna()
    om = punto_rocio_openmeteo(g.index)
    dif = (g["Td"] - om).median()
    g["td_relleno"] = hueco_td & om.notna()
    g.loc[g["td_relleno"], "Td"] = om[g["td_relleno"]] + dif
    g["p_interpolada"] = g["p_kPa"].isna()
    g["p_kPa"] = g["p_kPa"].interpolate(limit_direction="both")
    comp["huecos"] = {"punto_rocio_rellenado_h": int(g["td_relleno"].sum()), "desfase_openmeteo_K": float(dif),
                      "punto_rocio_sin_dato_h": int(g["Td"].isna().sum()),
                      "presion_interpolada_h": int(g["p_interpolada"].sum())}

    # 2. Humedad
    hr = humedad_relativa(g["T"], g["Td"])
    pv = 0.61094 * np.exp(17.625 * g["Td"] / (g["Td"] + 243.04))  # kPa
    w = 0.622 * pv / (g["p_kPa"] - pv)

    # 3. Radiación: sol a mitad de la hora que termina en t
    medio = g.index.tz_localize("UTC") - pd.Timedelta(minutes=30)
    sol = pvlib.solarposition.get_solarposition(medio, LAT, LON, altitude=ALTURA)
    z = sol["zenith"].to_numpy()
    ghi = g["I"].to_numpy()
    sep = pvlib.irradiance.erbs(ghi, z, medio)
    dni = np.nan_to_num(np.asarray(sep["dni"]))
    dhi = np.nan_to_num(np.asarray(sep["dhi"]))
    etr_n = np.asarray(pvlib.irradiance.get_extra_radiation(medio))
    etr_h = np.clip(etr_n * np.cos(np.radians(z)), 0, None)
    muros = {}
    for nombre, az in MUROS.items():
        poa = pvlib.irradiance.get_total_irradiance(90.0, az, z, sol["azimuth"].to_numpy(), dni, ghi, dhi,
                                                    albedo=ALBEDO, model="isotropic")
        muros[f"I_muro_{nombre}"] = np.clip(np.nan_to_num(np.asarray(poa["poa_global"])), 0, None)

    # 4. Cielo
    t_cielo = (g["L"] / SIGMA) ** 0.25 - 273.15

    hora_local = (g.index.tz_localize("UTC").tz_convert("America/Bogota").tz_localize(None)).rename("hora_local")
    s = pd.DataFrame({
        "T": g["T"].to_numpy(), "Td": g["Td"].to_numpy(), "HR": np.asarray(hr), "w_kgkg": w.to_numpy(),
        "p_kPa": g["p_kPa"].to_numpy(), "HI": np.asarray(indice_calor(g["T"], hr)),
        "GHI": ghi, "DNI": dni, "DHI": dhi, "ETR_horizontal": etr_h, "ETR_normal": etr_n,
        "cenit_sol": z, "azimut_sol": sol["azimuth"].to_numpy(), "I_cubierta": ghi, **muros,
        "L_onda_larga": g["L"].to_numpy(), "T_cielo": t_cielo.to_numpy(), "dT_cielo": (g["T"] - t_cielo).to_numpy(),
        "viento": g["viento"].to_numpy(), "dir_viento": (np.degrees(np.arctan2(-g["u10"], -g["v10"])) % 360).to_numpy(),
        "lluvia_mm": g["lluvia_mm"].to_numpy(), "td_relleno": g["td_relleno"].to_numpy(),
        "p_interpolada": g["p_interpolada"].to_numpy(),
    }, index=hora_local)

    # 5. Calendario (por fecha local de la hora; la hora 24 = 00:00 del día siguiente pertenece al día anterior)
    fecha = (s.index - pd.Timedelta(seconds=1)).normalize()
    cal = calendario(fecha.unique())
    cal["vacaciones_escolares"] = vacaciones_escolares(cal.index)
    cal = cal.reindex(fecha)
    for c in ["tipo_dia", "festivo", "carnaval", "semana_santa", "fin_anio", "vacaciones_escolares"]:
        s[c] = cal[c].to_numpy()
    s["anio_pandemia"] = fecha.year == 2020

    # Comprobaciones
    dia = s["cenit_sol"] < 85
    cierre = s["DNI"] * np.cos(np.radians(s["cenit_sol"])) + s["DHI"] - s["GHI"]
    loc = pvlib.location.Location(LAT, LON, altitude=ALTURA)
    cs = loc.get_clearsky(medio, model="ineichen")["ghi"].to_numpy()
    # Con el sol bajo, el cielo despejado calculado a mitad de la hora subestima la hora completa; se compara solo
    # donde el cielo despejado supera 300 W/m²
    razon = np.where(cs > 300, s["GHI"] / np.where(cs > 300, cs, 1), np.nan)
    media_hora = s["GHI"].groupby(s.index.hour).mean()
    comp["radiacion"] = {
        "cierre_max_abs_Wm2_sol_alto": float(cierre[dia].abs().max()),
        "frac_horas_GHI_sobre_1.1_cielo_despejado_cs300": float(np.nanmean(razon[~np.isnan(razon)] > 1.1)),
        "razon_GHI_cielo_despejado_p99_cs300": float(np.nanpercentile(razon, 99)),
        "hora_local_de_mayor_GHI_media": int(media_hora.idxmax()),
        "simetria_GHI_media_horas_12_13_y_7_18": [round(float(media_hora[h]), 1) for h in (12, 13, 7, 18)],
        "GHI_media_Wm2": float(s["GHI"].mean()),
        "irradiancia_media_muros_Wm2": {k: float(s[f"I_muro_{k}"].mean()) for k in MUROS},
        "frac_difusa_diurna": float(s.loc[dia, "DHI"].sum() / s.loc[dia, "GHI"].sum()),
        "horas_GHI_positiva_con_sol_bajo_horizonte": int(((s["GHI"] > 5) & (s["cenit_sol"] > 90)).sum()),
    }
    comp["cielo"] = {"T_cielo_media": float(s["T_cielo"].mean()), "dT_cielo_media": float(s["dT_cielo"].mean()),
                     "dT_cielo_noche_media": float(s.loc[~dia, "dT_cielo"].mean()),
                     "dT_cielo_p5_p95": [float(s["dT_cielo"].quantile(.05)), float(s["dT_cielo"].quantile(.95))]}
    comp["periodo"] = [str(s.index.min()), str(s.index.max()), int(len(s))]
    comp["horas_completas"] = bool(len(pd.date_range(s.index.min(), s.index.max(), freq="h")) == len(s))

    SALIDAS.mkdir(parents=True, exist_ok=True)
    s.to_parquet(SALIDAS / "clima_horario_barranquilla.parquet")
    s.round(4).to_csv(SALIDAS / "clima_horario_barranquilla.csv.gz")
    (SALIDAS / "comprobaciones_clima.json").write_text(json.dumps(comp, indent=2, ensure_ascii=False),
                                                       encoding="utf-8")
    print(json.dumps(comp, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
