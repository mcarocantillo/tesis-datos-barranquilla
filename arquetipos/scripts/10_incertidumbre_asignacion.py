"""Paso 5 con la Nota 9 (AJ21): incertidumbre de la asignación de las viviendas a los arquetipos.

En cada estrato de la solución final con más de un grupo, repite el ajuste del algoritmo final en las mismas 100
submuestras del 80 % del análisis de estabilidad, asigna todas las viviendas del estrato y empareja los grupos de cada
reajuste con los arquetipos finales por el método húngaro, sobre los puntos de ajuste que comparten. La probabilidad de
que una vivienda pertenezca a un arquetipo es la fracción de submuestras en que cae en él; en los estratos con un solo
arquetipo vale 1. Reemplaza las probabilidades del clasificador del Paso 5, que valen casi 1 por construcción.
Con --prueba usa 5 submuestras (solo para revisar el código y medir el tiempo).

Salidas (sufijo «_prueba» con --prueba):
  salidas/tablas/asg_incertidumbre_{sol}.csv   por arquetipo: probabilidad media de pertenecer a su propio arquetipo,
                                               fracción de viviendas por debajo de 0,8 y el arquetipo con que más se confunde
  salidas/tablas/asg_incertidumbre.json        control: el ajuste con todos los puntos reproduce la solución final
  datos_internos/probabilidades_agrupamiento_{sol}.parquet  probabilidad de cada vivienda en cada arquetipo (no se publica)
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from scipy.optimize import linear_sum_assignment

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.agrupamiento import A, Estrato, Modelo, atipicos, fijar_variables, preparar, submuestra  # noqa: E402
from src.comun import DECISION, INTERNOS, POSICIONES, SEMILLA, TABLAS, asignar_epoca_faltante, cargar_viviendas  # noqa: E402

N9 = DECISION["nota9"]["incertidumbre_asignacion"]
SOLUCIONES = ["por_vivienda", "por_m2"]


def ruido_por_posicion(v, x, idx):
    """Atípicos de DBSCAN de cada posición (Sección 7.4), los mismos de la solución final."""
    ruido = pd.Series(False, index=idx)
    for p in POSICIONES:
        ip = idx[(v.loc[idx, "posicion"] == p).to_numpy()]
        ruido.loc[ip] = atipicos(Estrato(p, x.loc[ip]))[0]
    return ruido


def un_reajuste(alg, est, k, pos_ajuste, etiquetas, x_estrato, b, frac):
    """Reajuste en la submuestra b del análisis de estabilidad (misma semilla que jaccard) y grupo de cada vivienda
    del estrato, con los grupos emparejados a los de la solución final por el método húngaro."""
    rng = np.random.default_rng(SEMILLA + b)
    sel = np.sort(rng.choice(len(pos_ajuste), size=int(round(frac * len(pos_ajuste))), replace=False))
    mod = Modelo(alg, est, k, pos_ajuste[sel])
    coincidencias = np.zeros((k, k))
    np.add.at(coincidencias, (mod.etiquetas, etiquetas[sel]), 1)
    fila, col = linear_sum_assignment(-coincidencias)
    mapa = np.arange(k)
    mapa[fila] = col
    return mapa[mod.asignar(x_estrato)].astype(np.int8)


def resumen(prob, ref, codigos):
    """Por arquetipo: probabilidad media de pertenecer a su propio arquetipo, fracción por debajo del umbral y el
    arquetipo con que más se confunde (solo si esa probabilidad media no redondea a cero)."""
    col = {c: i for i, c in enumerate(codigos)}
    propio = prob[np.arange(len(ref)), [col[c] for c in ref]]
    otros = prob.copy()
    otros[np.arange(len(ref)), [col[c] for c in ref]] = -1
    filas = []
    for c in codigos:
        m = ref == c
        media_otros = otros[m].mean(axis=0)
        j = int(np.argmax(media_otros))
        p_otro = round(float(max(media_otros[j], 0)), 4)
        filas.append({"arquetipo": c, "viviendas": int(m.sum()), "probabilidad_media": round(float(propio[m].mean()), 4),
                      "frac_menor_0_8": round(float((propio[m] < N9["umbral_reporte"]).mean()), 4),
                      "se_confunde_con": codigos[j] if p_otro > 0 else "", "probabilidad_media_otro": p_otro})
    return pd.DataFrame(filas)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prueba", action="store_true")
    prueba = ap.parse_args().prueba
    suf = "_prueba" if prueba else ""
    n_sub = 5 if prueba else A["jaccard"]["submuestras"]

    v = cargar_viviendas()
    asignar_epoca_faltante(v)
    x = preparar(v)
    finales = pd.read_parquet(INTERNOS / "arquetipos_final.parquet")
    final = json.loads((TABLAS / "agr_resultado_final.json").read_text(encoding="utf-8"))
    idx = submuestra(v, np.random.default_rng(SEMILLA))
    estrato = (v["posicion"].astype(str) + "|" + v["bloque"]).to_numpy()

    control = {}
    for sol in SOLUCIONES:
        f = final[sol]
        assert f["diseno_adoptado"] == "anidado", sol
        fijar_variables(f.get("variables", "base"))
        ruido = ruido_por_posicion(v, x, idx)
        ref = finales[sol].astype(str).to_numpy()
        codigos = sorted(pd.unique(ref))
        col = {c: i for i, c in enumerate(codigos)}
        prob = np.zeros((len(v), len(codigos)), dtype=np.float32)
        k_est = pd.read_csv(TABLAS / f"arquetipos_{sol}.csv").groupby("estrato_algoritmo").size()
        for e, k in k_est.items():
            filas = np.flatnonzero(estrato == e)
            if k == 1:
                prob[filas, col[ref[filas[0]]]] = 1.0
                continue
            t0 = time.time()
            ie = idx[(estrato[v.index.get_indexer(idx)] == e)]
            est = Estrato(e, x.loc[ie])
            pos = np.flatnonzero(~ruido.loc[ie].to_numpy())
            mod0 = Modelo(f["algoritmo_final"], est, int(k), pos)
            x_e = x.iloc[filas]
            g0 = mod0.asignar(x_e)
            cod = pd.crosstab(g0, ref[filas]).idxmax(axis=1)  # arquetipo final de cada grupo del ajuste completo
            reproduce = float((cod.reindex(g0).to_numpy() == ref[filas]).mean())
            res = Parallel(n_jobs=-1)(delayed(un_reajuste)(f["algoritmo_final"], est, int(k), pos, mod0.etiquetas, x_e, b,
                                                           A["jaccard"]["fraccion"]) for b in range(n_sub))
            cuenta = np.zeros((len(filas), int(k)))
            for r in res:
                cuenta[np.arange(len(filas)), r] += 1
            for g in range(int(k)):
                prob[filas, col[cod[g]]] = cuenta[:, g] / n_sub
            control[f"{sol} {e}"] = {"algoritmo": f["algoritmo_final"], "k": int(k), "submuestras": n_sub,
                                     "reproduce_solucion_final": reproduce, "segundos": round(time.time() - t0)}
            print(f"{sol} {e}: k={k}, reproduce {reproduce:.4f}, {time.time() - t0:.0f} s", flush=True)

        tabla = resumen(prob, ref, codigos)
        tabla.to_csv(TABLAS / f"asg_incertidumbre_{sol}{suf}.csv", index=False, encoding="utf-8-sig")
        pd.DataFrame(prob, index=v.index, columns=codigos).to_parquet(INTERNOS / f"probabilidades_agrupamiento_{sol}{suf}.parquet")
        print(tabla.to_string(index=False), flush=True)
    (TABLAS / f"asg_incertidumbre{suf}.json").write_text(json.dumps(control, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
