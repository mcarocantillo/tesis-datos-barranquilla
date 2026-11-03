"""Paso 3: carga anual de enfriamiento simplificada y R² de las tipologías por reglas.

Evalúa la tipología base y su variante con clases de tamaño (Nota 2 del preregistro; sensibilidad).
Salidas:
  datos_internos/carga_viviendas.parquet  carga por vivienda y componente (microdato, no se publica)
  salidas/tablas/carga_coeficientes.csv   coeficientes climáticos de la envolvente común
  salidas/tablas/carga_por_arquetipo.csv  carga mediana y reparto por componente (y _tamano para la variante)
  salidas/tablas/carga_r2_reglas.csv      R², η² del estrato y análisis A3 y A4 de ambas tipologías
  salidas/tablas/carga_arbol_cota.csv     A2: R² de un árbol de regresión con k hojas (cota de referencia)
  salidas/figuras/carga_r2_k.png          curva de R² frente a k
"""
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter
from sklearn.tree import DecisionTreeRegressor

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.carga import carga, coeficientes, eta2_estrato, geometria, r2
from src.comun import DECISION, FIGURAS, INTERNOS, SEMILLA, TABLAS, cargar_viviendas
from src.estilo import GREY, OCH, PET, guardar, lienzo

K_MAX = 30
TIPOLOGIAS = {"base": "tipologia_reglas", "tamano": "tipologia_reglas_tamano"}


def variables_fisicas(v):
    """Variables de agrupamiento del Paso 2 (sin estrato), codificadas para el árbol."""
    x = pd.DataFrame({"area": v["area_construida"], "pisos_unidad": v["total_plantas"].fillna(1),
                      "piso": v["planta_ubicacion"].fillna(1), "ph": v["condicion_predio"].astype(str).str.startswith("PH"),
                      "multifamiliar": v["tipo"] == "multifamiliar"}, index=v.index).astype(float)
    x = x.join(pd.get_dummies(v["posicion"], prefix="pos").astype(float))
    return x.join(pd.get_dummies(v["epoca"].fillna("sin"), prefix="ep").astype(float))


def curva_arbol(x, y, ks):
    out = []
    for k in ks:
        t = DecisionTreeRegressor(max_leaf_nodes=k, random_state=SEMILLA).fit(x, y)
        out.append(r2(y, t.apply(x)))
    return np.array(out)


def indicadores(q, q_m2, g, grupos, estrato):
    filas = {"k": grupos.nunique(), "R2 carga por vivienda": r2(q, grupos),
             "eta2 estrato dentro de los arquetipos": eta2_estrato(q, grupos, estrato),
             "A3: R2 carga por m2": r2(q_m2, grupos)}
    for nombre, kw in [("f_v=0,3", {"f_v": 0.3}), ("f_v=0,7", {"f_v": 0.7}), ("n=0,5", {"n": 0.5}), ("n=2,0", {"n": 2.0})]:
        filas[f"A4: R2 con {nombre}"] = r2(carga(g, coeficientes(**kw)).sum(axis=1), grupos)
    return pd.Series(filas)


def main():
    t0 = time.time()
    v = cargar_viviendas()
    c = coeficientes()
    pd.Series(c).round(4).to_csv(TABLAS / "carga_coeficientes.csv", header=["valor"], encoding="utf-8-sig")
    g = geometria(v)
    comp = carga(g, c)
    q = comp.sum(axis=1)
    q_m2 = q / v["area_construida"]
    print("coeficientes (kWh/año por m² o m³):", {k: round(val, 2) for k, val in c.items() if k.startswith("c_")})
    print(f"carga por vivienda: mediana {q.median():,.0f} kWh/año (P10 {q.quantile(.1):,.0f}, P90 {q.quantile(.9):,.0f})")
    print("reparto en la ciudad:", (comp.sum() / q.sum() * 100).round(1).to_dict())

    INTERNOS.mkdir(exist_ok=True)
    comp.assign(total=q, por_m2=q_m2).astype("float32").to_parquet(INTERNOS / "carga_viviendas.parquet")

    res = {}
    for nombre, archivo in TIPOLOGIAS.items():
        arq = pd.Series(pd.read_parquet(INTERNOS / f"{archivo}.parquet")["arquetipo"].to_numpy(), index=v.index)
        t = comp.groupby(arq).sum()
        pa = (t.div(t.sum(axis=1), axis=0) * 100).round(1).add_prefix("pct_")
        pa.insert(0, "carga_mediana_kWh", q.groupby(arq).median().round(0))
        pa.insert(1, "carga_m2_mediana_kWh", q_m2.groupby(arq).median().round(1))
        pa.to_csv(TABLAS / f"carga_por_arquetipo{'' if nombre == 'base' else '_tamano'}.csv", encoding="utf-8-sig")
        res[nombre] = indicadores(q, q_m2, g, arq, v["estrato_num"])

    # A2: cota de referencia con un árbol de regresión sobre las variables físicas
    x = variables_fisicas(v)
    ks = np.arange(2, K_MAX + 1)
    cota = curva_arbol(x, q, ks)
    cota_m2 = curva_arbol(x, q_m2, ks)
    d = DECISION["carga"]["criterio"]["delta_R2_min"]
    tab = pd.DataFrame({"k": ks, "R2_arbol": cota.round(4), "delta": np.r_[np.nan, np.diff(cota)].round(4),
                        "R2_arbol_por_m2": cota_m2.round(4)})
    tab.to_csv(TABLAS / "carga_arbol_cota.csv", index=False, encoding="utf-8-sig")

    res = pd.DataFrame(res)
    res.loc["A2: R2 del árbol con el mismo k"] = [cota[int(k) - 2] for k in res.loc["k"]]
    res.round(4).to_csv(TABLAS / "carga_r2_reglas.csv", encoding="utf-8-sig")
    print(f"\n{res.round(3).to_string()}")
    print(f"\nA2: primer k del árbol cuyo siguiente grupo suma < {d}: {ks[np.argmax(np.diff(cota) < d)]}")

    coma = FuncFormatter(lambda y, _: f"{y:.1f}".replace(".", ","))
    fig, ax = lienzo(14, 9.5)
    ax.plot(ks, cota, color=GREY, lw=1.2, label="Árbol de regresión, carga por vivienda (cota)")
    ax.plot(ks, cota_m2, color=GREY, lw=1.2, ls="--", label="Árbol de regresión, carga por m² (cota)")
    for nombre, color, etiqueta in [("base", OCH, "Reglas"), ("tamano", PET, "Reglas con tamaño")]:
        k = res.loc["k", nombre]
        ax.scatter([k], [res.loc["R2 carga por vivienda", nombre]], color=color, zorder=3,
                   label=f"{etiqueta} (k = {k:.0f}), carga por vivienda")
        ax.scatter([k], [res.loc["A3: R2 carga por m2", nombre]], color=color, marker="s", facecolor="white",
                   zorder=3, label=f"{etiqueta}, carga por m²")
    ax.set_xlabel("Número de grupos, k")
    ax.set_ylabel("Fracción de la varianza de la carga explicada (R²)")
    ax.set_ylim(0, 1.02)
    ax.yaxis.set_major_formatter(coma)
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2, fontsize=7)
    guardar(fig, FIGURAS / "carga_r2_k.png")
    print(f"\ntiempo total: {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
