"""Verificación de la caída del consumo residencial por suscriptor en Barranquilla (SUI 2015-2025).

Entradas (solo lectura):
  tesis-datos-barranquilla/tablas/SUI_Barranquilla_urbano_residencial_2015_2026.csv
  compuerta_horaria/datos/procesados/clima_diario.parquet   (ERA5-Land, copia de Open-Meteo)
Salidas en esta carpeta: tablas CSV y figura PNG.

Uso: python -I caida_consumo.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
SUI = RAIZ / "tesis-datos-barranquilla" / "tablas" / "SUI_Barranquilla_urbano_residencial_2015_2026.csv"
CLIMA = RAIZ / "compuerta_horaria" / "datos" / "procesados" / "clima_diario.parquet"

# Meses en que el SUI reporta suscriptores inflados (unos 30.000 de más en el total; en E6, 16.000 frente a 12.000-13.000
# antes y después). Dividir el consumo por esos suscriptores baja artificialmente el kWh por suscriptor.
INFLADOS = {(2020, 6)} | {(2021, m) for m in range(6, 13)} | {(2022, m) for m in range(1, 8)}

# Inflación anual del IPC (diciembre a diciembre, DANE), en %.
IPC = {2015: 6.77, 2016: 5.75, 2017: 4.09, 2018: 3.18, 2019: 3.80, 2020: 1.61, 2021: 5.62,
       2022: 13.12, 2023: 9.28, 2024: 5.20, 2025: 5.10}

ANTES, DESPUES = range(2015, 2020), [2023, 2024, 2025]


def cargar():
    d = pd.read_csv(SUI, sep=";")
    d = d[d.anio <= 2025].copy()
    d["valido"] = d.bandera.isna() & ~d.apply(lambda r: (r.anio, r.mes) in INFLADOS, axis=1)
    c = pd.read_parquet(CLIMA)
    m = c.groupby([c.index.year, c.index.month]).hi_media.mean()
    m.index.names = ["anio", "mes"]
    m = m.rename("hi").reset_index()
    # índice de calor del mes anterior (el consumo facturado de un mes corresponde sobre todo al ciclo previo)
    m["mes"] = m.mes % 12 + 1
    m.loc[m.mes == 1, "anio"] += 1
    return d.merge(m.rename(columns={"hi": "hi_lag"}), on=["anio", "mes"], how="left"), c


def ajuste(g, col, con_hi):
    """ln(col) = efecto de año + efecto de mes (+ beta * HI del mes anterior). Devuelve efectos de año y beta."""
    g = g.dropna(subset=["hi_lag"]) if con_hi else g
    X = pd.concat([pd.get_dummies(g.anio, prefix="a", dtype=float),
                   pd.get_dummies(g.mes, prefix="m", drop_first=True, dtype=float)], axis=1)
    if con_hi:
        X["hi"] = g.hi_lag.values
    b, *_ = np.linalg.lstsq(X.values, np.log(g[col].values.astype(float)), rcond=None)
    coef = dict(zip(X.columns, b))
    ya = pd.Series({y: coef[f"a_{y}"] for y in sorted(g.anio.unique())})
    return ya, 100 * coef.get("hi", np.nan)


def efectos_anuales(d):
    """kWh por suscriptor a clima constante, por estrato: % frente a 2015."""
    ef, betas = {}, {}
    for e, g in d[d.valido & (d.estrato != "total")].groupby("estrato"):
        ya, betas[e] = ajuste(g, "kWh_suscriptor", True)
        ef[e] = 100 * (np.exp(ya - ya.loc[2015]) - 1)
    return pd.DataFrame(ef), betas


def main():
    d, clima = cargar()
    v = d[d.valido]

    # 1) Totales: consumo anual equivalente y suscriptores medios
    tot = v[v.estrato == "total"].groupby("anio").agg(kwh=("consumo_kWh", "sum"), meses=("mes", "count"),
                                                      S=("suscriptores", "mean"))
    tot["GWh"] = tot.kwh / tot.meses * 12 / 1e6
    tot["kWh_susc"] = tot.kwh / tot.meses / tot.S
    # Índices con efectos de mes: en 2021 y 2022 quedan pocos meses válidos y el promedio simple tendría sesgo estacional
    gt = v[v.estrato == "total"]
    idx = pd.DataFrame({k: 100 * np.exp(ajuste(gt, c, False)[0] - ajuste(gt, c, False)[0].loc[2015])
                        for k, c in [("GWh", "consumo_kWh"), ("S", "suscriptores"), ("kWh_susc", "kWh_suscriptor")]})

    por = v[v.estrato != "total"].groupby(["anio", "estrato"]).agg(
        kwh=("consumo_kWh", "sum"), meses=("mes", "count"), S=("suscriptores", "mean")).reset_index()
    por["GWh"] = por.kwh / por.meses * 12 / 1e6
    por["kWh_susc"] = por.kwh / por.meses / por.S
    bruto = por.pivot(index="anio", columns="estrato", values="kWh_susc")

    # 2) Ajuste por clima
    ef, betas = efectos_anuales(d)
    cambio_aj = {e: 100 * (np.exp(np.log(1 + ef.loc[DESPUES, e] / 100).mean()
                                  - np.log(1 + ef.loc[list(ANTES), e] / 100).mean()) - 1) for e in ef.columns}
    cambio_bruto = (100 * (bruto.loc[DESPUES].mean() / bruto.loc[list(ANTES)].mean() - 1)).to_dict()

    # 3) Precio: COP/kWh del estrato 4 (paga el costo unitario sin subsidio ni contribución), deflactado
    p4 = v[v.estrato == "4"].groupby("anio").apply(lambda x: x.valor_COP.sum() / x.consumo_kWh.sum())
    nivel, fin = {}, 100.0
    for y in sorted(IPC):
        ini = fin; fin = ini * (1 + IPC[y] / 100)
        nivel[y] = (ini * fin) ** 0.5                     # nivel medio del año (aproximación geométrica)
    real = p4 / pd.Series(nivel) * nivel[2015]
    dlnp = np.log(real.loc[DESPUES].mean() / real.loc[list(ANTES)].mean())
    elast = {e: np.log(1 + cambio_aj[e] / 100) / dlnp for e in cambio_aj}
    # 2019 -> 2024: deja fuera la caída de 2016-2019, que ocurrió sin alza real del precio
    dlnp_1924 = np.log(real.loc[2024] / real.loc[2019])
    elast_1924 = {e: np.log((1 + ef.loc[2024, e] / 100) / (1 + ef.loc[2019, e] / 100)) / dlnp_1924 for e in ef.columns}

    hi_anual = clima.groupby(clima.index.year).hi_media.mean()

    # Tablas
    pd.DataFrame({"GWh_anual": tot.GWh.round(0), "suscriptores_medios": tot.S.round(0),
                  "kWh_por_suscriptor": tot.kWh_susc.round(1), "indice_GWh": idx.GWh.round(1),
                  "indice_suscriptores": idx.S.round(1), "indice_kWh_susc": idx.kWh_susc.round(1),
                  "HI_medio_ERA5": hi_anual.reindex(tot.index).round(2),
                  "COP_kWh_E4_nominal": p4.round(0), "COP_kWh_E4_real_2015": real.round(0)}
                 ).to_csv(AQUI / "totales_ciudad.csv", sep=";", decimal=",")
    resumen = pd.DataFrame({"suscriptores_2015": por[por.anio == 2015].set_index("estrato").S.round(0),
                            "suscriptores_2025": por[por.anio == 2025].set_index("estrato").S.round(0),
                            "GWh_2015": por[por.anio == 2015].set_index("estrato").GWh.round(0),
                            "GWh_2025": por[por.anio == 2025].set_index("estrato").GWh.round(0),
                            "cambio_bruto_pct": pd.Series(cambio_bruto).round(1),
                            "cambio_clima_constante_pct": pd.Series(cambio_aj).round(1),
                            "beta_pct_por_C": pd.Series(betas).round(1),
                            "elasticidad_implicita": pd.Series(elast).round(2),
                            "elasticidad_2019_2024": pd.Series(elast_1924).round(2)})
    resumen.to_csv(AQUI / "resumen_por_estrato.csv", sep=";", decimal=",")
    ef.round(1).to_csv(AQUI / "efecto_anual_clima_constante.csv", sep=";", decimal=",")

    print(pd.DataFrame({"GWh": tot.GWh, "S": tot.S, "kWh_susc": tot.kWh_susc, "HI": hi_anual.reindex(tot.index),
                        "E4_nominal": p4, "E4_real": real}).round(1).to_string())
    print(resumen.to_string())
    print("Δln precio real (2015-19 → 2023-25):", round(dlnp, 3), "=", round(100 * (np.exp(dlnp) - 1), 1), "%")
    print(ef.round(1).to_string())

    # Figura: tres paneles, cada uno con un solo eje
    col = {"1": "#2a78d6", "2": "#eb6834", "3": "#1baf7a", "4": "#eda100", "5": "#e87ba4", "6": "#008300"}
    tinta, tinta2, rejilla = "#0b0b0b", "#52514e", "#e4e3df"
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": rejilla, "axes.labelcolor": tinta2,
                         "xtick.color": tinta2, "ytick.color": tinta2, "font.family": "DejaVu Sans"})
    fig, ax = plt.subplots(1, 3, figsize=(13, 4.3))
    anios = tot.index
    for k, (s, nom, c) in enumerate([("GWh", "Consumo total", "#2a78d6"), ("S", "Suscriptores", "#eb6834"),
                                     ("kWh_susc", "kWh por suscriptor", "#1baf7a")]):
        ax[0].plot(anios, idx[s], color=c, lw=2, marker="o", ms=4)
        ax[0].annotate(f"{nom} ({idx[s].iloc[-1]:.0f})", (anios[-1], idx[s].iloc[-1]), xytext=(6, 0),
                       textcoords="offset points", va="center", color=tinta, fontsize=8.5)
    ax[0].axhline(100, color=tinta2, lw=0.8)
    ax[0].set_title("A. Ciudad: índice 2015 = 100 (con efectos de mes)", loc="left", color=tinta, fontsize=10)

    # etiquetas directas separadas al menos 1,4 puntos para que no se encimen
    fin = ef.iloc[-1].sort_values()
    pos, ult = {}, -1e9
    for e, yv in fin.items():
        pos[e] = max(yv, ult + 1.4); ult = pos[e]
    for e in ["1", "2", "3", "4", "5", "6"]:
        ax[1].plot(ef.index, ef[e], color=col[e], lw=2, marker="o", ms=3.5, label=f"E{e}")
        ax[1].annotate(f"E{e} ({ef[e].iloc[-1]:+.0f} %)", (ef.index[-1] + 0.15, pos[e]), va="center",
                       color=tinta, fontsize=8.5)
    ax[1].axhline(0, color=tinta2, lw=0.8)
    ax[1].set_title("B. kWh por suscriptor a clima constante (% frente a 2015)", loc="left", color=tinta, fontsize=10)
    ax[1].legend(ncol=6, fontsize=7.5, frameon=False, loc="lower left", handlelength=1.2, columnspacing=0.8)

    ax[2].plot(real.index, 100 * real / real.loc[2015], color="#2a78d6", lw=2, marker="o", ms=4)
    ax[2].axhline(100, color=tinta2, lw=0.8)
    ax[2].set_title("C. Precio real del kWh, estrato 4 (2015 = 100)", loc="left", color=tinta, fontsize=10)
    for a in ax:
        a.grid(axis="y", color=rejilla, lw=0.6); a.spines[["top", "right"]].set_visible(False)
        a.set_xlim(2014.6, 2027.2); a.set_xticks(range(2015, 2026, 2))
    fig.text(0.01, -0.02, "Fuente: SUI (ele_com_096), Barranquilla urbano; ERA5-Land; IPC del DANE. "
             "Sin meses con bandera ni meses con suscriptores inflados (jun. 2020 y jun. 2021-jul. 2022).",
             fontsize=7.5, color=tinta2)
    fig.tight_layout()
    fig.savefig(AQUI / "caida_consumo.png", dpi=170, bbox_inches="tight", facecolor="#fcfcfb")


if __name__ == "__main__":
    main()
