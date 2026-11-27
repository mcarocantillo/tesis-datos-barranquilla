"""¿Cuánto de la carga explican las cuatro tipologías de CEELA frente a los arquetipos?

CEELA trabaja con cuatro tipologías residenciales: unifamiliar o multifamiliar, cada una de vivienda de interés social
(VIS) o no VIS (ceela2025b). Aquí se arman con el catastro igual que en su análisis del SUI: unifamiliar es la casa (C),
multifamiliar es el apartamento intermedio o de último piso (S y U), VIS son los estratos 1 y 2 y no VIS los estratos
3 a 6. Se comparan con los arquetipos finales y con la sola partición por posición y bloque de estratos.

Tres medidas, todas sobre la carga simplificada del Paso 3 de las 332.718 viviendas:
  r2_por_vivienda     fracción de la varianza de la carga por vivienda que explica la media de cada grupo
  r2_con_area         ŷ = (Σ carga / Σ área del grupo) × área de cada vivienda, frente a la carga por vivienda
  r2_por_m2           fracción de la varianza de la carga por m² que explica la media de cada grupo

Uso: python scripts/21_r2_tipologias_ceela.py
Salida:
  salidas/tablas/agr_r2_tipologias_ceela.csv   R² de cada agrupación con las tres medidas
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.comun import INTERNOS, TABLAS  # noqa: E402

c = pd.read_parquet(INTERNOS / "carga_viviendas.parquet")
y = c["total"].astype(float).to_numpy()
q = c["por_m2"].astype(float).to_numpy()
area = y / q


def r2_media(v, g):
    m = pd.Series(v).groupby(g).transform("mean").to_numpy()
    return 1 - ((v - m) ** 2).sum() / ((v - v.mean()) ** 2).sum()


def r2_con_area(g):
    s = pd.DataFrame({"g": g, "y": y, "a": area})
    k = s.groupby("g")["y"].transform("sum") / s.groupby("g")["a"].transform("sum")
    return 1 - ((y - k * area) ** 2).sum() / ((y - y.mean()) ** 2).sum()


a = pd.read_parquet(INTERNOS / "arquetipos_final.parquet")
pos_bloque = a["por_m2"].str.split("-").str[0]
ceela = (np.where(pos_bloque.str[0] == "C", "unifamiliar", "multifamiliar") + "_"
         + np.where(pos_bloque.str[1:] == "12", "VIS", "no_VIS"))
grupos = {"Tipologías de CEELA": ceela, "Posición × bloque de estratos": pos_bloque.to_numpy(),
          "Arquetipos por m²": a["por_m2"].to_numpy(), "Arquetipos por vivienda": a["por_vivienda"].to_numpy()}
filas = [{"agrupacion": n, "grupos": int(pd.Series(g).nunique()), "r2_por_vivienda": r2_media(y, g),
          "r2_con_area": r2_con_area(g), "r2_por_m2": r2_media(q, g)} for n, g in grupos.items()]
t = pd.DataFrame(filas).round(3)
t.to_csv(TABLAS / "agr_r2_tipologias_ceela.csv", index=False)
print(t.to_string(index=False))
print("\nViviendas por tipología de CEELA (%):")
print((pd.Series(ceela).value_counts(normalize=True) * 100).round(1).to_string())
