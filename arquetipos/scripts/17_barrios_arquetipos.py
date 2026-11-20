"""Composición de arquetipos por barrio, para escoger los barrios cuyos consumos se piden a Air-e.

Ubica cada vivienda en un barrio del POT (datos.gov.co, conjunto qui6-qeux, CC BY-SA 4.0) por sus coordenadas y
resume cada barrio: viviendas, estrato más frecuente y fracción de viviendas de cada arquetipo de las dos soluciones.

Uso: python scripts/17_barrios_arquetipos.py
Salidas:
  salidas/tablas/barrios_arquetipos.csv   por barrio: viviendas, estratos y fracción de cada arquetipo (agregados)
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import shapely

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.comun import INTERNOS, RAIZ, TABLAS, cargar_viviendas  # noqa: E402

BARRIOS = RAIZ / "datos_externos" / "barrios_pot" / "barrios_pot_qui6-qeux.geojson"
MIN_VIVIENDAS = 10


def barrios():
    d = json.loads(BARRIOS.read_text(encoding="utf-8"))
    props = pd.DataFrame([f["properties"] for f in d["features"]])
    geoms = np.array([shapely.geometry.shape(f["geometry"]) for f in d["features"]])
    return props, geoms


def ubicar(v, geoms):
    """Índice del barrio que contiene cada vivienda (-1 si ninguno; el primero si hay solapes)."""
    pts = shapely.points(v["lon"].to_numpy(), v["lat"].to_numpy())
    arbol = shapely.STRtree(geoms)
    i_pt, i_b = arbol.query(pts, predicate="within")
    out = np.full(len(v), -1)
    _, primero = np.unique(i_pt, return_index=True)
    out[i_pt[primero]] = i_b[primero]
    return out, np.bincount(i_pt, minlength=len(v))


def main():
    v = cargar_viviendas()
    arq = pd.read_parquet(INTERNOS / "arquetipos_final.parquet")
    props, geoms = barrios()
    con_coord = v["lat"].notna() & v["lon"].notna()
    ib = np.full(len(v), -1)
    veces = np.zeros(len(v), int)
    ib[con_coord.to_numpy()], veces[con_coord.to_numpy()] = ubicar(v[con_coord], geoms)
    print(f"viviendas: {len(v):,}; con coordenadas: {con_coord.sum():,}; en algún barrio: {(ib >= 0).sum():,}; "
          f"en más de uno: {(veces > 1).sum():,}")

    d = pd.DataFrame({"barrio": ib, "estrato": v["estrato_num"].to_numpy(),
                      "por_vivienda": arq["por_vivienda"].astype(str).to_numpy(),
                      "por_m2": arq["por_m2"].astype(str).to_numpy()})
    d = d[d["barrio"] >= 0]
    g = d.groupby("barrio")
    t = pd.DataFrame({"viviendas": g.size(),
                      "estrato_moda": g["estrato"].agg(lambda s: s.mode().iloc[0]),
                      "frac_estrato_moda": g["estrato"].agg(lambda s: s.value_counts(normalize=True).iloc[0])})
    for sol in ["por_vivienda", "por_m2"]:
        f = pd.crosstab(d["barrio"], d[sol], normalize="index").add_prefix(f"{sol}:")
        t = t.join(f)
        t[f"{sol}:dominante"] = f.idxmax(axis=1).str.split(":").str[1]
        t[f"{sol}:frac_dominante"] = f.max(axis=1)
    # Igual que en los mapas, no se publica la composición de barrios con menos de 10 viviendas
    pocas = t["viviendas"] < MIN_VIVIENDAS
    t.loc[pocas, [c for c in t.columns if c != "viviendas"]] = np.nan
    t = props.join(t, how="right").drop(columns="id")
    t.insert(0, "barrio_id", t.index)
    t = t.round(4).sort_values("viviendas", ascending=False)
    t.to_csv(TABLAS / "barrios_arquetipos.csv", index=False, encoding="utf-8-sig")
    print(t[["nombre", "localidad", "viviendas", "estrato_moda", "por_vivienda:dominante",
             "por_vivienda:frac_dominante", "por_m2:dominante", "por_m2:frac_dominante"]].head(40).to_string(index=False))


if __name__ == "__main__":
    main()
