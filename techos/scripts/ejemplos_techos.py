"""Figuras de ejemplo del piloto de techos: unión de polígonos por predio, máscara de árboles y sombra, tono y color.

Uso: python ejemplos_techos.py <carpeta piloto_techos extraída> <carpeta de salida>
Requiere numpy, shapely 2, tifffile, Pillow y matplotlib. Usa la misma regla que la sección 3 del notebook.
"""
import json, colorsys
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import shape
from PIL import Image, ImageDraw
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPoly

import sys
import tifffile

R = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('datos_crudos/piloto_techos')
SAL = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('figuras')
SAL.mkdir(exist_ok=True)
ZONAS = ["e1_carrizal", "e2_el_milagro", "e3_cevillar", "e4_el_recreo", "e5_el_prado", "e6_el_golf"]
RGB, ROJO, NIR = (4, 2, 1), 4, 6
MIN_M2 = 20
UMBRAL_NDVI, UMBRAL_SOMBRA = 0.3, 0.07
BORDE_M = 0.7   # se usan solo los píxeles interiores, a 0,7 m del borde, por si el polígono está corrido


def leer(z):
    """Imagen de 8 bandas (8, H, W) y su georreferenciación (tamaño de píxel y esquina superior izquierda)."""
    with tifffile.TiffFile(R / z / "wv2026_8b.tif") as t:
        a = t.asarray()
        tags = {k.name: k.value for k in t.pages[0].tags.values()}
    if a.shape[-1] == 8:
        a = np.moveaxis(a, -1, 0)
    sc, tp = tags["ModelPixelScaleTag"], tags["ModelTiepointTag"]
    return a.astype("float32"), {"a": sc[0], "e": -sc[1], "c": tp[3], "f": tp[4]}


img, T = {}, {}
for z in ZONAS:
    img[z], T[z] = leer(z)
todo = np.concatenate([img[z].reshape(8, -1) for z in ZONAS], axis=1)
P2, P98 = np.percentile(todo, 2, axis=1), np.percentile(todo, 98, axis=1)
esc = {z: np.clip((img[z] - P2[:, None, None]) / (P98 - P2)[:, None, None], 0, 1) for z in ZONAS}
rgb = {z: np.dstack([esc[z][i] for i in RGB]) for z in ZONAS}


def a_px(geom, t):
    polis = geom.geoms if geom.geom_type == "MultiPolygon" else [geom]
    return [[((x - t["c"]) / t["a"], (y - t["f"]) / t["e"]) for x, y in p.exterior.coords] for p in polis]


def rasterizar(geoms, t, H=588, W=588):
    im = Image.new("I", (W, H), 0)
    d = ImageDraw.Draw(im)
    for i, g in enumerate(geoms, 1):
        for xy in a_px(g, t):
            d.polygon(xy, fill=i)
    return np.array(im)


def unir_por_predio(feats):
    """Une las construcciones que se tocan y son del mismo terreno (21 primeros dígitos del número predial)."""
    grupos = {}
    for f in feats:
        grupos.setdefault(str(f["properties"]["local_id"])[:21], []).append(shape(f["geometry"]))
    out = []
    for gs in grupos.values():
        u = shapely.union_all([g.buffer(0.3) for g in gs]).buffer(-0.3)
        out += list(u.geoms) if u.geom_type == "MultiPolygon" else [u]
    return [g for g in out if not g.is_empty]


def nombre_color(r, g, b):
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    h *= 360
    if v > 0.72 and s < 0.18: return "blanco o claro"
    if (h < 20 or h > 345) and s > 0.35 and v > 0.3: return "rojo o terracota"
    if 75 <= h < 165 and s > 0.15 and v > 0.3: return "verde"
    if 165 <= h < 255 and s > 0.15 and v > 0.3: return "azul"
    if 15 <= h < 60 and (s > 0.2 or (v < 0.4 and s > 0.1)): return "marrón o beige"
    return "gris claro" if v > 0.45 else "gris oscuro"


COLORES = {"blanco o claro": "#f4f4f4", "gris claro": "#a8adb3", "gris oscuro": "#3b3b3b", "marrón o beige": "#8b5a2b",
           "rojo o terracota": "#c0502b", "verde": "#3e8e41", "azul": "#3c78d8"}

techos, resumen = [], []
for z in ZONAS:
    feats = json.load(open(R / z / "construcciones.geojson", encoding="utf-8"))["features"]
    orig = [shape(f["geometry"]) for f in feats]
    unidos = unir_por_predio(feats)
    a0, a1 = np.array([g.area for g in orig]), np.array([g.area for g in unidos])
    resumen.append((z, len(orig), int((a0 < MIN_M2).sum()), len(unidos), int((a1 < MIN_M2).sum())))
    t, e = T[z], esc[z]
    ndvi = (img[z][NIR] - img[z][ROJO]) / (img[z][NIR] + img[z][ROJO] + 1e-6)
    brillo = (e[RGB[0]] + e[RGB[1]] + e[RGB[2]]) / 3
    veg = ndvi > UMBRAL_NDVI
    sombra = (brillo < UMBRAL_SOMBRA) & (e[NIR] < 0.12) & ~veg
    grandes = [g for g in unidos if g.area >= MIN_M2]
    ids = rasterizar([g.buffer(-BORDE_M) if not g.buffer(-BORDE_M).is_empty else g for g in grandes], t)
    for i, g in enumerate(grandes, 1):
        m = ids == i
        n = m.sum()
        if n < 30: continue
        vis = m & ~veg & ~sombra
        fvis = vis.sum() / n
        if fvis < 0.5:
            tono, color, med = "no visible", "no visible", None
        else:
            med = np.median(rgb[z][vis], axis=0)
            b = float(np.median(brillo[vis]))
            tono = "claro" if b > 0.55 else ("oscuro" if b < 0.30 else "medio")
            color = nombre_color(*med)
        techos.append(dict(zona=z, geom=g, n=n, fvis=fvis, fveg=(m & veg).sum() / n, fsom=(m & sombra).sum() / n,
                           tono=tono, color=color))
    esc[z + "_veg"], esc[z + "_som"] = veg, sombra

print("zona, construcciones, <20 m2, techos unidos, <20 m2")
for r in resumen: print(r)
import collections
print(collections.Counter(t_["tono"] for t_ in techos))
print(collections.Counter(t_["color"] for t_ in techos))


def recorte(t_, margen=6, atenuar=True):
    z, g = t_["zona"], t_["geom"]
    t = T[z]
    x0, y0, x1, y1 = g.bounds
    c0, c1 = int((x0 - margen - t["c"]) / t["a"]), int((x1 + margen - t["c"]) / t["a"]) + 1
    r0, r1 = int((y1 + margen - t["f"]) / t["e"]), int((y0 - margen - t["f"]) / t["e"]) + 1
    c0, r0 = max(c0, 0), max(r0, 0)
    a = rgb[z][r0:r1, c0:c1].copy()
    return a, (c0, r0)


def dibujar_poli(ax, g, t, off, color, lw=1.5):
    for xy in a_px(g, t):
        ax.add_patch(MplPoly([(x - off[0], y - off[1]) for x, y in xy], fill=False, ec=color, lw=lw))


# Figura 1: unión de polígonos en una manzana de El Milagro
z = "e2_el_milagro"; t = T[z]
feats = json.load(open(R / z / "construcciones.geojson", encoding="utf-8"))["features"]
orig = [shape(f["geometry"]) for f in feats]
unidos = unir_por_predio(feats)
cx, cy = 4804007 - 25, 2766743 + 20
caja = shapely.box(cx - 30, cy - 30, cx + 30, cy + 30)
c0, r0 = int((cx - 30 - t["c"]) / t["a"]), int((cy + 30 - t["f"]) / t["e"])
c1, r1 = int((cx + 30 - t["c"]) / t["a"]), int((cy - 30 - t["f"]) / t["e"])
fig, ax = plt.subplots(1, 2, figsize=(12, 6.2))
for a_, polis, col, tit in [(ax[0], orig, "yellow", "Antes: construcciones del catastro"),
                            (ax[1], unidos, "cyan", "Después: unidas por predio")]:
    a_.imshow(rgb[z][r0:r1, c0:c1])
    for g in polis:
        if g.intersects(caja):
            dibujar_poli(a_, g, t, (c0, r0), col, 1.4 if g.area >= MIN_M2 else 0.8)
            if g.area < MIN_M2 and g.within(caja):
                p = g.representative_point()
                a_.plot((p.x - t["c"]) / t["a"] - c0, (p.y - t["f"]) / t["e"] - r0, "r.", ms=7)
    a_.set_xlim(0, c1 - c0); a_.set_ylim(r1 - r0, 0); a_.set_title(tit); a_.axis("off")
fig.suptitle("El Milagro, 60 × 60 m. Punto rojo: polígono de menos de 20 m²", fontsize=11)
plt.tight_layout(rect=(0, 0, 1, 0.95)); plt.savefig(SAL / "1_union_poligonos.png", dpi=130); plt.close()

# Figura 2: máscara de árboles y sombra en Cevillar y El Golf
fig, ax = plt.subplots(2, 2, figsize=(12, 12))
for fila, z in enumerate(["e3_cevillar", "e6_el_golf"]):
    sl = (slice(150, 450), slice(150, 450))
    ax[fila, 0].imshow(rgb[z][sl]); ax[fila, 0].set_title(f"{z[3:].replace('_', ' ').title()}: color natural")
    over = rgb[z][sl].copy()
    over[esc[z + "_veg"][sl]] = [0.2, 0.85, 0.2]
    over[esc[z + "_som"][sl]] = [0.75, 0.2, 0.85]
    ax[fila, 1].imshow(over); ax[fila, 1].set_title("Verde: árboles (NDVI). Morado: sombra")
    for a_ in ax[fila]: a_.axis("off")
plt.tight_layout(); plt.savefig(SAL / "2_sombra_arboles.png", dpi=110); plt.close()

# Figura 3: ejemplos por tono y por color
rng = np.random.default_rng(42)


def grilla(campo, clases, archivo, titulo, n=7):
    fig, ax = plt.subplots(len(clases), n, figsize=(2 * n, 2.1 * len(clases)))
    for r, c in enumerate(clases):
        cand = [t_ for t_ in techos if t_[campo] == c and t_["n"] > 120]
        sel = [cand[i] for i in rng.permutation(len(cand))[:n]]
        for j in range(n):
            a_ = ax[r, j]; a_.axis("off")
            if j < len(sel):
                im, off = recorte(sel[j])
                a_.imshow(im); dibujar_poli(a_, sel[j]["geom"], T[sel[j]["zona"]], off, "yellow", 1)
        ax[r, 0].set_title(f"{c} ({len(cand)})", loc="left", fontsize=10)
    fig.suptitle(titulo, fontsize=12)
    plt.tight_layout(); plt.savefig(SAL / archivo, dpi=110); plt.close()


grilla("tono", ["claro", "medio", "oscuro", "no visible"], "3_ejemplos_tono.png",
       "Tono según el brillo de los píxeles visibles (automático, sin etiquetas)")
grilla("color", [c for c in COLORES if any(t_["color"] == c for t_ in techos)] + ["no visible"], "4_ejemplos_color.png",
       "Color según el color mediano de los píxeles visibles (automático, sin etiquetas)")

# Figura 5: mapa de colores, demostración
fig, ax = plt.subplots(2, 3, figsize=(16, 11))
for a_, z in zip(ax.ravel(), ZONAS):
    t = T[z]
    a_.imshow(rgb[z] * 0.55)
    for t_ in techos:
        if t_["zona"] != z: continue
        col = COLORES.get(t_["color"], "#00000000") if t_["color"] != "no visible" else "#ff00ff"
        for xy in a_px(t_["geom"], t):
            a_.add_patch(MplPoly(xy, fc=col, ec="yellow", lw=0.3, alpha=0.9 if t_["color"] != "no visible" else 0.35))
    a_.set_title(z[3:].replace("_", " ").title()); a_.axis("off")
from matplotlib.patches import Patch
fig.legend([Patch(fc=v) for v in COLORES.values()] + [Patch(fc="#ff00ff", alpha=0.35)], list(COLORES) + ["no visible"],
           loc="lower center", ncol=8, fontsize=10)
fig.suptitle("Color de los techos estimado desde la ortoimagen WorldView 2026 y las construcciones del catastro", fontsize=13)
plt.tight_layout(rect=(0, 0.04, 1, 0.97), h_pad=2.5); plt.savefig(SAL / "5_mapa_colores_demo.png", dpi=110); plt.close()
print("ok")
