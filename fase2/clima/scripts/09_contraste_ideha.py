"""Contraste del clima con la estación IDEHA-01 de Uninorte (Davis, registros de 30 minutos, mayo de 2025 en adelante).

Hasta ahora el clima solo se contrastaba con la estación 0029045190 del IDEAM en el aeropuerto, y solo en temperatura
y humedad. IDEHA-01 está en el campus de Uninorte (unos 11,02° N, 74,85° O, a mitad de camino entre las celdas de
ERA5-Land de 74,8° O y 74,9° O) y mide además radiación global, viento y lluvia. Con dos estaciones se puede ver si el
sesgo de ERA5-Land al mediodía es del reanálisis o del sitio del aeropuerto, y validar las variables sin contraste.

Convenciones:
  - Los registros de la Davis son promedios (o sumas) de 30 minutos marcados al final del intervalo, en hora local.
  - Variables instantáneas (T, humedad, viento): ERA5-Land da el valor en la hora en punto. Se compara con el promedio
    de los dos registros de 30 minutos que rodean la hora (los que terminan en H y en H + 30 min), centrado en H.
  - Variables acumuladas (radiación y lluvia): ERA5-Land da la hora que termina en H. Se compara con los registros que
    terminan en H − 30 min y en H (promedio de la radiación, suma de la lluvia).
  - Se exigen los dos registros de cada hora. El índice de calor se calcula con la misma función de la NOAA para
    todas las fuentes. El viento de la Davis viene en km/h a la altura del sensor (no a 10 m).
  - La hora local de la Davis se comprueba con el desfase que maximiza la correlación de la radiación con ERA5-Land.

Uso:  python scripts/09_contraste_ideha.py CARPETA_IDEHA [CARPETA_DESCARGAS]
Salidas (salidas/): contraste_ideha_resumen.csv, contraste_ideha_hora.csv, contraste_ideha_mes.csv,
                    contraste_ideha_radiacion.csv, contraste_ideha_lluvia_diaria.csv, contraste_ideha.json,
                    contraste_ideha.png
La serie de 30 minutos y la horaria de la estación quedan en datos/ideha/ (no se publican).
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import xarray as xr  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
BASE = RAIZ.parents[1]
COMPUERTA = next(p for p in (BASE / "compuerta_horaria", BASE / "scripts" / "compuerta") if p.exists())
sys.path.insert(0, str(COMPUERTA / "scripts" if (COMPUERTA / "scripts").exists() else COMPUERTA))
from comun import humedad_relativa, indice_calor  # noqa: E402

SALIDAS = RAIZ / "salidas"
DATOS = RAIZ / "datos" / "ideha"
IDEAM = COMPUERTA / "datos" / "procesados" / "ideam_horario.parquet"
OPENMETEO = COMPUERTA / "datos" / "crudos" / "openmeteo"
CELDAS = {"ERA5-Land 74,8 O": (11.0, 285.2), "ERA5-Land 74,9 O": (11.0, 285.1)}
VARS_NC = {"era5land_met": ["t2m", "d2m", "u10", "v10"], "era5land_rad_tp": ["ssrd", "tp"]}
INICIO = "2025-05-01"
SITIO = (11.02, -74.85)        # campus de Uninorte, aproximado
RELOJ_BIEN = pd.Timestamp("2026-05-20")  # desde aquí el reloj de la estación coincide con el sol
IDEAM_UTC = (pd.Timestamp("2024-10-29"), pd.Timestamp("2026-08-01"))  # tramo del IDEAM con la hora en UTC
# columnas de la exportación de WeatherLink que se usan (posición en la fila)
COLS = {"T": 2, "HR": 5, "Td": 6, "viento_kmh": 7, "lluvia_mm": 17, "GHI": 19}


def leer_ideha(carpeta):
    """Todos los .txt de la estación en una serie de 30 minutos sin duplicados."""
    filas = []
    for f in sorted(Path(carpeta).glob("*.txt")):
        for linea in f.read_text(encoding="latin-1", errors="replace").splitlines():
            p = linea.split()
            if len(p) > 19 and p[0].count("/") == 2:
                filas.append([p[0], p[1]] + [p[i] for i in COLS.values()])
    d = pd.DataFrame(filas, columns=["fecha", "hora", *COLS])
    doce = d.hora.str.endswith(("a", "p"))
    t12 = pd.to_datetime(d.fecha + " " + d.hora.str.replace("a", "AM").str.replace("p", "PM"),
                         format="%d/%m/%y %I:%M%p", errors="coerce")
    t24 = pd.to_datetime(d.fecha + " " + d.hora, format="%d/%m/%y %H:%M", errors="coerce")
    d.index = t12.where(doce, t24)
    d = d[d.index.notna()].drop(columns=["fecha", "hora"])
    d = d[~d.index.duplicated(keep="last")].sort_index().apply(pd.to_numeric, errors="coerce")
    d.index.name = "fin_intervalo_local"
    return d


def horaria_ideha(d):
    """Serie horaria de la estación con las convenciones del encabezado."""
    d = d.asfreq("30min")
    sig = d.shift(-1)  # el registro que termina 30 min después
    ant = d.shift(1)   # el registro que termina 30 min antes
    h = pd.DataFrame(index=d.index)
    for c in ["T", "HR", "Td"]:
        h[c] = (d[c] + sig[c]) / 2
    h["viento"] = (d["viento_kmh"] + sig["viento_kmh"]) / 2 / 3.6
    h["GHI"] = (d["GHI"] + ant["GHI"]) / 2
    h["lluvia_mm"] = d["lluvia_mm"] + ant["lluvia_mm"]
    h = h[h.index.minute == 0]
    h["HI"] = indice_calor(h["T"], h["HR"])
    h.index.name = "hora_local"
    return h


def leer_celdas(raiz):
    """T, Td, viento, radiación y lluvia de las dos celdas de ERA5-Land, en hora local, desde INICIO."""
    cols = {}
    for carpeta, variables in VARS_NC.items():
        for var in variables:
            partes = []
            for f in sorted((raiz / carpeta).glob(f"*.{var}.e5land.*.nc")):
                if f.name.split(".")[-2][:8] < INICIO.replace("-", "")[:6] + "00":
                    continue
                with xr.open_dataset(f) as ds:
                    partes.append(ds[var].sel(latitude=11.0, method="nearest")
                                  .sel(longitude=[c[1] for c in CELDAS.values()], method="nearest").load())
            cols[var] = xr.concat(partes, dim="valid_time").sortby("valid_time")
    salida = {}
    for nombre, (lat, lon) in CELDAS.items():
        s = pd.DataFrame({v: cols[v].sel(longitude=lon, method="nearest").to_series() for v in cols})
        s.index = pd.to_datetime(s.index)
        s = s[~s.index.duplicated()]
        for v in ["ssrd", "tp"]:
            s[v] = np.where(s.index.hour == 1, s[v], s[v].diff())
        s.index = s.index - pd.Timedelta(hours=5)
        g = pd.DataFrame({"T": s.t2m - 273.15, "Td": s.d2m - 273.15, "viento": np.hypot(s.u10, s.v10),
                          "GHI": (s.ssrd / 3600).clip(lower=0), "lluvia_mm": (s.tp * 1000).clip(lower=0)})
        g["HR"] = humedad_relativa(g["T"], g["Td"])
        g["HI"] = indice_calor(g["T"], g["HR"])
        salida[nombre] = g.iloc[1:]
    return salida


def leer_openmeteo():
    """Viento y radiación de ERA5 (0,25°) que sirve Open-Meteo, en hora local."""
    partes = []
    for f in sorted(OPENMETEO.glob("om_202[56].json")):
        h = json.loads(f.read_text())["hourly"]
        partes.append(pd.DataFrame({"viento": h["wind_speed_10m_era5"], "GHI": h["shortwave_radiation_era5"]},
                                   index=pd.to_datetime(h["time"])))
    o = pd.concat(partes)
    o.index = o.index - pd.Timedelta(hours=5)
    return o


def leer_ideam():
    """IDEAM horario sin el tramo en que la API de datos.gov.co entrega la hora en UTC (pico diario a las 16–19 h)."""
    i = pd.read_parquet(IDEAM).rename(columns={"t_ideam": "T", "hr_ideam": "HR"})
    i = i[(i.index < IDEAM_UTC[0]) | (i.index >= IDEAM_UTC[1])]
    i["HI"] = indice_calor(i["T"], i["HR"])
    return i[["T", "HR", "HI"]]


def metricas(x, y):
    m = pd.concat([x, y], axis=1).dropna()
    e = m.iloc[:, 0] - m.iloc[:, 1]
    return {"n": len(m), "sesgo": e.mean(), "rmse": float(np.sqrt((e ** 2).mean())),
            "r": m.iloc[:, 0].corr(m.iloc[:, 1])}


def desfase_diario(d):
    """Desfase del reloj de la estación en cada día (h, múltiplos de 30 min), con la radiación de cielo despejado.

    Para cada día con sol se busca el corrimiento de -14 h a +14 h que maximiza la correlación entre la radiación
    de la Davis y la de cielo despejado (Haurwitz, pvlib) en el centro de cada intervalo. Hora real = etiqueta − desfase.
    """
    import pvlib
    d = d.asfreq("30min")
    t = (d.index - pd.Timedelta(minutes=15)).tz_localize("Etc/GMT+5")
    cs = pd.Series(pvlib.location.Location(*SITIO, tz="Etc/GMT+5").get_clearsky(t, model="haurwitz")["ghi"].values,
                   index=d.index)
    filas = []
    for dia, g in d.groupby(d.index.date):
        if g["GHI"].notna().sum() < 40 or g["GHI"].max() < 200:
            continue
        dia = pd.Timestamp(dia)
        w = d["GHI"].loc[dia - pd.Timedelta(hours=14):dia + pd.Timedelta(hours=38)]
        y = cs.loc[str(dia.date())]
        mejor = (np.nan, -1.0)
        for k in range(-28, 29):
            r = w.shift(-k).reindex(y.index).corr(y)
            if r > mejor[1]:
                mejor = (k / 2, r)
        filas.append({"dia": dia, "desfase_h": mejor[0], "r": mejor[1]})
    return pd.DataFrame(filas).set_index("dia")


def corregir(d, desf, modo):
    """«limpio»: solo los días con reloj correcto (|desfase| ≤ 0,5 h desde el 20-may-2026), sin corrimiento.
    «corregido»: cada día con r ≥ 0,9 se corre según su desfase. Los demás días se descartan."""
    dia = pd.DatetimeIndex(d.index.normalize())
    if modo == "limpio":
        ok = desf.index[(desf["desfase_h"].abs() <= 0.5) & (desf.index >= RELOJ_BIEN) & (desf["r"] >= 0.9)]
        return d[dia.isin(ok)]
    ok = desf[desf["r"] >= 0.9]["desfase_h"]
    d = d[dia.isin(ok.index)].copy()
    d.index = d.index - pd.to_timedelta(ok.reindex(pd.DatetimeIndex(d.index.normalize())).values, unit="h")
    return d[~d.index.duplicated()].sort_index()


def main():
    carpeta = Path(sys.argv[1])
    raiz = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.home() / "Downloads"
    d30 = leer_ideha(carpeta)
    DATOS.mkdir(parents=True, exist_ok=True)
    d30.to_csv(DATOS / "ideha01_30min.csv.gz")
    desf = desfase_diario(d30)
    desf.round(3).to_csv(SALIDAS / "contraste_ideha_desfase_diario.csv")
    print(f"IDEHA-01: {len(d30)} registros de 30 min, {d30.index.min()} a {d30.index.max()}; "
          f"{len(desf)} días con desfase estimado")
    refs = leer_celdas(raiz)
    refs["IDEAM aeropuerto"] = leer_ideam()
    om = leer_openmeteo()
    fin = min(r.index.max() for k, r in refs.items() if k.startswith("ERA5"))
    for modo in ["limpio", "corregido"]:
        est = horaria_ideha(corregir(d30, desf, modo))
        est = est[(est.index >= INICIO) & (est.index <= fin)]
        est.round(3).to_csv(DATOS / f"ideha01_horaria_{modo}.csv.gz")
        analizar(est, refs, om, modo)

    # lluvia diaria con todos los días de 48 registros: la selección por días soleados del modo «corregido» dejaría
    # fuera los días de lluvia, y un desfase de hasta 3 h solo mueve una parte del total de un día al siguiente
    ll = d30["lluvia_mm"].asfreq("30min")
    n = ll.groupby(ll.index.date).count()
    ll = ll.groupby(ll.index.date).sum()[n == 48]
    ll.index = pd.to_datetime(ll.index)
    ll = ll[(ll.index >= INICIO) & (ll.index < fin.normalize())]
    dia = pd.DataFrame({"IDEHA": ll, **{k: v["lluvia_mm"].resample("D").sum().reindex(ll.index)
                                        for k, v in refs.items() if k.startswith("ERA5")}}).dropna()
    dia.round(2).to_csv(SALIDAS / "contraste_ideha_lluvia_diaria.csv")
    resumen = {c: {"total_mm": round(float(dia[c].sum()), 1), "dias_mas_1mm": int((dia[c] > 1).sum()),
                   "r_diaria": round(float(dia[c].corr(dia["IDEHA"])), 3)} for c in dia}
    resumen["dias"] = len(dia)
    (SALIDAS / "contraste_ideha_lluvia.json").write_text(json.dumps(resumen, indent=2, ensure_ascii=False),
                                                        encoding="utf-8")
    print("lluvia:", json.dumps(resumen, ensure_ascii=False))


def analizar(est, refs, om, sufijo):
    # comprobación de la hora: desfase de la radiación que maximiza la correlación con ERA5-Land
    ref_ghi = refs["ERA5-Land 74,8 O"]["GHI"]
    desfase = {k: est["GHI"].shift(k).corr(ref_ghi) for k in range(-3, 4)}
    mejor = max(desfase, key=desfase.get)

    # horas comunes a todas las fuentes de temperatura, para comparar sesgos sobre las mismas horas
    comunes = est[["T", "HR"]].dropna().index
    for r in refs.values():
        comunes = comunes.intersection(r[["T", "HR"]].dropna().index)

    resumen, por_hora, por_mes = [], [], []
    for var in ["T", "HR", "HI"]:
        for nombre, r in refs.items():
            for muestra, idx in [("horas comunes", comunes), ("todas", est.index)]:
                m = metricas(r[var].reindex(idx), est[var].reindex(idx))
                resumen.append({"variable": var, "fuente": nombre, "muestra": muestra, **m})
            e = (r[var] - est[var]).reindex(comunes)
            por_hora.append(e.groupby(e.index.hour).mean().rename(f"{var} | {nombre}"))
            por_mes.append(e.groupby(e.index.to_period("M")).mean().rename(f"{var} | {nombre}"))
    for var, fuentes in [("GHI", {**{k: v for k, v in refs.items() if k.startswith("ERA5")}, "ERA5 (Open-Meteo)": om}),
                         ("viento", {**{k: v for k, v in refs.items() if k.startswith("ERA5")}, "ERA5 (Open-Meteo)": om})]:
        for nombre, r in fuentes.items():
            m = metricas(r[var].reindex(est.index), est[var])
            m["media_fuente"] = r[var].reindex(est[var].dropna().index).mean()
            m["media_ideha"] = est[var].reindex(r[var].dropna().index).mean()
            resumen.append({"variable": var, "fuente": nombre, "muestra": "todas", **m})
            e = (r[var] - est[var]).dropna()
            por_hora.append(e.groupby(e.index.hour).mean().rename(f"{var} | {nombre}"))

    res = pd.DataFrame(resumen)
    hora = pd.concat(por_hora, axis=1)
    mes = pd.concat(por_mes, axis=1)

    # radiación diaria (solo días con las 24 horas en las dos fuentes)
    rad = pd.DataFrame({"IDEHA": est["GHI"], "ERA5-Land": ref_ghi.reindex(est.index),
                        "ERA5": om["GHI"].reindex(est.index)}).dropna()
    rad = rad[rad.groupby(rad.index.date)["IDEHA"].transform("size") == 24]
    rad_dia = rad.groupby(rad.index.date).sum() / 1000
    perfil_rad = rad.groupby(rad.index.hour).mean()

    SALIDAS.mkdir(parents=True, exist_ok=True)
    res.round(4).to_csv(SALIDAS / f"contraste_ideha_resumen_{sufijo}.csv", index=False)
    hora.round(3).to_csv(SALIDAS / f"contraste_ideha_hora_{sufijo}.csv")
    mes.round(3).to_csv(SALIDAS / f"contraste_ideha_mes_{sufijo}.csv")
    perfil_rad.round(1).to_csv(SALIDAS / f"contraste_ideha_radiacion_{sufijo}.csv")

    info = {
        "periodo": [str(est.index.min()), str(est.index.max())],
        "horas_estacion": int(est["T"].notna().sum()),
        "horas_comunes_temperatura": len(comunes),
        "desfase_radiacion_h": {str(k): round(v, 4) for k, v in desfase.items()},
        "desfase_optimo_h": mejor,
        "radiacion_diaria_kWh_m2": {c: round(rad_dia[c].mean(), 3) for c in rad_dia},
        "dias_radiacion": len(rad_dia),
    }
    (SALIDAS / f"contraste_ideha_{sufijo}.json").write_text(json.dumps(info, indent=2, ensure_ascii=False, default=float), encoding="utf-8")

    fig, ax = plt.subplots(2, 2, figsize=(12, 8))
    for nombre, c in zip(refs, ["#2a78d6", "#1baf7a", "#eb6834"]):
        ax[0, 0].plot(hora.index, hora[f"T | {nombre}"], marker="o", ms=3, color=c, label=nombre)
        ax[0, 1].plot(hora.index, hora[f"HI | {nombre}"], marker="o", ms=3, color=c, label=nombre)
    for a, t in [(ax[0, 0], "Temperatura: fuente − IDEHA-01 (°C)"), (ax[0, 1], "Índice de calor: fuente − IDEHA-01 (°C)")]:
        a.axhline(0, color="k", lw=.8)
        a.set(title=t, xlabel="Hora local", xticks=range(0, 24, 3))
        a.legend(fontsize=8)
    for c, col in zip(perfil_rad, ["k", "#2a78d6", "#e87ba4"]):
        ax[1, 0].plot(perfil_rad.index + 0.5 - 1, perfil_rad[c], color=col, label=c)
    ax[1, 0].set(title="Radiación global media por hora (W/m²)", xlabel="Hora local (centro de la hora)",
                 xticks=range(0, 24, 3))
    ax[1, 0].legend(fontsize=8)
    vi = pd.DataFrame({"IDEHA-01 (sensor)": est["viento"], "ERA5-Land 74,8 O": refs["ERA5-Land 74,8 O"]["viento"],
                       "ERA5 (Open-Meteo)": om["viento"]}).reindex(est.index).dropna()
    for c, col in zip(vi, ["k", "#2a78d6", "#e87ba4"]):
        p = vi[c].groupby(vi.index.hour).mean()
        ax[1, 1].plot(p.index, p.values, color=col, label=c)
    ax[1, 1].set(title="Viento medio por hora (m/s)", xlabel="Hora local", xticks=range(0, 24, 3))
    ax[1, 1].legend(fontsize=8)
    fig.suptitle(f"Contraste con la estación IDEHA-01 de Uninorte ({sufijo}), {est.index.min():%b %Y} a {est.index.max():%b %Y}")
    fig.tight_layout()
    fig.savefig(SALIDAS / f"contraste_ideha_{sufijo}.png", dpi=140)

    plt.close(fig)
    pd.set_option("display.width", 200)
    print(f"===== {sufijo} =====")
    print(res.round(2).to_string(index=False))
    print(json.dumps(info, indent=2, ensure_ascii=False, default=float))
    print(hora.round(2).to_string())


if __name__ == "__main__":
    main()
