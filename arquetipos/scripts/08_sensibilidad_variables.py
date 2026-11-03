"""Paso 7, Sección 10.4: sensibilidad de las soluciones finales a las variables de agrupamiento (preregistro, v5).

Para cada solución final y cada variable, repite el agrupamiento de los estratos con más de un grupo sin esa variable
(mismo algoritmo, submuestra, k y semilla; atípicos de DBSCAN recalculados sin ella) y lo compara con la solución
final por el índice de Rand ajustado y el R² de la carga. La primera fila de cada solución es el control con las seis
variables, que debe reproducir la solución final.
Salida: salidas/tablas/val_sensibilidad_variables.csv
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import adjusted_rand_score

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.agrupamiento import (VARIABLES, Estrato, Modelo, atipicos, fijar_variables, preparar, submuestra,  # noqa: E402
                              suma_cuadrados)
from src.comun import DECISION, INTERNOS, POSICIONES, SEMILLA, TABLAS, asignar_epoca_faltante, cargar_viviendas  # noqa: E402

S = DECISION["paso7_v5"]["sensibilidad"]
LEGIBLE = {None: "ninguna (control)", "log_area": "área", "log_plantas": "pisos de la unidad",
           "log_piso": "piso de la unidad", "epoca_ord": "época", "tipo_bin": "tipo (multifamiliar)",
           "ph": "propiedad horizontal", "log_habitaciones": "habitaciones", "log_banios": "baños",
           "log_terreno": "área del terreno", "vis_vip": "VIS o VIP"}


def sin_variable(x, quitar):
    """Copia de las variables con `quitar` constante: Estrato la descarta porque su moda cubre el 100 %."""
    xs = x.copy()
    if quitar:
        xs[quitar] = 0
    return xs


def ruido_por_posicion(v, xs, idx, original=None):
    """Atípicos de DBSCAN por posición, como en la Sección 7.4. Si sin la variable el codo de las k-distancias cae
    en ε = 0 (las variables que quedan son casi todas discretas y muchas viviendas son idénticas), DBSCAN no está
    definido y se conservan los atípicos originales de esa posición."""
    ruido, originales = pd.Series(False, index=idx), []
    for p in POSICIONES:
        ip = idx[(v.loc[idx, "posicion"] == p).to_numpy()]
        try:
            ruido.loc[ip] = atipicos(Estrato(p, xs.loc[ip]))[0]
        except ValueError:
            ruido.loc[ip] = original.loc[ip]
            originales.append(p)
    return ruido, originales


def una_variable(v, x, idx, estrato, cargas, finales, sol, f, quitar, ruido_original):
    """Repite el agrupamiento de los estratos con más de un grupo sin la variable `quitar` y lo compara con la
    solución final."""
    xs = sin_variable(x, quitar)
    ruido, originales = ruido_por_posicion(v, xs, idx, ruido_original)
    k_est = pd.read_csv(TABLAS / f"arquetipos_{sol}.csv").groupby("estrato_algoritmo").size()
    multi = {e: int(k) for e, k in k_est.items() if k > 1}
    en_multi = estrato.isin(list(multi)).to_numpy()
    ref = finales[sol].to_numpy()
    etiqueta = ref.astype(object).copy()
    usadas, sin_ajuste = [], []  # usadas: variables que entran en esos estratos con todas las variables
    for e, k in multi.items():
        ie = idx[(estrato.loc[idx] == e).to_numpy()]
        usadas += Estrato(e, x.loc[ie]).vars
        est = Estrato(e, xs.loc[ie])
        try:
            mod = Modelo(f["algoritmo_final"], est, k, np.flatnonzero(~ruido.loc[ie].to_numpy()))
        except ValueError:  # con las variables que quedan hay menos perfiles distintos que grupos
            sin_ajuste.append(e)
            continue
        mask = (estrato == e).to_numpy()
        etiqueta[mask] = [f"{e}#{g}" for g in mod.asignar(xs.loc[mask])]
    y = cargas[sol]
    sst = float(((y - y.mean()) ** 2).sum())
    r2_final = 1 - suma_cuadrados(y, ref) / sst
    aplica = quitar is None or quitar in usadas
    fila = dict(solucion=sol, variables=f.get("variables", "base"), algoritmo=f["algoritmo_final"],
                variable_quitada=LEGIBLE[quitar], aplica=aplica, atipicos_originales_en=", ".join(originales),
                sin_k_grupos_en=", ".join(sin_ajuste),
                estratos_con_varios_grupos="; ".join(f"{e} (k={k})" for e, k in multi.items()),
                viviendas_en_esos_estratos=int(en_multi.sum()), R2_final=round(r2_final, 4))
    if sin_ajuste:  # sin la variable no se pueden formar los k grupos: la variable es imprescindible
        fila.update(rand_ajustado=np.nan, rand_ajustado_en_esos_estratos=np.nan, R2=np.nan, delta_R2=np.nan,
                    influyente=aplica)
    else:
        r2 = 1 - suma_cuadrados(y, etiqueta) / sst
        ari = adjusted_rand_score(ref, etiqueta)
        fila.update(rand_ajustado=round(ari, 4),
                    rand_ajustado_en_esos_estratos=round(adjusted_rand_score(ref[en_multi], etiqueta[en_multi]), 4),
                    R2=round(r2, 4), delta_R2=round(r2 - r2_final, 4),
                    influyente=bool(quitar and aplica and (ari < S["rand_min"] or r2 - r2_final <= -S["caida_R2"])))
    return fila


def main():
    v = cargar_viviendas()
    asignar_epoca_faltante(v)
    x = preparar(v)
    cc = pd.read_parquet(INTERNOS / "carga_viviendas.parquet")
    cargas = {"por_vivienda": cc["total"].to_numpy(float), "por_m2": cc["por_m2"].to_numpy(float)}
    finales = pd.read_parquet(INTERNOS / "arquetipos_final.parquet")
    final = json.loads((TABLAS / "agr_resultado_final.json").read_text(encoding="utf-8"))
    idx = submuestra(v, np.random.default_rng(SEMILLA))
    estrato = v["posicion"].astype(str) + "|" + v["bloque"]

    filas = []
    for sol in ["por_vivienda", "por_m2"]:
        f = final[sol]
        assert f["diseno_adoptado"] == "anidado", sol
        conjunto = f.get("variables", "base")  # Nota 8: las variables del agrupamiento ganador
        fijar_variables(conjunto)
        ruido_original, _ = ruido_por_posicion(v, x, idx)
        for quitar in [None] + VARIABLES[conjunto]:
            t0 = time.time()
            filas.append(una_variable(v, x, idx, estrato, cargas, finales, sol, f, quitar, ruido_original))
            print(filas[-1], flush=True)
            print(f"  {sol}, {LEGIBLE[quitar]}: {time.time() - t0:.0f} s", flush=True)
    tabla = pd.DataFrame(filas)
    tabla.to_csv(TABLAS / "val_sensibilidad_variables.csv", index=False, encoding="utf-8-sig")
    print(tabla.drop(columns="estratos_con_varios_grupos").to_string())


if __name__ == "__main__":
    main()
