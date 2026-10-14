import pandas as pd, numpy as np
p=pd.read_pickle('/home/claude/work/enut_atl.pkl')
a=p[(p.CLASE.str.strip()=='1')&(p.EDAD>=10)].copy()
a['MIN_FUERA_TRABAJO']=np.where(a.TRABAJA_EN_CASA,0,a.MIN_TRABAJO)+a.MIN_VIAJE_TRAB
o=a[(a.TIPO=='Ocupado')]
for f,d in o.groupby('FINDE'):
    print('ocupados finde',f,'h fuera por trabajo',round((d.MIN_FUERA_TRABAJO*d.W).sum()/d.W.sum()/60,2))
# person-level CSV
keep=['DIRECTORIO','SECUENCIA_P','ORDEN','ESTRATO','GRUPO_ESTRATO','P424','FECHA','DOW','FINDE','MES','EDAD','P6020','P425','TIPO','P1152','P6880','TRABAJA_EN_CASA','P1101','P1176S1','P1176S3','P6008']+[c for c in a.columns if c.startswith('MIN_')]+['W']
out=a[keep].rename(columns={'P424':'TIPO_VIVIENDA','P6020':'SEXO','P425':'PARENTESCO','P1152':'ACTIVIDAD_SEMANA','P6880':'LUGAR_TRABAJO','P1101':'JORNADA_ESTUDIO','P1176S1':'LAVADORA','P1176S3':'NEVERA','P6008':'PERSONAS_HOGAR','W':'FEX_C'})
out['DOW']=out.DOW.map({0:'lun',1:'mar',2:'mie',3:'jue',4:'vie',5:'sab',6:'dom'})
out.to_csv('/mnt/user-data/outputs/ENUT2024_25_Atlantico_cabecera_personas.csv',sep=';',index=False,encoding='utf-8-sig',decimal=',')
# summary hours table by TIPO x dia
cols=['MIN_DORMIR','MIN_COMER','MIN_ASEO','MIN_DESCANSAR','MIN_COCINAR','MIN_LAVAR_LOZA','MIN_ROPA','MIN_LIMPIAR','MIN_TV','MIN_INTERNET','MIN_MUSICA_RADIO','MIN_TRABAJO','MIN_VIAJE_TRAB','MIN_VIAJE_EST','MIN_FUERA_TRABAJO']
rows=[]
for (t,f),d in list(a.groupby(['TIPO','FINDE']))+[(('Todos',ff),dd) for ff,dd in a.groupby('FINDE')]:
    r={'tipo':t,'dia':'fin de semana' if f else 'entre semana','n':len(d),'poblacion':round(d.W.sum())}
    for c in cols: r['h_'+c[4:].lower()]=round((d[c]*d.W).sum()/d.W.sum()/60,2)
    rows.append(r)
s=pd.DataFrame(rows)
s.to_csv('/mnt/user-data/outputs/ENUT2024_25_Atlantico_horas_por_tipo.csv',sep=';',index=False,encoding='utf-8-sig',decimal=',')
print(s[['tipo','dia','n','h_dormir','h_tv','h_trabajo','h_fuera_trabajo']].to_string())
print(len(out))
