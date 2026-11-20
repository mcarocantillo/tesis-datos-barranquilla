"""Análisis de las variables del catastro para los arquetipos (preregistro, Nota 14; análisis complementario A13).

Documenta por qué los arquetipos usan las seis variables de la Sección 7.3, con el mismo esquema del trabajo previo de
predicción del estrato: univariado, bivariado y multivariado, más los usos de las demás variables fuera de los
arquetipos. No cambia la solución final.

  1. Univariado: tipo, cardinalidad, faltantes, ceros, estadísticos, asimetría con y sin logaritmo, frecuencias.
  2. Bivariado: Spearman entre numéricas por posición, Spearman, información mutua y η² de cada variable con la carga,
     V de Cramér entre categóricas y VIF de las numéricas por posición.
  3. Multivariado: R² de cada variable de la variante ampliada desde las seis base, PCA de las numéricas por posición,
     y el agrupamiento final repetido al agregar una sola variable (mismo algoritmo, submuestra, k y semilla).
  4. Fuera de los arquetipos: ocupación del lote de las casas que no están en PH, y tenencia de aire acondicionado en
     la ECV 2024 según el número de sanitarios del hogar, por bloque de estratos y con el diseño muestral.

Uso: python scripts/20_analisis_variables.py
Salidas (solo agregados): salidas/tablas/var_*.csv y salidas/figuras/var_*.png
"""
import importlib.util
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.feature_selection import mutual_info_regression
from sklearn.metrics import adjusted_rand_score

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from src import agrupamiento as ag  # noqa: E402
from src.agrupamiento import Estrato, Modelo, fijar_variables, preparar, submuestra, suma_cuadrados  # noqa: E402
from src.carga import v_cramer  # noqa: E402
from src.comun import (DECISION, FIGURAS, INTERNOS, POSICIONES, SEMILLA, TABLAS, asignar_epoca_faltante,  # noqa: E402
                       cargar_viviendas)
from src.ecv import hogares_2024, numero, razon  # noqa: E402
from src.estilo import BODY, INK, OCH, PALE, PET, guardar, lienzo  # noqa: E402

_spec = importlib.util.spec_from_file_location("sens", RAIZ / "scripts" / "08_sensibilidad_variables.py")
sens = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sens)

S = DECISION["paso7_v5"]["sensibilidad"]
BASE = ag.VARIABLES["base"]
AMPLIADA = ["log_habitaciones", "log_banios", "log_terreno", "vis_vip"]
NUMERICAS = {"area_construida": "Área construida (m²)", "total_plantas": "Pisos de la unidad",
             "planta_ubicacion": "Piso de ubicación", "altura": "Altura de piso (m)",
             "anio_construccion": "Año de construcción", "area_catastral_terreno": "Área del terreno (m²)",
             "total_habitaciones": "Habitaciones", "total_banios": "Baños", "dist_centro_km": "Distancia al centro (km)"}
CATEGORICAS = {"posicion": "Posición frente a la cubierta", "tipo": "Tipo de edificio", "epoca": "Época",
               "ph": "Propiedad horizontal", "vis": "VIS o VIP", "bloque": "Bloque de estratos",
               "estrato_num": "Estrato", "uso": "Uso catastral", "condicion_predio": "Condición del predio",
               "tipo_vivienda": "Tipo de vivienda"}
ROL = {"area_construida": "base", "total_plantas": "base", "planta_ubicacion": "base", "epoca": "base",
       "anio_construccion": "base (como época)", "tipo": "base", "ph": "base", "posicion": "estrato del diseño",
       "bloque": "estrato del diseño", "estrato_num": "estrato del diseño (por bloque)",
       "total_habitaciones": "variante ampliada", "total_banios": "variante ampliada",
       "area_catastral_terreno": "variante ampliada", "vis": "variante ampliada", "altura": "solo carga",
       "dist_centro_km": "no entra", "uso": "define el tipo", "condicion_predio": "define la PH",
       "tipo_vivienda": "define VIS o VIP"}
LEGIBLE = sens.LEGIBLE
N_MI = 50_000
UMBRAL_R2, UMBRAL_VIF = 0.5, 5.0


def base_de_datos():
    v = cargar_viviendas()
    asignar_epoca_faltante(v)
    v["ph"] = v["condicion_predio"].astype(str).str.startswith("PH").map({True: "PH", False: "no PH"})
    v["vis"] = v["tipo_vivienda"].astype(str).str.startswith("Vivienda de Inter").map({True: "VIS o VIP",
                                                                                       False: "no"})
    cc = pd.read_parquet(INTERNOS / "carga_viviendas.parquet")
    v["carga"], v["carga_m2"] = cc["total"].to_numpy(), cc["por_m2"].to_numpy()
    for c in ["posicion", "tipo", "epoca", "bloque", "uso", "condicion_predio", "tipo_vivienda"]:
        v[c] = v[c].astype(str)
    return v


# ---------------------------------------------------------------- 1. univariado

def univariado(v):
    filas = []
    for c, nombre in NUMERICAS.items():
        s = v[c].astype(float)
        sn = s.dropna()
        filas.append(dict(variable=nombre, columna=c, rol=ROL[c], tipo="numérica", cardinalidad=int(s.nunique()),
                          faltantes_pct=round(100 * s.isna().mean(), 2), ceros_pct=round(100 * (s == 0).mean(), 2),
                          minimo=sn.min(), p1=sn.quantile(.01), p25=sn.quantile(.25), mediana=sn.median(),
                          media=round(sn.mean(), 2), p75=sn.quantile(.75), p99=sn.quantile(.99), maximo=sn.max(),
                          asimetria=round(float(stats.skew(sn)), 2),
                          asimetria_log=round(float(stats.skew(np.log1p(sn.clip(lower=0)))), 2)))
    for c, nombre in CATEGORICAS.items():
        s = v[c]
        filas.append(dict(variable=nombre, columna=c, rol=ROL[c], tipo="categórica", cardinalidad=int(s.nunique()),
                          faltantes_pct=round(100 * s.isna().mean(), 2),
                          moda=str(s.mode().iloc[0]), moda_pct=round(100 * s.value_counts(normalize=True).iloc[0], 1)))
    t = pd.DataFrame(filas)
    cat = pd.concat([v[c].value_counts().rename("viviendas").to_frame().assign(
        pct=lambda d: (100 * d["viviendas"] / len(v)).round(2), variable=CATEGORICAS[c]).rename_axis("categoria")
        .reset_index() for c in CATEGORICAS], ignore_index=True)[["variable", "categoria", "viviendas", "pct"]]
    t.to_csv(TABLAS / "var_univariado.csv", index=False, encoding="utf-8-sig")
    cat.to_csv(TABLAS / "var_categoricas.csv", index=False, encoding="utf-8-sig")
    print(t.to_string(index=False))

    fig, axs = lienzo(17, 12)
    fig.clear()
    axs = fig.subplots(3, 3)
    for ax, (c, nombre) in zip(axs.flat, NUMERICAS.items()):
        s = v[c].astype(float).dropna()
        logx = stats.skew(s) > 2 and s.min() > 0
        bins = np.logspace(np.log10(s.quantile(.001)), np.log10(s.quantile(.999)), 40) if logx else 40
        ax.hist(s.clip(upper=s.quantile(.999)), bins=bins, color=PET, edgecolor="white", linewidth=0.3)
        if logx:
            ax.set_xscale("log")
        ax.set_title(nombre + (" (escala log)" if logx else ""), fontsize=7, color=INK)
        ax.tick_params(labelsize=6)
        ax.set_yticks([])
    guardar(fig, FIGURAS / "var_distribuciones.png")


# ---------------------------------------------------------------- 2. bivariado

def vif(x):
    """VIF de cada columna: 1 / (1 − R²) de su regresión sobre las demás."""
    z = (x - x.mean()) / x.std(ddof=0)
    out = {}
    for c in z.columns:
        a = np.column_stack([np.ones(len(z)), z.drop(columns=c).to_numpy()])
        coef, *_ = np.linalg.lstsq(a, z[c].to_numpy(), rcond=None)
        r2 = 1 - ((z[c].to_numpy() - a @ coef) ** 2).sum() / (z[c] ** 2).sum()
        out[c] = 1 / max(1 - r2, 1e-12)
    return out


def bivariado(v):
    rng = np.random.default_rng(SEMILLA)
    num = list(NUMERICAS) + ["carga", "carga_m2"]
    sp = []
    for p in ["todas"] + POSICIONES:
        d = v if p == "todas" else v[v["posicion"] == p]
        m = d[num].astype(float).corr(method="spearman")
        sp += [dict(posicion=p, var1=a, var2=b, rho=round(float(m.loc[a, b]), 3)) for a in num for b in num]
    sp = pd.DataFrame(sp)
    sp.to_csv(TABLAS / "var_spearman.csv", index=False, encoding="utf-8-sig")

    filas = []
    for p in ["todas"] + POSICIONES:
        d = v if p == "todas" else v[v["posicion"] == p]
        mues = d.iloc[rng.choice(len(d), size=min(N_MI, len(d)), replace=False)]
        for c, nombre in {**NUMERICAS, **CATEGORICAS}.items():
            if c in NUMERICAS:
                ok = mues[c].notna().to_numpy()
                xx, disc = mues.loc[ok, [c]].astype(float).to_numpy(), False
            else:
                ok = mues[c].notna().to_numpy()
                xx, disc = pd.factorize(mues.loc[ok, c])[0].reshape(-1, 1), True
            fila = dict(posicion=p, variable=nombre, columna=c)
            for y in ["carga", "carga_m2"]:
                yy = mues.loc[ok, y].to_numpy(float)
                fila[f"mi_{y}"] = round(float(mutual_info_regression(xx, yy, discrete_features=disc,
                                                                     random_state=SEMILLA)[0]), 3)
                if c in NUMERICAS:
                    fila[f"spearman_{y}"] = round(float(d[[c, y]].astype(float).corr(method="spearman").iloc[0, 1]), 3)
                else:
                    g = d[[c, y]].dropna()
                    medias = g.groupby(c)[y].transform("mean")
                    fila[f"eta2_{y}"] = round(float(1 - ((g[y] - medias) ** 2).sum()
                                                    / ((g[y] - g[y].mean()) ** 2).sum()), 3)
            filas.append(fila)
    vc = pd.DataFrame(filas)
    vc.to_csv(TABLAS / "var_vs_carga.csv", index=False, encoding="utf-8-sig")
    print(vc[vc["posicion"] == "todas"].to_string(index=False))

    cats = list(CATEGORICAS)
    cr = [dict(var1=CATEGORICAS[a], var2=CATEGORICAS[b], v_cramer=round(v_cramer(v[a], v[b]), 3))
          for i, a in enumerate(cats) for b in cats[i + 1:]]
    pd.DataFrame(cr).to_csv(TABLAS / "var_cramer.csv", index=False, encoding="utf-8-sig")

    filas = []
    logs = ["area_construida", "total_plantas", "planta_ubicacion", "anio_construccion", "area_catastral_terreno",
            "total_habitaciones", "total_banios", "dist_centro_km"]
    for p in POSICIONES:
        d = v[v["posicion"] == p][logs].astype(float).dropna()
        d = d.loc[:, d.nunique() > 1]
        x = pd.DataFrame({c: (d[c] if c == "anio_construccion" else np.log1p(d[c].clip(lower=0))) for c in d})
        filas += [dict(posicion=p, variable=NUMERICAS[c], vif=round(val, 2)) for c, val in vif(x).items()]
    pd.DataFrame(filas).to_csv(TABLAS / "var_vif.csv", index=False, encoding="utf-8-sig")
    print(pd.DataFrame(filas).to_string(index=False))

    etiquetas = [NUMERICAS[c] for c in NUMERICAS] + ["Carga por vivienda", "Carga por m²"]
    fig, _ = lienzo(17, 7.2)
    fig.clear()
    axs = fig.subplots(1, 3)
    for ax, p in zip(axs, POSICIONES):
        m = sp[sp["posicion"] == p].pivot(index="var1", columns="var2", values="rho").loc[num, num].to_numpy()
        im = ax.imshow(m, cmap="RdBu_r", vmin=-1, vmax=1)
        ax.set_xticks(range(len(num)), etiquetas, rotation=90, fontsize=5)
        ax.set_yticks(range(len(num)), etiquetas if ax is axs[0] else [""] * len(num), fontsize=5)
        ax.set_title({"casa": "Casas", "ultimo_piso": "Último piso", "sin_cubierta": "Sin cubierta"}[p], fontsize=7)
        for i in range(len(num)):
            for j in range(len(num)):
                if not np.isnan(m[i, j]):
                    ax.text(j, i, f"{m[i, j]:.1f}".replace(".", ","), ha="center", va="center", fontsize=3.6,
                            color="white" if abs(m[i, j]) > 0.6 else INK)
    fig.colorbar(im, ax=axs, shrink=0.6, label="ρ de Spearman")
    guardar(fig, FIGURAS / "var_spearman.png")


# ---------------------------------------------------------------- 3. multivariado

def redundancia(v, x):
    """R² de cada variable de la variante ampliada desde las seis base (época, tipo y PH como indicadoras)."""
    filas = []
    for p in POSICIONES:
        m = (v["posicion"] == p).to_numpy()
        xb = x.loc[m, BASE].copy()
        a = pd.get_dummies(xb.assign(epoca_ord=xb["epoca_ord"].astype(str)), columns=["epoca_ord"], drop_first=True,
                           dtype=float)
        a = a.loc[:, a.nunique() > 1]
        a = np.column_stack([np.ones(len(a)), a.to_numpy(float)])
        for c in AMPLIADA:
            y = x.loc[m, c].to_numpy(float)
            coef, *_ = np.linalg.lstsq(a, y, rcond=None)
            sst = ((y - y.mean()) ** 2).sum()
            r2 = 1 - ((y - a @ coef) ** 2).sum() / sst if sst > 0 else np.nan
            filas.append(dict(posicion=p, variable=LEGIBLE[c], r2_desde_base=round(float(r2), 3),
                              redundante=bool(r2 >= UMBRAL_R2)))
    t = pd.DataFrame(filas)
    t.to_csv(TABLAS / "var_redundancia.csv", index=False, encoding="utf-8-sig")
    print(t.to_string(index=False))


def pca(v):
    cols = ["area_construida", "total_plantas", "planta_ubicacion", "anio_construccion", "area_catastral_terreno",
            "total_habitaciones", "total_banios"]
    filas = []
    for p in POSICIONES:
        d = v.loc[v["posicion"] == p, cols].astype(float).dropna()
        d = d.loc[:, d.nunique() > 1]
        z = pd.DataFrame({c: (d[c] if c == "anio_construccion" else np.log1p(d[c].clip(lower=0))) for c in d})
        z = (z - z.mean()) / z.std(ddof=0)
        val, vec = np.linalg.eigh(np.cov(z.to_numpy().T))
        orden = np.argsort(val)[::-1]
        val, vec = val[orden], vec[:, orden]
        for i in range(min(3, len(val))):
            fila = dict(posicion=p, componente=f"CP{i + 1}", varianza_pct=round(100 * val[i] / val.sum(), 1))
            signo = np.sign(vec[np.argmax(np.abs(vec[:, i])), i])
            fila.update({NUMERICAS[c]: round(float(signo * vec[j, i]), 2) for j, c in enumerate(z.columns)})
            filas.append(fila)
    t = pd.DataFrame(filas)
    t.to_csv(TABLAS / "var_pca.csv", index=False, encoding="utf-8-sig")
    print(t.to_string(index=False))


def agregar(v, x, idx, estrato, cargas, finales, final):
    """La solución final repetida al agregar una variable de la variante ampliada a las seis base."""
    filas = []
    for sol in ["por_vivienda", "por_m2"]:
        f = final[sol]
        fijar_variables("base")
        k_est = pd.read_csv(TABLAS / f"arquetipos_{sol}.csv").groupby("estrato_algoritmo").size()
        multi = {e: int(k) for e, k in k_est.items() if k > 1}
        ref = finales[sol].astype(str).to_numpy()
        y = cargas[sol]
        sst = float(((y - y.mean()) ** 2).sum())
        r2_final = 1 - suma_cuadrados(y, ref) / sst
        ruido_base, _ = sens.ruido_por_posicion(v, x, idx)
        en_multi = estrato.isin(list(multi)).to_numpy()
        for extra in [None] + AMPLIADA:
            t0 = time.time()
            ag._candidatas = BASE + ([extra] if extra else [])
            ruido, originales = sens.ruido_por_posicion(v, x, idx, ruido_base)
            etiqueta = ref.astype(object).copy()
            entra = []
            for e, k in multi.items():
                ie = idx[(estrato.loc[idx] == e).to_numpy()]
                est = Estrato(e, x.loc[ie])
                if extra in est.vars:
                    entra.append(e)
                mod = Modelo(f["algoritmo_final"], est, k, np.flatnonzero(~ruido.loc[ie].to_numpy()))
                mask = (estrato == e).to_numpy()
                g = mod.asignar(x.loc[mask])
                cod = pd.crosstab(g, ref[mask]).idxmax(axis=1)
                etiqueta[mask] = cod.reindex(g).to_numpy()
            r2 = 1 - suma_cuadrados(y, etiqueta) / sst
            ari = adjusted_rand_score(ref, etiqueta)
            cambia = etiqueta != ref
            filas.append(dict(solucion=sol, variable_agregada=LEGIBLE[extra].replace("ninguna (control)", "ninguna"),
                              entra_en="; ".join(entra) if extra else "control",
                              atipicos_originales_en=", ".join(originales), R2_final=round(r2_final, 4),
                              R2=round(r2, 4), delta_R2=round(r2 - r2_final, 4), rand_ajustado=round(ari, 4),
                              rand_ajustado_en_esos_estratos=round(adjusted_rand_score(ref[en_multi],
                                                                                       etiqueta[en_multi]), 4),
                              viviendas_que_cambian_pct=round(100 * float(cambia.mean()), 2),
                              cambia_arquetipos=bool(extra and (ari < S["rand_min"]
                                                                or r2 - r2_final <= -S["caida_R2"]))))
            print(f"{sol} + {extra}: R² {r2:.4f}, Rand {ari:.3f}, cambian {100 * cambia.mean():.1f} %, "
                  f"{time.time() - t0:.0f} s", flush=True)
    ag._candidatas = BASE
    t = pd.DataFrame(filas)
    t.to_csv(TABLAS / "var_agregar_una.csv", index=False, encoding="utf-8-sig")
    return t


def figura_agregar(t):
    q = pd.read_csv(TABLAS / "val_sensibilidad_variables.csv", encoding="utf-8-sig")
    q = q[q["aplica"] & (q["variable_quitada"] != "ninguna (control)")]
    fig, axs = lienzo(17, 6.5)
    fig.clear()
    axs = fig.subplots(1, 2, sharey=False)
    for ax, sol, titulo in zip(axs, ["por_vivienda", "por_m2"], ["Carga por vivienda", "Carga por m²"]):
        a = t[(t["solucion"] == sol) & (t["variable_agregada"] != "ninguna")]
        b = q[q["solucion"] == sol]
        nombres = [f"− {n}" for n in b["variable_quitada"]] + [f"+ {n}" for n in a["variable_agregada"]]
        dr = list(b["delta_R2"].fillna(np.nan)) + list(a["delta_R2"])
        colores = [OCH] * len(b) + [PET] * len(a)
        ypos = np.arange(len(nombres))[::-1]
        ax.barh(ypos, dr, color=colores, height=0.6)
        ax.axvline(0, color=INK, linewidth=0.6)
        ax.axvline(-S["caida_R2"], color=BODY, linewidth=0.5, linestyle=":")
        ax.set_yticks(ypos, nombres, fontsize=6)
        ax.set_xlabel("Cambio del R² de la carga frente a la solución final", fontsize=6)
        ax.set_title(titulo, fontsize=7)
        ax.tick_params(labelsize=6)
    guardar(fig, FIGURAS / "var_agregar_quitar.png")


# ---------------------------------------------------------------- 4. fuera de los arquetipos

def ocupacion_lote(v):
    d = v[(v["posicion"] == "casa") & (v["condicion_predio"] == "NPH")].copy()
    d["huella"] = d["area_construida"] / d["total_plantas"].clip(lower=1)
    d["ocupacion"] = d["huella"] / d["area_catastral_terreno"].where(d["area_catastral_terreno"] > 0)
    filas = []
    for b, g in [("todas", d)] + list(d.groupby("bloque")):
        o = g["ocupacion"].dropna()
        filas.append(dict(bloque=b, casas=len(g), con_terreno=len(o), terreno_mediana=g["area_catastral_terreno"].median(),
                          huella_mediana=round(g["huella"].median(), 1), ocupacion_p25=round(o.quantile(.25), 2),
                          ocupacion_mediana=round(o.median(), 2), ocupacion_p75=round(o.quantile(.75), 2),
                          ocupacion_ge_080_pct=round(100 * (o >= 0.8).mean(), 1),
                          ocupacion_gt_1_pct=round(100 * (o > 1.0).mean(), 1),
                          spearman_carga_m2=round(float(g[["ocupacion", "carga_m2"]].corr(method="spearman")
                                                        .iloc[0, 1]), 3)))
    t = pd.DataFrame(filas)
    t.to_csv(TABLAS / "var_ocupacion_lote.csv", index=False, encoding="utf-8-sig")
    print(t.to_string(index=False))


def ecv_sanitarios():
    _, h = hogares_2024(["P5024", "P5010"], ["P1077S11"])
    h["sanitarios"] = numero(h["P5024"])
    h["ac"] = (h["P1077S11"].astype(str).str.strip() == DECISION["paso7_v5"]["hogar"]["codigo_si"]).astype(float)
    h["grupo"] = np.select([h["sanitarios"] <= 1, h["sanitarios"] == 2, h["sanitarios"] >= 3], ["1 o ninguno", "2",
                                                                                                  "3 o más"], "")
    filas = []
    for b in ["todos", "1-2", "3-4", "5-6"]:
        en_b = np.ones(len(h), bool) if b == "todos" else (h["bloque"] == b).to_numpy()
        for gr in ["1 o ninguno", "2", "3 o más"]:
            dom = en_b & (h["grupo"] == gr).to_numpy()
            p, ee = razon(h["ac"], h["w"], dom, h["segmento"])
            filas.append(dict(bloque=b, sanitarios=gr, hogares=int(dom.sum()), con_ac_pct=round(100 * p, 1),
                              ee_pct=round(100 * ee, 1)))
    t = pd.DataFrame(filas)
    t.to_csv(TABLAS / "var_ecv_sanitarios.csv", index=False, encoding="utf-8-sig")
    print(t.to_string(index=False))


def main():
    t0 = time.time()
    v = base_de_datos()
    univariado(v)
    bivariado(v)
    x = preparar(v)
    redundancia(v, x)
    pca(v)
    finales = pd.read_parquet(INTERNOS / "arquetipos_final.parquet")
    final = json.loads((TABLAS / "agr_resultado_final.json").read_text(encoding="utf-8"))
    idx = submuestra(v, np.random.default_rng(SEMILLA))
    estrato = v["posicion"].astype(str) + "|" + v["bloque"]
    cargas = {"por_vivienda": v["carga"].to_numpy(float), "por_m2": v["carga_m2"].to_numpy(float)}
    t = agregar(v, x, idx, estrato, cargas, finales, final)
    print(t.to_string(index=False))
    figura_agregar(t)
    ocupacion_lote(v)
    ecv_sanitarios()
    print(f"tiempo total: {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
