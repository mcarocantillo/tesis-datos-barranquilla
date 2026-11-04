"""Corrección de onda larga del sol-aire de la cubierta con la radiación de ERA5-Land, y su efecto en la carga del Paso 3.

El Paso 3 de la Fase 1 usa T_sa = T + α·I/h_o − 3,9 K en la cubierta. Los 3,9 K son la corrección de ASHRAE para
superficies horizontales, ε·ΔR/h_o, con ΔR ≈ 63–66 W/m² (la diferencia entre la radiación de cuerpo negro a la
temperatura del aire y la de onda larga que llega del cielo) en un cielo templado. Con la onda larga descendente
horaria de ERA5-Land (L) se puede calcular para Barranquilla:

    ΔR_t = σ·(T_t + 273,15)⁴ − L_t,     corrección_t = ε·ΔR_t / h_o

Esta magnitud no es la diferencia entre la temperatura del aire y la del cielo (7,3 K en promedio, columna dT_cielo de
la serie), que es la que usa el 5R1C de la ISO 13790 (Δθ_er, 11 K por defecto); las dos describen el mismo
intercambio con fórmulas distintas.

Se recalcula la carga de la vivienda media y el R² de los arquetipos finales con la corrección horaria (ε = 0,9, y 0,8
y 0,95 como rango), con el clima de GDEX de 2015–2025 por año local. Los demás coeficientes no cambian. Es una prueba de
robustez: no cambia la solución de la Fase 1.

Uso:  python scripts/06_onda_larga_paso3.py   (necesita el catastro y la asignación de arquetipos, que no se publican)
Salida: salidas/onda_larga_paso3.csv   corrección media, coeficiente de la cubierta, carga media y R² por variante
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
BASE = RAIZ.parents[1]
sys.path.insert(0, str(BASE / "arquetipos"))
from src import carga as cg  # noqa: E402
from src.comun import INTERNOS, cargar_viviendas  # noqa: E402

SALIDAS = RAIZ / "salidas"
SIGMA = 5.670374419e-8
EMISIVIDADES = [0.8, 0.9, 0.95]


def coef_cubierta(c, correccion, p):
    sa = c["T"] + p["absortancia"] * c["I"] / p["h_o"] - correccion
    gh = (sa - p["consigna_C"]).clip(lower=0).groupby(c["anio"]).sum().mean()
    return p["U_cubierta"] * gh / 1000, gh


def main():
    p = cg.DECISION["carga"]
    s = pd.read_parquet(SALIDAS / "clima_horario_barranquilla.parquet")
    anio = (s.index - pd.Timedelta(seconds=1)).year
    s = s[(anio >= 2015) & (anio <= 2025)]
    c = pd.DataFrame({"anio": (s.index - pd.Timedelta(seconds=1)).year, "T": s["T"].to_numpy(),
                      "Td": s["Td"].to_numpy(), "I": s["GHI"].to_numpy()})
    dR = SIGMA * (s["T"].to_numpy() + 273.15) ** 4 - s["L_onda_larga"].to_numpy()
    base = cg.coeficientes(c=c)

    v = cargar_viviendas()
    geo = cg.geometria(v)
    arq = pd.read_parquet(INTERNOS / "arquetipos_final.parquet").reindex(v.index)

    variantes = [("constante_3.9K", np.full(len(c), p["dT_onda_larga_horizontal_K"]))]
    variantes += [(f"horaria_eps_{e:g}", e * dR / p["h_o"]) for e in EMISIVIDADES]
    filas = []
    for nombre, corr in variantes:
        coefs = dict(base)
        coefs["c_t"], gh = coef_cubierta(c, corr, p)
        q = cg.carga(geo, coefs)
        tot = q.sum(axis=1)
        dia = s["cenit_sol"].to_numpy() < 85
        filas.append({"variante": nombre, "correccion_media_K": float(np.mean(corr)),
                      "correccion_dia_K": float(np.mean(corr[dia])), "correccion_noche_K": float(np.mean(corr[~dia])),
                      "gh_cubierta": gh, "c_t": coefs["c_t"], "carga_cubierta": q["cubierta"].mean(),
                      "carga_total": tot.mean(), "frac_cubierta": q["cubierta"].mean() / tot.mean(),
                      "R2_por_vivienda": cg.r2(tot, arq["por_vivienda"]),
                      "R2_por_m2": cg.r2(tot / v["area_construida"], arq["por_m2"])})
    t = pd.DataFrame(filas).set_index("variante")
    t["dif_%_carga_total"] = 100 * (t["carga_total"] / t.loc["constante_3.9K", "carga_total"] - 1)
    t["dif_%_carga_cubierta"] = 100 * (t["carga_cubierta"] / t.loc["constante_3.9K", "carga_cubierta"] - 1)
    t.round(4).to_csv(SALIDAS / "onda_larga_paso3.csv")
    print(f"ΔR medio {dR.mean():.1f} W/m² (día {dR[s['cenit_sol'] < 85].mean():.1f}, noche "
          f"{dR[s['cenit_sol'] >= 85].mean():.1f})")
    print(t.round(3).to_string())


if __name__ == "__main__":
    main()
