"""Paso 6: priors de envolvente por arquetipo (preregistro, versión 4, con las Notas 5 a 7).

Lee el material de techo, paredes y pisos de la ECV 2019 y 2024 de Barranquilla, prueba con Rao-Scott si cambia entre
olas, arma una Dirichlet por bloque de estratos y tipo de vivienda de la ECV y la lleva a cada arquetipo de las dos
soluciones finales. A cada material le asigna transmitancia (ISO 6946), clase de masa (ISO 13790) y absortancia, y
suma las ventanas, la sombra y la fracción climatizada de CEELA. Solo escribe agregados.

Salidas (salidas/tablas, prefijo «env_»):
  env_ecv_proporciones.csv        proporción de cada material por ola, bloque y tipo, con viviendas y error estándar
  env_ecv_por_estrato.csv         lo mismo por estrato (descriptivo)
  env_rao_scott.csv               prueba entre olas por celda y variable, y su sensibilidad al efecto de diseño
  env_decision_olas.json          olas por variable, efectos de diseño y fracción de multifamiliares por bloque
  env_dirichlet_celdas.csv        Dirichlet de cada celda (y sus variantes A7 y A8)
  env_propiedades_materiales.csv  U del techo por la ISO 6946, U de muros, clase de masa y absortancia, con su fuente
  env_priors_{sol}.csv            priors por arquetipo (media, percentiles 5 y 95, distribución y fuente)
  env_priors_{sol}.json           los mismos priors como parámetros, para la Fase 2
  env_a7_{sol}.csv                complementario A7: techo de cada arquetipo con la otra opción de olas
  env_a8_{sol}.csv                complementario A8: techo con las reglas originales de la Sección 9.3
  salidas/figuras/env_techo_ecv.png
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from src.comun import BLOQUES, DECISION, FIGURAS, INTERNOS, SEMILLA, TABLAS, cargar_viviendas  # noqa: E402
from src.ecv import hogares_2024, leer_zip, numero, razon, segmentos_2024  # noqa: E402
from src.estilo import GREY, INK, OCH, PALE, PET, guardar, lienzo  # noqa: E402

P = DECISION["envolvente_v4"]
N5 = P["nota5"]
# Nota 7: lognormal de la infiltración por sus percentiles 5 y 95 -> (mediana, σ del logaritmo)
INFILTRACION = {g: (float(np.sqrt(x["p5"] * x["p95"])), float(np.log(x["p95"] / x["p5"]) / (2 * stats.norm.ppf(0.95))))
                for g, x in P["nota7"]["infiltracion_ach_ventanas_cerradas"].items() if g in ("cerrada", "abierta")}
VARIABLES = ["techo", "paredes", "pisos"]
CODIGO = {"techo": "P4567", "paredes": "P4005", "pisos": "P4015"}
CATEGORIAS = {var: list(P["ecv"]["categorias"][var]) for var in VARIABLES}
TIPOS_ECV = ["casa", "apartamento"]
SOLUCIONES = ["por_vivienda", "por_m2"]
N_SORTEOS = P["dirichlet"]["sorteos"]
ETIQUETA = {"concreto": "Concreto", "asbesto_cemento": "Asbesto-cemento", "metalica_zinc": "Metálica o zinc",
            "otro": "Otro"}


# ---------------------------------------------------------------- ECV

def ecv(anio):
    """Viviendas de Barranquilla de una ola, con estrato, tipo, peso y material en categorías."""
    if anio == 2019:
        v = leer_zip("ECV 2019/Datos de la vivienda_ECV_2019.zip", "vivienda")
        mun = leer_zip("ECV 2019/Municipio de aplicacion de la encuesta 2019_ECV_2019.zip", "municipio")
        v = v.merge(mun.drop_duplicates("DIRECTORIO"), on="DIRECTORIO", how="left")
    else:
        v = leer_zip("ECV 2024/DBF-ENCV-Datos_vivienda-2024 (2).zip", "vivienda")
    v = v[(v["P1_DEPARTAMENTO"].str.strip() == "08") & (v["P1_MUNICIPIO"].str.strip() == "001")].copy()
    d = pd.DataFrame({"anio": anio, "directorio": v["DIRECTORIO"].str.strip().to_numpy(),
                      "estrato": numero(v["P8520S1A1"]).to_numpy(), "w": numero(v["FEX_C"]).to_numpy()})
    tipo = {str(c): t for t, cods in P["ecv"]["tipo"].items() for c in cods}
    d["tipo"] = v["P1070"].str.strip().map(tipo).to_numpy()
    for var in VARIABLES:
        cod = numero(v[CODIGO[var]]).astype("Int64")
        if var == "paredes" and anio == 2024:
            armonizar = {c: c for c in range(1, 11)} | {int(k): x for k, x in P["ecv"]["paredes_2024_a_2019"].items()}
            cod = cod.map(armonizar)
        mapa = {c: cat for cat, cods in P["ecv"]["categorias"][var].items() for c in cods}
        d[var] = cod.map(mapa).to_numpy()
    if anio == 2024:
        d["segmento"] = d["directorio"].map(segmentos_2024())
        assert d["segmento"].notna().all(), "viviendas de 2024 sin segmento"
    validas = d["estrato"].isin(P["ecv"]["estratos_validos"])
    excluidas = int((~validas).sum())
    d = d[validas].copy()
    d["estrato"] = d["estrato"].astype(int)
    bloque = {e: b for b, ests in DECISION["variables"]["bloques_estrato"].items() for e in ests}
    d["bloque"] = d["estrato"].map(bloque)
    assert d["tipo"].notna().all() and d[VARIABLES].notna().all().all(), "códigos sin categoría"
    return d, excluidas


def proporciones(d, dominio, var, todo=None):
    """Proporción ponderada por categoría en un dominio y su covarianza.

    2024: linealización de Taylor con el segmento como unidad primaria, sobre toda la muestra de la ola (dominio).
    2019: multinomial × efecto de diseño de 1,5."""
    cats = CATEGORIAS[var]
    w = d["w"] * dominio
    n = int(dominio.sum())
    if n == 0:
        return np.full(len(cats), np.nan), np.full((len(cats), len(cats)), np.nan), 0
    y = np.column_stack([(d[var] == c).to_numpy(float) for c in cats])
    p = (w.to_numpy()[:, None] * y).sum(0) / w.sum()
    if d["anio"].iloc[0] == 2024:
        z = w.to_numpy()[:, None] * (y - p) / w.sum()
        t = pd.DataFrame(z).groupby(d["segmento"].to_numpy()).sum().to_numpy()
        c = len(t)
        dt = t - t.mean(0)
        cov = c / (c - 1) * dt.T @ dt
    else:
        cov = P["rao_scott"]["deff_2019"] * (np.diag(p) - np.outer(p, p)) / n
    return p, cov, n


def rao_scott(p1, v1, n1, p2, v2, n2):
    """Homogeneidad entre dos muestras independientes: χ² de Pearson con la corrección de segundo orden de Rao y Scott."""
    pbar = (n1 * p1 + n2 * p2) / (n1 + n2)
    k = pbar > 0
    if k.sum() < 2:  # una sola categoría en las dos olas: no hay nada que probar
        return dict(p=np.nan)
    p1, p2, pbar = p1[k], p2[k], pbar[k]
    x2 = sum(n * ((pp - pbar) ** 2 / pbar).sum() for n, pp in [(n1, p1), (n2, p2)])
    idx = np.flatnonzero(k)[:-1]
    srs = ((np.diag(pbar) - np.outer(pbar, pbar)) * (1 / n1 + 1 / n2))[:-1, :-1]
    dis = (v1 + v2)[np.ix_(idx, idx)]
    delta = np.linalg.eigvals(np.linalg.solve(srs, dis)).real
    dm = delta.mean()
    a2 = ((delta - dm) ** 2).sum() / (len(delta) * dm ** 2)
    gl = len(delta) / (1 + a2)
    x2rs = x2 / (dm * (1 + a2))
    return dict(x2=x2, deff_medio=dm, a2=a2, gl=gl, x2_rs=x2rs, p=float(stats.chi2.sf(x2rs, gl)))


def deff_2024(p, cov, n):
    """Efecto de diseño medio (valores propios) de una proporción multinomial de la ola 2024."""
    k = np.flatnonzero(p > 0)
    if len(k) < 2:
        return np.nan
    k = k[:-1]
    srs = (np.diag(p) - np.outer(p, p))[np.ix_(k, k)] / n
    return float(np.linalg.eigvals(np.linalg.solve(srs, cov[np.ix_(k, k)])).real.mean())


def efectos_diseno(d24):
    """Nota 5: efecto de diseño de 2024 de cada variable dentro de cada tipo de vivienda, en toda la ciudad."""
    crudo = {}
    for var in VARIABLES:
        for tipo in TIPOS_ECV:
            p, cov, n = proporciones(d24, (d24["tipo"] == tipo).astype(float), var)
            crudo[(var, tipo)] = deff_2024(p, cov, n)
    usado = {k: max(N5["deff_minimo"], x) if np.isfinite(x) else N5["deff_minimo"] for k, x in crudo.items()}
    return crudo, usado


def factor_habitaciones(v):
    """Nota 6: dormitorios medios de la ECV 2024 / habitaciones medias del catastro, en los apartamentos de cada
    estrato (último piso y sin cubierta en el catastro; tipo apartamento en la ECV)."""
    _, h = hogares_2024(["P5010"], [])
    dorm = numero(h["P5010"])
    hab = v["total_habitaciones"].clip(lower=1)
    apto = v["posicion"].astype(str) != "casa"
    out = {}
    for e in range(1, 7):
        dom = (h["estrato"] == e) & (h["tipo"] == "apartamento") & dorm.notna()
        out[e] = float(razon(dorm.fillna(0), h["w"], dom, h["segmento"])[0] / hab[apto & (v["estrato_num"] == e)].mean())
    return out


def holm(pvals):
    p = np.asarray(pvals, float)
    orden = np.argsort(p)
    ajust = np.empty_like(p)
    ajust[orden] = np.minimum(1, np.maximum.accumulate(p[orden] * (len(p) - np.arange(len(p)))))
    return ajust


# ---------------------------------------------------------------- propiedades de los materiales

def resistencia_capas(capas, i):
    """Σ d/λ; si el espesor es una lista, i elige el caso (0 = U mínima, 1 = moda, 2 = U máxima)."""
    return sum((d[i] if isinstance(d, list) else d) / lam for d, lam in capas)


def u_techos():
    iso = P["iso6946"]
    filas = []
    for mat, cfg in iso["techos"].items():
        r = [resistencia_capas(cfg["capas"], i) for i in range(3)]
        u_abajo = 1 / (iso["R_si_abajo"] + r[1] + iso["R_se"])
        u_arriba = 1 / (iso["R_si_arriba"] + r[2] + iso["R_se"])
        if cfg["cielo_raso"]:
            d, lam = iso["cielo_raso_placa"]
            u_min = 1 / (iso["R_si_abajo"] + r[0] + iso["R_aire_abajo"] + d / lam + iso["R_se"])
        else:
            u_min = 1 / (iso["R_si_abajo"] + r[0] + iso["R_se"])
        filas.append(dict(material=mat, U_min=u_min, U_moda=u_abajo, U_max=u_arriba,
                          U_ceela=iso["ceela_comparacion"].get(mat, np.nan)))
    return pd.DataFrame(filas).set_index("material")


def tabla_propiedades(ut):
    m = P["masa_iso13790"]
    cl = m["clases"]
    a = P["absortancia"]
    fuente_u = "ISO 6946:2017 (R_si, R_se y cámaras de aire) y λ de la ISO 10456; cielo raso solo en el mínimo (supuesto)"
    filas = []
    for mat in CATEGORIAS["techo"]:
        u = ut.loc[mat]
        masa = m["losa_encima"] if mat == "concreto" else m["techo_liviano"]
        filas.append(dict(elemento="techo", material=mat, parametro="U (W/m²K)", minimo=u.U_min, moda=u.U_moda,
                          maximo=u.U_max, comparacion_ceela=u.U_ceela, fuente=fuente_u))
        filas.append(dict(elemento="techo", material=mat, parametro="absortancia solar", minimo=a["techo"]["min"],
                          moda=a["techo"]["moda"][mat], maximo=a["techo"]["max"],
                          fuente="moda: 1 − reflectancia de CEELA (concreto, asbesto-cemento) o valor del Paso 3; "
                                 "rango: color como supuesto"))
        filas.append(dict(elemento="techo", material=mat, parametro="capacidad (kJ/K por m² de piso)",
                          minimo=cl[masa[0]][0], moda=cl[masa[1]][0], maximo=cl[masa[2]][0],
                          fuente=f"ISO 13790, Tabla 12: clase {masa[1].replace('_', ' ')} "
                                 f"({masa[0].replace('_', ' ')} a {masa[2].replace('_', ' ')}); asignación supuesta"))
    mu = P["muros"]
    for clave, moda in mu["mamposteria"]["moda"].items():
        filas.append(dict(elemento="muro", material=f"mamposteria ({clave})", parametro="U (W/m²K)",
                          minimo=mu["mamposteria"]["min"], moda=moda, maximo=mu["mamposteria"]["max"],
                          fuente="CEELA, edificios representativos de Barranquilla (Caracterización, Tablas 33–37)"))
    filas.append(dict(elemento="muro", material="otro", parametro="U (W/m²K)", minimo=mu["otro"][0],
                      moda=mu["otro"][1], maximo=mu["otro"][2], fuente="supuesto; máximo = lámina con R_si horizontal"))
    filas.append(dict(elemento="muro", material="todos", parametro="absortancia solar", minimo=a["muro"][0],
                      moda=a["muro"][1], maximo=a["muro"][2],
                      fuente="extremos: superficies claras y oscuras de ASHRAE; moda: valor del Paso 3"))
    om = m["muro_otro"]
    filas.append(dict(elemento="muro", material="otro", parametro="capacidad (kJ/K por m² de piso)",
                      minimo=cl[om[0]][0], moda=cl[om[1]][0], maximo=cl[om[2]][0],
                      fuente="ISO 13790, Tabla 12: clase ligera (muy ligera a media); asignación supuesta"))
    return pd.DataFrame(filas)


# ---------------------------------------------------------------- celdas de la ECV

def celdas(olas, decision, deff):
    """Proporciones por ola y Dirichlet de cada celda y variable: la usada (decisión de olas y efecto de diseño de la
    Nota 5), A7 (la otra opción de olas) y A8 (efecto de diseño de 1,5 de la Sección 9.3)."""
    filas, dir_filas = [], []
    for var in VARIABLES:
        for alternativa in ["usada", "a7", "a8"]:
            juntar = decision[var] == "juntar"
            if alternativa == "a7":
                juntar = not juntar
            usadas = [2019, 2024] if juntar else [2024]
            for tipo in TIPOS_ECV:
                d_ef = P["dirichlet"]["deff"] if alternativa == "a8" else deff[(var, tipo)]
                q = combinar([proporciones(olas[a], (olas[a]["tipo"] == tipo).astype(float), var) for a in usadas])
                for bloque in BLOQUES:
                    est = [proporciones(olas[a], ((olas[a]["tipo"] == tipo) & (olas[a]["bloque"] == bloque)).astype(float),
                                        var) for a in usadas]
                    p, n = combinar(est)
                    alfa = n / d_ef * np.nan_to_num(p) + P["dirichlet"]["m"] * q[0]
                    a0 = alfa.sum()
                    for j, cat in enumerate(CATEGORIAS[var]):
                        dir_filas.append(dict(variable=var, alternativa=alternativa, olas="+".join(map(str, usadas)),
                                              tipo=tipo, bloque=bloque, categoria=cat, n=n, deff=d_ef, p=p[j],
                                              alfa=alfa[j],
                                              media=alfa[j] / a0,
                                              p5=stats.beta.ppf(0.05, alfa[j], a0 - alfa[j]) if alfa[j] > 0 else 0.0,
                                              p95=stats.beta.ppf(0.95, alfa[j], a0 - alfa[j]) if alfa[j] > 0 else 0.0))
        for anio, d in olas.items():
            for tipo in TIPOS_ECV:
                for bloque in BLOQUES:
                    dom = ((d["tipo"] == tipo) & (d["bloque"] == bloque)).astype(float)
                    p, cov, n = proporciones(d, dom, var)
                    for j, cat in enumerate(CATEGORIAS[var]):
                        filas.append(dict(anio=anio, variable=var, tipo=tipo, bloque=bloque, categoria=cat, n=n,
                                          p=p[j], ee=np.sqrt(max(cov[j, j], 0)) if n else np.nan))
    return pd.DataFrame(filas), pd.DataFrame(dir_filas)


def combinar(est):
    """Promedio de las olas ponderado por sus viviendas en el dominio."""
    n = sum(e[2] for e in est)
    if n == 0:
        return np.full(len(est[0][0]), np.nan), 0
    p = sum(e[2] * np.nan_to_num(e[0]) for e in est) / n
    return p, n


def pruebas(olas, deff):
    """Rao-Scott por celda (sección 7.5: varianza de 2019 × 1,5) y su sensibilidad con la de 2019 × d (Nota 5)."""
    filas = []
    minimo = P["rao_scott"]["min_viviendas_por_ola"]
    for var in VARIABLES:
        for tipo in TIPOS_ECV:
            for bloque in BLOQUES:
                est = {a: proporciones(d, ((d["tipo"] == tipo) & (d["bloque"] == bloque)).astype(float), var)
                       for a, d in olas.items()}
                (p1, v1, n1), (p2, v2, n2) = est[2019], est[2024]
                fila = dict(variable=var, tipo=tipo, bloque=bloque, n_2019=n1, n_2024=n2,
                            deff_2024=deff_2024(p2, v2, n2) if n2 else np.nan)
                if min(n1, n2) >= minimo:
                    fila.update(rao_scott(p1, v1, n1, p2, v2, n2))
                    escala = deff[(var, tipo)] / P["rao_scott"]["deff_2019"]
                    fila["p_sens"] = rao_scott(p1, v1 * escala, n1, p2, v2, n2)["p"]
                filas.append(fila)
    r = pd.DataFrame(filas)
    decision, sens = {}, {}
    for col, dec in [("p", decision), ("p_sens", sens)]:
        r[col + "_holm"] = np.nan
        for var, g in r.groupby("variable"):
            ok = g[col].notna()
            r.loc[g.index[ok], col + "_holm"] = holm(g.loc[ok, col])
            rechaza = (r.loc[g.index[ok], col + "_holm"] < P["rao_scott"]["alfa"]).any()
            dec[var] = "solo_2024" if rechaza else "juntar"
    return r, decision, sens


def por_estrato(olas):
    filas = []
    for anio, d in olas.items():
        for var in VARIABLES:
            for e in range(1, 7):
                for tipo in TIPOS_ECV + ["todos"]:
                    dom = (d["estrato"] == e) & ((d["tipo"] == tipo) if tipo != "todos" else True)
                    p, cov, n = proporciones(d, dom.astype(float), var)
                    for j, cat in enumerate(CATEGORIAS[var]):
                        filas.append(dict(anio=anio, variable=var, estrato=e, tipo=tipo, categoria=cat, n=n, p=p[j]))
    return pd.DataFrame(filas)


# ---------------------------------------------------------------- priors por arquetipo

def tri(rng, lmm, n):
    lo, mo, hi = lmm
    return rng.triangular(lo, mo, hi, n) if hi > lo else np.full(n, mo)


def sortear_categoria(rng, probs):
    """Una categoría por fila, con la probabilidad de esa fila."""
    u = rng.random(len(probs))
    return (u[:, None] > np.cumsum(probs, axis=1)).sum(1).clip(max=probs.shape[1] - 1)


def dirichlet(rng, alfa, n):
    """Sorteos de una Dirichlet; las categorías con α = 0 (ausentes en toda la ciudad) quedan en 0."""
    x = np.zeros((n, len(alfa)))
    k = alfa > 0
    x[:, k] = rng.dirichlet(alfa[k], n)
    return x


def techo_s6(p_apto, f_mf, frac_mf, restar):
    """Techo del último piso: concreto en los multifamiliares (S6). En los de baja altura, los apartamentos de la ECV
    tal cual (Nota 5) o, con restar=True (Sección 9.3, análisis A8), sin la parte de concreto de los multifamiliares."""
    c = CATEGORIAS["techo"].index("concreto")
    ba = p_apto.copy()
    if restar:
        pc = p_apto[:, c]
        pc_ba = np.maximum(pc - f_mf, 0) / (1 - f_mf)
        resto = np.where(1 - pc > 0, (1 - pc_ba) / np.where(1 - pc > 0, 1 - pc, 1), 0)
        ba = p_apto * resto[:, None]
        ba[:, c] = pc_ba
        ba[1 - pc <= 0, c] = 1
    mezcla = (1 - frac_mf) * ba
    mezcla[:, c] += frac_mf
    return mezcla


def resumen(x):
    return dict(media=float(np.mean(x)), p5=float(np.percentile(x, 5)), p95=float(np.percentile(x, 95)))


def priors_arquetipo(rng, nombre, pos, bloque, viv, alfas, ut, f_mf, factor_hab, restar=False):
    """Priors de un arquetipo: filas para el CSV y parámetros para el JSON."""
    tipo = "casa" if pos == "casa" else "apartamento"
    filas, js = [], {"posicion": pos, "bloque": bloque, "celda_ecv": f"{tipo}|{bloque}"}
    n = N_SORTEOS
    cl = P["masa_iso13790"]["clases"]
    a = P["absortancia"]

    def fila(param, unidad, valores, dist, fuente, **extra):
        filas.append(dict(arquetipo=nombre, parametro=param, unidad=unidad, distribucion=dist, fuente=fuente,
                          **resumen(valores), **extra))

    # materiales (proporciones de la celda)
    prop = {}
    for var in ["paredes", "pisos", "techo"]:
        alfa = alfas[(var, tipo, bloque)]
        prop[var] = dirichlet(rng, alfa, n)
        js[var] = {"alfa": dict(zip(CATEGORIAS[var], np.round(alfa, 4).tolist()))}
    frac_mf = float((viv["tipo"] == "multifamiliar").mean())
    techo_expuesto = pos in ("casa", "ultimo_piso")
    if pos == "ultimo_piso":
        prop["techo"] = techo_s6(prop["techo"], f_mf[bloque], frac_mf, restar)
        js["techo"]["s6"] = {"regla": N5["a8"] if restar else N5["techo_ultimo_piso"],
                             "frac_multifamiliar_arquetipo": round(frac_mf, 4)}
    for var in (["techo"] if techo_expuesto else []) + ["paredes", "pisos"]:
        for j, cat in enumerate(CATEGORIAS[var]):
            fila(f"{var}: {cat}", "fracción", prop[var][:, j], "Dirichlet" + (" con S6" if var == "techo" and
                                                                                pos == "ultimo_piso" else ""),
                 f"ECV, celda {tipo}|{bloque}")
    if not techo_expuesto:
        js.pop("techo")

    # material de cada sorteo
    muro = np.array(CATEGORIAS["paredes"])[sortear_categoria(rng, prop["paredes"])]
    if techo_expuesto:
        techo = np.array(CATEGORIAS["techo"])[sortear_categoria(rng, prop["techo"])]
        u_t = np.empty(n)
        a_t = np.empty(n)
        for mat in CATEGORIAS["techo"]:
            k = techo == mat
            u_t[k] = tri(rng, ut.loc[mat, ["U_min", "U_moda", "U_max"]].to_list(), k.sum())
            a_t[k] = tri(rng, [a["techo"]["min"], a["techo"]["moda"][mat], a["techo"]["max"]], k.sum())
        fila("U del techo", "W/m²K", u_t, "mezcla de triangulares por material", "ISO 6946; ver propiedades")
        fila("absortancia del techo", "-", a_t, "mezcla de triangulares por material", "CEELA y supuesto de color")
        liviano = techo != "concreto"
    else:
        liviano = np.zeros(n, bool)
    clave = f"{tipo}|{bloque}"
    mamp = P["muros"]["mamposteria"]
    u_m = np.where(muro == "mamposteria", tri(rng, [mamp["min"], mamp["moda"][clave], mamp["max"]], n),
                   tri(rng, P["muros"]["otro"], n))
    fila("U del muro", "W/m²K", u_m, "mezcla de triangulares por material", "CEELA (mampostería); supuesto (otro)")
    js["U_muro"] = {"mamposteria": [mamp["min"], mamp["moda"][clave], mamp["max"]], "otro": P["muros"]["otro"]}
    fila("absortancia del muro", "-", tri(rng, a["muro"], n), "triangular", "ASHRAE y Paso 3")
    js["absortancia_muro"] = a["muro"]

    # capacidad: clase de masa según el muro y lo que hay encima
    m = P["masa_iso13790"]
    rangos = {"muro_otro": m["muro_otro"], "techo_liviano": m["techo_liviano"], "losa_encima": m["losa_encima"]}
    caso = np.where(muro == "otro", "muro_otro", np.where(liviano, "techo_liviano", "losa_encima"))
    cm = np.empty(n)
    for c, clases in rangos.items():
        k = caso == c
        cm[k] = tri(rng, [cl[x][0] for x in clases], k.sum())
    fila("capacidad C_m", "kJ/K por m² de piso", cm, "mezcla de triangulares por construcción", "ISO 13790, Tabla 12")
    js["capacidad"] = {c: {"clases": rangos[c], "kJ_K_m2": [cl[x][0] for x in rangos[c]],
                           "A_m_por_A_piso": cl[rangos[c][1]][1]} for c in rangos}

    # infiltración con las ventanas cerradas (Nota 7): construcción abierta si el techo es liviano o el muro es de
    # otro material; cerrada si hay losa encima
    abierta = caso != "losa_encima"
    ach = np.empty(n)
    for grupo, sel in [("abierta", abierta), ("cerrada", ~abierta)]:
        mediana, sigma = INFILTRACION[grupo]
        ach[sel] = rng.lognormal(np.log(mediana), sigma, sel.sum())
    fila("infiltración", "renovaciones por hora", ach, "mezcla de lognormales por construcción",
         "Mathur y Damle 2021 (cerrada); Rodrigues et al. 2021 y supuesto (abierta)")
    js["infiltracion_ventanas_cerradas"] = {
        "regla": "abierta si el techo es liviano o el muro es de otro material; cerrada si hay losa encima",
        **{g: {"mediana": round(m, 4), "sigma_log": round(s, 4)} for g, (m, s) in INFILTRACION.items()}}
    if techo_expuesto:
        js["U_techo"] = {mat: ut.loc[mat, ["U_min", "U_moda", "U_max"]].round(3).to_list() for mat in CATEGORIAS["techo"]}
        js["absortancia_techo"] = {mat: [a["techo"]["min"], a["techo"]["moda"][mat], a["techo"]["max"]]
                                   for mat in CATEGORIAS["techo"]}

    # ventanas, sombra y fracción climatizada (CEELA)
    ven = P["ventanas"]
    wwr = ven["wwr"]["5-6"] if bloque == "5-6" else ven["wwr"].get(clave, ven["wwr"]["amplio"])
    sombra = ven["sombra"]["ninguno"] if clave == "casa|1-2" else ven["sombra"]["balcones"]
    for param, unidad, lmm, fuente in [("relación ventana-muro", "-", wwr, "CEELA (ampliado en 1-2 y 3-4)"),
                                       ("U de la ventana", "W/m²K", ven["U"], "CEELA; ± 10 % supuesto"),
                                       ("factor solar del vidrio", "-", ven["g"], "supuesto"),
                                       ("factor de sombra", "-", sombra, "CEELA (tipo de sombra) y supuesto")]:
        fila(param, unidad, tri(rng, lmm, n), "triangular", fuente, minimo=lmm[0], moda=lmm[1], maximo=lmm[2])
    js.update({"relacion_ventana_muro": wwr, "U_ventana": ven["U"], "factor_solar": ven["g"], "factor_sombra": sombra})

    zona = P["climatizada"]["zona"].get(bloque, P["climatizada"]["zona"].get(clave))
    muestra = viv.sample(n, replace=True, random_state=SEMILLA)
    area = muestra["area_construida"].to_numpy(float)
    hab = muestra["total_habitaciones"].fillna(1).clip(lower=1).to_numpy(float)
    if zona == "toda":
        f = tri(rng, P["climatizada"]["toda"], n)
    else:
        # Nota 6: las habitaciones del catastro, llevadas a los dormitorios medios de la ECV de su estrato
        n_hab = (np.maximum(1, hab * muestra["estrato_num"].map(factor_hab).to_numpy())
                 if zona == "habitaciones" else 1.0)
        f = np.minimum(1, n_hab * tri(rng, P["climatizada"]["A_hab_m2"], n) / area)
    fila("fracción climatizada", "-", f, f"regla «{zona}» sobre las viviendas del arquetipo", "CEELA y supuesto de área",
         zona=zona)
    js["climatizada"] = {"zona": zona, "A_hab_m2": P["climatizada"]["A_hab_m2"], "toda": P["climatizada"]["toda"]}
    if zona == "habitaciones":
        js["climatizada"]["factor_habitaciones_por_estrato"] = {str(e): round(x, 4) for e, x in factor_hab.items()}
    return filas, js


# ---------------------------------------------------------------- figura

def figura(prop, decision):
    colores = {"concreto": GREY, "asbesto_cemento": PET, "metalica_zinc": OCH, "otro": PALE}
    t = prop[prop.variable == "techo"]
    fig, ax = lienzo(16, 8)
    etiquetas, y = [], 0
    for tipo in TIPOS_ECV:
        for bloque in BLOQUES:
            for anio in [2019, 2024]:
                g = t[(t.tipo == tipo) & (t.bloque == bloque) & (t.anio == anio)].set_index("categoria")
                izq = 0
                for cat in CATEGORIAS["techo"]:
                    val = g.loc[cat, "p"] * 100
                    ax.barh(y, val, left=izq, color=colores[cat], edgecolor=INK if cat == "otro" else "none",
                            linewidth=0.3, height=0.8, label=ETIQUETA[cat] if y == 0 else None)
                    if val >= 8:
                        ax.text(izq + val / 2, y, f"{val:.0f}", ha="center", va="center", fontsize=6.5,
                                color="white" if cat in ("asbesto_cemento", "metalica_zinc") else INK)
                    izq += val
                n = int(g["n"].iloc[0])
                etiquetas.append(f"{'Casa' if tipo == 'casa' else 'Apartamento'}, E{bloque} · {anio} (n = {n})")
                y += 1
            y += 0.5
    pos = [i + 0.5 * (i // 2) for i in range(len(etiquetas))]
    ax.set_yticks(pos, etiquetas)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel("Viviendas (%)")
    ax.legend(ncols=4, loc="upper center", bbox_to_anchor=(0.5, -0.12), frameon=False)
    nota = "olas juntas" if decision["techo"] == "juntar" else "solo 2024"
    ax.set_title(f"Material del techo según la ECV, por tipo de vivienda y bloque de estratos (prior: {nota})",
                 fontsize=8, loc="left", color=INK)
    guardar(fig, FIGURAS / "env_techo_ecv.png")


# ---------------------------------------------------------------- principal

def main():
    rng = np.random.default_rng(SEMILLA)
    olas, excluidas = {}, {}
    for anio in P["ecv"]["olas"]:
        olas[anio], excluidas[anio] = ecv(anio)
        print(f"ECV {anio}: {len(olas[anio])} viviendas con estrato 1-6; {excluidas[anio]} excluidas sin estrato")

    deff_crudo, deff = efectos_diseno(olas[2024])
    print("Efecto de diseño de 2024 por variable y tipo (usado):",
          {f"{v}|{t}": f"{deff_crudo[(v, t)]:.2f} ({x:.2f})" for (v, t), x in deff.items()})
    prueba, decision, sens = pruebas(olas, deff)
    prueba.to_csv(TABLAS / "env_rao_scott.csv", index=False, encoding="utf-8-sig")
    print("\nRao-Scott:\n", prueba.round(3).to_string())
    print("Decisión:", decision, "| con la varianza de 2019 × d:", sens)

    prop, diri = celdas(olas, decision, deff)
    prop.to_csv(TABLAS / "env_ecv_proporciones.csv", index=False, encoding="utf-8-sig")
    diri.to_csv(TABLAS / "env_dirichlet_celdas.csv", index=False, encoding="utf-8-sig")
    por_estrato(olas).to_csv(TABLAS / "env_ecv_por_estrato.csv", index=False, encoding="utf-8-sig")

    ut = u_techos()
    print("\nU de techos (ISO 6946):\n", ut.round(2).to_string())
    tabla_propiedades(ut).to_csv(TABLAS / "env_propiedades_materiales.csv", index=False, encoding="utf-8-sig")

    v = cargar_viviendas()
    arq = pd.read_parquet(INTERNOS / "arquetipos_final.parquet")
    apto = v["posicion"].isin(["ultimo_piso", "sin_cubierta"])
    f_mf = (v.loc[apto, "tipo"] == "multifamiliar").groupby(v.loc[apto, "bloque"]).mean().to_dict()
    factor_hab = factor_habitaciones(v)
    print("Nota 6, dormitorios de la ECV / habitaciones del catastro en apartamentos, por estrato:",
          {e: round(x, 3) for e, x in factor_hab.items()})
    print("\nFracción de multifamiliares entre las viviendas que no son casa, por bloque:", {k: round(x, 3) for k, x in f_mf.items()})
    (TABLAS / "env_decision_olas.json").write_text(json.dumps(
        {"olas_por_variable": decision, "olas_si_2019_usara_el_deff_de_la_variable": sens,
         "deff_2024_variable_tipo": {f"{v}|{t}": round(x, 3) for (v, t), x in deff_crudo.items()},
         "deff_usado_nota5": {f"{v}|{t}": round(x, 3) for (v, t), x in deff.items()},
         "nota6_factor_habitaciones_apartamentos": {str(e): round(x, 4) for e, x in factor_hab.items()},
         "viviendas_excluidas_sin_estrato": excluidas,
         "viviendas_por_ola": {a: len(d) for a, d in olas.items()},
         "f_multifamiliar_por_bloque": {k: round(x, 4) for k, x in f_mf.items()}}, ensure_ascii=False, indent=2),
        encoding="utf-8")

    for sol in SOLUCIONES:
        for alternativa in ["usada", "a7", "a8"]:
            d = diri[diri.alternativa == alternativa]
            alfas = {(var, t, b): g.set_index("categoria").loc[CATEGORIAS[var], "alfa"].to_numpy()
                     for (var, t, b), g in d.groupby(["variable", "tipo", "bloque"])}
            filas, js = [], {}
            for nombre in sorted(arq[sol].unique()):
                viv = v[arq[sol] == nombre]
                pos, bloque = viv["posicion"].astype(str).iloc[0], viv["bloque"].iloc[0]
                assert viv["posicion"].nunique() == 1 and viv["bloque"].nunique() == 1, nombre
                f, j = priors_arquetipo(rng, nombre, pos, bloque, viv, alfas, ut, f_mf, factor_hab,
                                        restar=alternativa == "a8")
                filas += f
                js[nombre] = j
            tabla = pd.DataFrame(filas)
            if alternativa == "usada":
                tabla.to_csv(TABLAS / f"env_priors_{sol}.csv", index=False, encoding="utf-8-sig")
                (TABLAS / f"env_priors_{sol}.json").write_text(json.dumps(
                    {"preregistro": "versión 4, sección 9, con la Nota 5", "olas": decision,
                     "deff": {f"{v}|{t}": round(x, 3) for (v, t), x in deff.items()}, "arquetipos": js},
                    ensure_ascii=False,
                    indent=1), encoding="utf-8")
                print(f"\nPriors {sol} (techo y fracción climatizada):")
                sel = tabla[tabla.parametro.str.startswith("techo:") | tabla.parametro.isin(
                    ["U del techo", "U del muro", "capacidad C_m", "fracción climatizada"])]
                print(sel.pivot(index="arquetipo", columns="parametro", values="media").round(3).to_string())
            else:
                tabla[tabla.parametro.str.startswith("techo:") | (tabla.parametro == "U del techo")].to_csv(
                    TABLAS / f"env_{alternativa}_{sol}.csv", index=False, encoding="utf-8-sig")
    figura(prop, decision)


if __name__ == "__main__":
    main()
