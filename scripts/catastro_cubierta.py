"""Posición de cada vivienda frente a la cubierta (catastro limpio, 332.718 unidades).
Edificio = npn_edificio (primeros 22 dígitos del NPN, igual que en el entregable de ML).
Una unidad ocupa los pisos [planta_ubicacion, planta_ubicacion + total_plantas - 1].
Techo del edificio = máximo piso superior entre sus unidades residenciales.
"""
import pandas as pd, numpy as np, pickle
d = pd.read_pickle('/home/claude/work/catastro_limpio.pkl')
d['p_ini'] = d.planta_ubicacion
d['n_pl'] = d.total_plantas.fillna(1).clip(lower=1)
d['p_fin'] = d.p_ini + d.n_pl - 1
b = d.groupby('npn_edificio').agg(techo=('p_fin', 'max'), n_unid=('id_fila', 'size'))
d = d.join(b, on='npn_edificio')

def pos(r):
    if pd.isna(r.p_ini): return 'Sin dato de piso'
    arriba = r.p_fin >= r.techo
    if r.p_ini <= 1 and arriba: return 'Casa (suelo y cubierta propia)'
    if r.p_ini > 1 and arriba: return 'Último piso (bajo cubierta)'
    if r.p_ini <= 1: return 'Primer piso con vivienda encima'
    return 'Piso intermedio'
d['POSICION'] = d.apply(pos, axis=1)
d['TIPO_USO'] = np.where(d.uso.str.contains('Apartamentos'), 'Edificio 4+ pisos', 'Vivienda hasta 3 pisos')
d['EST'] = 'E' + d.estrato_num.astype(int).astype(str)
order = ['Casa (suelo y cubierta propia)', 'Último piso (bajo cubierta)', 'Piso intermedio', 'Primer piso con vivienda encima', 'Sin dato de piso']
T = {}
ct = pd.crosstab(d.EST, d.POSICION, margins=True, margins_name='Total')[order + ['Total']]
pc = (pd.crosstab(d.EST, d.POSICION, normalize='index', margins=True, margins_name='Total') * 100).round(1)[order]
T['cat_pos_n'] = ct; T['cat_pos_pct'] = pc
T['cat_pos_uso'] = (pd.crosstab([d.EST, d.TIPO_USO], d.POSICION, normalize='index') * 100).round(1)[order]
T['cat_pos_uso_n'] = pd.crosstab([d.EST, d.TIPO_USO], d.POSICION)[order]
# pisos del edificio para último piso / intermedio
T['cat_altura'] = d.groupby('EST').techo.describe(percentiles=[.5, .9]).round(1)
print(ct); print(pc); print(T['cat_pos_uso']); print(T['cat_altura'])
print('edificios', len(b), 'con >1 unidad', (b.n_unid > 1).sum())
pickle.dump(T, open('/home/claude/work/extra_catastro.pkl', 'wb'))
d[['numero_predial_nacional', 'npn_edificio', 'estrato_num', 'uso', 'condicion_predio', 'planta_ubicacion', 'total_plantas', 'techo', 'n_unid', 'POSICION']].to_csv(
    '/mnt/user-data/outputs/Catastro_posicion_cubierta.csv', sep=';', index=False, encoding='utf-8-sig')
