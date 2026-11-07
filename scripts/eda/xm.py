"""EDA de la demanda horaria de XM (API pública servapibi.xm.com.co) que usa la compuerta horaria.

Lee los parquet que arma scripts/compuerta/02_descargar_xm.py (mercados CARIBE SOL y COSTA CARIBE, agentes de
Electricaribe y Air-e, demanda no atendida por subárea) y el clima diario de 01_clima.py, y escribe figuras en
figuras/eda/xm_*.png y tablas agregadas en tablas/eda/xm_*.csv.

El año 2026 está reservado para la prueba ciega: solo entra en la tabla de cobertura, no en los análisis.
Uso (desde la raíz del repositorio):  python scripts/eda/xm.py
"""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from estilo import *  # noqa: E402,F401,F403
from estilo import TXT2  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

np.random.seed(SEMILLA)

# ------------------------------------------------------------------ rutas y funciones de la compuerta
# Los datos están en scripts/compuerta/datos/ si se reconstruyeron dentro del repositorio; si no, en la carpeta de
# trabajo original de la compuerta horaria.
CANDIDATAS = [REPO / "scripts" / "compuerta", ML / "compuerta_horaria" / "scripts"]
for _c in CANDIDATAS:
    _raiz = _c if (_c / "datos" / "procesados").exists() else _c.parent
    if (_raiz / "datos" / "procesados" / "xm_mercados_horario.parquet").exists():
        PROC, SCRIPTS_COMPUERTA, DATOS = _raiz / "datos" / "procesados", _c, _raiz / "datos"
        break
else:
    raise FileNotFoundError("No se encontraron los parquet de XM; corra scripts/compuerta/02_descargar_xm.py")


def _modulo(nombre, archivo):
    spec = importlib.util.spec_from_file_location(nombre, archivo)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nombre] = mod
    spec.loader.exec_module(mod)
    return mod


comun = _modulo("comun", SCRIPTS_COMPUERTA / "comun.py")
calendario = comun.calendario
UMBRAL_DNA, UMBRAL_ANOMALIA = 0.005, 0.12        # los mismos de 03_estimar.py
FIN_EDA = pd.Timestamp("2025-12-31")
EVENTOS = [("2016-11-15", "EDCC → EDIC\n(intervención)"), ("2020-03-25", "Cuarentena\nnacional"),
           ("2020-10-01", "Air-e\n(CSSC)"), ("2024-09-13", "CSSC → CSIC\n(intervención)")]
FUENTE = "Fuente: XM, API pública (servapibi.xm.com.co). Cálculos propios."
coma = FuncFormatter(lambda v, _: fmt(v, 0) if abs(v - round(v)) < 1e-9 else fmt(v, 1))


def marcar_anomalias(L, cal):
    """Copia de 03_estimar.marcar_anomalias: hora > 12 % fuera de la mediana móvil de su hora y tipo de día."""
    marcas = pd.DataFrame(False, index=L.index, columns=L.columns)
    for tipo in cal["tipo_dia"].unique():
        idx = cal.index[cal["tipo_dia"] == tipo].intersection(L.index)
        sub = L.loc[idx]
        med = sub.rolling(29 if tipo == "laboral" else 9, center=True, min_periods=5).median()
        marcas.loc[idx] = (np.abs(sub / med - 1) > UMBRAL_ANOMALIA) | sub.isna() | (sub <= 0)
    return marcas


def desvio_mediana(L, cal):
    """Cociente de cada hora con la mediana móvil de su hora y tipo de día (para el histograma)."""
    r = pd.DataFrame(np.nan, index=L.index, columns=L.columns)
    for tipo in cal["tipo_dia"].unique():
        idx = cal.index[cal["tipo_dia"] == tipo].intersection(L.index)
        sub = L.loc[idx]
        r.loc[idx] = sub / sub.rolling(29 if tipo == "laboral" else 9, center=True, min_periods=5).median()
    return r


def lineas_eventos(ax, texto=True, y=0.98):
    for f, t in EVENTOS:
        x = pd.Timestamp(f)
        ax.axvline(x, color=TXT2, lw=.8, ls="--", zorder=1)
        if texto:
            # la cuarentena y el cambio a Air-e están a seis meses: la etiqueta de la cuarentena va a la izquierda
            izq = f.startswith("2020-03")
            ax.text(x, y, (t + " ") if izq else (" " + t), transform=ax.get_xaxis_transform(), fontsize=8,
                    color=TXT2, va="top", ha="right" if izq else "left")


# ------------------------------------------------------------------ datos
mc = pd.read_parquet(PROC / "xm_mercados_horario.parquet")
ag = pd.read_parquet(PROC / "xm_agentes_horario.parquet")
dna = pd.read_parquet(PROC / "xm_dna_diaria.parquet")
for d in (mc, ag, dna):
    d["fecha"] = pd.to_datetime(d["fecha"])
clima = pd.read_parquet(PROC / "clima_diario.parquet")
clima.index = pd.to_datetime(clima.index).normalize()


def matriz(df):
    return df.pivot_table(index="fecha", columns="hora", values="kwh", aggfunc="sum").sort_index()


sol_reg = matriz(mc[(mc.codigo == "CARIBE SOL") & (mc.tipo_mercado == "REGULADO")])
sol_nreg = matriz(mc[(mc.codigo == "CARIBE SOL") & (mc.tipo_mercado == "NO REGULADO")])
costa_reg = matriz(mc[(mc.codigo == "COSTA CARIBE") & (mc.tipo_mercado == "REGULADO")])
costa_nreg = matriz(mc[(mc.codigo == "COSTA CARIBE") & (mc.tipo_mercado == "NO REGULADO")])
ag_come = matriz(ag[ag.metrica == "DemaComeReg"])        # cadena EDCC → EDIC → CSSC → CSIC, un agente por día
ag_real = matriz(ag[ag.metrica == "DemaRealReg"])
ag_perd = matriz(ag[ag.metrica == "PerdidasEnerReg"])
agente_dia = ag[ag.metrica == "DemaComeReg"].groupby("fecha")["codigo"].first()

# ------------------------------------------------------------------ 1. cobertura
filas = []
series = [("DemaCome / MercadoComercializacion", "CARIBE SOL", "REGULADO"),
          ("DemaCome / MercadoComercializacion", "CARIBE SOL", "NO REGULADO"),
          ("DemaCome / MercadoComercializacion", "COSTA CARIBE", "REGULADO"),
          ("DemaCome / MercadoComercializacion", "COSTA CARIBE", "NO REGULADO")]
for ep, cod, tm in series:
    s = mc[(mc.codigo == cod) & (mc.tipo_mercado == tm)]
    filas.append((ep, f"{cod} ({tm.lower()})", s))
for m in ["DemaRealReg", "PerdidasEnerReg", "DemaComeReg"]:
    for cod in ["EDCC", "EDIC", "CSSC", "CSIC"]:
        filas.append((f"{m} / Agente", cod, ag[(ag.metrica == m) & (ag.codigo == cod)]))
cob = []
for ep, nombre, s in filas:
    ini, fin = s.fecha.min(), s.fecha.max()
    dias_cal = (fin - ini).days + 1
    horas = s.groupby("fecha").size()
    cob.append({"endpoint": ep, "serie": nombre, "frecuencia": "horaria", "inicio": ini.date(), "fin": fin.date(),
                "dias": int(s.fecha.nunique()), "dias_faltantes": int(dias_cal - s.fecha.nunique()),
                "dias_incompletos": int((horas != 24).sum()), "valores_nulos": int(s.kwh.isna().sum()),
                "valores_cero_o_negativos": int((s.kwh <= 0).sum()), "unidad": "kWh por hora"})
for (m, sa), s in dna.groupby(["metrica", "subarea"]):
    cob.append({"endpoint": f"{m} / Subarea", "serie": sa.replace("SUBAREA ", "Subárea "), "frecuencia": "diaria",
                "inicio": s.fecha.min().date(), "fin": s.fecha.max().date(), "dias": int(s.fecha.nunique()),
                "dias_faltantes": np.nan, "dias_incompletos": np.nan, "valores_nulos": int(s.kwh.isna().sum()),
                "valores_cero_o_negativos": int((s.kwh <= 0).sum()), "unidad": "kWh por día (solo días con evento)"})
cob = pd.DataFrame(cob)
cob[["dias_faltantes", "dias_incompletos"]] = cob[["dias_faltantes", "dias_incompletos"]].astype("Int64")
tabla(cob, "xm_cobertura.csv", index=False)
print(cob.to_string())

# A partir de aquí, sin 2026 (prueba ciega)
cortar = lambda x: x[x.index <= FIN_EDA]  # noqa: E731
sol_reg, sol_nreg, costa_reg, costa_nreg = map(cortar, (sol_reg, sol_nreg, costa_reg, costa_nreg))
ag_come, ag_real, ag_perd, agente_dia = map(cortar, (ag_come, ag_real, ag_perd, agente_dia))
dna = dna[dna.fecha <= FIN_EDA]

# ------------------------------------------------------------------ 2. identidades y cocientes entre series
perd_share = (ag_perd.sum(axis=1) / ag_come.sum(axis=1))
ident = ((ag_real + ag_perd) / ag_come - 1).abs().max().max()
cociente_sol = (sol_reg / ag_come.reindex(sol_reg.index))
cociente_costa = (costa_reg / ag_come.reindex(costa_reg.index))
perd_no_pos = ag[(ag.metrica == "PerdidasEnerReg") & (ag.kwh <= 0) & (ag.fecha <= FIN_EDA)]
print("\nIdentidad DemaComeReg = DemaRealReg + PerdidasEnerReg, máx. desvío relativo:", ident)
print("Pérdidas / DemaComeReg (media diaria):", perd_share.mean(), "rango anual",
      perd_share.groupby(perd_share.index.year).mean().round(4).to_dict())
print("Horas con pérdidas <= 0:", len(perd_no_pos), "ceros:", int((perd_no_pos.kwh == 0).sum()),
      "por agente", perd_no_pos.codigo.value_counts().to_dict(), "por año", perd_no_pos.fecha.dt.year.value_counts().sort_index().to_dict())
print("CARIBE SOL reg / agente Air-e (hora):", cociente_sol.stack().describe().round(4).to_dict())
print("Hora de máximo cociente:", cociente_sol.stack().idxmax())
print("COSTA CARIBE reg / agente Electricaribe (hora):", cociente_costa.stack().describe().round(4).to_dict())

# ------------------------------------------------------------------ 3. totales anuales
dia = lambda m: m.sum(axis=1) / 1e6  # GWh/día  # noqa: E731
anual = pd.DataFrame({
    "costa_caribe_regulado_GWh": dia(costa_reg).groupby(costa_reg.index.year).sum(),
    "costa_caribe_no_regulado_GWh": dia(costa_nreg).groupby(costa_nreg.index.year).sum(),
    "caribe_sol_regulado_GWh": dia(sol_reg).groupby(sol_reg.index.year).sum(),
    "caribe_sol_no_regulado_GWh": dia(sol_nreg).groupby(sol_nreg.index.year).sum(),
    "agente_regulado_DemaComeReg_GWh": dia(ag_come).groupby(ag_come.index.year).sum(),
    "perdidas_pct_de_DemaComeReg": 100 * perd_share.groupby(perd_share.index.year).mean(),
})
anual["dias_costa_caribe"] = costa_reg.groupby(costa_reg.index.year).size()
anual["dias_caribe_sol"] = sol_reg.groupby(sol_reg.index.year).size()
anual["agentes"] = agente_dia.groupby(agente_dia.index.year).agg(lambda s: "+".join(dict.fromkeys(s)))
anual["dna_atlantico_GWh"] = dna[dna.subarea == "SUBAREA ATLANTICO"].groupby(dna.fecha.dt.year)["kwh"].sum() / 1e6
anual["dna_gcm_GWh"] = dna[dna.subarea == "SUBAREA GCM"].groupby(dna.fecha.dt.year)["kwh"].sum() / 1e6
anual.index.name = "anio"

# Pandemia y cambio de comercializador (cadena de agentes)
d_ag = dia(ag_come)
m_ag = d_ag.groupby(d_ag.index.to_period("M")).mean()
pandemia = {f"{m}": 100 * (m_ag[pd.Period(f"2020-{m:02d}")] / m_ag[pd.Period(f"2019-{m:02d}")] - 1) for m in range(1, 10)}
print("\nAgente Electricaribe, demanda media diaria 2020 frente a 2019 (%):", {k: round(v, 1) for k, v in pandemia.items()})
salto = d_ag["2020-10-01":"2020-10-31"].mean() / d_ag["2020-09-01":"2020-09-30"].mean()
print("Octubre 2020 (Air-e) / septiembre 2020 (Electricaribe), agente:", salto)
salto_mc = dia(sol_reg)["2020-10"].mean() / dia(costa_reg)["2020-09"].mean()
print("Octubre 2020 CARIBE SOL / septiembre 2020 COSTA CARIBE, mercado regulado:", salto_mc)
d_csic = d_ag["2024-09-13":"2024-10-12"].mean() / d_ag["2024-08-14":"2024-09-12"].mean()
print("30 días tras CSIC / 30 días antes:", d_csic)

# ------------------------------------------------------------------ 4. calendario, atípicos y DNA (como la compuerta)
cal_sol = calendario(sol_reg.index)
anom_sol = marcar_anomalias(sol_reg, cal_sol)
dna_dia = dna.groupby("fecha")["kwh"].sum()
total_sol = sol_reg + sol_nreg
frac_dna = (dna_dia.reindex(total_sol.index).fillna(0) / total_sol.sum(axis=1))
cal_ag = calendario(ag_come.index)
anom_ag = marcar_anomalias(ag_come, cal_ag)
# para el periodo de Electricaribe la DNA se escala con la demanda total de COSTA CARIBE (2017-2019, descriptivo)
total_costa = costa_reg + costa_nreg
frac_dna_costa = (dna_dia.reindex(total_costa.index).fillna(0) / total_costa.sum(axis=1))

anual["dias_con_horas_anomalas"] = pd.concat([
    anom_ag.any(axis=1)[anom_ag.index < "2020-10-01"], anom_sol.any(axis=1)]).groupby(lambda x: x.year).sum()
anual["horas_anomalas"] = pd.concat([
    anom_ag.sum(axis=1)[anom_ag.index < "2020-10-01"], anom_sol.sum(axis=1)]).groupby(lambda x: x.year).sum()
anual["dias_dna_mayor_0_5pct"] = pd.concat([frac_dna_costa[frac_dna_costa.index < "2020-10-01"],
                                             frac_dna]).gt(UMBRAL_DNA).groupby(lambda x: x.year).sum()
anual.loc[[2015, 2016], "dias_dna_mayor_0_5pct"] = np.nan   # sin COSTA CARIBE para escalar
tabla(anual.round(3), "xm_anual.csv")
print(anual.round(2).to_string())

m21 = (sol_reg.index.year >= 2021)
exc = anom_sol.any(axis=1) | frac_dna.gt(UMBRAL_DNA)
print("\nComprobación con decision.json, 2021-2025: días", int(m21.sum()), "anómalos", int(anom_sol.any(axis=1)[m21].sum()),
      "DNA>0,5 %", int(frac_dna.gt(UMBRAL_DNA)[m21].sum()), "excluidos", int(exc[m21].sum()))
hora_anom = anom_sol[m21].sum()
print("Horas anómalas por hora del día 2021-2025:", hora_anom.to_dict())

# Eventos de DNA más grandes
ev = dna.copy()
ev["mercado_GWh"] = ev.fecha.map(total_sol.sum(axis=1) / 1e6).fillna(ev.fecha.map(total_costa.sum(axis=1) / 1e6))
ev["MWh"] = ev.kwh / 1e3
ev["pct_del_mercado"] = 100 * ev.MWh / 1e3 / ev.mercado_GWh
top = (ev.sort_values("MWh", ascending=False).head(12)[["fecha", "subarea", "metrica", "MWh", "pct_del_mercado"]])
top["fecha"] = top.fecha.dt.date
tabla(top.round(2), "xm_dna_eventos.csv", index=False)
print(top.to_string())
print("Días con DNA > 0 (cualquier subárea y tipo), por año:", dna.groupby(dna.fecha.dt.year).fecha.nunique().to_dict())

# ------------------------------------------------------------------ 5. perfiles horarios
def perfil(L, cal, anios):
    sel = L[L.index.year.isin(anios)]
    c = cal.loc[sel.index]
    tipo = c["tipo_dia"].map({"laboral": "Hábil", "sabado": "Sábado", "dom_fest": "Domingo o festivo"})
    out = (sel / 1e3).groupby(tipo.values).mean().T     # MWh/h
    out.index.name = "hora"
    return out


p_sol = perfil(sol_reg, cal_sol, range(2021, 2026))
p_ele = perfil(ag_come, cal_ag, range(2015, 2020))
perf = pd.concat({"CARIBE SOL regulado 2021-2025": p_sol, "Electricaribe (agente) 2015-2019": p_ele}, axis=1)
tabla(perf.round(1), "xm_perfil_horario.csv")
print(perf.round(0).to_string())
# cociente entre noche y tarde del perfil medio
for nom, p in [("SOL", p_sol), ("ELE", p_ele)]:
    h = p["Hábil"]
    print(nom, "hora máx", h.idxmax(), "hora mín", h.idxmin(), "máx/mín", round(h.max() / h.min(), 3),
          "noche 22-5 / día 6-21", round(h[[22, 23, 0, 1, 2, 3, 4, 5]].mean() / h[list(range(6, 22))].mean(), 3))

# forma por mes (cociente con la media del día), 2021-2025, días hábiles sin excluir
sel = sol_reg[m21 & (cal_sol["tipo_dia"] == "laboral").values & ~exc.values]
forma_mes = sel.div(sel.mean(axis=1), axis=0).groupby(sel.index.month).mean()
forma_mes.index.name = "mes"
tabla(forma_mes.round(4), "xm_forma_mes_hora.csv")
dmes = dia(sol_reg[m21]).groupby(sol_reg[m21].index.month).mean()
print("GWh/día medio por mes 2021-2025:", dmes.round(2).to_dict())

# ------------------------------------------------------------------ 6. demanda y calor (descriptivo)
dd = pd.DataFrame({"gwh": dia(sol_reg)}).join(clima[["hi_media"]], how="inner").join(cal_sol)
dd = dd[(dd.index.year >= 2021) & (dd.tipo_dia == "laboral") & ~exc.reindex(dd.index).values
        & ~dd.fin_anio & ~dd.carnaval & ~dd.semana_santa]
dd["am"] = dd.index.to_period("M")
dd["y"] = 100 * np.log(dd.gwh)
dd["y_c"] = dd.y - dd.groupby("am").y.transform("mean")
dd["hi_c"] = dd.hi_media - dd.groupby("am").hi_media.transform("mean")
pend = np.polyfit(dd.hi_c, dd.y_c, 1)
pend_anio = {a: np.polyfit(g.hi_c, g.y_c, 1)[0] for a, g in dd.groupby(dd.index.year)}
r_total = np.corrcoef(dd.hi_media, dd.gwh)[0, 1]
r_c = np.corrcoef(dd.hi_c, dd.y_c)[0, 1]
print(f"\nDispersión: {len(dd)} días hábiles; pendiente dentro del mes {pend[0]:.3f} %/°C; r bruto {r_total:.3f}; r dentro del mes {r_c:.3f}")
print("Pendiente por año:", {k: round(v, 2) for k, v in pend_anio.items()})
disp = pd.DataFrame({"anio": list(pend_anio) + ["2021-2025"], "pendiente_pct_por_C": list(pend_anio.values()) + [pend[0]],
                     "dias": [int((dd.index.year == a).sum()) for a in pend_anio] + [len(dd)]})
tabla(disp.round(3), "xm_pendiente_dentro_mes.csv", index=False)

# ================================================================== FIGURAS
# Fig. 1: serie diaria y estacionalidad mensual
fig, axs = plt.subplots(2, 1, figsize=(12, 9.8), gridspec_kw={"height_ratios": [1.3, 1]})
ax = axs[0]
colores_ag = {"EDCC": PAL[2], "EDIC": PAL[2], "CSSC": PAL[0], "CSIC": PAL[0]}
for cod, g in d_ag.groupby(agente_dia.reindex(d_ag.index).values):
    ax.plot(g.index, g.values, color=colores_ag[cod], lw=.4, alpha=.35)
roll = d_ag.rolling(30, center=True, min_periods=20).mean()
pre = roll.index < "2020-10-01"
ax.plot(roll.index[pre], roll[pre], color=PAL[2], lw=2, label="Agente Electricaribe (EDCC, EDIC), media de 30 días")
ax.plot(roll.index[~pre], roll[~pre], color=PAL[0], lw=2, label="Agente Air-e (CSSC, CSIC), media de 30 días")
for m, col, lab in [(costa_reg, PAL[3], "Mercado COSTA CARIBE regulado"), (sol_reg, PAL[1], "Mercado CARIBE SOL regulado")]:
    s = dia(m).rolling(30, center=True, min_periods=20).mean()
    ax.plot(s.index, s.values, color=col, lw=1.4, ls=(0, (4, 2)), label=lab + ", media de 30 días")
lineas_eventos(ax)
ax.set_ylabel("GWh por día")
ax.set_ylim(0, None)
ax.yaxis.set_major_formatter(coma)
ax.legend(loc="lower left", fontsize=9, ncol=2)
titulo(ax, "(a) Demanda regulada diaria, 2015–2025",
       "Líneas finas: valor diario del agente. El salto de 2020 es de área: de siete a tres departamentos")
ax = axs[1]
rampa = ["#a9c8ef", "#7aa9e6", "#4a89dc", "#2a6fc0", "#1b4f8f"]
dsol = dia(sol_reg)
for a, c in zip(range(2021, 2026), rampa):
    s = dsol[dsol.index.year == a]
    ax.plot(range(1, 13), s.groupby(s.index.month).mean().values, color=c, lw=2, marker="o", ms=4, label=str(a))
dpre = d_ag[d_ag.index.year <= 2019]
ax2 = ax.twinx()
ax2.plot(range(1, 13), dpre.groupby(dpre.index.month).mean().values, color=PAL[2], lw=1.6, ls="--",
         label="Electricaribe 2015–2019 (eje derecho)")
ax2.set_ylabel("GWh por día (Electricaribe)", color=PAL[2])
ax2.spines["right"].set_visible(True)
ax2.grid(False)
ax2.yaxis.set_major_formatter(coma)
ax.set_xticks(range(1, 13))
ax.set_xticklabels(["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"])
ax.set_ylabel("GWh por día (CARIBE SOL)")
ax.yaxis.set_major_formatter(coma)
h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, ncol=6, fontsize=9, loc="upper center", bbox_to_anchor=(0.5, -0.1))
titulo(ax, "(b) Demanda media diaria por mes", "Mercado CARIBE SOL regulado por año y agente de Electricaribe 2015–2019")
guardar(fig, "xm_serie_diaria.png", FUENTE)

# Fig. 2: perfil horario por tipo de día y forma por mes
fig, axs = plt.subplots(1, 2, figsize=(13, 5.2), gridspec_kw={"width_ratios": [1, 1.15]})
ax = axs[0]
for tipo, col in [("Hábil", PAL[0]), ("Sábado", PAL[3]), ("Domingo o festivo", PAL[1])]:
    ax.plot(p_sol.index, p_sol[tipo], color=col, lw=2, marker="o", ms=3, label=tipo)
ax.axvspan(-0.5, 5.5, color="#ecebe6", zorder=0, lw=0)
ax.axvspan(21.5, 23.5, color="#ecebe6", zorder=0, lw=0)
ax.set_xlim(-0.5, 23.5)
ax.set_xticks(range(0, 24, 2))
ax.set_xlabel("Hora local (inicio del intervalo)")
ax.set_ylabel("MWh por hora")
ax.yaxis.set_major_formatter(coma)
ax.legend(loc="lower right")
titulo(ax, "(a) Perfil medio por tipo de día", "CARIBE SOL regulado, 2021–2025 (sombreado: 22 a 5 h)")
ax = axs[1]
im = ax.imshow(forma_mes.values, aspect="auto", cmap="RdBu_r", vmin=0.8, vmax=1.2)
ax.set_xticks(range(0, 24, 2))
ax.set_yticks(range(12))
ax.set_yticklabels(["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"])
ax.set_xlabel("Hora local (inicio del intervalo)")
ax.grid(False)
cb = fig.colorbar(im, ax=ax, fraction=.04, pad=.02)
cb.set_label("Demanda de la hora / media del día")
cb.ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: fmt(v, 2)))
titulo(ax, "(b) Forma horaria por mes", "Días hábiles no excluidos, 2021–2025")
guardar(fig, "xm_perfil_horario.png", FUENTE)

# Fig. 3: atípicos (regla de la compuerta)
ratio = desvio_mediana(sol_reg[m21], cal_sol[m21])
fig, axs = plt.subplots(1, 2, figsize=(13, 5))
ax = axs[0]
v = ratio.stack().dropna().values
ax.hist(np.clip(v, 0.5, 1.5), bins=np.linspace(0.5, 1.5, 101), color=PAL[0], log=True)
for x in (1 - UMBRAL_ANOMALIA, 1 + UMBRAL_ANOMALIA):
    ax.axvline(x, color=PAL[7], lw=1.2, ls="--")
ax.set_xlabel("Demanda de la hora / mediana móvil de su hora y tipo de día")
ax.set_ylabel("Horas (escala logarítmica)")
ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: fmt(x, 1)))
titulo(ax, "(a) Desvío frente a la mediana móvil", "CARIBE SOL regulado, 2021–2025; líneas: umbral de ±12 %")
ax = axs[1]
an = anual.loc[2015:2025]
x = np.arange(len(an))
ax.bar(x - 0.2, an["dias_con_horas_anomalas"], 0.4, color=PAL[0], label="Días con alguna hora anómala")
ax.bar(x + 0.2, an["dias_dna_mayor_0_5pct"].fillna(0), 0.4, color=PAL[1], label="Días con DNA > 0,5 % del mercado")
ax.set_xticks(x)
ax.set_xticklabels(an.index)
ax.set_ylabel("Días")
ax.set_ylim(0, 78)
ax.legend(loc="upper left")
titulo(ax, "(b) Días marcados por año",
       "Agente Electricaribe hasta sep-2020 y CARIBE SOL desde oct-2020; DNA sin 2015–2016")
guardar(fig, "xm_atipicos.png", FUENTE)

# Fig. 4: demanda no atendida
fig, axs = plt.subplots(2, 1, figsize=(12, 8))
ax = axs[0]
mens = dna.assign(mes=dna.fecha.dt.to_period("M").dt.to_timestamp()).pivot_table(
    index="mes", columns=["subarea", "metrica"], values="kwh", aggfunc="sum").fillna(0) / 1e6
mens = mens.reindex(pd.date_range("2015-01-01", "2025-12-01", freq="MS"), fill_value=0)
abajo = np.zeros(len(mens))
etq = {("SUBAREA ATLANTICO", "DemaNoAtenProg"): ("Atlántico, programada", PAL[0]),
       ("SUBAREA ATLANTICO", "DemaNoAtenNoProg"): ("Atlántico, no programada", "#7aa9e6"),
       ("SUBAREA GCM", "DemaNoAtenProg"): ("GCM, programada", PAL[1]),
       ("SUBAREA GCM", "DemaNoAtenNoProg"): ("GCM, no programada", "#f3a37f")}
for k, (lab, col) in etq.items():
    if k in mens:
        ax.bar(mens.index, mens[k].values, width=25, bottom=abajo, color=col, label=lab)
        abajo += mens[k].values
lineas_eventos(ax, texto=False)
ax.set_ylabel("GWh por mes")
ax.set_ylim(0, mens.sum(axis=1).max() * 1.25)
ax.yaxis.set_major_formatter(coma)
ax.legend(loc="upper left", ncol=4, fontsize=9)
titulo(ax, "(a) Demanda no atendida mensual por subárea y tipo", "GCM: Guajira, Cesar y Magdalena")
ax = axs[1]
f = 100 * frac_dna[m21]
fp = f[f > 0]
ax.scatter(fp.index, fp.values, s=7, color=np.where(fp > 100 * UMBRAL_DNA, PAL[1], PAL[0]), lw=0)
ax.axhline(100 * UMBRAL_DNA, color=PAL[7], lw=1.2, ls="--")
ax.set_yscale("log")
ax.set_ylabel("% de la demanda total de CARIBE SOL")
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: fmt(v, 3).rstrip("0").rstrip(",")))
ax.text(fp.index[3], 100 * UMBRAL_DNA * 1.25, "umbral de exclusión: 0,5 %", color=PAL[7], fontsize=9)
titulo(ax, "(b) DNA diaria de Atlántico y GCM frente a la demanda del mercado, 2021–2025",
       f"Solo los {len(fp)} de {len(f)} días con DNA; naranja: días excluidos de la compuerta")
guardar(fig, "xm_dna.png", FUENTE)

# Fig. 5: demanda y calor
fig, axs = plt.subplots(1, 2, figsize=(13, 5.4))
ax = axs[0]
for a, c in zip(range(2021, 2026), rampa):
    g = dd[dd.index.year == a]
    ax.scatter(g.hi_media, g.gwh, s=9, color=c, alpha=.8, label=str(a), lw=0)
ax.set_xlabel("Índice de calor medio del día, ERA5-Land (°C)")
ax.set_ylabel("GWh por día")
ax.yaxis.set_major_formatter(coma)
ax.legend(ncol=5, loc="upper left", fontsize=9, markerscale=2)
titulo(ax, "(a) Demanda diaria e índice de calor", "CARIBE SOL regulado, días hábiles no excluidos")
ax = axs[1]
ax.scatter(dd.hi_c, dd.y_c, s=8, color=PAL[0], alpha=.5, lw=0)
xs = np.linspace(dd.hi_c.min(), dd.hi_c.max(), 10)
ax.plot(xs, np.polyval(pend, xs), color=PAL[1], lw=2,
        label=f"pendiente {fmt(pend[0], 2)} %/°C (r = {fmt(r_c, 2)})")
ax.set_xlabel("Índice de calor menos la media de su año-mes (°C)")
ax.set_ylabel("100·ln(demanda) menos la media del año-mes")
ax.xaxis.set_major_formatter(coma)
ax.yaxis.set_major_formatter(coma)
ax.legend(loc="upper left")
titulo(ax, "(b) Variación dentro de cada mes", "Misma muestra; quita la estacionalidad y el crecimiento")
guardar(fig, "xm_dispersion_calor.png", FUENTE + " Clima: ERA5-Land de GDEX (celda de Barranquilla).")

print("\nFiguras en", FIG, "y tablas en", TAB)
