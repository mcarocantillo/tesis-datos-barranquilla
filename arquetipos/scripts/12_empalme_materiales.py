"""Empalme de los materiales del catastro (calificación convencional) con las 332.718 viviendas de la Fase 1.

Las tablas son de la Gerencia de Gestión Catastral (preregistro, Nota 13):

  datos_internos/catastro_materiales/entrega_2026-11-19/  entrega de la Gerencia del 19-nov-2026, en parquet:
      535_calificacion                 cubierta, muros, armazón, etc. (con etiquetas) y estado de conservación;
                                       llave cr_caracteristicasunidad_guid
      505_caracteristicas_residencial  objectid y GUID_Caracteristica (= globalid de la 505)
  Downloads/catastro_arquetipos_v2/.../datos_crudos/       descarga del servicio catastro/datosabiertos (17-sep-2026):
      505_caracteristicas_residenciales  año, área, uso y pisos de cada registro de 505 (objectid)
      505_305_enlace                   unidades de construcción (305) de cada registro de 505
      305_unidades_construccion        planta de cada unidad
      602_unidad_predio                unidad de construcción -> predio
      500_predios                      número predial nacional

Los atributos de la 505 se toman de la descarga del servicio, porque en el Excel de la entrega algunas áreas perdieron
el separador decimal. La entrega no trae la tabla 545 (visitas), así que el resultado de la visita queda vacío.

Cadena: 535 -> 505 -> 305 -> 602 -> 500 -> número predial. La base de viviendas sale, en el mismo orden, de los
parquet procesados del primer trabajo, que guardan el número predial. Un registro de 505 puede describir varias
unidades, y un predio puede tener varias viviendas; el empalme va por etapas:

  unico                un solo registro con ese número predial en la base y en el catastro
  atributos            número predial + área + año + planta + uso, únicos en los dos lados
  area                 número predial + área, únicos en los dos lados
  materiales_iguales   todas las unidades del catastro con ese número predial tienen los mismos materiales
  ambiguo              no se pudo decidir; sin materiales
  sin_predio           el número predial no aparece en el catastro descargado

Uso: python scripts/12_empalme_materiales.py
Salidas:
  datos_internos/viviendas_materiales.parquet   una fila por vivienda, mismo orden que la base (no se publica)
  salidas/tablas/materiales_empalme.csv         viviendas por etapa de empalme
  salidas/tablas/materiales_cobertura.csv       calificación completa, solo puntaje o sin registro, por tipo,
                                                posición, bloque y época (celdas con menos de 30 viviendas, fuera)
  salidas/tablas/materiales_por_visita.csv      estado de la calificación según el resultado de la visita
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.comun import INTERNOS, ML, TABLAS, cargar_viviendas  # noqa: E402

ENTREGA = INTERNOS / "catastro_materiales" / "entrega_2026-11-19"
CRUDOS = ML.parent / "catastro_arquetipos_v2" / "catastro_arquetipos_v2" / "datos_crudos"
PROCESADOS = ML / "e1_git" / "datos" / "procesados"
MATERIALES = ["armazon", "muros", "cubierta", "fachada", "cubrimiento_muros", "piso", "conservacion_estructura"]
N_MIN = 30


def guid(s):
    return s.astype(str).str.strip("{}").str.upper()


def llave(df, cols):
    return df[cols[0]].astype(str).str.cat([df[c].astype(str) for c in cols[1:]], sep="|")


def leer():
    c535 = pd.read_parquet(ENTREGA / "535_calificacion.parquet")
    c535 = c535.rename(columns={c535.columns[-1]: "estado_conservacion"})  # «Estado Conservación»
    llave505 = pd.read_parquet(ENTREGA / "505_caracteristicas_residencial.parquet",
                               columns=["objectid", "GUID_Caracteristica"])
    c505 = pd.read_parquet(CRUDOS / "505_caracteristicas_residenciales.parquet")
    c505["objectid"] = c505["objectid"].astype(int)
    llave505["objectid"] = llave505["objectid"].astype(int)
    c505 = c505.merge(llave505.rename(columns={"GUID_Caracteristica": "globalid"}), on="objectid", how="left",
                      validate="one_to_one")
    c305 = pd.read_parquet(CRUDOS / "305_unidades_construccion.parquet", columns=["globalid", "planta_ubicacion"])
    rel = pd.read_parquet(CRUDOS / "505_305_enlace.parquet").rename(
        columns={"carac_objectid": "objectid_505", "uc_globalid": "globalid_305"})
    rel["objectid_505"] = rel["objectid_505"].astype(int)
    rel = rel.merge(c305.rename(columns={"globalid": "globalid_305"}), on="globalid_305", how="left")
    c602 = pd.read_parquet(CRUDOS / "602_unidad_predio.parquet")
    c500 = pd.read_parquet(CRUDOS / "500_predios.parquet", columns=["globalid", "numero_predial_nacional"])
    return c535, c505, rel, c602, c500


def unidades_catastro(c535, c505, rel, c602, c500):
    """Una fila por unidad de construcción residencial, con sus materiales y su predio."""
    c535["guid505"] = guid(c535["cr_caracteristicasunidad_guid"])
    c535["objectid"] = pd.to_numeric(c535["objectid"])
    c535["total_calificacion"] = pd.to_numeric(c535["total_calificacion"], errors="coerce")
    dup = c535["guid505"].duplicated().sum()
    c535 = c535.sort_values("objectid").drop_duplicates("guid505")
    sin_llave = int(c505["globalid"].isna().sum())
    c505["guid505"] = guid(c505["globalid"]).where(c505["globalid"].notna())
    u = rel.rename(columns={"objectid_505": "objectid"}).merge(
        c505.drop(columns="globalid"), on="objectid", how="left", validate="many_to_one")
    u = u.merge(c535[["guid505", "total_calificacion", "estado_conservacion", *MATERIALES]], on="guid505",
                how="left")
    u["calificacion"] = np.where(u["cubierta"].notna(), "completa",
                                 np.where(u["total_calificacion"].notna(), "solo_puntaje", "sin_registro"))
    u["guid305"] = guid(u["globalid_305"])
    c602["guid305"], c602["guid500"] = guid(c602["cr_unidadconstruccion_guid"]), guid(c602["cr_predio_guid"])
    multi = c602["guid305"].duplicated(keep=False)
    u = u.merge(c602.loc[~multi, ["guid305", "guid500"]], on="guid305", how="left")
    c500["guid500"] = guid(c500["globalid"])
    u = u.merge(c500[["guid500", "numero_predial_nacional"]], on="guid500", how="left", validate="many_to_one")
    u["resultado_visita"], u["anio_visita"] = pd.NA, np.nan  # sin tabla 545 en la entrega
    print(f"535: {len(c535):,} registros ({dup:,} duplicados por registro de 505 descartados); "
          f"505 residencial sin llave en la entrega: {sin_llave:,} de {len(c505):,}")
    print(f"unidades 305 de 505 residencial: {len(u):,}; con predio: {u['numero_predial_nacional'].notna().sum():,}"
          f" ({multi.sum():,} filas de 602 con la unidad en varios predios, fuera)")
    return u[u["numero_predial_nacional"].notna()].reset_index(drop=True)


def empalmar(base, u):
    """Asigna a cada vivienda de la base la unidad del catastro que le corresponde (por etapas)."""
    salida = pd.DataFrame(index=base.index, columns=["fila_u", "empalme"], dtype=object)
    # mismos tipos en los dos lados, para que las llaves de texto coincidan
    norm = {"a": lambda d: d["area_construida"].astype(float).round(1),
            "anio": lambda d: pd.to_numeric(d["anio_construccion"], errors="coerce").astype(float),
            "p": lambda d: d["planta_ubicacion"].astype(float).fillna(-1)}
    b = base.assign(**{k: f(base) for k, f in norm.items()})
    c = u.assign(**{k: f(u) for k, f in norm.items()}, uso=u["uso"].astype(str))
    libre_b, libre_u = pd.Series(True, index=b.index), pd.Series(True, index=c.index)
    etapas = {"unico": ["numero_predial_nacional"],
              "atributos": ["numero_predial_nacional", "a", "anio", "p", "uso"],
              "area": ["numero_predial_nacional", "a"]}
    for etapa, cols in etapas.items():
        kb, kc = llave(b.loc[libre_b], cols), llave(c.loc[libre_u], cols)
        unicas = kb[~kb.duplicated(keep=False)]
        cu = kc[~kc.duplicated(keep=False)]
        par = pd.Series(cu.index, index=cu.to_numpy()).reindex(unicas.to_numpy())
        ok = par.notna().to_numpy()
        filas_b, filas_u = unicas.index[ok], par.to_numpy()[ok].astype(int)
        salida.loc[filas_b, "fila_u"], salida.loc[filas_b, "empalme"] = filas_u, etapa
        libre_b[filas_b], libre_u[filas_u] = False, False
    # Predios cuyas unidades del catastro tienen todas los mismos materiales
    firma = llave(c, MATERIALES + ["total_calificacion"])
    por_npn = firma.groupby(c["numero_predial_nacional"]).nunique()
    iguales = por_npn.index[por_npn == 1]
    primera = pd.Series(c.index, index=c["numero_predial_nacional"]).groupby(level=0).first()
    resto = libre_b & b["numero_predial_nacional"].isin(iguales)
    salida.loc[resto, "fila_u"] = primera.reindex(b.loc[resto, "numero_predial_nacional"]).to_numpy()
    salida.loc[resto, "empalme"] = "materiales_iguales"
    libre_b &= ~resto
    en_cat = b["numero_predial_nacional"].isin(c["numero_predial_nacional"])
    salida.loc[libre_b & en_cat, "empalme"] = "ambiguo"
    salida.loc[libre_b & ~en_cat, "empalme"] = "sin_predio"
    return salida


def cobertura(v):
    filas = []
    cortes = {"total": [], "tipo": ["tipo"], "posicion": ["posicion"], "bloque": ["bloque"], "epoca": ["epoca"],
              "tipo_posicion_bloque_epoca": ["tipo", "posicion", "bloque", "epoca"]}
    for nombre, por in cortes.items():
        g = v.groupby(por, observed=True) if por else v.assign(_t="total").groupby("_t")
        t = g["calificacion"].value_counts(normalize=True).unstack(fill_value=0).mul(100).round(1)
        t["n"] = g.size()
        t = t[t["n"] >= N_MIN].reset_index()
        t.insert(0, "corte", nombre)
        filas.append(t)
    return pd.concat(filas, ignore_index=True)


def main():
    u = unidades_catastro(*leer())
    base = pd.concat([pd.read_parquet(PROCESADOS / f"{f}.parquet") for f in ["dataset_modelado", "sin_coordenadas"]],
                     ignore_index=True)
    base["uso"] = base["uso"].astype(str)
    v = cargar_viviendas()
    assert len(base) == len(v) and np.allclose(base["area_construida"], v["area_construida"], equal_nan=True)
    emp = empalmar(base, u)
    cols = MATERIALES + ["total_calificacion", "calificacion", "estado_conservacion", "resultado_visita",
                         "anio_visita"]
    fila = pd.to_numeric(emp["fila_u"], errors="coerce")
    mat = u.reindex(fila.fillna(-1).astype(int).to_numpy())[cols].reset_index(drop=True)
    mat.loc[fila.isna().to_numpy(), "calificacion"] = "sin_empalme"
    mat["empalme"] = emp["empalme"].to_numpy()
    mat.to_parquet(INTERNOS / "viviendas_materiales.parquet", index=False)

    resumen = mat["empalme"].value_counts().rename("n").to_frame()
    resumen["pct"] = (100 * resumen["n"] / len(mat)).round(2)
    resumen.rename_axis("empalme").to_csv(TABLAS / "materiales_empalme.csv")
    print("\nEmpalme:\n" + resumen.to_string())
    v["calificacion"] = mat["calificacion"].to_numpy()
    cob = cobertura(v)
    cob.to_csv(TABLAS / "materiales_cobertura.csv", index=False)
    print("\nCobertura (total y por corte simple):\n" + cob[cob["corte"] != "tipo_posicion_bloque_epoca"].to_string(index=False))
    if mat["resultado_visita"].isna().all():
        return
    vis = (mat.assign(resultado_visita=mat["resultado_visita"].fillna("sin dato"))
           .groupby("resultado_visita")["calificacion"].value_counts().unstack(fill_value=0))
    vis = vis[vis.sum(axis=1) >= N_MIN]
    vis.to_csv(TABLAS / "materiales_por_visita.csv")
    print("\nCalificación según el resultado de la visita:\n" + vis.to_string())


if __name__ == "__main__":
    main()
