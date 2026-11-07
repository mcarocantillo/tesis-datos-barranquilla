"""EDA de la ENUT 2024–2025 (DANE) para el dominio que usa la tesis: cabeceras del Atlántico.

Lee los microdatos directo del zip del DANE, reconstruye las variables de `scripts/enut.py` y
`scripts/enut_stats.py` y escribe solo agregados (figuras en figuras/eda/enut_*.png y tablas en
tablas/eda/enut_*.csv). Ninguna salida es por persona u hogar. Las celdas con menos de 10 personas
(u hogares) de muestra quedan marcadas en la columna «n_menor_10».

Uso (desde la raíz del repositorio):
    python scripts/eda/enut.py
"""
import sys
import zipfile
import datetime as dt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from estilo import *  # noqa: E402,F401,F403

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

np.random.seed(SEMILLA)
ZIP = DESCARGAS / "DANE" / "ENUT" / "BDATOS-ENUT-2024_2025.zip"
FUENTE = "Fuente: DANE, ENUT 2024–2025 (microdatos), cabeceras del Atlántico. Cálculos propios, ponderados con FEX_C."
K = ["DIRECTORIO", "SECUENCIA_P", "ORDEN"]
H = ["DIRECTORIO", "SECUENCIA_P"]
GRUPOS = ["E1–2", "E3–4", "E5–6"]
COL_G = {"E1–2": PAL[0], "E3–4": PAL[1], "E5–6": PAL[2]}
TIPOS = ["Ocupado", "Oficios del hogar", "Estudiante", "Mayor 65+ no ocupado", "Busca trabajo", "Otro / incapacitado"]
DIAS = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
# Festivos nacionales de Colombia (Ley 51 de 1983) dentro del periodo de referencia, de lunes a viernes.
FESTIVOS = ["2024-10-14", "2024-11-04", "2024-11-11", "2024-12-25", "2025-01-01", "2025-01-06", "2025-03-24",
            "2025-04-17", "2025-04-18", "2025-05-01", "2025-06-02", "2025-06-23", "2025-06-30", "2025-08-07",
            "2025-08-18"]

Z = zipfile.ZipFile(ZIP)


def rd(nombre, cols=None):
    """Lee un módulo CSV del zip (separador «;», UTF-8 con BOM) como texto, con nombres en mayúscula."""
    with Z.open(nombre) as fh:
        d = pd.read_csv(fh, sep=";", encoding="utf-8-sig", dtype=str, low_memory=False,
                        usecols=(lambda c: c.upper() in cols) if cols else None)
    d.columns = [c.upper() for c in d.columns]
    return d


def num(s):
    return pd.to_numeric(s.astype(str).str.strip().str.replace(",", "."), errors="coerce")


def txt(s):
    return s.fillna("").astype(str).str.strip()


def wmean(x, w):
    m = x.notna()
    return float((x[m] * w[m]).sum() / w[m].sum()) if w[m].sum() > 0 else np.nan


def wq(x, w, q):
    """Cuantil ponderado: primer valor cuyo peso acumulado alcanza q (como en 04_metodologia.md)."""
    m = x.notna()
    x, w = x[m].to_numpy(), w[m].to_numpy()
    o = np.argsort(x, kind="mergesort")
    c = np.cumsum(w[o]) / w.sum()
    return float(x[o][np.searchsorted(c, q)])


def pct(mask, w):
    return float(w[mask].sum() / w.sum() * 100)


def marca(df, col="n"):
    df["n_menor_10"] = np.where(df[col] < 10, "sí", "")
    return df


# ---------------------------------------------------------------- 1. Vivienda (C1) y dominio
c1 = rd("ENUT_C1.csv")
n_viv_pais = len(c1)
atl = c1[num(c1.DPTO) == 8].copy()
n_viv_atl = len(atl)
n_viv_resto = int((txt(atl.CLASE) == "2").sum())
c1 = atl[txt(atl.CLASE) == "1"].copy()
c1["ESTRATO"] = num(c1.P4030S1A1)
c1["FECHA"] = pd.to_datetime("1970-01-01") + pd.to_timedelta(num(c1.DIA_REF), unit="D")
c1["DOW"] = c1.FECHA.dt.dayofweek
c1["FINDE"] = c1.DOW >= 5
c1["MES"] = c1.FECHA.dt.month
c1["FESTIVO"] = c1.FECHA.dt.strftime("%Y-%m-%d").isin(FESTIVOS) & ~c1.FINDE
c1["GRUPO"] = c1.ESTRATO.map({1: "E1–2", 2: "E1–2", 3: "E3–4", 4: "E3–4", 5: "E5–6", 6: "E5–6"})
c1 = c1[["DIRECTORIO", "P424", "ESTRATO", "GRUPO", "FECHA", "DOW", "FINDE", "MES", "FESTIVO"]]

# ---------------------------------------------------------------- 2. Hogar (C2) y personas (C3)
c2 = rd("ENUT_C2.csv", H + ["P1176S1", "P1176S2", "P1176S3", "P6008", "FEX_C"]).merge(c1, on="DIRECTORIO")
c2["WH"] = num(c2.FEX_C)
c3 = rd("ENUT_C3.csv", K + ["P6040", "P6020", "FEX_C"])
p = c3.merge(c1, on="DIRECTORIO")
p["W"] = num(p.FEX_C)
p["EDAD"] = num(p.P6040)

# ---------------------------------------------------------------- 3. Educación (C6), trabajo (C7, C7_1), uso del tiempo (C8)
c6 = rd("ENUT_C6.csv", K + ["P6170", "P1101", "P1160", "P1160S1A1", "P1160S1A2", "P1159S1", "P1159S2"])
c7 = rd("ENUT_C7.csv", K + ["P1152"])
c71 = rd("ENUT_C7_1.csv", K + ["P6880", "P1151", "P1150", "P1150S1", "P1150S2", "P1099S1", "P1099S2",
                               "P6535S1A1", "P6535S1A2", "P6534S1", "P6534S2", "P6530S1A1", "P6530S1A2"])
ACT = {"DORMIR": ["P1144S1"], "COMER": ["P1144S2"], "ASEO": ["P1144S3"], "DESCANSAR": ["P1144S6"],
       "COCINAR": ["P1143S1"], "TV": ["P1110S1", "P1110S2"], "INTERNET": ["P1110S5", "P1110S6"]}
c8 = rd("ENUT_C8.csv", K + ["P1144S1"] + [v + s for vs in ACT.values() for v in vs for s in ("A1", "A2")])
c8["EN_C8"] = True
p = p.merge(c6, on=K, how="left").merge(c7, on=K, how="left").merge(c71, on=K, how="left").merge(c8, on=K, how="left")
p["EN_C8"] = p.EN_C8.fillna(False).astype(bool)


def hm(h, m):
    return num(p[h]).fillna(0) * 60 + num(p[m]).fillna(0)


for a, vs in ACT.items():
    p["MIN_" + a] = sum(hm(v + "A1", v + "A2") for v in vs)
p["MIN_TRABAJO"] = hm("P1150S1", "P1150S2") + hm("P6535S1A1", "P6535S1A2") + hm("P6530S1A1", "P6530S1A2")
p["MIN_VIAJE_TRAB"] = 2 * (hm("P1099S1", "P1099S2") + hm("P6534S1", "P6534S2"))
p["MIN_VIAJE_EST"] = 2 * hm("P1159S1", "P1159S2")
p["MIN_CLASE"] = np.where(txt(p.P1160) == "1", hm("P1160S1A1", "P1160S1A2"), 0)
p["TRABAJA_EN_CASA"] = txt(p.P6880) == "2"
p["MIN_FUERA_TRAB"] = np.where(p.TRABAJA_EN_CASA, 0, p.MIN_TRABAJO) + p.MIN_VIAJE_TRAB
p["MIN_FUERA"] = p.MIN_FUERA_TRAB + p.MIN_VIAJE_EST                    # definición publicada (sin clases)
p["MIN_FUERA_CLASE"] = p.MIN_FUERA + p.MIN_CLASE                       # sensibilidad: con horas de clase


def tipo(r):
    e, a = r.EDAD, str(r.P1152).strip()
    if e < 10:
        return "Niño <10"
    if e >= 65 and a != "1":
        return "Mayor 65+ no ocupado"
    return {"1": "Ocupado", "3": "Estudiante", "4": "Oficios del hogar", "2": "Busca trabajo"}.get(a, "Otro / incapacitado")


p["TIPO"] = p.apply(tipo, axis=1)
a = p[p.EDAD >= 10].copy()          # universo de las estadísticas de tiempo
a["DIA"] = np.where(a.FINDE, "fin de semana", "día hábil")

# ---------------------------------------------------------------- 4. Muestra
filas = []
for e, d in list(p.groupby("ESTRATO")) + [("Total", p)]:
    h = c2 if e == "Total" else c2[c2.ESTRATO == e]
    filas.append({"estrato": e if e == "Total" else (f"E{int(e)}" if e <= 6 else "sin dato (9)"),
                  "viviendas": d.DIRECTORIO.nunique(), "hogares": len(h), "personas": len(d),
                  "personas_10mas": int((d.EDAD >= 10).sum()), "hogares_expandidos": round(h.WH.sum()),
                  "personas_expandidas": round(d.W.sum()), "pct_personas_expandidas": round(d.W.sum() / p.W.sum() * 100, 1)})
t_muestra = marca(pd.DataFrame(filas), "personas_10mas")
tabla(t_muestra, "enut_muestra_estrato.csv", index=False, decimal=",")

dow = a.groupby(["DOW", "GRUPO"]).size().unstack(fill_value=0).reindex(columns=GRUPOS)
dow.index = [DIAS[i] for i in dow.index]
dow["total"] = dow.sum(axis=1)
dow["pct_expandido"] = (a.groupby("DOW").W.sum() / a.W.sum() * 100).round(1).to_numpy()
tabla(dow.rename_axis("dia"), "enut_muestra_dia.csv", decimal=",")
mes = a.assign(PER=a.FECHA.dt.strftime("%Y-%m")).groupby("PER").agg(personas_10mas=("W", "size"),
                                                                   hogares=("DIRECTORIO", "nunique"))
tabla(marca(mes.reset_index(), "personas_10mas"), "enut_muestra_mes.csv", index=False)

# ---------------------------------------------------------------- 5. Tipo de persona por grupo de estrato
filas = []
for g, d in list(a.groupby("GRUPO")) + [("Total", a)]:
    for t in TIPOS:
        m = d.TIPO == t
        filas.append({"grupo": g, "tipo": t, "n": int(m.sum()), "pct": round(pct(m, d.W), 1)})
t_tipo = marca(pd.DataFrame(filas))
tabla(t_tipo, "enut_tipo_estrato.csv", index=False, decimal=",")

# Actividad principal de la semana (P1152) de las personas de 15 años o más, para comparar con la GEIH (P6240)
ACT15 = {"1": "Trabajando", "2": "Buscando trabajo", "3": "Estudiando", "4": "Oficios del hogar",
         "5": "Incapacitado permanente", "6": "Otra actividad"}
b = a[a.EDAD >= 15]
filas = []
for g, d in list(b.groupby("GRUPO")) + [("Total", b)]:
    for c, lab in ACT15.items():
        m = txt(d.P1152) == c
        filas.append({"grupo": g, "actividad": lab, "n": int(m.sum()), "pct": round(pct(m, d.W), 1)})
tabla(marca(pd.DataFrame(filas)), "enut_actividad_15mas.csv", index=False, decimal=",")

# ---------------------------------------------------------------- 6. Presencia: hogares con alguien en casa todo el día
hog = a.groupby(H).agg(GRUPO=("GRUPO", "first"), FINDE=("FINDE", "first"), FESTIVO=("FESTIVO", "first"),
                       alguien=("MIN_FUERA", lambda s: (s == 0).any()),
                       alguien_clase=("MIN_FUERA_CLASE", lambda s: (s == 0).any())).reset_index()
hog = hog.merge(c2[H + ["WH"]], on=H)
filas = []
for (g, f), d in list(hog.groupby(["GRUPO", "FINDE"])) + [(("Total", f), d) for f, d in hog.groupby("FINDE")]:
    filas.append({"grupo": g, "dia": "fin de semana" if f else "día hábil", "n": len(d),
                  "pct_alguien_en_casa": round(pct(d.alguien, d.WH), 1),
                  "pct_alguien_en_casa_con_clases": round(pct(d.alguien_clase, d.WH), 1)})
hab = hog[~hog.FINDE & ~hog.FESTIVO]
for g, d in list(hab.groupby("GRUPO")) + [("Total", hab)]:
    filas.append({"grupo": g, "dia": "día hábil sin festivos", "n": len(d),
                  "pct_alguien_en_casa": round(pct(d.alguien, d.WH), 1),
                  "pct_alguien_en_casa_con_clases": round(pct(d.alguien_clase, d.WH), 1)})
t_pres = marca(pd.DataFrame(filas))
tabla(t_pres, "enut_presencia_estrato.csv", index=False, decimal=",")

# Tramos de horas fuera de la vivienda por trabajo o estudio
TRAMOS = ["0 h", "hasta 4 h", "4–8 h", "8–10 h", "más de 10 h"]


def tramo(m):
    return pd.cut(m / 60, [-1, 0, 4, 8, 10, 99], labels=TRAMOS)


a["TRAMO"] = tramo(a.MIN_FUERA)
filas = []
for (t, dd), d in a.groupby(["TIPO", "DIA"]):
    r = {"tipo": t, "dia": dd, "n": len(d), "h_fuera_media": round(wmean(d.MIN_FUERA / 60, d.W), 2),
         "h_fuera_media_con_clases": round(wmean(d.MIN_FUERA_CLASE / 60, d.W), 2)}
    for tr in TRAMOS:
        r["pct_" + tr] = round(pct(d.TRAMO == tr, d.W), 1)
    filas.append(r)
t_fuera = marca(pd.DataFrame(filas))
tabla(t_fuera, "enut_fuera_tramos.csv", index=False, decimal=",")

# ---------------------------------------------------------------- 7. Sueño
filas = []
for keys, d in list(a.groupby(["TIPO", "DIA"])) + list(a.groupby(["GRUPO", "DIA"])) + [(("Todos", dd), d) for dd, d in a.groupby("DIA")]:
    s = d.MIN_DORMIR / 60
    filas.append({"grupo_o_tipo": keys[0], "dia": keys[1], "n": len(d), "h_media": round(wmean(s, d.W), 2),
                  "p10": wq(s, d.W, .1), "p50": wq(s, d.W, .5), "p90": wq(s, d.W, .9)})
t_sueno = marca(pd.DataFrame(filas))
tabla(t_sueno, "enut_sueno.csv", index=False, decimal=",")

# ---------------------------------------------------------------- 8. Jornada de estudio (todas las edades que asisten)
JOR = {"1": "Mañana", "2": "Tarde", "3": "Noche", "4": "Completa o única", "5": "Fin de semana"}
st = p[txt(p.P6170) == "1"].copy()
st["JOR"] = txt(st.P1101).map(JOR)
filas = []
for g, d in list(st.groupby("GRUPO")) + [("Total", st)]:
    r = {"grupo": g, "n": len(d)}
    for j in JOR.values():
        r["pct_" + j] = round(pct(d.JOR == j, d.W), 1)
    r["pct_sin_dato"] = round(pct(d.JOR.isna(), d.W), 1)
    hab_ = d[~d.FINDE]
    r["n_dia_habil"] = len(hab_)
    r["pct_asistio_clase_dia_habil"] = round(pct(txt(hab_.P1160) == "1", hab_.W), 1)
    cl = hab_[txt(hab_.P1160) == "1"]
    r["h_clase_media_si_asistio"] = round(wmean(cl.MIN_CLASE / 60, cl.W), 2) if len(cl) else np.nan
    filas.append(r)
t_jor = marca(pd.DataFrame(filas))
tabla(t_jor, "enut_jornada_estudio.csv", index=False, decimal=",")

# ---------------------------------------------------------------- 9. Faltantes y valores raros
oc = a[a.TIPO == "Ocupado"]
falt = [
    ("Estrato (P4030S1A1) sin dato o 9", "viviendas", c1.DIRECTORIO.nunique(), int((~c1.ESTRATO.between(1, 6)).sum())),
    ("Actividad principal (P1152) vacía", "personas de 10+", len(a), int((txt(a.P1152) == "").sum())),
    ("Sin registro en el módulo C8", "personas de 10+", len(a), int((~a.EN_C8).sum())),
    ("Dormir (P1144S1) no reportado", "personas de 10+ en C8", int(a.EN_C8.sum()), int((a.EN_C8 & (txt(a.P1144S1) != "1")).sum())),
    ("Sueño menor de 4 h (reportado)", "personas de 10+ en C8", int(a.EN_C8.sum()), int(((a.MIN_DORMIR > 0) & (a.MIN_DORMIR < 240)).sum())),
    ("Sueño mayor de 14 h", "personas de 10+ en C8", int(a.EN_C8.sum()), int((a.MIN_DORMIR > 840).sum())),
    ("Lugar de trabajo (P6880) vacío", "ocupados de 10+", len(oc), int((txt(oc.P6880) == "").sum())),
    ("Horas normales de trabajo (P1151) vacías", "ocupados de 10+", len(oc), int((txt(oc.P1151) == "").sum())),
    ("Jornada de estudio (P1101) vacía", "personas que estudian", len(st), int(st.JOR.isna().sum())),
    ("Día hábil que es festivo nacional", "personas de 10+ en día hábil", int((~a.FINDE).sum()), int(a.FESTIVO.sum())),
]
t_falt = pd.DataFrame(falt, columns=["variable", "universo", "n_universo", "n_faltante"])
t_falt["pct"] = (t_falt.n_faltante / t_falt.n_universo * 100).round(1)
tabla(t_falt, "enut_faltantes.csv", index=False, decimal=",")

# Ocupados que trabajan en su vivienda (P6880 = 2) y comprobación del código con el viaje al trabajo
oc_ = a[a.TIPO == "Ocupado"]
filas = []
for g, d in list(oc_.groupby("GRUPO")) + [("Total", oc_)]:
    c, f_ = d[d.TRABAJA_EN_CASA], d[~d.TRABAJA_EN_CASA]
    filas.append({"grupo": g, "n_ocupados": len(d), "n_en_casa": len(c), "pct_en_casa": round(pct(d.TRABAJA_EN_CASA, d.W), 1),
                  "pct_sin_viaje_si_en_casa": round(pct(c.MIN_VIAJE_TRAB == 0, c.W), 1) if len(c) else np.nan,
                  "pct_sin_viaje_si_fuera": round(pct(f_.MIN_VIAJE_TRAB == 0, f_.W), 1)})
tabla(marca(pd.DataFrame(filas), "n_en_casa"), "enut_trabajo_casa.csv", index=False, decimal=",")

# Bienes del hogar (para el cruce con la ECV)
bienes = {n: round(pct(txt(c2[v]) == "1", c2.WH), 1) for v, n in [("P1176S1", "lavadora"), ("P1176S2", "secadora"), ("P1176S3", "nevera")]}

# ---------------------------------------------------------------- 10. Figuras
# F1: muestra por estrato, día de la semana y mes
fig, ax = plt.subplots(1, 3, figsize=(13, 4.2), gridspec_kw={"width_ratios": [1, 1, 1.6]})
m6 = t_muestra[t_muestra.estrato.str.match(r"E\d")]
ax[0].bar(m6.estrato, m6.personas_10mas, color=[EST[e] for e in m6.estrato])
for x, v in zip(m6.estrato, m6.personas_10mas):
    ax[0].text(x, v, fmt(v, 0), ha="center", va="bottom", fontsize=9)
titulo(ax[0], "Por estrato", "personas de 10+ en la muestra")
ax[1].bar(dow.index, dow.total, color=[PAL[0]] * 5 + [PAL[1]] * 2)
titulo(ax[1], "Por día de referencia", "azul: día hábil; naranja: fin de semana")
ax[2].bar(range(len(mes)), mes.personas_10mas, color=PAL[6])
ax[2].set_xticks(range(len(mes)), [MESES[int(s[5:]) - 1] + "\n" + s[2:4] for s in mes.index], fontsize=8)
titulo(ax[2], "Por mes del día de referencia", "personas de 10+")
guardar(fig, "enut_muestra.png", FUENTE)

# F2: tipo de persona por grupo de estrato
fig, ax = plt.subplots(figsize=(11, 3.8))
pv = t_tipo.pivot(index="grupo", columns="tipo", values="pct").reindex(index=GRUPOS + ["Total"], columns=TIPOS)
pv = pv.iloc[::-1]
izq = np.zeros(len(pv))
for i, t in enumerate(TIPOS):
    ax.barh(pv.index, pv[t], left=izq, color=PAL[i], label=t)
    for y, (l, v) in enumerate(zip(izq, pv[t])):
        if v >= 6:
            ax.text(l + v / 2, y, fmt(v, 0), ha="center", va="center", color="white", fontsize=9)
    izq += pv[t].to_numpy()
ax.set_xlim(0, 100)
ax.set_xlabel("% de las personas de 10 años o más (ponderado)")
ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(.5, -.22), fontsize=9)
titulo(ax, "Tipo de persona por grupo de estrato")
guardar(fig, "enut_tipo_estrato.png", FUENTE)

# F3: distribución de las horas de sueño
fig, ax = plt.subplots(1, 2, figsize=(12, 4.2))
bins = np.arange(3, 14.5, .5)
for dd, c in [("día hábil", PAL[0]), ("fin de semana", PAL[1])]:
    d = a[(a.DIA == dd) & (a.MIN_DORMIR > 0)]
    hgt, _ = np.histogram(d.MIN_DORMIR / 60, bins=bins, weights=d.W)
    ax[0].step(bins[:-1], hgt / d.W.sum() * 100, where="post", color=c, lw=2, label=dd)
ax[0].set_xlabel("horas de sueño en el día de referencia")
ax[0].set_ylabel("% de personas (ponderado)")
ax[0].legend()
titulo(ax[0], "Distribución de las horas de sueño", "personas de 10+ que reportan dormir")
ss = t_sueno[t_sueno.grupo_o_tipo.isin(TIPOS)].pivot(index="grupo_o_tipo", columns="dia", values="h_media").reindex(TIPOS)
y = np.arange(len(TIPOS))
ax[1].barh(y - .2, ss["día hábil"], .4, color=PAL[0], label="día hábil")
ax[1].barh(y + .2, ss["fin de semana"], .4, color=PAL[1], label="fin de semana")
ax[1].set_yticks(y, TIPOS)
ax[1].invert_yaxis()
ax[1].set_xlim(6, 10)
ax[1].set_xlabel("horas de sueño, media ponderada")
ax[1].legend(loc="upper right", fontsize=9)
titulo(ax[1], "Sueño medio por tipo de persona")
guardar(fig, "enut_sueno.png", FUENTE)

# F4: tramos de horas fuera de la vivienda por trabajo o estudio, día hábil
fig, ax = plt.subplots(figsize=(11, 4.2))
fh = t_fuera[t_fuera.dia == "día hábil"].set_index("tipo").reindex(TIPOS[::-1])
izq = np.zeros(len(fh))
colt = ["#d9d8d3", PAL[3], PAL[1], PAL[7], "#7a1f1f"]
for i, tr in enumerate(TRAMOS):
    v = fh["pct_" + tr].to_numpy()
    ax.barh(fh.index, v, left=izq, color=colt[i], label=tr)
    for yy, (l, vv) in enumerate(zip(izq, v)):
        if vv >= 7:
            ax.text(l + vv / 2, yy, fmt(vv, 0), ha="center", va="center", fontsize=9,
                    color="black" if i == 0 else "white")
    izq += v
ax.set_xlim(0, 100)
ax.set_xlabel("% de las personas (ponderado)")
ax.legend(ncol=5, loc="upper center", bbox_to_anchor=(.5, -.18), fontsize=9)
titulo(ax, "Horas fuera de la vivienda por trabajo o estudio en un día hábil",
       "trabajo fuera de la vivienda + traslados al trabajo y al estudio (sin horas de clase)")
guardar(fig, "enut_fuera.png", FUENTE)

# F5: presencia en el hogar por grupo de estrato
fig, ax = plt.subplots(figsize=(11, 4.2))
pr = t_pres[t_pres.grupo.isin(GRUPOS)]
x = np.arange(len(GRUPOS))
for i, (dd, c) in enumerate([("día hábil", PAL[0]), ("fin de semana", PAL[1])]):
    d = pr[pr.dia == dd].set_index("grupo").reindex(GRUPOS)
    ax.bar(x + (i - .5) * .38, d.pct_alguien_en_casa, .36, color=c, label=f"{dd}, definición publicada")
    ax.scatter(x + (i - .5) * .38, d.pct_alguien_en_casa_con_clases, marker="_", s=600, color="black", lw=2.5,
               label="sumando las horas de clase" if i == 0 else None, zorder=3)
    for xx, v in zip(x + (i - .5) * .38, d.pct_alguien_en_casa):
        ax.text(xx, 2, fmt(v), ha="center", va="bottom", color="white", fontsize=9)
ax.set_xticks(x, GRUPOS)
ax.set_ylim(0, 100)
ax.set_ylabel("% de hogares (ponderado)")
ax.legend(loc="upper center", bbox_to_anchor=(.5, -.1), ncol=3, fontsize=9)
titulo(ax, "Hogares con al menos una persona de 10+ en casa todo el día")
guardar(fig, "enut_presencia.png", FUENTE)

# F6: jornada de estudio por grupo de estrato
fig, ax = plt.subplots(figsize=(11, 3.4))
jj = t_jor.set_index("grupo").reindex(GRUPOS + ["Total"]).iloc[::-1]
izq = np.zeros(len(jj))
for i, j in enumerate(JOR.values()):
    v = jj["pct_" + j].to_numpy()
    ax.barh(jj.index, v, left=izq, color=PAL[i], label=j)
    for yy, (l, vv) in enumerate(zip(izq, v)):
        if vv >= 6:
            ax.text(l + vv / 2, yy, fmt(vv, 0), ha="center", va="center", color="white", fontsize=9)
    izq += v
ax.set_xlim(0, 100)
ax.set_xlabel("% de las personas que estudian (ponderado)")
ax.legend(ncol=5, loc="upper center", bbox_to_anchor=(.5, -.25), fontsize=9)
titulo(ax, "Jornada de estudio por grupo de estrato")
guardar(fig, "enut_jornada.png", FUENTE)

# ---------------------------------------------------------------- 11. Resumen en consola
print("Viviendas: país", n_viv_pais, "| Atlántico", n_viv_atl, "| resto", n_viv_resto, "| cabecera", c1.DIRECTORIO.nunique())
print("Periodo del día de referencia:", c1.FECHA.min().date(), "a", c1.FECHA.max().date())
print(t_muestra.to_string(index=False))
print("Hogares", len(c2), "expandidos", round(c2.WH.sum()), "| personas", len(p), "expandidas", round(p.W.sum()),
      "| 10+", len(a), "| en C8", int(a.EN_C8.sum()))
print("Personas por hogar (P6008, ponderado):", round(wmean(num(c2.P6008), c2.WH), 2), "| bienes %", bienes)
print(dow.to_string())
print(t_tipo.pivot(index="tipo", columns="grupo", values="pct").to_string())
print(t_pres.to_string(index=False))
print(t_fuera[["tipo", "dia", "n", "h_fuera_media", "h_fuera_media_con_clases", "pct_0 h"]].to_string(index=False))
print(t_sueno.to_string(index=False))
print(t_jor.to_string(index=False))
print(t_falt.to_string(index=False))
o = a[a.TIPO == "Ocupado"]
print("Ocupados que trabajan en su vivienda (P6880 = 2), %:", round(pct(o.TRABAJA_EN_CASA, o.W), 1),
      "| por grupo", {g: round(pct(d.TRABAJA_EN_CASA, d.W), 1) for g, d in o.groupby("GRUPO")})
print("Ocupados: viaje de ida al trabajo = 0 según P6880 (2 vs resto), %:",
      round(((o.MIN_VIAJE_TRAB == 0) & o.TRABAJA_EN_CASA).sum() / max(o.TRABAJA_EN_CASA.sum(), 1) * 100, 1),
      round(((o.MIN_VIAJE_TRAB == 0) & ~o.TRABAJA_EN_CASA).sum() / max((~o.TRABAJA_EN_CASA).sum(), 1) * 100, 1))
for dd, d in o.groupby("DIA"):
    print("Ocupados", dd, "h fuera por trabajo:", round(wmean(d.MIN_FUERA_TRAB / 60, d.W), 2),
          "| trabajó el día de referencia %:", round(pct(txt(d.P1150) == "1", d.W), 1))
print("Horas normales a la semana de los ocupados (P1151):", round(wmean(num(o.P1151), o.W), 1))
