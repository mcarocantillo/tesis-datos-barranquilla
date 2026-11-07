"""Estilo común de las figuras del EDA (el mismo de scripts/figuras.py): paleta fija por estrato, rutas y formato."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
DESCARGAS = REPO.parents[1]                       # C:/Users/.../Downloads
ML = REPO.parent                                  # C:/Users/.../Downloads/ml_trabajo
FIG = REPO / "figuras" / "eda"
TAB = REPO / "tablas" / "eda"
SEMILLA = 42

PAL = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
EST = {f"E{i + 1}": PAL[i] for i in range(6)}
TXT, TXT2, GRID = "#0b0b0b", "#52514e", "#e4e3df"

plt.rcParams.update({
    "font.size": 11, "font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#9a9993", "axes.labelcolor": TXT2, "xtick.color": TXT2, "ytick.color": TXT2,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": .8, "axes.axisbelow": True,
    "axes.titlelocation": "left", "axes.titlesize": 13, "axes.titlecolor": TXT, "legend.frameon": False,
    "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "axes.formatter.use_locale": False,
})


def fmt(v, d=1):
    """Número con coma decimal y punto de miles, como en el resto del libro."""
    s = f"{v:,.{d}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def titulo(ax, t, s=None):
    ax.set_title(t, pad=22 if s else 8, fontweight="bold")
    if s:
        ax.text(0, 1.02, s, transform=ax.transAxes, fontsize=10, color=TXT2)


def guardar(fig, nombre, fuente=None):
    """Guarda la figura en figuras/eda/ con la fuente abajo a la izquierda."""
    FIG.mkdir(parents=True, exist_ok=True)
    if fuente:
        fig.text(0.012, 0.012, fuente, fontsize=8.5, color=TXT2)
    fig.tight_layout(rect=(0, 0.03 if fuente else 0, 1, 1))
    fig.savefig(FIG / nombre, dpi=160)
    plt.close(fig)


def tabla(df, nombre, **kw):
    """Guarda una tabla agregada en tablas/eda/ con «;» y UTF-8 con BOM, como las demás tablas del repositorio."""
    TAB.mkdir(parents=True, exist_ok=True)
    df.to_csv(TAB / nombre, sep=";", encoding="utf-8-sig", **kw)
