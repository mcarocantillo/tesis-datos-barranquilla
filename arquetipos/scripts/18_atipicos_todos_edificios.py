"""Atípicos (DBSCAN) con todos los edificios: completa la prueba de robustez del script 14.

El script 14 ajustó la solución final con una vivienda de cada uno de los 177.093 edificios, pero sin excluir atípicos,
porque DBSCAN sobre la matriz de Gower de todos los pares no cabe en memoria (unos 96 GB solo en las casas). Este script
aplica la regla de la Sección 7.4 del preregistro a todos los edificios sin esa matriz:

  - Con las variables de agrupamiento, la distancia de Gower es la distancia de Manhattan sobre las variables
    reescaladas, dividida por el número de variables: las numéricas y la época divididas por su rango, y el tipo y la
    PH, que valen 0 o 1, sin cambio. El recorte en 1 de la Gower no actúa, porque el rango se calcula con los mismos
    puntos. Así, los vecinos dentro de ε se buscan con un árbol, sin calcular todos los pares.
  - Los edificios con las mismas variables se reúnen en un punto con peso. DBSCAN con pesos equivale a repetir los
    puntos, y la curva de k-distancias se arma repitiendo la de cada punto tantas veces como su peso.

Pasos:
  0. Verificación: en la submuestra del script 03, el método da los mismos ε y los mismos atípicos que la Gower
     completa. Si no coinciden, el script se detiene.
  1. DBSCAN dentro de cada posición con todos los edificios: min_samples = 2 × variables y ε en el codo.
  2. Ajuste de la solución final (diseño anidado; k-prototypes por vivienda y K-Means por m²) con todos los edificios
     menos los atípicos, con el k final de cada estrato, y asignación de todas las viviendas. Los grupos se emparejan
     con los arquetipos finales por el método húngaro, como en el script 14.
El barrido de k del script 14 (unas 9 horas) y la silueta no se repiten.

Uso: python scripts/18_atipicos_todos_edificios.py
Salidas:
  salidas/tablas/dbscan_todos_verificacion.csv   paso 0, por posición
  salidas/tablas/dbscan_todos_atipicos.csv       paso 1, por posición
  salidas/tablas/dbscan_todos_arquetipos.csv     paso 2, por arquetipo
  salidas/tablas/dbscan_todos_resumen.json       R² y concordancias; tiempos
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from scipy.optimize import linear_sum_assignment
from sklearn.cluster import DBSCAN
from sklearn.metrics import adjusted_rand_score
from sklearn.neighbors import NearestNeighbors

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.agrupamiento import (A, NOMINALES, NUMERICAS, Estrato, Modelo, atipicos, fijar_variables, preparar,  # noqa: E402
                              submuestra)
from src.carga import r2  # noqa: E402
from src.comun import INTERNOS, POSICIONES, SEMILLA, TABLAS, asignar_epoca_faltante, cargar_viviendas  # noqa: E402

MEDIDA = {"por_vivienda": "total", "por_m2": "por_m2"}
HOLGURA = 1e-6  # empates en ε: la Gower original se calculó en float32


def variables_de(x_pos):
    """Variables de la posición, con la misma regla que Estrato (se descarta la que tenga moda del 99 % o más)."""
    moda = x_pos.apply(lambda s: s.value_counts(normalize=True).iloc[0])
    return [c for c in A_CANDIDATAS if moda[c] < A["descartar_si_moda_cubre"]]


def reescalar(x_pos, variables, rango):
    """Matriz en la que la distancia de Manhattan es la Gower de la Sección 7.4."""
    cols = [x_pos[c].to_numpy(float) if c in NOMINALES else x_pos[c].to_numpy(float) / rango[c] for c in variables]
    return np.column_stack(cols) / len(variables)


def dbscan_l1(z):
    """Regla de la Sección 7.4 sobre la matriz reescalada, con los puntos repetidos reunidos por peso."""
    ms = 2 * z.shape[1]
    zu, inv, w = np.unique(np.round(z, 12), axis=0, return_inverse=True, return_counts=True)
    inv = inv.ravel()
    nn = NearestNeighbors(n_neighbors=min(ms, len(zu)), metric="manhattan").fit(zu)
    dist, vec = nn.kneighbors(zu)
    acum = np.cumsum(w[vec], axis=1)
    kd_u = dist[np.arange(len(zu)), np.argmax(acum >= ms, axis=1)]
    kd = np.sort(np.repeat(kd_u, w))
    xs = np.linspace(0, 1, len(kd))
    ys = (kd - kd[0]) / max(kd[-1] - kd[0], 1e-12)
    eps = float(kd[int(np.argmax(xs - ys))])
    lab = DBSCAN(eps=eps + HOLGURA, min_samples=ms, metric="manhattan").fit(zu, sample_weight=w).labels_
    return lab[inv] == -1, eps, ms, len(zu)


def emparejar(g, ref):
    """Arquetipo final de cada grupo (método húngaro sobre el número de viviendas), como en el script 14."""
    tabla = pd.crosstab(g, ref)
    fila, col = linear_sum_assignment(-tabla.to_numpy())
    return dict(zip(tabla.index[fila], tabla.columns[col]))


class EstratoSinGower(Estrato):
    """Como Estrato, pero sin la matriz de Gower, que con todos los edificios no cabe en memoria."""

    def __init__(self, nombre, x_ajuste):
        self.nombre = nombre
        moda = x_ajuste.apply(lambda s: s.value_counts(normalize=True).iloc[0])
        self.vars = [c for c in A_CANDIDATAS if moda[c] < A["descartar_si_moda_cubre"]]
        self.num = [c for c in self.vars if c in NUMERICAS]
        self.cat = [c for c in self.vars if c not in NUMERICAS]
        self.x = x_ajuste
        self.mu = x_ajuste[self.vars].mean()
        self.sd = x_ajuste[self.vars].std(ddof=0)
        self.rango = (x_ajuste[self.vars].max() - x_ajuste[self.vars].min()).replace(0, 1)


def ajustar(alg, est, k, x_e):
    t0 = time.time()
    g = Modelo(alg, est, k, np.arange(len(est.x))).asignar(x_e).astype(np.int16)
    return est.nombre, g, time.time() - t0


def main():
    global A_CANDIDATAS
    t_ini = time.time()
    fijar_variables("base")
    from src import agrupamiento as ag
    A_CANDIDATAS = ag._candidatas

    v = cargar_viviendas()
    asignar_epoca_faltante(v)
    x = preparar(v)
    pos = v["posicion"].astype(str).to_numpy()

    # 0. verificación en la submuestra del script 03
    idx_sub = submuestra(v, np.random.default_rng(SEMILLA))
    previo = pd.read_csv(TABLAS / "agr_atipicos.csv").set_index("posicion")
    filas_ver = []
    for p in POSICIONES:
        ip = idx_sub[pos[idx_sub] == p]
        est = Estrato(p, x.loc[ip])
        r_gower, eps_g, ms_g = atipicos(est)
        r_l1, eps_l1, ms_l1, n_u = dbscan_l1(reescalar(x.loc[ip], est.vars, est.rango))
        filas_ver.append({"posicion": p, "edificios": len(ip), "min_samples": ms_g, "eps_gower": round(eps_g, 6),
                          "eps_manhattan": round(eps_l1, 6), "atipicos_gower": int(r_gower.sum()),
                          "atipicos_manhattan": int(r_l1.sum()), "atipicos_publicados": int(previo.loc[p, "atipicos"]),
                          "mismos_edificios": bool((r_gower == r_l1).all())})
        print(filas_ver[-1], flush=True)
    ver = pd.DataFrame(filas_ver)
    ver.to_csv(TABLAS / "dbscan_todos_verificacion.csv", index=False, encoding="utf-8-sig")
    if not (ver["mismos_edificios"].all() and (ver["atipicos_gower"] == ver["atipicos_publicados"]).all()):
        sys.exit("la distancia de Manhattan reescalada no reproduce los atípicos de la Gower: se detiene")

    # 1. DBSCAN con todos los edificios (la misma selección del script 14)
    rng = np.random.default_rng(SEMILLA)
    idx = np.concatenate([v[v["posicion"] == p].sample(frac=1, random_state=rng).drop_duplicates("edificio_id").index
                          for p in POSICIONES])
    ruido = pd.Series(False, index=idx)
    filas_at = []
    for p in POSICIONES:
        t0 = time.time()
        ip = idx[pos[idx] == p]
        vars_p = variables_de(x.loc[ip])
        rango = (x.loc[ip, vars_p].max() - x.loc[ip, vars_p].min()).replace(0, 1)
        r, eps, ms, n_u = dbscan_l1(reescalar(x.loc[ip], vars_p, rango))
        ruido.loc[ip] = r
        fila_prev = previo.loc[p]
        filas_at.append({"posicion": p, "edificios": len(ip), "combinaciones_distintas": n_u, "variables": " ".join(vars_p),
                         "min_samples": ms, "eps": round(eps, 4), "atipicos": int(r.sum()), "pct_atipicos": round(r.mean() * 100, 1),
                         "area_mediana_atipicos": float(v.loc[ip[r], "area_construida"].median()) if r.any() else None,
                         "area_mediana_resto": float(v.loc[ip[~r], "area_construida"].median()),
                         "pct_atipicos_submuestra": float(fila_prev["pct_atipicos"]), "eps_submuestra": float(fila_prev["eps"]),
                         "segundos": round(time.time() - t0)})
        print(filas_at[-1], flush=True)
    pd.DataFrame(filas_at).to_csv(TABLAS / "dbscan_todos_atipicos.csv", index=False, encoding="utf-8-sig")

    # 2. solución final ajustada sin los atípicos, con el k final de cada estrato
    cc = pd.read_parquet(INTERNOS / "carga_viviendas.parquet")
    finales = pd.read_parquet(INTERNOS / "arquetipos_final.parquet")
    todos = pd.read_parquet(INTERNOS / "arquetipos_todos_edificios.parquet")
    final = json.loads((TABLAS / "agr_resultado_final.json").read_text(encoding="utf-8"))
    estrato = (v["posicion"].astype(str) + "|" + v["bloque"]).to_numpy()
    sin_at = idx[~ruido.loc[idx].to_numpy()]
    filas_arq, resumen = [], {}
    for sol, medida in MEDIDA.items():
        f = final[sol]
        assert f["diseno_adoptado"] == "anidado" and f.get("variables", "base") == "base", sol
        alg = f["algoritmo_final"]
        y = cc[medida].to_numpy(float)
        ref = finales[sol].astype(str).to_numpy()
        ref14 = todos[sol].astype(str).to_numpy()
        k_final = pd.read_csv(TABLAS / f"arquetipos_{sol}.csv").groupby("estrato_algoritmo").size()
        filas = {e: np.flatnonzero(estrato == e) for e in k_final.index}
        pedidos = [e for e in k_final.index if k_final[e] > 1]
        t0 = time.time()
        res = Parallel(n_jobs=-1)(delayed(ajustar)(alg, EstratoSinGower(e, x.loc[sin_at[estrato[sin_at] == e]]), int(k_final[e]),
                                                   x.iloc[filas[e]]) for e in pedidos)
        asig, ari = ref.copy(), {}
        for e, g, seg in res:
            mapa = emparejar(g, ref[filas[e]])
            asig[filas[e]] = pd.Series(g).map(mapa).to_numpy()
            ari[e] = round(adjusted_rand_score(ref[filas[e]], g), 4)
        for c in sorted(pd.unique(ref)):
            m_ref = ref == c
            filas_arq.append({"solucion": sol, "arquetipo": c, "estrato": estrato[m_ref][0],
                              "viviendas_final": int(m_ref.sum()), "viviendas_sin_atipicos": int((asig == c).sum()),
                              "conserva_frente_a_final": round(float((asig[m_ref] == c).mean()), 4),
                              "conserva_frente_a_todos_con_atipicos": round(float((asig[ref14 == c] == c).mean()), 4)
                              if (ref14 == c).any() else None})
        resumen[sol] = {"algoritmo": alg, "K": int(k_final.sum()), "R2_final": round(float(r2(y, ref)), 4),
                        "R2_todos_con_atipicos": round(float(r2(y, ref14)), 4),
                        "R2_todos_sin_atipicos": round(float(r2(y, asig)), 4),
                        "conservan_frente_a_final": round(float((asig == ref).mean()), 4),
                        "conservan_frente_a_todos_con_atipicos": round(float((asig == ref14).mean()), 4),
                        "ari_por_estrato": ari, "segundos": round(time.time() - t0)}
        print(json.dumps(resumen[sol], ensure_ascii=False), flush=True)

    resumen["edificios_ajuste"] = int(len(idx))
    resumen["edificios_sin_atipicos"] = int(len(sin_at))
    resumen["tiempo_s"] = round(time.time() - t_ini)
    pd.DataFrame(filas_arq).to_csv(TABLAS / "dbscan_todos_arquetipos.csv", index=False, encoding="utf-8-sig")
    (TABLAS / "dbscan_todos_resumen.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"tiempo total: {resumen['tiempo_s']} s")


A_CANDIDATAS = None

if __name__ == "__main__":
    main()
