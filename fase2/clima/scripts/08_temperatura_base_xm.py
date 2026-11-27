"""Temperatura base de los grados-hora de enfriamiento estimada con la demanda diaria de XM.

Con el SUI mensual (script 04) la base queda mal identificada: el R² casi no cambia entre 24 y 32 °C, porque 120 meses
con efectos fijos de año dejan poca variación del calor. Aquí se usa la demanda diaria del mercado regulado de Air-e
(CARIBE SOL, 2021–2025), con los mismos días excluidos, el mismo calendario y los mismos efectos fijos año-mes que la
compuerta horaria (Ecuación 10), de modo que la base sale de la variación del calor entre días del mismo mes:

    100·ln L_d = β·CDH_d(T_b) + γ·(tipo de día) + δ_(año-mes) + ε_d,   CDH_d(T_b) = Σ_h max(0, HI_h − T_b)

Para cada T_b de 22 a 34 °C (paso de 0,1 °C) se ajusta por mínimos cuadrados y se elige la base con menor suma de
cuadrados de los residuos (punto de quiebre, como en PRISM). El intervalo de T_b se obtiene con un bootstrap por bloques
de año-mes (los efectos fijos se reestiman en cada réplica). Variantes de robustez:
  - temperatura del aire en lugar del índice de calor;
  - grados-hora del día anterior además de los del día (inercia de las viviendas y de los hábitos);
  - índice de calor sin el salto de la fórmula de la NOAA cerca de 26,7 °C (punto 9 de los datos sospechosos);
  - solo días hábiles; sin excluir los días con cortes; con vacaciones escolares como control;
  - índice de calor medido por el IDEAM (días con las 24 horas); Electricaribe (agente EDIC, siete departamentos) en
    2017–2019.
Como la base que mejor ajusta puede quedar por debajo de todo el rango observado, solo su cota superior tiene sentido.
Además se prueba si la respuesta es lineal: deciles del HI medio diario, término cuadrático, dos pendientes y dos bases
horarias (capítulo 29_temperatura_base.md).

Limitaciones: XM mide todo el mercado regulado de Atlántico, Magdalena y La Guajira, con comercio pequeño incluido, y el
clima es el de la celda de Barranquilla. La base es la del agregado, no la de cada estrato ni la de un equipo.

Uso (entorno de la compuerta, que tiene holidays):
    ../../../compuerta_horaria/.venv/Scripts/python.exe scripts/08_temperatura_base_xm.py
Salidas (salidas/):
  tbase_xm_perfil.csv     SSE, R² parcial del calor y β por base y variante
  tbase_xm_forma.csv      respuesta por decil del HI y de la temperatura medios del día (IC 95 % HAC)
  tbase_xm_resumen.json   base, cotas, IC bootstrap, β y pruebas de forma
  tbase_xm_perfil.png     (a) R² parcial según la base; (b) respuesta por decil
"""
import importlib.util
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
SALIDAS = RAIZ / "salidas"
ML = next(p for p in RAIZ.parents if (p / "compuerta_horaria").exists())  # ml_trabajo
COMPUERTA = ML / "compuerta_horaria" / "scripts"
sys.path.insert(0, str(COMPUERTA))
_spec = importlib.util.spec_from_file_location("estimar", COMPUERTA / "03_estimar.py")
est = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(est)
from comun import calendario, indice_calor  # noqa: E402

SEMILLA = 42
BASES = np.round(np.arange(18.0, 36.001, 0.1), 1)
B_BOOT = 500


# ---------------------------------------------------------------- clima
def hi_suave(t_c, hr):
    """Índice de calor de la NOAA sin el salto: mezcla lineal entre Steadman y Rothfusz en ±1 °F del umbral de 80 °F."""
    t = np.asarray(t_c, float) * 9 / 5 + 32
    simple = 0.5 * (t + 61.0 + (t - 68.0) * 1.2 + np.asarray(hr, float) * 0.094)
    # Rothfusz con el ajuste por humedad alta (en Barranquilla la HR nunca baja de 13 %), mezclado con Steadman
    # según el mismo promedio con que la NOAA elige la fórmula.
    rh = np.asarray(hr, float)
    hi = (-42.379 + 2.04901523 * t + 10.14333127 * rh - 0.22475541 * t * rh
          - 6.83783e-3 * t ** 2 - 5.481717e-2 * rh ** 2 + 1.22874e-3 * t ** 2 * rh
          + 8.5282e-4 * t * rh ** 2 - 1.99e-6 * t ** 2 * rh ** 2)
    aj_humedo = ((rh - 85) / 10) * ((87 - t) / 5)
    hi = np.where((rh > 85) & (t >= 80) & (t <= 87), hi + aj_humedo, hi)
    m = (simple + t) / 2
    w = np.clip((m - 79.0) / 2.0, 0, 1)  # 0 por debajo de 79 °F, 1 por encima de 81 °F
    return ((1 - w) * simple + w * hi - 32) * 5 / 9


def clima_diario():
    s = pd.read_parquet(SALIDAS / "clima_horario_barranquilla.parquet")
    if "hora_local" not in s.columns:
        s = s.reset_index()
    s["hora_local"] = pd.to_datetime(s["hora_local"])
    # cada fila es la hora que termina en hora_local; el día es el de su inicio (00-01 h es la hora 0 del día)
    s["fecha"] = (s["hora_local"] - pd.Timedelta(hours=1)).dt.normalize()
    s["HI_suave"] = hi_suave(s["T"].to_numpy(), s["HR"].to_numpy())
    cuenta = s.groupby("fecha").size()
    s = s[s["fecha"].isin(cuenta.index[cuenta == 24])]
    return s


def cdh(s, var, bases):
    """Grados-hora diarios (°C·h) sobre cada base."""
    x = s[var].to_numpy()[:, None] - bases[None, :]
    d = pd.DataFrame(np.clip(x, 0, None), index=s["fecha"], columns=bases)
    return d.groupby(level=0).sum()


# ---------------------------------------------------------------- demanda
def demanda(codigo, excluir_dna=True):
    if codigo == "CARIBE SOL":
        reg, total = est.serie_mercado()
        anios = est.ANIOS
    else:
        reg = est.serie_agentes(["EDIC"], ["DemaComeReg"])
        reg = reg[reg.index >= "2017-01-14"]
        mc = pd.read_parquet(est.PROC / "xm_mercados_horario.parquet")
        mc["fecha"] = pd.to_datetime(mc["fecha"])
        total = mc[mc["codigo"] == "COSTA CARIBE"].groupby(["fecha", "hora"])["kwh"].sum().unstack()
        anios = [2017, 2018, 2019]
    cal = calendario(reg.index)
    excluir = est.marcar_anomalias(reg, cal).any(axis=1)
    if excluir_dna:
        excluir = excluir | (est.dias_dna(total) > est.UMBRAL_DNA).reindex(reg.index).fillna(False)
    L = reg.sum(axis=1)
    L = L[~excluir & L.index.year.isin(anios)]
    df = pd.DataFrame({"y": 100 * np.log(L)}).join(cal)
    df["anio_mes"] = df.index.strftime("%Y-%m")
    return df


def controles(df):
    X = pd.DataFrame(index=df.index)
    X["sabado"] = (df["tipo_dia"] == "sabado").astype(float)
    X["dom_fest"] = (df["tipo_dia"] == "dom_fest").astype(float)
    for c in ["fin_anio", "carnaval", "semana_santa", "vacaciones"]:
        if c in df:
            X[c] = df[c].astype(float)
    fe = pd.get_dummies(df["anio_mes"], prefix="m", dtype=float)
    X = pd.concat([X, fe], axis=1)
    return X.loc[:, (X.std() > 0) | X.columns.str.startswith("m_")]


# ---------------------------------------------------------------- perfil
def residualizar(Z, A):
    """Residuo de cada columna de A tras proyectar sobre Z (Frisch-Waugh-Lovell)."""
    coef, *_ = np.linalg.lstsq(Z, A, rcond=None)
    return A - Z @ coef


def perfil(y, Z, C, extra=None):
    """SSE, β y R² dentro de mes para cada base. C: matriz días × bases de grados-hora; extra: idem del día anterior."""
    ry = residualizar(Z, y[:, None])[:, 0]
    rc = residualizar(Z, C)
    sst = float(ry @ ry)
    sse, beta = np.empty(C.shape[1]), np.empty(C.shape[1])
    if extra is None:
        num = rc.T @ ry
        den = (rc * rc).sum(0)
        con = den > 1e-9 * den.max()  # bases por encima de toda la serie: sin variación
        beta = np.where(con, num / np.where(con, den, 1), np.nan)
        sse = np.where(con, sst - num ** 2 / np.where(con, den, 1), np.nan)
    else:
        re = residualizar(Z, extra)
        for j in range(C.shape[1]):
            if np.ptp(rc[:, j]) < 1e-9:
                sse[j] = beta[j] = np.nan
                continue
            X = np.column_stack([rc[:, j], re[:, j]])
            b, *_ = np.linalg.lstsq(X, ry, rcond=None)
            r = ry - X @ b
            sse[j], beta[j] = r @ r, b[0]
    return sse, beta, 1 - sse / sst, sst


def lineal_hi(y, Z, hi):
    ry = residualizar(Z, y[:, None])[:, 0]
    rh = residualizar(Z, hi[:, None])[:, 0]
    b = (rh @ ry) / (rh @ rh)
    r = ry - b * rh
    return float(r @ r), float(b)


def bootstrap(y, Z, C, meses, n_cal, extra=None, b_total=B_BOOT):
    """T_b de cada réplica; las n_cal primeras columnas de Z son el calendario y el resto los efectos año-mes."""
    rng = np.random.default_rng(SEMILLA)
    unicos = np.unique(meses)
    grupos = {m: np.flatnonzero(meses == m) for m in unicos}
    out = np.empty(b_total)
    for b in range(b_total):
        sel = rng.choice(unicos, size=len(unicos), replace=True)
        idx = np.concatenate([grupos[m] for m in sel])
        # cada copia de un mes recibe su propio efecto fijo
        etiqueta = np.concatenate([np.full(len(grupos[m]), i) for i, m in enumerate(sel)])
        fe = (etiqueta[:, None] == np.arange(len(sel))[None, :]).astype(float)
        Zb = np.column_stack([Z[idx][:, :n_cal], fe])
        sse, *_ = perfil(y[idx], Zb, C[idx], None if extra is None else extra[idx])
        out[b] = BASES[int(np.nanargmin(sse))]
    return out


def correr(nombre, df, s, var="HI", lag=False, boot=True):
    C_all = cdh(s, var, BASES)
    hi_d = s.groupby("fecha")[var].mean()
    d = df.join(C_all, how="inner")
    d = d[d.index.isin(hi_d.index)]
    if lag:
        prev = C_all.shift(1, freq="D").reindex(d.index)
        ok = prev.notna().all(axis=1)
        d, prev = d[ok], prev[ok]
    X = controles(d)
    y = d["y"].to_numpy()
    Z = X.to_numpy()
    C = d[BASES].to_numpy()
    sse, beta, r2, sst = perfil(y, Z, C, prev.to_numpy() if lag else None)
    j = int(np.nanargmin(sse))
    sse_lin, b_lin = lineal_hi(y, Z, hi_d.reindex(d.index).to_numpy())
    # fracción de horas por encima de la base estimada en los días de la muestra
    horas = s[s["fecha"].isin(d.index)][var]
    res = {"variante": nombre, "dias": int(len(d)), "T_b": float(BASES[j]),
           "beta_pct_por_100_CDH": round(100 * float(beta[j]), 4),
           "R2_dentro_mes": round(float(r2[j]), 4),
           "R2_dentro_mes_lineal_media_diaria": round(1 - sse_lin / sst, 4),
           "beta_lineal_pct_por_C": round(b_lin, 3),
           "horas_sobre_T_b_pct": round(100 * float((horas > BASES[j]).mean()), 1),
           "rango_horario_variable": [round(float(horas.quantile(q)), 2) for q in (0.01, 0.5, 0.99)]}
    # intervalo por perfil: bases cuya SSE no supera la mínima en más de un χ²(1) al 95 % (aproximado, sin HAC)
    n, p = len(y), Z.shape[1] + (2 if lag else 1)
    tope = sse[j] * (1 + 3.84 / (n - p))
    dentro = BASES[sse <= tope]
    res["IC_perfil_aprox"] = [float(dentro.min()), float(dentro.max())]
    if boot:
        n_cal = int((~X.columns.str.startswith("m_")).sum())
        bb = bootstrap(y, Z, C, d["anio_mes"].to_numpy(), n_cal, prev.to_numpy() if lag else None)
        res["IC95_bootstrap_meses"] = [float(np.quantile(bb, 0.025)), float(np.quantile(bb, 0.975))]
        res["bootstrap_mediana"] = float(np.median(bb))
    tabla = pd.DataFrame({"variante": nombre, "T_b": BASES, "sse": sse, "R2_dentro_mes": r2,
                          "beta_pct_por_100_CDH": 100 * beta})
    print(json.dumps(res, ensure_ascii=False), flush=True)
    return res, tabla


def clima_ideam():
    """HI horario del IDEAM (aeropuerto), solo días con las 24 horas: variante con el clima medido."""
    ide = pd.read_parquet(est.PROC / "ideam_horario.parquet").dropna(subset=["hi_ideam"])
    s = pd.DataFrame({"fecha": ide.index.normalize(), "HI": ide["hi_ideam"].to_numpy()})
    cuenta = s.groupby("fecha").size()
    return s[s["fecha"].isin(cuenta.index[cuenta == 24])].reset_index(drop=True)


def hac(y, regs, X, lags=est.HAC_LAGS):
    import statsmodels.api as sm
    A = pd.concat([regs, X], axis=1)
    return sm.OLS(y, A).fit(cov_type="HAC", cov_kwds={"maxlags": lags})


def forma(df, s, var="HI"):
    """¿Es lineal la respuesta? Respuesta por deciles del HI medio diario, término cuadrático, dos pendientes en el
    HI medio y dos bases en los grados-hora horarios. Los p de las dos últimas son optimistas, porque el corte se
    elige con los mismos datos."""
    hi_d = s.groupby("fecha")[var].mean().rename("hi")
    d = df.join(hi_d, how="inner")
    X = controles(d)
    y = d["y"]
    out = {}
    lin = hac(y, d[["hi"]], X)
    out["lineal"] = {"beta_pct_por_C": round(lin.params["hi"], 3),
                     "IC95_HAC": [round(v, 3) for v in lin.conf_int().loc["hi"]]}
    # deciles del HI medio diario (referencia: el primero)
    dec = pd.qcut(d["hi"], 10, labels=False)
    D = pd.get_dummies(dec, prefix="dec", dtype=float).drop(columns="dec_0")
    fd = hac(y, D, X)
    ci = fd.conf_int()
    tabla = pd.DataFrame({"decil": range(10), "hi_medio": d.groupby(dec)["hi"].mean().to_numpy(),
                          "dias": d.groupby(dec).size().to_numpy(),
                          "efecto_pct": [0.0] + [fd.params[f"dec_{k}"] for k in range(1, 10)],
                          "ic_inf": [0.0] + [ci.loc[f"dec_{k}", 0] for k in range(1, 10)],
                          "ic_sup": [0.0] + [ci.loc[f"dec_{k}", 1] for k in range(1, 10)]})
    # pendiente entre deciles consecutivos (% por °C)
    tabla["pendiente_tramo"] = tabla["efecto_pct"].diff() / tabla["hi_medio"].diff()
    # término cuadrático
    c = d["hi"] - d["hi"].mean()
    fq = hac(y, pd.DataFrame({"c": c, "c2": c ** 2}), X)
    out["cuadratico"] = {"coef_c2": round(fq.params["c2"], 4), "p": round(fq.pvalues["c2"], 4)}
    # dos pendientes en el HI medio diario
    mejor = None
    for k in np.round(np.arange(*d["hi"].quantile([0.1, 0.9]).to_numpy(), 0.1), 1):
        f2 = hac(y, pd.DataFrame({"hi": d["hi"], "sobre": (d["hi"] - k).clip(lower=0)}), X)
        if mejor is None or f2.ssr < mejor[1].ssr:
            mejor = (float(k), f2)
    k, f2 = mejor
    out["dos_pendientes_hi_medio"] = {"corte": k, "pendiente_bajo": round(f2.params["hi"], 3),
                                      "pendiente_sobre": round(f2.params["hi"] + f2.params["sobre"], 3),
                                      "p_cambio_optimista": round(f2.pvalues["sobre"], 4),
                                      "R2_ganancia": round((lin.ssr - f2.ssr) / lin.centered_tss, 5)}
    # dos bases en los grados-hora horarios: todas las horas y las horas sobre un umbral alto
    mejor = None
    for k in np.arange(27.0, 36.01, 0.5):
        C = cdh(s, var, np.array([18.0, k])).reindex(d.index)
        C.columns = ["cdh_todas", "cdh_sobre"]
        f3 = hac(y, C, X)
        if mejor is None or f3.ssr < mejor[1].ssr:
            mejor = (float(k), f3)
    k, f3 = mejor
    out["dos_bases_horarias"] = {"umbral_alto": k,
                                 "pct_por_100_CDH_todas": round(100 * f3.params["cdh_todas"], 3),
                                 "pct_por_100_CDH_extra_sobre_umbral": round(100 * f3.params["cdh_sobre"], 3),
                                 "p_optimista": round(f3.pvalues["cdh_sobre"], 4)}
    # temperatura más baja de cada día
    minimo = s.groupby("fecha")[var].min().reindex(d.index)
    out["minimo_diario"] = {"percentiles_5_50_95": [round(float(minimo.quantile(q)), 2) for q in (0.05, 0.5, 0.95)],
                            "dias_con_alguna_hora_bajo_25.1_pct": round(100 * float((minimo < 25.1).mean()), 1)}
    return out, tabla


def main():
    s = clima_diario()
    vac = s.groupby("fecha")["vacaciones_escolares"].first().rename("vacaciones")
    sol = demanda("CARIBE SOL")
    sol_dna = demanda("CARIBE SOL", excluir_dna=False)
    sol_vac = sol.join(vac, how="inner")
    habiles = sol[(sol["tipo_dia"] == "laboral") & ~sol[["fin_anio", "carnaval", "semana_santa"]].any(axis=1)]
    elec = demanda("EDIC")
    ide = clima_ideam()
    print(f"días CARIBE SOL: {len(sol)}; con DNA: {len(sol_dna)}; EDIC 2017-2019: {len(elec)}", flush=True)

    corridas = [
        correr("principal: HI, CARIBE SOL 2021-2025", sol, s),
        correr("temperatura del aire", sol, s, var="T"),
        correr("HI con grados-hora del día anterior", sol, s, lag=True),
        correr("HI sin el salto de la fórmula", sol, s, var="HI_suave"),
        correr("solo días hábiles", habiles, s, boot=False),
        correr("sin excluir días con cortes (DNA)", sol_dna, s, boot=False),
        correr("con vacaciones escolares", sol_vac, s, boot=False),
        correr("HI medido por el IDEAM (días completos)", sol, ide, boot=False),
        correr("Electricaribe (EDIC) 2017-2019", elec, s),
    ]
    resumen = {"variantes": [r for r, _ in corridas]}
    tabla = pd.concat([t for _, t in corridas])
    tabla.round(6).to_csv(SALIDAS / "tbase_xm_perfil.csv", index=False)

    f_hi, t_hi = forma(sol, s)
    f_t, t_t = forma(sol, s, var="T")
    resumen["forma_HI"], resumen["forma_T"] = f_hi, f_t
    t_hi.insert(0, "variable", "HI")
    t_t.insert(0, "variable", "T")
    pd.concat([t_hi, t_t]).round(4).to_csv(SALIDAS / "tbase_xm_forma.csv", index=False)
    (SALIDAS / "tbase_xm_resumen.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"forma_HI": f_hi, "forma_T": f_t}, ensure_ascii=False, indent=1))
    print(t_hi.round(3).to_string(index=False))

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
    for nombre, t in tabla.groupby("variante", sort=False):
        a1.plot(t["T_b"], t["R2_dentro_mes"], lw=1.4, label=nombre)
    a1.set_xlabel("Temperatura base $T_b$ (°C)")
    a1.set_ylabel("R² parcial del calor (dentro del año-mes)")
    a1.set_title("(a) Ajuste según la base", loc="left", fontsize=10)
    a1.grid(alpha=0.3)
    a1.legend(fontsize=6, frameon=False)
    a2.errorbar(t_hi["hi_medio"], t_hi["efecto_pct"], yerr=[t_hi["efecto_pct"] - t_hi["ic_inf"],
                t_hi["ic_sup"] - t_hi["efecto_pct"]], fmt="o", ms=4, capsize=2, color="#2a6f97")
    b = f_hi["lineal"]["beta_pct_por_C"]
    x0 = t_hi["hi_medio"].iloc[0]
    xs = np.array([t_hi["hi_medio"].min(), t_hi["hi_medio"].max()])
    a2.plot(xs, b * (xs - x0), "--", color="0.4", lw=1, label=f"recta: {b:.2f} % por °C")
    a2.set_xlabel("Índice de calor medio del día (°C), media de cada decil")
    a2.set_ylabel("Demanda frente al decil más fresco (%)")
    a2.set_title("(b) Forma de la respuesta", loc="left", fontsize=10)
    a2.grid(alpha=0.3)
    a2.legend(fontsize=7, frameon=False)
    fig.tight_layout()
    fig.savefig(SALIDAS / "tbase_xm_perfil.png", dpi=200)
    print(pd.DataFrame(resumen["variantes"]).to_string(index=False))


if __name__ == "__main__":
    main()
