import pandas as pd, numpy as np, csv, json
O = '/mnt/user-data/outputs/'
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 40)
n = lambda s: pd.to_numeric(s.astype(str).str.strip().str.replace(',', '.'), errors='coerce')
T = {}

def wmean(d, c):
    x = d[c] if pd.api.types.is_numeric_dtype(d[c]) else n(d[c])
    m = x.notna()
    return (x[m] * d.W[m]).sum() / d.W[m].sum() if d.W[m].sum() > 0 else np.nan

def wpct(d, mask):
    return d.W[mask].sum() / d.W.sum() * 100

def wq(x, w, q):
    i = np.argsort(x); x, w = np.asarray(x)[i], np.asarray(w)[i]
    c = np.cumsum(w) / w.sum()
    return x[np.searchsorted(c, q)]

# ---------------- ECV 2019 ----------------
a = pd.read_csv(O + 'ECV2019_Barranquilla_consolidado.csv', sep=';', dtype=str, encoding='utf-8-sig')
a['W'] = n(a.FEX_C); a['E'] = n(a.ESTRATO)
en = {}
with open('/home/claude/work/ecv2019_extract/energeticos_ecv2019.csv', encoding='utf-8-sig') as f:
    for r in csv.DictReader(f, delimiter=';'):
        en[(r['DIRECTORIO'], r['SECUENCIA_ENCUESTA'], r['SECUENCIA_P'])] = r
a['MESES'] = [en.get((r.DIRECTORIO, r.SECUENCIA_ENCUESTA, r.SECUENCIA_P), {}).get('P5018S1', '') for r in a.itertuples()]
a['PAGO_MES'] = n(a.PAGO_ELEC_P5018) / n(a.MESES).replace(0, np.nan)
for c in ['TIENE_AC', 'TIENE_VENTILADOR', 'TIENE_NEVERA', 'HORAS_AC_P5524', 'HORAS_VENTILADOR_P5526', 'NEVERA_TAMANO_P5514', 'NEVERA_ANTIGUEDAD_ANOS_P5515', 'INGRESO_PERCAPITA', 'INGRESO_HOGAR', 'PERSONAS_HOGAR', 'CUARTOS_P5000', 'CUARTOS_DORMIR_P5010', 'NUM_SANITARIOS_P5024']:
    a[c] = n(a[c])
a.loc[a.NEVERA_ANTIGUEDAD_ANOS_P5515 >= 90, 'NEVERA_ANTIGUEDAD_ANOS_P5515'] = np.nan
a['LAV'] = a.LAVADORA_CARGA_P5509.notna() & (a.LAVADORA_CARGA_P5509.astype(str).str.strip() != '')
a['TVLCD'] = n(a.TV_LCD_H_LV_P5522S1).notna()
a['TVCONV'] = n(a.TV_CONV_H_LV_P5521S1).notna()
a['PC'] = n(a.PC_ESCRITORIO_H_P5527).notna()
a['PORT'] = n(a.PORTATILES_P5529).fillna(0) > 0
a['CAL'] = n(a.CALENTADOR_AGUA_P5518).notna()
a['HAC'] = a.CUARTOS_DORMIR_P5010.where(a.CUARTOS_DORMIR_P5010 > 0)
a['PERS_DORM'] = a.PERSONAS_HOGAR / a.HAC
b16 = lambda c: n(a[c]).fillna(0)
a['B_INC'], a['B_FLU'], a['B_LED'] = b16('BOMBILLAS_INCAND_P5533S1'), b16('BOMBILLAS_FLUOR_P5533S2'), b16('BOMBILLAS_LED_P5533S3')
a['B_TOT'] = a.B_INC + a.B_FLU + a.B_LED
s = a[a.E.between(1, 6)]
# income quintiles (weighted) on per-capita income
q = [wq(s.INGRESO_PERCAPITA.fillna(0), s.W, p) for p in (0.2, 0.4, 0.6, 0.8)]
s = s.assign(QUINT=np.digitize(s.INGRESO_PERCAPITA.fillna(0), q) + 1)

rows = []
for e, d in s.groupby('E'):
    ac = d[d.TIENE_AC == 1]; nev = d[d.TIENE_NEVERA == 1]
    rows.append(dict(estrato=int(e), n=len(d),
        nevera=round(wpct(d, d.TIENE_NEVERA == 1), 1),
        nev_pequena=round(wpct(nev, nev.NEVERA_TAMANO_P5514 == 1), 1), nev_mediana=round(wpct(nev, nev.NEVERA_TAMANO_P5514 == 2), 1), nev_grande=round(wpct(nev, nev.NEVERA_TAMANO_P5514 == 3), 1),
        nev_edad_media=round(wmean(nev, 'NEVERA_ANTIGUEDAD_ANOS_P5515'), 1),
        nev_10mas=round(wpct(nev, nev.NEVERA_ANTIGUEDAD_ANOS_P5515 >= 10), 1),
        lavadora=round(wpct(d, d.LAV), 1), tv_lcd=round(wpct(d, d.TVLCD), 1), tv_conv=round(wpct(d, d.TVCONV), 1), pc=round(wpct(d, d.PC), 1), portatil=round(wpct(d, d.PORT), 1), calentador=round(wpct(d, d.CAL), 1),
        led_share=round((d.B_LED * d.W).sum() / (d.B_TOT * d.W).sum() * 100, 1), bombillas=round(wmean(d, 'B_TOT'), 1)))
T['ecv19_equipos_estrato'] = pd.DataFrame(rows)

nev = s[s.TIENE_NEVERA == 1]
T['ecv19_nevera_edad_dist'] = pd.DataFrame([dict(rango=k, pct=round(wpct(nev, m), 1)) for k, m in [('0-2 años', nev.NEVERA_ANTIGUEDAD_ANOS_P5515 <= 2), ('3-5', nev.NEVERA_ANTIGUEDAD_ANOS_P5515.between(3, 5)), ('6-9', nev.NEVERA_ANTIGUEDAD_ANOS_P5515.between(6, 9)), ('10-14', nev.NEVERA_ANTIGUEDAD_ANOS_P5515.between(10, 14)), ('15+', nev.NEVERA_ANTIGUEDAD_ANOS_P5515 >= 15), ('no sabe', nev.NEVERA_ANTIGUEDAD_ANOS_P5515.isna())]])
T['ecv19_nevera_global'] = dict(nevera=wpct(s, s.TIENE_NEVERA == 1), edad_media=wmean(nev, 'NEVERA_ANTIGUEDAD_ANOS_P5515'), edad_mediana=float(wq(nev.NEVERA_ANTIGUEDAD_ANOS_P5515.dropna(), nev.W[nev.NEVERA_ANTIGUEDAD_ANOS_P5515.notna()], .5)), peq=wpct(nev, nev.NEVERA_TAMANO_P5514 == 1), med=wpct(nev, nev.NEVERA_TAMANO_P5514 == 2), gra=wpct(nev, nev.NEVERA_TAMANO_P5514 == 3))
# lavadora loads, TV hours, plancha
T['ecv19_uso_otros'] = dict(
    lav_cargas_sem_mediana=float(wq(n(s.LAVADORA_CARGAS_SEM_P5510).dropna(), s.W[n(s.LAVADORA_CARGAS_SEM_P5510).notna()], .5)),
    tv_lcd_h_lv=wmean(s[s.TVLCD], 'TV_LCD_H_LV_P5522S1'), tv_lcd_h_fs=wmean(s[s.TVLCD], 'TV_LCD_H_FS_P5522S2'),
    tv_conv_h_lv=wmean(s[s.TVCONV], 'TV_CONV_H_LV_P5521S1'),
    planchadas_mes=wmean(s[n(s.PLANCHADAS_MES_P5531).notna()], 'PLANCHADAS_MES_P5531'),
    led_share=(s.B_LED * s.W).sum() / (s.B_TOT * s.W).sum() * 100, inc_share=(s.B_INC * s.W).sum() / (s.B_TOT * s.W).sum() * 100, flu_share=(s.B_FLU * s.W).sum() / (s.B_TOT * s.W).sum() * 100, bombillas=wmean(s, 'B_TOT'))

# AC deep
acrows = []
for e, d in s.groupby('E'):
    ac = d[(d.TIENE_AC == 1) & d.HORAS_AC_P5524.notna()]
    h = ac.HORAS_AC_P5524
    fan = d[d.HORAS_VENTILADOR_P5526 > 0]
    acrows.append(dict(estrato=int(e), n_ac=len(ac), h_media=round(wmean(ac, 'HORAS_AC_P5524'), 1), h_p25=float(wq(h, ac.W, .25)) if len(ac) else None, h_mediana=float(wq(h, ac.W, .5)) if len(ac) else None, h_p75=float(wq(h, ac.W, .75)) if len(ac) else None, pct_mas12h=round(wpct(ac, h > 12), 1) if len(ac) else None,
        fan_h_mediana=float(wq(fan.HORAS_VENTILADOR_P5526, fan.W, .5)), fan_h_media=round(wmean(fan, 'HORAS_VENTILADOR_P5526'), 1)))
T['ecv19_horas_estrato'] = pd.DataFrame(acrows)
T['ecv19_ac_quintil'] = pd.DataFrame([dict(quintil=int(k), n=len(d), ac=round(wpct(d, d.TIENE_AC == 1), 1), ingreso_pc_mediana=round(float(wq(d.INGRESO_PERCAPITA.fillna(0), d.W, .5)))) for k, d in s.groupby('QUINT')])
ten = {'1': 'Propia pagada', '2': 'Propia pagando', '3': 'Arriendo', '4': 'Usufructo', '5': 'Posesión sin título', '6': 'Colectiva'}
s['G'] = s.E.map({1: '1-2', 2: '1-2', 3: '3-4', 4: '3-4', 5: '5-6', 6: '5-6'})
s['TEN'] = s.TENENCIA_P5095.str.strip().map(lambda x: 'Propia' if x in ('1', '2') else ('Arriendo' if x == '3' else 'Otra'))
T['ecv19_ac_tenencia'] = s.groupby(['G', 'TEN']).apply(lambda d: pd.Series(dict(n=len(d), ac=round(wpct(d, d.TIENE_AC == 1), 1)))).reset_index()
s['PERS_G'] = pd.cut(s.PERSONAS_HOGAR, [0, 1, 2, 3, 4, 99], labels=['1', '2', '3', '4', '5+'])
T['ecv19_ac_personas'] = s.groupby('PERS_G', observed=True).apply(lambda d: pd.Series(dict(n=len(d), ac=round(wpct(d, d.TIENE_AC == 1), 1)))).reset_index()
# electricity bill: AC vs no AC by estrato group
pay = s[s.PAGO_MES.between(1000, 3e6)]
T['ecv19_pago_ac'] = pay.groupby(['G', 'TIENE_AC']).apply(lambda d: pd.Series(dict(n=len(d), pago_mediana=round(float(wq(d.PAGO_MES, d.W, .5)), -3), pago_media=round(wmean(d, 'PAGO_MES'), -3)))).reset_index()
T['ecv19_pago_estrato'] = pay.groupby('E').apply(lambda d: pd.Series(dict(n=len(d), pago_mediana=round(float(wq(d.PAGO_MES, d.W, .5)), -3)))).reset_index()
# housing materials
mt = {'TECHO_P4567': {'1': 'Plancha de concreto', '2': 'Teja de barro', '3': 'Asbesto-cemento', '4': 'Zinc / metálica', '5': 'Teja plástica'}, 'PISOS_P4015': {'3': 'Mármol', '4': 'Baldosa/cerámica', '6': 'Cemento', '7': 'Tierra', '2': 'Madera pulida'}}
for c, lab in mt.items():
    T['ecv19_' + c] = s.groupby('G').apply(lambda d: pd.Series({v: round(wpct(d, d[c].str.strip() == k), 1) for k, v in lab.items()})).reset_index()
T['ecv19_techo_ac'] = s.groupby(s.TECHO_P4567.str.strip().map(mt['TECHO_P4567'])).apply(lambda d: pd.Series(dict(n=len(d), pct_hog=round(wpct(s, s.TECHO_P4567.str.strip().map(mt['TECHO_P4567']) == d.name), 1), ac=round(wpct(d, d.TIENE_AC == 1), 1)))).reset_index()
# household structure
hrows = []
for e, d in s.groupby('E'):
    hrows.append(dict(estrato=int(e), personas=round(wmean(d, 'PERSONAS_HOGAR'), 2), unipersonal=round(wpct(d, d.PERSONAS_HOGAR == 1), 1), cinco_mas=round(wpct(d, d.PERSONAS_HOGAR >= 5), 1), menores5=round(wmean(d, 'N_MENORES_5'), 2), n5_14=round(wmean(d, 'N_5_14'), 2), mayores65=round(wmean(d, 'N_65_MAS'), 2), con_65=round(wpct(d, n(d.N_65_MAS) > 0), 1), ocupados=round(wmean(d, 'N_OCUPADOS_P6240_1'), 2), sin_ocupado=round(wpct(d, n(d.N_OCUPADOS_P6240_1) == 0), 1), oficios=round(wmean(d, 'N_OFICIOS_HOGAR_P6240_4'), 2), jefa_mujer=round(wpct(d, d.SEXO_JEFE_P6020.str.strip() == '2'), 1), edad_jefe=round(wmean(d, 'EDAD_JEFE'), 1), cuartos=round(wmean(d, 'CUARTOS_P5000'), 2), dormitorios=round(wmean(d, 'CUARTOS_DORMIR_P5010'), 2), pers_dorm=round(wmean(d, 'PERS_DORM'), 2), hacinamiento=round(wpct(d, d.PERS_DORM > 3), 1), sanitarios=round(wmean(d, 'NUM_SANITARIOS_P5024'), 2), ingreso_pc_med=round(float(wq(d.INGRESO_PERCAPITA.fillna(0), d.W, .5)), -3)))
T['ecv19_hogar_estrato'] = pd.DataFrame(hrows)

# ---------------- ECV 2024 ----------------
b = pd.read_csv(O + 'ECV2024_Barranquilla_hogares.csv', sep=';', dtype=str, encoding='utf-8-sig')
b['W'] = n(b.FEX_C); b['E'] = n(b.ESTRATO)
b = b[b.E.between(1, 6)]
for c in ['TIENE_AC', 'TIENE_VENT', 'TIENE_NEVERA', 'TIENE_LAVADORA', 'TIENE_TV_LED', 'TIENE_CALENTADOR', 'CANT_PERSONAS_HOGAR', 'PERCAPITA', 'CUARTOS', 'DORMITORIOS', 'SANITARIOS', 'N_65', 'N_MEN5']:
    b[c] = n(b[c])
yes = lambda c: b[c].str.strip() == '1'
b['TV_CONV'], b['PC'], b['PORT'] = yes('P1077S7'), yes('P1077S21'), yes('P1077S22')
b['PAGO_MES'] = n(b.PAGO_ELEC) / n(b.MESES_PAGO).replace(0, np.nan)
b['G'] = b.E.map({1: '1-2', 2: '1-2', 3: '3-4', 4: '3-4', 5: '5-6', 6: '5-6'})
rows = []
for e, d in b.groupby('E'):
    rows.append(dict(estrato=int(e), n=len(d), ac=round(wpct(d, d.TIENE_AC == 1), 1), ventilador=round(wpct(d, d.TIENE_VENT == 1), 1), nevera=round(wpct(d, d.TIENE_NEVERA == 1), 1), lavadora=round(wpct(d, d.TIENE_LAVADORA == 1), 1), tv_led=round(wpct(d, d.TIENE_TV_LED == 1), 1), tv_conv=round(wpct(d, d.TV_CONV), 1), pc=round(wpct(d, d.PC), 1), portatil=round(wpct(d, d.PORT), 1), calentador=round(wpct(d, d.TIENE_CALENTADOR == 1), 1), pago_mediana=round(float(wq(d.PAGO_MES.dropna(), d.W[d.PAGO_MES.notna()], .5)), -3), personas=round(wmean(d, 'CANT_PERSONAS_HOGAR'), 2), cuartos=round(wmean(d, 'CUARTOS'), 2), sanitarios=round(wmean(d, 'SANITARIOS'), 2)))
T['ecv24_estrato'] = pd.DataFrame(rows)
pay = b[b.PAGO_MES.between(1000, 5e6)]
T['ecv24_pago_ac'] = pay.groupby(['G', 'TIENE_AC']).apply(lambda d: pd.Series(dict(n=len(d), pago_mediana=round(float(wq(d.PAGO_MES, d.W, .5)), -3)))).reset_index()
b['TEN'] = b.TENENCIA.str.strip().map(lambda x: 'Propia' if x in ('1', '2') else ('Arriendo' if x == '3' else 'Otra'))
T['ecv24_ac_tenencia'] = b.groupby(['G', 'TEN']).apply(lambda d: pd.Series(dict(n=len(d), ac=round(wpct(d, d.TIENE_AC == 1), 1)))).reset_index()
q24 = [wq(b.PERCAPITA.fillna(0), b.W, p) for p in (0.2, 0.4, 0.6, 0.8)]
b['QUINT'] = np.digitize(b.PERCAPITA.fillna(0), q24) + 1
T['ecv24_ac_quintil'] = pd.DataFrame([dict(quintil=int(k), n=len(d), ac=round(wpct(d, d.TIENE_AC == 1), 1), ingreso_pc_mediana=round(float(wq(d.PERCAPITA.fillna(0), d.W, .5)), -3)) for k, d in b.groupby('QUINT')])
T['ecv24_techo'] = b.groupby('G').apply(lambda d: pd.Series({v: round(wpct(d, d.P4567.str.strip() == k), 1) for k, v in mt['TECHO_P4567'].items()})).reset_index()

# ---------------- ENUT (Atlántico cabecera) ----------------
p = pd.read_pickle('/home/claude/work/enut_atl.pkl')
cab = p[p.CLASE.str.strip() == '1']
hh = cab.drop_duplicates(['DIRECTORIO', 'SECUENCIA_P']).copy()
hh['E'] = hh.ESTRATO
T['enut_bienes_estrato'] = pd.DataFrame([dict(estrato=int(e), n=len(d), nevera=round(wpct(d, d.P1176S3.str.strip() == '1'), 1), lavadora=round(wpct(d, d.P1176S1.str.strip() == '1'), 1), secadora=round(wpct(d, d.P1176S2.str.strip() == '1'), 1)) for e, d in hh[hh.E.between(1, 6)].groupby('E')])
a10 = cab[cab.EDAD >= 10].copy()
a10['MIN_FUERA'] = np.where(a10.TRABAJA_EN_CASA, 0, a10.MIN_TRABAJO) + a10.MIN_VIAJE_TRAB + a10.MIN_VIAJE_EST
cols = ['MIN_DORMIR', 'MIN_TV', 'MIN_INTERNET', 'MIN_COCINAR', 'MIN_TRABAJO', 'MIN_FUERA']
T['enut_grupo_estrato'] = a10.groupby('GRUPO_ESTRATO').apply(lambda d: pd.Series({**{c[4:].lower(): round(wmean(d, c) / 60, 2) for c in cols}, 'n': len(d), 'ocupados_pct': round(wpct(d, d.TIPO == 'Ocupado'), 1), 'oficios_pct': round(wpct(d, d.TIPO == 'Oficios del hogar'), 1), 'mayores_pct': round(wpct(d, d.TIPO == 'Mayor 65+ no ocupado'), 1)})).reset_index()
dn = {0: 'lun', 1: 'mar', 2: 'mié', 3: 'jue', 4: 'vie', 5: 'sáb', 6: 'dom'}
T['enut_dia_semana'] = a10.groupby('DOW').apply(lambda d: pd.Series({'n': len(d), 'dormir': round(wmean(d, 'MIN_DORMIR') / 60, 2), 'trabajo': round(wmean(d, 'MIN_TRABAJO') / 60, 2), 'fuera': round(wmean(d, 'MIN_FUERA') / 60, 2), 'tv': round(wmean(d, 'MIN_TV') / 60, 2)})).reset_index().assign(DOW=lambda x: x.DOW.map(dn))
# share of 10+ who were away > 4 h (proxy of empty-house time) by weekday/weekend
T['enut_fuera_dist'] = a10.groupby('FINDE').apply(lambda d: pd.Series({'0h': round(wpct(d, d.MIN_FUERA == 0), 1), '0-4h': round(wpct(d, d.MIN_FUERA.between(1, 240)), 1), '4-8h': round(wpct(d, d.MIN_FUERA.between(241, 480)), 1), '8-10h': round(wpct(d, d.MIN_FUERA.between(481, 600)), 1), '>10h': round(wpct(d, d.MIN_FUERA > 600), 1)})).reset_index()
# household-level: does anyone stay home all day? (all 10+ with MIN_FUERA==0) - only for households fully covered
g = a10.groupby(['DIRECTORIO', 'SECUENCIA_P', 'FINDE', 'GRUPO_ESTRATO']).agg(W=('W', 'first'), all_out=('MIN_FUERA', lambda x: (x > 0).all()), min_out=('MIN_FUERA', 'min')).reset_index()
T['enut_hogar_alguien_casa'] = g.groupby(['GRUPO_ESTRATO', 'FINDE']).apply(lambda d: pd.Series({'n': len(d), 'alguien_en_casa_todo_dia_pct': round(wpct(d, ~d.all_out), 1)})).reset_index()
T['enut_mes'] = a10.groupby('MES').apply(lambda d: pd.Series({'n': len(d), 'dormir': round(wmean(d, 'MIN_DORMIR') / 60, 2), 'fuera': round(wmean(d, 'MIN_FUERA') / 60, 2), 'tv': round(wmean(d, 'MIN_TV') / 60, 2)})).reset_index()

# ---------------- SUI ----------------
sui = pd.read_csv(O + 'SUI_Barranquilla_urbano_residencial_2019_2026.csv', sep=';', encoding='utf-8-sig', dtype={'estrato': str})
ok = sui[sui.bandera.isna() | (sui.bandera == '')].copy()
ok = ok[~ok.bandera.fillna('').str.contains('consumo')]
idx = []
for (y, e), d in ok[ok.anio.between(2019, 2025)].groupby(['anio', 'estrato']):
    if len(d) < 10: continue
    mu = d.kWh_suscriptor.mean()
    for r in d.itertuples(): idx.append((e, r.mes, r.kWh_suscriptor / mu, y))
ix = pd.DataFrame(idx, columns=['estrato', 'mes', 'ind', 'anio'])
T['sui_indice_mensual'] = ix.groupby(['estrato', 'mes']).ind.mean().unstack(0).round(3)
# climate-sensitive fraction proxy: 1 - mean(feb,mar)/annual mean, per estrato, averaged by year
fr = []
for (y, e), d in ok[ok.anio.between(2019, 2025)].groupby(['anio', 'estrato']):
    if len(d) < 10: continue
    base = d[d.mes.isin([2, 3])].kWh_suscriptor.mean(); mu = d.kWh_suscriptor.mean()
    fr.append((e, y, 1 - base / mu, mu - base))
fr = pd.DataFrame(fr, columns=['estrato', 'anio', 'frac', 'kwh'])
T['sui_fraccion_sensible'] = fr.groupby('estrato').agg(frac_media=('frac', 'mean'), frac_min=('frac', 'min'), frac_max=('frac', 'max'), kwh_mes_sobre_base=('kwh', 'mean')).round(3).reset_index()
T['sui_suscriptores_anual'] = sui[sui.mes == 12].pivot_table(index='anio', columns='estrato', values='suscriptores')
T['sui_kwh_total_anual_GWh'] = (ok.groupby(['anio']).apply(lambda d: d[d.estrato == 'total'].consumo_kWh.mean() * 12 / 1e6)).round(1)

for k, v in T.items():
    print('\n###', k)
    print(v if not isinstance(v, dict) else json.dumps({a: (round(b, 2) if isinstance(b, float) else b) for a, b in v.items()}))
pd.to_pickle(T, '/home/claude/work/deep_tables.pkl')
