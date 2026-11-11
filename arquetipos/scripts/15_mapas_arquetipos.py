"""Mapas de los arquetipos: en qué partes de la ciudad está cada uno.

Las viviendas con coordenadas (322.418 de 332.718) se agregan en celdas de 0,0025° (unos 275 m de lado). Cada panel
muestra, en las celdas con 10 viviendas o más, la fracción de sus viviendas que pertenece al arquetipo; las celdas
donde el arquetipo no aparece quedan en gris y las de menos de 10 viviendas no se dibujan. No se dibuja ninguna
vivienda. Si existe la salida del script 14, un tercer mapa muestra la fracción de viviendas de cada celda que cambia
de arquetipo cuando el agrupamiento se ajusta con todos los edificios.

Uso: python scripts/15_mapas_arquetipos.py
Salidas:
  salidas/figuras/mapa_arquetipos_por_vivienda.png
  salidas/figuras/mapa_arquetipos_por_m2.png
  salidas/figuras/mapa_cambios_todos_edificios.png   (solo si existe datos_internos/arquetipos_todos_edificios.parquet)
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, ListedColormap

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.comun import FIGURAS, INTERNOS, POSICIONES, TABLAS, cargar_viviendas  # noqa: E402
from src.estilo import BODY, INK, OCH, PET, guardar  # noqa: E402

CELDA = 0.0025
N_MIN = 10
FONDO = ListedColormap(["#e9e9e9"])
SEQ_PET = LinearSegmentedColormap.from_list("pet", ["#c4e6ec", PET, "#00343d"])
SEQ_OCH = LinearSegmentedColormap.from_list("och", ["#f8d3c6", OCH, "#7a2410"])
ASPECTO = 1 / np.cos(np.radians(10.98))


def numero(x, dec=1):
    return f"{x:,.{dec}f}".replace(",", " ").replace(".", ",")


class Rejilla:
    """Celdas de CELDA grados con al menos N_MIN viviendas."""

    def __init__(self, v):
        self.lon0, self.lat0 = v["lon"].min(), v["lat"].min()
        self.ix = np.floor((v["lon"].to_numpy() - self.lon0) / CELDA).astype(int)
        self.iy = np.floor((v["lat"].to_numpy() - self.lat0) / CELDA).astype(int)
        self.nx, self.ny = self.ix.max() + 1, self.iy.max() + 1
        self.total = self.contar(np.ones(len(v), bool))
        self.valida = self.total >= N_MIN
        self.bordes_x = self.lon0 + np.arange(self.nx + 1) * CELDA
        self.bordes_y = self.lat0 + np.arange(self.ny + 1) * CELDA

    def contar(self, mascara):
        c = np.zeros((self.ny, self.nx))
        np.add.at(c, (self.iy[mascara], self.ix[mascara]), 1)
        return c

    def fraccion(self, mascara):
        f = self.contar(mascara) / np.where(self.valida, self.total, 1)
        return np.ma.masked_where(~self.valida | (f == 0), f)

    def dibujar(self, ax, valores, cmap, vmax=1.0):
        ax.pcolormesh(self.bordes_x, self.bordes_y, np.ma.masked_where(~self.valida, np.zeros_like(self.total)),
                      cmap=FONDO, rasterized=True)
        m = ax.pcolormesh(self.bordes_x, self.bordes_y, valores, cmap=cmap, vmin=0, vmax=vmax, rasterized=True)
        ax.set_aspect(ASPECTO)
        ax.set_xticks([]), ax.set_yticks([])
        for s in ax.spines.values():
            s.set_visible(False)
        return m


def escala(ax, rej, km=2):
    """Barra de escala de `km` kilómetros en la esquina inferior derecha."""
    grados = km / (111.32 * np.cos(np.radians(10.98)))
    x1 = rej.bordes_x[-1] - 0.004
    y = rej.bordes_y[0] + 0.004
    ax.plot([x1 - grados, x1], [y, y], color=INK, lw=1.2, solid_capstyle="butt")
    ax.text(x1 - grados / 2, y + 0.002, f"{km} km", ha="center", va="bottom", fontsize=6, color=INK)


def mapa_solucion(v, rej, sol, ncol):
    perfil = pd.read_csv(TABLAS / f"arquetipos_{sol}.csv")
    perfil["orden"] = perfil["estrato_algoritmo"].str.split("|").str[0].map({p: i for i, p in enumerate(POSICIONES)})
    perfil = perfil.sort_values(["orden", "arquetipo"]).reset_index(drop=True)
    arq = pd.read_parquet(INTERNOS / "arquetipos_final.parquet")[sol].to_numpy()[v.index]
    nfil = int(np.ceil((len(perfil) + 1) / ncol))
    fig, axs = plt.subplots(nfil, ncol, figsize=(16 / 2.54, nfil * 16 / 2.54 / ncol * 1.25))
    axs = axs.ravel()
    for ax, (_, p) in zip(axs, perfil.iterrows()):
        m = rej.dibujar(ax, rej.fraccion(arq == p["arquetipo"]), SEQ_PET)
        pisos = int(p["plantas_mediana"])
        ax.set_title(f"{p['arquetipo']}\n{p['area_mediana']:.0f} m² · {pisos} piso{'s' if pisos > 1 else ''} · "
                     f"{numero(p['pct_viviendas'])} %", fontsize=6.5, color=INK, pad=2, linespacing=1.15)
    for ax in axs[len(perfil):]:
        ax.axis("off")
    leyenda = axs[len(perfil)]
    escala(axs[len(perfil) - 1], rej)
    cax = leyenda.inset_axes([0.08, 0.58, 0.84, 0.08])
    cb = fig.colorbar(m, cax=cax, orientation="horizontal", ticks=[0, 0.25, 0.5, 0.75, 1])
    cb.ax.set_xticklabels(["0", "25", "50", "75", "100"], fontsize=6)
    cb.ax.tick_params(length=2, pad=1)
    cb.outline.set_visible(False)
    cb.ax.xaxis.set_label_position("top")
    cb.set_label("Viviendas de la celda\nen el arquetipo (%)", fontsize=6, color=INK, labelpad=3)
    leyenda.text(0.08, 0.40, "Gris: celdas sin el arquetipo.\nCeldas de ≈ 275 m con\n10 viviendas o más.",
                 fontsize=5.5, color=BODY, transform=leyenda.transAxes, va="top", linespacing=1.3)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.93, bottom=0.01, wspace=0.04, hspace=0.32)
    guardar(fig, FIGURAS / f"mapa_arquetipos_{sol}.png")


def mapa_cambios(v, rej):
    """Casas que cambian de arquetipo (carga por vivienda) si el agrupamiento se ajusta con todos los edificios. Con la
    carga por m² no cambia ninguna vivienda, y en las demás posiciones hay un solo arquetipo por bloque."""
    finales = pd.read_parquet(INTERNOS / "arquetipos_final.parquet")["por_vivienda"].to_numpy()
    todos = pd.read_parquet(INTERNOS / "arquetipos_todos_edificios.parquet")["por_vivienda"].to_numpy()
    casa = (v["posicion"] == "casa").to_numpy()
    cambia = (finales != todos)[v.index]
    n_casa = rej.contar(casa)
    f = rej.contar(cambia & casa) / np.maximum(n_casa, 1)
    f = np.ma.masked_where(~rej.valida | (n_casa < N_MIN) | (f == 0), f)  # gris: ninguna casa cambia o hay menos de 10
    fig, ax = plt.subplots(figsize=(9 / 2.54, 9.6 / 2.54))
    m = rej.dibujar(ax, f, SEQ_OCH, vmax=0.5)
    escala(ax, rej)
    cb = fig.colorbar(m, ax=ax, orientation="horizontal", fraction=0.05, pad=0.02, shrink=0.7, ticks=[0, 0.25, 0.5])
    cb.ax.set_xticklabels(["0", "25", "50 o más"], fontsize=6)
    cb.outline.set_visible(False)
    cb.set_label("Casas de la celda que cambian de arquetipo (%)\nGris: ninguna cambia, o la celda tiene menos de 10 casas",
                 fontsize=6, color=INK)
    print(f"casas que cambian (carga por vivienda): {cambia[casa].mean() * 100:.1f} %")
    guardar(fig, FIGURAS / "mapa_cambios_todos_edificios.png")


def main():
    v = cargar_viviendas()
    v = v[v["tiene_coordenadas"].astype(bool)]
    rej = Rejilla(v)
    print(f"{len(v):,} viviendas con coordenadas en {int(rej.valida.sum()):,} celdas con {N_MIN} o más "
          f"({int(rej.total[rej.valida].sum()):,} viviendas)")
    mapa_solucion(v, rej, "por_vivienda", ncol=6)
    mapa_solucion(v, rej, "por_m2", ncol=4)
    if (INTERNOS / "arquetipos_todos_edificios.parquet").exists():
        mapa_cambios(v, rej)


if __name__ == "__main__":
    main()
