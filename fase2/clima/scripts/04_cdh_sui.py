"""Grados-hora de enfriamiento y respuesta mensual del consumo al calor por estrato (avance de la Ecuación 9).

Consumo: SUI, cubo de facturación O3, Barranquilla, residencial, solo suscriptores con lectura real, 2015–2025 sin
2020 (tablas/SUI_O3_Barranquilla_residencial_lectura_2015_2025.csv del repositorio). C_e,m = kWh / suscriptores.
Clima: serie horaria de 01_serie_clima.py.

El consumo facturado en el mes m corresponde a lecturas tomadas a lo largo del mes, así que cubre en parte el mes
anterior. Se prueban tres asignaciones del clima: el mismo mes, el mes anterior y la mitad de cada uno.

A. Temperatura base. Para cada base T_b de 24 a 32 °C se calcula CDH_m = Σ max(0, HI_t − T_b) (Ecuación 2) y se ajusta,
   en cada estrato, ln C_m = β·CDH_m + μ_año. La base con mayor R² dentro del año (sumando los seis estratos) es la
   estimada por punto de quiebre, como prevé la propuesta. No hay efecto fijo de mes, así que aquí β mezcla el
   calor con cualquier otra estacionalidad del consumo (por ejemplo, las vacaciones).
B. Ecuación 9 por estrato: ln C_m = β·HI_m + μ_año + ν_mes + ε, con HI_m el índice de calor medio del mes y errores
   HAC (3 rezagos). Con los efectos fijos de mes, β sale solo de las anomalías interanuales del calor del mismo mes;
   la propuesta anticipa que su intervalo puede ser ancho con una sola ciudad.

Uso:  python scripts/04_cdh_sui.py
Salidas (salidas/):
  cdh_base_perfil.csv       R² dentro del año por base, asignación y estrato
  cdh_sui_respuesta.csv     β de la Ecuación 9 por estrato y asignación (% por °C, IC 95 %), y β con la mejor base
"""
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

RAIZ = Path(__file__).resolve().parents[1]
BASE = RAIZ.parents[1]
SALIDAS = RAIZ / "salidas"
SUI = next(p for p in (BASE / "tesis-datos-barranquilla" / "tablas", BASE / "tablas") if p.exists()) / \
    "SUI_O3_Barranquilla_residencial_lectura_2015_2025.csv"
BASES = np.arange(24.0, 32.01, 0.5)
ASIGNACIONES = ["mismo_mes", "mes_anterior", "mitad_y_mitad"]


def consumo():
    d = pd.read_csv(SUI, sep=";")
    d = d[(d["lectura"] == "Real") & (d["anio"] != 2020)]
    d = d.groupby(["anio", "mes", "estrato"], as_index=False)[["suscriptores", "consumo_kWh"]].sum()
    d["lnC"] = np.log(d["consumo_kWh"] / d["suscriptores"])
    d["fecha"] = pd.to_datetime(dict(year=d["anio"], month=d["mes"], day=1))
    return d


def clima_mensual(s):
    fecha = (s.index - pd.Timedelta(seconds=1)).to_period("M").to_timestamp()
    g = s["HI"].groupby(fecha)
    m = pd.DataFrame({"HI": g.mean()})
    for tb in BASES:
        m[f"CDH_{tb:g}"] = g.apply(lambda x, tb=tb: (x - tb).clip(lower=0).sum())
    return m


def asignar(m, modo):
    if modo == "mismo_mes":
        return m
    previo = m.shift(1)
    return previo if modo == "mes_anterior" else (m + previo) / 2


def main():
    s = pd.read_parquet(SALIDAS / "clima_horario_barranquilla.parquet")
    cm = clima_mensual(s)
    d = consumo()

    perfiles, respuestas = [], []
    for modo in ASIGNACIONES:
        x = d.join(asignar(cm, modo), on="fecha").dropna()
        for tb in BASES:
            col = f"CDH_{tb:g}"
            for e, de in x.groupby("estrato"):
                y = de["lnC"] - de.groupby("anio")["lnC"].transform("mean")
                z = de[col] - de.groupby("anio")[col].transform("mean")
                b = (y * z).sum() / (z ** 2).sum() if (z ** 2).sum() > 0 else np.nan
                r2 = 1 - ((y - b * z) ** 2).sum() / (y ** 2).sum()
                perfiles.append({"asignacion": modo, "T_b": tb, "estrato": e, "r2_dentro_anio": r2,
                                 "beta_por_1000_CDH_%": 100 * b * 1000, "sc_res": ((y - b * z) ** 2).sum(),
                                 "sc_tot": (y ** 2).sum()})
        for e, de in x.groupby("estrato"):
            X = pd.get_dummies(de[["anio", "mes"]].astype(str), drop_first=True).astype(float)
            X.insert(0, "HI", de["HI"].to_numpy())
            X = sm.add_constant(X)
            r = sm.OLS(de["lnC"].to_numpy(), X).fit(cov_type="HAC", cov_kwds={"maxlags": 3})
            ci = r.conf_int().loc["HI"]
            respuestas.append({"asignacion": modo, "estrato": e, "n_meses": int(r.nobs),
                               "beta_%_por_C": 100 * r.params["HI"], "ic_inf": 100 * ci[0], "ic_sup": 100 * ci[1],
                               "p": r.pvalues["HI"], "r2": r.rsquared})

    pf = pd.DataFrame(perfiles)
    conj = pf.groupby(["asignacion", "T_b"])[["sc_res", "sc_tot"]].sum()
    conj["r2_conjunto"] = 1 - conj["sc_res"] / conj["sc_tot"]
    pf = pf.join(conj["r2_conjunto"], on=["asignacion", "T_b"])
    pf.drop(columns=["sc_res", "sc_tot"]).round(5).to_csv(SALIDAS / "cdh_base_perfil.csv", index=False)
    mejor = conj["r2_conjunto"].idxmax()
    rp = pd.DataFrame(respuestas)
    rp.round(4).to_csv(SALIDAS / "cdh_sui_respuesta.csv", index=False)

    print("R² conjunto dentro del año por base (filas) y asignación:")
    print(conj["r2_conjunto"].unstack(0).round(3).to_string())
    print(f"Mejor: asignación {mejor[0]}, T_b = {mejor[1]:g} °C")
    best = pf[(pf["asignacion"] == mejor[0])]
    print("Mejor base por estrato con esa asignación:")
    print(best.loc[best.groupby("estrato")["r2_dentro_anio"].idxmax(),
                   ["estrato", "T_b", "r2_dentro_anio", "beta_por_1000_CDH_%"]].round(3).to_string(index=False))
    print("Ecuación 9 (beta en % por °C de HI medio mensual):")
    print(rp.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
