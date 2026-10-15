"""Estrato 1: viviendas del catastro en edificios de 4 o más pisos frente al techo declarado en la ECV.

1. Revisa total_plantas y planta_ubicacion en el estrato 1 (coherencia con el uso «Apartamentos 4 y más pisos»).
2. Agrupa las unidades en lotes matriz (npn_edificio) y describe su altura, área, cuartos y año registrado.
3. Compara la fracción de viviendas con otra vivienda encima (catastro) con la fracción de hogares con techo de
   plancha (ECV 2019 y 2024) y busca en la ECV 2024 los segmentos con perfil de bloque de apartamentos.
4. Sensibilidad: tenencia de A/C de E1 2024 si la ECV tuviera la proporción de apartamentos con placa del catastro.
Salidas: tabla por lote, resumen y figura.
"""
import numpy as np, pandas as pd
from scipy import stats
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

OUT_T = '/home/claude/book/site/tablas/'; OUT_F = '/home/claude/book/site/figuras/'
PAL = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#6250d6', '#e34948']
TXT = '#0b0b0b'; TXT2 = '#52514e'; GRID = '#e4e3df'
plt.rcParams.update({'font.size': 11, 'font.family': 'DejaVu Sans', 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.edgecolor': '#9a9993', 'axes.labelcolor': TXT2, 'xtick.color': TXT2, 'ytick.color': TXT2,
                     'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': .8, 'axes.axisbelow': True,
                     'axes.titlelocation': 'left', 'axes.titlesize': 13, 'axes.titlecolor': TXT, 'legend.frameon': False,
                     'figure.facecolor': '#fcfcfb', 'axes.facecolor': '#fcfcfb'})
fmt = lambda v, d=1: f'{v:.{d}f}'.replace('.', ',')

# ---------- 1. catastro ----------
d = pd.read_pickle('/home/claude/work/catastro_limpio.pkl')
d['APT4'] = d.uso.str.contains('Apartamentos')
d['p_fin'] = d.planta_ubicacion + d.total_plantas.fillna(1).clip(lower=1) - 1
d = d.join(d.groupby('npn_edificio').p_fin.max().rename('techo_lote'), on='npn_edificio')
e = d[d.estrato_num == 1].copy()
a = e[e.APT4].copy()
R = {}
R['viviendas_E1'] = len(e); R['apt4_E1'] = len(a); R['pct_apt4'] = len(a) / len(e) * 100
R['lotes_apt4'] = a.npn_edificio.nunique()
R['hasta3_total_plantas_mayor3'] = int(((~e.APT4) & (e.total_plantas > 3)).sum())
R['apt4_en_lote_techo_menor4'] = int((a.techo_lote < 4).sum())
R['apt4_area_mediana'] = a.area_construida.median(); R['apt4_hab_mediana'] = a.total_habitaciones.median()
pos = np.where(a.p_fin >= a.techo_lote, 'ultimo', np.where(a.planta_ubicacion <= 1, 'primero', 'intermedio'))
for k, v in pd.Series(pos).value_counts(normalize=True).items(): R['apt4_pos_' + k] = v * 100
R['apt4_con_vivienda_encima_pct_E1'] = (pos != 'ultimo').mean() * len(a) / len(e) * 100
# posición en todo E1 (casa / último / intermedio / primer piso con vivienda encima)
pos_all = np.where(e.planta_ubicacion.isna(), 'sin dato', np.where(e.p_fin >= e.techo_lote, 'bajo cubierta', 'con vivienda encima'))
R['E1_con_vivienda_encima_pct'] = (pos_all == 'con vivienda encima').mean() * 100
# año registrado
R['apt4_anio_antes1975_E1'] = int((a.anio_construccion < 1975).sum())
R['apt4_anio_antes1975_E2'] = int(((d.estrato_num == 2) & d.APT4 & (d.anio_construccion < 1975)).sum())
R['apt4_anio_antes1975_E3a6'] = int(((d.estrato_num >= 3) & d.APT4 & (d.anio_construccion < 1975)).sum())
R['apt4_desde2019_E1'] = int((a.anio_construccion >= 2019).sum())

lotes = a.groupby('npn_edificio').agg(
    zona_sector=('numero_predial_nacional', lambda s: s.iat[0][5:9]), unidades=('id_fila', 'size'),
    piso_max=('techo_lote', 'max'), area_mediana_m2=('area_construida', 'median'),
    habitaciones_mediana=('total_habitaciones', 'median'), anio_registrado_mediana=('anio_construccion', 'median'),
    lat=('centroide_lat', 'median'), lon=('centroide_lon', 'median')).sort_values('unidades', ascending=False)
lotes['anio_implausible'] = lotes.anio_registrado_mediana < 1975
lotes.reset_index().to_csv(OUT_T + 'Catastro_E1_edificios_4pisos_por_lote.csv', sep=';', index=False, encoding='utf-8-sig', decimal=',')

# ---------- 2. ECV ----------
TE = {1: 'Concreto', 2: 'Teja de barro', 3: 'Asbesto-cemento', 4: 'Zinc/metálica', 5: 'Teja plástica'}
h = pd.read_csv('/mnt/user-data/outputs/ECV2024_Barranquilla_hogares.csv', sep=';', dtype={'DIRECTORIO': str})
seg = pd.read_csv('/home/claude/work/ecv24/c/dis.csv', sep=';', dtype=str, encoding='latin-1')[['DIRECTORIO', 'SEGMENTO']].drop_duplicates()
h = h.merge(seg, on='DIRECTORIO'); h['W'] = pd.to_numeric(h.FEX_C)
g = h[h.ESTRATO == 1].copy()
g['conc'] = g.P4567 == 1; g['apto_conc'] = (g.TIPO_VIVIENDA == 2) & g.conc
w = lambda m, s: float(s.W[m].sum() / s.W.sum() * 100)
R['ecv24_E1_n'] = len(g); R['ecv24_E1_concreto'] = w(g.conc, g); R['ecv24_E1_apto_concreto'] = w(g.apto_conc, g)
R['ecv24_E1_casa_concreto'] = w(g.conc[g.TIPO_VIVIENDA == 1], g[g.TIPO_VIVIENDA == 1])
c = pd.read_csv('/mnt/user-data/outputs/ECV2019_Barranquilla_consolidado.csv', sep=None, engine='python')
c.columns = [x.replace('﻿', '') for x in c.columns]
c['W'] = pd.to_numeric(c.FEX_C.astype(str).str.replace(',', '.'), errors='coerce')
c = c[pd.to_numeric(c.ESTRATO, errors='coerce') == 1]
tc = pd.to_numeric(c.TECHO_P4567, errors='coerce'); tv = pd.to_numeric(c.TIPO_VIVIENDA_P1070, errors='coerce')
R['ecv19_E1_concreto'] = w(tc == 1, c); R['ecv19_E1_apto_concreto'] = w((tc == 1) & (tv == 2), c)
# segmentos con perfil de bloque de apartamentos (todos los hogares en apartamento y con plancha)
sg = h.groupby('SEGMENTO').agg(tiene_E1=('ESTRATO', lambda x: (x == 1).any()), apto=('TIPO_VIVIENDA', lambda x: (x == 2).mean()),
                               conc=('P4567', lambda x: (x == 1).mean()))
sg1 = sg[sg.tiene_E1]
R['ecv24_segmentos_con_E1'] = len(sg1); R['ecv24_segmentos_E1_bloque'] = int(((sg1.apto >= .99) & (sg1.conc >= .99)).sum())
R['ecv24_segmentos_E1_bloque_esperados'] = len(sg1) * R['pct_apt4'] / 100
R['p_binomial_bloques'] = float(stats.binom.cdf(R['ecv24_segmentos_E1_bloque'], len(sg1), R['pct_apt4'] / 100))
# A/C de E1 2024 por grupo y reponderación
ac = lambda m: float((g.TIENE_AC * g.W)[m].sum() / g.W[m].sum() * 100)
R['ecv24_ac_apto_concreto'] = ac(g.apto_conc); R['ecv24_ac_resto'] = ac(~g.apto_conc); R['ecv24_ac_E1'] = ac(g.W > 0)
R['ecv24_n_apto_concreto'] = int(g.apto_conc.sum()); R['ecv24_seg_apto_concreto'] = g[g.apto_conc].SEGMENTO.nunique()
for nombre, t in [('rep_con_vivienda_encima', R['apt4_con_vivienda_encima_pct_E1']), ('rep_apt4', R['pct_apt4'])]:
    R['ecv24_ac_E1_' + nombre] = t / 100 * R['ecv24_ac_apto_concreto'] + (1 - t / 100) * R['ecv24_ac_resto']
ac19 = lambda m: float((c.TIENE_AC * c.W)[m].sum() / c.W[m].sum() * 100)
R['ecv19_ac_apto_concreto'] = ac19((tc == 1) & (tv == 2)); R['ecv19_ac_resto'] = ac19(~((tc == 1) & (tv == 2)))
pd.Series(R).to_csv(OUT_T + 'Catastro_ECV_E1_edificios_resumen.csv', sep=';', header=['valor'], encoding='utf-8-sig', decimal=',')
for k, v in R.items(): print(f'{k}: {v:.2f}' if isinstance(v, float) else f'{k}: {v}')

# ---------- 3. figura (dos paneles horizontales) ----------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6.4), gridspec_kw={'width_ratios': [1.05, 1]})
casas = e[(~e.APT4) & e.tiene_coordenadas]
ax1.scatter(casas.centroide_lon, casas.centroide_lat, s=1, c='#c9c8c3', alpha=.35, lw=0, label='Otras viviendas de E1')
for flag, col, lab in [(False, PAL[0], 'Lote de edificios 4+ (año registrado plausible)'), (True, PAL[1], 'Lote de edificios 4+ (año registrado 1932–1972)')]:
    L = lotes[lotes.anio_implausible == flag]
    ax1.scatter(L.lon, L.lat, s=L.unidades / 4, c=col, alpha=.75, edgecolors='white', lw=.6, label=lab)
ax1.set_xlabel('Longitud'); ax1.set_ylabel('Latitud'); ax1.set_aspect('equal', adjustable='datalim')
from matplotlib.lines import Line2D
hs = [Line2D([], [], ls='', marker='o', ms=6, mfc='#c9c8c3', mec='none', label='Otras viviendas de E1'),
      Line2D([], [], ls='', marker='o', ms=9, mfc=PAL[0], mec='white', alpha=.8, label='Lote de edificios 4+ (año registrado plausible)'),
      Line2D([], [], ls='', marker='o', ms=9, mfc=PAL[1], mec='white', alpha=.8, label='Lote de edificios 4+ (año registrado 1932–1972)')]
ax1.legend(handles=hs, loc='upper left', fontsize=9)
ax1.set_title('32.178 viviendas de E1 están en solo 74 lotes', pad=22, fontweight='bold')
ax1.text(0, 1.02, 'Tamaño del círculo = viviendas del lote; casi todos de 5 pisos, 43 m² de mediana', transform=ax1.transAxes, fontsize=10, color=TXT2)
bars = [('Catastro: con otra vivienda encima', R['E1_con_vivienda_encima_pct'], PAL[2]),
        ('Catastro: en edificio 4+ con vivienda encima', R['apt4_con_vivienda_encima_pct_E1'], PAL[2]),
        ('ECV 2019: techo de plancha', R['ecv19_E1_concreto'], PAL[6]),
        ('ECV 2024: techo de plancha', R['ecv24_E1_concreto'], PAL[6]),
        ('ECV 2024: apartamento con plancha', R['ecv24_E1_apto_concreto'], PAL[6])]
y = np.arange(len(bars))[::-1]
ax2.barh(y, [b[1] for b in bars], color=[b[2] for b in bars], height=.62)
for yi, (lab, v, _) in zip(y, bars): ax2.text(v + .6, yi, fmt(v) + ' %', va='center', fontsize=10.5)
ax2.set_yticks(y); ax2.set_yticklabels([b[0] for b in bars]); ax2.set_xlim(0, 40); ax2.set_xlabel('% de las viviendas u hogares de E1')
ax2.grid(axis='y', visible=False)
ax2.set_title('La ECV registra menos placas que el catastro', pad=22, fontweight='bold')
ax2.text(0, 1.02, 'Quien vive bajo otra vivienda tiene placa de concreto encima', transform=ax2.transAxes, fontsize=10, color=TXT2)
fig.text(0.012, 0.012, 'Fuentes: catastro de Barranquilla (2026); DANE, ECV 2019 y 2024 (hogares de estrato 1).', fontsize=8.5, color=TXT2)
fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(OUT_F + 'catastro_e1_edificios.png', dpi=160); plt.close(fig)
print('ok')
