"""¿Ganaría peso el agrupamiento si la carga del Paso 3 usara el techo de cada vivienda?

El Paso 3 usa una envolvente común (U de cubierta 4,0 y absortancia 0,7), así que la carga solo ve la geometría y la
posición. Esta prueba asigna a cada vivienda con cubierta un techo sorteado con las proporciones de su arquetipo en
los priors del Paso 6 (ECV), le pone el U y la absortancia de ese material (moda de env_propiedades_materiales.csv) y
recalcula la carga. Si los materiales llegan del catastro, el techo dejaría de sortearse; el orden de magnitud es el
mismo mientras las proporciones se parezcan a las de la ECV.

Escenarios del techo:
  moda        U y absortancia moda de cada material (los techos livianos sin cielo raso)
  cielo_raso  igual, pero asbesto-cemento, zinc y otro con cielo raso (su U mínima)

Para cada solución (por vivienda y por m², cada una con su medida de carga) se compara la fracción de la varianza
explicada (R²) por los arquetipos actuales con y sin el techo como variable adicional. Si agregar el techo sube el R²
en 0,02 o más (el umbral de la Nota 3), el criterio del Paso 3 lo habría tomado: el agrupamiento separaría por techo.

Uso: python scripts/13_sensibilidad_techo.py
Salidas:
  salidas/tablas/techo_coeficientes.csv   coeficiente de cubierta (kWh/año por m² de techo) por material y escenario
  salidas/tablas/techo_r2.csv             R² de posición × bloque y de los arquetipos, sin y con el techo
  salidas/tablas/techo_carga.csv          carga mediana por m² de cada arquetipo según el techo (celdas de 30 o más)
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src import carga as cg  # noqa: E402
from src.comun import DECISION, INTERNOS, SEMILLA, TABLAS, cargar_viviendas  # noqa: E402

MEDIDA = {"por_vivienda": "total", "por_m2": "por_m2"}
N_MIN = 30
UMBRAL = DECISION["carga"]["criterio"]["delta_R2_min"]


def propiedades():
    t = pd.read_csv(TABLAS / "env_propiedades_materiales.csv")
    t = t[t["elemento"] == "techo"].set_index(["material", "parametro"])
    u = t.xs("U (W/m²K)", level="parametro")
    a = t.xs("absortancia solar", level="parametro")["moda"]
    livianos = u.index != "concreto"
    return {"moda": pd.DataFrame({"U": u["moda"], "alfa": a}),
            "cielo_raso": pd.DataFrame({"U": np.where(livianos, u["minimo"], u["moda"]), "alfa": a}, index=u.index)}


def coef_cubierta(clima, u, alfa):
    """U × grados-hora sol-aire de la cubierta con esa absortancia (kWh/año por m² de techo), como en el Paso 3."""
    p = DECISION["carga"]
    sa = clima["T"] + alfa * clima["I"] / p["h_o"] - p["dT_onda_larga_horizontal_K"]
    gh = (sa - p["consigna_C"]).clip(lower=0).groupby(clima["anio"]).sum().mean()
    return u * gh / 1000


def sortear_techo(arq, sol, rng):
    """Techo de cada vivienda según las proporciones medias de su arquetipo en los priors (vacío si no tiene)."""
    pr = pd.read_csv(TABLAS / f"env_priors_{sol}.csv")
    pr = pr[pr["parametro"].str.startswith("techo: ")].drop_duplicates(["arquetipo", "parametro"])
    pr = pr.assign(material=pr["parametro"].str.removeprefix("techo: "))
    probs = pr.pivot(index="arquetipo", columns="material", values="media").fillna(0)
    techo = pd.Series(pd.NA, index=arq.index, dtype=object)
    for a, p in probs.iterrows():
        filas = arq.index[arq == a]
        techo[filas] = rng.choice(p.index.to_numpy(), size=len(filas), p=(p / p.sum()).to_numpy())
    return techo


def main():
    v = cargar_viviendas()
    q = pd.read_parquet(INTERNOS / "carga_viviendas.parquet")
    arq = pd.read_parquet(INTERNOS / "arquetipos_final.parquet")
    c0 = cg.coeficientes()
    a_t = q["cubierta"] / c0["c_t"]  # m² de cubierta de cada vivienda
    clima = cg.clima()
    props = propiedades()
    coefs = pd.concat({e: p.assign(c_t=[coef_cubierta(clima, r.U, r.alfa) for r in p.itertuples()])
                       for e, p in props.items()}, names=["escenario", "material"])
    coefs.loc[("comun", "todos"), :] = [DECISION["carga"]["U_cubierta"], DECISION["carga"]["absortancia"], c0["c_t"]]
    coefs.round(3).to_csv(TABLAS / "techo_coeficientes.csv", encoding="utf-8-sig")
    print("Coeficiente de cubierta (kWh/año por m² de techo):\n" + coefs.round(2).to_string())

    pos_bloque = v["posicion"].astype(str) + "|" + v["bloque"].astype(str)
    filas_r2, filas_carga = [], []
    for sol, medida in MEDIDA.items():
        techo = sortear_techo(arq[sol], sol, np.random.default_rng(SEMILLA))
        con_techo = (a_t > 0).to_numpy()
        sin_dato = con_techo & techo.isna().to_numpy()
        print(f"\n{sol}: {con_techo.sum():,} viviendas con cubierta; {sin_dato.sum():,} sin proporciones de techo")
        techo_txt = techo.fillna("sin_cubierta").astype(str)
        for esc in ["comun", "moda", "cielo_raso"]:
            if esc == "comun":
                total = q["total"]
            else:
                c_t = techo.map(coefs.loc[esc, "c_t"]).astype(float).fillna(c0["c_t"])
                total = q["total"] - q["cubierta"] + a_t * c_t
            y = total if medida == "total" else total / v["area_construida"]
            r = {"solucion": sol, "medida": medida, "escenario": esc,
                 "R2_posicion_bloque": cg.r2(y, pos_bloque),
                 "R2_posicion_bloque_techo": cg.r2(y, pos_bloque + "|" + techo_txt),
                 "R2_arquetipos": cg.r2(y, arq[sol]),
                 "R2_arquetipos_techo": cg.r2(y, arq[sol] + "|" + techo_txt)}
            r["ganancia_techo"] = r["R2_arquetipos_techo"] - r["R2_arquetipos"]
            r["techo_entraria"] = r["ganancia_techo"] >= UMBRAL
            filas_r2.append(r)
            if esc != "comun" and medida == "por_m2":
                g = pd.DataFrame({"arquetipo": arq[sol], "techo": techo_txt, "y": y})[con_techo]
                t = g.groupby(["arquetipo", "techo"])["y"].agg(["median", "size"]).reset_index()
                t = t[t["size"] >= N_MIN].rename(columns={"median": "carga_m2_mediana_kWh", "size": "viviendas"})
                filas_carga.append(t.assign(solucion=sol, escenario=esc))
    r2 = pd.DataFrame(filas_r2)
    r2.round(4).to_csv(TABLAS / "techo_r2.csv", index=False, encoding="utf-8-sig")
    print("\nR² sin y con el techo como variable:\n" + r2.round(3).to_string(index=False))
    carga = pd.concat(filas_carga, ignore_index=True)
    carga["carga_m2_mediana_kWh"] = carga["carga_m2_mediana_kWh"].round(1)
    carga.to_csv(TABLAS / "techo_carga.csv", index=False, encoding="utf-8-sig")
    tabla = carga[carga["solucion"] == "por_m2"].pivot_table(
        index="arquetipo", columns=["escenario", "techo"], values="carga_m2_mediana_kWh")
    print("\nCarga mediana por m² de cada arquetipo según el techo (solución por m²):\n" + tabla.to_string())


if __name__ == "__main__":
    main()
