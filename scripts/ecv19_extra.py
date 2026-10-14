"""Cálculos adicionales con la ECV 2019 (Barranquilla):
1) horas de ventilador con y sin AC por estrato (insumo de p_c)
2) distribución de horas de AC (prior del número de equipos)
4) techo x tipo de vivienda x estrato y logit AC ~ techo
"""
import pandas as pd, numpy as np, statsmodels.api as sm, pickle

d = pd.read_csv('/mnt/user-data/outputs/ECV2019_Barranquilla_consolidado.csv', sep=None, engine='python')
d.columns = [c.replace('﻿', '') for c in d.columns]
d['W'] = pd.to_numeric(d.FEX_C.astype(str).str.replace(',', '.'), errors='coerce')
d['E'] = pd.to_numeric(d.ESTRATO, errors='coerce')
d = d[d.E.between(1, 6)].copy()          # 0 = sin estrato (rural) se excluye
G = {1: 'E1', 2: 'E2', 3: 'E3', 4: 'E4', 5: 'E5', 6: 'E6'}
d['EST'] = d.E.map(G)
T = {}

def wmean(x, w):
    m = x.notna(); return np.nan if m.sum() == 0 else float((x[m] * w[m]).sum() / w[m].sum())

def wq(x, w, q):
    m = x.notna(); x, w = x[m].values, w[m].values
    if len(x) == 0: return np.nan
    o = np.argsort(x); x, w = x[o], w[o]; c = np.cumsum(w) / w.sum()
    return float(x[np.searchsorted(c, q)])

def wpct(mask, w):
    return float(w[mask].sum() / w.sum() * 100)

# ---------- 1) ventilador con / sin AC ----------
hv = pd.to_numeric(d.HORAS_VENTILADOR_P5526, errors='coerce')
hv = hv.where(hv.between(0, 24))            # >24 h/día = error de captura
d['HV'] = hv
rows = []
for est, g in list(d.groupby('EST')) + [('Total', d)]:
    for ac, gg in [(1, g[g.TIENE_AC == 1]), (0, g[g.TIENE_AC == 0])]:
        f = gg[gg.TIENE_VENTILADOR == 1]
        rows.append(dict(estrato=est, tiene_ac='Sí' if ac else 'No', n_hogares=len(gg),
                         pct_con_ventilador=round(wpct(gg.TIENE_VENTILADOR == 1, gg.W), 1),
                         n_con_vent_y_horas=int(f.HV.notna().sum()),
                         horas_vent_media=round(wmean(f.HV, f.W), 1),
                         horas_vent_mediana=wq(f.HV, f.W, .5),
                         p25=wq(f.HV, f.W, .25), p75=wq(f.HV, f.W, .75)))
t1 = pd.DataFrame(rows)
# razón horas con AC / sin AC por estrato
r = t1.pivot(index='estrato', columns='tiene_ac', values='horas_vent_media')
r['razon_conAC_sinAC'] = (r['Sí'] / r['No']).round(2)
r['p_c_desplazado'] = (1 - r['Sí'] / r['No']).round(2)
T['vent_con_sin_ac'] = t1
T['vent_razon'] = r.reset_index()
print(t1.to_string()); print(r)

# ---------- 2) horas de AC (prior de equipos) ----------
ha = pd.to_numeric(d.HORAS_AC_P5524, errors='coerce')
ha = ha.where(ha.between(0, 24))
d['HA'] = ha
rows = []
for est, g in list(d.groupby('EST')) + [('Total', d)]:
    a = g[(g.TIENE_AC == 1) & g.HA.notna()]
    rows.append(dict(estrato=est, n_hogares_ac=len(a),
                     horas_media=round(wmean(a.HA, a.W), 1), horas_mediana=wq(a.HA, a.W, .5),
                     pct_0h=round(wpct(a.HA == 0, a.W), 1),
                     pct_mas_8h=round(wpct(a.HA > 8, a.W), 1),
                     pct_12h_o_mas=round(wpct(a.HA >= 12, a.W), 1),
                     pct_mas_12h=round(wpct(a.HA > 12, a.W), 1),
                     pct_16h_o_mas=round(wpct(a.HA >= 16, a.W), 1),
                     pct_24h=round(wpct(a.HA == 24, a.W), 1),
                     pct_minisplit=round(wpct(g.loc[g.TIENE_AC == 1, 'TIPO_AC_P5523'] == 1, g.loc[g.TIENE_AC == 1, 'W']), 1),
                     pct_ventana=round(wpct(g.loc[g.TIENE_AC == 1, 'TIPO_AC_P5523'] == 2, g.loc[g.TIENE_AC == 1, 'W']), 1),
                     pct_central=round(wpct(g.loc[g.TIENE_AC == 1, 'TIPO_AC_P5523'] == 3, g.loc[g.TIENE_AC == 1, 'W']), 1)))
t2 = pd.DataFrame(rows); T['horas_ac_dist'] = t2; print(t2.to_string())
# histograma de horas (total)
a = d[(d.TIENE_AC == 1) & d.HA.notna()]
bins = [-0.1, 0, 4, 8, 12, 16, 23.9, 24]
lab = ['0', '1–4', '5–8', '9–12', '13–16', '17–23', '24']
T['horas_ac_hist'] = (a.groupby([a.EST.where(a.E <= 4, 'E5-6').where(a.E > 2, 'E1-2').where(a.E > 0), pd.cut(a.HA, bins, labels=lab)], observed=False)
                      .W.sum().groupby(level=0).transform(lambda s: s / s.sum() * 100).round(1).unstack())
print(T['horas_ac_hist'])
# n invalid
print('AC horas >24 excluidas:', int(((pd.to_numeric(d.HORAS_AC_P5524, errors='coerce') > 24)).sum()),
      'vent horas >24 excluidas:', int((pd.to_numeric(d.HORAS_VENTILADOR_P5526, errors='coerce') > 24).sum()))

# ---------- 4) techo x tipo de vivienda x estrato ----------
TE = {1: 'Concreto', 2: 'Teja de barro', 3: 'Asbesto-cemento', 4: 'Zinc/metálica', 5: 'Teja plástica'}
TV = {1: 'Casa', 2: 'Apartamento', 3: 'Cuarto', 5: 'Otro'}
d['TECHO'] = pd.to_numeric(d.TECHO_P4567, errors='coerce').map(TE).fillna('Otro')
d['TIPO'] = pd.to_numeric(d.TIPO_VIVIENDA_P1070, errors='coerce').map(TV).fillna('Otro')
d['TIPO2'] = d.TIPO.replace({'Cuarto': 'Casa/cuarto', 'Casa': 'Casa/cuarto', 'Otro': 'Casa/cuarto'})
rows = []
for est, g in list(d.groupby('EST')) + [('Total', d)]:
    for tp, gg in g.groupby('TIPO2'):
        row = dict(estrato=est, tipo=tp, n=len(gg), pct_hogares_estrato=round(gg.W.sum() / g.W.sum() * 100, 1))
        for k in ['Concreto', 'Asbesto-cemento', 'Zinc/metálica', 'Teja de barro', 'Teja plástica', 'Otro']:
            row[k] = round(wpct(gg.TECHO == k, gg.W), 1)
        row['AC_%'] = round(wpct(gg.TIENE_AC == 1, gg.W), 1)
        rows.append(row)
t4 = pd.DataFrame(rows); T['techo_tipo_estrato'] = t4; print(t4.to_string())
# AC por techo dentro de estrato
rows = []
for (est, te), g in d.groupby(['EST', 'TECHO']):
    rows.append(dict(estrato=est, techo=te, n=len(g), ac=round(wpct(g.TIENE_AC == 1, g.W), 1)))
T['ac_techo_estrato'] = pd.DataFrame(rows).pivot(index='estrato', columns='techo', values=['ac', 'n'])
print(T['ac_techo_estrato'])

# ---------- logit ponderado ----------
m = d.copy()
m['T3'] = m.TECHO.map({'Concreto': 'Concreto', 'Asbesto-cemento': 'Asbesto', 'Zinc/metálica': 'Zinc/otro'}).fillna('Zinc/otro')
m['lny'] = np.log(pd.to_numeric(m.INGRESO_PERCAPITA.astype(str).str.replace(',', '.'), errors='coerce').clip(lower=1e4))
m['wn'] = m.W / m.W.mean()                     # pesos normalizados (suman n)

def logit(cols, data):
    X = pd.get_dummies(data[cols], drop_first=False).astype(float)
    drop = [c for c in X.columns if c in ('T3_Concreto', 'EG_E1-2', 'TIPO2_Casa/cuarto')]
    X = sm.add_constant(X.drop(columns=drop))
    res = sm.GLM(data.TIENE_AC.astype(float), X, family=sm.families.Binomial(), var_weights=data.wn).fit(cov_type='HC1')
    out = pd.DataFrame({'coef': res.params, 'OR': np.exp(res.params), 'IC95_inf': np.exp(res.conf_int()[0]),
                        'IC95_sup': np.exp(res.conf_int()[1]), 'p': res.pvalues}).round(3)
    return out, res

m['EG'] = m.E.map({1: 'E1-2', 2: 'E1-2', 3: 'E3', 4: 'E4', 5: 'E5-6', 6: 'E5-6'})
mods = {}
mods['M1: techo'] = logit(['T3'], m)
mods['M2: techo + estrato'] = logit(['T3', 'EG'], m)
mm = m[m.lny.notna()].copy()
mods['M3: techo + estrato + tipo + ln(ingreso pc)'] = logit(['T3', 'EG', 'TIPO2', 'lny'], mm)
for k, (o, res) in mods.items():
    print('\n', k, 'n=', int(res.nobs), 'pseudoR2(McF)=', round(1 - res.llf / res.llnull, 3)); print(o)
T['logit'] = pd.concat({k: o.assign(n=int(r.nobs), pseudoR2=round(1 - r.llf / r.llnull, 3)) for k, (o, r) in mods.items()}).reset_index().rename(columns={'level_0': 'modelo', 'level_1': 'variable'})
pickle.dump(T, open('/home/claude/work/extra_ecv19.pkl', 'wb'))
