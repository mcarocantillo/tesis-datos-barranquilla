"""Análisis complementario A5 para las soluciones finales: repetir el agrupamiento sin excluir los atípicos de DBSCAN.

Usa la misma submuestra (semilla 42), el diseño y el algoritmo finales de agr_resultado_final.json y la regla de la
Nota 3 para elegir k. Compara con la solución final por el número de grupos, el R² y el índice de Rand ajustado.
Salida: salidas/tablas/agr_a5_final.json
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import adjusted_rand_score

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.agrupamiento import A, Estrato, Modelo, elegir_k, frontera, preparar, submuestra, suma_cuadrados
from src.comun import DECISION, INTERNOS, SEMILLA, TABLAS, asignar_epoca_faltante, cargar_viviendas

UMBRAL = DECISION["carga"]["criterio"]["delta_R2_min"]
N3 = A["nota3"]


def main():
    final = json.loads((TABLAS / "agr_resultado_final.json").read_text(encoding="utf-8"))
    v = cargar_viviendas()
    asignar_epoca_faltante(v)
    x = preparar(v)
    cc = pd.read_parquet(INTERNOS / "carga_viviendas.parquet")
    cargas = {"por_vivienda": cc["total"].to_numpy(float), "por_m2": cc["por_m2"].to_numpy(float)}
    finales = pd.read_parquet(INTERNOS / "arquetipos_final.parquet")
    idx = submuestra(v, np.random.default_rng(SEMILLA))

    out = {}
    for m in ["por_vivienda", "por_m2"]:
        f = final[m]
        diseno, alg = f["diseno_adoptado"], f["algoritmo_final"]
        estrato = v["posicion"].astype(str) if diseno == "plano" else v["posicion"].astype(str) + "|" + v["bloque"]
        kmax = A["k_por_estrato"][diseno][1]
        ssw, etiquetas, tope = {}, {}, {}
        ests = {e: Estrato(e, x.loc[idx[(estrato.loc[idx] == e).to_numpy()]]) for e in sorted(estrato.loc[idx].unique())}

        def calcular(e, k):
            mask = (estrato == e).to_numpy()
            g = Modelo(alg, ests[e], k, np.arange(len(ests[e].x))).asignar(x.loc[mask])  # todos los puntos, sin excluir
            etiquetas[(e, k)] = g
            ssw[e].append(suma_cuadrados(cargas[m][mask], g))

        for e in ests:
            ssw[e], tope[e] = [], kmax
            for k in range(1, kmax + 1):
                calcular(e, k)
        sst = float(((cargas[m] - cargas[m].mean()) ** 2).sum())
        while True:
            front = frontera(ssw, sst)
            i = elegir_k(front, UMBRAL)
            ampliar = [e for e, k in front[i][2].items() if k == tope[e] and tope[e] < N3["tope_seguridad"]]
            if not ampliar:
                break
            for e in ampliar:
                nuevo = min(tope[e] + N3["ampliar_tope"], N3["tope_seguridad"])
                for k in range(tope[e] + 1, nuevo + 1):
                    calcular(e, k)
                tope[e] = nuevo
        K, r2, asig = front[i]
        etiqueta = np.empty(len(v), dtype=object)
        for e, k in asig.items():
            mask = (estrato == e).to_numpy()
            etiqueta[mask] = [f"{e}#{g}" for g in etiquetas[(e, k)]]
        out[m] = {"diseno": diseno, "algoritmo": alg, "k_final": f["k_final"], "R2_final": f["R2_final"],
                  "k_sin_excluir": int(K), "R2_sin_excluir": round(float(r2), 4),
                  "rand_ajustado_frente_a_final": round(adjusted_rand_score(finales[m], etiqueta), 3)}
        print(m, out[m], flush=True)
    (TABLAS / "agr_a5_final.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
