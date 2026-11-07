"""EDA de El Niño y La Niña: ONI de la NOAA y anomalías del clima de Barranquilla y de la carga del Paso 3 por fase.

Lee (solo lectura):
  fase2/clima/datos/noaa/oni.ascii.txt                       ONI del CPC de la NOAA, descargado el 3-nov-2026
  fase2/clima/salidas/clima_horario_barranquilla.parquet     serie horaria de la Fase 2 (ERA5-Land de GDEX)
  fase2/clima/salidas/enso_meses.csv, enso_anios.csv         salidas de fase2/clima/scripts/03_enso.py (la carga del
                                                             Paso 3 por mes, que necesita el código de arquetipos)

Rehace la clasificación de los meses con la regla de la NOAA y las anomalías de temperatura, índice de calor y lluvia
para comprobar las salidas de la Fase 2, y añade el perfil horario de la anomalía por fase.

Escribe figuras/eda/enso_*.png y tablas/eda/enso_*.csv.

Uso:  python scripts/eda/enso.py   (desde la raíz del repositorio)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from estilo import *  # noqa: E402,F401,F403

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

np.random.seed(SEMILLA)

CLIMA = ML / "fase2" / "clima"
ONI = CLIMA / "datos" / "noaa" / "oni.ascii.txt"
SERIE = CLIMA / "salidas" / "clima_horario_barranquilla.parquet"
MESES_F2 = CLIMA / "salidas" / "enso_meses.csv"
ANIOS_F2 = CLIMA / "salidas" / "enso_anios.csv"
CENTRO = {"DJF": 1, "JFM": 2, "FMA": 3, "MAM": 4, "AMJ": 5, "MJJ": 6, "JJA": 7, "JAS": 8, "ASO": 9, "SON": 10,
          "OND": 11, "NDJ": 12}
COLOR = {"el_nino": PAL[7], "la_nina": PAL[0], "neutro": "#9a9993"}
NOMBRE = {"el_nino": "El Niño", "la_nina": "La Niña", "neutro": "Neutro"}
FUENTE = "Fuente: ONI del CPC de la NOAA (3-nov-2026); ERA5-Land (GDEX), serie de la Fase 2. Cálculos propios."


def leer_oni():
    o = pd.read_csv(ONI, sep=r"\s+")
    o["mes"] = pd.to_datetime(dict(year=o["YR"], month=o["SEAS"].map(CENTRO), day=1))
    return o.set_index("mes")["ANOM"].rename("oni")


def fases(oni, umbral=0.5, minimo=5):
    """Regla de la NOAA: episodio si el ONI pasa el umbral en al menos cinco trimestres móviles seguidos."""
    fase = pd.Series("neutro", index=oni.index)
    episodio = pd.Series(pd.NA, index=oni.index, dtype="object")
    for nombre, signo in [("el_nino", 1), ("la_nina", -1)]:
        cumple = (signo * oni) >= umbral
        bloque = (cumple != cumple.shift()).cumsum()
        for _, idx in cumple.groupby(bloque).groups.items():
            if cumple.loc[idx[0]] and len(idx) >= minimo:
                fase.loc[idx] = nombre
                episodio.loc[idx] = f"{nombre}_{idx[0]:%Y-%m}"
    pico = oni.abs().groupby(episodio).transform("max")
    intensidad = pd.cut(pico, [0.5, 1.0, 1.5, 2.0, np.inf], right=False,
                        labels=["debil", "moderado", "fuerte", "muy_fuerte"]).astype("object")
    return pd.DataFrame({"oni": oni, "fase": fase, "episodio": episodio, "intensidad": intensidad})


def mensual(s):
    s = s[(s.index - pd.Timedelta(seconds=1)) >= "2015-01-01"]
    g = s.groupby(s.index.to_period("M").to_timestamp())
    m = pd.DataFrame({"T": g["T"].mean(), "HI": g["HI"].mean(), "HR": g["HR"].mean(), "GHI": g["GHI"].mean(),
                      "lluvia_mm": g["lluvia_mm"].sum(), "horas_lluvia_vacias": g["lluvia_mm"].apply(
                          lambda x: int(x.isna().sum())), "horas": g.size()})
    m = m[m["horas"] >= 24 * 28]
    base = m[m.index.year <= 2025]
    for v in ["T", "HI", "HR", "GHI", "lluvia_mm"]:
        clim = base.groupby(base.index.month)[v].mean()
        m[f"anom_{v}"] = m[v] - m.index.month.map(clim).to_numpy()
        m[f"clim_{v}"] = m.index.month.map(clim).to_numpy()
    return m


def main():
    oni = leer_oni()
    f = fases(oni)
    print(f"ONI: {oni.index.min():%Y-%m} a {oni.index.max():%Y-%m}, {len(oni)} trimestres")
    s = pd.read_parquet(SERIE)
    m = mensual(s).join(f, how="left")
    f2 = pd.read_csv(MESES_F2, index_col="mes", parse_dates=True)
    m = m.join(f2[["carga_total", "anom_%_carga_total", "clim_carga_total", "CDH_26.5", "clim_CDH_26.5"]])

    # Comprobación frente a la Fase 2
    comp = {"meses": len(m), "fase_distinta": int((m["fase"] != f2["fase"].reindex(m.index)).sum()),
            "max_dif_anom_HI": float((m["anom_HI"] - f2["anom_HI"].reindex(m.index)).abs().max()),
            "max_dif_anom_T": float((m["anom_T"] - f2["anom_T"].reindex(m.index)).abs().max())}
    print("Comprobación con fase2/clima/salidas/enso_meses.csv:", comp)

    # Meses por fase y por año
    mp = pd.crosstab(m.index.year, m["fase"]).reindex(columns=["el_nino", "la_nina", "neutro"], fill_value=0)
    mp.loc["total"] = mp.sum()
    mp.index.name = "anio"
    tabla(mp, "enso_meses_por_fase.csv")
    print(mp.to_string())

    # Episodios (con el ONI completo, no solo los meses de la serie)
    ep = f.dropna(subset=["episodio"]).loc["2014":]
    filas = []
    for e, d in ep.groupby("episodio"):
        dm = m[m["episodio"] == e]
        filas.append({"episodio": e, "fase": d["fase"].iloc[0], "inicio": f"{d.index.min():%Y-%m}",
                      "fin": f"{d.index.max():%Y-%m}", "meses_episodio": len(d), "meses_en_serie": len(dm),
                      "oni_pico": d["oni"].abs().max() * (1 if d["fase"].iloc[0] == "el_nino" else -1),
                      "intensidad": d["intensidad"].iloc[0], "anom_T": dm["anom_T"].mean(),
                      "anom_HI": dm["anom_HI"].mean(), "anom_%_carga": dm["anom_%_carga_total"].mean()})
    te = pd.DataFrame(filas).sort_values("inicio")
    tabla(te.round(3), "enso_episodios.csv", index=False)
    print(te.round(2).to_string(index=False))

    # Anomalías por fase
    filas = []
    for fase, d in m.groupby("fase"):
        fila = {"fase": fase, "meses": len(d), "episodios": d["episodio"].nunique()}
        for v in ["T", "HI", "HR", "GHI"]:
            fila[f"anom_{v}"] = d[f"anom_{v}"].mean()
            fila[f"ee_{v}"] = d[f"anom_{v}"].std(ddof=1) / np.sqrt(len(d))
        fila["anom_%_lluvia"] = 100 * d["anom_lluvia_mm"].sum() / d["clim_lluvia_mm"].sum()
        fila["anom_%_CDH_26.5"] = 100 * (d["CDH_26.5"].sum() / d["clim_CDH_26.5"].sum() - 1)
        fila["anom_%_carga"] = 100 * (d["carga_total"].sum() / d["clim_carga_total"].sum() - 1)
        fila["ee_%_carga"] = d["anom_%_carga_total"].std(ddof=1) / np.sqrt(len(d))
        filas.append(fila)
    ta = pd.DataFrame(filas).set_index("fase").loc[["el_nino", "la_nina", "neutro"]]
    tabla(ta.round(4), "enso_anomalias_fase.csv")
    print(ta.round(3).T.to_string())

    # Regresión descriptiva del HI sobre el ONI con tendencia (como en 03_enso.py)
    x = np.arange(len(m)) / 120
    X = np.column_stack([np.ones(len(m)), m["oni"], x])
    reg = {}
    for v in ["anom_HI", "anom_T", "anom_%_carga_total"]:
        b = np.linalg.lstsq(X, m[v], rcond=None)[0]
        reg[v] = {"por_unidad_oni": b[1], "tendencia_decada": b[2], "r_oni": np.corrcoef(m["oni"], m[v])[0, 1]}
    tr = pd.DataFrame(reg).T
    tabla(tr.round(4).rename_axis("variable"), "enso_regresion.csv")
    print(tr.round(3).to_string())

    # Perfil horario de la anomalía del HI por fase (frente al mismo mes calendario y la misma hora, 2015–2025)
    h = s[(s.index - pd.Timedelta(seconds=1)) >= "2015-01-01"][["T", "HI"]].copy()
    h["mes"] = h.index.to_period("M").to_timestamp()
    h["hora"] = h.index.hour
    h["mes_cal"] = h.index.month
    base = h[h.index.year <= 2025]
    clim = base.groupby(["mes_cal", "hora"])[["T", "HI"]].mean()
    h = h.join(clim, on=["mes_cal", "hora"], rsuffix="_clim")
    h["anom_HI"] = h["HI"] - h["HI_clim"]
    h["anom_T"] = h["T"] - h["T_clim"]
    h["fase"] = h["mes"].map(m["fase"])
    ph = h.dropna(subset=["fase"]).groupby(["fase", "hora"])[["anom_T", "anom_HI"]].mean().unstack(0)
    tabla(ph.round(4), "enso_anomalia_horaria.csv")
    print(ph["anom_HI"].round(2).to_string())

    # Años ENSO
    ya = pd.read_csv(ANIOS_F2)
    tabla(ya[["anio_enso_jul_jun", "fase_dominante", "oni_max", "oni_min", "HI_medio", "lluvia_mm", "CDH_26.5",
              "carga_vs_media_%"]], "enso_anios.csv", index=False)
    print(ya.round(2).to_string(index=False))

    # ---------------------------------------------------------------- figuras
    # 1. Serie del ONI
    fig, (a, b) = plt.subplots(2, 1, figsize=(12, 7.5), gridspec_kw={"height_ratios": [1, 1.5]})
    a.fill_between(oni.index, oni, 0, where=oni >= 0, color=PAL[7], alpha=.6, lw=0)
    a.fill_between(oni.index, oni, 0, where=oni < 0, color=PAL[0], alpha=.6, lw=0)
    a.axvspan(pd.Timestamp("2015-01-01"), pd.Timestamp("2026-09-30"), color=GRID, alpha=.6, lw=0)
    a.set_ylabel("ONI (°C)")
    titulo(a, "(a) ONI de 1950 a 2026", "Sombreado gris: periodo de la serie de clima (2015 a septiembre de 2026)")
    o = f.loc["2014-01":]
    a2 = b
    a2.bar(o.index, o["oni"], width=25, color=[COLOR[x] for x in o["fase"]])
    for y in (-0.5, 0.5):
        a2.axhline(y, color=TXT2, ls="--", lw=.8)
    a2.axhline(0, color=TXT2, lw=.8)
    for e, r in te.iterrows():
        t0 = pd.Timestamp(r["inicio"]) + (pd.Timestamp(r["fin"]) - pd.Timestamp(r["inicio"])) / 2
        a2.text(t0, r["oni_pico"] + (0.12 if r["oni_pico"] > 0 else -0.25), f"{fmt(r['oni_pico'], 2)}",
                ha="center", fontsize=8.5, color=TXT2)
    a2.set_ylabel("ONI (°C)")
    from matplotlib.patches import Patch
    a2.set_ylim(-1.4, 2.95)
    a2.legend(handles=[Patch(color=COLOR[k], label=NOMBRE[k]) for k in COLOR], fontsize=9, loc="lower left",
              ncol=3)
    titulo(a2, "(b) Fase de cada mes, 2014–2026", "Regla de la NOAA: ±0,5 °C en cinco trimestres seguidos; "
                                                  "número: ONI pico del episodio")
    guardar(fig, "enso_oni.png", "Fuente: ONI del CPC de la NOAA, descargado el 3-nov-2026. Cálculos propios.")

    # 2. Anomalías por fase
    fig, ejes = plt.subplots(1, 4, figsize=(14, 4.4))
    orden = ["el_nino", "la_nina", "neutro"]
    for ax, (col, ee, u, tt) in zip(ejes, [("anom_T", "ee_T", "°C", "(a) Temperatura"),
                                           ("anom_HI", "ee_HI", "°C", "(b) Índice de calor"),
                                           ("anom_%_lluvia", None, "%", "(c) Lluvia"),
                                           ("anom_%_carga", "ee_%_carga", "%", "(d) Carga del Paso 3")]):
        y = ta.loc[orden, col]
        ax.bar(range(3), y, color=[COLOR[k] for k in orden],
               yerr=None if ee is None else ta.loc[orden, ee], capsize=4)
        ax.axhline(0, color=TXT2, lw=.8)
        ax.set_xticks(range(3), [f"{NOMBRE[k]}\n({ta.loc[k, 'meses']} m)" for k in orden], fontsize=9.5)
        ax.set_ylabel(u)
        for i, v in enumerate(y):
            ax.text(i + 0.12, v / 2, fmt(0.0 if abs(v) < 0.005 else v, 2 if u == "°C" else 1), ha="left",
                    va="center", fontsize=9, color=TXT)
        titulo(ax, tt)
    guardar(fig, "enso_anomalias_fase.png", FUENTE + " Barras de error: ± 1 error estándar.")

    # 3. Dispersión con el ONI y perfil horario
    fig, (a, b, c) = plt.subplots(1, 3, figsize=(15, 4.6))
    for k in orden:
        d = m[m["fase"] == k]
        a.scatter(d["oni"], d["anom_HI"], s=18, color=COLOR[k], label=NOMBRE[k], alpha=.85)
        b.scatter(d["oni"], d["anom_%_carga_total"], s=18, color=COLOR[k], alpha=.85)
    for ax, v in [(a, "anom_HI"), (b, "anom_%_carga_total")]:
        bb = np.polyfit(m["oni"], m[v], 1)
        xx = np.linspace(m["oni"].min(), m["oni"].max(), 10)
        ax.plot(xx, np.polyval(bb, xx), color=TXT, lw=1, ls="--")
        ax.axhline(0, color=TXT2, lw=.6)
        ax.axvline(0, color=TXT2, lw=.6)
        ax.set_xlabel("ONI (°C)")
    a.set_ylabel("Anomalía del HI mensual (°C)")
    a.legend(fontsize=9)
    titulo(a, "(a) Índice de calor y ONI", f"r = {fmt(reg['anom_HI']['r_oni'], 2)}; 141 meses")
    b.set_ylabel("Anomalía de la carga (%)")
    titulo(b, "(b) Carga del Paso 3 y ONI", f"r = {fmt(reg['anom_%_carga_total']['r_oni'], 2)}")
    for k in orden:
        c.plot(range(24), ph[("anom_HI", k)], color=COLOR[k], lw=2, marker=".", label=NOMBRE[k])
    c.axhline(0, color=TXT2, lw=.6)
    c.axvspan(-0.5, 5.5, color=GRID, alpha=.6, lw=0)
    c.axvspan(21.5, 23.5, color=GRID, alpha=.6, lw=0)
    c.set_xticks(range(0, 24, 3))
    c.set_xlabel("Hora local")
    c.set_ylabel("Anomalía del HI (°C)")
    titulo(c, "(c) Anomalía del HI por hora", "Frente al mismo mes y hora, 2015–2025")
    guardar(fig, "enso_dispersion.png", FUENTE + " Línea discontinua: recta de mínimos cuadrados.")

    # 4. Años ENSO
    fig, ax = plt.subplots(figsize=(12, 4.6))
    ax.bar(range(len(ya)), ya["carga_vs_media_%"], color=[COLOR[k] for k in ya["fase_dominante"]])
    ax.axhline(0, color=TXT2, lw=.8)
    ax.set_xticks(range(len(ya)), ya["anio_enso_jul_jun"], rotation=30)
    ax.set_ylabel("Carga del Paso 3 frente a la media (%)")
    for i, (v, om) in enumerate(zip(ya["carga_vs_media_%"], ya["oni_max"])):
        ax.text(i, v + (0.3 if v >= 0 else -0.3), fmt(v), ha="center", va="bottom" if v >= 0 else "top", fontsize=9)
    ax.legend(handles=[Patch(color=COLOR[k], label=NOMBRE[k]) for k in COLOR], fontsize=9, loc="upper left")
    titulo(ax, "Carga anual por año ENSO (julio a junio)", "Color: fase dominante del año")
    guardar(fig, "enso_anios.png", "Fuente: fase2/clima/salidas/enso_anios.csv (script 03_enso.py). ")


if __name__ == "__main__":
    main()
