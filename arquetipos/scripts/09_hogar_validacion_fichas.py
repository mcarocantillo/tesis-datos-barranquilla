"""Paso 7: atributos del hogar, representatividad frente a la ECV y fichas de los arquetipos (preregistro, v5).

Necesita las salidas de los scripts 02 a 08. Solo escribe agregados.

Salidas (salidas/tablas, salvo las fichas):
  hog_ecv_por_estrato.csv          cuartos, dormitorios, personas y tenencia de equipos por estrato (ECV 2024)
  hog_por_arquetipo_{sol}.csv      los mismos valores llevados a cada arquetipo con su composición de estratos
  val_habitaciones.csv             habitaciones del catastro frente a dormitorios de la ECV, por estrato y tipo
  val_representatividad.csv        catastro frente a la ECV: estratos, fracción de casas y habitaciones
  salidas/figuras/val_representatividad.png
  salidas/fichas/fichas_{sol}.md   una ficha por arquetipo
  salidas/fichas/fichas_{sol}.csv  lo principal de cada ficha, una fila por arquetipo
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from src.comun import BLOQUES, DECISION, FIGURAS, INTERNOS, TABLAS, cargar_viviendas  # noqa: E402
from src.ecv import hogares_2024, numero, razon  # noqa: E402
from src.estilo import GREY, INK, OCH, PET, guardar, lienzo  # noqa: E402

P7 = DECISION["paso7_v5"]
FICHAS = RAIZ / "salidas" / "fichas"
SOLUCIONES = {"por_vivienda": "carga por vivienda", "por_m2": "carga por m²"}
Z = 1.959964
EQUIPOS = P7["hogar"]["equipos"]
ETIQUETA_EQUIPO = {"aire_acondicionado": "aire acondicionado", "ventilador": "ventilador", "nevera": "nevera",
                   "lavadora": "lavadora", "televisor_plano": "televisor plano",
                   "calentador_agua": "calentador de agua o ducha eléctrica"}
POSICION = {"casa": "Casa", "ultimo_piso": "Último piso",
            "sin_cubierta": "Sin cubierta (apartamento intermedio o primer piso con vivienda encima)"}
ALGORITMO = {"kmeans": "K-Means", "kprototypes": "k-prototypes", "jerarquico": "jerárquico con Gower"}


def f(x, d=1):
    """Número con coma decimal y punto de miles."""
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "–"
    return f"{x:,.{d}f}".replace(",", "§").replace(".", ",").replace("§", ".")


def pct(x, d=1):
    return f"{f(100 * x, d)} %"


# ---------------------------------------------------------------- ECV 2024

def ecv_2024():
    """Viviendas y hogares de Barranquilla en la ECV 2024, con los atributos del hogar de la Sección 10.1."""
    viv, h = hogares_2024(P7["hogar"]["variables"].values(), EQUIPOS.values())
    for nombre, col in P7["hogar"]["variables"].items():
        h[nombre] = numero(h[col])
    for nombre, col in EQUIPOS.items():
        h[nombre] = (h[col].astype(str).str.strip() == P7["hogar"]["codigo_si"]).astype(float)
    return viv, h


def estimar(d, y, dominio):
    """Estimación y error estándar en un dominio, dejando fuera las filas sin dato."""
    y = pd.Series(y, index=d.index).astype(float)
    dom = np.asarray(dominio, bool) & y.notna().to_numpy()
    est, ee = razon(y.fillna(0), d["w"], dom, d["segmento"])
    return est, ee, int(dom.sum())


def hogar_por_estrato(h):
    filas = []
    variables = list(P7["hogar"]["variables"]) + list(EQUIPOS)
    for e in list(range(1, 7)) + ["ciudad"]:
        dom = h["estrato"].between(1, 6) if e == "ciudad" else h["estrato"] == e
        for var in variables:
            est, ee, n = estimar(h, h[var], dom)
            filas.append(dict(estrato=e, variable=var, hogares=n, valor=est, ee=ee,
                              ic_inf=est - Z * ee, ic_sup=est + Z * ee))
    return pd.DataFrame(filas)


def hogar_por_arquetipo(hog, arq):
    """Valores por estrato llevados a cada arquetipo con su composición de estratos (Sección 10.1)."""
    t = hog[hog["estrato"] != "ciudad"].copy()
    t["estrato"] = t["estrato"].astype(int)
    filas = []
    for _, a in arq.iterrows():
        peso = pd.Series({e: a[f"pct_E{e}"] / 100 for e in range(1, 7)})
        for var, g in t.groupby("variable"):
            g = g.set_index("estrato")
            val = float((peso * g["valor"]).sum())
            ee = float(np.sqrt((peso ** 2 * g["ee"] ** 2).sum()))
            filas.append(dict(arquetipo=a["arquetipo"], variable=var, valor=val, ee=ee))
    return pd.DataFrame(filas)


# ---------------------------------------------------------------- validación

def habitaciones_catastro(v):
    hab = v["total_habitaciones"].clip(lower=1)
    tipo = np.where(v["posicion"].astype(str) == "casa", "casa", "apartamento")
    return hab, pd.Series(tipo, index=v.index)


def validar_habitaciones(v, h):
    hab, tipo_cat = habitaciones_catastro(v)
    clases = P7["habitaciones"]["clases"]
    filas = []
    for e in range(1, 7):
        for tipo in ["todos", "casa", "apartamento"]:
            mc = (v["estrato_num"] == e) & hab.notna() & ((tipo_cat == tipo) if tipo != "todos" else True)
            de = (h["estrato"] == e) & ((h["tipo"] == tipo) if tipo != "todos" else True)
            est, ee, n = estimar(h, h["dormitorios"], de)
            fila = dict(estrato=e, tipo=tipo, viviendas_catastro=int(mc.sum()), hogares_ecv=n,
                        media_catastro=float(hab[mc].mean()), media_ecv=est, ic_inf=est - Z * ee, ic_sup=est + Z * ee)
            fila["dentro_ic"] = bool(fila["ic_inf"] <= fila["media_catastro"] <= fila["ic_sup"]) if n else None
            for c in clases:
                tope = c == clases[-1]
                sel_c = (hab[mc] >= c) if tope else (hab[mc] == c)
                sel_e = (h["dormitorios"] >= c) if tope else (h["dormitorios"] == c)
                fila[f"catastro_{c}{'+' if tope else ''}"] = float(sel_c.mean())
                fila[f"ecv_{c}{'+' if tope else ''}"] = estimar(h, sel_e.astype(float), de)[0]
            filas.append(fila)
    return pd.DataFrame(filas)


def representatividad(v, viv, hab_val):
    filas = []
    valida = viv["estrato"].between(1, 6)

    def agregar(comp, grupo, cat, est, ee, n):
        filas.append(dict(comparacion=comp, grupo=grupo, catastro=cat, ecv=est, ic_inf=est - Z * ee,
                          ic_sup=est + Z * ee, dentro_ic=bool(est - Z * ee <= cat <= est + Z * ee),
                          diferencia=cat - est, muestra_ecv=n))

    for e in range(1, 7):
        est, ee, n = estimar(viv, (viv["estrato"] == e).astype(float), valida)
        agregar("viviendas por estrato (fracción)", f"E{e}", float((v["estrato_num"] == e).mean()), est, ee, n)
    pos = v["posicion"].astype(str)
    primer_piso = (pos == "sin_cubierta") & (v["planta_ubicacion"] <= 1) & (v["tipo"] == "baja_altura")
    for b in BLOQUES:
        mb = v["bloque"] == b
        est, ee, n = estimar(viv, (viv["tipo"] == "casa").astype(float), valida & (viv["bloque"] == b))
        agregar("fracción de casas", f"{b}: catastro, posición casa", float((pos[mb] == "casa").mean()), est, ee, n)
        agregar("fracción de casas", f"{b}: catastro, casa y primer piso de baja altura",
                float(((pos == "casa") | primer_piso)[mb].mean()), est, ee, n)
    for _, r in hab_val[hab_val["tipo"] == "todos"].iterrows():
        filas.append(dict(comparacion="habitaciones (media)", grupo=f"E{r['estrato']}", catastro=r["media_catastro"],
                          ecv=r["media_ecv"], ic_inf=r["ic_inf"], ic_sup=r["ic_sup"], dentro_ic=r["dentro_ic"],
                          diferencia=r["media_catastro"] - r["media_ecv"], muestra_ecv=r["hogares_ecv"]))
    return pd.DataFrame(filas)


def figura(rep):
    fig, axs = lienzo(16, 6.5)
    fig.clf()
    axs = fig.subplots(1, 3)
    coma = FuncFormatter(lambda x, _: f(x, 1) if abs(x - round(x)) > 1e-9 else f(x, 0))
    paneles = [("viviendas por estrato (fracción)", "Viviendas por estrato (%)", 100),
               ("fracción de casas", "Casas por bloque de estratos (%)", 100),
               ("habitaciones (media)", "Habitaciones (catastro) y dormitorios (ECV)", 1)]
    for ax, (comp, titulo, esc) in zip(axs, paneles):
        t = rep[rep["comparacion"] == comp].reset_index(drop=True)
        if comp == "fracción de casas":
            t = t.assign(base=t["grupo"].str.split(":").str[0])
            ecv = t.drop_duplicates("base")
            xs = np.arange(len(ecv))
            ax.errorbar(xs, ecv["ecv"] * esc, yerr=[(ecv["ecv"] - ecv["ic_inf"]) * esc, (ecv["ic_sup"] - ecv["ecv"]) * esc],
                        fmt="o", color=PET, ms=4, capsize=2, lw=0.8, label="ECV 2024 (IC 95 %)")
            a = t[t["grupo"].str.contains("posición casa")]
            bb = t[t["grupo"].str.contains("primer piso")]
            ax.scatter(xs - 0.12, a["catastro"] * esc, marker="D", s=14, color=OCH, zorder=3, label="Catastro")
            ax.scatter(xs + 0.12, bb["catastro"] * esc, marker="D", s=14, facecolor="white", edgecolor=OCH, zorder=3,
                       label="Catastro, con primeros pisos de baja altura")
            ax.set_xticks(xs, [f"E{b}" for b in ecv["base"]])
        else:
            xs = np.arange(len(t))
            ax.errorbar(xs, t["ecv"] * esc, yerr=[(t["ecv"] - t["ic_inf"]) * esc, (t["ic_sup"] - t["ecv"]) * esc],
                        fmt="o", color=PET, ms=4, capsize=2, lw=0.8, label="ECV 2024 (IC 95 %)")
            ax.scatter(xs, t["catastro"] * esc, marker="D", s=14, color=OCH, zorder=3, label="Catastro")
            ax.set_xticks(xs, t["grupo"])
        ax.set_title(titulo, fontsize=8, loc="left", color=INK)
        ax.yaxis.set_major_formatter(coma)
        ax.grid(axis="y", color=GREY, lw=0.3, alpha=0.4)
    h1, l1 = axs[1].get_legend_handles_labels()
    fig.legend(h1, l1, ncols=3, loc="lower center", frameon=False, bbox_to_anchor=(0.5, -0.02))
    fig.set_layout_engine("constrained")
    fig.get_layout_engine().set(rect=(0, 0.08, 1, 0.92))
    guardar(fig, FIGURAS / "val_representatividad.png")


# ---------------------------------------------------------------- fichas

def reglas_arbol(sol):
    """Reglas del árbol del Paso 5 por arquetipo, de mayor a menor número de viviendas."""
    patron = re.compile(r"^(\S+)\s+\(([\d,]+) viviendas, (\d+)% del arquetipo\): (.*?)(\.\.\.)?$")
    reglas = {}
    for linea in (TABLAS / f"clf_reglas_arbol_{sol}.txt").read_text(encoding="utf-8").splitlines():
        m = patron.match(linea.strip())
        if m:
            reglas.setdefault(m[1], []).append((int(m[2].replace(",", "")), m[4]))
    return {k: sorted(x, reverse=True) for k, x in reglas.items()}


ENVOLVENTE = [("techo: concreto", "Techo de concreto", "%"), ("techo: asbesto_cemento", "Techo de asbesto-cemento", "%"),
              ("techo: metalica_zinc", "Techo metálico o de zinc", "%"), ("techo: otro", "Techo de otro material", "%"),
              ("U del techo", "U del techo (W/m²K)", 2), ("absortancia del techo", "Absortancia del techo", 2),
              ("paredes: mamposteria", "Muros de mampostería", "%"), ("U del muro", "U del muro (W/m²K)", 2),
              ("absortancia del muro", "Absortancia del muro", 2),
              ("capacidad C_m", "Capacidad C_m (kJ/K por m² de piso)", 0),
              ("infiltración", "Infiltración con ventanas cerradas (renovaciones por hora)", 2),
              ("pisos: acabado", "Pisos con acabado", "%"), ("relación ventana-muro", "Relación ventana-muro", 2),
              ("U de la ventana", "U de la ventana (W/m²K)", 2), ("factor solar del vidrio", "Factor solar del vidrio", 2),
              ("factor de sombra", "Factor de sombra", 2), ("fracción climatizada", "Fracción climatizada", 2)]


def fichas(sol, v, arq_v, hog_arq, hab_val, rep, sens):
    arq = pd.read_csv(TABLAS / f"arquetipos_{sol}.csv")
    final = json.loads((TABLAS / "agr_resultado_final.json").read_text(encoding="utf-8"))[sol]
    reglas = reglas_arbol(sol)
    recall = pd.read_csv(TABLAS / f"clf_recall_{sol}.csv", index_col=0)
    prob = pd.read_csv(TABLAS / f"clf_probabilidades_{sol}.csv").set_index("arquetipo")
    env = pd.read_csv(TABLAS / f"env_priors_{sol}.csv")
    diri = pd.read_csv(TABLAS / "env_dirichlet_celdas.csv")
    diri = diri[(diri["alternativa"] == "usada") & (diri["variable"] == "techo")].drop_duplicates(["tipo", "bloque"])
    n_celda = {(r.tipo, r.bloque): int(r.n) for r in diri.itertuples()}
    s = sens[sens["solucion"] == sol]
    influyentes = s.loc[s["influyente"] & s["aplica"], "variable_quitada"].tolist()
    k_est = arq.groupby("estrato_algoritmo")["arquetipo"].apply(list)
    hab, _ = habitaciones_catastro(v)
    fuera_hab = hab_val[(hab_val["tipo"] == "todos") & (hab_val["dentro_ic"] == False)]["estrato"].tolist()  # noqa: E712
    casas_fuera = rep[(rep["comparacion"] == "fracción de casas") & rep["grupo"].str.contains("posición casa")
                      & (rep["dentro_ic"] == False)]["grupo"].str.split(":").str[0].tolist()  # noqa: E712

    md = [f"# Fichas de los arquetipos: solución con {SOLUCIONES[sol]} ({len(arq)} arquetipos)", "",
          "Preregistro de la Fase 1, versión 5, Sección 10.5. Solo agregados. La carga es el índice simplificado del "
          "Paso 3, con una envolvente común para todas las viviendas; no es la carga simulada de la Fase 2. Los priors "
          "de envolvente son los del Paso 6 (media e intervalo del 90 %) y los atributos del hogar salen de la ECV 2024 "
          "por estrato, llevados a cada arquetipo con su composición de estratos.", ""]
    tabla = []
    for _, a in arq.iterrows():
        nombre = a["arquetipo"]
        pos_txt, bloque = a["estrato_algoritmo"].split("|")
        viv = v[arq_v == nombre]
        hermanos = [x for x in k_est[a["estrato_algoritmo"]] if x != nombre]
        tipo_ecv = "casa" if pos_txt == "casa" else "apartamento"
        e_pct = {e: a[f"pct_E{e}"] for e in range(1, 7) if a[f"pct_E{e}"] > 0}
        ep = env[env["arquetipo"] == nombre].set_index("parametro")
        hg = hog_arq[hog_arq["arquetipo"] == nombre].set_index("variable")
        h_cat = hab.loc[viv.index]

        md += [f"## {nombre} · {POSICION[pos_txt].split(' (')[0]}, estratos {bloque}", ""]
        md += [f"**Identificación.** {f(a['viviendas'], 0)} viviendas ({f(a['pct_viviendas'], 1)} % de la ciudad) en "
               f"{f(a['edificios'], 0)} edificios. Posición: {POSICION[pos_txt].lower()}. Agrupamiento: "
               f"{ALGORITMO[final['algoritmo_final']]} en el estrato «{POSICION[pos_txt].split(' (')[0].lower()} · {bloque}», "
               f"con {len(k_est[a['estrato_algoritmo']])} grupo(s).", ""]
        md += [f"**Definición.** Rasgos típicos (percentiles 25 a 75): área de {f(a['area_p25'], 0)} a "
               f"{f(a['area_p75'], 0)} m² (mediana {f(a['area_mediana'], 0)} m²); {f(a['plantas_mediana'], 0)} piso(s) "
               f"en la unidad; piso {f(a['piso_mediana'], 0)} del edificio (mediana).", "",
               "Reglas principales del árbol de asignación (Paso 5):", ""]
        rs = reglas.get(nombre, [])
        md += [f"- {r} ({f(n, 0)} viviendas de entrenamiento)" for n, r in rs[:3]]
        if len(rs) > 3:
            md += [f"- y {len(rs) - 3} reglas más (`clf_reglas_arbol_{sol}.txt`)"]
        md += ["", "**Rasgos físicos.**", "", "| Rasgo | Valor |", "| --- | --- |",
               f"| Área (m²), mediana (P25–P75) | {f(a['area_mediana'], 0)} ({f(a['area_p25'], 0)}–{f(a['area_p75'], 0)}) |",
               f"| Pisos de la unidad, mediana | {f(a['plantas_mediana'], 0)} |",
               f"| Piso de la unidad, mediana | {f(a['piso_mediana'], 0)} |",
               f"| En propiedad horizontal | {f(a['pct_ph'], 1)} % |",
               f"| En multifamiliar (4 pisos o más) | {f(a['pct_multifamiliar'], 1)} % |",
               f"| Época: antes de 1990 / 1990–2009 / 2010 o después | {f(a['pct_antes_1990'], 1)} / "
               f"{f(a['pct_1990_2009'], 1)} / {f(a['pct_2010_o_despues'], 1)} % |",
               "| Estratos | " + ", ".join(f"E{e} {f(p, 1)} %" for e, p in e_pct.items()) + " |", ""]
        md += [f"**Carga simplificada (índice del Paso 3).** Mediana de {f(a['carga_mediana_kWh'], 0)} kWh térmicos al "
               f"año por vivienda y {f(a['carga_m2_mediana_kWh'], 0)} kWh por m².", ""]
        md += ["**Envolvente (priors del Paso 6).**", "", "| Parámetro | Media | Intervalo del 90 % |", "| --- | --- | --- |"]
        for clave, etq, d in ENVOLVENTE:
            if clave not in ep.index:
                continue
            r = ep.loc[clave]
            if d == "%":
                md.append(f"| {etq} | {pct(r['media'], 0)} | {pct(r['p5'], 0)}–{pct(r['p95'], 0)} |")
            else:
                extra = f" ({r['zona']})" if clave == "fracción climatizada" else ""
                md.append(f"| {etq}{extra} | {f(r['media'], d)} | {f(r['p5'], d)}–{f(r['p95'], d)} |")
        if pos_txt == "sin_cubierta":
            md.append("| Techo | no expuesto (hay otra vivienda encima) | |")
        md += ["", "**Hogar.**", "", "| Atributo | Valor |", "| --- | --- |",
               f"| Habitaciones según el catastro, mediana (media) | {f(h_cat.median(), 0)} ({f(h_cat.mean(), 1)}) |",
               f"| Dormitorios según la ECV, media | {f(hg.loc['dormitorios', 'valor'], 1)} (± {f(Z * hg.loc['dormitorios', 'ee'], 1)}) |",
               f"| Personas por hogar según la ECV | {f(hg.loc['personas', 'valor'], 1)} (± {f(Z * hg.loc['personas', 'ee'], 1)}) |"]
        md += [f"| Hogares con {ETIQUETA_EQUIPO[eq]} | {pct(hg.loc[eq, 'valor'], 0)} (± {f(100 * Z * hg.loc[eq, 'ee'], 0)} puntos) |"
               for eq in EQUIPOS]
        rec = recall.loc[nombre] if nombre in recall.index else None
        md += ["", f"**Calidad.** Estabilidad (Jaccard): {f(a['jaccard'], 2)}. Recall en la prueba: árbol "
                   f"{f(rec['arbol'], 3) if rec is not None else '–'}, Random Forest {f(rec['bosque'], 3) if rec is not None else '–'}. "
                   f"Probabilidad media de asignación: {f(prob.loc[nombre, 'probabilidad_media'], 3)} "
                   f"({pct(prob.loc[nombre, 'frac_menor_0_8'], 1)} de las viviendas por debajo de 0,8).", ""]

        lim = []
        if hermanos:
            lim.append(f"Comparte con {', '.join(hermanos)} el prior de materiales de la ECV, que no distingue tamaño "
                       "ni época dentro de la misma posición y bloque; los atributos del hogar solo cambian por la "
                       "composición de estratos.")
        n = n_celda.get((tipo_ecv, bloque), 0)
        if n < 30:
            lim.append(f"La celda de la ECV ({tipo_ecv}, estratos {bloque}) tiene solo {n} viviendas: los priors de "
                       "materiales son muy inciertos.")
        otros = sorted({b for _, r in rs for b in re.findall(r"\d-\d", r.split("bloque de estratos:")[-1])
                        if "bloque de estratos:" in r} - {bloque})
        if otros:
            lim.append(f"Alguna regla del árbol admite el bloque {', '.join(otros)}, donde el arquetipo no tiene "
                       "viviendas; el árbol los junta porque casi no hay viviendas así en esos estratos. El arquetipo "
                       "se define por su bloque.")
        if pos_txt == "ultimo_piso":
            lim.append("Techo: concreto en los multifamiliares (supuesto S6) y, en los de baja altura, el reparto de "
                       "los apartamentos de la ECV (Nota 5).")
        if bloque in casas_fuera:
            lim.append(f"La fracción de casas del catastro en los estratos {bloque} queda fuera del intervalo de la "
                       "ECV, así que el puente entre la posición y el tipo de vivienda de la ECV es aproximado.")
        fuera = [e for e in e_pct if e in fuera_hab and e_pct[e] >= 5]
        if fuera:
            lim.append("Las habitaciones del catastro difieren de los dormitorios de la ECV en los estratos "
                       f"{', '.join(map(str, fuera))} (fuera del intervalo del 95 %).")
        if hermanos and influyentes:
            lim.append(f"Su frontera con los demás grupos del estrato depende de: {', '.join(influyentes)} "
                       "(Sección 10.4).")
        elif not hermanos:
            lim.append("Lo definen la posición y el bloque de estratos; no depende de las variables de agrupamiento.")
        md += ["**Limitaciones.**", ""] + [f"- {x}" for x in lim] + [""]

        tabla.append({"arquetipo": nombre, "posicion": pos_txt, "bloque": bloque, "viviendas": int(a["viviendas"]),
                      "pct_viviendas": a["pct_viviendas"], "area_mediana": a["area_mediana"],
                      "pct_multifamiliar": a["pct_multifamiliar"], "carga_mediana_kWh": a["carga_mediana_kWh"],
                      "carga_m2_mediana_kWh": a["carga_m2_mediana_kWh"],
                      **{f"env_{k}": ep.loc[k, "media"] for k, _, _ in ENVOLVENTE if k in ep.index},
                      "zona_climatizada": ep.loc["fracción climatizada", "zona"],
                      "habitaciones_catastro_media": h_cat.mean(),
                      **{f"ecv_{k}": hg.loc[k, "valor"] for k in hg.index},
                      "jaccard": a["jaccard"], "prob_media": prob.loc[nombre, "probabilidad_media"],
                      "limitaciones": " | ".join(lim)})
    FICHAS.mkdir(parents=True, exist_ok=True)
    (FICHAS / f"fichas_{sol}.md").write_text("\n".join(md), encoding="utf-8")
    pd.DataFrame(tabla).to_csv(FICHAS / f"fichas_{sol}.csv", index=False, encoding="utf-8-sig")


# ---------------------------------------------------------------- principal

def main():
    viv, h = ecv_2024()
    print(f"ECV 2024: {len(viv)} viviendas y {len(h)} hogares de Barranquilla; "
          f"{int(h['estrato'].between(1, 6).sum())} hogares con estrato 1-6")
    hog = hogar_por_estrato(h)
    hog.to_csv(TABLAS / "hog_ecv_por_estrato.csv", index=False, encoding="utf-8-sig")
    print(hog.pivot(index="variable", columns="estrato", values="valor").round(2).to_string())

    v = cargar_viviendas()
    hab_val = validar_habitaciones(v, h)
    hab_val.to_csv(TABLAS / "val_habitaciones.csv", index=False, encoding="utf-8-sig")
    print("\nHabitaciones:\n", hab_val[["estrato", "tipo", "hogares_ecv", "media_catastro", "media_ecv", "ic_inf",
                                        "ic_sup", "dentro_ic"]].round(2).to_string())
    rep = representatividad(v, viv, hab_val)
    rep.to_csv(TABLAS / "val_representatividad.csv", index=False, encoding="utf-8-sig")
    print("\nRepresentatividad:\n", rep.round(3).to_string())
    figura(rep)

    sens = pd.read_csv(TABLAS / "val_sensibilidad_variables.csv")
    arq_final = pd.read_parquet(INTERNOS / "arquetipos_final.parquet")
    for sol in SOLUCIONES:
        arq = pd.read_csv(TABLAS / f"arquetipos_{sol}.csv")
        hog_arq = hogar_por_arquetipo(hog, arq)
        hog_arq.to_csv(TABLAS / f"hog_por_arquetipo_{sol}.csv", index=False, encoding="utf-8-sig")
        fichas(sol, v, arq_final[sol], hog_arq, hab_val, rep, sens)
        print(f"Fichas {sol}: {len(arq)}")


if __name__ == "__main__":
    main()
