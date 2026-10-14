import pandas as pd, numpy as np, datetime
D = '/home/claude/work/enut2425/'
K = ['DIRECTORIO', 'SECUENCIA_P', 'ORDEN']

def rd(f, cols=None):
    df = pd.read_csv(D + f, sep=';', encoding='utf-8-sig', usecols=cols, dtype=str, low_memory=False)
    df.columns = [c.upper() for c in df.columns]
    return df

def num(s):
    return pd.to_numeric(s.astype(str).str.strip().str.replace(',', '.'), errors='coerce')

c1 = rd('ENUT_C1.csv')
c1 = c1[(num(c1.DPTO) == 8)]
c1['ESTRATO'] = num(c1.P4030S1A1)
c1['FECHA'] = num(c1.DIA_REF).apply(lambda d: datetime.date(1970, 1, 1) + datetime.timedelta(days=int(d)))
c1['DOW'] = c1.FECHA.apply(lambda d: d.weekday())  # 0=lunes
c1['FINDE'] = c1.DOW >= 5
c1['MES'] = c1.FECHA.apply(lambda d: d.month)
c1 = c1[['DIRECTORIO', 'CLASE', 'P424', 'ESTRATO', 'FECHA', 'DOW', 'FINDE', 'MES']]

c2 = rd('ENUT_C2.csv', ['DIRECTORIO', 'SECUENCIA_P', 'P5090', 'P1176S1', 'P1176S2', 'P1176S3', 'P6008'])
c3 = rd('ENUT_C3.csv', K + ['P6040', 'P6020', 'P425', 'FEX_C'])
p = c3.merge(c1, on='DIRECTORIO').merge(c2, on=['DIRECTORIO', 'SECUENCIA_P'], how='left')
p['W'] = num(p.FEX_C); p['EDAD'] = num(p.P6040)

c7 = rd('ENUT_C7.csv', K + ['P1152'])
c71 = rd('ENUT_C7_1.csv', K + ['P6880', 'P1151', 'P1150', 'P1150S1', 'P1150S2', 'P1099S1', 'P1099S2', 'P1098', 'P6535S1A1', 'P6535S1A2', 'P6534S1', 'P6534S2', 'P6530S1A1', 'P6530S1A2'])
c6 = rd('ENUT_C6.csv', K + ['P6170', 'P1101', 'P1160', 'P1159S1', 'P1159S2', 'P1158'])
p = p.merge(c7, on=K, how='left').merge(c71, on=K, how='left').merge(c6, on=K, how='left')

hm = lambda h, m: num(p[h]).fillna(0) * 60 + num(p[m]).fillna(0)
p['MIN_TRABAJO'] = hm('P1150S1', 'P1150S2') + hm('P6535S1A1', 'P6535S1A2') + hm('P6530S1A1', 'P6530S1A2')
p['MIN_VIAJE_TRAB'] = 2 * (hm('P1099S1', 'P1099S2') + hm('P6534S1', 'P6534S2'))
p['MIN_VIAJE_EST'] = 2 * hm('P1159S1', 'P1159S2')
p['TRABAJA_EN_CASA'] = num(p.P6880) == 2

# C8: time-use durations (persons 10+)
c8cols = K.copy()
acts = {
 'DORMIR': ['P1144S1'], 'COMER': ['P1144S2'], 'ASEO': ['P1144S3'], 'DESCANSAR': ['P1144S6'], 'GUARDAR_CAMA': ['P1144S5'],
 'COCINAR': ['P1143S1'], 'LAVAR_LOZA': ['P1143S2'], 'ROPA': ['P1142S1'], 'LIMPIAR': ['P1136S1'],
 'TV': ['P1110S1', 'P1110S2'], 'MUSICA_RADIO': ['P1110S3', 'P1110S4'], 'INTERNET': ['P1110S5', 'P1110S6'], 'TELEFONO': ['P1110S7'], 'LEER': ['P1110S8'],
 'SOCIAL': ['P1113S1', 'P1113S2'], 'DEPORTE': ['P1112S1'], 'CAMINAR': ['P1112S2'],
}
for a, vs in acts.items():
    for v in vs:
        c8cols += [v + 'A1', v + 'A2']
c8 = rd('ENUT_C8.csv', c8cols)
for a, vs in acts.items():
    c8['MIN_' + a] = sum(num(c8[v + 'A1']).fillna(0) * 60 + num(c8[v + 'A2']).fillna(0) for v in vs)
c8 = c8[K + ['MIN_' + a for a in acts]]
p = p.merge(c8, on=K, how='left')
p['EN_C8'] = p['MIN_DORMIR'].notna()

# person type
def tipo(r):
    e = r.EDAD
    if e < 10: return 'Niño <10'
    a = str(r.P1152).strip()
    if e >= 65 and a != '1': return 'Mayor 65+ no ocupado'
    if a == '1': return 'Ocupado'
    if a == '3': return 'Estudiante'
    if a == '4': return 'Oficios del hogar'
    if a == '2': return 'Busca trabajo'
    return 'Otro / incapacitado'
p['TIPO'] = p.apply(tipo, axis=1)
p['GRUPO_ESTRATO'] = p.ESTRATO.map({1: 'E1-2', 2: 'E1-2', 3: 'E3-4', 4: 'E3-4', 5: 'E5-6', 6: 'E5-6'})
p.to_pickle('/home/claude/work/enut_atl.pkl')
print(p.groupby('CLASE').size(), p.EN_C8.sum())
