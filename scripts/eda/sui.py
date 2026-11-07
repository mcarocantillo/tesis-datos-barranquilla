"""EDA del Sistema Único de Información (SUI) de la Superservicios para el capítulo «Sistema Único de Información (SUI)».

Entradas (solo lectura):
  tablas/SUI_Barranquilla_urbano_residencial_2015_2026.csv     consolidado ele_com_096, residencial, mes x estrato
  tablas/SUI_Barranquilla_urbano_NO_residencial_2019_2026.csv  consolidado ele_com_096, no residencial, mes
  tablas/SUI_O3_Barranquilla_residencial_lectura_2015_2025.csv cubo O3, mes x estrato x tipo de lectura
  tablas/SUI_O3_5municipios_residencial_lectura_2015_2025.csv  cubo O3, cinco municipios (solo cobertura)
  Downloads/Superservicios/SIU 2019/*/*.csv                    reportes crudos ele_com_096 por empresa, ene.-ago. 2019
Salidas: figuras/eda/sui_*.png y tablas/eda/sui_*.csv (solo agregados por mes, estrato y tipo de lectura).

Regla de meses atípicos del cubo O3: dentro de cada estrato y tipo de lectura, un mes es atípico si su kWh por
suscriptor queda fuera de 0,5 a 2 veces la mediana móvil centrada de 7 meses (mínimo 3) o si no tiene consumo.
Las cuentas «n/a» (0 kWh) no entran en el consumo por suscriptor.

Uso, desde la raíz del repositorio: python scripts/eda/sui.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from estilo import *  # noqa: E402,F401,F403

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import ListedColormap  # noqa: E402

np.random.seed(SEMILLA)
T = REPO / "tablas"
CONS = T / "SUI_Barranquilla_urbano_residencial_2015_2026.csv"
NORES = T / "SUI_Barranquilla_urbano_NO_residencial_2019_2026.csv"
O3 = T / "SUI_O3_Barranquilla_residencial_lectura_2015_2025.csv"
O3M = T / "SUI_O3_5municipios_residencial_lectura_2015_2025.csv"
CRUDO19 = DESCARGAS / "Superservicios" / "SIU 2019"

F_CONS = "Fuente: SUI, reporte ele_com_096 (Barranquilla, urbano, residencial)."
F_O3 = "Fuente: SUI, cubo O3 VISTA_FACTURACION_ENERGIA (Barranquilla, urbano, residencial), consultado el 27-oct-2026."
F_AMBOS = "Fuente: SUI, reporte ele_com_096 y cubo O3 (Barranquilla, urbano, residencial)."
LECT = ["Real", "Estimada", "No tiene medidor", "n/a"]
NOM_LECT = {"Real": "Real", "Estimada": "Estimada", "No tiene medidor": "Sin medidor", "n/a": "«n/a» (0 kWh)"}
COL_LECT = {"Real": PAL[0], "Estimada": PAL[3], "No tiene medidor": PAL[7], "n/a": "#c9c8c2"}
VALIDACION = {2023, 2025}
MESES = "ene. feb. mar. abr. may. jun. jul. ago. sep. oct. nov. dic.".split()


def fecha(d):
    return pd.to_datetime(dict(year=d.anio, month=d.mes, day=15))


# ---------------------------------------------------------------- carga

def cargar():
    c = pd.read_csv(CONS, sep=";", dtype={"estrato": str})
    c["bandera"] = c.bandera.fillna("")
    nr = pd.read_csv(NORES, sep=";")
    o = pd.read_csv(O3, sep=";", keep_default_na=False)
    m = pd.read_csv(O3M, sep=";", keep_default_na=False)
    return c, nr, o, m


def meses_bandera_total(c):
    """Meses con bandera de consumo en el total residencial del consolidado (refacturaciones y meses sin consumo)."""
    t = c[(c.estrato == "total") & c.bandera.str.contains("consumo")]
    return set(zip(t.anio, t.mes))


def atipicos(o, mb):
    """Marca, por estrato y tipo de lectura, los meses fuera de 0,5-2 veces la mediana móvil de 7 meses.
    Además descarta, en todos los estratos, los meses con bandera de consumo en el total del consolidado (mb):
    la refacturación de sep. 2022 sube el consumo de todos los estratos a la vez, y en E2-E6 queda por debajo de 2."""
    o = o.sort_values(["estrato", "lectura", "anio", "mes"]).copy()
    o["kWh_susc"] = o.consumo_kWh / o.suscriptores.replace(0, np.nan)
    o["mediana7"] = o.groupby(["estrato", "lectura"]).kWh_susc.transform(
        lambda x: x.rolling(7, center=True, min_periods=3).median())
    o["razon"] = o.kWh_susc / o.mediana7
    regla = (o.lectura != "n/a") & ((o.consumo_kWh <= 0) | ~o.razon.between(0.5, 2.0))
    mes_mal = (o.lectura != "n/a") & pd.Series([k in mb for k in zip(o.anio, o.mes)], index=o.index)
    o["atipico"] = regla | mes_mal
    o["motivo"] = np.where(regla, "mediana móvil", np.where(mes_mal, "mes con bandera en el consolidado", ""))
    return o


def leer_crudo_2019():
    """Reportes ele_com_096 por empresa (ene.-ago. 2019) que están en Descargas/Superservicios."""
    filas = []
    for f in sorted(CRUDO19.glob("*/*.csv")):
        txt = f.read_text(encoding="latin-1").splitlines()
        pie = dict(l.split(",", 1) for l in txt if l.count(",") == 1)
        var, mes = pie.get("Reporte a Consultar"), int(pie.get("Período", pie.get("Período", "0")))
        cab = txt[0].split(",")
        for l in txt[1:]:
            p = l.split(",")
            if len(p) != len(cab) or not p[2]:
                continue
            r = dict(zip(cab, p))
            for col in cab[4:]:
                v = r[col]
                filas.append(dict(mes=mes, variable=var, empresa=r["Empresa"].strip(), columna=col,
                                  valor=0.0 if v in ("ND", "") else float(v)))
    return pd.DataFrame(filas)


# ---------------------------------------------------------------- tablas y figuras

def verificar(c, o):
    """El cubo O3 sumado sobre el tipo de lectura debe reproducir el consolidado."""
    s = o.groupby(["anio", "mes", "estrato"])[["suscriptores", "consumo_kWh"]].sum().reset_index()
    cc = c[c.estrato != "total"].assign(estrato=lambda d: d.estrato.astype(int))
    j = cc.merge(s, on=["anio", "mes", "estrato"], suffixes=("_cons", "_o3"))
    d_s = (j.suscriptores_cons - j.suscriptores_o3).abs().max()
    d_k = (j.consumo_kWh_cons - j.consumo_kWh_o3).abs().max()
    print(f"O3 vs consolidado: {len(j)} filas mes x estrato; dif. máx. suscriptores {d_s}, kWh {d_k}")
    return len(j), d_s, d_k


def cobertura(c, nr, o, m, crudo):
    meses = pd.period_range("2015-01", "2026-08", freq="M")
    ct = c[c.estrato == "total"].set_index(pd.PeriodIndex(fecha(c[c.estrato == "total"]), freq="M"))
    o_t = o.groupby(["anio", "mes"]).agg(na=("suscriptores", lambda x: 0), n=("suscriptores", "size"))
    na = o[o.lectura == "n/a"].groupby(["anio", "mes"]).suscriptores.sum()
    tot = o.groupby(["anio", "mes"]).suscriptores.sum()
    frac_na = (na / tot).reindex(tot.index).fillna(0)
    at_e1 = o[o.atipico & (o.estrato == 1)].groupby(["anio", "mes"]).size()
    nr_k = nr.set_index(pd.PeriodIndex(fecha(nr), freq="M"))
    nr_k["kps"] = nr_k.kWh_nores / nr_k.S_nores
    nr_k["r"] = nr_k.kps / nr_k.kps[nr_k.S_nores >= 1000].median()   # misma regla que las banderas de 04_metodologia
    cr = set(crudo.mes.unique())
    # 0 fuera del periodo, 1 disponible, 2 atípico o bandera de consumo, 3 solo bandera de tarifa, 4 falta
    G = np.zeros((4, len(meses)), dtype=int)
    for i, p in enumerate(meses):
        if p.year <= 2026:
            if p in ct.index:
                b = ct.loc[p, "bandera"]
                G[0, i] = 2 if "consumo" in b else 3 if b else 1
            else:
                G[0, i] = 4
        if p.year <= 2025:
            k = (p.year, p.month)
            if k not in tot.index:
                G[1, i] = 4
            else:
                G[1, i] = 2 if (frac_na.get(k, 0) > 0.5 or k in at_e1.index) else 1
        if p.year >= 2019:
            if p in nr_k.index:
                G[2, i] = 2 if (nr_k.loc[p, "S_nores"] < 1000 or not 0.5 <= nr_k.loc[p, "r"] <= 1.5) else 1
            else:
                G[2, i] = 4
        if p.year == 2019 and p.month in cr:
            G[3, i] = 1
    filas = ["Consolidado residencial\n(ele_com_096)", "Cubo O3 por tipo\nde lectura", "Consolidado no\nresidencial",
             "Reportes crudos por\nempresa (locales)"]
    fig, ax = plt.subplots(figsize=(12, 3.6))
    cmap = ListedColormap(["#f1f0ec", "#9cc3ec", PAL[3], "#cfc6f2", PAL[7]])
    ax.imshow(G, aspect="auto", cmap=cmap, vmin=0, vmax=4, interpolation="nearest")
    ax.set_yticks(range(4), filas, fontsize=9.5)
    xt = [i for i, p in enumerate(meses) if p.month == 1]
    ax.set_xticks(xt, [str(meses[i].year) for i in xt])
    ax.set_xticks(np.arange(-0.5, len(meses), 1), minor=True)
    ax.grid(False)
    ax.tick_params(axis="x", which="minor", length=0)
    for y in np.arange(0.5, 4, 1):
        ax.axhline(y, color="#fcfcfb", lw=3)
    from matplotlib.patches import Patch
    leg = [Patch(color="#9cc3ec", label="Disponible"), Patch(color=PAL[3], label="Mes atípico o con bandera de consumo"),
           Patch(color="#cfc6f2", label="Solo bandera de tarifa"), Patch(color=PAL[7], label="Falta"),
           Patch(color="#f1f0ec", label="Fuera del periodo")]
    ax.legend(handles=leg, ncol=5, loc="upper left", bbox_to_anchor=(0, -0.13), fontsize=9)
    titulo(ax, "Meses disponibles en cada producto del SUI usado", "Barranquilla urbano, enero de 2015 a agosto de 2026")
    guardar(fig, "sui_cobertura.png", "Fuente: SUI, reporte ele_com_096 y cubo O3. En O3 se marca el mes con más de la "
            "mitad de cuentas «n/a» o con un atípico del estrato 1.")

    # tabla de cobertura por producto
    filas_t = []
    filas_t.append(dict(producto="ele_com_096 residencial", desde="2015-01", hasta="2026-08",
                        meses=c[c.estrato == "total"].shape[0], faltantes="2022-06",
                        meses_bandera_consumo=int((c[c.estrato == "total"].bandera.str.contains("consumo")).sum()),
                        meses_bandera_tarifa=int((c[c.estrato == "total"].bandera.str.contains("valor")).sum()),
                        filas=len(c), unidad="mes x estrato (1-6 y total)"))
    filas_t.append(dict(producto="ele_com_096 no residencial", desde="2019-01", hasta="2026-08", meses=len(nr),
                        faltantes="2022-06 casi vacío (16 suscriptores)", meses_bandera_consumo=int((G[2] == 2).sum()),
                        meses_bandera_tarifa=0, filas=len(nr), unidad="mes (industrial, comercial, oficial, otros)"))
    filas_t.append(dict(producto="O3 Barranquilla", desde="2015-01", hasta="2025-12",
                        meses=o.groupby(["anio", "mes"]).ngroups, faltantes="2022-06",
                        meses_bandera_consumo=int(o[o.atipico & (o.estrato == 1)].groupby(["anio", "mes"]).ngroups),
                        meses_bandera_tarifa=0, filas=len(o), unidad="mes x estrato x tipo de lectura"))
    for mu, g in m.groupby("municipio"):
        filas_t.append(dict(producto=f"O3 cinco municipios: {mu.title()}", desde="2015-01", hasta="2025-12",
                            meses=g.groupby(["anio", "mes"]).ngroups, faltantes="",
                            meses_bandera_consumo=np.nan, meses_bandera_tarifa=np.nan, filas=len(g),
                            unidad=f"mes x estrato ({g.estrato.nunique()} estratos) x tipo de lectura"))
    filas_t.append(dict(producto="Reportes crudos locales por empresa", desde="2019-01", hasta="2019-08",
                        meses=crudo.mes.nunique(), faltantes="", meses_bandera_consumo=np.nan, meses_bandera_tarifa=np.nan,
                        filas=len(crudo), unidad="mes x empresa x columna (3 variables)"))
    tb = pd.DataFrame(filas_t)
    tabla(tb, "sui_cobertura.csv", index=False)
    print(tb.to_string())
    return G


def comercializadores(crudo, c):
    """Participación de cada empresa en el residencial, ene.-ago. 2019, y comprobación contra el consolidado."""
    res = crudo[crudo.columna == "Total Residencial"]
    piv = res.groupby(["variable", "empresa"]).valor.sum().unstack(0).fillna(0)
    piv = piv[(piv > 0).any(axis=1)]
    sh = (100 * piv / piv.sum()).round(2)
    sh.columns = [f"pct_{v.lower().replace(' ', '_')}" for v in sh.columns]
    n_emp = crudo[crudo.valor > 0].groupby("columna").empresa.nunique()
    print("empresas con dato > 0 por columna (ene.-ago. 2019):", n_emp.to_dict())
    tabla(sh.sort_values(sh.columns[0], ascending=False), "sui_comercializadores_2019.csv")
    # comprobación con el consolidado
    cons = c[(c.anio == 2019) & (c.estrato == "total")].set_index("mes")
    s = res[res.variable == "Suscriptores"].groupby("mes").valor.sum()
    k = res[res.variable == "Consumo"].groupby("mes").valor.sum()
    d_s = (s - cons.suscriptores.reindex(s.index)).abs().max()
    d_k = (k - cons.consumo_kWh.reindex(k.index)).abs().max()
    print(f"crudo 2019 vs consolidado: dif. máx. suscriptores {d_s}, kWh {d_k:.0f}")
    return sh, n_emp, d_s, d_k


def suscriptores(c, o):
    cc = c[c.estrato != "total"].assign(estrato=lambda d: d.estrato.astype(int))
    con = o[o.lectura != "n/a"].groupby(["anio", "mes", "estrato"]).suscriptores.sum().rename("sin_na")
    rea = o[o.lectura == "Real"].groupby(["anio", "mes", "estrato"]).suscriptores.sum().rename("reales")
    d = cc.set_index(["anio", "mes", "estrato"]).suscriptores.rename("consolidado").to_frame().join(con).join(rea)
    d = d.reset_index()
    # meses en que casi todas las cuentas son «n/a» (sep.-oct. 2024, ago. 2025): sin dato por tipo de lectura
    casi_na = {(2024, 9), (2024, 10), (2025, 8)}
    d.loc[[k in casi_na for k in zip(d.anio, d.mes)], ["sin_na", "reales"]] = np.nan
    tot = d.groupby(["anio", "mes"])[["consolidado", "sin_na", "reales"]].sum(min_count=1).reset_index()
    tot["f"] = fecha(tot)

    fig, ax = plt.subplots(1, 2, figsize=(12, 4.6), gridspec_kw={"width_ratios": [1, 1.1]})
    a = ax[0]
    a.plot(tot.f, tot.consolidado / 1e3, color=TXT2, lw=1.6, label="Consolidado (todas las cuentas)")
    a.plot(tot.f, tot.sin_na / 1e3, color=PAL[0], lw=2, label="Sin cuentas «n/a»")
    a.plot(tot.f, tot.reales / 1e3, color=PAL[2], lw=2, label="Solo lectura real")
    a.set_ylabel("miles de suscriptores")
    a.set_ylim(0, 380)
    a.legend(loc="lower left", fontsize=9)
    titulo(a, "A. Suscriptores residenciales", "Estratos 1 a 6; hasta mayo de 2021 el consolidado y la serie sin «n/a» coinciden")
    b = ax[1]
    dic = d[d.mes == 12].copy()
    for e in range(1, 7):
        g = d[d.estrato == e].copy()
        g["f"] = fecha(g)
        b.plot(g.f, g.sin_na / 1e3, color=EST[f"E{e}"], lw=2, label=f"E{e}")
        b.plot(g.f, g.consolidado / 1e3, color=EST[f"E{e}"], lw=0.9, ls=":", alpha=.9)
        b.annotate(f"E{e}", (g.f.iloc[-1], g.sin_na.iloc[-1] / 1e3), xytext=(4, 0), textcoords="offset points",
                   va="center", fontsize=9, color=EST[f"E{e}"])
    b.set_ylabel("miles de suscriptores")
    titulo(b, "B. Por estrato, sin cuentas «n/a»", "Línea punteada: consolidado")
    guardar(fig, "sui_suscriptores.png", F_AMBOS)

    # tabla: diciembre de cada año, consolidado y sin «n/a»; participación por estrato
    dic = d[d.mes == 12].copy()
    t = dic.pivot(index="anio", columns="estrato", values="consolidado")
    t.columns = [f"E{e}" for e in t.columns]
    t["total"] = t.sum(axis=1)
    t2 = dic.pivot(index="anio", columns="estrato", values="sin_na").sum(axis=1, min_count=1).rename("total_sin_na")
    t3 = dic.pivot(index="anio", columns="estrato", values="reales").sum(axis=1, min_count=1).rename("total_reales")
    sh = (100 * dic.pivot(index="anio", columns="estrato", values="consolidado").div(t.total, axis=0)).round(1)
    sh.columns = [f"pct_E{e}" for e in sh.columns]
    out = t.join(t2).join(t3).join(sh)
    tabla(out, "sui_suscriptores_diciembre.csv")
    print(out.to_string())
    return d, tot, out


def series(c, o):
    """kWh por suscriptor mensual por estrato: consolidado, sin «n/a» y solo reales (sin meses atípicos)."""
    v = o[~o.atipico & (o.lectura != "n/a")]
    bad = o[o.atipico].groupby(["anio", "mes", "estrato"]).size().index
    vv = o[(o.lectura != "n/a")].set_index(["anio", "mes", "estrato"])
    vv = vv[~vv.index.isin(bad)].reset_index()
    sin_na = vv.groupby(["anio", "mes", "estrato"])[["suscriptores", "consumo_kWh"]].sum()
    sin_na = (sin_na.consumo_kWh / sin_na.suscriptores).rename("sin_na")
    rea = v[v.lectura == "Real"].set_index(["anio", "mes", "estrato"])
    rea = (rea.consumo_kWh / rea.suscriptores).rename("reales")
    cc = c[c.estrato != "total"].assign(estrato=lambda d: d.estrato.astype(int)).set_index(["anio", "mes", "estrato"])
    # consolidado: meses sin ninguna bandera, como en estacionalidad_sui.py (reproduce la tabla tab-calibracion)
    cons = cc.kWh_suscriptor.where(cc.bandera == "").rename("consolidado")
    d = pd.concat([cons, sin_na, rea], axis=1).reset_index()
    d = d[d.anio <= 2025]
    d["f"] = fecha(d)

    fig, axs = plt.subplots(2, 3, figsize=(13, 7), sharex=True)
    for e, a in zip(range(1, 7), axs.flat):
        g = d[d.estrato == e]
        a.plot(g.f, g.consolidado, color="#9a9993", lw=1.1, label="Consolidado (meses sin bandera)")
        a.plot(g.f, g.reales, color=EST[f"E{e}"], lw=1.8, label="Solo lectura real")
        for y in VALIDACION:
            a.axvspan(pd.Timestamp(y, 1, 1), pd.Timestamp(y, 12, 31), color="#efeee9", zorder=0)
        a.axvspan(pd.Timestamp(2020, 1, 1), pd.Timestamp(2020, 12, 31), color="#f6e3dc", zorder=0)
        lo = np.nanmin([g.consolidado.min(), g.reales.min()])
        hi = np.nanmax([g.consolidado.max(), g.reales.max()])
        a.set_ylim(lo * 0.85, hi * 1.08)
        a.set_title(f"E{e}", loc="left", fontweight="bold", color=EST[f"E{e}"])
        if e in (1, 4):
            a.set_ylabel("kWh por suscriptor y mes")
    axs[0, 0].legend(loc="upper right", fontsize=8.5)
    fig.suptitle("Consumo por suscriptor: consolidado frente a lecturas reales", x=0.01, ha="left",
                 fontweight="bold", fontsize=13)
    guardar(fig, "sui_kwh_serie.png", F_AMBOS + " Sin meses atípicos. Rosado: 2020 (fuera de la calibración); "
            "gris: 2023 y 2025 (validación).")

    # tabla anual: media de los meses válidos (como 03_resultados) y razón consolidado / real
    an = d.groupby(["anio", "estrato"])[["consolidado", "sin_na", "reales"]].mean()
    n = d.groupby(["anio", "estrato"]).reales.count().rename("meses_reales")
    an = an.join(n)
    an["razon_cons_real"] = an.consolidado / an.reales
    tabla(an.round(1).reset_index(), "sui_kwh_anual.csv", index=False)
    per = {}
    for lab, yy in [("2015-2019", range(2015, 2020)), ("2023-2025", [2023, 2024, 2025]),
                    ("calibracion", [y for y in range(2015, 2026) if y not in (2020, 2023, 2025)])]:
        per[lab] = d[d.anio.isin(yy)].groupby("estrato")[["consolidado", "reales"]].mean()
    pe = pd.concat(per, axis=1).round(0)
    print(pe.to_string())
    tabla(pe, "sui_kwh_periodos.csv")
    return d, an, pe


def estacionalidad(d):
    """Índice mensual y alza ago.-sep. frente a feb.-mar. con lecturas reales y con el consolidado.
    Como en estacionalidad_sui.py: solo años con 10 o más meses válidos del estrato."""
    filas, idx = [], {}

    def alza(h, col):
        a = h[h.mes.isin([8, 9])].groupby("anio")[col].mean()
        b = h[h.mes.isin([2, 3])].groupby("anio")[col].mean()
        return (a / b - 1).dropna() * 100

    for col in ("reales", "consolidado"):
        g = d.dropna(subset=[col]).copy()
        g = g[g.groupby(["estrato", "anio"])[col].transform("size") >= 10]
        g["i"] = g[col] / g.groupby(["estrato", "anio"])[col].transform("mean")
        idx[col] = g[g.anio != 2020].groupby(["mes", "estrato"]).i.mean().unstack()
        for e, h in g.groupby("estrato"):
            r = alza(h[h.anio != 2020], col)
            r2 = alza(h, col)
            filas.append(dict(serie=col, estrato=e, anios=len(r), alza_media=r.mean(), alza_min=r.min(),
                              alza_max=r.max(), alza_media_con_2020=r2.mean()))
    al = pd.DataFrame(filas)
    tabla(al.round(1), "sui_alza_estacional.csv", index=False)
    ir = idx["reales"].round(3)
    ir.columns = [f"E{e}" for e in ir.columns]
    tabla(ir, "sui_indice_estacional_reales.csv")
    print(al.round(1).to_string())

    fig, ax = plt.subplots(1, 2, figsize=(12, 4.6), gridspec_kw={"width_ratios": [1.2, 1]})
    a = ax[0]
    for e in range(1, 7):
        a.plot(range(1, 13), idx["reales"][e], color=EST[f"E{e}"], lw=2, marker="o", ms=3.5, label=f"E{e}")
    a.axhline(1, color=TXT2, lw=.8)
    a.set_xticks(range(1, 13), list("EFMAMJJASOND"))
    a.set_ylabel("kWh del mes / media del año")
    a.legend(ncol=3, fontsize=9, loc="upper left")
    titulo(a, "A. Índice estacional con lecturas reales", "Media de los años 2015-2025 con 10 o más meses válidos, sin 2020")
    b = ax[1]
    x = np.arange(6)
    w = .38
    ar = al[al.serie == "reales"].set_index("estrato").alza_media
    ac = al[al.serie == "consolidado"].set_index("estrato").alza_media
    b.bar(x - w / 2, ac.values, w, color="#c9c8c2", label="Consolidado")
    b.bar(x + w / 2, ar.values, w, color=[EST[f"E{e}"] for e in range(1, 7)], label="Solo lectura real")
    for i, (u, v) in enumerate(zip(ac.values, ar.values)):
        b.annotate(fmt(v, 0), (i + w / 2, v), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=9)
        b.annotate(fmt(u, 0), (i - w / 2, u), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=9,
                   color=TXT2)
    b.set_xticks(x, [f"E{e}" for e in range(1, 7)])
    b.set_ylabel("%")
    b.legend(fontsize=9, loc="upper left")
    titulo(b, "B. Alza de ago.-sep. frente a feb.-mar., %", "Media de los años 2015-2025 sin 2020")
    guardar(fig, "sui_estacionalidad.png", F_AMBOS)
    return al, idx


def tipos_lectura(o):
    """Composición por tipo de lectura: suscriptores y consumo, por estrato y año."""
    a = o.groupby(["anio", "estrato", "lectura"])[["suscriptores", "consumo_kWh"]].sum().unstack("lectura").fillna(0)
    ps = 100 * a["suscriptores"].div(a["suscriptores"].sum(axis=1), axis=0)
    pk = 100 * a["consumo_kWh"].div(a["consumo_kWh"].sum(axis=1), axis=0)
    # parte del consumo sin lectura real, con y sin los meses atípicos (se descarta el mes del estrato completo)
    bad = o[o.atipico].groupby(["anio", "mes", "estrato"]).size().index
    oo = o[o.lectura != "n/a"].set_index(["anio", "mes", "estrato"])
    limpio = oo[~oo.index.isin(bad)].reset_index()
    def no_real(x):
        k = x.groupby(["anio", "estrato", "lectura"]).consumo_kWh.sum().unstack().fillna(0)
        return (100 * (1 - k["Real"] / k.sum(axis=1))).unstack()
    nr_todo, nr_limpio = no_real(o[o.lectura != "n/a"]), no_real(limpio)
    out = pd.concat({"pct_susc": ps, "pct_kWh": pk}, axis=1).round(1)
    corto = {"Real": "real", "Estimada": "estimada", "No tiene medidor": "sin_medidor", "n/a": "na"}
    out.columns = [f"{a_}_{corto[b_]}" for a_, b_ in out.columns]
    tabla(out.reset_index(), "sui_tipo_lectura_anual.csv", index=False)
    nn = pd.concat({"con_atipicos": nr_todo, "sin_atipicos": nr_limpio}, axis=1).round(1)
    nn.columns = [f"{a_}_E{b_}" for a_, b_ in nn.columns]
    tabla(nn, "sui_no_real_anual.csv")
    print(nn.to_string())

    # kWh por suscriptor por tipo de lectura, 2023-2025 (sin atípicos)
    v = o[~o.atipico & (o.lectura != "n/a") & o.anio.isin([2023, 2024, 2025])]
    kt = v.groupby(["estrato", "lectura"])[["consumo_kWh", "suscriptores"]].sum()
    kt = (kt.consumo_kWh / kt.suscriptores).unstack().round(0)
    tabla(kt, "sui_kwh_por_tipo_2023_2025.csv")
    print(kt.to_string())

    fig, ax = plt.subplots(1, 2, figsize=(12, 4.6), gridspec_kw={"width_ratios": [1.1, 1]})
    a = ax[0]
    s1 = ps.xs(1, level="estrato")[LECT]
    bot = np.zeros(len(s1))
    for l_ in LECT:
        a.bar(s1.index, s1[l_], bottom=bot, color=COL_LECT[l_], label=NOM_LECT[l_], width=.8)
        bot += s1[l_].values
    a.set_ylim(0, 100)
    a.set_ylabel("% de los suscriptores del año")
    a.set_xticks(range(2015, 2026, 2))
    a.legend(ncol=2, fontsize=9, loc="lower left")
    titulo(a, "A. Estrato 1: suscriptores por tipo de lectura", "Suma de los meses del año")
    b = ax[1]
    fin, pos, ult = nr_limpio.iloc[-1].sort_values(), {}, -1e9
    for e, yv in fin.items():                     # etiquetas finales sin solaparse
        pos[e] = max(yv, ult + 2.6)
        ult = pos[e]
    for e in range(1, 7):
        b.plot(nr_limpio.index, nr_limpio[e], color=EST[f"E{e}"], lw=2, marker="o", ms=3.5)
        b.annotate(f"E{e}", (2025.15, pos[e]), va="center", fontsize=9, color=EST[f"E{e}"])
    b.plot(nr_todo.index, nr_todo[1], color=EST["E1"], lw=1, ls="--")
    b.annotate("E1 con atípicos", (2023, nr_todo.loc[2023, 1]), xytext=(-95, -4), textcoords="offset points",
               fontsize=8.5, color=EST["E1"])
    b.set_ylim(0, 85)
    b.set_xlim(2014.6, 2025.9)
    b.set_xticks(range(2015, 2026, 2))
    b.set_ylabel("%")
    titulo(b, "B. Consumo facturado sin lectura real, %", "Estimadas y sin medidor, sin meses atípicos")
    guardar(fig, "sui_tipos_lectura.png", F_O3)
    return ps, pk, nr_todo, nr_limpio, kt


def fig_atipicos(o):
    e1 = o[(o.estrato == 1) & (o.lectura != "n/a")].copy()
    e1["f"] = fecha(e1)
    fig, ax = plt.subplots(figsize=(12, 4.8))
    for l_ in ["Real", "Estimada", "No tiene medidor"]:
        g = e1[e1.lectura == l_]
        ax.plot(g.f, g.kWh_susc, color=COL_LECT[l_], lw=1.6, label=NOM_LECT[l_])
        ax.fill_between(g.f, 0.5 * g.mediana7, 2 * g.mediana7, color=COL_LECT[l_], alpha=.10, lw=0)
        at = g[g.atipico & (g.kWh_susc > 0)]
        ax.scatter(at.f, at.kWh_susc, s=46, facecolor="none", edgecolor=TXT, lw=1.3, zorder=5)
        for _, r in at.iterrows():
            if r.kWh_susc > 1000:
                ax.annotate(f"{MESES[r.f.month - 1]} {r.f.year}: {fmt(r.kWh_susc, 0)}", (r.f, r.kWh_susc), xytext=(6, 2),
                            textcoords="offset points", fontsize=8.5, color=TXT)
    ax.set_yscale("log")
    ax.set_ylabel("kWh por suscriptor y mes (escala log.)")
    ax.legend(loc="upper left", fontsize=9)
    titulo(ax, "Estrato 1: consumo por suscriptor por tipo de lectura y meses atípicos",
           "Banda: 0,5 a 2 veces la mediana móvil de 7 meses de cada tipo; círculos: meses descartados")
    guardar(fig, "sui_atipicos_e1.png", F_O3)
    at = o[o.atipico].copy()
    at["peso_kWh_pct"] = 100 * at.consumo_kWh / o.groupby(["anio", "mes", "estrato"]).consumo_kWh.transform("sum")[at.index]
    t = at[["anio", "mes", "estrato", "lectura", "motivo", "suscriptores", "consumo_kWh", "kWh_susc", "mediana7", "razon"]]
    tabla(t.round(2).sort_values(["estrato", "anio", "mes"]), "sui_atipicos_o3.csv", index=False)
    res = at[at.motivo == "mediana móvil"].groupby("estrato").agg(celdas=("mes", "size"), susc_mediana=("suscriptores", "median"),
                                    celdas_100_o_mas=("suscriptores", lambda x: int((x >= 100).sum())))
    print(res.to_string())
    print(at[(at.suscriptores >= 100) & (at.motivo == "mediana móvil")][["anio", "mes", "estrato", "lectura", "suscriptores", "kWh_susc", "razon"]].round(2)
          .to_string())
    return at, res


def no_residencial(c, nr):
    ct = c[(c.estrato == "total") & (c.anio >= 2019)].copy()
    ct["f"] = fecha(ct)
    n = nr.copy()
    n["f"] = fecha(n)
    n["kps"] = n.kWh_nores / n.S_nores
    n["r"] = n.kps / n.kps[n.S_nores >= 1000].median()   # 0,5-1,5 veces la mediana de la serie, como las banderas del consolidado
    n["atipico"] = (n.S_nores < 1000) | ~n.r.between(0.5, 1.5)
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
    a = ax[0]
    ok = ~ct.bandera.str.contains("consumo")
    a.plot(ct.f[ok], ct.consumo_kWh[ok] / 1e6, color=PAL[0], lw=2, marker="o", ms=2.5, label="Residencial")
    m_ok = ~n.atipico
    for col, lab, cl in [("kWh_com", "Comercial", PAL[1]), ("kWh_ind", "Industrial", PAL[6]),
                         ("kWh_ofi", "Oficial", PAL[2]), ("kWh_otr", "Otros", PAL[3])]:
        a.plot(n.f[m_ok], n[col][m_ok] / 1e6, color=cl, lw=1.6, marker="o", ms=2.5, label=lab)
    a.scatter(n.f[n.atipico], n.kWh_nores[n.atipico] / 1e6, marker="x", color=PAL[7], s=30, zorder=5,
              label="No residencial total, mes atípico")
    a.set_ylabel("GWh por mes")
    a.set_ylim(0, 340)
    a.legend(fontsize=8.5, ncol=3, loc="upper right")
    titulo(a, "A. Consumo facturado por uso", "Meses válidos; x: total no residencial de los meses atípicos (2020: fuera de escala)")
    b = ax[1]
    for col, lab, cl in [("S_com", "Comercial", PAL[1]), ("S_ind", "Industrial", PAL[6])]:
        b.plot(n.f[n.S_nores >= 1000], n[col][n.S_nores >= 1000] / 1e3, color=cl, lw=1.8, label=lab)
    b.set_ylabel("miles de suscriptores")
    b.legend(fontsize=9)
    titulo(b, "B. Suscriptores no residenciales", "Sin junio de 2022 (16 suscriptores)")
    guardar(fig, "sui_no_residencial.png", "Fuente: SUI, reporte ele_com_096 (Barranquilla, urbano), suma de empresas.")
    # tabla anual con los meses válidos
    n["anio"] = n.anio.astype(int)
    an = n[~n.atipico].groupby("anio")[["kWh_ind", "kWh_com", "kWh_ofi", "kWh_otr", "kWh_nores"]].mean() / 1e6
    an["meses_validos"] = n[~n.atipico].groupby("anio").size()
    res = ct[ok].groupby("anio").consumo_kWh.mean() / 1e6
    an["residencial_GWh_mes"] = res
    an["pct_residencial"] = 100 * an.residencial_GWh_mes / (an.residencial_GWh_mes + an.kWh_nores)
    an.columns = [x.replace("kWh_", "GWh_mes_") for x in an.columns]
    tabla(an.round(1), "sui_no_residencial_anual.csv")
    print(an.round(1).to_string())
    print("meses atípicos no residencial:", n[n.atipico][["anio", "mes"]].astype(str).agg("-".join, axis=1).tolist())
    return an, n


def precio(c, o):
    """COP por kWh facturado (nominal) por estrato y año, del consolidado (meses sin bandera) y de O3 lecturas reales."""
    cc = c[(c.estrato != "total") & (c.bandera == "") & (c.anio <= 2025)]
    p1 = cc.groupby(["anio", "estrato"]).COP_kWh.mean().unstack().round(0)
    p1.columns = [f"cons_E{e}" for e in p1.columns]
    r = o[(o.lectura == "Real") & ~o.atipico]
    p2 = r.groupby(["anio", "estrato"])[["fact_consumo_COP", "consumo_kWh"]].sum()
    p2 = (p2.fact_consumo_COP / p2.consumo_kWh).unstack().round(0)
    p2.columns = [f"real_E{e}" for e in p2.columns]
    p = p1.join(p2)
    tabla(p, "sui_cop_kwh_anual.csv")
    print(p.to_string())
    return p


def main():
    c, nr, o, m = cargar()
    o = atipicos(o, meses_bandera_total(c))
    crudo = leer_crudo_2019()
    verificar(c, o)
    cobertura(c, nr, o, m, crudo)
    comercializadores(crudo, c)
    suscriptores(c, o)
    d, an, pe = series(c, o)
    estacionalidad(d)
    tipos_lectura(o)
    fig_atipicos(o)
    no_residencial(c, nr)
    precio(c, o)
    # cifras sueltas para el texto
    na = o[o.lectura == "n/a"].groupby(["anio", "mes"]).suscriptores.sum()
    tot = o.groupby(["anio", "mes"]).suscriptores.sum()
    f = (100 * na / tot).dropna()
    print("fracción n/a (meses normales): min", round(f[f < 50].min(), 1), "max", round(f[f < 50].max(), 1),
          "; meses >50 %:", f[f > 50].round(1).to_dict())
    print("meses válidos con lecturas reales por estrato, 2015-2025 sin 2020:",
          d[(d.anio != 2020)].groupby("estrato").reales.count().to_dict())


if __name__ == "__main__":
    main()
