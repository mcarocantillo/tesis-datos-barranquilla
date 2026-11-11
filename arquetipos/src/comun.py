"""Rutas, constantes y variables derivadas comunes a la Fase 1 (arquetipos de vivienda).

Todas las reglas salen de preregistro/decision_fase1.json; este módulo solo las aplica.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
ML = RAIZ.parent
VIVIENDAS = ML / "e2_git" / "datos" / "viviendas.pkl.gz"
PROCESADOS_E1 = ML / "e1_git" / "datos" / "procesados"  # número predial de cada vivienda, en el mismo orden
CLIMA = ML / "compuerta_horaria" / "datos" / "crudos" / "openmeteo"
TABLAS = RAIZ / "salidas" / "tablas"
FIGURAS = RAIZ / "salidas" / "figuras"
INTERNOS = RAIZ / "datos_internos"  # microdatos por vivienda: no se publican

DECISION = json.loads((RAIZ / "preregistro" / "decision_fase1.json").read_text(encoding="utf-8"))
SEMILLA = DECISION["semilla"]

POSICIONES = DECISION["variables"]["posicion"]
EPOCAS = DECISION["variables"]["epocas"]["etiquetas"]
BLOQUES = list(DECISION["variables"]["bloques_estrato"])
TIPOS = ["baja_altura", "multifamiliar"]


def cargar_viviendas():
    """Catastro limpio (332.718 viviendas) con las variables derivadas de la Fase 1."""
    v = pd.read_pickle(VIVIENDAS)
    v["torre_id"] = _torre(v)
    v["tipo"] = np.where(v["uso"].astype(str).str.contains("Apartamentos 4"), "multifamiliar", "baja_altura")
    v["posicion"] = _posicion(v)
    v["epoca"] = _epoca(v)
    bloque = {e: b for b, ests in DECISION["variables"]["bloques_estrato"].items() for e in ests}
    v["bloque"] = v["estrato_num"].map(bloque)
    return v


def asignar_epoca_faltante(v):
    """Viviendas sin época: la época con más viviendas de su tipo × posición × bloque (Sección 2)."""
    sin_epoca = v["epoca"].isna()
    moda = (v[~sin_epoca].groupby(["tipo", "posicion", "bloque"], observed=True)["epoca"]
            .agg(lambda s: s.value_counts().idxmax()))
    llave = pd.MultiIndex.from_frame(v.loc[sin_epoca, ["tipo", "posicion", "bloque"]].astype(str))
    v.loc[sin_epoca, "epoca"] = moda.reindex(llave).to_numpy()
    return sin_epoca


def _torre(v):
    """Edificio o torre de cada vivienda: los 24 primeros dígitos del número predial, que agregan el número de torre al
    predio matriz de `edificio_id` (Nota 11). La base sigue el orden de los parquet del trabajo previo."""
    npn = pd.concat([pd.read_parquet(PROCESADOS_E1 / f, columns=["numero_predial_nacional", "area_construida"])
                     for f in ["dataset_modelado.parquet", "sin_coordenadas.parquet"]], ignore_index=True)
    assert len(npn) == len(v) and np.allclose(npn["area_construida"], v["area_construida"], rtol=1e-5)
    return pd.factorize(npn["numero_predial_nacional"].astype(str).str[:24])[0]


def _posicion(v):
    p_ini = v["planta_ubicacion"]
    p_fin = p_ini + v["total_plantas"].fillna(1).clip(lower=1) - 1
    techo = p_fin.groupby(v["torre_id"]).transform("max")  # el techo de la torre, no del predio matriz (Nota 11)
    arriba = p_fin >= techo
    pos = np.select([arriba & (p_ini <= 1), arriba & (p_ini > 1)], ["casa", "ultimo_piso"], "sin_cubierta")
    # sin dato de piso: casa si es vivienda de baja altura fuera de PH; si no, sin cubierta
    sin_dato = p_ini.isna().to_numpy()
    casa_nph = (v["uso"].astype(str).str.contains("Hasta 3 Pisos") & ~v["uso"].astype(str).str.contains("PH")
                & (v["condicion_predio"].astype(str) == "NPH")).to_numpy()
    pos = np.where(sin_dato, np.where(casa_nph, "casa", "sin_cubierta"), pos)
    # en un multifamiliar, una unidad con suelo y techo propios se trata como último piso
    pos = np.where((pos == "casa") & (v["uso"].astype(str).str.contains("Apartamentos 4")), "ultimo_piso", pos)
    return pd.Categorical(pos, categories=POSICIONES)


def _epoca(v):
    cortes = DECISION["variables"]["epocas"]["cortes"]
    anio = v["anio_construccion"]
    ep = pd.cut(anio, [-np.inf, cortes[0], cortes[1], np.inf], right=False, labels=EPOCAS).astype(object)
    # S13: lotes de apartamentos 4+ de estratos 1-2 con año registrado implausible (mediana < 1975)
    apt = v["uso"].astype(str).str.contains("Apartamentos 4") & v["estrato_num"].isin([1, 2])
    med = anio[apt].groupby(v.loc[apt, "edificio_id"]).median()
    lotes_s13 = med.index[med < 1975]
    ep[apt & v["edificio_id"].isin(lotes_s13)] = np.nan
    return pd.Series(ep, index=v.index, name="epoca")
