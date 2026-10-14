import pandas as pd, numpy as np
p=pd.read_pickle('/home/claude/work/enut_atl.pkl')
cab=p[p.CLASE.str.strip()=='1']
a=cab[cab.EDAD>=10].copy()
def wm(df,c): return (df[c]*df.W).sum()/df.W.sum()
print('personas cab',len(cab),'10+',len(a),'hogares',cab[['DIRECTORIO','SECUENCIA_P']].drop_duplicates().shape[0])
print('estrato viviendas', cab.drop_duplicates('DIRECTORIO').ESTRATO.value_counts().sort_index().to_dict())
print('dow persons 10+', a.DOW.value_counts().sort_index().to_dict())
cols=['MIN_DORMIR','MIN_COMER','MIN_ASEO','MIN_DESCANSAR','MIN_COCINAR','MIN_LAVAR_LOZA','MIN_ROPA','MIN_LIMPIAR','MIN_TV','MIN_INTERNET','MIN_MUSICA_RADIO','MIN_TRABAJO','MIN_VIAJE_TRAB','MIN_VIAJE_EST']
pd.set_option('display.width',250); pd.set_option('display.max_columns',30)
def tab(g):
    out=a.groupby(g).apply(lambda d: pd.Series({**{c[4:]:round(wm(d,c)/60,2) for c in cols},'n':len(d),'pob':round(d.W.sum())}))
    print(out)
tab('TIPO'); tab('FINDE'); tab('GRUPO_ESTRATO'); tab(['TIPO','FINDE'])
# share by TIPO weighted
print((a.groupby('TIPO').W.sum()/a.W.sum()*100).round(1))
# ocupados: work location, worked on ref day
o=a[a.TIPO=='Ocupado']
print('ocupados trabaja en su vivienda %',round(o[o.TRABAJA_EN_CASA].W.sum()/o.W.sum()*100,1), 'P6880 dist', (o.groupby(o.P6880.str.strip()).W.sum()/o.W.sum()*100).round(1).to_dict())
print('ocupados trabajo dia ref % (entre semana / finde)', o.groupby('FINDE').apply(lambda d: round(d[d.P1150.str.strip()=='1'].W.sum()/d.W.sum()*100,1)).to_dict())
print('horas semanales normales', round(wm(o.assign(h=pd.to_numeric(o.P1151,errors='coerce')).dropna(subset=['h']),'h'),1))
# students jornada
s=a[a.P6170.str.strip()=='1'] if 'P6170' in a else None
allst=cab[cab.P6170.fillna('').str.strip()=='1']
print('estudiantes (todas edades) jornada %',(allst.groupby(allst.P1101.str.strip()).W.sum()/allst.W.sum()*100).round(1).to_dict(), len(allst))
# households appliances
h=cab.drop_duplicates(['DIRECTORIO','SECUENCIA_P'])
for v,n in [('P1176S1','lavadora'),('P1176S2','secadora'),('P1176S3','nevera')]:
    print(n, round(h[h[v].str.strip()=='1'].W.sum()/h.W.sum()*100,1))
print('personas/hogar', round(wm(h.assign(x=pd.to_numeric(h.P6008,errors='coerce')),'x'),2))
