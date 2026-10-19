"""Compuerta horaria: respuesta horaria al calor de la demanda regulada del mercado de Air-e (Ec. 10, propuesta v4).

    100·ln L_{d,h} = a_h + b_h·HI_d + γ_h(tipo de día) + δ_h(año-mes) + ε_{d,h}

Una regresión por hora h (0 = 00:00-01:00, hora local). L es la demanda comercial regulada del mercado CARIBE SOL
(Air-e, con pérdidas) y HI_d el índice de calor medio del día (ERA5-Land, celda de Barranquilla). Con el logaritmo,
b_h se lee como % de cambio de la demanda de la hora h por cada °C de HI_d: compara formas, no niveles. Los efectos
fijos año-mes absorben el crecimiento, la estacionalidad y los cambios de mercado, de modo que b_h sale de la
variación de calor entre días del mismo mes. Errores estándar HAC (Newey-West, 7 rezagos diarios).

γ(tipo de día): sábado y domingo/festivo frente a laboral, más fin de año (24 dic-6 ene), Carnaval y Semana Santa.
Se excluyen 2020 (pandemia) y 2026 (reservado para la prueba ciega), y los días con demanda no atendida relevante
en las subáreas Atlántico o GCM o con horas anómalas (posibles desconexiones o fallas de medida).

Salidas: salidas/b_h_por_hora.csv, salidas/franjas.csv, salidas/estabilidad.csv, salidas/decision.json,
         salidas/b_h_compuerta.png
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import statsmodels.api as sm  # noqa: E402
from scipy import stats  # noqa: E402

from comun import PROC, SALIDAS, calendario  # noqa: E402

HAC_LAGS = 7
NOCHE = [22, 23, 0, 1, 2, 3, 4, 5]
FRANJAS = {"noche (22-5 h)": NOCHE, "mañana (6-11 h)": list(range(6, 12)),
           "tarde (12-17 h)": list(range(12, 18)), "pico (18-21 h)": list(range(18, 22))}
ANIOS = [2021, 2022, 2023, 2024, 2025]
ANIOS_PRE = [2015, 2016, 2017, 2018, 2019]
UMBRAL_DNA = 0.005      # día marcado si la DNA de Atlántico + GCM supera 0,5 % de la demanda total del mercado
UMBRAL_ANOMALIA = 0.12  # hora anómala si se aparta más de 12 % de la mediana móvil de su hora y tipo de día


# ---------------------------------------------------------------- datos
def serie_mercado():
    """Mercado CARIBE SOL (Air-e) regulado; se usa desde 2021. Total (reg + no reg) para la escala de la DNA."""
    mc = pd.read_parquet(PROC / "xm_mercados_horario.parquet")
    mc["fecha"] = pd.to_datetime(mc["fecha"])
    sol = mc[mc["codigo"] == "CARIBE SOL"]
    reg = sol[sol["tipo_mercado"] == "REGULADO"].pivot_table(index="fecha", columns="hora", values="kwh")
    total = sol.groupby(["fecha", "hora"])["kwh"].sum().unstack()
    return reg, total


def serie_agentes(codigos, metricas):
    ag = pd.read_parquet(PROC / "xm_agentes_horario.parquet")
    ag["fecha"] = pd.to_datetime(ag["fecha"])
    ag = ag[ag["codigo"].isin(codigos) & ag["metrica"].isin(metricas)]
    return ag.groupby(["fecha", "hora"])["kwh"].sum(min_count=1).unstack()


def marcar_anomalias(L, cal):
    """Horas que se apartan > UMBRAL de la mediana de la misma hora y tipo de día en ±14 días."""
    marcas = pd.DataFrame(False, index=L.index, columns=L.columns)
    for tipo in cal["tipo_dia"].unique():
        idx = cal.index[cal["tipo_dia"] == tipo].intersection(L.index)
        sub = L.loc[idx]
        med = sub.rolling(29 if tipo == "laboral" else 9, center=True, min_periods=5).median()
        marcas.loc[idx] = (np.abs(sub / med - 1) > UMBRAL_ANOMALIA) | sub.isna() | (sub <= 0)
    return marcas


def dias_dna(total_mercado):
    dna = pd.read_parquet(PROC / "xm_dna_diaria.parquet")
    dna["fecha"] = pd.to_datetime(dna["fecha"])
    d = dna.groupby("fecha")["kwh"].sum()
    dem = total_mercado.sum(axis=1)
    frac = (d.reindex(dem.index).fillna(0) / dem)
    return frac


def panel(L, clima, excluir, anios, log=True, noche_contigua=False):
    """Tabla día x hora con y = 100 ln L (o L en MWh si log=False), HI_d y calendario.

    Con noche_contigua=True las horas 0-5 de la fila d se toman del día d+1, de modo que la noche 22-5 h queda
    completa y toda después del calor del día d (variante de robustez; la Ec. 10 usa el día calendario).
    """
    cal = calendario(L.index)
    y = 100 * np.log(L.where(L > 0)) if log else L.where(L > 0) / 1000.0
    y = y.mask(excluir.reindex(y.index).fillna(False), axis=0)
    if noche_contigua:
        siguiente = y.index + pd.Timedelta(days=1)
        for h in range(6):
            y[h] = y[h].reindex(siguiente).values
    y = y.dropna(how="all")
    y = y[y.index.year.isin(anios)]
    df = y.join(clima, how="inner").join(cal)
    df["anio_mes"] = df.index.strftime("%Y-%m")
    return df


# ---------------------------------------------------------------- regresiones
def disenio(df, hi="hi_media", interacciones=None):
    X = pd.DataFrame(index=df.index)
    X[hi] = df[hi]
    X["sabado"] = (df["tipo_dia"] == "sabado").astype(float)
    X["dom_fest"] = (df["tipo_dia"] == "dom_fest").astype(float)
    for c in ["fin_anio", "carnaval", "semana_santa"]:
        X[c] = df[c].astype(float)
    if interacciones:
        for nombre, serie in interacciones.items():
            X[nombre] = serie
    fe = pd.get_dummies(df["anio_mes"], prefix="m", dtype=float)
    X = pd.concat([X, fe], axis=1)  # sin constante: los efectos año-mes la contienen
    X = X.loc[:, X.std() > 0] if len(fe.columns) > 1 else X
    return X


def ajustar(yv, X, lags=HAC_LAGS):
    ok = yv.notna() & X.notna().all(axis=1)
    return sm.OLS(yv[ok], X[ok]).fit(cov_type="HAC", cov_kwds={"maxlags": lags})


def b_por_hora(df, hi="hi_media", lags=HAC_LAGS, etiqueta=""):
    filas = []
    for h in range(24):
        r = ajustar(df[h], disenio(df, hi), lags)
        ci = r.conf_int().loc[hi]
        filas.append({"especificacion": etiqueta, "hora": h, "b": r.params[hi], "ee": r.bse[hi],
                      "ic_inf": ci[0], "ic_sup": ci[1], "p": r.pvalues[hi], "n_dias": int(r.nobs),
                      "r2": r.rsquared})
    return pd.DataFrame(filas)


def b_dom_fest(df, lags=HAC_LAGS):
    """b_h en días laborales y sábados (base) y en domingos/festivos (base + interacción)."""
    filas = []
    df_ = df["tipo_dia"].eq("dom_fest").astype(float)
    for h in range(24):
        X = disenio(df, interacciones={"hi_x_df": df["hi_media"] * df_})
        r = ajustar(df[h], X, lags)
        g = np.array([1.0 if c in ("hi_media", "hi_x_df") else 0.0 for c in X.columns])
        b_df = g @ r.params.values
        ee_df = np.sqrt(g @ r.cov_params().values @ g)
        for tipo, b, ee in [("laboral y sábado", r.params["hi_media"], r.bse["hi_media"]),
                            ("domingo o festivo", b_df, ee_df)]:
            filas.append({"especificacion": f"2021-2025, {tipo}", "hora": h, "b": b, "ee": ee,
                          "ic_inf": b - 1.96 * ee, "ic_sup": b + 1.96 * ee,
                          "p": 2 * stats.norm.sf(abs(b / ee)), "n_dias": int(r.nobs),
                          "dif_df": r.params["hi_x_df"], "p_dif_df": r.pvalues["hi_x_df"]})
    return pd.DataFrame(filas)


def franjas(df, etiqueta, lags=HAC_LAGS):
    filas = []
    for nombre, horas in FRANJAS.items():
        yb = df[horas].mean(axis=1)
        X = disenio(df)
        r = ajustar(yb, X, lags)
        ci = r.conf_int().loc["hi_media"]
        # diferencia domingo/festivo en la franja
        df_ = df["tipo_dia"].eq("dom_fest").astype(float)
        r2 = ajustar(yb, disenio(df, interacciones={"hi_x_df": df["hi_media"] * df_}), lags)
        filas.append({"muestra": etiqueta, "franja": nombre, "b": r.params["hi_media"], "ee": r.bse["hi_media"],
                      "ic_inf": ci[0], "ic_sup": ci[1], "p": r.pvalues["hi_media"], "n_dias": int(r.nobs),
                      "b_laboral_sab": r2.params["hi_media"], "dif_dom_fest": r2.params["hi_x_df"],
                      "p_dif_dom_fest": r2.pvalues["hi_x_df"]})
    return pd.DataFrame(filas)


def homogeneidad_noche(df, anios, lags=HAC_LAGS):
    """Wald (HAC): ¿la pendiente de la franja nocturna es igual en todos los años?"""
    yb = df[NOCHE].mean(axis=1)
    inter = {f"hi_{a}": df["hi_media"] * (df.index.year == a) for a in anios}
    X = disenio(df, interacciones=inter).drop(columns="hi_media")
    r = ajustar(yb, X, lags)
    nombres = [f"hi_{a}" for a in anios]
    R = np.zeros((len(anios) - 1, len(X.columns)))
    for i in range(len(anios) - 1):
        R[i, X.columns.get_loc(nombres[i])] = 1
        R[i, X.columns.get_loc(nombres[i + 1])] = -1
    w = r.wald_test(R, scalar=True)
    return float(w.statistic), float(w.pvalue), {a: (r.params[f"hi_{a}"], r.bse[f"hi_{a}"]) for a in anios}


def prueba_forma(df, horas, anios=None):
    """Forma centrada c_h = b_h - media de b en 'horas', con covarianza conjunta agrupada por semana.

    Todas las horas comparten los mismos regresores diarios, así que el sistema apilado equivale a una MCO por
    hora; la covarianza conjunta entre horas y días cercanos se obtiene sumando los scores por semana (sandwich
    agrupado). Como la forma centrada suma cero, la última hora se omite en las pruebas.
    Sin 'anios': H0 forma plana (c_h = 0 para todo h). Con 'anios': H0 misma forma en todos los años.
    """
    Z = df[horas].sub(df[horas].mean(axis=1), axis=0)
    W = disenio(df).drop(columns="hi_media")
    if anios:
        X = pd.DataFrame({f"hi_{a}": df["hi_media"] * (df.index.year == a) for a in anios}, index=df.index)
    else:
        X = df[["hi_media"]]
    ok = Z.notna().all(axis=1) & W.notna().all(axis=1)
    Z, W, X = Z[ok].values, W[ok].values, X[ok].values.astype(float)
    semana = (df.index[ok] - pd.Timestamp("2000-01-03")).days // 7
    Xt = X - W @ np.linalg.lstsq(W, X, rcond=None)[0]
    Zt = Z - W @ np.linalg.lstsq(W, Z, rcond=None)[0]
    XtX_inv = np.linalg.inv(Xt.T @ Xt)
    B = XtX_inv @ Xt.T @ Zt                      # k x H
    E = Zt - Xt @ B
    k, H = B.shape
    scores = (E[:, :, None] * Xt[:, None, :]).reshape(len(E), H * k)   # índice h*k + j
    S = pd.DataFrame(scores).groupby(np.asarray(semana)).sum().values
    G = len(S)
    pan = np.kron(np.eye(H), XtX_inv)
    V = pan @ (S.T @ S) @ pan * G / (G - 1)
    vecB = B.T.reshape(-1)
    if not anios:
        idx = list(range(H - 1))
        R = np.eye(H * k)[idx]
    else:
        filas = []
        for h in range(H - 1):
            for j in range(k - 1):
                r = np.zeros(H * k)
                r[h * k + j], r[h * k + j + 1] = 1, -1
                filas.append(r)
        R = np.array(filas)
    rb = R @ vecB
    est = float(rb @ np.linalg.pinv(R @ V @ R.T) @ rb)
    gl = R.shape[0]
    out = {"estadistico": est, "gl": gl, "p": float(stats.chi2.sf(est, gl)), "semanas": G}
    if not anios:
        ee = np.sqrt(np.diag(V))
        out["c_h"] = {int(h): [float(vecB[i]), float(ee[i])] for i, h in enumerate(horas)}
        out["amplitud"] = float(vecB.max() - vecB.min())
    else:
        out["c_h_por_anio"] = {int(a): {int(h): float(B[j, i]) for i, h in enumerate(horas)}
                               for j, a in enumerate(anios)}
    return out


def reparto(tabla):
    """Reparto horario de la respuesta en niveles: s_h = b_h / suma de b_h (en %)."""
    t = tabla.copy()
    t["reparto_pct"] = 100 * t["b"] / t["b"].sum()
    return t


# ---------------------------------------------------------------- figura
def figura(bh, bdf, anual, fr, niv, niv_anual, niv_pre, archivo):
    azul, naranja, gris = "#2a78d6", "#eb6834", "#52514e"
    rampa = ["#a9c8ef", "#7aa9e6", "#4a89dc", "#2a6fc0", "#1b4f8f"]  # secuencial, un solo tono, por año
    orden = list(range(24))  # día calendario, como en la Ec. (10): las horas 0-5 ocurren antes del calor del día
    xs = np.arange(24)
    etiquetas = [f"{h}" for h in orden]

    def reordenar(t):
        return t.set_index("hora").loc[orden].reset_index()

    def sombrear(ax):
        ax.axvspan(-0.5, 5.5, color="#ecebe6", zorder=0, lw=0)
        ax.axvspan(21.5, 23.5, color="#ecebe6", zorder=0, lw=0)
        ax.set_xlim(-0.5, 23.5)
        ax.axhline(0, color=gris, lw=0.8)
        ax.set_xticks(xs[::2])
        ax.set_xticklabels(etiquetas[::2])
        ax.set_xlabel("Hora local (inicio del intervalo)")
        ax.grid(axis="y", color="#e2e1dc", lw=0.6)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)

    plt.rcParams.update({"font.size": 9, "font.family": "DejaVu Sans"})
    fig, axs = plt.subplots(2, 2, figsize=(11, 7.6))

    ax = axs[0, 0]
    t = reordenar(bh)
    ax.fill_between(xs, t["ic_inf"], t["ic_sup"], color=azul, alpha=0.18, lw=0)
    ax.plot(xs, t["b"], color=azul, lw=2, marker="o", ms=3.5, label="Todos los días")
    for tipo, col, ls in [("domingo o festivo", naranja, "-")]:
        u = reordenar(bdf[bdf["especificacion"].str.contains(tipo)])
        ax.plot(xs, u["b"], color=col, lw=1.6, ls=ls, marker="s", ms=3, label="Domingos y festivos")
        ax.fill_between(xs, u["ic_inf"], u["ic_sup"], color=col, alpha=0.10, lw=0)
    sombrear(ax)
    ax.set_ylabel("b_h (% de la demanda horaria por °C de HI diario)")
    ax.set_title("(a) Respuesta al calor 2021-2025, IC 95 % (HAC)", loc="left", fontsize=10)
    ax.legend(frameon=False, loc="lower center", ncol=2)

    ax = axs[0, 1]
    for a, c in zip(ANIOS, rampa):
        u = reordenar(anual[anual["especificacion"] == str(a)])
        ax.plot(xs, u["b"], color=c, lw=1.6, label=str(a))
    sombrear(ax)
    ax.set_title("(b) b_h por año (efectos fijos año-mes)", loc="left", fontsize=10)
    ax.legend(frameon=False, ncol=5, loc="lower center", fontsize=8)

    ax = axs[1, 0]
    nombres = list(FRANJAS)
    sub = fr[fr["muestra"].isin(["2021-2025"] + [str(a) for a in ANIOS])]
    muestras = ["2021-2025"] + [str(a) for a in ANIOS]
    colores = [azul] + rampa
    ancho = 0.13
    for j, (m, c) in enumerate(zip(muestras, colores)):
        u = sub[sub["muestra"] == m].set_index("franja").loc[nombres]
        x = np.arange(len(nombres)) + (j - 2.5) * ancho
        ax.errorbar(x, u["b"], yerr=[u["b"] - u["ic_inf"], u["ic_sup"] - u["b"]], fmt="o", color=c,
                    ms=4.5 if j == 0 else 3.5, lw=1.4 if j == 0 else 1, capsize=0, label=m)
    ax.axhline(0, color=gris, lw=0.8)
    ax.set_xticks(np.arange(len(nombres)))
    ax.set_xticklabels(nombres)
    ax.grid(axis="y", color="#e2e1dc", lw=0.6)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_ylabel("b por franja (%/°C)")
    ax.set_title("(c) Franjas horarias: conjunto y por año, IC 95 %", loc="left", fontsize=10)
    ax.legend(frameon=False, ncol=6, fontsize=7.5, loc="lower center", handletextpad=0.2, columnspacing=0.8)

    ax = axs[1, 1]
    for a, c in zip(ANIOS, rampa):
        u = reordenar(niv_anual[niv_anual["especificacion"].str.startswith(str(a))])
        ax.plot(xs, u["reparto_pct"], color=c, lw=1.2, label=str(a))
    u = reordenar(niv)
    ax.plot(xs, u["reparto_pct"], color=azul, lw=2.2, marker="o", ms=3, label="2021-2025")
    u = reordenar(niv_pre)
    ax.plot(xs, u["reparto_pct"], color=gris, lw=1.6, ls="--", label="Electricaribe 2015-2019")
    ax.axhline(100 / 24, color=gris, lw=0.6, ls=":")
    sombrear(ax)
    ax.set_ylabel("% de la respuesta diaria en MWh/°C")
    ax.set_title("(d) Reparto horario de la respuesta en niveles (Ec. 10)", loc="left", fontsize=10)
    ax.legend(frameon=False, ncol=4, fontsize=7.5, loc="lower center", columnspacing=0.8)

    fig.suptitle("Compuerta horaria: respuesta de la demanda regulada al índice de calor diario "
                 "(sombreado: horas nocturnas 22-5 h)", fontsize=11, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(archivo, dpi=200)
    plt.close(fig)


# ---------------------------------------------------------------- principal
def main():
    clima = pd.read_parquet(PROC / "clima_diario.parquet")
    ide = pd.read_parquet(PROC / "ideam_diario.parquet")
    clima = clima.join(ide, how="left")

    reg, total = serie_mercado()
    cal = calendario(reg.index)
    anom = marcar_anomalias(reg, cal)
    frac_dna = dias_dna(total)
    dia_anom = anom.any(axis=1)
    dia_dna = frac_dna > UMBRAL_DNA
    excluir = dia_anom | dia_dna.reindex(reg.index).fillna(False)
    en_muestra = reg.index.year.isin(ANIOS)
    resumen_exclusion = {
        "dias_2021_2025": int(en_muestra.sum()),
        "dias_con_horas_anomalas": int((dia_anom & en_muestra).sum()),
        "dias_con_DNA_mayor_0.5pct": int((dia_dna.reindex(reg.index).fillna(False) & en_muestra).sum()),
        "dias_excluidos": int((excluir & en_muestra).sum()),
    }
    marcas = pd.DataFrame({"hora_anomala": anom.stack(), "dia_excluido": excluir.reindex(anom.index).repeat(24).values})
    marcas.to_csv(SALIDAS / "marcas_desconexiones.csv")
    print(resumen_exclusion)

    df = panel(reg, clima, excluir, ANIOS)

    resultados = [b_por_hora(df, etiqueta="2021-2025")]
    bh = resultados[0]
    anual = pd.concat([b_por_hora(df[df.index.year == a], etiqueta=str(a)) for a in ANIOS])
    bdf = b_dom_fest(df)

    # robustez
    resultados.append(b_por_hora(df, hi="hi_max", etiqueta="2021-2025, HI máximo diario"))
    resultados.append(b_por_hora(df, lags=14, etiqueta="2021-2025, HAC 14 rezagos"))
    df_ide = df.dropna(subset=["hi_media_ideam"])
    resultados.append(b_por_hora(df_ide, hi="hi_media_ideam", etiqueta="2021-2025, HI de IDEAM (días con datos)"))
    df_todo = panel(reg, clima, pd.Series(False, index=reg.index), ANIOS)
    resultados.append(b_por_hora(df_todo, etiqueta="2021-2025, sin excluir días marcados"))
    # Mercado COSTA CARIBE (Electricaribe, siete departamentos) 2017-2019, como contraste del mercado completo
    mc = pd.read_parquet(PROC / "xm_mercados_horario.parquet")
    mc["fecha"] = pd.to_datetime(mc["fecha"])
    costa = mc[(mc["codigo"] == "COSTA CARIBE") & (mc["tipo_mercado"] == "REGULADO")].pivot_table(
        index="fecha", columns="hora", values="kwh")
    exc_c = marcar_anomalias(costa, calendario(costa.index)).any(axis=1)
    resultados.append(b_por_hora(panel(costa, clima, exc_c, [2017, 2018, 2019]),
                                 etiqueta="2017-2019, mercado COSTA CARIBE"))

    if (PROC / "xm_agentes_horario.parquet").exists():
        aire = serie_agentes(["CSSC", "CSIC"], ["DemaRealReg", "PerdidasEnerReg"])
        df_aire = panel(aire, clima, excluir, ANIOS)
        resultados.append(b_por_hora(df_aire, etiqueta="2021-2025, agente Air-e (real + pérdidas)"))
        # 2015-2019: Electricaribe por agente (siete departamentos; no es el mismo mercado)
        elec = serie_agentes(["EDCC", "EDIC"], ["DemaComeReg"])
    else:
        print("AVISO: falta xm_agentes_horario.parquet; 2015-2019 se estima con el mercado COSTA CARIBE 2017-2019")
        elec = costa
    cal_e = calendario(elec.index)
    exc_e = marcar_anomalias(elec, cal_e).any(axis=1)
    df_pre = panel(elec, clima, exc_e, ANIOS_PRE)
    pre = b_por_hora(df_pre, etiqueta="2015-2019, Electricaribe")
    anios_pre = sorted(set(df_pre.index.year))
    anual_pre = pd.concat([b_por_hora(df_pre[df_pre.index.year == a], etiqueta=f"{a} Electricaribe")
                           for a in anios_pre])
    resultados += [pre]

    todo = pd.concat(resultados + [bdf.drop(columns=["dif_df", "p_dif_df"]), anual, anual_pre],
                     ignore_index=True)
    todo.to_csv(SALIDAS / "b_h_por_hora.csv", index=False, float_format="%.4f")

    fr = pd.concat([franjas(df, "2021-2025")] + [franjas(df[df.index.year == a], str(a)) for a in ANIOS]
                   + [franjas(df_pre, "2015-2019 Electricaribe")]
                   + [franjas(df_pre[df_pre.index.year == a], f"{a} Electricaribe") for a in anios_pre],
                   ignore_index=True)
    fr.to_csv(SALIDAS / "franjas.csv", index=False, float_format="%.4f")

    # ---------------- estabilidad de la forma
    def corr(a, b, horas=range(24)):
        return float(np.corrcoef(a.set_index("hora").loc[list(horas), "b"],
                                 b.set_index("hora").loc[list(horas), "b"])[0, 1])

    est = []
    for a in ANIOS:
        u = anual[anual["especificacion"] == str(a)]
        un = u.set_index("hora").loc[NOCHE]
        f = fr[(fr["muestra"] == str(a)) & (fr["franja"] == "noche (22-5 h)")].iloc[0]
        est.append({"anio": a, "corr_24h_con_conjunto": corr(u, bh), "corr_noche_con_conjunto": corr(u, bh, NOCHE),
                    "b_noche": f["b"], "ic_inf_noche": f["ic_inf"], "ic_sup_noche": f["ic_sup"],
                    "horas_noche_ic_sobre_0": int((un["ic_inf"] > 0).sum()),
                    "cociente_noche_tarde": f["b"] / fr[(fr["muestra"] == str(a))
                                                         & (fr["franja"] == "tarde (12-17 h)")]["b"].iloc[0]})
    est = pd.DataFrame(est)
    est.to_csv(SALIDAS / "estabilidad.csv", index=False, float_format="%.4f")
    w_stat, w_p, _ = homogeneidad_noche(df, ANIOS)

    # ---------------- forma: pruebas conjuntas sobre c_h = b_h - media (log), agrupadas por semana
    forma = {
        "noche_existe": prueba_forma(df, NOCHE),
        "noche_igual_entre_anios": prueba_forma(df, NOCHE, ANIOS),
        "dia_existe": prueba_forma(df, list(range(24))),
        "dia_igual_entre_anios": prueba_forma(df, list(range(24)), ANIOS),
    }
    df_cont = panel(reg, clima, excluir, ANIOS, noche_contigua=True)
    forma["noche_contigua_existe"] = prueba_forma(df_cont, NOCHE)
    forma["noche_contigua_igual_entre_anios"] = prueba_forma(df_cont, NOCHE, ANIOS)
    cont = b_por_hora(df_cont, etiqueta="2021-2025, noche contigua (0-5 h del día siguiente)")
    cont_anual = pd.concat([b_por_hora(df_cont[df_cont.index.year == a], etiqueta=f"{a}, noche contigua")
                            for a in ANIOS])
    pd.concat([cont, cont_anual]).to_csv(SALIDAS / "b_h_noche_contigua.csv", index=False, float_format="%.4f")
    if len(anios_pre) > 1:
        forma["noche_existe_2015_2019"] = prueba_forma(df_pre, NOCHE)
        forma["noche_igual_entre_anios_2015_2019"] = prueba_forma(df_pre, NOCHE, anios_pre)
    (SALIDAS / "pruebas_forma.json").write_text(json.dumps(forma, indent=2, ensure_ascii=False), encoding="utf-8")

    # ---------------- Ec. (10) en niveles (MWh/°C) y reparto horario de la respuesta
    df_niv = panel(reg, clima, excluir, ANIOS, log=False)
    niv = reparto(b_por_hora(df_niv, etiqueta="2021-2025, niveles (MWh/°C)"))
    niv_anual = pd.concat([reparto(b_por_hora(df_niv[df_niv.index.year == a], etiqueta=f"{a}, niveles (MWh/°C)"))
                           for a in ANIOS])
    df_pre_niv = panel(elec, clima, exc_e, ANIOS_PRE, log=False)
    niv_pre = reparto(b_por_hora(df_pre_niv, etiqueta="2015-2019, Electricaribe, niveles (MWh/°C)"))
    niveles = pd.concat([niv, niv_anual, niv_pre], ignore_index=True)
    niveles.to_csv(SALIDAS / "b_h_niveles_reparto.csv", index=False, float_format="%.4f")
    est["reparto_noche_pct"] = [niv_anual[niv_anual["especificacion"].str.startswith(str(a))]
                                .set_index("hora").loc[NOCHE, "reparto_pct"].sum() for a in ANIOS]
    est.to_csv(SALIDAS / "estabilidad.csv", index=False, float_format="%.4f")

    # ---------------- decisión
    fn = fr[(fr["muestra"] == "2021-2025") & (fr["franja"] == "noche (22-5 h)")].iloc[0]
    noche_h = bh.set_index("hora").loc[NOCHE]
    c1 = bool(fn["ic_inf"] > 0 and (noche_h["ic_inf"] > 0).sum() >= 6)
    anios_sig = int((est["ic_inf_noche"] > 0).sum())
    c2a = bool(anios_sig >= 4 and w_p > 0.05)
    c2b = bool(forma["noche_igual_entre_anios"]["p"] > 0.05)
    decision = {
        "regla": ("Capa B si (C1) la franja 22-5 h tiene b > 0 con IC 95 % sobre cero en 2021-2025 y al menos 6 de "
                  "las 8 horas nocturnas también; (C2a) el nivel nocturno es significativo en al menos 4 de 5 años y "
                  "no difiere entre años (Wald HAC, p > 0,05); y (C2b) la forma nocturna centrada (b_h menos la "
                  "media nocturna) no difiere entre años (Wald conjunto agrupado por semana, p > 0,05). Si no, capa C."),
        "C1_noche_distinta_de_cero": c1,
        "C2a_nivel_nocturno_estable": c2a,
        "C2b_forma_nocturna_estable": c2b,
        "capa": "B" if (c1 and c2a and c2b) else "C",
        "b_noche_2021_2025": [fn["b"], fn["ic_inf"], fn["ic_sup"]],
        "horas_noche_con_ic_sobre_0": int((noche_h["ic_inf"] > 0).sum()),
        "anios_noche_significativa": anios_sig,
        "wald_homogeneidad_nivel_noche": {"estadistico": w_stat, "p": w_p},
        "forma_noche_existe_p": forma["noche_existe"]["p"],
        "forma_noche_amplitud_pp": forma["noche_existe"]["amplitud"],
        "forma_noche_igual_entre_anios_p": forma["noche_igual_entre_anios"]["p"],
        "forma_noche_contigua_existe_p": forma["noche_contigua_existe"]["p"],
        "forma_noche_contigua_igual_entre_anios_p": forma["noche_contigua_igual_entre_anios"]["p"],
        "forma_dia_existe_p": forma["dia_existe"]["p"],
        "forma_dia_igual_entre_anios_p": forma["dia_igual_entre_anios"]["p"],
        "corr_24h_min_descriptiva": float(est["corr_24h_con_conjunto"].min()),
        "corr_forma_2015_2019_vs_2021_2025": corr(pre, bh),
        "reparto_noche_pct_por_anio": dict(zip(ANIOS, est["reparto_noche_pct"].round(2))),
        "exclusiones": resumen_exclusion,
        "dias_en_regresion": int(len(df)),
        "sd_hi_media_dentro_de_mes": float(df.groupby("anio_mes")["hi_media"].std().mean()),
    }
    (SALIDAS / "decision.json").write_text(json.dumps(decision, indent=2, ensure_ascii=False, default=float),
                                           encoding="utf-8")
    figura(bh, bdf, anual, fr, niv, niv_anual, niv_pre, SALIDAS / "b_h_compuerta.png")

    pd.set_option("display.width", 200)
    print(bh[["hora", "b", "ic_inf", "ic_sup", "p"]].round(3).to_string(index=False))
    print(fr[fr["muestra"].isin(["2021-2025", "2015-2019 Electricaribe"])].round(3).to_string(index=False))
    print(est.round(3).to_string(index=False))
    print(niv[["hora", "b", "ic_inf", "ic_sup", "reparto_pct"]].round(2).to_string(index=False))
    print({k: {kk: vv for kk, vv in v.items() if kk in ("estadistico", "gl", "p", "amplitud")}
           for k, v in forma.items()})
    print(json.dumps(decision, indent=2, ensure_ascii=False, default=float))


if __name__ == "__main__":
    main()
