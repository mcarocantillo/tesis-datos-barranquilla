"""Verificación de la base de arquetipos: comprobaciones automáticas de coherencia y reproducibilidad.

No recalcula el agrupamiento. Comprueba que las salidas guardadas sean coherentes entre sí y con el código:

  - la base de viviendas y la de arquetipos tienen las mismas filas, sin vacíos;
  - el código de cada arquetipo corresponde a la posición y el bloque de estratos de la vivienda;
  - los conteos y las cargas medianas de las tablas publicadas salen de la base;
  - la carga del Paso 3 se recalcula idéntica con src/carga.py;
  - el R² de cada solución y el de la partición por posición y bloque coinciden con los reportados;
  - el ajuste con la submuestra reproduce la solución final (control del script 10);
  - rangos de las variables y faltantes, como información.

Uso: python scripts/16_verificacion.py
Salida: salidas/tablas/verificacion.csv (comprobación, valor, esperado, resultado). Termina con error si alguna falla.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src import carga as cg  # noqa: E402
from src.comun import INTERNOS, TABLAS, asignar_epoca_faltante, cargar_viviendas  # noqa: E402

CORTO = {"casa": "C", "ultimo_piso": "U", "sin_cubierta": "S"}
MEDIDA = {"por_vivienda": "total", "por_m2": "por_m2"}
filas = []


def anotar(comprobacion, valor, esperado=None, ok=None):
    if ok is None:
        ok = esperado is None or valor == esperado
    filas.append({"comprobacion": comprobacion, "valor": valor, "esperado": "" if esperado is None else esperado,
                  "resultado": ("información" if esperado is None and ok is True else "pasa" if ok else "FALLA")})


def main():
    v = cargar_viviendas()
    arq = pd.read_parquet(INTERNOS / "arquetipos_final.parquet")
    q = pd.read_parquet(INTERNOS / "carga_viviendas.parquet")
    final = json.loads((TABLAS / "agr_resultado_final.json").read_text(encoding="utf-8"))

    anotar("viviendas en la base", len(v), 332718)
    anotar("misma longitud: base, arquetipos y cargas", int(len(v) == len(arq) == len(q)), 1)
    anotar("índice de la base es 0..n-1", int((v.index == np.arange(len(v))).all()), 1)
    estrato = v["posicion"].astype(str) + "|" + v["bloque"]
    prefijo = v["posicion"].astype(str).map(CORTO) + v["bloque"].str.replace("-", "")

    q2 = cg.carga(cg.geometria(v), cg.coeficientes())
    for c in q2.columns:
        anotar(f"carga recalculada = guardada: {c}", int(np.allclose(q2[c], q[c], rtol=1e-6)), 1)
    anotar("carga total = suma de componentes", int(np.allclose(q2.sum(axis=1), q["total"], rtol=1e-6)), 1)
    anotar("carga por m² = total / área", int(np.allclose(q["por_m2"], q["total"] / v["area_construida"], rtol=1e-6)), 1)

    for sol, medida in MEDIDA.items():
        a = arq[sol].astype(str)
        tabla = pd.read_csv(TABLAS / f"arquetipos_{sol}.csv").set_index("arquetipo")
        anotar(f"{sol}: viviendas sin arquetipo", int(arq[sol].isna().sum()), 0)
        anotar(f"{sol}: código = posición y bloque de la vivienda (%)",
               round(float((a.str.split("-").str[0] == prefijo).mean() * 100), 2), 100.0)
        anotar(f"{sol}: arquetipos en la base", int(a.nunique()), int(final[sol]["k_final"]))
        anotar(f"{sol}: cada arquetipo en un solo estrato del algoritmo", int(estrato.groupby(a).nunique().max()), 1)
        anotar(f"{sol}: conteos de la tabla = base", int((a.value_counts().reindex(tabla.index) == tabla["viviendas"]).all()), 1)
        anotar(f"{sol}: suma de la tabla", int(tabla["viviendas"].sum()), 332718)
        y = q[medida]
        col, dec = ("carga_mediana_kWh", 0) if medida == "total" else ("carga_m2_mediana_kWh", 1)
        med = y.groupby(a).median().reindex(tabla.index).round(dec)
        anotar(f"{sol}: carga mediana de la tabla = base", int(np.allclose(med, tabla[col], rtol=1e-3)), 1)
        anotar(f"{sol}: R² de los arquetipos", round(float(cg.r2(y, a)), 4), round(float(final[sol]["R2_final"]), 4))
        anotar(f"{sol}: R² de posición × bloque (referencia)", round(float(cg.r2(y, estrato)), 4))

    control = json.loads((TABLAS / "asg_incertidumbre.json").read_text(encoding="utf-8"))
    for clave, c in control.items():
        anotar(f"el ajuste con la submuestra reproduce la solución final: {clave}", c["reproduce_solucion_final"], 1.0)
    todos = TABLAS / "todos_resumen.json"
    if todos.exists():
        r = json.loads(todos.read_text(encoding="utf-8"))
        for sol in MEDIDA:
            anotar(f"{sol}: viviendas que conservan el arquetipo con todos los edificios (A10)",
                   r[sol]["viviendas_que_conservan_arquetipo"])

    anotar("casas con piso de la unidad mayor que 1", int(((v["posicion"] == "casa") & (v["planta_ubicacion"] > 1)).sum()), 0)
    sin_epoca = asignar_epoca_faltante(v)
    anotar("viviendas sin año: época asignada por la regla de la Sección 2", int(sin_epoca.sum()))
    anotar("viviendas con época después de la regla", int(v["epoca"].notna().sum()), len(v))
    anotar("viviendas con año 1986 (%)", round(float((v["anio_construccion"] == 1986).mean() * 100), 1))
    anotar("año 1986 dentro de «antes de 1990» (%)",
           round(float((v["anio_construccion"] == 1986).sum() / (v["epoca"] == "antes_1990").sum() * 100), 1))
    for c in ["area_construida", "anio_construccion", "total_plantas", "planta_ubicacion"]:
        anotar(f"{c}: mínimo, mediana y máximo", f"{v[c].min():g}, {v[c].median():g}, {v[c].max():g}")
    anotar("viviendas sin coordenadas (se asignan por sus atributos)", int((~v["tiene_coordenadas"].astype(bool)).sum()))

    t = pd.DataFrame(filas)
    t.to_csv(TABLAS / "verificacion.csv", index=False, encoding="utf-8-sig")
    print(t.to_string(index=False))
    fallas = (t["resultado"] == "FALLA").sum()
    print(f"\n{len(t)} comprobaciones, {fallas} fallas")
    sys.exit(1 if fallas else 0)


if __name__ == "__main__":
    main()
