"""¿La caída del consumo por suscriptor es solo de Barranquilla? Comparación con Soledad y Santa Marta (Air-e),
Cartagena (Afinia) y Medellín (EPM), con solo lecturas reales (SUI, cubo O3).

Entrada: datos_o3/SUI_O3_5municipios_residencial_lectura_2015_2025.csv (de o3_a_csv.py).
Uso: python lecturas_reales.py ... (o directamente) python comparacion_municipios.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from caida_consumo import ANTES, DESPUES, IPC, ajuste

AQUI = Path(__file__).resolve().parent
O3 = AQUI / "datos_o3" / "SUI_O3_5municipios_residencial_lectura_2015_2025.csv"
NOMBRE = {"BARRANQUILLA": "Barranquilla", "SOLEDAD": "Soledad", "SANTA MARTA": "Santa Marta",
          "CARTAGENA DE INDIAS": "Cartagena", "MEDELLIN": "Medellín"}
COL = {"Barranquilla": "#2a78d6", "Soledad": "#eb6834", "Santa Marta": "#1baf7a", "Cartagena": "#eda100",
       "Medellín": "#e87ba4"}
GRUPOS = {"E1-E3": [1, 2, 3], "E4-E6": [4, 5, 6]}
MIN_SUSC = 1000


def indice_anual(s):
    """Índice anual (2015 = 100) de kWh por suscriptor con efectos de mes; s tiene anio, mes, kWh_suscriptor."""
    ya, _ = ajuste(s, "kWh_suscriptor", False)
    return 100 * np.exp(ya - ya.loc[2015])


def main():
    o = pd.read_csv(O3, sep=";", keep_default_na=False)
    o = o[(o.anio <= 2025)]
    o["ciudad"] = o.municipio.map(NOMBRE)
    r = o[(o.lectura == "Real") & (o.consumo_kWh > 0)]

    # índices por grupo de estratos (suma de kWh / suma de suscriptores reales), excluyendo meses atípicos
    filas, tabla = {}, []
    for (c, gnom), g in [((c, gn), r[(r.ciudad == c) & r.estrato.isin(es)]) for c in NOMBRE.values()
                         for gn, es in GRUPOS.items()]:
        s = g.groupby(["anio", "mes"])[["consumo_kWh", "suscriptores"]].sum().reset_index()
        # con menos de 1.000 suscriptores con lectura real la serie es ruido (Soledad en E4-E6)
        if s.empty or s.suscriptores.mean() < MIN_SUSC:
            continue
        s["kWh_suscriptor"] = s.consumo_kWh / s.suscriptores
        med = s.kWh_suscriptor.rolling(7, center=True, min_periods=3).median()
        s = s[(s.kWh_suscriptor / med).between(0.75, 1.3)]
        idx = indice_anual(s)
        filas[(c, gnom)] = idx
        cambio = 100 * (np.exp(np.log(idx.loc[DESPUES] / 100).mean() - np.log(idx.loc[list(ANTES)] / 100).mean()) - 1)
        nivel = s[s.anio.isin(DESPUES)].consumo_kWh.sum() / s[s.anio.isin(DESPUES)].suscriptores.sum()
        tabla.append(dict(ciudad=c, grupo=gnom, cambio_pct_2015_19_a_2023_25=round(cambio, 1),
                          kWh_susc_real_2023_25=round(nivel, 0)))
    tabla = pd.DataFrame(tabla)

    # cambio por estrato (solo lecturas reales)
    por = []
    for (c, e), g in r.groupby(["ciudad", "estrato"]):
        s = g.groupby(["anio", "mes"])[["consumo_kWh", "suscriptores"]].sum().reset_index()
        s["kWh_suscriptor"] = s.consumo_kWh / s.suscriptores
        med = s.kWh_suscriptor.rolling(7, center=True, min_periods=3).median()
        s = s[(s.kWh_suscriptor / med).between(0.75, 1.3)]
        if s.anio.nunique() < 10 or s.suscriptores.mean() < 300:
            continue
        idx = indice_anual(s)
        por.append(dict(ciudad=c, estrato=e, cambio=round(100 * (np.exp(np.log(idx.loc[DESPUES] / 100).mean()
                                                                       - np.log(idx.loc[list(ANTES)] / 100).mean()) - 1), 1)))
    por = pd.DataFrame(por).pivot(index="ciudad", columns="estrato", values="cambio")

    # % del consumo facturado sin lectura real, por grupo de estratos
    nr = []
    for (c, gn), g in [((c, gn), o[(o.ciudad == c) & o.estrato.isin(es) & (o.consumo_kWh > 0)]) for c in NOMBRE.values()
                       for gn, es in GRUPOS.items()]:
        t = g.groupby(["anio", "lectura"]).consumo_kWh.sum().unstack().fillna(0)
        if t.empty or "Real" not in t:
            continue
        p = 100 * (1 - t["Real"] / t.sum(axis=1))
        nr.append(dict(ciudad=c, grupo=gn, no_real_2015_19=round(p.loc[list(ANTES)].mean(), 0),
                       no_real_2023_25=round(p.loc[DESPUES].mean(), 0)))
    nr = pd.DataFrame(nr)

    # precio real del kWh del estrato 4 por ciudad (IPC nacional)
    nivel, fin = {}, 100.0
    for y in sorted(IPC):
        ini = fin; fin = ini * (1 + IPC[y] / 100); nivel[y] = (ini * fin) ** 0.5
    e4 = o[(o.estrato == 4) & (o.consumo_kWh > 0)].groupby(["ciudad", "anio"])[["fact_consumo_COP", "consumo_kWh"]].sum()
    precio = (e4.fact_consumo_COP / e4.consumo_kWh).unstack("ciudad")
    susc_e4 = r[r.estrato == 4].groupby(["ciudad", "anio", "mes"]).suscriptores.sum().groupby("ciudad").mean()
    precio = precio[[c for c in precio.columns if susc_e4.get(c, 0) >= MIN_SUSC]]
    real = precio.div(pd.Series(nivel), axis=0) * nivel[2015]
    real_idx = 100 * real / real.loc[2015]

    tabla = tabla.merge(nr, on=["ciudad", "grupo"], how="left")
    tabla.to_csv(AQUI / "comparacion_municipios.csv", sep=";", decimal=",", index=False)
    por.to_csv(AQUI / "comparacion_municipios_por_estrato.csv", sep=";", decimal=",")
    real_idx.round(0).to_csv(AQUI / "precio_real_E4_municipios.csv", sep=";", decimal=",")
    print(tabla.to_string(index=False))
    print("\nCambio por estrato, solo lecturas reales (%, 2015-19 → 2023-25, con efectos de mes):")
    print(por.to_string())
    print("\nPrecio real del kWh del estrato 4 (2015 = 100):")
    print(real_idx.round(0).to_string())

    # Figura
    tinta, tinta2, rejilla = "#0b0b0b", "#52514e", "#e4e3df"
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": rejilla, "xtick.color": tinta2, "ytick.color": tinta2})
    fig, ax = plt.subplots(1, 3, figsize=(14, 4.3))
    for k, gn in enumerate(GRUPOS):
        fins = {c: filas[(c, gn)].iloc[-1] for c in NOMBRE.values() if (c, gn) in filas}
        rango = max(s.max() for (cc, gg), s in filas.items() if gg == gn) - min(s.min() for (cc, gg), s in filas.items() if gg == gn)
        pos, ult = {}, -1e9
        for c, yv in sorted(fins.items(), key=lambda x: x[1]):
            pos[c] = max(yv, ult + 0.045 * rango); ult = pos[c]
        for c in NOMBRE.values():
            if (c, gn) not in filas:
                continue
            s = filas[(c, gn)]
            ax[k].plot(s.index, s.values, color=COL[c], lw=2, marker="o", ms=3, label=c)
            ax[k].annotate(c, (s.index[-1] + 0.15, pos[c]), va="center", fontsize=8, color=tinta)
        ax[k].axhline(100, color=tinta2, lw=0.8)
        ax[k].set_title(f"{'AB'[k]}. kWh por suscriptor, lecturas reales, {gn} (2015 = 100)", loc="left",
                        color=tinta, fontsize=9.5)
    for c in [c for c in NOMBRE.values() if c in real_idx.columns]:
        ax[2].plot(real_idx.index, real_idx[c], color=COL[c], lw=2, marker="o", ms=3, label=c)
    ax[2].axhline(100, color=tinta2, lw=0.8)
    ax[2].set_title("C. Precio real del kWh, estrato 4 (2015 = 100)", loc="left", color=tinta, fontsize=9.5)
    ax[2].legend(fontsize=7.5, frameon=False, loc="upper left")
    for a in ax:
        a.grid(axis="y", color=rejilla, lw=0.6); a.spines[["top", "right"]].set_visible(False)
        a.set_xticks(range(2015, 2026, 2))
    ax[0].set_xlim(2014.6, 2027.6); ax[1].set_xlim(2014.6, 2027.6)
    fig.text(0.01, -0.02, "Fuente: SUI, cubo O3 VISTA_FACTURACION_ENERGIA (urbano, residencial), consultado el 27-oct-2026; "
             "IPC del DANE. Sin ajuste por clima; meses atípicos excluidos.", fontsize=7.5, color=tinta2)
    fig.tight_layout()
    fig.savefig(AQUI / "comparacion_municipios.png", dpi=170, bbox_inches="tight", facecolor="#fcfcfb")


if __name__ == "__main__":
    main()
