"""Pasos 2 a 4: agrupamiento, número de arquetipos, estabilidad y diseño plano frente a anidado.

Sigue la versión 2 del preregistro (Sección 7). Con --prueba corre una submuestra del 10 % y 5 submuestras de
Jaccard, solo para revisar que el código funciona; sus salidas llevan el sufijo «_prueba». Con --ampliada usa las
variables de la Nota 8 (habitaciones, baños, área del terreno y VIS o VIP) y sus salidas llevan el sufijo «_ampliada».

Salidas (salidas/tablas, prefijo «agr_»):
  agr_muestra.csv              edificios de la submuestra por posición, tipo y bloque
  agr_atipicos.csv             DBSCAN por posición: ε, min_samples y atípicos
  agr_camino_{diseño}.csv      frontera óptima: mejor R² de la ciudad para cada K, por algoritmo y medida (Nota 3)
  agr_metricas_{diseño}.csv    A1: silueta (Gower), Calinski-Harabasz y Davies-Bouldin por estrato y k
  agr_seleccion_{diseño}.csv   k, R², Jaccard y silueta de cada algoritmo; algoritmo elegido (Sección 7.7)
  agr_grupos_{diseño}_{medida}_{algoritmo}.csv  perfil de cada grupo, para los tres algoritmos
  agr_decision_paso4.json      regla del Paso 4 para cada algoritmo y análisis A5
  datos_internos/agrupamiento.parquet  arquetipo de cada vivienda en cada diseño, medida y algoritmo (no se publica)
"""
import argparse
import json
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter
from sklearn.metrics import calinski_harabasz_score, davies_bouldin_score, silhouette_score

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.agrupamiento import (A, ALGORITMOS, Estrato, Modelo, atipicos, elegir_k, fijar_variables, frontera, jaccard, preparar,
                              submuestra, suma_cuadrados)
from src.carga import eta2_estrato, eta2_por_grupo, v_cramer
from src.comun import DECISION, EPOCAS, FIGURAS, INTERNOS, SEMILLA, TABLAS, asignar_epoca_faltante, cargar_viviendas
from src.estilo import GREY, OCH, PET, INK, guardar, lienzo

UMBRAL = DECISION["carga"]["criterio"]["delta_R2_min"]
N3 = A["nota3"]
P4 = DECISION["paso4"]
CORTO = {"casa": "C", "ultimo_piso": "U", "sin_cubierta": "S"}
APLICA = "por_vivienda"  # medida vigente mientras el director no apruebe el cambio (AJ5)


def correr_diseno(diseno, v, x, cargas, idx, ruido, n_jaccard, log):
    """Recorrido completo de un diseño: barrido de k, recorrido voraz, Jaccard y elección del algoritmo."""
    estrato = v["posicion"].astype(str) if diseno == "plano" else v["posicion"].astype(str) + "|" + v["bloque"]
    kmax = A["k_por_estrato"][diseno][1]
    nombres = sorted(estrato.loc[idx].unique())
    ests, ajuste, mascaras = {}, {}, {}
    for e in nombres:
        ie = idx[(estrato.loc[idx] == e).to_numpy()]
        ests[e] = Estrato(e, x.loc[ie])
        ajuste[e] = np.flatnonzero(~ruido.loc[ie].to_numpy())
        mascaras[e] = (estrato == e).to_numpy()
        log(f"  {diseno} · {e}: {len(ie)} edificios ({len(ajuste[e])} sin atípicos); variables {ests[e].vars}")

    sst = {m: float(((q - q.mean()) ** 2).sum()) for m, q in cargas.items()}
    etiquetas, ssw, metricas = {}, {m: {a: {e: [] for e in ests} for a in ALGORITMOS} for m in cargas}, []

    def calcular(alg, e, k):
        est = ests[e]
        mod = Modelo(alg, est, k, ajuste[e])
        g = mod.asignar(x.loc[mascaras[e]]).astype(np.int16)
        etiquetas[(alg, e, k)] = (g, mod)
        for m, q in cargas.items():
            ssw[m][alg][e].append(suma_cuadrados(q[mascaras[e]], g))
        lab = mod.etiquetas
        if k >= 2 and len(np.unique(lab)) >= 2:
            pos = ajuste[e]
            zf = est.z(est.x.iloc[pos], est.vars)
            metricas.append({"estrato": e, "algoritmo": alg, "k": k, "k_real": len(np.unique(lab)),
                             "silueta_gower": silhouette_score(est.D[np.ix_(pos, pos)], lab, metric="precomputed"),
                             "calinski_harabasz": calinski_harabasz_score(zf, lab),
                             "davies_bouldin": davies_bouldin_score(zf, lab)})

    topes = {}
    for alg in ALGORITMOS:
        t0 = time.time()
        tope = {e: kmax for e in ests}
        for e in ests:
            for k in range(1, kmax + 1):
                calcular(alg, e, k)
        while True:  # Nota 3: ampliar el máximo de un estrato si la solución elegida lo alcanza
            ampliar = set()
            for m in cargas:
                front = frontera({e: ssw[m][alg][e] for e in ests}, sst[m])
                for e, k in front[elegir_k(front, UMBRAL)][2].items():
                    if k == tope[e] and tope[e] < N3["tope_seguridad"]:
                        ampliar.add(e)
            if not ampliar:
                break
            for e in sorted(ampliar):
                nuevo = min(tope[e] + N3["ampliar_tope"], N3["tope_seguridad"])
                for k in range(tope[e] + 1, nuevo + 1):
                    calcular(alg, e, k)
                log(f"  {diseno} · {alg}: máximo de {e} ampliado de {tope[e]} a {nuevo}")
                tope[e] = nuevo
        topes[alg] = tope
        log(f"  {diseno} · {alg}: barrido de k en {time.time() - t0:.0f} s")

    filas_camino, seleccion, grupos_sel = [], [], {}
    cache_j = {}
    for m in cargas:
        for alg in ALGORITMOS:
            front = frontera({e: ssw[m][alg][e] for e in ests}, sst[m])
            i_sel = elegir_k(front, UMBRAL)
            for i, (K, r2, kd) in enumerate(front):
                filas_camino.append({"medida": m, "algoritmo": alg, "k": K, "R2": r2,
                                     "ganancia_siguiente": front[i + 1][1] - r2 if i + 1 < len(front) else np.nan,
                                     "elegido": i == i_sel, **{f"k_{e}": kd[e] for e in kd}})
            k_sel, r2_sel = front[i_sel][2], front[i_sel][1]
            # Jaccard por grupo, peso = fracción de viviendas de la ciudad
            jg, peso, sil, n_sil, ids = [], [], 0.0, 0, []
            for e, est in ests.items():
                k = k_sel[e]
                g, mod = etiquetas[(alg, e, k)]
                clave = (alg, e, k)
                if clave not in cache_j:
                    t0 = time.time()
                    cache_j[clave] = jaccard(alg, est, k, ajuste[e], mod.etiquetas, n_jaccard, A["jaccard"]["fraccion"])
                    log(f"  {diseno} · Jaccard {alg} {e} k={k}: {time.time() - t0:.0f} s")
                j = cache_j[clave]
                for h in range(len(j)):
                    jg.append(j[h])
                    peso.append((g == h).sum() / len(v))
                    ids.append((e, h))
                if k >= 2 and len(np.unique(mod.etiquetas)) >= 2:
                    pos = ajuste[e]
                    sil += silhouette_score(est.D[np.ix_(pos, pos)], mod.etiquetas, metric="precomputed") * len(pos)
                    n_sil += len(pos)
            jg, peso = np.array(jg), np.array(peso)
            grandes = peso > P4["frac_grupo_relevante"]
            seleccion.append({"medida": m, "algoritmo": alg, "k": sum(k_sel.values()), **{f"k_{e}": k_sel[e] for e in k_sel},
                              "R2": r2_sel, "jaccard_ponderado": float((jg * peso).sum() / peso.sum()),
                              "jaccard_min_grupos_grandes": float(jg[grandes].min()) if grandes.any() else np.nan,
                              "silueta_gower": sil / n_sil if n_sil else np.nan})
            grupos_sel[(m, alg)] = (k_sel, dict(zip(ids, jg)))

    sel = pd.DataFrame(seleccion)
    for m in cargas:
        s = sel[sel.medida == m].sort_values("jaccard_ponderado", ascending=False).reset_index()
        criterio = "Jaccard"
        if len(s) > 1 and s.jaccard_ponderado[0] - s.jaccard_ponderado[1] < 0.02:
            empate = s[s.jaccard_ponderado >= s.jaccard_ponderado[0] - 0.02].sort_values("silueta_gower", ascending=False)
            criterio = "silueta"
            if len(empate) > 1 and empate.silueta_gower.iloc[0] - empate.silueta_gower.iloc[1] < 0.02:
                empate = empate[empate.silueta_gower >= empate.silueta_gower.iloc[0] - 0.02].sort_values("R2", ascending=False)
                criterio = "R2"
            ganador = empate.algoritmo.iloc[0]
        else:
            ganador = s.algoritmo[0]
        sel.loc[(sel.medida == m), "elegido"] = sel.loc[(sel.medida == m), "algoritmo"] == ganador
        sel.loc[(sel.medida == m) & (sel.algoritmo == ganador), "criterio"] = criterio
    return (estrato, ests, etiquetas, sel, pd.DataFrame(filas_camino), pd.DataFrame(metricas), grupos_sel, ajuste,
            mascaras, topes)


def perfil(diseno, m, alg, k_sel, jac, v, estrato, etiquetas, cargas):
    """Arquetipos de la solución elegida, numerados dentro de cada estrato por área mediana."""
    arq = pd.Series(index=v.index, dtype=object)
    filas = []
    for e in sorted(k_sel):
        g, _ = etiquetas[(alg, e, k_sel[e])]
        mask = (estrato == e).to_numpy()
        orden = pd.Series(v.loc[mask, "area_construida"].to_numpy()).groupby(g).median().sort_values().index
        pos, bloque = (e.split("|") + [None])[:2]
        pref = CORTO[pos] + (bloque.replace("-", "") if bloque else "")
        for i, h in enumerate(orden, 1):
            nombre = f"{pref}-{i}"
            sel = np.flatnonzero(mask)[g == h]
            arq.iloc[sel] = nombre
            vv = v.iloc[sel]
            fila = {"arquetipo": nombre, "estrato_algoritmo": e, "viviendas": len(sel),
                    "pct_viviendas": round(len(sel) / len(v) * 100, 2), "edificios": vv["edificio_id"].nunique(),
                    "jaccard": round(float(jac[(e, h)]), 3),
                    "area_p25": vv["area_construida"].quantile(.25), "area_mediana": vv["area_construida"].median(),
                    "area_p75": vv["area_construida"].quantile(.75),
                    "plantas_mediana": vv["total_plantas"].median(), "piso_mediana": vv["planta_ubicacion"].median(),
                    "pct_ph": round(vv["condicion_predio"].astype(str).str.startswith("PH").mean() * 100, 1),
                    "pct_multifamiliar": round((vv["tipo"] == "multifamiliar").mean() * 100, 1),
                    "carga_mediana_kWh": round(float(np.median(cargas["por_vivienda"][sel])), 0),
                    "carga_m2_mediana_kWh": round(float(np.median(cargas["por_m2"][sel])), 1)}
            fila.update({f"pct_{ep}": round((vv["epoca"] == ep).mean() * 100, 1) for ep in EPOCAS})
            fila.update({f"pct_E{s}": round((vv["estrato_num"] == s).mean() * 100, 1) for s in range(1, 7)})
            filas.append(fila)
    return arq, pd.DataFrame(filas)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prueba", action="store_true")
    ap.add_argument("--ampliada", action="store_true", help="variante con las variables de la Nota 8")
    args = ap.parse_args()
    suf = ("_ampliada" if args.ampliada else "") + ("_prueba" if args.prueba else "")
    fijar_variables("ampliada" if args.ampliada else "base")
    n_jaccard = 5 if args.prueba else A["jaccard"]["submuestras"]
    if args.prueba:
        A["submuestra"]["tamano"] = {p: n // 10 for p, n in A["submuestra"]["tamano"].items()}
    t_ini = time.time()
    registro = []

    def log(s):
        print(s, flush=True)
        registro.append(s)

    v = cargar_viviendas()
    asignar_epoca_faltante(v)
    x = preparar(v)
    cc = pd.read_parquet(INTERNOS / "carga_viviendas.parquet")
    cargas = {"por_vivienda": cc["total"].to_numpy(float), "por_m2": cc["por_m2"].to_numpy(float)}

    idx = submuestra(v, np.random.default_rng(SEMILLA))
    muestra = v.loc[idx].groupby(["posicion", "tipo", "bloque"], observed=True).size().rename("edificios")
    muestra.to_csv(TABLAS / f"agr_muestra{suf}.csv", encoding="utf-8-sig")
    log(f"submuestra: {len(idx)} edificios\n{muestra.groupby(level=0).sum().to_string()}")

    # atípicos (DBSCAN) dentro de cada posición
    ruido = pd.Series(False, index=idx)
    filas = []
    for p in ["casa", "ultimo_piso", "sin_cubierta"]:
        ip = idx[(v.loc[idx, "posicion"] == p).to_numpy()]
        est = Estrato(p, x.loc[ip])
        r, eps, ms = atipicos(est)
        ruido.loc[ip] = r
        xa = v.loc[ip[r]]
        filas.append({"posicion": p, "edificios": len(ip), "min_samples": ms, "eps": round(eps, 4), "atipicos": int(r.sum()),
                      "pct_atipicos": round(r.mean() * 100, 1),
                      "area_mediana_atipicos": xa["area_construida"].median() if len(xa) else np.nan,
                      "area_mediana_resto": v.loc[ip[~r], "area_construida"].median()})
        log(f"DBSCAN {p}: min_samples={ms}, eps={eps:.4f}, atípicos={r.sum()} ({r.mean() * 100:.1f} %)")
    pd.DataFrame(filas).to_csv(TABLAS / f"agr_atipicos{suf}.csv", index=False, encoding="utf-8-sig")

    asign = pd.DataFrame(index=v.index)
    resultados = {}
    for diseno in ["plano", "anidado"]:
        log(f"\n=== diseño {diseno} ===")
        estrato, ests, etiquetas, sel, camino, metricas, grupos_sel, ajuste, mascaras, topes = correr_diseno(
            diseno, v, x, cargas, idx, ruido, n_jaccard, log)
        camino.to_csv(TABLAS / f"agr_camino_{diseno}{suf}.csv", index=False, encoding="utf-8-sig")
        metricas.to_csv(TABLAS / f"agr_metricas_{diseno}{suf}.csv", index=False, encoding="utf-8-sig")
        # estabilidad con los umbrales de Hennig de la Sección 4 (información; la elección sigue la Sección 7.7)
        sel["pasa_estabilidad"] = ((sel.jaccard_ponderado >= P4["jaccard_ponderado_min"])
                                   & ~(sel.jaccard_min_grupos_grandes < P4["jaccard_grupo_min"]))
        sel.to_csv(TABLAS / f"agr_seleccion_{diseno}{suf}.csv", index=False, encoding="utf-8-sig")
        log(sel.drop(columns=[c for c in sel.columns if c.startswith("k_")]).round(3).to_string(index=False))
        # se guardan los tres algoritmos, para poder aplicar cualquier regla de elección sin volver a correr
        for m in cargas:
            for _, fila in sel[sel.medida == m].iterrows():
                k_sel, jac = grupos_sel[(m, fila.algoritmo)]
                arq, prof = perfil(diseno, m, fila.algoritmo, k_sel, jac, v, estrato, etiquetas, cargas)
                prof.to_csv(TABLAS / f"agr_grupos_{diseno}_{m}_{fila.algoritmo}{suf}.csv", index=False, encoding="utf-8-sig")
                asign[f"{diseno}_{m}_{fila.algoritmo}"] = arq.to_numpy()
                resultados[(diseno, m, fila.algoritmo)] = (fila, prof, arq, k_sel, ests, etiquetas, ajuste, mascaras,
                                                           estrato, topes)

    # Paso 4: regla preregistrada sobre el diseño plano, para cada medida de carga y cada algoritmo
    decision = {"medida_que_aplica": APLICA}
    for m in cargas:
        decision[m] = {}
        for alg in ALGORITMOS:
            fila, prof, arq, *_ = resultados[("plano", m, alg)]
            grandes = prof[prof.pct_viviendas > P4["frac_grupo_relevante"] * 100]
            inestable = bool((grandes.jaccard < P4["jaccard_grupo_min"]).any()
                             or fila.jaccard_ponderado < P4["jaccard_ponderado_min"])
            eta2 = float(eta2_estrato(cargas[m], arq.to_numpy(), v["estrato_num"]))
            fa = resultados[("anidado", m, alg)][0]
            decision[m][alg] = {
                "elegido_regla_7_7": bool(fila.elegido), "k_plano": int(fila.k), "R2_plano": round(float(fila.R2), 4),
                "jaccard_ponderado": round(float(fila.jaccard_ponderado), 3),
                "grupos_grandes_con_jaccard_bajo": grandes.loc[grandes.jaccard < P4["jaccard_grupo_min"], "arquetipo"].tolist(),
                "plano_inestable": inestable, "eta2_estrato": round(eta2, 4),
                "v_cramer_estrato": round(v_cramer(arq.to_numpy(), v["estrato_num"]), 3),
                "eta2_por_grupo": {g: round(e, 4) for g, e in eta2_por_grupo(cargas[m], arq.to_numpy(),
                                                                               v["estrato_num"]).items()},
                "diseno_adoptado": "anidado" if (inestable or eta2 >= P4["eta2_umbral"]) else "plano",
                "k_anidado": int(fa.k), "R2_anidado": round(float(fa.R2), 4)}

    # A5: el diseño plano elegido sin excluir los atípicos de DBSCAN
    alg_v2 = next(a for a in ALGORITMOS if decision[APLICA][a]["elegido_regla_7_7"])
    fila, _, _, _, ests, _, _, mascaras, _, topes = resultados[("plano", APLICA, alg_v2)]
    ssw = {}
    for e, est in ests.items():
        xe = x.loc[mascaras[e]]
        todos = np.arange(len(est.x))
        ssw[e] = [suma_cuadrados(cargas[APLICA][mascaras[e]], Modelo(fila.algoritmo, est, k, todos).asignar(xe))
                  for k in range(1, topes[fila.algoritmo][e] + 1)]
    sst = float(((cargas[APLICA] - cargas[APLICA].mean()) ** 2).sum())
    front = frontera(ssw, sst)
    i_sel = elegir_k(front, UMBRAL)
    decision["A5_sin_excluir_atipicos"] = {"algoritmo": fila.algoritmo, "k": int(front[i_sel][0]),
                                           "R2": round(front[i_sel][1], 4)}
    decision["tiempo_s"] = round(time.time() - t_ini)
    (TABLAS / f"agr_decision_paso4{suf}.json").write_text(json.dumps(decision, ensure_ascii=False, indent=2), encoding="utf-8")
    log("\nPaso 4:\n" + json.dumps(decision, ensure_ascii=False, indent=2))

    INTERNOS.mkdir(exist_ok=True)
    asign.to_parquet(INTERNOS / f"agrupamiento{suf}.parquet")

    # figura: R² de la ciudad frente a k en el recorrido voraz del diseño plano
    camino = pd.read_csv(TABLAS / f"agr_camino_plano{suf}.csv")
    reglas = pd.read_csv(TABLAS / "carga_r2_reglas.csv", index_col=0)
    coma = FuncFormatter(lambda y, _: f"{y:.1f}".replace(".", ","))
    fig, axs = lienzo(16, 8)
    fig.clf()
    axs = fig.subplots(1, 2, sharey=True)
    for ax, m, titulo, fila_reglas in [(axs[0], "por_vivienda", "Carga por vivienda", "R2 carga por vivienda"),
                                       (axs[1], "por_m2", "Carga por m²", "A3: R2 carga por m2")]:
        for alg, color, ls in [("kmeans", INK, "-"), ("kprototypes", PET, "--"), ("jerarquico", OCH, ":")]:
            c = camino[(camino.medida == m) & (camino.algoritmo == alg)]
            ax.plot(c.k, c.R2, color=color, ls=ls, lw=1.1, label=alg.replace("kmeans", "K-Means").replace(
                "kprototypes", "k-prototypes").replace("jerarquico", "Jerárquico (Gower)"))
            e = c[c.elegido]
            ax.scatter(e.k, e.R2, color=color, zorder=3, s=18)
        ax.scatter([reglas.loc["k", "base"]], [reglas.loc[fila_reglas, "base"]], marker="s", color=GREY, s=18,
                   label="Tipología por reglas")
        ax.set_title(titulo, fontsize=8)
        ax.set_xlabel("Número de arquetipos, k")
        ax.yaxis.set_major_formatter(coma)
        ax.set_ylim(0, 1.02)
    axs[0].set_ylabel("Fracción de la varianza de la carga explicada (R²)")
    axs[1].legend(frameon=False, loc="lower right", fontsize=7)
    guardar(fig, FIGURAS / f"agr_r2_k{suf}.png")
    log(f"\ntiempo total: {time.time() - t_ini:.0f} s")
    (TABLAS / f"agr_registro{suf}.txt").write_text("\n".join(registro), encoding="utf-8")


if __name__ == "__main__":
    main()
