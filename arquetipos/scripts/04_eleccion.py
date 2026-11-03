"""Aplica la Nota 4 (elección del algoritmo) y la regla del Paso 4 a las salidas de 03_agrupamiento.py.

Salidas (sufijo «_prueba» con --prueba):
  salidas/tablas/agr_eleccion_nota4.csv   algoritmo elegido por diseño y medida de carga, con el criterio que decidió
  salidas/tablas/agr_resultado_final.json diseño adoptado (Paso 4), solución final y análisis A6 (regla 7.7)
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prueba", action="store_true")
    suf = "_prueba" if ap.parse_args().prueba else ""

    filas, selecciones = [], {}
    for diseno in ["plano", "anidado"]:
        sel = selecciones[diseno] = pd.read_csv(TABLAS / f"agr_seleccion_{diseno}{suf}.csv")
        for m, s in sel.groupby("medida"):
            f, criterio = elegir(s)
            filas.append({"diseno": diseno, "medida": m, "algoritmo": f.algoritmo, "k": int(f.k), "R2": round(f.R2, 4),
                          "jaccard_ponderado": round(f.jaccard_ponderado, 3), "silueta_gower": round(f.silueta_gower, 3),
                          "estable": bool(f.pasa_estabilidad), "criterio": criterio,
                          "algoritmo_regla_7_7": s.loc[s.elegido.astype(bool), "algoritmo"].iloc[0]})
    eleccion = pd.DataFrame(filas)
    eleccion.to_csv(TABLAS / f"agr_eleccion_nota4{suf}.csv", index=False, encoding="utf-8-sig")
    print(eleccion.to_string(index=False))

    paso4 = json.loads((TABLAS / f"agr_decision_paso4{suf}.json").read_text(encoding="utf-8"))
    asign = pd.read_parquet(INTERNOS / f"agrupamiento{suf}.parquet")
    final, cols = {"medida_que_aplica": paso4["medida_que_aplica"]}, {}
    for m in ["por_vivienda", "por_m2"]:
        plano = eleccion[(eleccion.diseno == "plano") & (eleccion.medida == m)].iloc[0]
        regla = paso4[m][plano.algoritmo]
        diseno = regla["diseno_adoptado"]
        sol = eleccion[(eleccion.diseno == diseno) & (eleccion.medida == m)].iloc[0]
        final[m] = {"algoritmo_plano": plano.algoritmo, "plano_inestable": regla["plano_inestable"],
                    "eta2_estrato": regla["eta2_estrato"], "diseno_adoptado": diseno,
                    "algoritmo_final": sol.algoritmo, "k_final": int(sol.k), "R2_final": float(sol.R2),
                    "estable": bool(sol.estable)}
        shutil.copy(TABLAS / f"agr_grupos_{diseno}_{m}_{sol.algoritmo}{suf}.csv", TABLAS / f"arquetipos_{m}{suf}.csv")
        cols[m] = asign[f"{diseno}_{m}_{sol.algoritmo}"]

    # A6: lo que habría dado la regla original de la Sección 7.7 (decide el mayor Jaccard)
    final["A6_regla_7_7"] = {}
    for m in ["por_vivienda", "por_m2"]:
        alg_plano = eleccion[(eleccion.diseno == "plano") & (eleccion.medida == m)].iloc[0].algoritmo_regla_7_7
        regla = paso4[m][alg_plano]
        diseno = regla["diseno_adoptado"]
        alg = eleccion[(eleccion.diseno == diseno) & (eleccion.medida == m)].iloc[0].algoritmo_regla_7_7
        f = selecciones[diseno].query("medida == @m and algoritmo == @alg").iloc[0]
        final["A6_regla_7_7"][m] = {
            "algoritmo_plano": alg_plano, "plano_inestable": regla["plano_inestable"], "eta2_estrato": regla["eta2_estrato"],
            "diseno_adoptado": diseno, "algoritmo_final": alg, "k_final": int(f.k), "R2_final": round(float(f.R2), 4),
            "jaccard_ponderado": round(float(f.jaccard_ponderado), 3), "silueta_gower": round(float(f.silueta_gower), 3),
            "rand_ajustado_frente_a_nota4": round(adjusted_rand_score(cols[m], asign[f"{diseno}_{m}_{alg}"]), 3)}
    (TABLAS / f"agr_resultado_final{suf}.json").write_text(json.dumps(final, ensure_ascii=False, indent=2), encoding="utf-8")
    pd.DataFrame(cols).to_parquet(INTERNOS / f"arquetipos_final{suf}.parquet")
    print(json.dumps(final, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
