"""Días representativos: tres días por mes de cada año con su peso, para simular cuando el cómputo lo exija.

La propuesta (sección 7.6) estima entre 4 y 6 horas por corrida con 36 días representativos (tres por mes) y prevé
usarlos en la calibración con emulador. La calibración usa el nivel anual de consumo y la validación la respuesta
mensual al calor (Ecuación 9), que sale de las anomalías interanuales de cada mes; por eso los días se eligen dentro de
cada mes de cada año, y no un año típico.

Método: en cada mes de 2015 a septiembre de 2026, k-medoides exacto con k = 3 (se prueban todas las ternas de días)
sobre cinco rasgos diarios estandarizados con toda la serie: temperatura media y máxima, índice de calor máximo,
irradiancia diaria y humedad específica media. Cada día representativo pesa el número de días de su grupo, así que los
pesos de un mes suman sus días. Como referencia se toman 200 sorteos de tres días al azar con pesos iguales.

Validación, por mes: temperatura e índice de calor medios, irradiancia, grados-hora (26,5 °C) y carga del Paso 3 de la
vivienda media (envolvente común, geometría de las tablas del script 11 de arquetipos), reconstruidos con los días
y sus pesos frente al mes completo; correlación de las anomalías mensuales del índice de calor y de la carga, que son
las que identifican la Ecuación 9.

Uso:  python scripts/07_dias_representativos.py
Salidas (salidas/):
  dias_representativos.csv          año, mes, fecha del día representativo, peso y rasgos
  dias_representativos_validacion.csv   errores por mes (k-medoides y mediana de los sorteos al azar)
  dias_representativos_resumen.json     errores medios, máximos y correlaciones de las anomalías
"""
import itertools
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
BASE = RAIZ.parents[1]
sys.path.insert(0, str(BASE / "arquetipos"))
from src import carga as cg  # noqa: E402

SALIDAS = RAIZ / "salidas"
TABLAS_ARQ = BASE / "arquetipos" / "salidas" / "tablas"
RASGOS = ["T_media", "T_max", "HI_max", "GHI_dia", "w_media"]
K, SORTEOS, SEMILLA = 3, 200, 42
COMPONENTES = {"cubierta": "c_t", "muros": "c_m", "ventanas": "c_v", "infiltracion_sensible": "c_V_sens",
               "latente": "c_V_lat"}


def geometria_media():
    q = pd.read_csv(TABLAS_ARQ / "clima_gdex_carga.csv", index_col="clima").loc["gdex"]
    c = pd.read_csv(TABLAS_ARQ / "clima_gdex_coeficientes.csv", index_col="coeficiente")["gdex"]
    return {k: q[k] / c[v] for k, v in COMPONENTES.items()}


def grados_hora(h):
    """Grados-hora de cada hora para la carga del Paso 3 (mismas fórmulas que src/carga.py)."""
    p = cg.DECISION["carga"]
    tc = p["consigna_C"]
    wc = cg._w(p["humedad_relativa_consigna"] * cg._pv(tc))
    sa_t = h["T"] + p["absortancia"] * h["GHI"] / p["h_o"] - p["dT_onda_larga_horizontal_K"]
    sa_m = h["T"] + p["absortancia"] * p["f_v_muros"] * h["GHI"] / p["h_o"]
    return pd.DataFrame({"t": (sa_t - tc).clip(lower=0), "m": (sa_m - tc).clip(lower=0),
                         "v": (h["T"] - tc).clip(lower=0), "w": (cg._w(cg._pv(h["Td"])) - wc).clip(lower=0),
                         "cdh": (h["HI"] - 26.5).clip(lower=0)}, index=h.index)


def carga_de(gh, geo):
    """Carga del Paso 3 (kWh) de la vivienda media a partir de las sumas de grados-hora."""
    p = cg.DECISION["carga"]
    m3 = cg.RHO * p["renovaciones_h"] / 3600
    return (p["U_cubierta"] * gh["t"] * geo["cubierta"] + p["U_muro"] * gh["m"] * geo["muros"]
            + p["U_vidrio"] * gh["v"] * geo["ventanas"] + m3 * cg.CP * gh["v"] * geo["infiltracion_sensible"]
            + m3 * cg.HFG * gh["w"] * geo["latente"]) / 1000


def kmedoides(x):
    """k-medoides exacto: la terna de días que minimiza la suma de distancias de cada día a su medoide."""
    d = np.sqrt(((x[:, None, :] - x[None, :, :]) ** 2).sum(-1))
    mejor, costo = None, np.inf
    for terna in itertools.combinations(range(len(x)), K):
        c = d[:, terna].min(axis=1).sum()
        if c < costo:
            mejor, costo = terna, c
    grupo = d[:, mejor].argmin(axis=1)
    return list(mejor), np.bincount(grupo, minlength=K)


def main():
    s = pd.read_parquet(SALIDAS / "clima_horario_barranquilla.parquet")
    s["fecha"] = (s.index - pd.Timedelta(seconds=1)).normalize()
    s = s[s["fecha"] >= "2015-01-01"]
    completos = s.groupby("fecha").size()
    s = s[s["fecha"].isin(completos[completos == 24].index)]
    g = s.groupby("fecha")
    dia = pd.DataFrame({"T_media": g["T"].mean(), "T_max": g["T"].max(), "HI_max": g["HI"].max(),
                        "GHI_dia": g["GHI"].sum() / 1000, "w_media": g["w_kgkg"].mean() * 1000})
    z = (dia[RASGOS] - dia[RASGOS].mean()) / dia[RASGOS].std()
    gh = grados_hora(s)
    gh["fecha"] = s["fecha"]
    gh_dia = gh.groupby("fecha").sum()
    clima_dia = pd.DataFrame({"T": g["T"].mean(), "HI": g["HI"].mean(), "GHI": g["GHI"].mean()})
    geo = geometria_media()

    rng = np.random.default_rng(SEMILLA)
    elegidos, valid = [], []
    for mes, idx in dia.groupby(dia.index.to_period("M")).groups.items():
        if len(idx) < 28:
            continue
        idx = pd.DatetimeIndex(idx)
        meds, pesos = kmedoides(z.loc[idx].to_numpy())
        for i, w in zip(meds, pesos):
            elegidos.append({"anio": mes.year, "mes": mes.month, "fecha": idx[i].date(), "peso": int(w),
                             **dia.loc[idx[i]].round(3).to_dict()})
        completo = {"T": clima_dia.loc[idx, "T"].mean(), "HI": clima_dia.loc[idx, "HI"].mean(),
                    "GHI": clima_dia.loc[idx, "GHI"].mean(), "CDH": gh_dia.loc[idx, "cdh"].sum(),
                    "carga": carga_de(gh_dia.loc[idx].sum(), geo)}

        def reconstruir(dias, w):
            w = np.asarray(w, float)
            return {"T": np.average(clima_dia.loc[dias, "T"], weights=w),
                    "HI": np.average(clima_dia.loc[dias, "HI"], weights=w),
                    "GHI": np.average(clima_dia.loc[dias, "GHI"], weights=w),
                    "CDH": float((gh_dia.loc[dias, "cdh"] * w).sum()),
                    "carga": carga_de((gh_dia.loc[dias] * w[:, None]).sum(), geo)}

        rep = reconstruir(idx[meds], pesos)
        azar = [reconstruir(idx[rng.choice(len(idx), K, replace=False)], [len(idx) / K] * K)
                for _ in range(SORTEOS)]
        fila = {"mes": str(mes), "dias": len(idx)}
        for v in completo:
            fila[f"{v}_completo"] = completo[v]
            fila[f"{v}_kmedoides"] = rep[v]
            if v in ("CDH", "carga"):
                fila[f"err_%_{v}_kmedoides"] = 100 * (rep[v] / completo[v] - 1)
                fila[f"err_abs_%_{v}_azar_mediana"] = float(np.median([abs(100 * (a[v] / completo[v] - 1))
                                                                       for a in azar]))
            else:
                fila[f"err_{v}_kmedoides"] = rep[v] - completo[v]
                fila[f"err_abs_{v}_azar_mediana"] = float(np.median([abs(a[v] - completo[v]) for a in azar]))
        valid.append(fila)

    sel = pd.DataFrame(elegidos)
    va = pd.DataFrame(valid).set_index("mes")
    SALIDAS.mkdir(parents=True, exist_ok=True)
    sel.to_csv(SALIDAS / "dias_representativos.csv", index=False)
    va.round(4).to_csv(SALIDAS / "dias_representativos_validacion.csv")

    meses = pd.PeriodIndex(va.index, freq="M").month
    resumen = {"meses": len(va), "dias_representativos": len(sel)}
    for v in ["T", "HI", "GHI"]:
        resumen[v] = {"err_abs_medio_kmedoides": float(va[f"err_{v}_kmedoides"].abs().mean()),
                      "err_abs_max_kmedoides": float(va[f"err_{v}_kmedoides"].abs().max()),
                      "err_abs_mediano_azar": float(va[f"err_abs_{v}_azar_mediana"].mean())}
    for v in ["CDH", "carga"]:
        resumen[v] = {"err_abs_medio_%_kmedoides": float(va[f"err_%_{v}_kmedoides"].abs().mean()),
                      "err_abs_max_%_kmedoides": float(va[f"err_%_{v}_kmedoides"].abs().max()),
                      "sesgo_%_kmedoides": float(va[f"err_%_{v}_kmedoides"].mean()),
                      "err_abs_mediano_%_azar": float(va[f"err_abs_%_{v}_azar_mediana"].mean())}
        anual = va[f"{v}_kmedoides"].groupby(pd.PeriodIndex(va.index, freq="M").year).sum() / \
            va[f"{v}_completo"].groupby(pd.PeriodIndex(va.index, freq="M").year).sum()
        resumen[v]["err_anual_%_rango"] = [float(100 * (anual.min() - 1)), float(100 * (anual.max() - 1))]
    for v in ["HI", "carga"]:
        a_c = va[f"{v}_completo"] - va[f"{v}_completo"].groupby(meses).transform("mean")
        a_r = va[f"{v}_kmedoides"] - va[f"{v}_kmedoides"].groupby(meses).transform("mean")
        resumen[f"correlacion_anomalias_{v}"] = float(np.corrcoef(a_c, a_r)[0, 1])
    (SALIDAS / "dias_representativos_resumen.json").write_text(json.dumps(resumen, indent=2, ensure_ascii=False),
                                                              encoding="utf-8")
    print(json.dumps(resumen, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
