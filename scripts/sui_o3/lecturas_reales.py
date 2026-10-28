"""Consumo residencial de Barranquilla por tipo de lectura (SUI, cubo O3), 2015-2025.

Repite el análisis de `caida_consumo.py` con solo las lecturas reales y mide cuánto del consumo
facturado no viene de un medidor leído (lecturas estimadas y usuarios sin medidor).

Entradas: datos_o3/SUI_O3_Barranquilla_residencial_lectura_2015_2025.csv (de o3_a_csv.py) y el clima de la compuerta.
Uso: python -I lecturas_reales.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from caida_consumo import ANTES, CLIMA, DESPUES, ajuste

AQUI = Path(__file__).resolve().parent
O3 = AQUI / "datos_o3" / "SUI_O3_Barranquilla_residencial_lectura_2015_2025.csv"


def clima_mensual():
    c = pd.read_parquet(CLIMA)
    m = c.groupby([c.index.year, c.index.month]).hi_media.mean()
    m.index.names = ["anio", "mes"]
    m = m.rename("hi_lag").reset_index()
    m["mes"] = m.mes % 12 + 1                    # índice de calor del mes anterior
    m.loc[m.mes == 1, "anio"] += 1
    return m


def serie(o, lecturas):
    """kWh por suscriptor mensual por estrato con las lecturas indicadas; marca meses atípicos."""
    s = o[o.lectura.isin(lecturas)].groupby(["anio", "mes", "estrato"])[["suscriptores", "consumo_kWh"]].sum()
    s = s.reset_index()
    s["kWh_suscriptor"] = s.consumo_kWh / s.suscriptores
    # atípico: lejos de la mediana móvil de 7 meses del mismo estrato, o sin consumo
    s = s.sort_values(["estrato", "anio", "mes"])
    med = s.groupby("estrato").kWh_suscriptor.transform(lambda x: x.rolling(7, center=True, min_periods=3).median())
    r = s.kWh_suscriptor / med
    s["valido"] = (s.consumo_kWh > 0) & r.between(0.75, 1.3)
    return s


def cambios(s, clima):
    d = s[s.valido].merge(clima, on=["anio", "mes"], how="left")
    ef, beta = {}, {}
    for e, g in d.groupby("estrato"):
        ya, beta[e] = ajuste(g, "kWh_suscriptor", True)
        ef[e] = 100 * (np.exp(ya - ya.loc[2015]) - 1)
    ef = pd.DataFrame(ef)
    cam = {e: 100 * (np.exp(np.log(1 + ef.loc[DESPUES, e] / 100).mean()
                            - np.log(1 + ef.loc[list(ANTES), e] / 100).mean()) - 1) for e in ef.columns}
    return ef, pd.Series(cam), pd.Series(beta)


def main():
    o = pd.read_csv(O3, sep=";", keep_default_na=False)
    o = o[o.anio <= 2025]
    clima = clima_mensual()

    # Composición por tipo de lectura (promedio anual de los meses con consumo)
    a = o[o.consumo_kWh > 0].groupby(["anio", "estrato", "lectura"])[["suscriptores", "consumo_kWh"]].sum()
    a = a.unstack("lectura").fillna(0)
    no_real_kwh = 100 * (1 - a["consumo_kWh"]["Real"] / a["consumo_kWh"].sum(axis=1))
    sin_medidor_s = 100 * a["suscriptores"]["No tiene medidor"] / a["suscriptores"].drop(columns="n/a", errors="ignore").sum(axis=1)
    estimada_s = 100 * a["suscriptores"]["Estimada"] / a["suscriptores"].drop(columns="n/a", errors="ignore").sum(axis=1)
    kwh_tipo = (a["consumo_kWh"] / a["suscriptores"]).drop(columns="n/a", errors="ignore")

    # Series: todas las lecturas (sin las cuentas «n/a», que tienen 0 kWh) y solo reales
    todas = serie(o, ["Real", "Estimada", "No tiene medidor"])
    reales = serie(o, ["Real"])
    ef_t, cam_t, beta_t = cambios(todas, clima)
    ef_r, cam_r, beta_r = cambios(reales, clima)

    nivel = reales[reales.valido].groupby(["estrato"]).apply(
        lambda g: pd.Series({p: (g[g.anio.isin(list(a_))].consumo_kWh.sum() / g[g.anio.isin(list(a_))].suscriptores.sum())
                             for p, a_ in [("2015_2019", ANTES), ("2021_2024", range(2021, 2025)), ("2023_2025", DESPUES)]}))
    nivel_t = todas[todas.valido].groupby(["estrato"]).apply(
        lambda g: g[g.anio.isin(range(2021, 2025))].consumo_kWh.sum() / g[g.anio.isin(range(2021, 2025))].suscriptores.sum())

    res = pd.DataFrame({"pct_kWh_no_real_2015_19": no_real_kwh.unstack().loc[list(ANTES)].mean().round(0),
                        "pct_kWh_no_real_2023_25": no_real_kwh.unstack().loc[DESPUES].mean().round(0),
                        "pct_susc_sin_medidor_2025": sin_medidor_s.unstack().loc[2025].round(1),
                        "pct_susc_estimada_2025": estimada_s.unstack().loc[2025].round(1),
                        "kWh_susc_real_2015_19": nivel["2015_2019"].round(0),
                        "kWh_susc_real_2021_24": nivel["2021_2024"].round(0),
                        "kWh_susc_todas_2021_24": nivel_t.round(0),
                        "kWh_susc_real_2023_25": nivel["2023_2025"].round(0),
                        "cambio_clima_const_todas_pct": cam_t.round(1),
                        "cambio_clima_const_reales_pct": cam_r.round(1),
                        "beta_reales_pct_por_C": beta_r.round(1)})
    res.to_csv(AQUI / "resumen_lecturas_reales.csv", sep=";", decimal=",")
    ef_r.round(1).to_csv(AQUI / "efecto_anual_reales.csv", sep=";", decimal=",")
    kwh_tipo.round(0).to_csv(AQUI / "kWh_suscriptor_por_tipo_lectura.csv", sep=";", decimal=",")
    print(res.to_string())
    print("\nkWh por suscriptor-mes por tipo de lectura (2023-2025):")
    print(kwh_tipo.loc[DESPUES].groupby(level="estrato").mean().round(0).to_string())
    print("\nmeses excluidos (reales):", len(reales[~reales.valido]), "de", len(reales))
    print(ef_r.round(1).to_string())

    # Figura: A) % del consumo facturado sin lectura real; B) cambio a clima constante, todas vs reales
    col = {1: "#2a78d6", 2: "#eb6834", 3: "#1baf7a", 4: "#eda100", 5: "#e87ba4", 6: "#008300"}
    tinta, tinta2, rejilla = "#0b0b0b", "#52514e", "#e4e3df"
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": rejilla, "axes.labelcolor": tinta2,
                         "xtick.color": tinta2, "ytick.color": tinta2})
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.3), gridspec_kw={"width_ratios": [1.15, 1]})
    nr = no_real_kwh.unstack()
    fin = nr.iloc[-1].sort_values(); pos, ult = {}, -1e9
    for e, yv in fin.items():
        pos[e] = max(yv, ult + 3.2); ult = pos[e]
    for e in range(1, 7):
        ax[0].plot(nr.index, nr[e], color=col[e], lw=2, marker="o", ms=3.5, label=f"E{e}")
        ax[0].annotate(f"E{e} ({nr[e].iloc[-1]:.0f} %)", (nr.index[-1] + 0.15, pos[e]), va="center", color=tinta, fontsize=8.5)
    ax[0].set_title("A. Consumo facturado sin lectura real (estimado o sin medidor), %", loc="left", color=tinta, fontsize=10)
    ax[0].set_ylim(0, 85); ax[0].set_xlim(2014.6, 2027.3); ax[0].set_xticks(range(2015, 2026, 2))
    ax[0].legend(ncol=6, fontsize=7.5, frameon=False, loc="upper left", handlelength=1.2, columnspacing=0.8)

    x = np.arange(6); w = 0.38
    ax[1].bar(x - w / 2, cam_t.values, w, color="#c9c8c2", label="Todas las lecturas")
    ax[1].bar(x + w / 2, cam_r.values, w, color="#2a78d6", label="Solo lecturas reales")
    for i, (vt, vr) in enumerate(zip(cam_t.values, cam_r.values)):
        ax[1].annotate(f"{vr:+.0f} %", (i + w / 2, vr), xytext=(0, -11 if vr < 0 else 3), textcoords="offset points",
                       ha="center", fontsize=8, color=tinta)
    ax[1].axhline(0, color=tinta2, lw=0.8)
    ax[1].set_ylim(min(cam_t.min(), cam_r.min()) - 4, max(cam_t.max(), cam_r.max(), 0) + 3)
    ax[1].set_xticks(x, [f"E{e}" for e in range(1, 7)])
    ax[1].set_title("B. kWh por suscriptor a clima constante, 2015-19 → 2023-25", loc="left", color=tinta, fontsize=10)
    ax[1].legend(fontsize=8, frameon=False, loc="lower right")
    for a_ in ax:
        a_.grid(axis="y", color=rejilla, lw=0.6); a_.spines[["top", "right"]].set_visible(False)
    fig.text(0.01, -0.02, "Fuente: SUI, cubo O3 VISTA_FACTURACION_ENERGIA (Barranquilla, urbano, residencial), "
             "consultado el 27-oct-2026; ERA5-Land. En B se excluyen las cuentas «n/a» (0 kWh) y los meses atípicos.",
             fontsize=7.5, color=tinta2)
    fig.tight_layout()
    fig.savefig(AQUI / "lecturas_reales.png", dpi=170, bbox_inches="tight", facecolor="#fcfcfb")


if __name__ == "__main__":
    main()
