"""Robustez frente a la submuestra: la solución final del agrupamiento ajustada con todos los edificios.

Los Pasos 2 a 4 ajustaron el agrupamiento con una submuestra de 10.294 edificios (preregistro, Sección 7.2) y después
asignaron las 332.718 viviendas. Esta prueba repite el ajuste de la solución final (diseño anidado; k-prototypes para la
carga por vivienda y K-Means para la carga por m²) con una vivienda al azar de cada uno de los 177.105 edificios de cada
posición, sin cuotas:

  1. barrido de k con la regla de la Nota 3 (frontera y ganancia mínima de 0,02): ¿cambia el número de arquetipos?
  2. ajuste con el k de la solución final: ¿cuántas viviendas cambian de arquetipo? Los grupos se emparejan con los
     arquetipos finales por el método húngaro, contando viviendas.

DBSCAN, la silueta y el jerárquico necesitan la distancia de Gower entre todos los pares de edificios (unos 96 GB solo
en las casas), así que no se repiten y no se excluyen atípicos. Con --prueba usa el 10 % de los edificios, solo para
revisar el código y medir el tiempo.

Uso: python scripts/14_agrupamiento_todos_edificios.py [--prueba]
Salidas (sufijo «_prueba» con --prueba):
  salidas/tablas/todos_k.csv            edificios y k de cada estrato: solución final y barrido con todos los edificios
  salidas/tablas/todos_arquetipos.csv   por arquetipo: viviendas, área mediana y fracción que conserva su arquetipo
  salidas/tablas/todos_resumen.json     K, R² y concordancia de cada solución; tiempos
  datos_internos/arquetipos_todos_edificios.parquet  arquetipo de cada vivienda con el ajuste completo (no se publica)
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
from sklearn.metrics import adjusted_rand_score

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src import agrupamiento as ag  # noqa: E402
from src.agrupamiento import A, NUMERICAS, Estrato, Modelo, elegir_k, fijar_variables, frontera, preparar, suma_cuadrados  # noqa: E402
from src.carga import r2  # noqa: E402
from src.comun import DECISION, INTERNOS, POSICIONES, SEMILLA, TABLAS, asignar_epoca_faltante, cargar_viviendas  # noqa: E402

UMBRAL = DECISION["carga"]["criterio"]["delta_R2_min"]
N3 = A["nota3"]
KMAX = A["k_por_estrato"]["anidado"][1]
MEDIDA = {"por_vivienda": "total", "por_m2": "por_m2"}


class EstratoTodos(Estrato):
    """Como Estrato, pero sin la matriz de Gower, que con todos los edificios no cabe en memoria."""

    def __init__(self, nombre, x_ajuste):
        self.nombre = nombre
        moda = x_ajuste.apply(lambda s: s.value_counts(normalize=True).iloc[0])
        self.vars = [c for c in ag._candidatas if moda[c] < A["descartar_si_moda_cubre"]]
        self.num = [c for c in self.vars if c in NUMERICAS]
        self.cat = [c for c in self.vars if c not in NUMERICAS]
        self.x = x_ajuste
        self.mu = x_ajuste[self.vars].mean()
        self.sd = x_ajuste[self.vars].std(ddof=0)
        self.rango = (x_ajuste[self.vars].max() - x_ajuste[self.vars].min()).replace(0, 1)


def todos_los_edificios(v, rng):
    """Una vivienda al azar de cada edificio dentro de cada posición: la unidad de la Sección 7.2, sin cuotas."""
    return np.concatenate([v[v["posicion"] == p].sample(frac=1, random_state=rng).drop_duplicates("edificio_id").index
                           for p in POSICIONES])


def ajustar(alg, est, k, x_e, y_e):
    t0 = time.time()
    g = Modelo(alg, est, k, np.arange(len(est.x))).asignar(x_e).astype(np.int16)
    return est.nombre, k, g, suma_cuadrados(y_e, g), time.time() - t0


def emparejar(g, ref):
    """Arquetipo final de cada grupo del ajuste completo (método húngaro sobre el número de viviendas)."""
    tabla = pd.crosstab(g, ref)
    fila, col = linear_sum_assignment(-tabla.to_numpy())
    return dict(zip(tabla.index[fila], tabla.columns[col]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prueba", action="store_true")
    prueba = ap.parse_args().prueba
    suf = "_prueba" if prueba else ""
    t_ini = time.time()

    v = cargar_viviendas()
    asignar_epoca_faltante(v)
    x = preparar(v)
    cc = pd.read_parquet(INTERNOS / "carga_viviendas.parquet")
    finales = pd.read_parquet(INTERNOS / "arquetipos_final.parquet")
    final = json.loads((TABLAS / "agr_resultado_final.json").read_text(encoding="utf-8"))
    rng = np.random.default_rng(SEMILLA)
    idx = todos_los_edificios(v, rng)
    if prueba:
        idx = np.sort(rng.choice(idx, size=len(idx) // 10, replace=False))
    estrato = (v["posicion"].astype(str) + "|" + v["bloque"]).to_numpy()
    m = pd.read_csv(TABLAS / "agr_muestra.csv")
    muestra = m.groupby(m["posicion"] + "|" + m["bloque"])["edificios"].sum()
    print(f"edificios de ajuste: {len(idx):,}", flush=True)

    filas_k, filas_arq, resumen = [], [], {}
    nuevo = pd.DataFrame(index=v.index)
    for sol, medida in MEDIDA.items():
        f = final[sol]
        assert f["diseno_adoptado"] == "anidado", sol
        fijar_variables(f.get("variables", "base"))
        alg = f["algoritmo_final"]
        y = cc[medida].to_numpy(float)
        sst = float(((y - y.mean()) ** 2).sum())
        ref = finales[sol].astype(str).to_numpy()
        k_final = pd.read_csv(TABLAS / f"arquetipos_{sol}.csv").groupby("estrato_algoritmo").size()
        ie = {e: idx[estrato[idx] == e] for e in k_final.index}
        ests = {e: EstratoTodos(e, x.loc[i]) for e, i in ie.items()}
        filas = {e: np.flatnonzero(estrato == e) for e in ests}

        # 1. barrido de k con todos los edificios y regla de la Nota 3
        ssw, etiquetas, tope = {e: {} for e in ests}, {}, {e: 0 for e in ests}

        def correr(pedidos):
            res = Parallel(n_jobs=-1)(delayed(ajustar)(alg, ests[e], k, x.iloc[filas[e]], y[filas[e]]) for e, k in pedidos)
            for e, k, g, s, seg in res:
                ssw[e][k], etiquetas[(e, k)] = s, g
                if seg > 60:
                    print(f"  {sol} {e} k={k}: {seg:.0f} s", flush=True)

        t0 = time.time()
        correr([(e, k) for e in ests for k in range(1, KMAX + 1)])
        tope = {e: KMAX for e in ests}
        while True:
            front = frontera({e: [ssw[e][k] for k in range(1, tope[e] + 1)] for e in ests}, sst)
            i_sel = elegir_k(front, UMBRAL)
            ampliar = [e for e, k in front[i_sel][2].items() if k == tope[e] and tope[e] < N3["tope_seguridad"]]
            if not ampliar:
                break
            nuevos = {e: min(tope[e] + N3["ampliar_tope"], N3["tope_seguridad"]) for e in ampliar}
            correr([(e, k) for e in ampliar for k in range(tope[e] + 1, nuevos[e] + 1)])
            print(f"  {sol}: máximo ampliado en {', '.join(f'{e} ({tope[e]} -> {nuevos[e]})' for e in ampliar)}", flush=True)
            tope.update(nuevos)
        K_todos, r2_todos, k_todos = front[i_sel]
        print(f"{sol}: barrido en {time.time() - t0:.0f} s; K = {K_todos} con todos los edificios "
              f"(final {int(k_final.sum())})", flush=True)

        # 2. ajuste con el k de la solución final y emparejamiento con los arquetipos finales
        asig = ref.copy()
        for e in ests:
            k = int(k_final[e])
            filas_k.append({"solucion": sol, "estrato": e, "edificios_submuestra": int(muestra.get(e, 0)),
                            "edificios_todos": len(ie[e]), "variables": " ".join(ests[e].vars),
                            "k_final": k, "k_todos": int(k_todos[e])})
            if k == 1:
                continue
            g = etiquetas[(e, k)]
            mapa = emparejar(g, ref[filas[e]])
            asig[filas[e]] = pd.Series(g).map(mapa).to_numpy()
            filas_k[-1]["ari"] = round(adjusted_rand_score(ref[filas[e]], g), 4)
            filas_k[-1]["concordancia"] = round(float((asig[filas[e]] == ref[filas[e]]).mean()), 4)
        nuevo[sol] = asig
        area = v["area_construida"]
        for c in sorted(pd.unique(ref)):
            m_ref, m_new = ref == c, asig == c
            filas_arq.append({"solucion": sol, "arquetipo": c, "estrato": estrato[m_ref][0],
                              "viviendas_final": int(m_ref.sum()), "viviendas_todos": int(m_new.sum()),
                              "conserva": round(float((asig[m_ref] == c).mean()), 4),
                              "area_mediana_final": round(float(area[m_ref].median()), 1),
                              "area_mediana_todos": round(float(area[m_new].median()), 1) if m_new.any() else None})
        resumen[sol] = {"algoritmo": alg, "K_final": int(k_final.sum()), "K_todos": int(K_todos),
                        "R2_final": round(float(r2(y, ref)), 4), "R2_todos_mismo_k": round(float(r2(y, asig)), 4),
                        "R2_todos_k_propio": round(float(r2_todos), 4),
                        "viviendas_que_conservan_arquetipo": round(float((asig == ref).mean()), 4)}
        print(json.dumps(resumen[sol], ensure_ascii=False), flush=True)

    resumen["edificios_ajuste"] = int(len(idx))
    resumen["tiempo_s"] = round(time.time() - t_ini)
    pd.DataFrame(filas_k).to_csv(TABLAS / f"todos_k{suf}.csv", index=False, encoding="utf-8-sig")
    tabla = pd.DataFrame(filas_arq)
    tabla.to_csv(TABLAS / f"todos_arquetipos{suf}.csv", index=False, encoding="utf-8-sig")
    (TABLAS / f"todos_resumen{suf}.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    nuevo.to_parquet(INTERNOS / f"arquetipos_todos_edificios{suf}.parquet")
    print(pd.DataFrame(filas_k).to_string(index=False))
    print(tabla.to_string(index=False))
    print(f"tiempo total: {resumen['tiempo_s']} s")


if __name__ == "__main__":
    main()
