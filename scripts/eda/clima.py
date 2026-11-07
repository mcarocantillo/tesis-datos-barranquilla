"""EDA del clima horario de Barranquilla: ERA5-Land de GDEX (fuente principal), copia de Open-Meteo e IDEAM 0029045190.

Lee (solo lectura):
  fase2/clima/salidas/clima_horario_barranquilla.parquet          serie procesada de la Fase 2 (hora local)
  compuerta_horaria/datos/crudos/era5land_gdex/era5land_horario_11.0N_74.8W.csv.gz   celda de GDEX en UTC
  compuerta_horaria/datos/crudos/openmeteo/om_*.json               copia de ERA5-Land de Open-Meteo (UTC)
  compuerta_horaria/datos/crudos/ideam/temperatura.csv, humedad.csv   estación 0029045190 (hora local)

Escribe figuras/eda/clima_*.png y tablas/eda/clima_*.csv (solo agregados).

Convenciones: cada fila de la serie es la hora que termina en `hora_local` (UTC−5). Las variables instantáneas
(T, Td, HR, HI, viento) son las del final de la hora; las acumuladas (GHI, onda larga, lluvia) son el total o la
media de la hora que termina ahí. La noche es de 22 a 5 h, como en la compuerta horaria.

Uso:  python scripts/eda/clima.py   (desde la raíz del repositorio)
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from estilo import *  # noqa: E402,F401,F403

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

np.random.seed(SEMILLA)

SERIE = ML / "fase2" / "clima" / "salidas" / "clima_horario_barranquilla.parquet"
CRUDOS = ML / "compuerta_horaria" / "datos" / "crudos"
GDEX = CRUDOS / "era5land_gdex" / "era5land_horario_11.0N_74.8W.csv.gz"
OM = CRUDOS / "openmeteo"
IDEAM = CRUDOS / "ideam"
FUENTE = "Fuente: ERA5-Land (GDEX, NCAR), celda 11,0 N; 74,8 O; serie de la Fase 2. Cálculos propios."
NOCHE = [22, 23, 0, 1, 2, 3, 4, 5]
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
SECA = [12, 1, 2, 3, 4]  # temporada seca del Caribe colombiano (diciembre a abril)


# ---------------------------------------------------------------- funciones de humedad (las de la compuerta)
def humedad_relativa(t_c, td_c):
    def es(x):
        return 6.1094 * np.exp(17.625 * x / (x + 243.04))
    return np.clip(100 * es(td_c) / es(t_c), 0, 100)


def indice_calor(t_c, hr):
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


# ---------------------------------------------------------------- lectura
def leer_openmeteo():
    partes = []
    for f in sorted(OM.glob("om_*.json")):
        h = json.loads(f.read_text(encoding="utf-8"))["hourly"]
        d = pd.DataFrame(h)
        d["time"] = pd.to_datetime(d["time"])
        partes.append(d.set_index("time"))
    o = pd.concat(partes)
    return o[~o.index.duplicated()].apply(pd.to_numeric, errors="coerce")


def leer_ideam():
    """Igual que compuerta_horaria/scripts/01_clima.py: hora en punto, límites físicos y media de la hora."""
    series, crudos = {}, {}
    for var, col, lim in [("temperatura", "t_ideam", (15, 45)), ("humedad", "hr_ideam", (5, 100))]:
        d = pd.read_csv(IDEAM / f"{var}.csv")
        d["hora_local"] = pd.to_datetime(d["fechaobservacion"]).dt.floor("h")
        d["v"] = pd.to_numeric(d["valorobservado"], errors="coerce")
        crudos[col] = (len(d), int((~d["v"].between(*lim)).sum()))
        d = d[d["v"].between(*lim)]
        series[col] = d.groupby("hora_local")["v"].mean()
    df = pd.DataFrame(series)
    df["hi_ideam"] = indice_calor(df["t_ideam"], df["hr_ideam"])
    return df, crudos


def utc_a_local(idx):
    return idx.tz_localize("UTC").tz_convert("America/Bogota").tz_localize(None)


# ---------------------------------------------------------------- figuras y tablas
def cobertura(s, g, ide, crudos):
    filas = []
    n = len(s)
    for col, var, unidad in [("T", "T", "°C"), ("Td", "Td", "°C"), ("p_kPa", "p_kPa", "kPa"), ("I", "GHI", "W/m²"),
                             ("L", "L_onda_larga", "W/m²"), ("viento", "viento", "m/s"),
                             ("lluvia_mm", "lluvia_mm", "mm")]:
        faltan = int(g[col].isna().sum())
        trat = {"Td": "relleno con Open-Meteo + 0,175 K", "p_kPa": "interpolada en el tiempo",
                "lluvia_mm": "sin tratar (quedan vacías)"}.get(col, "")
        filas.append({"fuente": "ERA5-Land GDEX", "variable": var, "unidad": unidad, "horas": n,
                      "faltantes_crudo": faltan, "faltantes_serie": int(s[var].isna().sum()), "tratamiento": trat})
    ini, fin = s.index.min(), s.index.max()
    total = int((fin - ini) / pd.Timedelta("1h")) + 1
    for col, nombre in [("t_ideam", "T IDEAM"), ("hr_ideam", "HR IDEAM"), ("hi_ideam", "HI IDEAM")]:
        x = ide.loc[ini:fin, col].dropna()
        filas.append({"fuente": "IDEAM 0029045190", "variable": nombre, "unidad": "", "horas": len(x),
                      "faltantes_crudo": total - len(x), "faltantes_serie": total - len(x),
                      "tratamiento": "registros fuera de rango descartados: "
                                     + (str(crudos[col][1]) if col in crudos else "-")})
    t = pd.DataFrame(filas)
    tabla(t, "clima_cobertura.csv", index=False)

    # Horas por año: IDEAM (T y HR) y huecos de GDEX
    anio = ide.loc["2015":"2025"]
    por_anio = pd.DataFrame({"T IDEAM": anio["t_ideam"].notna().groupby(anio.index.year).sum(),
                             "HR IDEAM": anio["hr_ideam"].notna().groupby(anio.index.year).sum()})
    huecos = pd.DataFrame({"Td rellenado (GDEX)": s["td_relleno"].groupby(s.index.year).sum(),
                           "Lluvia vacía (GDEX)": s["lluvia_mm"].isna().groupby(s.index.year).sum()}).loc[2015:2025]
    tabla(por_anio.join(huecos).rename_axis("anio"), "clima_cobertura_anual.csv")

    fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4.6), gridspec_kw={"width_ratios": [1.4, 1]})
    x = np.arange(len(por_anio))
    a.bar(x - .2, por_anio["T IDEAM"], .4, color=PAL[0], label="Temperatura")
    a.bar(x + .2, por_anio["HR IDEAM"], .4, color=PAL[2], label="Humedad relativa")
    horas_anio = pd.Series([8784 if y % 4 == 0 else 8760 for y in por_anio.index])
    a.plot(x, horas_anio, color=TXT2, ls="--", lw=1, label="Horas del año (ERA5-Land completo)")
    a.set_xticks(x, por_anio.index, rotation=45)
    a.set_ylabel("Horas con dato")
    a.set_ylim(0, 11000)
    a.legend(loc="upper center", fontsize=8.5, ncol=3)
    titulo(a, "(a) Estación IDEAM 0029045190", "Horas con dato por año")
    x2 = np.arange(len(huecos))
    b.bar(x2 - .2, huecos.iloc[:, 0], .4, color=PAL[1], label="Td rellenado con Open-Meteo")
    b.bar(x2 + .2, huecos.iloc[:, 1], .4, color=PAL[6], label="Lluvia vacía")
    b.set_xticks(x2, huecos.index, rotation=45)
    b.set_ylabel("Horas")
    b.legend(fontsize=9)
    titulo(b, "(b) Huecos de ERA5-Land de GDEX", "Horas por año")
    guardar(fig, "clima_cobertura.png", "Fuente: ERA5-Land (GDEX); IDEAM (datos.gov.co, recursos sbwg-7ju4 y uext-mhny).")
    return t, por_anio, huecos


def resumen(s):
    vars_ = {"T": "°C", "Td": "°C", "HR": "%", "w_kgkg": "kg/kg", "p_kPa": "kPa", "HI": "°C", "GHI": "W/m²",
             "DNI": "W/m²", "DHI": "W/m²", "I_muro_N": "W/m²", "I_muro_E": "W/m²", "I_muro_S": "W/m²",
             "I_muro_O": "W/m²", "L_onda_larga": "W/m²", "T_cielo": "°C", "dT_cielo": "K", "viento": "m/s",
             "lluvia_mm": "mm/h"}
    filas = []
    for v, u in vars_.items():
        x = s[v].dropna()
        filas.append({"variable": v, "unidad": u, "n": len(x), "media": x.mean(), "de": x.std(), "min": x.min(),
                      "p5": x.quantile(.05), "p50": x.median(), "p95": x.quantile(.95), "max": x.max()})
    t = pd.DataFrame(filas).round(4)
    tabla(t, "clima_resumen.csv", index=False)
    return t


def climatologia(s):
    d = s.loc["2015":"2025"]
    g = d.groupby(d.index.month)
    m = pd.DataFrame({v: g[v].mean() for v in ["T", "HR", "HI", "GHI", "viento"]})
    for v in ["T", "HI"]:
        dia = d[v].resample("D")
        m[f"{v}_max_diaria"] = dia.max().groupby(dia.max().index.month).mean()
        m[f"{v}_min_diaria"] = dia.min().groupby(dia.min().index.month).mean()
    lluvia = d["lluvia_mm"].resample("MS").sum(min_count=1)
    m["lluvia_mm_mes"] = lluvia.groupby(lluvia.index.month).mean()
    m.index.name = "mes"
    tabla(m.round(3), "clima_climatologia_mensual.csv")

    fig, ejes = plt.subplots(2, 2, figsize=(12, 7.5))
    x = np.arange(1, 13)
    for ax, v, u, c, tt in [(ejes[0, 0], "T", "°C", PAL[1], "(a) Temperatura"),
                            (ejes[0, 1], "HR", "%", PAL[0], "(b) Humedad relativa"),
                            (ejes[1, 0], "HI", "°C", PAL[7], "(c) Índice de calor"),
                            (ejes[1, 1], "GHI", "W/m²", PAL[3], "(d) Irradiancia global horizontal")]:
        p10 = g[v].quantile(.10)
        p90 = g[v].quantile(.90)
        ax.fill_between(x, p10, p90, color=c, alpha=.18, lw=0, label="Percentiles 10–90 horarios")
        ax.plot(x, m[v], color=c, lw=2.2, marker="o", label="Media")
        if v in ("T", "HI"):
            ax.plot(x, m[f"{v}_max_diaria"], color=c, lw=1, ls="--", label="Máxima diaria media")
            ax.plot(x, m[f"{v}_min_diaria"], color=c, lw=1, ls=":", label="Mínima diaria media")
        ax.set_xticks(x, MESES)
        ax.set_ylabel(u)
        titulo(ax, tt)
        ax.legend(fontsize=8.5, loc="best")
    guardar(fig, "clima_climatologia.png", FUENTE + " 2015–2025.")
    return m


def perfil_horario(s):
    d = s.loc["2015":"2025"]
    temporada = np.where(d.index.month.isin(SECA), "seca", "lluviosa")
    t = d[["T", "HR", "HI", "GHI"]].groupby([temporada, d.index.hour]).mean()
    t.index.names = ["temporada", "hora"]
    todo = d[["T", "HR", "HI", "GHI"]].groupby(d.index.hour).mean()
    todo.index = pd.MultiIndex.from_product([["todo"], todo.index], names=["temporada", "hora"])
    t = pd.concat([todo, t])
    tabla(t.round(3), "clima_perfil_horario.csv")

    fig, ejes = plt.subplots(2, 2, figsize=(12, 7.5))
    for ax, v, u, tt in [(ejes[0, 0], "T", "°C", "(a) Temperatura"), (ejes[0, 1], "HR", "%", "(b) Humedad relativa"),
                         (ejes[1, 0], "HI", "°C", "(c) Índice de calor"),
                         (ejes[1, 1], "GHI", "W/m²", "(d) Irradiancia global horizontal")]:
        for tem, c, nom in [("seca", PAL[1], "Seca (dic–abr)"), ("lluviosa", PAL[0], "Lluviosa (may–nov)")]:
            ax.plot(range(24), t.loc[tem, v], color=c, lw=2, marker=".", label=nom)
        ax.plot(range(24), t.loc["todo", v], color=TXT2, lw=1, ls="--", label="Todo el año")
        ax.axvspan(-0.5, 5.5, color=GRID, alpha=.6, lw=0)
        ax.axvspan(21.5, 23.5, color=GRID, alpha=.6, lw=0)
        ax.set_xticks(range(0, 24, 3))
        ax.set_xlim(-.5, 23.5)
        ax.set_xlabel("Hora local")
        ax.set_ylabel(u)
        titulo(ax, tt)
    ejes[0, 0].legend(fontsize=9)
    guardar(fig, "clima_perfil_horario.png", FUENTE + " 2015–2025. Sombreado: noche (22 a 5 h).")
    return t


def distribucion_hi(s):
    d = s.loc["2015":"2025"]
    cortes = [-np.inf, 27, 32, 41, np.inf]
    nombres = ["< 27 °C", "27–32 °C (precaución)", "32–41 °C (precaución extrema)", "≥ 41 °C (peligro)"]
    cat = pd.cut(d["HI"], cortes, labels=nombres, right=False)
    hora = d.index.hour
    filas = []
    for nombre, sel in [("todas", slice(None)), ("noche (22 a 5 h)", np.isin(hora, NOCHE)),
                        ("tarde (12 a 17 h)", (hora >= 12) & (hora <= 17))]:
        c = cat[sel].value_counts(normalize=True).reindex(nombres) * 100
        filas.append({"horas": nombre, **c.round(2).to_dict(), "HI_medio": d["HI"][sel].mean(),
                      "HI_p95": d["HI"][sel].quantile(.95)})
    t = pd.DataFrame(filas)
    hi_d = d["HI"].resample("D").mean()
    t2 = pd.DataFrame([{"horas": "media diaria", "HI_medio": hi_d.mean(), "HI_p95": hi_d.quantile(.95),
                        **{n: np.nan for n in nombres}}])
    t = pd.concat([t, t2], ignore_index=True)
    tabla(t.round(3), "clima_hi_categorias.csv", index=False)

    fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4.6))
    bins = np.arange(22, 43, .5)
    a.hist(d["HI"], bins=bins, color=PAL[7], alpha=.85)
    for v in (27, 32, 41):
        a.axvline(v, color=TXT2, lw=1, ls="--")
    a.set_xlabel("Índice de calor horario (°C)")
    a.set_ylabel("Horas")
    titulo(a, "(a) Índice de calor horario", "Líneas: umbrales de la NOAA (27, 32 y 41 °C)")
    b.hist(hi_d, bins=np.arange(25, 36, .25), color=PAL[1], alpha=.85, label="Media diaria")
    b.hist(d["HI"].resample("D").max(), bins=np.arange(25, 43, .25), color=PAL[7], alpha=.45, label="Máxima diaria")
    b.set_xlabel("Índice de calor diario (°C)")
    b.set_ylabel("Días")
    b.legend(fontsize=9)
    titulo(b, "(b) Índice de calor diario", "Media y máxima de cada día")
    guardar(fig, "clima_hi_distribucion.png", FUENTE + " 2015–2025.")
    return t


def tendencia(s):
    d = s.loc["2015":"2025"]
    g = d.groupby(d.index.year)
    a = pd.DataFrame({"T": g["T"].mean(), "HI": g["HI"].mean(), "HR": g["HR"].mean(), "GHI": g["GHI"].mean(),
                      "lluvia_mm": g["lluvia_mm"].sum(min_count=1), "horas_lluvia_vacias": g["lluvia_mm"].apply(
                          lambda x: int(x.isna().sum())),
                      "CDH_26.5": g["HI"].apply(lambda x: (x - 26.5).clip(lower=0).sum())})
    a.index.name = "anio"
    pend = {}
    x = a.index.to_numpy(dtype=float)
    for v in ["T", "HI", "HR", "GHI", "CDH_26.5"]:
        b = np.polyfit(x, a[v], 1)
        pend[v] = b[0] * 10
    a.loc["pendiente_por_decada"] = pd.Series(pend)
    tabla(a.round(3), "clima_tendencia_anual.csv")
    a = a.drop("pendiente_por_decada")

    fig, (ax, bx) = plt.subplots(1, 2, figsize=(12, 4.6))
    for v, c, nom in [("T", PAL[1], "Temperatura"), ("HI", PAL[7], "Índice de calor")]:
        ax.plot(a.index, a[v], color=c, marker="o", lw=2, label=f"{nom} ({fmt(pend[v], 2)} °C por década)")
        b = np.polyfit(x, a[v], 1)
        ax.plot(a.index, np.polyval(b, x), color=c, lw=1, ls="--")
    ax.set_ylabel("°C")
    ax.legend(fontsize=9)
    titulo(ax, "(a) Media anual", "Recta de mínimos cuadrados, 2015–2025")
    bx.bar(a.index, a["lluvia_mm"], color=PAL[0])
    bx.set_ylabel("mm/año")
    titulo(bx, "(b) Lluvia anual", "2019 y 2022 con horas vacías (ver texto)")
    guardar(fig, "clima_tendencia.png", FUENTE)
    return a, pend


def contraste(s, g, om, ide):
    # GDEX frente a Open-Meteo (ambas en UTC; la serie de Open-Meteo trae ERA5-Land para T y Td y ERA5 para el resto)
    j = g.join(om, how="inner")
    filas = []
    for a, b, nom in [("T", "temperature_2m_era5_land", "T: GDEX − Open-Meteo (ERA5-Land)"),
                      ("Td", "dew_point_2m_era5_land", "Td: GDEX − Open-Meteo (ERA5-Land)"),
                      ("I", "shortwave_radiation_era5", "GHI: GDEX (ERA5-Land) − Open-Meteo (ERA5)"),
                      ("viento", "wind_speed_10m_era5", "Viento: GDEX (ERA5-Land) − Open-Meteo (ERA5)")]:
        e = (j[a] - j[b]).dropna()
        filas.append({"comparacion": nom, "horas": len(e), "media_A": j.loc[e.index, a].mean(),
                      "media_B": j.loc[e.index, b].mean(), "sesgo": e.mean(), "de_diferencia": e.std(),
                      "rmse": np.sqrt((e ** 2).mean()), "correlacion": j[a].corr(j[b])})
    # ERA5-Land (GDEX y Open-Meteo) frente a IDEAM, hora local
    oml = om.copy()
    oml.index = utc_a_local(oml.index)
    oml["hr"] = humedad_relativa(oml["temperature_2m_era5_land"], oml["dew_point_2m_era5_land"])
    oml["hi"] = indice_calor(oml["temperature_2m_era5_land"], oml["hr"])
    fuentes = {"GDEX": s[["T", "HR", "HI"]].rename(columns={"T": "t", "HR": "hr", "HI": "hi"}),
               "Open-Meteo": oml[["temperature_2m_era5_land", "hr", "hi"]].rename(
                   columns={"temperature_2m_era5_land": "t"})}
    por_hora, por_mes, jj = [], [], {}
    for fnom, f in fuentes.items():
        k = f.join(ide, how="inner").dropna()
        jj[fnom] = k
        for v, (a, b) in {"T": ("t", "t_ideam"), "HR": ("hr", "hr_ideam"), "HI": ("hi", "hi_ideam")}.items():
            e = k[a] - k[b]
            dia_a, dia_b = k[a].resample("D").mean(), k[b].resample("D").mean()
            filas.append({"comparacion": f"{v}: {fnom} − IDEAM", "horas": len(e), "media_A": k[a].mean(),
                          "media_B": k[b].mean(), "sesgo": e.mean(), "de_diferencia": e.std(),
                          "rmse": np.sqrt((e ** 2).mean()), "correlacion": k[a].corr(k[b]),
                          "sesgo_noche": e[np.isin(k.index.hour, NOCHE)].mean(),
                          "sesgo_11_17": e[(k.index.hour >= 11) & (k.index.hour <= 17)].mean(),
                          "corr_media_diaria": dia_a.corr(dia_b)})
            ph = e.groupby(k.index.hour).agg(["mean", "size"]).rename(columns={"mean": "sesgo", "size": "n"})
            ph["rmse"] = e.groupby(k.index.hour).apply(lambda x: np.sqrt((x ** 2).mean()))
            ph["fuente"], ph["variable"] = fnom, v
            por_hora.append(ph.rename_axis("hora").reset_index())
            pm = e.groupby(k.index.month).agg(["mean", "size"]).rename(columns={"mean": "sesgo", "size": "n"})
            pm["fuente"], pm["variable"] = fnom, v
            por_mes.append(pm.rename_axis("mes").reset_index())
    t = pd.DataFrame(filas)
    tabla(t.round(4), "clima_contraste_fuentes.csv", index=False)
    ph = pd.concat(por_hora)
    pm = pd.concat(por_mes)
    tabla(ph.round(4), "clima_contraste_hora.csv", index=False)
    tabla(pm.round(4), "clima_contraste_mes.csv", index=False)

    fig, ejes = plt.subplots(1, 3, figsize=(15, 4.8))
    a, b, c = ejes
    for (fnom, v), col, ls in [(("GDEX", "T"), PAL[1], "-"), (("Open-Meteo", "T"), PAL[1], ":"),
                               (("GDEX", "HI"), PAL[7], "-"), (("Open-Meteo", "HI"), PAL[7], ":")]:
        x = ph[(ph.fuente == fnom) & (ph.variable == v)]
        a.plot(x["hora"], x["sesgo"], color=col, ls=ls, lw=2, marker="." if ls == "-" else None,
               label=f"{v}, {fnom}")
    a.axhline(0, color=TXT2, lw=.8)
    a.axvspan(-0.5, 5.5, color=GRID, alpha=.6, lw=0)
    a.axvspan(21.5, 23.5, color=GRID, alpha=.6, lw=0)
    a.set_xticks(range(0, 24, 3))
    a.set_xlabel("Hora local")
    a.set_ylabel("ERA5-Land − IDEAM (°C)")
    a.legend(fontsize=8.5)
    titulo(a, "(a) Sesgo por hora", "Frente a la estación 0029045190")
    for v, col in [("T", PAL[1]), ("HI", PAL[7]), ("HR", PAL[0])]:
        x = pm[(pm.fuente == "GDEX") & (pm.variable == v)]
        b.plot(x["mes"], x["sesgo"], color=col, lw=2, marker="o", label=f"{v} ({'puntos' if v == 'HR' else '°C'})")
    b.axhline(0, color=TXT2, lw=.8)
    b.set_xticks(range(1, 13), MESES, rotation=45)
    b.set_ylabel("GDEX − IDEAM")
    b.legend(fontsize=8.5)
    titulo(b, "(b) Sesgo por mes, GDEX", "Media de todas las horas")
    dT = (j["T"] - j["temperature_2m_era5_land"]).dropna()
    c.hist(dT, bins=np.arange(0.10, 0.25, 0.0025), color=PAL[2])
    c.axvline(dT.median(), color=TXT2, ls="--", lw=1)
    c.set_xlabel("T de GDEX − T de Open-Meteo (K)")
    c.set_ylabel("Horas")
    titulo(c, "(c) GDEX frente a Open-Meteo", f"Mediana {fmt(dT.median(), 3)} K; desv. est. {fmt(dT.std(), 3)} K")
    guardar(fig, "clima_contraste.png",
            "Fuente: ERA5-Land de GDEX y de Open-Meteo; IDEAM 0029045190. Sombreado: noche (22 a 5 h).")
    return t, ph, pm


def viento_lluvia(s):
    d = s.loc["2015":"2025"]
    sectores = ["N", "NE", "E", "SE", "S", "SO", "O", "NO"]
    sec = pd.cut((d["dir_viento"] + 22.5) % 360, np.arange(0, 361, 45), labels=sectores, right=False)
    frec = sec.value_counts(normalize=True).reindex(sectores) * 100
    vel = d["viento"].groupby(sec, observed=False).mean().reindex(sectores)
    temporada = np.where(d.index.month.isin(SECA), "seca", "lluviosa")
    vt = d["viento"].groupby(temporada).mean()
    mes_v = d["viento"].groupby(d.index.month).mean()
    lluvia_m = d["lluvia_mm"].resample("MS").sum(min_count=1)
    mes_ll = lluvia_m.groupby(lluvia_m.index.month).mean()
    horas_lluvia = (d["lluvia_mm"] >= 0.1).groupby(d.index.month).mean() * 100
    t = pd.DataFrame({"viento_m_s": mes_v, "lluvia_mm_mes": mes_ll, "pct_horas_lluvia_0.1mm": horas_lluvia})
    t.index.name = "mes"
    tabla(t.round(3), "clima_viento_lluvia_mensual.csv")
    tabla(pd.DataFrame({"frecuencia_pct": frec, "velocidad_media": vel}).rename_axis("sector").round(3),
          "clima_viento_direccion.csv")

    fig = plt.figure(figsize=(14, 4.8))
    a = fig.add_subplot(1, 3, 1, projection="polar")
    ang = np.radians(np.arange(0, 360, 45))
    a.bar(ang, frec.to_numpy(), width=np.radians(40), color=PAL[0], alpha=.85)
    a.set_theta_zero_location("N")
    a.set_theta_direction(-1)
    a.set_xticks(ang, sectores)
    a.set_title("(a) Dirección de origen (% de horas)", fontweight="bold", fontsize=12, pad=24, loc="center")
    b = fig.add_subplot(1, 3, 2)
    b.plot(range(1, 13), mes_v, color=PAL[0], lw=2, marker="o")
    b.set_xticks(range(1, 13), MESES, rotation=45)
    b.set_ylabel("m/s")
    titulo(b, "(b) Viento medio a 10 m", f"Seca {fmt(vt['seca'])} m/s; lluviosa {fmt(vt['lluviosa'])} m/s")
    c = fig.add_subplot(1, 3, 3)
    c.bar(range(1, 13), mes_ll, color=PAL[2])
    c.set_xticks(range(1, 13), MESES, rotation=45)
    c.set_ylabel("mm/mes")
    titulo(c, "(c) Lluvia media mensual", "2015–2025")
    guardar(fig, "clima_viento_lluvia.png", FUENTE + " 2015–2025.")
    return frec, vel, vt, t


def muros(s):
    d = s.loc["2015":"2025"]
    cols = {"I_cubierta": "Cubierta", "I_muro_N": "Muro N", "I_muro_E": "Muro E", "I_muro_S": "Muro S",
            "I_muro_O": "Muro O"}
    ph = d[list(cols)].groupby(d.index.hour).mean().rename(columns=cols)
    pm = d[list(cols)].groupby(d.index.month).mean().rename(columns=cols)
    diaria = d[list(cols)].mean().rename(index=cols) * 24 / 1000  # kWh/m²·día
    t = pd.DataFrame({"media_W_m2": d[list(cols)].mean().rename(index=cols), "kWh_m2_dia": diaria})
    dia_sol = d["cenit_sol"] < 85
    t.loc["Fracción difusa diurna", "media_W_m2"] = d.loc[dia_sol, "DHI"].sum() / d.loc[dia_sol, "GHI"].sum()
    tabla(t.round(4).rename_axis("superficie"), "clima_irradiancia_orientacion.csv")
    tabla(pm.round(3).rename_axis("mes"), "clima_irradiancia_orientacion_mes.csv")

    fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4.8))
    colores = [PAL[3], PAL[0], PAL[1], PAL[2], PAL[6]]
    for (k, nom), c in zip(cols.items(), colores):
        a.plot(range(24), ph[nom], color=c, lw=2, label=nom)
        if nom != "Cubierta":
            b.plot(range(1, 13), pm[nom], color=c, lw=2, marker="o", label=nom)
    a.set_xticks(range(0, 24, 3))
    a.set_xlabel("Hora local (fin de la hora)")
    a.set_ylabel("W/m²")
    a.legend(fontsize=9)
    titulo(a, "(a) Perfil horario medio", "Cielo isótropo, albedo 0,2")
    b.set_xticks(range(1, 13), MESES, rotation=45)
    b.set_ylabel("W/m²")
    titulo(b, "(b) Media mensual en los muros", "Promedio de las 24 horas")
    guardar(fig, "clima_muros.png", FUENTE + " 2015–2025.")
    return t, pm


def cielo(s):
    d = s.loc["2015":"2025"]
    ph = d[["T", "T_cielo", "dT_cielo", "L_onda_larga"]].groupby(d.index.hour).mean()
    temporada = np.where(d.index.month.isin(SECA), "seca", "lluviosa")
    pt = d["dT_cielo"].groupby(temporada).mean()
    tabla(ph.round(3).rename_axis("hora"), "clima_cielo_perfil.csv")

    fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4.6))
    a.plot(range(24), ph["T"], color=PAL[1], lw=2, label="Aire (T)")
    a.plot(range(24), ph["T_cielo"], color=PAL[0], lw=2, label="Cielo (T_cielo)")
    a.fill_between(range(24), ph["T_cielo"], ph["T"], color=GRID, alpha=.7)
    a.set_xticks(range(0, 24, 3))
    a.set_xlabel("Hora local")
    a.set_ylabel("°C")
    a.legend(fontsize=9)
    titulo(a, "(a) Temperatura del aire y del cielo", "Media por hora")
    b.hist(d["dT_cielo"], bins=np.arange(-1, 18, .25), color=PAL[0], alpha=.85)
    b.axvline(d["dT_cielo"].mean(), color=TXT, lw=1.2, label=f"Media {fmt(d['dT_cielo'].mean())} K")
    b.axvline(11, color=PAL[7], lw=1.2, ls="--", label="11 K, ISO 13790")
    b.set_xlabel("T − T_cielo (K)")
    b.set_ylabel("Horas")
    b.legend(fontsize=9)
    titulo(b, "(b) Diferencia aire − cielo", "Distribución horaria")
    guardar(fig, "clima_cielo.png", FUENTE + " 2015–2025. T_cielo = (L/σ)^¼.")
    return ph, pt


def main():
    s = pd.read_parquet(SERIE)
    g = pd.read_csv(GDEX, index_col="tiempo_utc", parse_dates=True)
    om = leer_openmeteo()
    ide, crudos = leer_ideam()
    print(f"Serie: {len(s)} horas, {s.index.min()} a {s.index.max()}; GDEX crudo {len(g)}; "
          f"Open-Meteo {len(om)}; IDEAM {len(ide)}")
    print("Registros IDEAM (total, fuera de rango):", crudos)

    t_cob, por_anio, huecos = cobertura(s, g, ide, crudos)
    print(t_cob.to_string(index=False))
    print(por_anio.join(huecos).to_string())
    print(resumen(s).round(2).to_string(index=False))
    m = climatologia(s)
    print(m.round(2).to_string())
    p = perfil_horario(s)
    for tem in ["todo", "seca", "lluviosa"]:
        x = p.loc[tem]
        print(tem, "T min/max", x["T"].idxmin(), round(x["T"].min(), 2), x["T"].idxmax(), round(x["T"].max(), 2),
              "HI max", x["HI"].idxmax(), round(x["HI"].max(), 2), "HI min", round(x["HI"].min(), 2),
              "HR min", x["HR"].idxmin(), round(x["HR"].min(), 1), "HR max", round(x["HR"].max(), 1),
              "GHI max", x["GHI"].idxmax(), round(x["GHI"].max(), 1))
    print(distribucion_hi(s).round(2).to_string(index=False))
    a, pend = tendencia(s)
    print(a.round(2).to_string())
    print("pendientes por década", {k: round(v, 3) for k, v in pend.items()})
    t, ph, pm = contraste(s, g, om, ide)
    print(t.round(3).to_string(index=False))
    x = ph[(ph.fuente == "GDEX")]
    for v in ["T", "HI", "HR"]:
        y = x[x.variable == v].set_index("hora")["sesgo"]
        print(v, "GDEX sesgo min", y.idxmin(), round(y.min(), 2), "max", y.idxmax(), round(y.max(), 2))
    y = pm[(pm.fuente == "GDEX") & (pm.variable == "T")].set_index("mes")["sesgo"]
    print("T GDEX por mes", y.round(2).to_dict())
    frec, vel, vt, tv = viento_lluvia(s)
    print(frec.round(1).to_dict(), vel.round(2).to_dict(), vt.round(2).to_dict())
    print(tv.round(2).to_string())
    tm, pmm = muros(s)
    print(tm.round(3).to_string())
    ph_c, pt = cielo(s)
    print(ph_c.round(2).to_string())
    print("dT_cielo por temporada", pt.round(2).to_dict(), "noche", round(s.loc["2015":"2025", "dT_cielo"][
        np.isin(s.loc["2015":"2025"].index.hour, NOCHE)].mean(), 2))
    print("dT_cielo < 0 (h):", int((s["dT_cielo"] < 0).sum()))


if __name__ == "__main__":
    main()
