"""Clasificación de los meses en El Niño, La Niña o neutro y su efecto en el clima y la carga de Barranquilla.

Fuente: índice ONI de la NOAA (Climate Prediction Center, oni.ascii.txt), la anomalía de la temperatura del mar en la
región Niño 3.4 promediada en trimestres móviles. Cada trimestre se asigna a su mes central (DJF → enero).

Regla de la NOAA: hay un episodio de El Niño (La Niña) cuando el ONI es ≥ +0,5 (≤ −0,5) en al menos cinco trimestres
móviles seguidos; los meses del episodio llevan esa fase y los demás son neutros. La intensidad del episodio es la de
su ONI máximo en valor absoluto: débil (0,5–0,9), moderado (1,0–1,4), fuerte (1,5–1,9) y muy fuerte (≥ 2,0).

Para cada mes de la serie horaria (01_serie_clima.py) se calculan la temperatura, el índice de calor, la irradiancia,
la lluvia, los grados-hora de enfriamiento con el índice de calor (Ecuación 2 de la propuesta) con dos temperaturas
base, y la carga de enfriamiento del Paso 3 de la Fase 1 de la vivienda media del catastro. La carga usa la misma
envolvente común y la geometría media que se deduce de las tablas publicadas del script 11 de arquetipos. Como las
fases no se reparten igual en el año, se compara la anomalía de cada mes frente a la media de su mes calendario en
2015–2025, no el valor bruto.

Uso:  python scripts/03_enso.py
Salidas (salidas/):
  enso_meses.csv        ONI, fase, episodio e intensidad de cada mes, con las variables y sus anomalías
  enso_anomalias.csv    anomalía media por fase (y por intensidad) con su error estándar y el número de meses
  enso_anios.csv        año ENSO (julio a junio): fase dominante, ONI máximo y totales de grados-hora y carga
  enso_anomalias.png    anomalía mensual del índice de calor y de la carga con el ONI
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
BASE = RAIZ.parents[1]
sys.path.insert(0, str(BASE / "arquetipos"))
from src import carga as cg  # noqa: E402
from src.estilo import GREY, OCH, PET, guardar, lienzo  # noqa: E402

ONI = RAIZ / "datos" / "noaa" / "oni.ascii.txt"
SALIDAS = RAIZ / "salidas"
TABLAS_ARQ = BASE / "arquetipos" / "salidas" / "tablas"
CENTRO = {"DJF": 1, "JFM": 2, "FMA": 3, "MAM": 4, "AMJ": 5, "MJJ": 6, "JJA": 7, "JAS": 8, "ASO": 9, "SON": 10,
          "OND": 11, "NDJ": 12}
BASES_CDH = [26.5, 30.0]  # consigna del Paso 3 y una base alta; la propuesta estimará Tb con los datos
COMPONENTES = {"cubierta": "c_t", "muros": "c_m", "ventanas": "c_v", "infiltracion_sensible": "c_V_sens",
               "latente": "c_V_lat"}


def leer_oni():
    o = pd.read_csv(ONI, sep=r"\s+")
    o["mes"] = pd.to_datetime(dict(year=o["YR"], month=o["SEAS"].map(CENTRO), day=1))
    return o.set_index("mes")["ANOM"].rename("oni")


def fases(oni, umbral=0.5, minimo=5):
    """Fase de cada mes con la regla de cinco trimestres seguidos, y el número e intensidad del episodio."""
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


def geometria_media():
    """Áreas y volumen medios por vivienda: carga media de cada componente / su coeficiente (clima GDEX)."""
    q = pd.read_csv(TABLAS_ARQ / "clima_gdex_carga.csv", index_col="clima").loc["gdex"]
    c = pd.read_csv(TABLAS_ARQ / "clima_gdex_coeficientes.csv", index_col="coeficiente")["gdex"]
    return {k: q[k] / c[v] for k, v in COMPONENTES.items()}


def por_mes(s):
    s = s.copy()
    s["mes"] = s.index.to_period("M").to_timestamp()
    g = s.groupby("mes")
    m = pd.DataFrame({"T": g["T"].mean(), "HI": g["HI"].mean(), "GHI": g["GHI"].mean(),
                      "lluvia_mm": g["lluvia_mm"].sum(), "horas": g.size()})
    for tb in BASES_CDH:
        m[f"CDH_{tb:g}"] = g["HI"].apply(lambda x, tb=tb: (x - tb).clip(lower=0).sum())
    geo = geometria_media()
    cargas = []
    for mes, d in g:
        c = cg.coeficientes(c=pd.DataFrame({"anio": 0, "T": d["T"].to_numpy(), "Td": d["Td"].to_numpy(),
                                            "I": d["GHI"].to_numpy()}))
        cargas.append({"mes": mes, **{f"carga_{k}": c[v] * geo[k] for k, v in COMPONENTES.items()}})
    q = pd.DataFrame(cargas).set_index("mes")
    m = m.join(q)
    m["carga_total"] = q.sum(axis=1)
    return m[m["horas"] >= 24 * 28]  # meses completos


def main():
    s = pd.read_parquet(SALIDAS / "clima_horario_barranquilla.parquet")
    s = s[(s.index - pd.Timedelta(seconds=1)) >= "2015-01-01"]
    m = por_mes(s).join(fases(leer_oni()), how="left")
    variables = ["T", "HI", "GHI", "lluvia_mm"] + [f"CDH_{tb:g}" for tb in BASES_CDH] + ["carga_total"]
    clim = m[m.index.year <= 2025].groupby(m[m.index.year <= 2025].index.month)[variables].mean()
    RELATIVAS = [v for v in variables if v.startswith("CDH") or v.startswith("carga") or v == "lluvia_mm"]
    for v in variables:
        m[f"clim_{v}"] = m.index.month.map(clim[v]).to_numpy()
        m[f"anom_{v}"] = m[v] - m[f"clim_{v}"]
        if v in RELATIVAS:
            m[f"anom_%_{v}"] = 100 * m[f"anom_{v}"] / m[f"clim_{v}"]
    m["mes_num"] = m.index.month
    SALIDAS.mkdir(parents=True, exist_ok=True)
    m.round(4).to_csv(SALIDAS / "enso_meses.csv")

    filas = []
    # Anomalías absolutas: media de los meses del grupo. Relativas: suma de las anomalías sobre la suma de las
    # climatologías de esos meses (la media de porcentajes exagera los meses secos, con poca lluvia de base)
    for clave, grupo in [("fase", m["fase"]), ("intensidad", m["fase"] + "_" + m["intensidad"].fillna(""))]:
        for nombre, d in m.groupby(grupo):
            fila = {"agrupacion": clave, "grupo": nombre.rstrip("_"), "meses": len(d),
                    "episodios": d["episodio"].nunique()}
            for v in variables:
                fila[f"anom_{v}"] = d[f"anom_{v}"].mean()
                fila[f"ee_anom_{v}"] = d[f"anom_{v}"].std(ddof=1) / np.sqrt(len(d)) if len(d) > 1 else np.nan
                if v in RELATIVAS:
                    fila[f"anom_%_{v}"] = 100 * d[f"anom_{v}"].sum() / d[f"clim_{v}"].sum()
                    fila[f"ee_anom_%_{v}"] = 100 * fila[f"ee_anom_{v}"] / d[f"clim_{v}"].mean()
            filas.append(fila)
    ta = pd.DataFrame(filas)
    ta.round(4).to_csv(SALIDAS / "enso_anomalias.csv", index=False)

    # Regresión descriptiva de la anomalía mensual sobre el ONI y una tendencia lineal (la década tuvo La Niña al
    # principio y El Niño al final, así que sin tendencia el ONI absorbería parte del calentamiento). Los meses no son
    # independientes: los errores estándar de arriba son optimistas.
    x = np.arange(len(m)) / 120
    reg = {}
    for v in ["anom_HI", "anom_%_carga_total", "anom_%_CDH_26.5"]:
        X = np.column_stack([np.ones(len(m)), m["oni"], x])
        b = np.linalg.lstsq(X, m[v], rcond=None)[0]
        reg[v] = {"por_unidad_de_oni": round(float(b[1]), 3), "tendencia_por_decada": round(float(b[2]), 3),
                  "correlacion_con_oni": round(float(np.corrcoef(m["oni"], m[v])[0, 1]), 3)}
    (SALIDAS / "enso_regresion.json").write_text(pd.Series(reg).to_json(indent=2, force_ascii=False),
                                                 encoding="utf-8")
    print(reg)

    m["anio_enso"] = np.where(m.index.month >= 7, m.index.year, m.index.year - 1)
    g = m.groupby("anio_enso")
    ty = pd.DataFrame({"meses": g.size(), "oni_max": g["oni"].max(), "oni_min": g["oni"].min(),
                       "fase_dominante": g["fase"].agg(lambda x: x.value_counts().idxmax()),
                       "HI_medio": g["HI"].mean(), "lluvia_mm": g["lluvia_mm"].sum(),
                       **{f"CDH_{tb:g}": g[f"CDH_{tb:g}"].sum() for tb in BASES_CDH},
                       "carga_total": g["carga_total"].sum()})
    ty = ty[ty["meses"] == 12]
    ty["carga_vs_media_%"] = 100 * (ty["carga_total"] / ty["carga_total"].mean() - 1)
    ty.index = [f"{a}-{a + 1}" for a in ty.index]
    ty.index.name = "anio_enso_jul_jun"
    ty.round(3).to_csv(SALIDAS / "enso_anios.csv")

    fig, ejes = lienzo(16, 9)
    ejes.remove()
    ax1 = fig.add_subplot(2, 1, 1)
    ax2 = fig.add_subplot(2, 1, 2, sharex=ax1)
    for ax in (ax1, ax2):
        for fase, color in [("el_nino", OCH), ("la_nina", PET)]:
            sel = m["fase"] == fase
            for t in m.index[sel]:
                ax.axvspan(t, t + pd.offsets.MonthBegin(1), color=color, alpha=0.15, lw=0)
        ax.axhline(0, color=GREY, lw=0.6)
    ax1.bar(m.index, m["anom_HI"], width=25, color=GREY)
    ax1.set_ylabel("Anomalía del índice\nde calor (°C)")
    ax2.bar(m.index, m["anom_%_carga_total"], width=25, color=GREY)
    ax2.set_ylabel("Anomalía de la carga\ndel Paso 3 (%)")
    ax3 = ax1.twinx()
    ax3.plot(m.index, m["oni"], color="black", lw=0.8)
    ax3.set_ylabel("ONI (°C)")
    ax3.spines["right"].set_visible(True)
    ax1.set_title("Sombreado: El Niño (coral) y La Niña (turquesa) según la regla de la NOAA", fontsize=8)
    guardar(fig, SALIDAS / "enso_anomalias.png")

    print(m.groupby("fase").size().to_string())
    print(ta[["agrupacion", "grupo", "meses", "episodios", "anom_T", "anom_HI", "anom_%_lluvia_mm",
              "anom_%_CDH_26.5", "anom_%_carga_total", "ee_anom_%_carga_total"]].round(2).to_string(index=False))
    print(ty.round(2).to_string())
    print(m.loc[m["episodio"].notna()].groupby("episodio")["oni"].agg(["size", "max", "min"]).round(2).to_string())


if __name__ == "__main__":
    main()
