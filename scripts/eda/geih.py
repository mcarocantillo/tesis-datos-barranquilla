"""EDA de la GEIH 2024 (DANE) para el área metropolitana de Barranquilla (AREA = 08).

Lee los microdatos mensuales directo de los zips del DANE (en marzo y abril los CSV vienen en un zip
anidado), reconstruye las variables de `scripts/geih.py` y `scripts/geih2.py` y escribe solo agregados
(figuras en figuras/eda/geih_*.png y tablas en tablas/eda/geih_*.csv). Las celdas con menos de 10
personas u hogares de muestra quedan marcadas en la columna «n_menor_10».

Uso (desde la raíz del repositorio, después de scripts/eda/enut.py para la comparación con la ENUT):
    python scripts/eda/geih.py
"""
import sys
import io
import re
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from estilo import *  # noqa: E402,F401,F403

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

np.random.seed(SEMILLA)
DIR = DESCARGAS / "DANE" / "GEIH"
FUENTE = "Fuente: DANE, GEIH 2024 (microdatos mensuales disponibles), área metropolitana de Barranquilla. Cálculos propios."
H = ["MES", "DIRECTORIO", "SECUENCIA_P"]
K = H + ["ORDEN"]
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
GRUPOS = ["E1–2", "E3–4", "E5–6"]
LUGAR = {"1": "En esta vivienda", "2": "En otras viviendas", "3": "Kiosco o caseta", "4": "En un vehículo",
         "5": "De puerta en puerta", "6": "En la calle", "7": "Local fijo, oficina o fábrica",
         "8": "Campo, mar o río", "9": "Obra en construcción", "10": "Mina o cantera", "11": "Otro"}
LUGAR_G = {"En esta vivienda": "En esta vivienda", "En otras viviendas": "En otras viviendas",
           "Local fijo, oficina o fábrica": "Local fijo, oficina o fábrica", "En un vehículo": "En un vehículo",
           "Kiosco o caseta": "Calle, kiosco o puerta a puerta", "De puerta en puerta": "Calle, kiosco o puerta a puerta",
           "En la calle": "Calle, kiosco o puerta a puerta"}
ORDEN_LG = ["En esta vivienda", "En otras viviendas", "Local fijo, oficina o fábrica", "En un vehículo",
            "Calle, kiosco o puerta a puerta", "Obra, campo u otro"]
ACT = {"1": "Trabajando", "2": "Buscando trabajo", "3": "Estudiando", "4": "Oficios del hogar",
       "5": "Incapacitado permanente", "6": "Otra actividad"}


def num(s):
    return pd.to_numeric(s.astype(str).str.strip().str.replace(",", "."), errors="coerce")


def txt(s):
    return s.fillna("").astype(str).str.strip()


def pct(mask, w):
    return float(w[mask].sum() / w.sum() * 100) if w.sum() > 0 else np.nan


def marca(df, col="n"):
    df["n_menor_10"] = np.where(df[col] < 10, "sí", "")
    return df


def miembros(z):
    """Mapa {nombre del CSV: (zip, miembro)} de un zip mensual, entrando a CSV.zip si viene anidado."""
    zf, out = zipfile.ZipFile(z), {}
    for n in zf.namelist():
        if n.lower().endswith("csv.zip"):
            inner = zipfile.ZipFile(io.BytesIO(zf.read(n)))
            out.update({m: (inner, m) for m in inner.namelist() if m.lower().endswith(".csv")})
        elif n.lower().endswith(".csv"):
            out[n] = (zf, n)
    return out


def leer(mm, clave, cols):
    nombre = [n for n in mm if re.search(clave, n.split("/")[-1], flags=re.I)][0]
    zf, m = mm[nombre]
    with zf.open(m) as fh:
        d = pd.read_csv(fh, sep=";", dtype=str, encoding="latin-1", low_memory=False,
                        usecols=lambda c: c.replace("ï»¿", "").strip("﻿").upper() in cols)
    d.columns = [c.replace("ï»¿", "").strip("﻿").upper() for c in d.columns]
    return d[txt(d.AREA).isin(["08", "8"])]


# ---------------------------------------------------------------- 1. Lectura de los meses disponibles
hs, ps, fs, os_ = [], [], [], []
archivos = {}
for z in sorted(DIR.glob("*.zip")):
    mm = miembros(z)
    h = leer(mm, r"^Datos del hogar", set(H + ["AREA", "CLASE", "FEX_C18", "P4000", "P4030S1A1", "P5000", "P5010",
                                               "P5090", "P5110", "P6008"]))
    mes = int(h.MES.iloc[0])
    archivos[mes] = z.name
    hs.append(h)
    ps.append(leer(mm, r"^Caracter", set(K + ["AREA", "P6040", "P6020", "P6170"])))
    fs.append(leer(mm, r"^Fuerza de trabajo", set(K + ["AREA", "P6240", "FT", "PET"])))
    os_.append(leer(mm, r"^Ocupados", set(K + ["AREA", "P6800", "P6850", "P6880", "P6430", "OCI"])))
h, p, f, o = (pd.concat(x, ignore_index=True) for x in (hs, ps, fs, os_))
for d in (h, p, f, o):
    d["MES"] = num(d.MES).astype(int)
meses = sorted(h.MES.unique())
faltan = [m for m in range(1, 13) if m not in meses]
NM = len(meses)
h["W"] = num(h.FEX_C18) / NM                 # factor anual con los meses disponibles
h["ESTRATO"] = num(h.P4030S1A1)
h["GRUPO"] = h.ESTRATO.map({1: "E1–2", 2: "E1–2", 3: "E3–4", 4: "E3–4", 5: "E5–6", 6: "E5–6"})
dup = int(h.duplicated(["DIRECTORIO", "SECUENCIA_P"]).sum())

o["EN_CASA"] = txt(o.P6880) == "1"
o["LUGAR"] = txt(o.P6880).map(LUGAR)
o["LUGAR_G"] = o.LUGAR.map(LUGAR_G).fillna("Obra, campo u otro")
o = o.merge(h[H + ["W", "ESTRATO", "GRUPO"]], on=H, how="left")
p = p.merge(h[H + ["W", "ESTRATO", "GRUPO"]], on=H, how="left")
p["EDAD"] = num(p.P6040)
f = f.merge(p[K + ["EDAD"]], on=K, how="left").merge(h[H + ["W", "GRUPO"]], on=H, how="left")

# ---------------------------------------------------------------- 2. Muestra por mes
filas = []
for m in range(1, 13):
    if m not in meses:
        filas.append({"mes": MESES[m - 1], "archivo": "no disponible"})
        continue
    hh = h[h.MES == m]
    filas.append({"mes": MESES[m - 1], "archivo": archivos[m], "hogares": len(hh), "personas": int((p.MES == m).sum()),
                  "ocupados": int((o.MES == m).sum()), "hogares_expandidos_mes": round(num(hh.FEX_C18).sum()),
                  "personas_expandidas_mes": round(num(p[p.MES == m].W).sum() * NM),
                  "pct_ocupados_en_casa": round(pct(o[o.MES == m].EN_CASA, o[o.MES == m].W), 1)})
t_mes = pd.DataFrame(filas)
tabla(t_mes, "geih_muestra_mes.csv", index=False, decimal=",")

# ---------------------------------------------------------------- 3. Muestra y atributos por estrato, frente a la tabla publicada (12 meses)
pub = pd.read_csv(REPO / "tablas" / "GEIH2024_Barranquilla_AM_resumen_estrato.csv", sep=";", decimal=",", encoding="utf-8-sig")
hog_oc = o.groupby(H).agg(N_OC=("ORDEN", "size"), N_CASA=("EN_CASA", "sum"), HORAS=("P6800", lambda s: num(s).sum()))
h = h.merge(hog_oc, on=H, how="left")
for c in ["N_OC", "N_CASA", "HORAS"]:
    h[c] = h[c].fillna(0)
W = h[h.ESTRATO.between(1, 6)].W.sum()
filas = []
for e in range(1, 7):
    d = h[h.ESTRATO == e]
    oe = o[o.ESTRATO == e]
    pe = pub[pub.estrato == e].iloc[0]
    pc = pct(oe.EN_CASA, oe.W)
    n_oc = len(oe)
    se = np.sqrt(pc / 100 * (1 - pc / 100) / n_oc) * 100
    filas.append({"estrato": f"E{e}", "hogares_n": len(d), "hogares_n_12m": int(pe.n),
                  "pct_hogares": round(d.W.sum() / W * 100, 1), "pct_hogares_12m": pe.pct_hogares,
                  "personas_hogar": round((num(d.P6008) * d.W).sum() / d.W.sum(), 2), "personas_hogar_12m": pe.personas,
                  "ocupados_hogar": round((d.N_OC * d.W).sum() / d.W.sum(), 2), "ocupados_hogar_12m": pe.ocupados,
                  "hog_sin_ocupados_pct": round(pct(d.N_OC == 0, d.W), 1), "hog_sin_ocupados_pct_12m": pe.hog_sin_ocup,
                  "horas_sem_ocupado": round((d.HORAS * d.W).sum() / (d.N_OC * d.W).sum(), 1), "horas_sem_ocupado_12m": pe.horas_ocup,
                  "ocupados_n": n_oc, "ocupados_en_casa_n": int(oe.EN_CASA.sum()),
                  "pct_ocupados_en_casa": round(pc, 1), "ic95_inf": round(pc - 1.96 * se, 1), "ic95_sup": round(pc + 1.96 * se, 1),
                  "pct_ocupados_en_casa_12m": pe.trab_casa_pct,
                  "pct_hogares_con_ocupado_en_casa": round(pct(d.N_CASA > 0, d.W), 1)})
t_est = marca(pd.DataFrame(filas), "ocupados_en_casa_n")
tabla(t_est, "geih_estrato.csv", index=False, decimal=",")

# ---------------------------------------------------------------- 4. Trabajo en la vivienda por mes y grupo de estrato
filas = []
for m in meses:
    for g in GRUPOS + ["Total"]:
        d = o[(o.MES == m) & ((o.GRUPO == g) if g != "Total" else o.ESTRATO.between(1, 6))]
        filas.append({"mes": MESES[m - 1], "grupo": g, "n": len(d), "n_en_casa": int(d.EN_CASA.sum()),
                      "pct_en_casa": round(pct(d.EN_CASA, d.W), 1)})
t_mg = marca(pd.DataFrame(filas), "n_en_casa")
tabla(t_mg, "geih_trabajo_casa_mes.csv", index=False, decimal=",")

# ---------------------------------------------------------------- 5. Lugar de trabajo por grupo de estrato
filas = []
for g, d in list(o.groupby("GRUPO")) + [("Total", o[o.ESTRATO.between(1, 6)])]:
    for lg in ORDEN_LG:
        m = d.LUGAR_G == lg
        filas.append({"grupo": g, "lugar": lg, "n": int(m.sum()), "pct": round(pct(m, d.W), 1)})
t_lug = marca(pd.DataFrame(filas))
tabla(t_lug, "geih_lugar_trabajo.csv", index=False, decimal=",")

# ---------------------------------------------------------------- 6. Actividad principal de las personas de 15+ (P6240), para comparar con la ENUT
f15 = f[(f.EDAD >= 15) & (txt(f.P6240) != "")]
filas = []
for g, d in list(f15.groupby("GRUPO")) + [("Total", f15[f15.GRUPO.notna()])]:
    for c, lab in ACT.items():
        m = txt(d.P6240) == c
        filas.append({"grupo": g, "actividad": lab, "n": int(m.sum()), "pct": round(pct(m, d.W), 1)})
t_act = marca(pd.DataFrame(filas))
tabla(t_act, "geih_actividad_15mas.csv", index=False, decimal=",")

# ---------------------------------------------------------------- 7. Faltantes
falt = [
    ("Estrato (P4030S1A1) sin dato, 0 u otro código", "hogares", len(h), int((~h.ESTRATO.between(1, 6)).sum())),
    ("Personas por hogar (P6008) vacía", "hogares", len(h), int((txt(h.P6008) == "").sum())),
    ("Cuartos (P5000) vacío", "hogares", len(h), int((txt(h.P5000) == "").sum())),
    ("Valor de la vivienda (P5110) vacío", "hogares", len(h), int((txt(h.P5110) == "").sum())),
    ("Valor de la vivienda (P5110) vacío", "hogares propietarios (P5090 = 1–2)", int(txt(h.P5090).isin(["1", "2"]).sum()),
     int((txt(h.P5090).isin(["1", "2"]) & (txt(h.P5110) == "")).sum())),
    ("Lugar de trabajo (P6880) vacío", "ocupados", len(o), int((txt(o.P6880) == "").sum())),
    ("Horas normales (P6800) vacías", "ocupados", len(o), int((txt(o.P6800) == "").sum())),
    ("Actividad principal (P6240) vacía", "personas de 15+", int((f.EDAD >= 15).sum()), int(((f.EDAD >= 15) & (txt(f.P6240) == "")).sum())),
    ("Hogar repetido entre meses (DIRECTORIO + SECUENCIA_P)", "hogares", len(h), dup),
]
t_falt = pd.DataFrame(falt, columns=["variable", "universo", "n_universo", "n_faltante"])
t_falt["pct"] = (t_falt.n_faltante / t_falt.n_universo * 100).round(1)
tabla(t_falt, "geih_faltantes.csv", index=False, decimal=",")

# Quién trabaja en la vivienda: posición ocupacional (P6430) y horas normales (P6800), estratos 1–6
POS = {"1": "Empleado de empresa particular", "2": "Empleado del gobierno", "3": "Empleado doméstico",
       "4": "Cuenta propia", "5": "Patrón o empleador", "6": "Familiar sin remuneración",
       "7": "Sin remuneración en otro hogar", "8": "Jornalero o peón", "9": "Otro"}
oo = o[o.ESTRATO.between(1, 6)]
filas = []
for lab, d in [("En esta vivienda", oo[oo.EN_CASA]), ("Fuera de la vivienda", oo[~oo.EN_CASA])]:
    hn = num(d.P6800)
    r = {"lugar": lab, "n": len(d), "horas_normales_semana": round(float((hn * d.W).sum() / d.W[hn.notna()].sum()), 1)}
    for c, pl in POS.items():
        r["pct_" + pl] = round(pct(txt(d.P6430) == c, d.W), 1)
    filas.append(r)
tabla(marca(pd.DataFrame(filas)), "geih_posicion_en_casa.csv", index=False, decimal=",")

# ---------------------------------------------------------------- 8. Figuras
# F1: muestra por mes y grupo de estrato
fig, ax = plt.subplots(figsize=(11, 4.2))
base = np.zeros(12)
for i, g in enumerate(GRUPOS + ["sin estrato"]):
    v = np.array([((h.MES == m) & ((h.GRUPO == g) if g != "sin estrato" else h.GRUPO.isna())).sum() for m in range(1, 13)])
    ax.bar(range(12), v, bottom=base, color=PAL[i] if i < 3 else "#9a9993", label=g)
    base += v
for m in faltan:
    ax.bar(m - 1, base.max(), color="none", edgecolor="#9a9993", hatch="//", lw=0)
    ax.text(m - 1, base.max() / 2, "sin\narchivo", ha="center", va="center", fontsize=8.5, color=TXT2)
for m in meses:
    ax.text(m - 1, base[m - 1], fmt(base[m - 1], 0), ha="center", va="bottom", fontsize=8.5)
ax.set_xticks(range(12), MESES)
ax.set_ylabel("hogares en la muestra")
ax.set_ylim(0, base.max() * 1.12)
ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(.5, -.1), fontsize=9)
titulo(ax, "Hogares del área metropolitana en la muestra, por mes de 2024")
guardar(fig, "geih_muestra_mes.png", FUENTE)

# F2: trabajo en la propia vivienda por estrato, frente a la tabla publicada
fig, ax = plt.subplots(figsize=(10, 4.4))
x = np.arange(6)
ax.bar(x, t_est.pct_ocupados_en_casa, color=[EST[e] for e in t_est.estrato], label=f"{NM} meses disponibles")
ax.errorbar(x, t_est.pct_ocupados_en_casa, yerr=[t_est.pct_ocupados_en_casa - t_est.ic95_inf, t_est.ic95_sup - t_est.pct_ocupados_en_casa],
            fmt="none", ecolor="black", capsize=4, lw=1.2, label="IC 95 % (muestreo aleatorio simple)")
ax.scatter(x, t_est.pct_ocupados_en_casa_12m, marker="D", color="white", edgecolor="black", zorder=3, s=40,
           label="tabla publicada (12 meses)")
for xx, v, n in zip(x, t_est.pct_ocupados_en_casa, t_est.ocupados_n):
    ax.text(xx, 1, f"{fmt(v)} %\nn = {fmt(n, 0)}", ha="center", va="bottom", color="white", fontsize=8.5)
ax.set_xticks(x, t_est.estrato)
ax.set_ylabel("% de los ocupados (ponderado)")
ax.legend(fontsize=9, loc="upper left")
titulo(ax, "Ocupados que trabajan principalmente en su vivienda (P6880 = 1)")
guardar(fig, "geih_trabajo_casa_estrato.png", FUENTE)

# F3: trabajo en la vivienda por mes
fig, ax = plt.subplots(figsize=(11, 4.2))
for i, g in enumerate(GRUPOS + ["Total"]):
    d = t_mg[t_mg.grupo == g]
    xm = [MESES.index(m) for m in d.mes]
    ax.plot(xm, d.pct_en_casa, marker="o", color=PAL[i] if g != "Total" else "black", lw=2.5 if g == "Total" else 1.4,
            label=g if g != "Total" else "Total (estratos 1–6)")
for m in faltan:
    ax.axvspan(m - 1.4, m - .6, color="#eeede9", zorder=0)
ax.set_xticks(range(12), MESES)
ax.set_ylabel("% de los ocupados (ponderado)")
ax.legend(ncol=4, fontsize=9, loc="upper center", bbox_to_anchor=(.5, -.1))
n56 = int(t_mg[t_mg.grupo == "E5–6"].n.median())
titulo(ax, "Ocupados que trabajan en su vivienda, por mes",
       f"franjas grises: meses sin archivo; E5–6 tiene unos {n56} ocupados por mes en la muestra")
guardar(fig, "geih_trabajo_casa_mes.png", FUENTE)

# F4: lugar de trabajo por grupo de estrato
fig, ax = plt.subplots(figsize=(11, 3.6))
pv = t_lug.pivot(index="grupo", columns="lugar", values="pct").reindex(index=(GRUPOS + ["Total"])[::-1], columns=ORDEN_LG)
izq = np.zeros(len(pv))
for i, lg in enumerate(ORDEN_LG):
    ax.barh(pv.index, pv[lg], left=izq, color=PAL[i], label=lg)
    for yy, (l, v) in enumerate(zip(izq, pv[lg])):
        if v >= 6:
            ax.text(l + v / 2, yy, fmt(v, 0), ha="center", va="center", color="white", fontsize=9)
    izq += pv[lg].to_numpy()
ax.set_xlim(0, 100)
ax.set_xlabel("% de los ocupados (ponderado)")
ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(.5, -.25), fontsize=9)
titulo(ax, "Lugar donde los ocupados realizan principalmente su trabajo (P6880)")
guardar(fig, "geih_lugar_trabajo.png", FUENTE)

# F5: actividad principal de las personas de 15+ en la GEIH y en la ENUT
enut_f = TAB / "enut_actividad_15mas.csv"
if enut_f.exists():
    en = pd.read_csv(enut_f, sep=";", decimal=",", encoding="utf-8-sig")
    fig, ax = plt.subplots(1, 3, figsize=(13, 4), sharey=True)
    acts = list(ACT.values())
    y = np.arange(len(acts))
    for k, g in enumerate(GRUPOS):
        a1 = t_act[t_act.grupo == g].set_index("actividad").reindex(acts).pct
        a2 = en[en.grupo == g].set_index("actividad").reindex(acts).pct
        ax[k].barh(y - .2, a1, .4, color=PAL[0], label="GEIH 2024, área metropolitana")
        ax[k].barh(y + .2, a2, .4, color=PAL[1], label="ENUT 2024–2025, cabeceras del Atlántico")
        ax[k].set_yticks(y, acts)
        ax[k].invert_yaxis() if k == 0 else None
        titulo(ax[k], g)
        ax[k].set_xlabel("% de las personas de 15+")
    ax[0].legend(fontsize=8.5, loc="lower right")
    guardar(fig, "geih_actividad_vs_enut.png", "Fuente: DANE, GEIH 2024 y ENUT 2024–2025 (microdatos). Cálculos propios, ponderados.")

# ---------------------------------------------------------------- 9. Resumen en consola
print("Meses disponibles:", meses, "| faltan:", faltan, "| hogares repetidos entre meses:", dup)
print(t_mes.to_string(index=False))
print("Hogares", len(h), "| expandidos (FEX_C18/NM)", round(h.W.sum()), "| personas", len(p), "expandidas", round(p.W.sum()),
      "| ocupados", len(o), "expandidos", round(o.W.sum()))
print("CLASE en AREA 08:", h.CLASE.value_counts().to_dict(), "| estrato:", h.ESTRATO.value_counts(dropna=False).sort_index().to_dict())
print(t_est.T.to_string())
oo = o[o.ESTRATO.between(1, 6)]
print("Total ocupados en casa %:", round(pct(oo.EN_CASA, oo.W), 1), "| por grupo", {g: round(pct(d.EN_CASA, d.W), 1) for g, d in o.groupby("GRUPO")})
print(t_mg.pivot(index="mes", columns="grupo", values="pct_en_casa").reindex([MESES[m - 1] for m in meses]).to_string())
print("Rango mensual del total:", t_mg[t_mg.grupo == "Total"].pct_en_casa.min(), "a", t_mg[t_mg.grupo == "Total"].pct_en_casa.max())
print(t_lug.pivot(index="lugar", columns="grupo", values="pct").to_string())
print(t_act.pivot(index="actividad", columns="grupo", values="pct").to_string())
print(t_falt.to_string(index=False))
print("OCI:", txt(o.OCI).value_counts().to_dict(), "| edad min ocupados", num(o.merge(p[K + ['EDAD']], on=K).EDAD).min(),
      "| edad min con P6240", f[txt(f.P6240) != ""].EDAD.min())
en_casa_h = oo[oo.EN_CASA]
print("Horas normales/semana: en casa", round((num(en_casa_h.P6800) * en_casa_h.W).sum() / en_casa_h.W[num(en_casa_h.P6800).notna()].sum(), 1),
      "| fuera", round((num(oo[~oo.EN_CASA].P6800) * oo[~oo.EN_CASA].W).sum() / oo[~oo.EN_CASA].W[num(oo[~oo.EN_CASA].P6800).notna()].sum(), 1))
print("Posición ocupacional (P6430) de quienes trabajan en casa %:", (en_casa_h.groupby(txt(en_casa_h.P6430)).W.sum() / en_casa_h.W.sum() * 100).round(1).to_dict())
