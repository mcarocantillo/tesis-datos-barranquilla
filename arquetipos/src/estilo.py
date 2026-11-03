"""Estilo de figuras de la propuesta: Palatino y paleta turquesa/coral (figuras_propuesta/figuras_propuesta.py)."""
import os

import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

for f in ["pala.ttf", "palab.ttf", "palai.ttf", "palabi.ttf"]:
    ruta = os.path.join(r"C:\Windows\Fonts", f)
    if os.path.exists(ruta):
        fm.fontManager.addfont(ruta)
FONT = "Palatino Linotype"

INK = "#222222"
BODY = "#4a4a4a"
GREY = "#8c8c8c"
PET = "#00879e"
OCH = "#e4572e"
PAPER = "#fbeee0"
PALE = "#dff1f4"

plt.rcParams.update({"font.family": FONT, "font.size": 8, "axes.edgecolor": INK, "axes.labelcolor": INK,
                     "xtick.color": INK, "ytick.color": INK, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.formatter.use_locale": False, "mathtext.fontset": "custom", "mathtext.rm": FONT})


def lienzo(ancho_cm, alto_cm):
    return plt.subplots(figsize=(ancho_cm / 2.54, alto_cm / 2.54), constrained_layout=True)


def guardar(fig, ruta):
    fig.savefig(ruta, dpi=400, facecolor="white")
    plt.close(fig)
