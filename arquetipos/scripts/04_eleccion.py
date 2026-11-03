"""Aplica la Nota 4 (elección del algoritmo) y la regla del Paso 4 a las salidas de 03_agrupamiento.py y, si existe la
variante ampliada (03_agrupamiento.py --ampliada), la regla de la Nota 8 entre las dos soluciones.

Salidas (sufijo «_prueba» con --prueba):
  salidas/tablas/agr_eleccion_nota4.csv   algoritmo elegido por conjunto de variables, diseño y medida de carga
  salidas/tablas/agr_resultado_final.json diseño adoptado (Paso 4), solución final, Nota 8 y análisis A6 (regla 7.7)
  salidas/tablas/arquetipos_{medida}.csv  perfil de los arquetipos finales
  datos_internos/arquetipos_final.parquet arquetipo final de cada vivienda (no se publica)
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

import pandas as pd
from sklearn.metrics import adjusted_rand_score

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.comun import DECISION, INTERNOS, TABLAS

N4 = DECISION["agrupamiento_v2"]["nota4"]
MEDIDAS = ["por_vivienda", "por_m2"]


def elegir(sel):
    """Nota 4: filtro de estabilidad; entre las estables, mayor R²; empates por menos grupos y mayor silueta."""
    estables = sel[sel["pasa_estabilidad"]]
    if estables.empty:
        return sel.sort_values("jaccard_ponderado", ascending=False).iloc[0], "ninguna estable: mayor Jaccard"
    estables = estables.sort_values("R2", ascending=False)
    cand = estables[estables["R2"] >= estables["R2"].iloc[0] - N4["empate_R2"]]
    if len(cand) == 1:
        return cand.iloc[0], "mayor R2 entre las estables"
    return cand.sort_values(["k", "silueta_gower"], ascending=[True, False]).iloc[0], "empate de R2: menos grupos, silueta"


def resolver(suf, variables):
    """Nota 4, Paso 4 y A6 para un conjunto de variables (las salidas de 03 con el sufijo suf)."""
    filas, selecciones = [], {}
    for diseno in ["plano", "anidado"]:
        sel = selecciones[diseno] = pd.read_csv(TABLAS / f"agr_seleccion_{diseno}{suf}.csv")
        for m, s in sel.groupby("medida"):
            f, criterio = elegir(s)
            filas.append({"variables": variables, "diseno": diseno, "medida": m, "algoritmo": f.algoritmo,
                          "k": int(f.k), "R2": round(f.R2, 4), "jaccard_ponderado": round(f.jaccard_ponderado, 3),
                          "silueta_gower": round(f.silueta_gower, 3), "estable": bool(f.pasa_estabilidad),
                          "criterio": criterio,
                          "algoritmo_regla_7_7": s.loc[s.elegido.astype(bool), "algoritmo"].iloc[0]})
    eleccion = pd.DataFrame(filas)

    paso4 = json.loads((TABLAS / f"agr_decision_paso4{suf}.json").read_text(encoding="utf-8"))
    asign = pd.read_parquet(INTERNOS / f"agrupamiento{suf}.parquet")
    final, cols = {}, {}
    for m in MEDIDAS:
        plano = eleccion[(eleccion.diseno == "plano") & (eleccion.medida == m)].iloc[0]
        regla = paso4[m][plano.algoritmo]
        diseno = regla["diseno_adoptado"]
        sol = eleccion[(eleccion.diseno == diseno) & (eleccion.medida == m)].iloc[0]
        final[m] = {"variables": variables, "algoritmo_plano": plano.algoritmo,
                    "plano_inestable": regla["plano_inestable"], "eta2_estrato": regla["eta2_estrato"],
                    "diseno_adoptado": diseno, "algoritmo_final": sol.algoritmo, "k_final": int(sol.k),
                    "R2_final": float(sol.R2), "estable": bool(sol.estable),
                    "jaccard_ponderado": float(sol.jaccard_ponderado), "silueta_gower": float(sol.silueta_gower),
                    "tabla_grupos": f"agr_grupos_{diseno}_{m}_{sol.algoritmo}{suf}.csv"}
        cols[m] = asign[f"{diseno}_{m}_{sol.algoritmo}"]

    # A6: lo que habría dado la regla original de la Sección 7.7 (decide el mayor Jaccard)
    a6 = {}
    for m in MEDIDAS:
        alg_plano = eleccion[(eleccion.diseno == "plano") & (eleccion.medida == m)].iloc[0].algoritmo_regla_7_7
        regla = paso4[m][alg_plano]
        diseno = regla["diseno_adoptado"]
        alg = eleccion[(eleccion.diseno == diseno) & (eleccion.medida == m)].iloc[0].algoritmo_regla_7_7
        f = selecciones[diseno].query("medida == @m and algoritmo == @alg").iloc[0]
        a6[m] = {"algoritmo_plano": alg_plano, "plano_inestable": regla["plano_inestable"],
                 "eta2_estrato": regla["eta2_estrato"], "diseno_adoptado": diseno, "algoritmo_final": alg,
                 "k_final": int(f.k), "R2_final": round(float(f.R2), 4),
                 "jaccard_ponderado": round(float(f.jaccard_ponderado), 3),
                 "silueta_gower": round(float(f.silueta_gower), 3),
                 "rand_ajustado_frente_a_nota4": round(adjusted_rand_score(cols[m], asign[f"{diseno}_{m}_{alg}"]), 3)}
    return eleccion, final, cols, a6, paso4["medida_que_aplica"]


def elegir_variables(finalistas):
    """Nota 8 entre los finalistas de cada conjunto de variables: estable; mayor R²; empate (< 0,02) por menos
    grupos, luego el de seis variables (el de la propuesta) y luego mayor silueta."""
    estables = [f for f in finalistas if f["estable"]]
    if not estables:
        return max(finalistas, key=lambda f: f["jaccard_ponderado"]), "ninguna estable: mayor Jaccard"
    if len(estables) == 1:
        return estables[0], "solo una es estable"
    mejor = max(f["R2_final"] for f in estables)
    cand = [f for f in estables if f["R2_final"] >= mejor - N4["empate_R2"]]
    if len(cand) == 1:
        return cand[0], "mayor R2"
    cand.sort(key=lambda f: (f["k_final"], f["variables"] != "base", -f["silueta_gower"]))
    return cand[0], "empate de R2: menos grupos, seis variables, silueta"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prueba", action="store_true")
    p = "_prueba" if ap.parse_args().prueba else ""

    conjuntos = {"base": resolver(p, "base")}
    if (TABLAS / f"agr_seleccion_plano_ampliada{p}.csv").exists():
        conjuntos["ampliada"] = resolver(f"_ampliada{p}", "ampliada")
    eleccion = pd.concat([c[0] for c in conjuntos.values()], ignore_index=True)
    eleccion.to_csv(TABLAS / f"agr_eleccion_nota4{p}.csv", index=False, encoding="utf-8-sig")
    print(eleccion.to_string(index=False))

    final, cols = {"medida_que_aplica": conjuntos["base"][4]}, {}
    if len(conjuntos) > 1:
        final["nota8"] = {}
    for m in MEDIDAS:
        finalistas = [c[1][m] for c in conjuntos.values()]
        ganador, criterio = elegir_variables(finalistas)
        final[m] = ganador
        cols[m] = conjuntos[ganador["variables"]][2][m]
        shutil.copy(TABLAS / ganador["tabla_grupos"], TABLAS / f"arquetipos_{m}{p}.csv")
        if len(conjuntos) > 1:
            final["nota8"][m] = {
                "ganador": ganador["variables"], "criterio": criterio,
                **{v: {k: c[1][m][k] for k in ["algoritmo_final", "k_final", "R2_final", "estable",
                                                  "jaccard_ponderado", "silueta_gower", "diseno_adoptado"]}
                   for v, c in conjuntos.items()},
                "rand_ajustado_base_frente_a_ampliada": round(
                    adjusted_rand_score(conjuntos["base"][2][m], conjuntos["ampliada"][2][m]), 3)}
    final["A6_regla_7_7"] = conjuntos["base"][3]
    if "ampliada" in conjuntos:
        final["A6_regla_7_7_ampliada"] = conjuntos["ampliada"][3]
    (TABLAS / f"agr_resultado_final{p}.json").write_text(json.dumps(final, ensure_ascii=False, indent=2), encoding="utf-8")
    pd.DataFrame(cols).to_parquet(INTERNOS / f"arquetipos_final{p}.parquet")
    print(json.dumps(final, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
