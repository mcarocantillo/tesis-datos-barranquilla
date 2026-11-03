"""Tipología por reglas (referencia del Paso 4) y su variante con clases de tamaño (Nota 2 del preregistro).

Base:     tipo × posición × época × bloque de estratos.
Variante: tipo × posición × época × tamaño × bloque de estratos (sensibilidad; no decide).

Aplica las reglas de preregistro/decision_fase1.json: asignación de las viviendas sin época, tamaño mínimo de
celda y fusión por etapas. Salidas (sufijo «_tamano» para la variante):
  datos_internos/tipologia_reglas.parquet    arquetipo de cada vivienda (microdato, no se publica)
  salidas/tablas/reglas_celdas_iniciales.csv celdas posibles antes de fusionar
  salidas/tablas/reglas_fusiones.csv         registro de cada fusión
  salidas/tablas/reglas_arquetipos.csv       arquetipos finales con sus agregados
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.comun import (BLOQUES, DECISION, EPOCAS, INTERNOS, POSICIONES, TABLAS, TIPOS, asignar_epoca_faltante,
                       cargar_viviendas)

R = DECISION["reglas"]
VT = DECISION["variante_tamano"]
TAMANOS = VT["etiquetas"]
ORDEN = {"c_tipo": TIPOS, "c_tam": TAMANOS, "c_bloque": BLOQUES}


def tamanos(v, cols):
    g = v.groupby(cols, observed=True)
    return pd.DataFrame({"viviendas": g.size(), "edificios": g["edificio_id"].nunique()})


def cumple(t, n_total):
    return (t["viviendas"] >= R["min_frac_viviendas"] * n_total) & (t["edificios"] >= R["min_edificios"])


def mascara(v, valores):
    m = np.ones(len(v), bool)
    for c, x in valores.items():
        m &= (v[c] == x).to_numpy()
    return m


def juntar_epocas(v, cols, n, log):
    """Etapa 1: las celdas que no cumplen juntan todas las épocas de su combinación."""
    t = tamanos(v, cols)
    otras = [c for c in cols if c != "c_epoca"]
    for idx in t.index[~cumple(t, n)]:
        d = dict(zip(cols, idx))
        m = mascara(v, {c: d[c] for c in otras})
        if (v.loc[m, "c_epoca"] != "todas").any():
            v.loc[m, "c_epoca"] = "todas"
            log.append(("juntar_epocas", "|".join(map(str, idx)), "todas las épocas", int(m.sum())))


def unir_vecino(v, cols, n, log, col, etapa, una_vez):
    """Une cada celda que no cumple con la celda vecina en `col` que tenga más viviendas.

    Las vecinas son las clases adyacentes en el orden de `col`; la unión toma todas las épocas de ambas
    combinaciones. Con `una_vez`, una celda ya unida en `col` no se vuelve a unir en esta etapa.
    """
    orden = ORDEN[col]
    otras = [c for c in cols if c not in (col, "c_epoca")]
    sin_destino = set()
    while True:
        t = tamanos(v, cols)
        malas = [i for i in t[~cumple(t, n)].sort_values("viviendas").index if i not in sin_destino]
        if una_vez:
            malas = [i for i in malas if "+" not in str(dict(zip(cols, i))[col])]
        if not malas:
            return
        idx = malas[0]
        d = dict(zip(cols, idx))
        partes = d[col].split("+")
        pos = [orden.index(p) for p in partes]
        vecinos = {orden[i] for i in (min(pos) - 1, max(pos) + 1) if 0 <= i < len(orden)}
        t2 = tamanos(v, otras + [col])
        cand = [i for i in t2.index
                if all(dict(zip(otras + [col], i))[c] == d[c] for c in otras)
                and set(str(dict(zip(otras + [col], i))[col]).split("+")) & vecinos]
        if not cand:
            sin_destino.add(idx)
            continue
        dest = max(cand, key=lambda i: t2.loc[i, "viviendas"])
        dd = dict(zip(otras + [col], dest))
        m_src = mascara(v, {c: d[c] for c in otras + [col]})
        m_dst = mascara(v, dd)
        nuevo = "+".join(sorted({*partes, *dd[col].split("+")}, key=orden.index))
        v.loc[m_src | m_dst, col] = nuevo
        v.loc[m_src | m_dst, "c_epoca"] = "todas"
        log.append((etapa, "|".join(map(str, idx)), "|".join(map(str, dest)), int(m_src.sum())))


def tipologia(v, con_tamano):
    n = len(v)
    v = v.copy()
    v["c_tipo"], v["c_pos"], v["c_epoca"], v["c_bloque"] = v["tipo"], v["posicion"].astype(str), v["epoca"], v["bloque"]
    cols = ["c_tipo", "c_pos", "c_epoca", "c_bloque"]
    niveles = [TIPOS, POSICIONES, EPOCAS, BLOQUES]
    if con_tamano:
        c = VT["cortes_m2"]
        v["c_tam"] = pd.cut(v["area_construida"], [-np.inf, c[0], c[1], np.inf], right=False, labels=TAMANOS).astype(str)
        cols.insert(3, "c_tam")
        niveles.insert(3, TAMANOS)

    ini = tamanos(v, cols).reindex(pd.MultiIndex.from_product(niveles, names=cols), fill_value=0)
    ini = ini[~((ini.index.get_level_values("c_tipo") == "multifamiliar") & (ini.index.get_level_values("c_pos") == "casa"))]
    ini["cumple"] = cumple(ini, n)

    log = []
    juntar_epocas(v, cols, n, log)
    if con_tamano:
        unir_vecino(v, cols, n, log, "c_tam", "tamano_vecino", una_vez=False)
    unir_vecino(v, cols, n, log, "c_bloque", "bloque_vecino", una_vez=True)
    unir_vecino(v, cols, n, log, "c_tipo", "juntar_tipos", una_vez=True)
    v["c_tipo"] = v["c_tipo"].replace({"+".join(TIPOS): "ambos"})

    t = tamanos(v, cols)
    for idx in t.index[~cumple(t, n)]:
        log.append(("sin_destino", "|".join(map(str, idx)), "se conserva", int(t.loc[idx, "viviendas"])))

    # arquetipos finales, ordenados por posición, tipo, tamaño, bloque y época
    fin = tamanos(v, cols).reset_index()
    rango = {"c_pos": POSICIONES, "c_tipo": TIPOS + ["ambos"], "c_tam": TAMANOS, "c_bloque": BLOQUES}
    clave = lambda s: s.map(lambda x: rango[s.name].index(x.split("+")[0])) if s.name in rango else s
    fin = fin.sort_values(["c_pos", "c_tipo"] + (["c_tam"] if con_tamano else []) + ["c_bloque", "c_epoca"], key=clave)
    fin["arquetipo"] = [f"{'T' if con_tamano else 'R'}{i:02d}" for i in range(1, len(fin) + 1)]
    v = v.merge(fin[cols + ["arquetipo"]], on=cols, how="left")
    return v, cols, ini, log, fin


def agregados(v, fin, cols):
    n = len(v)
    g = v.groupby("arquetipo")
    agg = fin.set_index("arquetipo").rename(columns=lambda c: c.replace("c_", ""))
    agg["pct_viviendas"] = (agg["viviendas"] / n * 100).round(2)
    agg["area_mediana_m2"] = g["area_construida"].median().round(0)
    agg["area_p25_m2"] = g["area_construida"].quantile(.25).round(0)
    agg["area_p75_m2"] = g["area_construida"].quantile(.75).round(0)
    agg["pisos_unidad_mediana"] = g["total_plantas"].median()
    agg["pct_vis_vip"] = (g["tipo_vivienda"].apply(lambda s: s.astype(str).str.contains("Interés").mean()) * 100).round(1)
    agg["pct_informal"] = (g["condicion_predio"].apply(lambda s: (s.astype(str) == "Informal").mean()) * 100).round(1)
    est = pd.crosstab(v["arquetipo"], v["estrato_num"], normalize="index").mul(100).round(1)
    est.columns = [f"pct_E{c}" for c in est.columns]
    return agg.join(est)


def main():
    v0 = cargar_viviendas()

    sin_epoca = asignar_epoca_faltante(v0)
    print(f"viviendas sin época asignadas por moda: {sin_epoca.sum():,} "
          f"(S13: {(sin_epoca & v0['anio_construccion'].notna()).sum():,})")

    pd.set_option("display.width", 220)
    for con_tamano, suf, archivo in [(False, "", "tipologia_reglas"), (True, "_tamano", "tipologia_reglas_tamano")]:
        v, cols, ini, log, fin = tipologia(v0, con_tamano)
        ini.reset_index().to_csv(TABLAS / f"reglas_celdas_iniciales{suf}.csv", index=False, encoding="utf-8-sig")
        pd.DataFrame(log, columns=["etapa", "celda", "destino", "viviendas"]).to_csv(
            TABLAS / f"reglas_fusiones{suf}.csv", index=False, encoding="utf-8-sig")
        agg = agregados(v, fin, cols)
        agg.to_csv(TABLAS / f"reglas_arquetipos{suf}.csv", encoding="utf-8-sig")
        INTERNOS.mkdir(exist_ok=True)
        v[["edificio_id", "arquetipo", "tipo", "posicion", "epoca", "bloque", "estrato_num"]].to_parquet(
            INTERNOS / f"{archivo}.parquet")

        print(f"\n=== {'variante con tamaño' if con_tamano else 'tipología base'} ===")
        print(f"celdas posibles: {len(ini)}; con viviendas: {(ini.viviendas > 0).sum()}; cumplen: {ini.cumple.sum()}; "
              f"fusiones: {len(log)}; arquetipos finales: {len(agg)}")
        mostrar = ["tipo", "pos", "epoca"] + (["tam"] if con_tamano else []) + ["bloque", "viviendas", "pct_viviendas",
                                                                              "edificios", "area_mediana_m2"]
        print(agg[mostrar].to_string())


if __name__ == "__main__":
    main()
