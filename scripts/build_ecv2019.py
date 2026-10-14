import csv, glob, os, sys, collections

W = "/home/claude/work/"
OUT = "/mnt/user-data/outputs/"
os.makedirs(OUT, exist_ok=True)


def rd(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def num(x):
    x = (x or "").strip().replace(",", ".")
    try:
        return float(x)
    except ValueError:
        return None


def key(r):
    return (r["DIRECTORIO"].strip(), r["SECUENCIA_ENCUESTA"].strip(), r["SECUENCIA_P"].strip())


mun = {r["DIRECTORIO"].strip(): r["P1_MUNICIPIO"].strip() for r in rd(W + "ecv2019_municipio/municipio_ecv2019.csv")}
viv = rd(W + "ecv2019_vivienda/vivienda_ecv2019.csv")
bq = {}
for r in viv:
    if r["P1_DEPARTAMENTO"].strip() == "08" and mun.get(r["DIRECTORIO"].strip()) == "001":
        bq[key(r)] = r
print("hogares Barranquilla:", len(bq))
dirs = {k[0] for k in bq}

serv = {key(r): r for r in rd(W + "ecv2019_servicios/servicios_ecv2019.csv") if key(r) in bq}
ener = {key(r): r for r in rd(W + "ecv2019_extract/energeticos_ecv2019.csv") if key(r) in bq}
ten = {key(r): r for r in rd(glob.glob(W + "ecv2019_tenencia/*.csv")[0]) if key(r) in bq}
print("cols viv:", list(viv[0].keys())[:40])
print("cols serv:", list(next(iter(serv.values())).keys()))

# persons
hmap = {(k[0], k[2]): k for k in bq}
def hk(r):
    return hmap.get((r["DIRECTORIO"].strip(), r["SECUENCIA_P"].strip()))
pers = collections.defaultdict(list)
for r in rd(W + "ecv2019_caract/caract_ecv2019.csv"):
    if hk(r):
        pers[hk(r)].append(r)
lab = collections.defaultdict(list)
for r in rd(glob.glob(W + "ecv2019_fuerza/Fuerza*.csv")[0]):
    if hk(r):
        lab[hk(r)].append(r)
print("persons:", sum(len(v) for v in pers.values()), "labor rows:", sum(len(v) for v in lab.values()))

rows = []
for k, v in bq.items():
    s = serv.get(k, {})
    e = ener.get(k, {})
    t = ten.get(k, {})
    ps = pers.get(k, [])
    ls = lab.get(k, [])
    ages = [num(p["P6040"]) for p in ps if num(p["P6040"]) is not None]
    head = [p for p in ps if p["P6051"].strip() == "1"]
    row = {
        "DIRECTORIO": k[0], "SECUENCIA_ENCUESTA": k[1], "SECUENCIA_P": k[2],
        "CLASE": v.get("CLASE", ""),
        "ESTRATO": v.get("P8520S1A1", "").strip(),
        "TIPO_VIVIENDA_P1070": v.get("P1070", "").strip(),
        "PAREDES_P4005": v.get("P4005", "").strip(),
        "PISOS_P4015": v.get("P4015", "").strip(),
        "TECHO_P4567": v.get("P4567", "").strip(),
        "CUARTOS_P5000": s.get("P5000", "").strip(),
        "CUARTOS_DORMIR_P5010": s.get("P5010", "").strip(),
        "PERSONAS_HOGAR": s.get("CANT_PERSONAS_HOGAR", "").strip(),
        "INGRESO_HOGAR": s.get("I_HOGAR", "").strip(),
        "INGRESO_PERCAPITA": s.get("PERCAPITA", "").strip(),
        "TIPO_AC_P5523": e.get("P5523", "").strip(),
        "HORAS_AC_P5524": e.get("P5524", "").strip(),
        "TIENE_AC": 1 if e.get("P5523", "").strip() else 0,
        "TIENE_VENTILADOR": 1 if (any(e.get("P5525S%d" % i, "").strip() == "1" for i in (1, 2, 3, 4)) or (num(e.get("P5526", "")) or 0) > 0) else 0,
        "VENT_TECHO_P5525S1": e.get("P5525S1", "").strip() or 0,
        "VENT_PARED_P5525S2": e.get("P5525S2", "").strip() or 0,
        "VENT_MESA_P5525S3": e.get("P5525S3", "").strip() or 0,
        "VENT_PEDESTAL_P5525S4": e.get("P5525S4", "").strip() or 0,
        "HORAS_VENTILADOR_P5526": e.get("P5526", "").strip(),
        "PAGO_ELEC_P5018": e.get("P5018", "").strip(),
        "TENENCIA_P5095": t.get("P5095", "").strip(),
        "VALOR_ARRIENDO_EST_P5130": t.get("P5130", "").strip(),
        "ARRIENDO_PAGADO_P5140": t.get("P5140", "").strip(),
        "N_PERSONAS_CARACT": len(ps),
        "EDAD_MIN": min(ages) if ages else "",
        "EDAD_MAX": max(ages) if ages else "",
        "EDAD_MEDIA": round(sum(ages) / len(ages), 1) if ages else "",
        "N_MENORES_5": sum(1 for a in ages if a < 5),
        "N_5_14": sum(1 for a in ages if 5 <= a < 15),
        "N_15_64": sum(1 for a in ages if 15 <= a < 65),
        "N_65_MAS": sum(1 for a in ages if a >= 65),
        "SEXO_JEFE_P6020": head[0]["P6020"].strip() if head else "",
        "EDAD_JEFE": head[0]["P6040"].strip() if head else "",
        "TIENE_NEVERA": 1 if e.get("P5514", "").strip() else 0,
        "NEVERA_TAMANO_P5514": e.get("P5514", "").strip(),
        "NEVERA_ANTIGUEDAD_ANOS_P5515": e.get("P5515", "").strip(),
        "LAVADORA_CARGA_P5509": e.get("P5509", "").strip(),
        "LAVADORA_CARGAS_SEM_P5510": e.get("P5510", "").strip(),
        "SECADORA_CARGAS_SEM_P5512": e.get("P5512", "").strip(),
        "CALENTADOR_AGUA_P5518": e.get("P5518", "").strip(),
        "TV_CONV_H_LV_P5521S1": e.get("P5521S1", "").strip(),
        "TV_CONV_H_FS_P5521S2": e.get("P5521S2", "").strip(),
        "TV_LCD_H_LV_P5522S1": e.get("P5522S1", "").strip(),
        "TV_LCD_H_FS_P5522S2": e.get("P5522S2", "").strip(),
        "PC_ESCRITORIO_H_P5527": e.get("P5527", "").strip(),
        "PORTATILES_P5529": e.get("P5529", "").strip(),
        "PLANCHADAS_MES_P5531": e.get("P5531", "").strip(),
        "BOMBILLAS_INCAND_P5533S1": e.get("P5533S1", "").strip(),
        "BOMBILLAS_FLUOR_P5533S2": e.get("P5533S2", "").strip(),
        "BOMBILLAS_LED_P5533S3": e.get("P5533S3", "").strip(),
        "NUM_SANITARIOS_P5024": s.get("P5024", "").strip(),
        "TIPO_SANITARIO_P8526": s.get("P8526", "").strip(),
        "GAS_NATURAL_RED_P5666": s.get("P5666", "").strip(),
        "COMBUSTIBLE_COCINA_P8536": s.get("P8536", "").strip(),
        "N_OCUPADOS_P6240_1": sum(1 for l in ls if (l.get("P6240") or "").strip() == "1"),
        "N_BUSCA_TRABAJO_P6240_2": sum(1 for l in ls if (l.get("P6240") or "").strip() == "2"),
        "N_ESTUDIA_P6240_3": sum(1 for l in ls if (l.get("P6240") or "").strip() == "3"),
        "N_OFICIOS_HOGAR_P6240_4": sum(1 for l in ls if (l.get("P6240") or "").strip() == "4"),
        "N_INCAPACITADO_P6240_5": sum(1 for l in ls if (l.get("P6240") or "").strip() == "5"),
        "N_OTRA_ACT_P6240_6": sum(1 for l in ls if (l.get("P6240") or "").strip() == "6"),
        "N_FUERZA_TRABAJO_ROWS": len(ls),
        "N_ACTIVIDAD_P6240": ";".join(sorted({(l.get("P6240") or "").strip() for l in ls})),
        "FEX_C": v.get("FEX_C", "").strip(),
    }
    rows.append(row)

with open(OUT + "ECV2019_Barranquilla_consolidado.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), delimiter=";")
    w.writeheader()
    w.writerows(rows)
print("escrito", len(rows))

# quick stats
def wt(r):
    return num(r["FEX_C"]) or 0
tot = sum(wt(r) for r in rows)
print("poblacion hogares ponderada:", round(tot))
for var in ["ESTRATO", "TENENCIA_P5095", "TIPO_VIVIENDA_P1070", "TIPO_AC_P5523"]:
    c = collections.Counter()
    for r in rows:
        c[r[var]] += wt(r)
    print(var, {k: (round(v / tot * 100, 1)) for k, v in sorted(c.items())})
