import pandas as pd, glob, numpy as np
D='/home/claude/work/geih24/'
num=lambda s: pd.to_numeric(s.astype(str).str.strip().str.replace(',','.'),errors='coerce')
def load(pat,cols):
    out=[]
    for d in sorted(glob.glob(D+'*/')):
        f=[x for x in glob.glob(d+'*') if pat in x][0]
        x=pd.read_csv(f,sep=';',dtype=str,encoding='latin-1',low_memory=False)
        x.columns=[c.replace('ï»¿','').strip('﻿').upper() for c in x.columns]
        x=x[x.AREA.str.strip()=='08']
        out.append(x if cols is None else x[[c for c in cols if c in x.columns]])
    return pd.concat(out)
K=['MES','DIRECTORIO','SECUENCIA_P']
h=load("Datos del hogar",None)
p=load('Caracter',K+['ORDEN','P6040','P6050','P6020'])
o=load('Ocupados',K+['ORDEN','P6800','P6880','P6430'])
p['EDAD']=num(p.P6040)
o['H']=num(o.P6800); o['CASA']=(o.P6880.str.strip()=='1')
pa=p.groupby(K).agg(N_PERS=('ORDEN','size'),N_MENORES_5=('EDAD',lambda x:(x<5).sum()),N_5_17=('EDAD',lambda x:((x>=5)&(x<18)).sum()),N_18_64=('EDAD',lambda x:((x>=18)&(x<65)).sum()),N_65_MAS=('EDAD',lambda x:(x>=65).sum())).reset_index()
oa=o.groupby(K).agg(N_OCUPADOS=('ORDEN','size'),N_TRABAJA_EN_CASA=('CASA','sum'),HORAS_SEM_OCUPADOS=('H','sum')).reset_index()
h=h.merge(pa,on=K,how='left').merge(oa,on=K,how='left')
for c in ['N_OCUPADOS','N_TRABAJA_EN_CASA','HORAS_SEM_OCUPADOS']: h[c]=h[c].fillna(0)
nm=h.MES.nunique(); print('meses',sorted(h.MES.unique())); h['W']=num(h.FEX_C18)/nm
h['ESTRATO']=num(h.P4030S1A1)
h['N_SIN_OCUPACION_ADULTOS']=h.N_18_64+h.N_65_MAS-h.N_OCUPADOS
cols={'P4000':'TIPO_VIVIENDA','P4010':'PAREDES','P4020':'PISOS','P5000':'CUARTOS','P5010':'DORMITORIOS','P5020':'SANITARIO','P5030':'SANITARIO_EXCLUSIVO','P5080':'COMBUSTIBLE_COCINA','P5090':'TENENCIA','P5110':'VALOR_VIVIENDA','P5130':'ARRIENDO_ESTIMADO','P5140':'ARRIENDO_PAGADO','P70':'HOGARES_EN_VIVIENDA','P6008':'PERSONAS_HOGAR','P4030S2':'GAS_NATURAL'}
out=h[K+['ESTRATO']+list(cols)+['N_PERS','N_MENORES_5','N_5_17','N_18_64','N_65_MAS','N_OCUPADOS','N_TRABAJA_EN_CASA','HORAS_SEM_OCUPADOS','W']].rename(columns=cols).rename(columns={'W':'FEX_ANUAL'})
out.to_csv('/mnt/user-data/outputs/GEIH2024_Barranquilla_AM_hogares.csv',sep=';',index=False,encoding='utf-8-sig',decimal=',')
W=h.W.sum(); print('hogares',len(h),'expandidos anual',round(W))
def wd(d,c): return {k:round(v/d.W.sum()*100,1) for k,v in d.groupby(d[c].str.strip()).W.sum().items()}
print('estrato %',{k:round(v/W*100,1) for k,v in h.groupby('ESTRATO').W.sum().items()})
print('tipo viv',wd(h,'P4000'),'paredes',wd(h,'P4010'),'pisos',wd(h,'P4020'),'tenencia',wd(h,'P5090'))
rows=[]
for e in range(1,7):
    d=h[h.ESTRATO==e]; w=d.W
    m=lambda s:(num(s)*w).sum()/w[num(s).notna()].sum()
    rows.append(dict(estrato=e,n=len(d),pct_hogares=round(w.sum()/W*100,1),apto=round(w[d.P4000.str.strip()=='2'].sum()/w.sum()*100,1),casa=round(w[d.P4000.str.strip()=='1'].sum()/w.sum()*100,1),cuartos=round(m(d.P5000),2),dormit=round(m(d.P5010),2),personas=round(m(d.P6008),2),menores5=round(m(d.N_MENORES_5),2),mayores65=round(m(d.N_65_MAS),2),ocupados=round(m(d.N_OCUPADOS),2),trab_casa_pct=round((d.N_TRABAJA_EN_CASA*w).sum()/(d.N_OCUPADOS*w).sum()*100,1),horas_ocup=round((d.HORAS_SEM_OCUPADOS*w).sum()/(d.N_OCUPADOS*w).sum(),1),hog_sin_ocup=round(w[d.N_OCUPADOS==0].sum()/w.sum()*100,1),propia=round(w[d.P5090.str.strip().isin(['1','2'])].sum()/w.sum()*100,1),arriendo=round(w[d.P5090.str.strip()=='3'].sum()/w.sum()*100,1),valor_mediana_mill=round(num(d.P5110).median()/1e6,0),piso_ceramica_marmol=round(w[d.P4020.str.strip().isin(['4','5','6','7'])].sum()/w.sum()*100,1)))
r=pd.DataFrame(rows); print(r.to_string())
r.to_csv('/mnt/user-data/outputs/GEIH2024_Barranquilla_AM_resumen_estrato.csv',sep=';',index=False,encoding='utf-8-sig',decimal=',')
