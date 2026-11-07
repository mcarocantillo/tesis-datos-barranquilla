"""EDA del catastro multipropósito de Barranquilla (Gerencia de Gestión Catastral, servicio catastro/datosabiertos).

Entradas (solo lectura, no se publican):
  Downloads/catastro_arquetipos_v2/catastro_arquetipos_v2/datos_crudos/*.parquet   tablas 105, 305, 500, 505, 505-305, 602
  Downloads/catastro_arquetipos (1)/catastro_arquetipos/datos_crudos/*.parquet     descarga con la que se armó la base
                                                                                   (agrega 315 y 601, con el centroide)
  Downloads/base_de_datos_predios_barranquilla/predios_residenciales_barranquilla.csv  una fila por registro de 505
  ml_trabajo/e1_git/src/limpieza.py                     reglas de limpieza (embudo de 382.597 a 332.718 filas)
  ml_trabajo/e2_git/datos/viviendas.pkl.gz              las 332.718 viviendas limpias (coordenadas a 3 decimales)
  ml_trabajo/arquetipos/datos_internos/catastro_materiales/cat_535_calificacion.csv   tabla 535
  tablas/SUI_Barranquilla_urbano_residencial_2015_2026.csv   suscriptores de diciembre de 2024

Salidas: figuras/eda/catastro_*.png y tablas/eda/catastro_*.csv, solo agregados (ninguna fila por vivienda, ningún
identificador; el mapa usa celdas de 500 m con al menos 10 viviendas).

Uso, desde la raíz del repositorio:  python scripts/eda/catastro.py
"""
import importlib.util
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # no dejar __pycache__ en las carpetas de solo lectura
sys.path.insert(0, str(Path(__file__).parent))
from estilo import *  # noqa: E402,F401,F403
from estilo import GRID, TXT2  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import ListedColormap, LogNorm  # noqa: E402

CRUDOS_V2 = DESCARGAS / "catastro_arquetipos_v2" / "catastro_arquetipos_v2" / "datos_crudos"
CRUDOS_BASE = DESCARGAS / "catastro_arquetipos (1)" / "catastro_arquetipos" / "datos_crudos"
CSV = DESCARGAS / "base_de_datos_predios_barranquilla" / "predios_residenciales_barranquilla.csv"
VIVIENDAS = ML / "e2_git" / "datos" / "viviendas.pkl.gz"
E1_SRC = ML / "e1_git" / "src"
M535 = ML / "arquetipos" / "datos_internos" / "catastro_materiales" / "cat_535_calificacion.csv"
SUI = REPO / "tablas" / "SUI_Barranquilla_urbano_residencial_2015_2026.csv"

FUENTE = "Fuente: Catastro de Barranquilla, Gerencia de Gestión Catastral (2026)."
ESTRATOS = [f"E{i}" for i in range(1, 7)]
CELDA_KM, MIN_CELDA = 0.5, 10
np.random.seed(SEMILLA)


def pct(a, b):
    return 100 * a / b if b else np.nan


def guid(s):
    return s.astype(str).str.strip("{}").str.upper()


# ---------------------------------------------------------------------------------------------------------------
# 1. Tamaño de cada tabla y llaves de unión
# ---------------------------------------------------------------------------------------------------------------
def tablas_y_llaves():
    def leer(carpeta, nombre):
        ruta = carpeta / f"{nombre}.parquet"
        return pd.read_parquet(ruta) if ruta.exists() else None

    nombres = {"505": "505_caracteristicas_residenciales", "505_305": "505_305_enlace",
               "305": "305_unidades_construccion", "602": "602_unidad_predio", "500": "500_predios",
               "105": "105_direccion", "315": "315_terreno_centroide", "601": "601_terreno_predio"}
    v2 = {k: leer(CRUDOS_V2, n) for k, n in nombres.items()}
    base = {k: leer(CRUDOS_BASE, n) for k, n in nombres.items()}

    # tasas de empalme con la descarga v2 (la que trae la tabla 105); 315 y 601 solo existen en la otra
    t = {k: (d.copy() if d is not None else None) for k, d in v2.items()}
    t["315"], t["601"] = base["315"].copy(), base["601"].copy()
    for k, col in (("505_305", "uc_globalid"), ("305", "globalid"), ("602", "cr_unidadconstruccion_guid"),
                   ("602", "cr_predio_guid"), ("500", "globalid"), ("105", "cr_predio_guid"), ("315", "globalid"),
                   ("601", "cr_terreno_guid"), ("601", "cr_predio_guid")):
        t[k][col] = guid(t[k][col])
    c, e, u, r, p, d = t["505"], t["505_305"], t["305"], t["602"], t["500"], t["105"]
    r1 = r.drop_duplicates()
    tp = t["601"].drop_duplicates()
    uc_res = e["uc_globalid"].unique()
    pred_res = r1.loc[r1["cr_unidadconstruccion_guid"].isin(uc_res), "cr_predio_guid"].unique()
    filas = [
        ("505", "Características de la unidad (solo residenciales)", "objectid", "con enlace a 305",
         pct(c["objectid"].isin(e["carac_objectid"]).sum(), len(c))),
        ("505–305", "Enlace características → unidad de construcción (queryRelatedRecords)", "carac_objectid, uc_globalid",
         "unidades del enlace que están en 305", pct(e["uc_globalid"].isin(u["globalid"]).sum(), len(e))),
        ("305", "Unidades de construcción", "globalid", "unidades residenciales con predio en 602",
         pct(pd.Series(uc_res).isin(r1["cr_unidadconstruccion_guid"]).sum(), len(uc_res))),
        ("602", "Relación unidad de construcción ↔ predio", "cr_unidadconstruccion_guid, cr_predio_guid",
         "predios de 602 que están en 500", pct(r1["cr_predio_guid"].isin(p["globalid"]).sum(), len(r1))),
        ("500", "Predios (estrato, condición, área del terreno)", "globalid; numero_predial_nacional",
         "predios con vivienda que tienen dirección en 105", pct(pd.Series(pred_res).isin(d["cr_predio_guid"]).sum(),
                                                                 len(pred_res))),
        ("105", "Dirección del predio", "cr_predio_guid", "registros marcados como dirección principal",
         pct((d["es_direccion_principal"] == 1).sum(), len(d))),
        ("315", "Terreno (polígono; se guarda su centroide)", "globalid", "terrenos con predio en 601",
         pct(t["315"]["globalid"].isin(tp["cr_terreno_guid"]).sum(), len(t["315"]))),
        ("601", "Relación terreno ↔ predio", "cr_terreno_guid, cr_predio_guid", "predios con vivienda con terreno propio",
         pct(pd.Series(pred_res).isin(tp["cr_predio_guid"]).sum(), len(pred_res))),
    ]
    clave = {"505": "505", "505–305": "505_305", "305": "305", "602": "602", "500": "500", "105": "105",
             "315": "315", "601": "601"}
    out = pd.DataFrame(filas, columns=["tabla", "contenido", "llave", "empalme", "pct_empalme"])
    out["filas_descarga_v2"] = [len(v2[clave[x]]) if v2[clave[x]] is not None else np.nan for x in out["tabla"]]
    out["filas_descarga_base"] = [len(base[clave[x]]) if base[clave[x]] is not None else np.nan for x in out["tabla"]]
    out["columnas_descargadas"] = [t[clave[x]].shape[1] for x in out["tabla"]]
    out["pct_empalme"] = out["pct_empalme"].round(2)

    extra = {
        "pares repetidos en 602": int(r.duplicated().sum()),
        "unidades de construcción en más de un predio (602)": int((r1.groupby("cr_unidadconstruccion_guid").size() > 1).sum()),
        "registros de 505 con más de una unidad de construcción": int((e.groupby("carac_objectid").size() > 1).sum()),
        "máximo de unidades por registro de 505": int(e.groupby("carac_objectid").size().max()),
        "números prediales repetidos en 500": int(p["numero_predial_nacional"].duplicated().sum()),
        "predios de 500 con estrato No_Aplica u Otro": int(p["estrato"].astype(str).str.contains("Aplica|Otro").sum()),
        "registros de 505 residenciales": len(c),
        "garajes y depósitos en 505": int(c["uso"].str.contains("Garajes|Depositos").sum()),
        "unidades de 305 con piso 99": int((u["planta_ubicacion"] == 99).sum()),
        "unidades de 305 con altura de 3 m": pct((u["altura"] == 3).sum(), len(u)),
        "direcciones con sector_predio": pct(d["sector_predio"].notna().sum(), len(d)),
    }
    print(out.to_string(index=False))
    print(pd.Series(extra).to_string())
    tabla(out, "catastro_tablas.csv", index=False)
    tabla(pd.Series(extra, name="valor").rename_axis("concepto").reset_index(), "catastro_tablas_extra.csv",
          index=False)
    return out


# ---------------------------------------------------------------------------------------------------------------
# 2. Embudo de limpieza (reglas de e1_git/src/limpieza.py, sin modificarlas)
# ---------------------------------------------------------------------------------------------------------------
def cargar_limpieza():
    spec = importlib.util.spec_from_file_location("e1src", E1_SRC / "__init__.py",
                                                  submodule_search_locations=[str(E1_SRC)])
    mod = importlib.util.module_from_spec(spec)
    sys.modules["e1src"] = mod
    spec.loader.exec_module(mod)
    import importlib as il
    return il.import_module("e1src.limpieza")


def embudo():
    L = cargar_limpieza()
    crudo = L.cargar_crudo(CSV)
    limpio, emb, imp = L.limpiar(crudo, verbose=False)
    emb = emb[["paso", "filas", "cambio", "% del total inicial", "motivo"]]
    print(emb.to_string(index=False))
    print(imp.to_string(index=False))
    fuente = crudo["centroide_fuente"].value_counts(dropna=False)
    print("centroide_fuente en el CSV:\n" + fuente.to_string())
    tabla(emb, "catastro_embudo.csv", index=False)
    tabla(imp.round(3), "catastro_imposibles.csv", index=False)
    fl = limpio["centroide_fuente"].fillna("sin_dato").value_counts().rename("viviendas").to_frame()
    fl["pct"] = (100 * fl["viviendas"] / len(limpio)).round(2)
    tabla(fl.rename_axis("origen_coordenada").reset_index(), "catastro_coordenadas.csv", index=False)
    print(fl.to_string())
    return limpio, emb, imp


# ---------------------------------------------------------------------------------------------------------------
# Viviendas limpias y variables derivadas (misma regla de posición que arquetipos/src/comun.py y
# scripts/catastro_cubierta.py)
# ---------------------------------------------------------------------------------------------------------------
def viviendas():
    v = pd.read_pickle(VIVIENDAS)
    v["EST"] = "E" + v["estrato_num"].astype(int).astype(str)
    uso = v["uso"].astype(str)
    v["tipo"] = np.where(uso.str.contains("Apartamentos 4"), "multifamiliar", "baja_altura")
    p_ini = v["planta_ubicacion"]
    p_fin = p_ini + v["total_plantas"].fillna(1).clip(lower=1) - 1
    v["pisos_edificio"] = p_fin.groupby(v["edificio_id"]).transform("max")
    arriba = p_fin >= v["pisos_edificio"]
    # cuatro posiciones (tab-posicion de 10_insumos.md)
    v["posicion4"] = np.select([p_ini.isna(), arriba & (p_ini <= 1), arriba & (p_ini > 1), p_ini <= 1],
                               ["sin_dato", "casa", "ultimo_piso", "primer_piso_con_vivienda_encima"],
                               "intermedio")
    # tres posiciones de la Fase 1 (arquetipos/src/comun.py::_posicion)
    pos = np.select([arriba & (p_ini <= 1), arriba & (p_ini > 1)], ["casa", "ultimo_piso"], "sin_cubierta")
    casa_nph = (uso.str.contains("Hasta 3 Pisos") & ~uso.str.contains("PH")
                & (v["condicion_predio"].astype(str) == "NPH")).to_numpy()
    pos = np.where(p_ini.isna().to_numpy(), np.where(casa_nph, "casa", "sin_cubierta"), pos)
    pos = np.where((pos == "casa") & uso.str.contains("Apartamentos 4").to_numpy(), "ultimo_piso", pos)
    v["posicion3"] = pos
    return v


# ---------------------------------------------------------------------------------------------------------------
# 3. Viviendas por estrato frente a los suscriptores del SUI
# ---------------------------------------------------------------------------------------------------------------
def estrato_sui(v):
    s = pd.read_csv(SUI, sep=";", encoding="utf-8-sig", dtype={"estrato": str})
    s = s[(s["anio"] == 2024) & (s["mes"] == 12) & s["estrato"].isin(list("123456"))]
    s = s.set_index("E" + s["estrato"])["suscriptores"]
    c = v["EST"].value_counts().reindex(ESTRATOS)
    t = pd.DataFrame({"viviendas_catastro": c, "suscriptores_sui_dic2024": s.reindex(ESTRATOS)})
    t["pct_catastro"] = 100 * t["viviendas_catastro"] / t["viviendas_catastro"].sum()
    t["pct_sui"] = 100 * t["suscriptores_sui_dic2024"] / t["suscriptores_sui_dic2024"].sum()
    t["dif_puntos"] = t["pct_catastro"] - t["pct_sui"]
    t["razon_catastro_sui"] = t["viviendas_catastro"] / t["suscriptores_sui_dic2024"]
    tot = pd.DataFrame({"viviendas_catastro": [t["viviendas_catastro"].sum()],
                        "suscriptores_sui_dic2024": [t["suscriptores_sui_dic2024"].sum()],
                        "pct_catastro": [100.0], "pct_sui": [100.0], "dif_puntos": [0.0],
                        "razon_catastro_sui": [t["viviendas_catastro"].sum() / t["suscriptores_sui_dic2024"].sum()]},
                       index=["Total"])
    D = 0.5 * t["dif_puntos"].abs().sum()
    t = pd.concat([t, tot]).round(3)
    print(t.to_string())
    print(f"índice de disimilitud catastro–SUI 2024: {D:.2f} %")
    tabla(t.rename_axis("estrato").reset_index(), "catastro_estrato_sui.csv", index=False)

    fig, ax = plt.subplots(figsize=(9, 4.6))
    x = np.arange(6)
    ax.bar(x - 0.2, t.loc[ESTRATOS, "pct_catastro"], 0.4, color=[EST[e] for e in ESTRATOS], label="Catastro 2026 (viviendas)")
    ax.bar(x + 0.2, t.loc[ESTRATOS, "pct_sui"], 0.4, color="none", edgecolor=[EST[e] for e in ESTRATOS], hatch="///",
           linewidth=1.2, label="SUI, diciembre de 2024 (suscriptores)")
    for i, e in enumerate(ESTRATOS):
        ax.text(i - 0.2, t.loc[e, "pct_catastro"] + 0.6, fmt(t.loc[e, "pct_catastro"]), ha="center", fontsize=9)
        ax.text(i + 0.2, t.loc[e, "pct_sui"] + 0.6, fmt(t.loc[e, "pct_sui"]), ha="center", fontsize=9, color=TXT2)
    ax.set_xticks(x, ESTRATOS)
    ax.set_ylabel("% del total de estratos 1 a 6")
    ax.legend(loc="upper right")
    titulo(ax, "Viviendas del catastro y suscriptores del SUI por estrato",
           f"{fmt(t.loc['Total', 'viviendas_catastro'], 0)} viviendas y "
           f"{fmt(t.loc['Total', 'suscriptores_sui_dic2024'], 0)} suscriptores; índice de disimilitud {fmt(D)} %")
    guardar(fig, "catastro_estrato_sui.png", FUENTE + " SUI (Superservicios).")
    return t, D


# ---------------------------------------------------------------------------------------------------------------
# 4. Distribuciones por estrato
# ---------------------------------------------------------------------------------------------------------------
VARS = [("area_construida", "Área construida (m²)", True), ("pisos_edificio", "Pisos del edificio", False),
        ("planta_ubicacion", "Piso de la unidad", False), ("anio_construccion", "Año de construcción", False),
        ("total_habitaciones", "Habitaciones", False), ("total_banios", "Baños", False)]


def distribuciones(v):
    filas = []
    for var, nombre, _ in VARS:
        for e in ESTRATOS + ["Total"]:
            s = v[var] if e == "Total" else v.loc[v["EST"] == e, var]
            q = s.quantile([.05, .25, .5, .75, .95])
            filas.append({"variable": var, "estrato": e, "n": int(s.notna().sum()), "faltantes": int(s.isna().sum()),
                          "media": s.mean(), "p05": q[.05], "p25": q[.25], "mediana": q[.5], "p75": q[.75],
                          "p95": q[.95]})
    t = pd.DataFrame(filas).round(2)
    tabla(t, "catastro_distribuciones.csv", index=False)
    print(t[t.estrato.isin(["E1", "E3", "E6", "Total"])].to_string(index=False))

    fig, axs = plt.subplots(2, 3, figsize=(13, 7.6))
    for ax, (var, nombre, logy) in zip(axs.ravel(), VARS):
        datos = [v.loc[v["EST"] == e, var].dropna().to_numpy() for e in ESTRATOS]
        st = [{"med": np.percentile(d, 50), "q1": np.percentile(d, 25), "q3": np.percentile(d, 75),
               "whislo": np.percentile(d, 5), "whishi": np.percentile(d, 95), "label": e} for d, e in zip(datos, ESTRATOS)]
        b = ax.bxp(st, showfliers=False, patch_artist=True, widths=0.6,
                   medianprops={"color": "#0b0b0b", "linewidth": 1.4})
        for patch, e in zip(b["boxes"], ESTRATOS):
            patch.set_facecolor(EST[e])
            patch.set_alpha(0.75)
        ax.plot(range(1, 7), [d.mean() for d in datos], "o", color="#0b0b0b", ms=4, zorder=5)
        if logy:
            ax.set_yscale("log")
            ax.set_yticks([20, 50, 100, 200, 500])
            ax.set_yticklabels(["20", "50", "100", "200", "500"])
            ax.yaxis.set_minor_formatter(plt.NullFormatter())
        ax.set_title(nombre, fontsize=11.5, fontweight="bold")
    fig.suptitle("Atributos de la vivienda por estrato (caja P25–P75, bigotes P5–P95, punto = media)",
                 x=0.01, ha="left", fontsize=13, fontweight="bold")
    guardar(fig, "catastro_distribuciones.png", FUENTE + " 332.718 viviendas.")
    return t


def anio(v):
    """Año de construcción por tipo de edificio: los bloques de E1–E2 con años de 1932 a 1972 (supuesto S13)."""
    apt12 = (v["tipo"] == "multifamiliar") & v["estrato_num"].isin([1, 2])
    grupos = {"Baja altura (hasta 3 pisos)": v["tipo"] == "baja_altura",
              "Multifamiliar, estratos 3 a 6": (v["tipo"] == "multifamiliar") & ~apt12,
              "Multifamiliar, estratos 1 y 2": apt12}
    bins = np.arange(1930, 2028, 2)
    fig, ax = plt.subplots(figsize=(11, 4.8))
    abajo = np.zeros(len(bins) - 1)
    colores = [PAL[0], PAL[6], PAL[1]]
    filas = []
    for (n, m), col in zip(grupos.items(), colores):
        h, _ = np.histogram(v.loc[m, "anio_construccion"].dropna(), bins)
        ax.bar(bins[:-1], h, width=2, bottom=abajo, align="edge", color=col, label=n, edgecolor="none")
        abajo += h
        a = v.loc[m, "anio_construccion"]
        filas.append({"grupo": n, "viviendas": int(m.sum()), "antes_1975": int((a < 1975).sum()),
                      "1975_1989": int(a.between(1975, 1989).sum()), "1990_2009": int(a.between(1990, 2009).sum()),
                      "2010_o_despues": int((a >= 2010).sum()), "sin_anio": int(a.isna().sum())})
    t = pd.DataFrame(filas)
    # casas (posición casa) anteriores a 1975, cifra citada en 11_coherencia.md
    casas = v["posicion4"] == "casa"
    a = v["anio_construccion"]
    top = a.value_counts().head(5)
    extra = {"casas_antes_1975": int((casas & (a < 1975)).sum()),
             "baja_altura_antes_1975": int(((v["tipo"] == "baja_altura") & (a < 1975)).sum()),
             **{f"anio_{int(k)}": int(n) for k, n in top.items()},
             "viviendas_con_anio": int(v["anio_construccion"].notna().sum()),
             "apt_E1E2_4mas_antes_1975": int((apt12 & (v["anio_construccion"] < 1975)).sum()),
             "edificios_E1E2_4mas_mediana_antes_1975": int((v[apt12].groupby("edificio_id")["anio_construccion"]
                                                            .median() < 1975).sum())}
    print(t.to_string(index=False))
    print(extra)
    t = pd.concat([t, pd.DataFrame([{"grupo": k, "viviendas": val} for k, val in extra.items()])], ignore_index=True)
    tabla(t, "catastro_anio.csv", index=False)
    ax.set_xlabel("Año de construcción registrado (intervalos de 2 años)")
    ax.set_ylabel("Viviendas")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: fmt(x, 0)))
    ax.legend(loc="upper left")
    titulo(ax, "Año de construcción del catastro por tipo de edificio",
           f"Solo {fmt(extra['baja_altura_antes_1975'], 0)} viviendas de baja altura antes de 1975; "
           f"{fmt(extra['apt_E1E2_4mas_antes_1975'], 0)} apartamentos de E1–E2 en bloques con años de 1932 a 1972")
    guardar(fig, "catastro_anio.png", FUENTE)
    return t, extra


# ---------------------------------------------------------------------------------------------------------------
# 5. Posición frente a la cubierta
# ---------------------------------------------------------------------------------------------------------------
def posicion(v):
    orden4 = ["casa", "ultimo_piso", "intermedio", "primer_piso_con_vivienda_encima", "sin_dato"]
    n4 = pd.crosstab(v["EST"], v["posicion4"]).reindex(columns=orden4, fill_value=0)
    p4 = n4.div(n4.sum(axis=1), axis=0) * 100
    orden3 = ["casa", "ultimo_piso", "sin_cubierta"]
    n3 = pd.crosstab(v["EST"], v["posicion3"]).reindex(columns=orden3, fill_value=0)
    p3 = n3.div(n3.sum(axis=1), axis=0) * 100
    edif4 = v.groupby("EST")["tipo"].apply(lambda s: 100 * (s == "multifamiliar").mean())
    tot4 = n4.sum() / n4.values.sum() * 100
    tot3 = n3.sum() / n3.values.sum() * 100
    t = pd.concat({"pct_posicion4": pd.concat([p4, tot4.to_frame("Total").T]),
                   "pct_posicion3": pd.concat([p3, tot3.to_frame("Total").T])}, axis=1).round(2)
    t[("pct_tipo", "multifamiliar_4_o_mas")] = pd.concat([edif4, pd.Series({"Total": 100 * (v["tipo"] == "multifamiliar").mean()})]).round(2)
    t[("n", "viviendas")] = pd.concat([n4.sum(axis=1), pd.Series({"Total": len(v)})])
    t.columns = [f"{a}|{b}" for a, b in t.columns]
    print(t.to_string())
    tabla(t.rename_axis("estrato").reset_index(), "catastro_posicion.csv", index=False)

    fig, axs = plt.subplots(1, 2, figsize=(13, 4.9), gridspec_kw={"width_ratios": [1.15, 1]})
    etq4 = {"casa": "Casa (suelo y techo propios)", "ultimo_piso": "Último piso",
            "intermedio": "Piso intermedio", "primer_piso_con_vivienda_encima": "Primer piso con vivienda encima",
            "sin_dato": "Sin dato de piso"}
    col4 = {"casa": PAL[1], "ultimo_piso": PAL[3], "intermedio": PAL[0], "primer_piso_con_vivienda_encima": PAL[6],
            "sin_dato": "#bdbcb7"}
    ax = axs[0]
    izq = np.zeros(6)
    for c in orden4:
        ax.barh(ESTRATOS[::-1], p4[c].reindex(ESTRATOS)[::-1], left=izq[::-1], color=col4[c], label=etq4[c])
        izq += p4[c].reindex(ESTRATOS).to_numpy()
    for i, e in enumerate(ESTRATOS[::-1]):
        bajo = p4.loc[e, "casa"] + p4.loc[e, "ultimo_piso"]
        ax.text(101, i, f"{fmt(bajo)} %", va="center", fontsize=9, color=TXT2)
    ax.set_xlim(0, 112)
    ax.set_xlabel("% de las viviendas del estrato (a la derecha: bajo cubierta)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=3, fontsize=8.5)
    titulo(ax, "Posición frente a la cubierta")
    ax = axs[1]
    for i, e in enumerate(ESTRATOS):
        sub = v[v["EST"] == e]
        h = sub.groupby("pisos_edificio").size()
        h = h[h.index <= 20]
        ax.plot(h.index, 100 * h.cumsum() / len(sub), color=EST[e], lw=2, label=e)
    ax.set_xlabel("Pisos del edificio (máximo piso con vivienda)")
    ax.set_ylabel("% acumulado de viviendas")
    ax.set_xticks([1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20])
    ax.legend(ncol=3, loc="lower right")
    titulo(ax, "Altura del edificio donde está la vivienda")
    guardar(fig, "catastro_posicion.png", FUENTE)
    return t, p4, p3


# ---------------------------------------------------------------------------------------------------------------
# 6. Faltantes y valores imposibles en las viviendas limpias
# ---------------------------------------------------------------------------------------------------------------
def faltantes(v, limpio):
    cols = ["area_construida", "area_catastral_terreno", "total_habitaciones", "total_banios", "total_plantas",
            "planta_ubicacion", "anio_construccion"]
    t = pd.DataFrame({e: v.loc[v["EST"] == e, cols].isna().mean() * 100 for e in ESTRATOS})
    t["Total"] = v[cols].isna().mean() * 100
    t["n_total"] = v[cols].isna().sum()
    coord = pd.Series({e: 100 * (~v.loc[v["EST"] == e, "tiene_coordenadas"]).mean() for e in ESTRATOS})
    coord["Total"], coord["n_total"] = 100 * (~v["tiene_coordenadas"]).mean(), int((~v["tiene_coordenadas"]).sum())
    man = pd.Series({e: 100 * v.loc[v["EST"] == e, "ubicado_por_manzana"].mean() for e in ESTRATOS})
    man["Total"], man["n_total"] = 100 * v["ubicado_por_manzana"].mean(), int(v["ubicado_por_manzana"].sum())
    t.loc["sin_coordenadas"] = coord
    t.loc["ubicada_por_centroide_de_manzana"] = man
    inf = pd.Series({e: 100 * (v.loc[v["EST"] == e, "condicion_predio"].astype(str) == "Informal").mean() for e in ESTRATOS})
    inf["Total"] = 100 * (v["condicion_predio"].astype(str) == "Informal").mean()
    inf["n_total"] = int((v["condicion_predio"].astype(str) == "Informal").sum())
    t.loc["condicion_informal"] = inf
    flags = limpio.filter(like="flag_").sum()
    t = t.round(3)
    print(t.to_string())
    print(flags.to_string())
    tabla(t.rename_axis("variable").reset_index(), "catastro_faltantes.csv", index=False)
    return t


# ---------------------------------------------------------------------------------------------------------------
# 7. Materiales (tabla 535, calificación convencional)
# ---------------------------------------------------------------------------------------------------------------
def materiales():
    c = pd.read_csv(M535, dtype=str)
    n = len(c)
    g = guid(c["cr_caracteristicasunidad_guid"].fillna(""))
    info = {"registros_535": n, "sin_llave_505": int(c["cr_caracteristicasunidad_guid"].isna().sum()),
            "llaves_505_distintas": int(g[c["cr_caracteristicasunidad_guid"].notna()].nunique()),
            "con_cubierta": int(c["cubierta"].notna().sum()), "con_muros": int(c["muros"].notna().sum()),
            "con_armazon": int(c["armazon"].notna().sum()),
            "con_puntaje": int(pd.to_numeric(c["total_calificacion"], errors="coerce").notna().sum()),
            "solo_puntaje_sin_materiales": int((c[["armazon", "muros", "cubierta", "fachada", "cubrimiento_muros",
                                                   "piso", "conservacion_estructura"]].isna().all(axis=1)).sum())}
    filas = []
    for campo in ["cubierta", "muros", "armazon"]:
        vc = c[campo].fillna("Sin dato").value_counts()
        for k, val in vc.items():
            filas.append({"campo": campo, "categoria": k, "registros": int(val), "pct": round(100 * val / n, 2),
                          "pct_con_dato": round(100 * val / c[campo].notna().sum(), 2) if k != "Sin dato" else np.nan})
    t = pd.DataFrame(filas)
    tabla(t, "catastro_materiales.csv", index=False)
    tabla(pd.Series(info, name="valor").rename_axis("concepto").reset_index(), "catastro_materiales_resumen.csv",
          index=False)
    print(info)
    print(t.to_string(index=False))

    etq = {"Zinc_Teja_De_Barro_Eternit_Rustico": "Zinc, teja de barro o eternit rústico",
           "Azotea_Aluminio_Placa_Sencilla_Con_Eternit": "Azotea, aluminio o placa sencilla con eternit",
           "Eternit_O_Teja_De_Barro_Cubierta_Sencilla": "Eternit o teja de barro, cubierta sencilla",
           "Placa_Impermeabilizada_Lujosa_U_Ornamental": "Placa impermeabilizada, lujosa u ornamental",
           "Placa_Impermeabilizada_Cubierta_Lujosa_U_Ornamental": "Placa impermeabilizada, cubierta lujosa",
           "Entrepiso_Cubierta_Provisional_Prefabricado": "Entrepiso, cubierta provisional o prefabricada",
           "Materiales_Desecho_Telas_Asfalticas": "Desechos o telas asfálticas",
           "Bloque_Ladrillo": "Bloque o ladrillo", "Concreto_Prefabricado": "Concreto prefabricado",
           "Madera": "Madera", "Materiales_Desecho_Esterilla": "Desechos o esterilla",
           "Bahareque_Adobe_Tapia": "Bahareque, adobe o tapia"}
    fig, axs = plt.subplots(1, 2, figsize=(13, 4.8), gridspec_kw={"width_ratios": [1.25, 1]})
    for ax, campo, col in zip(axs, ["cubierta", "muros"], [PAL[1], PAL[0]]):
        s = t[(t.campo == campo) & (t.categoria != "Sin dato")].sort_values("registros")
        ax.barh([etq.get(k, k) for k in s["categoria"]], s["pct_con_dato"], color=col)
        for i, val in enumerate(s["pct_con_dato"]):
            ax.text(val + 0.8, i, f"{fmt(val)} %", va="center", fontsize=9)
        falta = 100 * c[campo].isna().mean()
        ax.set_xlim(0, max(s["pct_con_dato"]) * 1.22)
        ax.set_xlabel("% de los registros con dato")
        ax.tick_params(axis="y", labelsize=9)
        titulo(ax, "Cubierta" if campo == "cubierta" else "Muros",
               f"{fmt(falta)} % de los {fmt(n, 0)} registros sin dato")
    guardar(fig, "catastro_materiales.png", FUENTE + " Tabla 535 (calificación convencional), descarga del 3-nov-2026.")
    return t, info


# ---------------------------------------------------------------------------------------------------------------
# 8. Mapa agregado: celdas de 500 m con al menos 10 viviendas
# ---------------------------------------------------------------------------------------------------------------
def mapa(v):
    lat0, lon0, R = 10.9837, -74.7766, 6371.0088  # centro y radio de e1_git/src/config.py
    m = v["tiene_coordenadas"]
    x = (v.loc[m, "lon"].astype(float) - lon0) * np.pi / 180 * R * np.cos(np.radians(lat0))
    y = (v.loc[m, "lat"].astype(float) - lat0) * np.pi / 180 * R
    ix, iy = np.floor(x / CELDA_KM).astype(int), np.floor(y / CELDA_KM).astype(int)
    d = pd.DataFrame({"ix": ix, "iy": iy, "e": v.loc[m, "estrato_num"].astype(int)})
    g = d.groupby(["ix", "iy"])
    celdas = pd.DataFrame({"viviendas": g.size(), "estrato_modal": g["e"].agg(lambda s: s.value_counts().idxmax()),
                           "pct_modal": g["e"].agg(lambda s: 100 * s.value_counts().iloc[0] / len(s))})
    total_celdas = len(celdas)
    ok = celdas[celdas["viviendas"] >= MIN_CELDA]
    resumen = {"celdas_con_viviendas": total_celdas, "celdas_publicadas": len(ok),
               "viviendas_en_celdas_publicadas": int(ok["viviendas"].sum()),
               "pct_viviendas_ubicadas_en_celdas_publicadas": round(100 * ok["viviendas"].sum() / m.sum(), 2),
               "viviendas_por_celda_mediana": float(ok["viviendas"].median()),
               "viviendas_por_celda_max": int(ok["viviendas"].max()),
               "pct_modal_mediano": round(float(ok["pct_modal"].median()), 1),
               "celdas_modal_E1": int((ok["estrato_modal"] == 1).sum())}
    por_estrato = ok.groupby("estrato_modal").agg(celdas=("viviendas", "size"), viviendas=("viviendas", "sum"),
                                                   pct_modal_mediano=("pct_modal", "median")).round(1)
    print(resumen)
    print(por_estrato.to_string())
    tabla(pd.Series(resumen, name="valor").rename_axis("concepto").reset_index(), "catastro_mapa_resumen.csv",
          index=False)
    tabla(por_estrato.rename(index=lambda i: f"E{i}").rename_axis("estrato_modal").reset_index(),
          "catastro_mapa_por_estrato.csv", index=False)

    xs = np.arange(ok.index.get_level_values(0).min(), ok.index.get_level_values(0).max() + 2)
    ys = np.arange(ok.index.get_level_values(1).min(), ok.index.get_level_values(1).max() + 2)
    dens = np.full((len(ys) - 1, len(xs) - 1), np.nan)
    moda = np.full_like(dens, np.nan)
    for (a, b), r in ok.iterrows():
        dens[b - ys[0], a - xs[0]] = r["viviendas"]
        moda[b - ys[0], a - xs[0]] = r["estrato_modal"]
    X, Y = xs * CELDA_KM, ys * CELDA_KM
    fig, axs = plt.subplots(1, 2, figsize=(13, 6.4))
    pc = axs[0].pcolormesh(X, Y, dens, cmap="viridis_r", norm=LogNorm(vmin=MIN_CELDA, vmax=np.nanmax(dens)))
    cb = fig.colorbar(pc, ax=axs[0], shrink=0.8)
    cb.set_label("Viviendas por celda de 500 m")
    titulo(axs[0], "Densidad de viviendas")
    cmap = ListedColormap([EST[e] for e in ESTRATOS])
    pm = axs[1].pcolormesh(X, Y, moda, cmap=cmap, vmin=0.5, vmax=6.5)
    cb2 = fig.colorbar(pm, ax=axs[1], shrink=0.8, ticks=range(1, 7))
    cb2.ax.set_yticklabels(ESTRATOS)
    cb2.set_label("Estrato modal")
    titulo(axs[1], "Estrato más frecuente de la celda")
    for ax in axs:
        ax.set_aspect("equal")
        ax.set_xlabel("km al este del centro histórico")
        ax.set_ylabel("km al norte del centro histórico")
        ax.grid(color=GRID, lw=0.5)
    guardar(fig, "catastro_mapa.png",
            FUENTE + f" Celdas de 500 m con al menos {MIN_CELDA} viviendas ({fmt(resumen['pct_viviendas_ubicadas_en_celdas_publicadas'], 2)} % de las viviendas ubicadas).")
    return resumen, por_estrato


def main():
    tablas_y_llaves()
    limpio, emb, imp = embudo()
    v = viviendas()
    assert len(v) == len(limpio) == 332_718, (len(v), len(limpio))
    print(f"edificios (prefijo de 22 dígitos): {v['edificio_id'].nunique():,}")
    viv_por_edif = v.groupby("edificio_id").size()
    print(viv_por_edif.describe().to_string())
    estructura = {"viviendas": len(v), "edificios": int(v["edificio_id"].nunique()),
                  "viviendas_por_edificio_mediana": float(viv_por_edif.median()),
                  "viviendas_por_edificio_max": int(viv_por_edif.max()),
                  "edificios_con_1_vivienda_pct": round(100 * (viv_por_edif == 1).mean(), 2),
                  "pct_tipo_vivienda_no_aplica": round(100 * (v["tipo_vivienda"].astype(str) == "No Aplica").mean(), 2),
                  "pct_vis": round(100 * (v["tipo_vivienda"].astype(str) == "Vivienda de Interés Social").mean(), 2),
                  "pct_vip": round(100 * (v["tipo_vivienda"].astype(str) == "Vivienda de Interés Prioritario").mean(), 2),
                  "pct_altura_3m": round(100 * (v["altura"] == 3).mean(), 2)}
    print(estructura)
    tabla(pd.Series(estructura, name="valor").rename_axis("concepto").reset_index(), "catastro_estructura.csv",
          index=False)
    estrato_sui(v)
    distribuciones(v)
    anio(v)
    posicion(v)
    faltantes(v, limpio)
    materiales()
    mapa(v)


if __name__ == "__main__":
    main()
