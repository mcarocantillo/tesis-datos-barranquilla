"""Materiales del catastro frente a la ECV 2024 (preregistro, Nota 13; análisis A12).

Compara, por bloque de estratos y tipo de vivienda, la proporción de techos de concreto y de paredes de mampostería
de las viviendas con la calificación convencional registrada (script 12) con la de la ECV 2024 y su intervalo del 95 %
por el diseño muestral (funciones del script 07). La categoría «Azotea_Aluminio_Placa_Sencilla_Con_Eternit» es
ambigua y se lleva como intervalo. Dentro de cada celda compara también las viviendas con y sin materiales en área,
año de construcción y estrato (diferencia de medias estandarizada).

Uso: python scripts/19_materiales_catastro_ecv.py
Salidas (solo agregados):
  salidas/tablas/materiales_vs_ecv.csv        proporciones de cada fuente, intervalos y concordancia por celda
  salidas/tablas/materiales_seleccion.csv     diferencias estandarizadas entre viviendas con y sin materiales
  salidas/tablas/materiales_catastro_techo.csv  reparto de las categorías de cubierta del catastro por celda
  salidas/tablas/env_escenario_techo_catastro_{sol}.csv  escenario de sensibilidad del techo de la Fase 2 (AJ31)
"""
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from src.comun import BLOQUES, INTERNOS, TABLAS, cargar_viviendas  # noqa: E402

_spec = importlib.util.spec_from_file_location("priors", RAIZ / "scripts" / "07_priors_envolvente.py")
priors = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(priors)

TECHO = {"Placa_Impermeabilizada_Lujosa_U_Ornamental": "concreto",
         "Placa_Impermeabilizada_Cubierta_Lujosa_U_Ornamental": "concreto",
         "Azotea_Aluminio_Placa_Sencilla_Con_Eternit": "ambigua",
         "Zinc_Teja_De_Barro_Eternit_Rustico": "liviano",
         "Eternit_O_Teja_De_Barro_Cubierta_Sencilla": "liviano",
         "Entrepiso_Cubierta_Provisional_Prefabricado": "liviano",
         "Materiales_Desecho_Telas_Asfalticas": "liviano"}
# posición del catastro que se compara con cada tipo de la ECV
POSICIONES = {"techo": {"casa": ["casa"], "apartamento": ["ultimo_piso"]},
              "paredes": {"casa": ["casa"], "apartamento": ["ultimo_piso", "sin_cubierta"]}}
Z = 1.96
UMBRAL_DME = 0.2
N_MIN_ESCENARIO = 30


def dme(x1, x0):
    """Diferencia de medias estandarizada (con − sin materiales)."""
    x1, x0 = x1.dropna(), x0.dropna()
    s = np.sqrt((x1.var() + x0.var()) / 2)
    return float((x1.mean() - x0.mean()) / s) if s > 0 else np.nan


def escenario_techo(v):
    """AJ31: el prior del techo con la proporción de concreto del catastro (ambigua como liviana)."""
    arq = pd.read_parquet(INTERNOS / "arquetipos_final.parquet")
    for sol in ["por_vivienda", "por_m2"]:
        base = json.loads((TABLAS / f"env_priors_{sol}.json").read_text(encoding="utf-8"))["arquetipos"]
        g = pd.DataFrame({"a": arq[sol].astype(str).to_numpy(), "t": v["techo_cat"].to_numpy()})
        filas = []
        for a, js in base.items():
            if "techo" not in js:
                continue
            alfa = pd.Series(js["techo"]["alfa"], dtype=float)
            t = g.loc[(g["a"] == a) & g["t"].notna(), "t"]
            fila = dict(arquetipo=a, con_dato=len(t), concreto_prior=round(alfa["concreto"] / alfa.sum(), 4))
            if len(t) >= N_MIN_ESCENARIO:
                pc = float((t == "concreto").mean())
                liv = alfa.drop("concreto")
                nuevo = pd.concat([pd.Series({"concreto": pc}), (1 - pc) * liv / liv.sum()]) * alfa.sum()
                fila.update(concreto_escenario=round(pc, 4), fuente="catastro")
            else:
                nuevo = alfa
                fila.update(concreto_escenario=fila["concreto_prior"], fuente="prior (menos de 30 con dato)")
            fila.update({f"alfa_{k}": round(float(x), 4) for k, x in nuevo.items()})
            filas.append(fila)
        t = pd.DataFrame(filas)
        t.to_csv(TABLAS / f"env_escenario_techo_catastro_{sol}.csv", index=False, encoding="utf-8-sig")
        print(t.to_string(index=False))


def main():
    v = cargar_viviendas()
    mat = pd.read_parquet(INTERNOS / "viviendas_materiales.parquet")
    assert len(mat) == len(v)
    v["techo_cat"] = mat["cubierta"].map(TECHO).to_numpy()
    v["muro_cat"] = np.where(mat["muros"].isna(), None,
                             np.where(mat["muros"] == "Bloque_Ladrillo", "mamposteria", "otro"))
    v["con_techo"], v["con_muro"] = v["techo_cat"].notna(), v["muro_cat"].notna()
    assert mat.loc[mat["cubierta"].notna(), "cubierta"].map(TECHO).notna().all(), "cubierta sin equivalencia"

    e, _ = priors.ecv(2024)
    filas, sel, rep = [], [], []
    for var in ["techo", "paredes"]:
        for bloque in BLOQUES:
            for tipo, pos in POSICIONES[var].items():
                c = v[(v["bloque"] == bloque) & v["posicion"].isin(pos)]
                p, cov, n = priors.proporciones(e, ((e["bloque"] == bloque) & (e["tipo"] == tipo)).astype(float),
                                                var)
                p_ecv, se = float(p[0]), float(np.sqrt(cov[0, 0]))
                lo, hi = max(0.0, p_ecv - Z * se), min(1.0, p_ecv + Z * se)
                con = c["con_techo"] if var == "techo" else c["con_muro"]
                d = c[con]
                fila = dict(variable=var, bloque=bloque, tipo_ecv=tipo, posiciones_catastro="+".join(pos),
                            viviendas_catastro=len(c), con_material=int(con.sum()),
                            cobertura=round(float(con.mean()), 4), hogares_ecv=n,
                            p_ecv=round(p_ecv, 4), ic95_ecv_bajo=round(lo, 4), ic95_ecv_alto=round(hi, 4))
                if var == "techo":
                    t = d["techo_cat"].value_counts(normalize=True)
                    a, b = t.get("concreto", 0.0), t.get("concreto", 0.0) + t.get("ambigua", 0.0)
                    fila.update(p_catastro_bajo=round(a, 4), p_catastro_alto=round(b, 4),
                                concuerda=bool(b >= lo and a <= hi))
                    cub = mat.loc[d.index, "cubierta"].value_counts(normalize=True).round(4)
                    rep += [dict(bloque=bloque, tipo_ecv=tipo, cubierta=k, fraccion=x) for k, x in cub.items()]
                else:
                    a = float((d["muro_cat"] == "mamposteria").mean())
                    fila.update(p_catastro_bajo=round(a, 4), p_catastro_alto=round(a, 4),
                                concuerda=bool(lo <= a <= hi))
                filas.append(fila)
                for x in ["area_construida", "anio_construccion", "estrato_num"]:
                    sel.append(dict(variable=var, bloque=bloque, tipo_ecv=tipo, atributo=x,
                                    media_con=round(float(c.loc[con, x].mean()), 2),
                                    media_sin=round(float(c.loc[~con, x].mean()), 2),
                                    dme=round(dme(c.loc[con, x], c.loc[~con, x]), 3)))
    t = pd.DataFrame(filas)
    s = pd.DataFrame(sel)
    s["marcada"] = s["dme"].abs() > UMBRAL_DME
    t = t.merge(s.groupby(["variable", "bloque", "tipo_ecv"])["marcada"].any().rename("seleccion_marcada")
                .reset_index(), on=["variable", "bloque", "tipo_ecv"])
    t.to_csv(TABLAS / "materiales_vs_ecv.csv", index=False, encoding="utf-8-sig")
    s.to_csv(TABLAS / "materiales_seleccion.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(rep).to_csv(TABLAS / "materiales_catastro_techo.csv", index=False, encoding="utf-8-sig")
    print(t.to_string(index=False))
    print(s.to_string(index=False))
    escenario_techo(v)


if __name__ == "__main__":
    main()
