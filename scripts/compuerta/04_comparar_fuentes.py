"""Compara la compuerta horaria con dos fuentes de ERA5-Land: la copia de Open-Meteo y la descarga de GDEX.

Antes de correrlo:
  1. Copiar las salidas de la corrida con Open-Meteo a salidas/fuente_openmeteo/ (o generarlas con
     `01_clima.py procesar --fuente=openmeteo`, `03_estimar.py` y copiarlas).
  2. Correr `01_clima.py procesar` (usa GDEX) y `03_estimar.py`.
Salida: salidas/comparacion_fuentes_clima.csv   b por franja (2021–2025 y por año), contraste con IDEAM y pruebas
                                                de la regla, con las dos fuentes y su diferencia.
"""
import json

import pandas as pd

from comun import SALIDAS

ANTES = SALIDAS / "fuente_openmeteo"


def main():
    filas = []
    fa, fg = pd.read_csv(ANTES / "franjas.csv"), pd.read_csv(SALIDAS / "franjas.csv")
    m = fa.merge(fg, on=["muestra", "franja"], suffixes=("_om", "_gdex"))
    for _, r in m.iterrows():
        filas.append({"bloque": "b por franja (%/°C)", "muestra": r["muestra"], "medida": r["franja"],
                      "openmeteo": r["b_om"], "gdex": r["b_gdex"],
                      "gdex_ic95": f"{r['ic_inf_gdex']:.2f} – {r['ic_sup_gdex']:.2f}",
                      "dias_openmeteo": r["n_dias_om"], "dias_gdex": r["n_dias_gdex"]})
    ca, cg = pd.read_csv(ANTES / "contraste_era5land_ideam.csv"), pd.read_csv(SALIDAS / "contraste_era5land_ideam.csv")
    for c in (ca, cg):
        c.drop(c[c["agrupacion"] != "total"].index, inplace=True)
    for (_, a), (_, g) in zip(ca.iterrows(), cg.iterrows()):
        for medida in ("sesgo", "rmse", "corr_diaria"):
            filas.append({"bloque": "contraste con IDEAM", "muestra": a["variable"], "medida": medida,
                          "openmeteo": a[medida], "gdex": g[medida], "dias_openmeteo": a["n"], "dias_gdex": g["n"]})
    da = json.loads((ANTES / "decision.json").read_text(encoding="utf-8"))
    dg = json.loads((SALIDAS / "decision.json").read_text(encoding="utf-8"))
    for clave in ("wald_homogeneidad_nivel_noche", "forma_noche_igual_entre_anios_p",
                  "forma_noche_contigua_igual_entre_anios_p", "forma_noche_amplitud_pp",
                  "corr_forma_2015_2019_vs_2021_2025", "capa"):
        a, g = da[clave], dg[clave]
        if isinstance(a, dict):
            a, g = a["p"], g["p"]
        filas.append({"bloque": "regla de la compuerta", "muestra": "2021-2025", "medida": clave,
                      "openmeteo": a, "gdex": g, "dias_openmeteo": da["dias_en_regresion"],
                      "dias_gdex": dg["dias_en_regresion"]})
    t = pd.DataFrame(filas)
    num = pd.to_numeric(t["openmeteo"], errors="coerce")
    t["dif_gdex_menos_openmeteo"] = pd.to_numeric(t["gdex"], errors="coerce") - num
    t.to_csv(SALIDAS / "comparacion_fuentes_clima.csv", index=False, float_format="%.4f")
    print(t[t["muestra"].isin(["2021-2025", "2015-2019 Electricaribe"]) | (t["bloque"] != "b por franja (%/°C)")]
          .round(3).to_string(index=False))


if __name__ == "__main__":
    main()
