"""Cobertura temporal de las bases de datos de la tesis (figura del capítulo «Bases de datos de la tesis»).

Las fechas salen de los capítulos de cada base y de los archivos crudos (primer y último registro).
Uso:  python scripts/eda/panorama.py
"""
import sys
from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent))
from estilo import PAL, TXT2, guardar, titulo  # noqa: E402

# (base, tipo, tramos continuos [(inicio, fin)], puntos sueltos, nota)
BASES = [
    ("ECV (DANE)", "encuesta", [], [date(a, 7, 1) for a in (2018, 2019, 2021, 2022, 2023, 2024, 2025)],
     "olas anuales, sin 2020"),
    ("ENUT (DANE)", "encuesta", [(date(2024, 9, 1), date(2025, 9, 30))], [], "sep. 2024 – sep. 2025"),
    ("GEIH (DANE)", "encuesta", [(date(2024, 1, 1), date(2024, 12, 31))], [], "2024 (9 meses en disco)"),
    ("SUI consolidado", "registro", [(date(2015, 1, 1), date(2026, 8, 31))], [], "mensual"),
    ("SUI por tipo de lectura (O3)", "registro", [(date(2015, 1, 1), date(2025, 12, 31))], [], "mensual"),
    ("Catastro", "registro", [], [date(2026, 9, 17), date(2026, 9, 27), date(2026, 11, 3)], "descargas de 2026"),
    ("XM", "registro", [(date(2015, 1, 1), date(2026, 10, 13))], [], "horaria"),
    ("ERA5-Land (GDEX)", "reanálisis", [(date(2015, 1, 1), date(2026, 9, 30))], [], "horaria"),
    ("Open-Meteo", "reanálisis", [(date(2015, 1, 1), date(2026, 9, 30))], [], "horaria, contraste"),
    ("IDEAM 0029045190", "medición", [(date(2015, 1, 1), date(2026, 10, 17))], [], "horaria, contraste"),
    ("ONI (NOAA)", "índice", [(date(2015, 1, 1), date(2026, 9, 30))], [], "mensual (serie desde 1950)"),
    ("CEELA", "documento", [], [date(2025, 8, 1)], "informe de 2025"),
]
COLOR = {"encuesta": PAL[0], "registro": PAL[1], "reanálisis": PAL[2], "medición": PAL[3], "índice": PAL[6],
         "documento": PAL[4]}


def main():
    fig, ax = plt.subplots(figsize=(10, 6.2))
    for i, (nombre, tipo, tramos, puntos, nota) in enumerate(BASES):
        y = len(BASES) - 1 - i
        c = COLOR[tipo]
        for a, b in tramos:
            ax.plot([a, b], [y, y], color=c, lw=7, solid_capstyle="butt")
        if puntos:
            ax.scatter(puntos, [y] * len(puntos), color=c, s=60, zorder=3, edgecolor="white", lw=1)
        ax.text(date(2027, 3, 1), y, nota, va="center", fontsize=8.5, color=TXT2)
    ax.axvspan(date(2020, 1, 1), date(2020, 12, 31), color="#efeee9", zorder=0, lw=0)
    ax.text(date(2020, 7, 1), -0.55, "2020 (pandemia)", ha="center", fontsize=8.5, color=TXT2)
    ax.set_yticks(range(len(BASES)))
    ax.set_yticklabels([b[0] for b in BASES][::-1])
    ax.set_xlim(date(2014, 9, 1), date(2029, 6, 1))
    ax.set_ylim(-0.7, len(BASES) - 0.1)
    ax.grid(axis="y", visible=False)
    for tipo, c in COLOR.items():
        ax.plot([], [], color=c, lw=7, label=tipo)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.08), ncols=6, fontsize=9)
    titulo(ax, "Periodo que cubre cada base de datos", "Barras: series continuas; puntos: olas o cortes únicos")
    guardar(fig, "panorama_cobertura.png", "Fuente: archivos crudos y capítulos de cada base.")


if __name__ == "__main__":
    main()
