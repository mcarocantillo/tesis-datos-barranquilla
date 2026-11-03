"""Carga anual de enfriamiento simplificada (Paso 3) con envolvente común.

Como la envolvente es igual para todas las viviendas, la carga es lineal en cuatro magnitudes geométricas:
    Q = c_t·A_t + c_m·A_m + c_v·A_v + c_V·V
El clima fija los coeficientes c (Wh/año por m² o por m³); la geometría sale del catastro.
"""
import json

import numpy as np
import pandas as pd

from .comun import CLIMA, DECISION

RHO, CP, HFG, P_ATM = 1.2, 1006.0, 2.45e6, 101.325  # kg/m³, J/kg·K, J/kg, kPa
ANIOS = range(2015, 2026)


def _pv(t_c):
    """Presión de vapor de saturación (kPa), Magnus."""
    return 0.6112 * np.exp(17.67 * t_c / (t_c + 243.5))


def _w(pv):
    return 0.622 * pv / (P_ATM - pv)


def clima():
    filas = []
    for a in ANIOS:
        h = json.loads((CLIMA / f"om_{a}.json").read_text(encoding="utf-8"))["hourly"]
        filas.append(pd.DataFrame({"anio": a, "T": h["temperature_2m_era5_land"],
                                   "Td": h["dew_point_2m_era5_land"], "I": h["shortwave_radiation_era5"]}))
    return pd.concat(filas, ignore_index=True)


def coeficientes(f_v=None, n=None, par=None):
    """Coeficientes anuales medios (kWh/año por m² de cubierta, muro y ventana, y por m³ de volumen)."""
    p = dict(DECISION["carga"] if par is None else par)
    f_v = p["f_v_muros"] if f_v is None else f_v
    n = p["renovaciones_h"] if n is None else n
    c = clima()
    tc = p["consigna_C"]
    wc = _w(p["humedad_relativa_consigna"] * _pv(tc))
    sa_t = c["T"] + p["absortancia"] * c["I"] / p["h_o"] - p["dT_onda_larga_horizontal_K"]
    sa_m = c["T"] + p["absortancia"] * f_v * c["I"] / p["h_o"]
    gh = pd.DataFrame({"anio": c["anio"],
                       "t": (sa_t - tc).clip(lower=0), "m": (sa_m - tc).clip(lower=0),
                       "v": (c["T"] - tc).clip(lower=0), "w": (_w(_pv(c["Td"])) - wc).clip(lower=0)})
    s = gh.groupby("anio").sum().mean()  # grados-hora (K·h) y kg/kg·h por año, promedio 2015–2025
    m_por_m3 = RHO * n / 3600  # kg/s por m³ de volumen
    return {"c_t": p["U_cubierta"] * s["t"] / 1000, "c_m": p["U_muro"] * s["m"] / 1000,
            "c_v": p["U_vidrio"] * s["v"] / 1000,
            "c_V_sens": m_por_m3 * CP * s["v"] / 1000, "c_V_lat": m_por_m3 * HFG * s["w"] / 1000,
            "gh_cubierta": s["t"], "gh_muro": s["m"], "gh_aire": s["v"], "w_h": s["w"]}


def geometria(v, par=None):
    """Áreas expuestas y volumen de cada vivienda según las reglas del preregistro."""
    p = DECISION["carga"] if par is None else par
    n_pl = v["total_plantas"].fillna(1).clip(lower=1)
    h = v["altura"].fillna(3.0).clip(*p["altura_piso_limites_m"])
    planta = v["area_construida"] / n_pl
    a_t = np.where(v["posicion"].astype(str).isin(["casa", "ultimo_piso"]), planta, 0.0)
    bruto = 4 * np.sqrt(planta) * p["frac_perimetro_expuesto"] * h * n_pl
    return pd.DataFrame({"A_t": a_t, "A_m": (1 - p["relacion_ventana_muro"]) * bruto,
                         "A_v": p["relacion_ventana_muro"] * bruto, "V": v["area_construida"] * h}, index=v.index)


def carga(g, c):
    """Carga anual por componente (kWh/año)."""
    return pd.DataFrame({"cubierta": c["c_t"] * g["A_t"], "muros": c["c_m"] * g["A_m"],
                         "ventanas": c["c_v"] * g["A_v"], "infiltracion_sensible": c["c_V_sens"] * g["V"],
                         "latente": c["c_V_lat"] * g["V"]}, index=g.index)


def r2(y, grupos):
    """Fracción de la varianza de y explicada por los grupos (η²)."""
    y = pd.Series(np.asarray(y, float))
    medias = y.groupby(np.asarray(grupos)).transform("mean")
    return 1 - ((y - medias) ** 2).sum() / ((y - y.mean()) ** 2).sum()


def eta2_estrato(y, grupos, estrato):
    """η² conjunto del estrato dentro de los grupos (regla del Paso 4)."""
    y = pd.Series(np.asarray(y, float))
    g = np.asarray(grupos).astype(str)
    sc_g = ((y - y.groupby(g).transform("mean")) ** 2).sum()
    ge = pd.Series(g) + "|" + pd.Series(np.asarray(estrato)).astype(str)
    sc_ge = ((y - y.groupby(ge.to_numpy()).transform("mean")) ** 2).sum()
    return (sc_g - sc_ge) / sc_g
