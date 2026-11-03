"""Paso 5: árbol de decisión y Random Forest que asignan las viviendas a los arquetipos (preregistro, versión 3).

Para cada solución final (carga por vivienda y carga por m²): búsqueda de hiperparámetros con los 5 pliegues kNNDM
del trabajo previo, evaluación en los 7 bloques de prueba de 2 km, reglas legibles del árbol y probabilidades de
asignación para la Fase 2. Con --prueba usa el 10 % de las viviendas de entrenamiento (solo para revisar el código).

Salidas (salidas/tablas, prefijo «clf_», y sufijo de la solución):
  clf_cv_{sol}.csv            F1 macro de validación de cada configuración
  clf_metricas_{sol}.json     métricas de prueba de los dos modelos y su rango entre bloques
  clf_recall_{sol}.csv        recall por arquetipo en la prueba
  clf_probabilidades_{sol}.csv  probabilidad media de pertenencia y fracción con probabilidad < 0,8, por arquetipo
  clf_reglas_arbol_{sol}.txt  reglas del árbol en unidades legibles
  salidas/modelos/arbol_{sol}.joblib           árbol entrenado (clasificador publicable)
  datos_internos/bosque_{sol}.joblib           Random Forest (no se publica: puede memorizar registros)
  datos_internos/probabilidades_{sol}.parquet  probabilidades de cada vivienda (no se publica)
"""
import argparse
import json
import sys
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, log_loss, recall_score
from sklearn.tree import DecisionTreeClassifier

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.append(str(RAIZ.parent / "e4"))  # módulos del trabajo previo (kNNDM); al final, porque e4 tiene su propio src
from e1 import vecinos as V  # noqa: E402
from src.agrupamiento import preparar  # noqa: E402
from src.comun import DECISION, EPOCAS, INTERNOS, ML, SEMILLA, TABLAS, asignar_epoca_faltante, cargar_viviendas  # noqa: E402

P = DECISION["clasificador_v3"]
MODELOS = RAIZ / "salidas" / "modelos"
LEGIBLE = {"log_area": "área", "log_plantas": "pisos de la unidad", "log_piso": "piso de la unidad",
           "log_habitaciones": "habitaciones", "log_banios": "baños", "log_terreno": "área del terreno"}
COLUMNAS = {"base": ["log_area", "log_plantas", "log_piso", "epoca_ord", "tipo_bin", "ph"]}
COLUMNAS["ampliada"] = COLUMNAS["base"] + ["log_habitaciones", "log_banios", "log_terreno", "vis_vip"]  # Nota 8


def matriz(v, variables="base"):
    x = preparar(v)[COLUMNAS[variables]]
    x = x.join(pd.get_dummies(v["posicion"].astype(str), prefix="pos").astype(float))
    return x.join(pd.get_dummies(v["bloque"], prefix="bloque").astype(float)).astype(float)


def pliegues(v, n_con, entrenamiento, prueba):
    """Los 5 pliegues kNNDM del trabajo previo (zonas nuevas), con caché en datos_internos."""
    cache = INTERNOS / "pliegues_knndm.npz"
    if cache.exists():
        z = np.load(cache)
        return [(z[f"tr{i}"], z[f"va{i}"]) for i in range(len(z.files) // 2)]
    m = pd.read_parquet(ML / "e1_git" / "datos" / "procesados" / "dataset_modelado.parquet",
                        columns=["x_km", "y_km", "npn_edificio", "estrato_num"])
    assert len(m) == n_con and (m["estrato_num"].to_numpy() == v["estrato_num"].to_numpy()[:n_con]).all()
    xy = m[["x_km", "y_km"]].to_numpy()
    tr, te = entrenamiento[:n_con], prueba[:n_con]
    xy_te, n_te, _ = V.puntos_unicos(xy[te], m["npn_edificio"].to_numpy()[te])
    kn = V.knndm(xy[tr], m["npn_edificio"].to_numpy()[tr], m["estrato_num"].to_numpy()[tr], xy_te, n_te, seed=SEMILLA)
    INTERNOS.mkdir(exist_ok=True)
    np.savez(cache, **{f"tr{i}": a for i, (a, b) in enumerate(kn["folds"])}, **{f"va{i}": b for i, (a, b) in enumerate(kn["folds"])})
    return kn["folds"]


def brier(y, proba, clases):
    uno = (np.asarray(y)[:, None] == np.asarray(clases)[None, :]).astype(float)
    return float(((proba - uno) ** 2).sum(1).mean())


def proba_completa(modelo, x, clases):
    """Probabilidades con una columna por cada arquetipo, aunque el modelo no haya visto alguno."""
    p = np.zeros((len(x), len(clases)))
    p[:, np.searchsorted(clases, modelo.classes_)] = modelo.predict_proba(x)
    return p


POSICIONES_TXT = {"casa": "casa", "ultimo_piso": "último piso", "sin_cubierta": "sin cubierta"}
EPOCAS_TXT = ["antes de 1990", "1990–2009", "2010 o después"]


def reglas_legibles(arbol, nombres):
    """Una regla por hoja: las condiciones de cada variable se juntan en un intervalo o un conjunto de valores,
    con el área en m² y los pisos en unidades (no en logaritmos)."""
    t = arbol.tree_
    posiciones = [n[4:] for n in nombres if n.startswith("pos_")]
    bloques = [n[7:] for n in nombres if n.startswith("bloque_")]
    salida = []

    def texto(c):
        partes = []
        for n, (lo, hi) in c["num"].items():
            inv = np.expm1 if n in ("log_habitaciones", "log_banios", "log_terreno") else np.exp  # log(1 + x) o log
            if n in ("log_area", "log_terreno"):
                lo_t, hi_t = (None if b is None else f"{inv(b):.1f}".replace(".", ",") for b in (lo, hi))
                rango = (f"entre {lo_t} y {hi_t} m²" if lo_t and hi_t else f"> {lo_t} m²" if lo_t else f"≤ {hi_t} m²")
            else:  # pisos, habitaciones y baños: números enteros
                a = None if lo is None else int(np.floor(inv(lo))) + 1
                b = None if hi is None else int(np.floor(inv(hi)))
                rango = (f"de {a} a {b}" if a is not None and b is not None and a < b else
                         f"= {a}" if a is not None and b is not None else f"≥ {a}" if a is not None else f"≤ {b}")
            partes.append(f"{LEGIBLE[n]} {rango}")
        for nombre, valores, todos, txt in [("posición", c["pos"], posiciones, POSICIONES_TXT),
                                            ("bloque de estratos", c["bloque"], bloques, {}),
                                            ("época", c["epoca"], list(range(3)), dict(enumerate(EPOCAS_TXT)))]:
            if len(valores) < len(todos):
                partes.append(f"{nombre}: " + " o ".join(txt.get(x, x) for x in todos if x in valores))
        for n, si, no in [("tipo_bin", "multifamiliar", "baja altura"), ("ph", "en propiedad horizontal", "sin PH"),
                          ("vis_vip", "VIS o VIP", "no VIS ni VIP")]:
            if c["bin"].get(n) is not None:
                partes.append(si if c["bin"][n] else no)
        return " · ".join(partes) or "todas"

    def recorrer(nodo, c):
        if t.children_left[nodo] == -1:
            valores = t.value[nodo][0]
            k = int(np.argmax(valores))
            salida.append((texto(c), arbol.classes_[k], int(t.n_node_samples[nodo]), float(valores[k] / valores.sum())))
            return
        n, thr = nombres[t.feature[nodo]], t.threshold[nodo]
        for izq, hijo in [(True, t.children_left[nodo]), (False, t.children_right[nodo])]:
            d = {"num": dict(c["num"]), "pos": set(c["pos"]), "bloque": set(c["bloque"]), "epoca": set(c["epoca"]),
                 "bin": dict(c["bin"])}
            if n in LEGIBLE:
                lo, hi = d["num"].get(n, (None, None))
                d["num"][n] = (lo, thr) if izq else (thr, hi)
            elif n == "epoca_ord":
                d["epoca"] = {e for e in d["epoca"] if (e <= thr) == izq}
            elif n.startswith("pos_"):
                d["pos"] = d["pos"] - {n[4:]} if izq else {n[4:]}
            elif n.startswith("bloque_"):
                d["bloque"] = d["bloque"] - {n[7:]} if izq else {n[7:]}
            else:
                d["bin"][n] = not izq
            recorrer(hijo, d)

    recorrer(0, {"num": {}, "pos": set(posiciones), "bloque": set(bloques), "epoca": {0, 1, 2}, "bin": {}})
    return salida


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prueba", action="store_true")
    prueba_codigo = ap.parse_args().prueba
    suf = "_prueba" if prueba_codigo else ""
    t0 = time.time()

    v = cargar_viviendas()
    asignar_epoca_faltante(v)
    etiquetas = pd.read_parquet(INTERNOS / "arquetipos_final.parquet")
    final = json.loads((TABLAS / "agr_resultado_final.json").read_text(encoding="utf-8"))
    part = v["particion"].astype(str).to_numpy()
    n_con = int((part != "sin coordenadas").sum())
    entrenamiento, prueba, sin = part == "train", part == "test", part == "sin coordenadas"
    folds = pliegues(v, n_con, entrenamiento, prueba)
    i_tr = np.flatnonzero(entrenamiento)
    print(f"pliegues kNNDM: {[len(b) for _, b in folds]} viviendas de validación ({time.time() - t0:.0f} s)", flush=True)
    if prueba_codigo:
        rng = np.random.default_rng(SEMILLA)
        guardar = np.sort(rng.choice(len(i_tr), len(i_tr) // 10, replace=False))
        nuevo = -np.ones(len(i_tr), int)
        nuevo[guardar] = np.arange(len(guardar))
        folds = [(nuevo[a][nuevo[a] >= 0], nuevo[b][nuevo[b] >= 0]) for a, b in folds]
        i_tr = i_tr[guardar]
    bloques = pd.read_parquet(ML / "e1_git" / "datos" / "procesados" / "dataset_modelado.parquet", columns=["bloque"])["bloque"]
    bloque_prueba = bloques.to_numpy()[prueba[:n_con]]

    for sol in P["soluciones"]:
        x = matriz(v, final[sol].get("variables", "base"))  # Nota 8: las variables del agrupamiento ganador
        y = etiquetas[sol].to_numpy().astype(str)
        clases = np.unique(y)
        xtr, ytr = x.iloc[i_tr], y[i_tr]
        filas = []

        def cv(modelo, nombre, guardar_oof=False):
            oof = np.zeros((len(i_tr), len(clases))) if guardar_oof else None
            f1s = []
            for a, b in folds:
                m = modelo.fit(xtr.iloc[a], ytr[a])
                p = proba_completa(m, xtr.iloc[b], clases)
                f1s.append(f1_score(ytr[b], clases[p.argmax(1)], average="macro"))
                if guardar_oof:
                    oof[b] = p
            filas.append({"modelo": nombre, "f1_macro_cv": float(np.mean(f1s)), "f1_macro_cv_de": float(np.std(f1s))})
            print(f"  {sol} · {nombre}: F1 macro CV {np.mean(f1s):.4f} ({time.time() - t0:.0f} s)", flush=True)
            return float(np.mean(f1s)), oof

        prof = {}
        for d in range(P["arbol"]["max_depth"][0], P["arbol"]["max_depth"][1] + 1):
            prof[d], _ = cv(DecisionTreeClassifier(max_depth=d, min_samples_leaf=P["arbol"]["min_samples_leaf"],
                                                   random_state=SEMILLA), f"arbol_profundidad_{d}")
        mejor = max(prof.values())
        d_sel = min(d for d, f in prof.items() if f >= mejor - 0.01)

        bosques, oofs = {}, {}
        for mf in P["bosque"]["max_features"]:
            for hoja in P["bosque"]["min_samples_leaf"]:
                nombre = f"bosque_mf{mf}_hoja{hoja}"
                bosques[nombre], oofs[nombre] = cv(RandomForestClassifier(
                    n_estimators=P["bosque"]["n_estimators"], max_features=mf, min_samples_leaf=hoja, n_jobs=-1,
                    random_state=SEMILLA), nombre, guardar_oof=True)
        b_sel = max(bosques, key=bosques.get)
        cvt = pd.DataFrame(filas)
        cvt["elegido"] = cvt["modelo"].isin([f"arbol_profundidad_{d_sel}", b_sel])
        cvt.to_csv(TABLAS / f"clf_cv_{sol}{suf}.csv", index=False, encoding="utf-8-sig")

        _, mf, hoja = b_sel.split("_")
        mf = "sqrt" if mf == "mfsqrt" else float(mf[2:])
        arbol = DecisionTreeClassifier(max_depth=d_sel, min_samples_leaf=P["arbol"]["min_samples_leaf"],
                                       random_state=SEMILLA).fit(xtr, ytr)
        bosque = RandomForestClassifier(n_estimators=P["bosque"]["n_estimators"], max_features=mf,
                                        min_samples_leaf=int(hoja[4:]), n_jobs=-1, random_state=SEMILLA).fit(xtr, ytr)

        met, recall = {"arbol": {"profundidad": d_sel, "hojas": int(arbol.get_n_leaves())}, "bosque": {"config": b_sel}}, {}
        yte = y[prueba]
        for nombre, mod in [("arbol", arbol), ("bosque", bosque)]:
            p = proba_completa(mod, x[prueba], clases)
            pred = clases[p.argmax(1)]
            por_bloque = [f1_score(yte[bloque_prueba == b], pred[bloque_prueba == b], average="macro")
                          for b in np.unique(bloque_prueba)]
            met[nombre].update({"f1_macro": f1_score(yte, pred, average="macro"), "exactitud": accuracy_score(yte, pred),
                                "log_loss": log_loss(yte, np.clip(p, 1e-15, 1), labels=clases),
                                "brier": brier(yte, p, clases),
                                "f1_macro_bloques_min": float(min(por_bloque)), "f1_macro_bloques_max": float(max(por_bloque)),
                                "concordancia_sin_coordenadas": float((mod.predict(x[sin]) == y[sin]).mean())})
            recall[nombre] = pd.Series(recall_score(yte, pred, labels=clases, average=None, zero_division=np.nan), index=clases)
        met["n"] = {"entrenamiento": int(len(i_tr)), "prueba": int(prueba.sum()), "sin_coordenadas": int(sin.sum())}
        met = json.loads(json.dumps(met, default=float))
        (TABLAS / f"clf_metricas_{sol}{suf}.json").write_text(json.dumps(met, ensure_ascii=False, indent=2), encoding="utf-8")
        pd.DataFrame(recall).assign(viviendas_prueba=pd.Series(yte).value_counts()).round(4).to_csv(
            TABLAS / f"clf_recall_{sol}{suf}.csv", encoding="utf-8-sig")

        # probabilidades de cada vivienda: fuera de muestra en entrenamiento; modelo completo en prueba y sin ubicar
        proba = np.full((len(v), len(clases)), np.nan, dtype=np.float32)
        proba[i_tr] = oofs[b_sel]
        proba[prueba] = proba_completa(bosque, x[prueba], clases)
        proba[sin] = proba_completa(bosque, x[sin], clases)
        pdf = pd.DataFrame(proba, columns=clases, index=v.index)
        pdf.to_parquet(INTERNOS / f"probabilidades_{sol}{suf}.parquet")
        validas = ~np.isnan(proba).any(1)
        propia = proba[np.flatnonzero(validas), np.searchsorted(clases, y[validas])]
        resumen = pd.DataFrame({"arquetipo": y[validas], "p": propia}).groupby("arquetipo")["p"].agg(
            probabilidad_media="mean", frac_menor_0_8=lambda s: (s < P["umbral_probabilidad_baja"]).mean(),
            viviendas="size")
        resumen.round(4).to_csv(TABLAS / f"clf_probabilidades_{sol}{suf}.csv", encoding="utf-8-sig")

        reglas = reglas_legibles(arbol, list(x.columns))
        texto = [f"Árbol de decisión, solución «{sol}»: profundidad {d_sel}, {len(reglas)} hojas. "
                 f"Entrenado con {len(i_tr):,} viviendas.", ""]
        for cond, clase, n, pureza in sorted(reglas, key=lambda r: (r[1], -r[2])):
            texto.append(f"{clase}  ({n:,} viviendas, {pureza:.0%} del arquetipo): {cond}")
        (TABLAS / f"clf_reglas_arbol_{sol}{suf}.txt").write_text("\n".join(texto), encoding="utf-8")

        # el árbol (hojas de 50 viviendas o más) se publica; el bosque puede memorizar registros y queda interno
        MODELOS.mkdir(parents=True, exist_ok=True)
        joblib.dump({"modelo": arbol, "variables": list(x.columns), "solucion": sol,
                     "preparacion": "src/agrupamiento.py:preparar y scripts/06_clasificador.py:matriz"},
                    MODELOS / f"arbol_{sol}{suf}.joblib", compress=3)
        joblib.dump({"modelo": bosque, "variables": list(x.columns), "solucion": sol},
                    INTERNOS / f"bosque_{sol}{suf}.joblib", compress=3)

        print(f"\n=== {sol}: árbol profundidad {d_sel} ({arbol.get_n_leaves()} hojas), bosque {b_sel}")
        print(json.dumps({k: met[k] for k in ["arbol", "bosque"]}, ensure_ascii=False, indent=1))
        print(resumen.round(3).to_string(), flush=True)
    print(f"\ntiempo total: {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
