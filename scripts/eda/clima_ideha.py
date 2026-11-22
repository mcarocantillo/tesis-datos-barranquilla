"""Figura y tablas del contraste con la estación IDEHA-01 de Uninorte (capítulo «Clima horario»).

Lee las salidas agregadas de fase2/clima/scripts/09_contraste_ideha.py y, como referencia, calcula el sesgo de
ERA5-Land frente al IDEAM por hora con los años en que la hora del IDEAM es local (2015 a octubre de 2024).
Uso:  python scripts/eda/clima_ideha.py
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from estilo import ML, PAL, TXT2, guardar, tabla, titulo  # noqa: E402

CLIMA = ML / "fase2" / "clima" / "salidas"
IDEAM = ML / "compuerta_horaria" / "datos" / "procesados" / "ideam_horario.parquet"
CELDA = "ERA5-Land 74,8 O"


def sesgo_ideam():
    """ERA5-Land − IDEAM por hora en 2015 a octubre de 2024, antes de que la serie del IDEAM pase a hora UTC."""
    s = pd.read_parquet(CLIMA / "clima_horario_barranquilla.parquet")
    i = pd.read_parquet(IDEAM).loc[:"2024-10-31"]
    return pd.DataFrame({"T": (s["T"] - i["t_ideam"]).dropna().groupby(lambda t: t.hour).mean(),
                         "HI": (s["HI"] - i["hi_ideam"]).dropna().groupby(lambda t: t.hour).mean()})


def main():
    lim = pd.read_csv(CLIMA / "contraste_ideha_hora_limpio.csv", index_col=0)
    cor = pd.read_csv(CLIMA / "contraste_ideha_hora_corregido.csv", index_col=0)
    rad = pd.read_csv(CLIMA / "contraste_ideha_radiacion_limpio.csv", index_col=0)
    res = pd.concat([pd.read_csv(CLIMA / f"contraste_ideha_resumen_{m}.csv").assign(periodo=m)
                     for m in ["limpio", "corregido"]])
    ide = sesgo_ideam()

    fig, ax = plt.subplots(2, 2, figsize=(11.5, 8.4))
    for k, (var, nombre) in enumerate([("T", "Temperatura"), ("HI", "Índice de calor")]):
        a = ax[0, k]
        a.axhline(0, color="#9a9993", lw=.8)
        a.plot(lim.index, lim[f"{var} | {CELDA}"], color=PAL[0], lw=2.2, marker="o", ms=3,
               label="frente a IDEHA-01, jun.–sep. 2026 (reloj correcto)")
        a.plot(cor.index, cor[f"{var} | {CELDA}"], color=PAL[0], lw=1.4, ls="--",
               label="frente a IDEHA-01, may. 2025–sep. 2026 (reloj corregido)")
        a.plot(ide.index, ide[var], color=PAL[1], lw=2, marker="s", ms=3, label="frente al IDEAM, 2015–oct. 2024")
        a.set(xlabel="Hora local", ylabel="ERA5-Land − estación (°C)", xticks=range(0, 24, 3))
        titulo(a, f"({'ab'[k]}) {nombre}")
        if k == 0:
            a.legend(fontsize=8, loc="lower left")
    a = ax[1, 0]
    for c, col, et in [("IDEHA", "#0b0b0b", "IDEHA-01"), ("ERA5-Land", PAL[0], "ERA5-Land (GDEX)"),
                       ("ERA5", PAL[4], "ERA5 (Open-Meteo)")]:
        a.plot(rad.index - 0.5, rad[c], color=col, lw=2, label=et)
    a.set(xlabel="Hora local (centro de la hora)", ylabel="W/m²", xticks=range(0, 24, 3))
    titulo(a, "(c) Radiación global media, jun.–sep. 2026")
    a.legend(fontsize=8)
    a = ax[1, 1]
    v = res[(res.variable == "viento") & (res.periodo == "corregido")].set_index("fuente")
    nombres = ["IDEHA-01 (sensor)", CELDA, "ERA5-Land 74,9 O", "ERA5 (Open-Meteo)"]
    valores = [v["media_ideha"].iloc[0]] + [v.loc[n, "media_fuente"] for n in nombres[1:]]
    a.bar(range(4), valores, color=["#0b0b0b", PAL[0], PAL[2], PAL[4]])
    for x, y in enumerate(valores):
        a.text(x, y + 0.1, f"{y:.1f}".replace(".", ","), ha="center", fontsize=9)
    a.set_xticks(range(4))
    a.set_xticklabels(["IDEHA-01\n(sensor)", "ERA5-Land\n74,8 O", "ERA5-Land\n74,9 O", "ERA5\n(Open-Meteo)"], fontsize=9)
    a.set(ylabel="m/s")
    titulo(a, "(d) Viento medio, may. 2025–sep. 2026")
    guardar(fig, "clima_ideha.png", "Fuente: estación IDEHA-01 (Uninorte), ERA5-Land de GDEX, Open-Meteo e IDEAM 0029045190.")

    tabla(res.round(3), "clima_ideha_resumen.csv", index=False)
    tabla(pd.concat({"limpio": lim, "corregido": cor}, axis=1).round(3), "clima_ideha_hora.csv")
    tabla(ide.round(3), "clima_ideha_sesgo_ideam_2015_2024.csv")
    print(ide.round(2).T.to_string())


if __name__ == "__main__":
    main()
