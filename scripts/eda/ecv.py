"""Análisis exploratorio de la Encuesta de Calidad de Vida (ECV, DANE) en Barranquilla.

Lee los microdatos de la ECV 2019 (catálogo 678) y la ECV 2024 (catálogo 861) tal como los publica el DANE,
en Downloads/DANE/ECV, y las tablas agregadas del repositorio para las demás olas (2018, 2020 a 2023 y 2025),
que no tienen microdatos locales. Solo escribe agregados: figuras en figuras/eda/ecv_*.png y tablas en
tablas/eda/ecv_*.csv. Las celdas con menos de 10 hogares de muestra quedan marcadas (columna «n_menor_10»).

Correr desde la raíz del repositorio:
    python scripts/eda/ecv.py
"""
import io
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from estilo import *  # noqa: E402,F401,F403
from estilo import TXT2  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ECV = DESCARGAS / "DANE" / "ECV"
TABLAS = REPO / "tablas"
K2 = ["DIRECTORIO", "SECUENCIA_ENCUESTA"]
ESTRATOS = [f"E{i}" for i in range(1, 7)]
GRIS = "#9a9993"
C19, C24 = "#9a9993", PAL[6]          # colores de las olas 2019 y 2024 (no se confunden con los estratos)
FUENTE = "Fuente: DANE, ECV, microdatos; cálculos propios con factores de expansión."
np.random.seed(SEMILLA)               # nada es aleatorio; se fija por convención del repositorio


# ----------------------------------------------------------------------------------------------- lectura
def leer_zip(ruta, patron, columnas=None):
    """Lee el CSV de un zip del DANE (separador «;»), todo como texto y sin espacios sobrantes."""
    with zipfile.ZipFile(ECV / ruta) as zf:
        nombre = [x for x in zf.namelist() if x.lower().endswith(".csv") and patron in x.lower()][0]
        crudo = zf.read(nombre)
    try:
        texto = crudo.decode("utf-8-sig")
    except UnicodeDecodeError:
        texto = crudo.decode("latin-1")
    d = pd.read_csv(io.StringIO(texto), sep=";", dtype=str, low_memory=False)
    d.columns = [c.replace("ï»¿", "").strip("\ufeff").strip() for c in d.columns]
    d = d[columnas] if columnas else d
    return d.apply(lambda s: s.str.strip())


def num(s):
    return pd.to_numeric(s.astype(str).str.strip().str.replace(",", "."), errors="coerce")


def vacio(s):
    return s.isna() | (s.astype(str).str.strip() == "")


def hogares_2019():
    """Hogares de Barranquilla, ECV 2019. El municipio viene en un archivo aparte (por DIRECTORIO); las
    características de la vivienda se pegan a todos sus hogares; los archivos de hogar se unen por
    DIRECTORIO + SECUENCIA_ENCUESTA (número de hogar dentro de la vivienda)."""
    m = leer_zip("ECV 2019/Municipio de aplicacion de la encuesta 2019_ECV_2019.zip", "municipio")
    v = leer_zip("ECV 2019/Datos de la vivienda_ECV_2019.zip", "vivienda",
                 ["DIRECTORIO", "P1_DEPARTAMENTO", "CLASE", "P1070", "P4567", "P8520S1A1"]).merge(m, on="DIRECTORIO")
    v = v[(v.P1_DEPARTAMENTO == "08") & (v.P1_MUNICIPIO == "001")]
    s = leer_zip("ECV 2019/Servicios del hogar_ECV_2019.zip", "servicios",
                 K2 + ["P5000", "P5010", "CANT_PERSONAS_HOGAR", "PERCAPITA", "FEX_C"])
    e = leer_zip("ECV 2019/Uso de energeticos del hogar_ECV_2019.zip", "energ",
                 K2 + ["P5514", "P5515", "P5523", "P5524", "P5525S1", "P5525S2", "P5525S3", "P5525S4", "P5526",
                       "P5018", "P5018S1"])
    t = leer_zip("ECV 2019/Tenencia y financiacion de la vivienda que ocupa el hogar_ECV_2019.zip", "tenencia",
                 K2 + ["P5095"])
    h = s[s.DIRECTORIO.isin(v.DIRECTORIO)].merge(v, on="DIRECTORIO").merge(e, on=K2, how="left").merge(t, on=K2, how="left")
    vent = h[["P5525S1", "P5525S2", "P5525S3", "P5525S4"]].eq("1").any(axis=1) | (num(h.P5526).fillna(0) > 0)
    d = pd.DataFrame({
        "anio": 2019, "viviendas": h.DIRECTORIO, "segmento": np.nan, "clase": h.CLASE,
        "estrato": num(h.P8520S1A1), "w": num(h.FEX_C),
        "ac": (~vacio(h.P5523)).astype(float), "vent": vent.astype(float), "nevera": (~vacio(h.P5514)).astype(float),
        "tipo_ac": num(h.P5523), "horas_ac": num(h.P5524), "horas_vent": num(h.P5526),
        "nevera_anios": num(h.P5515), "techo": num(h.P4567), "tipo_viv": num(h.P1070),
        "personas": num(h.CANT_PERSONAS_HOGAR), "cuartos": num(h.P5000), "dormitorios": num(h.P5010),
        "percapita": num(h.PERCAPITA), "tenencia": num(h.P5095),
        "pago": num(h.P5018), "meses_pago": num(h.P5018S1), "no_paga": (num(h.P5018) == 0).astype(float),
    })
    return d, h


def hogares_2024():
    """Hogares de Barranquilla, ECV 2024. El municipio viene en «Datos de la vivienda»; los hogares se toman del
    archivo de bienes y se unen a los demás archivos por DIRECTORIO + SECUENCIA_ENCUESTA."""
    v = leer_zip("ECV 2024/DBF-ENCV-Datos_vivienda-2024 (2).zip", "vivienda",
                 ["DIRECTORIO", "P1_DEPARTAMENTO", "P1_MUNICIPIO", "CLASE", "P1070", "P4567", "P8520S1A1"])
    v = v[(v.P1_DEPARTAMENTO == "08") & (v.P1_MUNICIPIO == "001")]
    seg = leer_zip("ECV 2024/BDF-ENCV-Variables_diseno_muestral-ENCV2024.zip", "muestral", ["DIRECTORIO", "SEGMENTO"])
    seg = seg.drop_duplicates("DIRECTORIO").set_index("DIRECTORIO").SEGMENTO
    b = leer_zip("ECV 2024/DBF-ENCV-Condiciones_vida_hogar_tenencia_bienes-2024.zip", "bienes",
                 K2 + ["FEX_C", "P1077S11", "P1077S12", "P1077S2"])
    s = leer_zip("ECV 2024/DBF-ENCV-Servicios_hogar-2024.zip", "servicios",
                 K2 + ["P5000", "P5010", "P791", "P5018", "P5018S1", "CANT_PERSONAS_HOGAR", "PERCAPITA"])
    t = leer_zip("ECV 2024/DBF-ENCV-Tenencia_financiacion_vivienda_ocupa_hogar-2024.zip", "tenencia", K2 + ["P5095"])
    h = b[b.DIRECTORIO.isin(v.DIRECTORIO)].merge(v, on="DIRECTORIO").merge(s, on=K2, how="left").merge(t, on=K2, how="left")
    h["SEGMENTO"] = h.DIRECTORIO.map(seg)
    assert h.SEGMENTO.notna().all(), "hogares sin segmento"
    d = pd.DataFrame({
        "anio": 2024, "viviendas": h.DIRECTORIO, "segmento": h.SEGMENTO, "clase": h.CLASE,
        "estrato": num(h.P8520S1A1), "w": num(h.FEX_C),
        "ac": h.P1077S11.eq("1").astype(float), "vent": h.P1077S12.eq("1").astype(float),
        "nevera": h.P1077S2.eq("1").astype(float),
        "tipo_ac": np.nan, "horas_ac": np.nan, "horas_vent": np.nan, "nevera_anios": np.nan,
        "techo": num(h.P4567), "tipo_viv": num(h.P1070),
        "personas": num(h.CANT_PERSONAS_HOGAR), "cuartos": num(h.P5000), "dormitorios": num(h.P5010),
        "percapita": num(h.PERCAPITA), "tenencia": num(h.P5095),
        "pago": num(h.P5018), "meses_pago": num(h.P5018S1), "no_paga": h.P791.eq("3").astype(float),
        "p791": num(h.P791),
    })
    return d, h


# ----------------------------------------------------------------------------------- estadísticos ponderados
def wq(x, w, q):
    """Cuantil ponderado: primer valor cuyo peso acumulado alcanza q (como en 04_metodologia)."""
    x, w = np.asarray(x, float), np.asarray(w, float)
    m = ~np.isnan(x)
    x, w = x[m], w[m]
    if len(x) == 0:
        return np.nan
    i = np.argsort(x, kind="stable")
    x, w = x[i], w[i]
    c = np.cumsum(w) / w.sum()
    return x[min(np.searchsorted(c, q), len(x) - 1)]


def wmean(x, w):
    m = x.notna()
    return (x[m] * w[m]).sum() / w[m].sum() if m.any() else np.nan


def wpct(cond, w):
    return 100 * w[cond].sum() / w.sum() if w.sum() > 0 else np.nan


def kish(w):
    """Efecto de diseño por la variación de los pesos (Kish): n·Σw²/(Σw)², y n efectivo."""
    w = np.asarray(w, float)
    d = len(w) * (w ** 2).sum() / w.sum() ** 2
    return d, len(w) / d


def var_conglomerados(h, y, dom):
    """Proporción ponderada en el dominio y su varianza por linealización de Taylor con los segmentos como
    unidades primarias sorteadas con reemplazo (igual que deff_ecv24.py)."""
    wd = h.w * dom
    p = (wd * y).sum() / wd.sum()
    z = wd * (y - p) / wd.sum()
    tc = z.groupby(h.segmento).sum()
    C = h.segmento.nunique()
    return p, C / (C - 1) * ((tc - tc.mean()) ** 2).sum()


def marca(n):
    return "sí" if n < 10 else ""


# ------------------------------------------------------------------------------------------------- datos
print("Leyendo microdatos de la ECV 2019 y 2024 ...")
h19, crudo19 = hogares_2019()
h24, crudo24 = hogares_2024()
H = pd.concat([h19, h24], ignore_index=True)
H["E"] = H.estrato.map({i: f"E{i}" for i in range(1, 7)})
B = H[H.E.notna()].copy()                       # hogares de estratos 1 a 6 (todo el municipio)

serie = pd.read_csv(TABLAS / "ECV_2018_2025_Barranquilla_tenencia_por_estrato.csv", sep=";", encoding="utf-8-sig",
                    dtype={"grupo": str})
post = pd.read_csv(TABLAS / "ECV_2018_2025_AC_postestratificado_SUI.csv", sep=";", encoding="utf-8-sig", decimal=",")
sui = pd.read_csv(TABLAS / "SUI_Barranquilla_urbano_residencial_2015_2026.csv", sep=";", encoding="utf-8-sig",
                  dtype={"estrato": str})
sui = sui[(sui.mes == 12) & sui.estrato.isin(list("123456"))].assign(E=lambda d: "E" + d.estrato)
SUI = sui.set_index(["anio", "E"]).suscriptores

for a, d in H.groupby("anio"):
    print(f"{a}: {len(d)} hogares en {d.viviendas.nunique()} viviendas; cabecera {int((d.clase == '1').sum())}; "
          f"E1–E6 {int(d.estrato.between(1, 6).sum())}; suma de factores {d.w.sum():,.0f}")

# ------------------------------------------------------------------------ 1. muestra por ola y estrato
filas = []
for a, d in serie.groupby("anio"):
    g = d.set_index("grupo")
    tot = int(g.loc["T", "n"])
    for e in "123456":
        n, w = int(g.loc[e, "n"]), float(g.loc[e, "w"])
        s = SUI.get((a, f"E{e}"), np.nan)
        filas.append(dict(anio=a, estrato=f"E{e}", hogares_muestra=n, hogares_expandidos=round(w),
                          suscriptores_SUI_dic=s, expandidos_sobre_SUI=w / s, n_menor_10=marca(n)))
    sin = tot - int(g.loc[list("123456"), "n"].sum())
    filas.append(dict(anio=a, estrato="Sin estrato (0, 8, 9 o vacío)", hogares_muestra=sin,
                      hogares_expandidos=round(float(g.loc["T", "w"] - g.loc[list("123456"), "w"].sum())),
                      suscriptores_SUI_dic=np.nan, expandidos_sobre_SUI=np.nan, n_menor_10=marca(sin)))
    st = SUI.loc[a].sum() if a in SUI.index.get_level_values(0) else np.nan
    filas.append(dict(anio=a, estrato="Total", hogares_muestra=tot, hogares_expandidos=round(float(g.loc["T", "w"])),
                      suscriptores_SUI_dic=st, expandidos_sobre_SUI=float(g.loc["T", "w"]) / st, n_menor_10=""))
muestra = pd.DataFrame(filas)
muestra["ola_usada"] = np.where(muestra.anio == 2020, "no (parte telefónica)", "sí")
tabla(muestra.round(3), "ecv_muestra_olas.csv", index=False)

fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 5.2), gridspec_kw=dict(width_ratios=[1.05, 1]))
anios = sorted(serie.anio.unique())
base = np.zeros(len(anios))
for e in ESTRATOS + ["Sin estrato (0, 8, 9 o vacío)"]:
    v = muestra[muestra.estrato == e].set_index("anio").hogares_muestra.reindex(anios).values
    a1.bar(anios, v, bottom=base, color=EST.get(e, "#d6d5d0"), label=e if e in EST else "Sin estrato",
           edgecolor="white", lw=.6)
    base += v
for x, t in zip(anios, base):
    a1.text(x, t + 12, fmt(t, 0), ha="center", fontsize=9, color=TXT2)
a1.bar([2020], [base[anios.index(2020)]], color="white", alpha=.55, hatch="//", edgecolor=GRIS, lw=0)
a1.text(2020, base[anios.index(2020)] / 2, "no se\nusa", ha="center", va="center", fontsize=9, color=TXT2)
a1.set_xticks(anios)
a1.set_ylabel("hogares en la muestra")
a1.legend(ncol=4, fontsize=9, loc="upper right", bbox_to_anchor=(1, 1.0))
a1.set_ylim(0, 1250)
titulo(a1, "Hogares encuestados en Barranquilla", "Por ola y estrato de la tarifa de energía")
M = muestra[muestra.estrato.isin(ESTRATOS)].pivot(index="estrato", columns="anio", values="expandidos_sobre_SUI")
N = muestra[muestra.estrato.isin(ESTRATOS)].pivot(index="estrato", columns="anio", values="hogares_muestra")
im = a2.imshow(M.values, cmap="RdBu_r", vmin=0.3, vmax=1.7, aspect="auto")
for i in range(M.shape[0]):
    for j in range(M.shape[1]):
        val, n = M.values[i, j], N.values[i, j]
        a2.text(j, i, fmt(val, 2) + ("*" if n < 10 else ""), ha="center", va="center", fontsize=9,
                color="white" if abs(val - 1) > .45 else "#0b0b0b")
a2.set_xticks(range(M.shape[1]), M.columns)
a2.set_yticks(range(M.shape[0]), M.index)
a2.grid(False)
cb = fig.colorbar(im, ax=a2, fraction=.04, pad=.02)
cb.set_label("hogares expandidos / suscriptores SUI", color=TXT2)
titulo(a2, "Expansión de la ECV frente al SUI", "Razón por estrato; * menos de 10 hogares en la muestra")
guardar(fig, "ecv_muestra_olas.png", "Fuente: tablas ECV_2018_2025_Barranquilla_tenencia_por_estrato.csv y "
        "SUI_Barranquilla_urbano_residencial_2015_2026.csv (diciembre).")

# ------------------------------------------------------------------------ 2. factores de expansión
filas = []
dominios = pd.concat([B, H.assign(E="Ciudad (todos los hogares)"), H[H.clase == "1"].assign(E="Cabecera"),
                      H[H.clase != "1"].assign(E="Resto (centros poblados y rural)")])
for (a, e), d in dominios.groupby(["anio", "E"]):
    kd, ne = kish(d.w)
    s = SUI.get((a, e), np.nan) if e in ESTRATOS else (SUI.loc[a].sum() if e.startswith("Ciudad") else np.nan)
    filas.append(dict(anio=a, dominio=e, hogares_muestra=len(d), suma_factores=d.w.sum(), suscriptores_SUI_dic=s,
                      suma_sobre_SUI=d.w.sum() / s, fex_min=d.w.min(), fex_p25=d.w.quantile(.25),
                      fex_mediana=d.w.median(), fex_p75=d.w.quantile(.75), fex_max=d.w.max(),
                      cv_fex=d.w.std(ddof=0) / d.w.mean(), deff_kish=kd, n_efectivo_kish=ne,
                      hogares_resto=int((d.clase != "1").sum()), n_menor_10=marca(len(d))))
fex = pd.DataFrame(filas)
tabla(fex.round(3), "ecv_factores_expansion.csv", index=False)

fig, ax = plt.subplots(figsize=(11, 4.8))
pos = []
for i, e in enumerate(ESTRATOS):
    for k, (a, c) in enumerate([(2019, C19), (2024, C24)]):
        d = B[(B.anio == a) & (B.E == e) & (B.clase == "1")].w
        r = B[(B.anio == a) & (B.E == e) & (B.clase != "1")].w
        p = i + (k - .5) * .36
        if len(r):
            ax.scatter(np.full(len(r), p), r, marker="_", color=PAL[7], s=60, lw=1.2, zorder=3)
        bp = ax.boxplot(d, positions=[p], widths=.3, patch_artist=True, showfliers=True,
                        flierprops=dict(marker=".", ms=3, mec=c), medianprops=dict(color="#0b0b0b"),
                        whiskerprops=dict(color=c), capprops=dict(color=c))
        bp["boxes"][0].set(facecolor=c, alpha=.55, edgecolor=c)
ax.set_xticks(range(6), ESTRATOS)
ax.set_yscale("log")
ax.set_ylabel("factor de expansión (hogares por hogar encuestado)")
ax.scatter([], [], marker="s", color=C19, label="2019")
ax.scatter([], [], marker="s", color=C24, label="2024")
ax.scatter([], [], marker="_", color=PAL[7], s=60, label="hogar del resto del municipio (rural)")
ax.legend(loc="center left", fontsize=9)
ax.set_ylim(1, 3000)
f19, f24 = fex[(fex.anio == 2019) & (fex.dominio.str.startswith("Ciudad"))].iloc[0], \
    fex[(fex.anio == 2024) & (fex.dominio.str.startswith("Ciudad"))].iloc[0]
titulo(ax, "Factores de expansión por estrato",
       f"Efecto de diseño de Kish por los pesos: {fmt(f19.deff_kish, 2)} en 2019 y {fmt(f24.deff_kish, 2)} en 2024 "
       "(todos los hogares); cajas: cabecera")
guardar(fig, "ecv_factores_expansion.png", FUENTE)

# ------------------------------------------------------------------------ 3. datos faltantes
def faltantes(anio, crudo, d):
    univ_ac = d.ac == 1
    filas = [
        ("P8520S1A1", "Estrato de la tarifa de energía", vacio(crudo.P8520S1A1), None,
         crudo.P8520S1A1.isin(["0", "8", "9"]), "0 sin estrato, 8 planta propia, 9 no sabe"),
        ("P4567", "Material del techo", vacio(crudo.P4567), None, None, ""),
        ("P1070", "Tipo de vivienda", vacio(crudo.P1070), None, None, ""),
        ("P5000", "Cuartos del hogar", vacio(crudo.P5000), None, None, ""),
        ("P5010", "Cuartos para dormir", vacio(crudo.P5010), None, None, ""),
        ("CANT_PERSONAS_HOGAR", "Personas del hogar", vacio(crudo.CANT_PERSONAS_HOGAR), None, None, ""),
        ("PERCAPITA", "Ingreso per cápita (imputado por el DANE)", vacio(crudo.PERCAPITA), None,
         num(crudo.PERCAPITA).fillna(0) <= 0, "ingreso 0"),
        ("P5095", "Tenencia de la vivienda", vacio(crudo.P5095), None, None, ""),
        ("P5018", "Último pago de electricidad", vacio(crudo.P5018), None, num(crudo.P5018) == 0, "pago 0"),
        ("P5018S1", "Meses que cubre el pago", vacio(crudo.P5018S1), ~vacio(crudo.P5018), None, ""),
    ]
    if anio == 2019:
        filas += [
            ("P5523", "Tipo de A/C (vacío = no tiene)", vacio(crudo.P5523), None, None, "salto: vacío se lee como sin A/C"),
            ("P5524", "Horas diarias de A/C", vacio(crudo.P5524), univ_ac, num(crudo.P5524) > 24,
             "solo hogares con A/C; otros = más de 24 h (suma de equipos, se conserva)"),
            ("P5526", "Horas diarias de ventilador", vacio(crudo.P5526), None, num(crudo.P5526) > 24,
             "vacío o 0 = sin uso; otros = más de 24 h (se excluye)"),
            ("P5514", "Tamaño de la nevera (vacío = no tiene)", vacio(crudo.P5514), None, None, "salto"),
            ("P5515", "Antigüedad de la nevera", vacio(crudo.P5515), ~vacio(crudo.P5514), num(crudo.P5515) == 99,
             "99 no sabe"),
        ]
    else:
        filas += [
            ("P1077S11", "Tiene A/C", vacio(crudo.P1077S11), None, None, ""),
            ("P1077S12", "Tiene ventilador", vacio(crudo.P1077S12), None, None, ""),
            ("P1077S2", "Tiene nevera", vacio(crudo.P1077S2), None, None, ""),
            ("P791", "¿Pagan la electricidad?", vacio(crudo.P791), None, crudo.P791.eq("4"), "4 sin servicio"),
        ]
    out = []
    for cod, desc, vac, univ, otra, nota in filas:
        u = pd.Series(True, index=crudo.index) if univ is None else univ.fillna(False).astype(bool)
        n_u = int(u.sum())
        out.append(dict(anio=anio, codigo=cod, pregunta=desc, hogares_universo=n_u, vacios=int((vac & u).sum()),
                        pct_vacios=100 * (vac & u).sum() / n_u if n_u else np.nan,
                        otros_codigos=int((otra.fillna(False) & u).sum()) if otra is not None else 0, nota=nota))
    return out


crudo19 = crudo19.reset_index(drop=True)
crudo24 = crudo24.reset_index(drop=True)
falt = pd.DataFrame(faltantes(2019, crudo19, h19.reset_index(drop=True)) + faltantes(2024, crudo24, h24.reset_index(drop=True)))
tabla(falt.round(2), "ecv_faltantes.csv", index=False)

# ------------------------------------------------------------------------ 4. equipos por ola (tabla agregada)
S6 = serie[serie.grupo.isin(list("123456"))].copy()
S6["E"] = "E" + S6.grupo
eq = S6[["anio", "E", "n", "pct_ac", "ic95_ac_pp", "pct_vent", "pct_nevera"]].rename(columns={"n": "hogares_muestra"})
eq["n_menor_10"] = eq.hogares_muestra.map(marca)
eq["ola_usada"] = np.where(eq.anio == 2020, "no", "sí")
# verificación: tasas recalculadas desde los microdatos frente a la tabla agregada
ver = []
for (a, e), d in B.groupby(["anio", "E"]):
    r = S6[(S6.anio == a) & (S6.E == e)].iloc[0]
    ver.append(dict(anio=a, estrato=e, n_microdatos=len(d), n_tabla=int(r.n),
                    ac_microdatos=wpct(d.ac == 1, d.w), ac_tabla=r.pct_ac,
                    vent_microdatos=wpct(d.vent == 1, d.w), vent_tabla=r.pct_vent,
                    nevera_microdatos=wpct(d.nevera == 1, d.w), nevera_tabla=r.pct_nevera))
ver = pd.DataFrame(ver)
eq = eq.merge(ver[["anio", "estrato", "n_microdatos", "ac_microdatos"]].rename(columns={"estrato": "E"}),
              on=["anio", "E"], how="left")
tabla(eq.round(2), "ecv_equipos_por_ola.csv", index=False)
print("\nVerificación microdatos frente a la tabla agregada:\n", ver.round(1).to_string(index=False))

fig, axs = plt.subplots(1, 3, figsize=(14, 4.9))
for ax, (col, nom, lim) in zip(axs, [("pct_ac", "A/C", (0, 104)), ("pct_vent", "Ventilador", (80, 101)),
                                     ("pct_nevera", "Nevera", (80, 101))]):
    ax.axvspan(2019.5, 2020.5, color="#efeee9", lw=0, zorder=0)
    for e in ESTRATOS:
        d = S6[S6.E == e].sort_values("anio")
        u = d[d.anio != 2020]
        ax.plot(u.anio, u[col], color=EST[e], lw=1.8, marker="o", ms=5, label=e)
        x = d[d.anio == 2020]
        ax.scatter(x.anio, x[col], facecolor="white", edgecolor=EST[e], s=30, zorder=3)
        pq = d[d.n < 10]
        ax.scatter(pq.anio, pq[col], marker="x", color="#0b0b0b", s=40, zorder=4)
    ax.set_ylim(*lim)
    ax.set_xticks(range(2018, 2026), [str(x)[2:] for x in range(2018, 2026)])
    ax.set_xlabel("ola (20xx)")
    titulo(ax, nom, "% de hogares de cada estrato")
axs[2].text(2020, 80.5, "2020\nno se usa", ha="center", fontsize=8.5, color=TXT2)
axs[2].scatter([], [], marker="x", color="#0b0b0b", label="menos de 10 hogares")
axs[2].scatter([], [], facecolor="white", edgecolor=GRIS, label="ola 2020")
han, lab = axs[0].get_legend_handles_labels()
h2, l2 = axs[2].get_legend_handles_labels()
axs[1].legend(han + h2[-2:], lab + l2[-2:], ncol=3, loc="lower center", fontsize=9, frameon=True,
              facecolor="#fcfcfb", edgecolor="none")
guardar(fig, "ecv_equipos_por_ola.png", "Fuente: tabla ECV_2018_2025_Barranquilla_tenencia_por_estrato.csv "
        "(tasas ponderadas con los factores de la ECV, sin suavizar).")

# ------------------------------------------------------------------------ 5. vivienda: techo y tipo
TECHO = {1: "Concreto", 3: "Asbesto-cemento", 4: "Zinc"}
TIPO = {1: "Casa", 2: "Apartamento"}
B["techo_c"] = B.techo.map(TECHO).fillna("Otro")
B["tipo_c"] = B.tipo_viv.map(TIPO).fillna("Cuarto u otro")
B["ten_c"] = B.tenencia.map({1: "Propia", 2: "Propia", 3: "Arriendo"}).fillna("Otra")
filas = []
for (a, e), d in pd.concat([B, B.assign(E="E1–E6")]).groupby(["anio", "E"]):
    r = dict(anio=a, estrato=e, hogares_muestra=len(d), n_menor_10=marca(len(d)))
    for c in ["Concreto", "Asbesto-cemento", "Zinc", "Otro"]:
        r[f"techo_{c}"] = wpct(d.techo_c == c, d.w)
    for c in ["Casa", "Apartamento", "Cuarto u otro"]:
        r[f"tipo_{c}"] = wpct(d.tipo_c == c, d.w)
    for c in ["Propia", "Arriendo", "Otra"]:
        r[f"tenencia_{c}"] = wpct(d.ten_c == c, d.w)
    filas.append(r)
viv = pd.DataFrame(filas)
tabla(viv.round(1), "ecv_vivienda_estrato.csv", index=False)

fig, axs = plt.subplots(2, 2, figsize=(13, 6.6), sharey=True)
cats = [("techo", ["Concreto", "Asbesto-cemento", "Zinc", "Otro"], [PAL[6], PAL[3], PAL[1], "#d6d5d0"]),
        ("tipo", ["Casa", "Apartamento", "Cuarto u otro"], [PAL[0], PAL[2], "#d6d5d0"])]
for j, (pref, cs, cols) in enumerate(cats):
    for i, a in enumerate([2019, 2024]):
        ax = axs[i, j]
        d = viv[(viv.anio == a) & (viv.estrato.isin(ESTRATOS))].set_index("estrato").reindex(ESTRATOS[::-1])
        left = np.zeros(6)
        for c, col in zip(cs, cols):
            v = d[f"{pref}_{c}"].values
            ax.barh(d.index, v, left=left, color=col, label=c, edgecolor="white", lw=.6)
            for k, (l0, vv) in enumerate(zip(left, v)):
                if vv >= 9:
                    ax.text(l0 + vv / 2, k, fmt(vv, 0), ha="center", va="center", fontsize=8.5,
                            color="white" if col != "#d6d5d0" else "#0b0b0b")
            left += v
        ax.set_xlim(0, 100)
        ax.grid(axis="y", visible=False)
        titulo(ax, f"{'Material del techo' if pref == 'techo' else 'Tipo de vivienda'}, {a}",
               "% de hogares de cada estrato")
        if i == 1:
            ax.legend(ncol=4, fontsize=9, loc="upper center", bbox_to_anchor=(.5, -.12))
guardar(fig, "ecv_vivienda_estrato.png", FUENTE + " Hogares de estratos 1 a 6.")

# ------------------------------------------------------------------------ 6. hogar e ingreso
B["dorm_ok"] = B.dormitorios.where(B.dormitorios > 0)
B["pers_dorm"] = B.personas / B.dorm_ok
filas = []
for (a, e), d in pd.concat([B, B.assign(E="E1–E6")]).groupby(["anio", "E"]):
    pos_ing = d[d.percapita > 0]
    filas.append(dict(anio=a, estrato=e, hogares_muestra=len(d), n_menor_10=marca(len(d)),
                      personas_media=wmean(d.personas, d.w), cuartos_media=wmean(d.cuartos, d.w),
                      dormitorios_media=wmean(d.dormitorios, d.w), personas_por_dormitorio=wmean(d.pers_dorm, d.w),
                      hacinamiento_pct=wpct(d.pers_dorm > 3, d.w), hogares_5mas_pct=wpct(d.personas >= 5, d.w),
                      ingreso_pc_mediana=wq(pos_ing.percapita, pos_ing.w, .5),
                      hogares_ingreso_0=int((d.percapita.fillna(0) <= 0).sum())))
hog = pd.DataFrame(filas)
tabla(hog.round(2), "ecv_hogar_estrato.csv", index=False)

filas = []
for a, d in B.groupby("anio"):
    d = d[d.percapita > 0].copy()
    cortes = [wq(d.percapita, d.w, q) for q in (.2, .4, .6, .8)]
    d["Q"] = np.digitize(d.percapita, cortes, right=True) + 1
    B.loc[d.index, "Q"] = d.Q
    for q, g in d.groupby("Q"):
        r = dict(anio=a, quintil=f"Q{int(q)}", hogares_muestra=len(g), n_menor_10=marca(len(g)),
                 corte_superior=cortes[int(q) - 1] if q < 5 else np.nan,
                 ingreso_pc_mediana=wq(g.percapita, g.w, .5), ac_pct=wpct(g.ac == 1, g.w))
        for e in ESTRATOS:
            r[f"{e}_pct_del_quintil"] = wpct(g.E == e, g.w)
        filas.append(r)
quin = pd.DataFrame(filas)
tabla(quin.round(1), "ecv_ingreso_quintiles.csv", index=False)

fig, axs = plt.subplots(1, 3, figsize=(14, 4.6))
x = np.arange(6)
for ax, col, nom in [(axs[0], "personas_media", "Personas por hogar"), (axs[1], "cuartos_media", "Cuartos por hogar")]:
    for k, (a, c) in enumerate([(2019, C19), (2024, C24)]):
        d = hog[(hog.anio == a)].set_index("estrato").reindex(ESTRATOS)
        ax.bar(x + (k - .5) * .38, d[col], width=.38, color=c, label=str(a))
    ax.set_xticks(x, ESTRATOS)
    titulo(ax, nom, "Media ponderada por estrato")
axs[0].legend(loc="upper right")
for a, c in [(2019, C19), (2024, C24)]:
    d = quin[quin.anio == a]
    axs[2].plot(d.quintil, d.ac_pct, marker="o", color=c, lw=2, label=str(a))
axs[2].set_ylim(0, 100)
titulo(axs[2], "A/C por quintil de ingreso", "% de hogares; quintiles del ingreso per cápita")
axs[2].legend(loc="upper left")
guardar(fig, "ecv_hogar_ingreso.png", FUENTE + " Estratos 1 a 6; quintiles sin hogares de ingreso 0.")

# ------------------------------------------------------------------------ 7. pago de la electricidad
TOPE = {2019: 3e6, 2024: 5e6}
B["pago_mes"] = B.pago / B.meses_pago.where(B.meses_pago > 0)
B["pago_valido"] = B.apply(lambda r: 1000 <= r.pago_mes <= TOPE[r.anio] if pd.notna(r.pago_mes) else False, axis=1)
filas = []
for (a, e), d in pd.concat([B, B.assign(E="E1–E6")]).groupby(["anio", "E"]):
    for grupo, g in [("Todos", d), ("Con A/C", d[d.ac == 1]), ("Sin A/C", d[d.ac == 0])]:
        v = g[g.pago_valido]
        filas.append(dict(anio=a, estrato=e, grupo=grupo, hogares_muestra=len(g), hogares_pago_valido=len(v),
                          n_menor_10=marca(len(v)), no_pagan_pct=wpct(g.no_paga == 1, g.w) if len(g) else np.nan,
                          pago_p25=wq(v.pago_mes, v.w, .25), pago_mediana=wq(v.pago_mes, v.w, .5),
                          pago_p75=wq(v.pago_mes, v.w, .75)))
pago = pd.DataFrame(filas)
pago["definicion_no_paga"] = np.where(pago.anio == 2019, "P5018 = 0 (pagó 0 pesos)", "P791 = 3 (no paga, tiene servicio)")
tabla(pago.round(1), "ecv_pago_electricidad.csv", index=False)

fig, axs = plt.subplots(1, 2, figsize=(13, 4.9), sharey=True)
for ax, a in zip(axs, [2019, 2024]):
    for k, (gr, c) in enumerate([("Sin A/C", GRIS), ("Con A/C", PAL[0])]):
        d = pago[(pago.anio == a) & (pago.grupo == gr) & pago.estrato.isin(ESTRATOS)].set_index("estrato").reindex(ESTRATOS)
        xx = x + (k - .5) * .3
        pq = d.hogares_pago_valido.values < 10
        ax.vlines(xx, d.pago_p25 / 1e3, d.pago_p75 / 1e3, color=c, lw=2.5, alpha=.6)
        ax.scatter(xx[~pq], d.pago_mediana.values[~pq] / 1e3, color=c, s=42, zorder=3, label=gr)
        ax.scatter(xx[pq], d.pago_mediana.values[pq] / 1e3, facecolor="white", edgecolor=c, s=42, zorder=3,
                   label=f"{gr}, menos de 10 hogares" if pq.any() else None)
    ax.set_xticks(x, ESTRATOS)
    ax.set_yscale("log")
    ax.set_yticks([20, 50, 100, 200, 500, 1000], ["20", "50", "100", "200", "500", "1.000"])
    titulo(ax, f"Pago mensual de electricidad, {a}", "Miles de pesos corrientes: mediana (punto) y P25–P75")
    ax.legend(fontsize=8.5, loc="upper left")
axs[0].set_ylabel("miles de COP por mes")
guardar(fig, "ecv_pago_electricidad.png", FUENTE + " Último pago ÷ meses que cubre; válidos de 1.000 COP "
        "al tope (3 millones en 2019, 5 millones en 2024).")

# ------------------------------------------------------------------------ 8. horas de uso, ECV 2019
U = B[B.anio == 2019].copy()
U["horas_vent"] = U.horas_vent.where(U.horas_vent <= 24)      # más de 24 h al día = error de captura (ecv19_extra.py)
U["ha_c"] = pd.cut(U.horas_ac, [-0.1, 4, 8, 12, 24.1], labels=["≤4 h", "5–8 h", "9–12 h", "más de 12 h"])
filas = []
for e, d in pd.concat([U, U.assign(E="E1–E6")]).groupby("E"):
    a = d[(d.ac == 1) & d.horas_ac.notna()]
    sv, cv = d[(d.ac == 0) & (d.horas_vent > 0)], d[(d.ac == 1) & (d.horas_vent > 0)]
    r = dict(estrato=e, hogares_con_AC=len(a), n_menor_10=marca(len(a)),
             horas_AC_p25=wq(a.horas_ac, a.w, .25), horas_AC_mediana=wq(a.horas_ac, a.w, .5),
             horas_AC_p75=wq(a.horas_ac, a.w, .75), horas_AC_media=wmean(a.horas_ac, a.w),
             horas_AC_max=a.horas_ac.max())
    for c in ["≤4 h", "5–8 h", "9–12 h", "más de 12 h"]:
        r[f"AC_{c}_pct"] = wpct(a.ha_c == c, a.w)
    r.update(minisplit_pct=wpct(a.tipo_ac == 1, a.w), pared_ventana_pct=wpct(a.tipo_ac == 2, a.w),
             central_pct=wpct(a.tipo_ac == 3, a.w),
             hogares_vent_sin_AC=len(sv), horas_vent_sin_AC_mediana=wq(sv.horas_vent, sv.w, .5),
             horas_vent_sin_AC_media=wmean(sv.horas_vent, sv.w),
             hogares_vent_con_AC=len(cv), horas_vent_con_AC_mediana=wq(cv.horas_vent, cv.w, .5),
             horas_vent_con_AC_media=wmean(cv.horas_vent, cv.w), horas_vent_max=d.horas_vent.max())
    filas.append(r)
horas = pd.DataFrame(filas)
tabla(horas.round(1), "ecv_horas_uso_2019.csv", index=False)

fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 4.9), gridspec_kw=dict(width_ratios=[1, 1]))
d = horas.set_index("estrato").reindex(ESTRATOS + ["E1–E6"])
left = np.zeros(len(d))
cols = ["#cfe0f5", "#7fb0e8", PAL[0], "#163f73"]
for c, col in zip(["≤4 h", "5–8 h", "9–12 h", "más de 12 h"], cols):
    v = d[f"AC_{c}_pct"].values
    a1.barh(d.index[::-1], v[::-1], left=left[::-1], color=col, label=c, edgecolor="white", lw=.6)
    left += v
for k, (e, n) in enumerate(zip(d.index[::-1], d.hogares_con_AC.values[::-1])):
    a1.text(101, k, f"n = {int(n)}", va="center", fontsize=8.5, color=TXT2)
a1.set_xlim(0, 112)
a1.grid(axis="y", visible=False)
a1.legend(ncol=4, fontsize=8.5, loc="upper center", bbox_to_anchor=(.45, -.08))
titulo(a1, "Horas diarias de A/C (suma de equipos)", "% de los hogares con A/C de cada estrato")
for k, (gr, c, col) in enumerate([("sin A/C", GRIS, "sin_AC"), ("con A/C", PAL[0], "con_AC")]):
    sub = U[(U.ac == (1 if gr == "con A/C" else 0)) & (U.horas_vent > 0)]
    for i, e in enumerate(ESTRATOS):
        g = sub[sub.E == e]
        if len(g) == 0:
            continue
        xx = i + (k - .5) * .3
        p25, p50, p75 = (wq(g.horas_vent, g.w, q) for q in (.25, .5, .75))
        a2.vlines(xx, p25, p75, color=c, lw=2.5, alpha=.6)
        a2.scatter([xx], [p50], color=c if len(g) >= 10 else "white", edgecolor=c, s=42, zorder=3,
                   label=gr if i == 0 else None)
a2.set_xticks(range(6), ESTRATOS)
a2.set_ylim(0, 25)
a2.set_ylabel("horas al día")
a2.legend(loc="upper right", fontsize=9)
titulo(a2, "Horas diarias de ventilador", "Mediana y P25–P75; punto hueco: menos de 10 hogares")
guardar(fig, "ecv_horas_uso_2019.png", "Fuente: DANE, ECV 2019, módulo de uso de energéticos (P5524, P5526, P5523); "
        "cálculos propios con factores de expansión.")

# ------------------------------------------------------------------------ 9. efecto de diseño, ECV 2024
D = B[B.anio == 2024].copy().reset_index(drop=True)
VARS = [("ac", "Tiene A/C", D.ac), ("vent", "Tiene ventilador", D.vent), ("nevera", "Tiene nevera", D.nevera),
        ("concreto", "Techo de concreto", (D.techo == 1).astype(float)),
        ("asbesto", "Techo de asbesto-cemento", (D.techo == 3).astype(float)),
        ("apto", "Vive en apartamento", (D.tipo_viv == 2).astype(float)),
        ("arriendo", "Vivienda en arriendo", (D.tenencia == 3).astype(float)),
        ("pers5", "Hogar de 5 personas o más", (D.personas >= 5).astype(float)),
        ("no_paga", "No paga la electricidad", D.no_paga)]
C_seg = D.segmento.nunique()
filas = []
for dom_nom, dom in [("E1–E6", pd.Series(1.0, index=D.index))] + \
        [(e, (D.E == e).astype(float)) for e in ESTRATOS]:
    n = int(dom.sum())
    kd, _ = kish(D.w[dom > 0])
    segs = D.segmento[dom > 0].nunique()
    for cod, nom, y in VARS:
        p, v = var_conglomerados(D, y, dom)
        vs = p * (1 - p) / n
        filas.append(dict(dominio=dom_nom, variable=nom, hogares_muestra=n, segmentos=segs, p_pct=100 * p,
                          ee_mas_pp=100 * np.sqrt(vs), ee_conglomerados_pp=100 * np.sqrt(v),
                          deff=v / vs if vs > 0 else np.nan, deff_kish_pesos=kd,
                          ic95_conglomerados_pp=196 * np.sqrt(v), n_menor_10=marca(n)))
# A/C de la ciudad postestratificada con el SUI (debe coincidir con 05_ajustes_v3)
W = SUI.loc[2024] / SUI.loc[2024].sum()
Z, P, vs = pd.Series(0.0, index=D.index), 0.0, 0.0
for e in ESTRATOS:
    dom = (D.E == e).astype(float)
    p, _ = var_conglomerados(D, D.ac, dom)
    wd = D.w * dom
    Z += W[e] * wd * (D.ac - p) / wd.sum()
    P += W[e] * p
    vs += W[e] ** 2 * p * (1 - p) / dom.sum()
tc = Z.groupby(D.segmento).sum()
vc = C_seg / (C_seg - 1) * ((tc - tc.mean()) ** 2).sum()
filas.append(dict(dominio="Ciudad postestratificada (SUI)", variable="Tiene A/C", hogares_muestra=len(D),
                  segmentos=C_seg, p_pct=100 * P, ee_mas_pp=100 * np.sqrt(vs), ee_conglomerados_pp=100 * np.sqrt(vc),
                  deff=vc / vs, deff_kish_pesos=np.nan, ic95_conglomerados_pp=196 * np.sqrt(vc), n_menor_10=""))
deff = pd.DataFrame(filas)
deff["hogares_por_segmento"] = deff.hogares_muestra / deff.segmentos
tabla(deff.round(3), "ecv_efecto_diseno.csv", index=False)
print("\nEfecto de diseño 2024:\n", deff[deff.dominio.isin(["E1–E6", "E1", "Ciudad postestratificada (SUI)"])]
      [["dominio", "variable", "p_pct", "deff", "deff_kish_pesos"]].round(2).to_string(index=False))

fig, ax = plt.subplots(figsize=(11, 5.2))
orden = [v[1] for v in VARS][::-1]
for dom_nom, c, mk in [("E1–E6", "#0b0b0b", "D"), ("E1", EST["E1"], "o"), ("E2", EST["E2"], "o"), ("E3", EST["E3"], "o")]:
    d = deff[deff.dominio == dom_nom].set_index("variable").reindex(orden)
    yy = np.arange(len(orden)) + {"E1–E6": .24, "E1": .08, "E2": -.08, "E3": -.24}[dom_nom]
    ax.scatter(d.deff, yy, color=c, marker=mk, s=40 if mk == "D" else 30, zorder=3,
               label="E1–E6 (tasa directa)" if dom_nom == "E1–E6" else dom_nom)
ax.axvline(1, color=GRIS, lw=1)
ax.axvline(1.5, color=PAL[7], lw=1, ls="--")
ax.text(1.52, len(orden) - .45, "1,5: valor que se aplica\na las demás olas", color=PAL[7], fontsize=8.5, va="top")
ax.set_yticks(range(len(orden)), orden)
ax.set_xlabel("efecto de diseño (varianza con conglomerados / varianza de muestreo simple)")
ax.grid(axis="y", visible=False)
ax.legend(loc="lower right", fontsize=9)
titulo(ax, "Efecto de diseño de la ECV 2024 en Barranquilla",
       f"{C_seg} segmentos con hogares de estratos 1 a 6; linealización de Taylor; E4 a E6 en la tabla")
guardar(fig, "ecv_efecto_diseno.png", "Fuente: DANE, ECV 2024, microdatos y variables de diseño muestral (SEGMENTO); "
        "cálculos propios.")

# ------------------------------------------------------------------------ resumen en consola
print("\nFactores de expansión:\n", fex[["anio", "dominio", "hogares_muestra", "suma_factores", "suma_sobre_SUI",
                                         "cv_fex", "deff_kish", "n_efectivo_kish"]].round(2).to_string(index=False))
print("\nFaltantes:\n", falt.round(1).to_string(index=False))
print("\nVivienda:\n", viv.round(1).to_string(index=False))
print("\nHogar:\n", hog.round(2).to_string(index=False))
print("\nQuintiles:\n", quin.round(1).to_string(index=False))
print("\nPago:\n", pago[pago.grupo != "x"].round(0).to_string(index=False))
print("\nHoras 2019:\n", horas.round(1).T.to_string())
print("\nListo: figuras en", FIG, "y tablas en", TAB)
