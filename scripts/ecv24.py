import pandas as pd, numpy as np
D='/home/claude/work/ecv24/c/'
rd=lambda f: pd.read_csv(D+f,sep=';',dtype=str,encoding='latin-1',low_memory=False)
K=['DIRECTORIO','SECUENCIA_ENCUESTA']  # hogar = DIRECTORIO + SECUENCIA_ENCUESTA (SECUENCIA_P siempre 1 en archivos de hogar)
num=lambda s: pd.to_numeric(s.astype(str).str.strip().str.replace(',','.'),errors='coerce')
v=rd('viv.csv'); v.columns=[c.strip('﻿').replace('ï»¿','') for c in v.columns]
bq=v[(v.P1_DEPARTAMENTO.str.strip()=='08')&(v.P1_MUNICIPIO.str.strip()=='001')]
print('viviendas BQ',len(bq),'clase',bq.CLASE.value_counts().to_dict())
b=rd('bienes.csv'); s=rd('serv.csv'); t=rd('ten.csv'); pe=rd('pers.csv')
for df in (b,s,t,pe): df.columns=[c.replace('ï»¿','').strip('﻿') for c in df.columns]
h=b[b.DIRECTORIO.isin(bq.DIRECTORIO)][K+['FEX_C','P1077S1','P1077S2','P1077S6','P1077S7','P1077S8','P1077S11','P1077S12','P1077S21','P1077S22']]
h=h.merge(bq[['DIRECTORIO','CLASE','P1070','P4005','P4015','P4567','P8520S1A1']],on='DIRECTORIO')
h=h.merge(s[K+['P5000','P5010','P5018','P5018S1','P5024','CANT_PERSONAS_HOGAR','I_HOGAR','PERCAPITA']],on=K,how='left')
h=h.merge(t[K+['P5095']],on=K,how='left')
pe['EDAD']=num(pe.P6040)
# en el archivo de personas SECUENCIA_P es el número de hogar y SECUENCIA_ENCUESTA el de persona
pe=pe.drop(columns=['SECUENCIA_ENCUESTA']).rename(columns={'SECUENCIA_P':'SECUENCIA_ENCUESTA'})
ag=pe.groupby(K).agg(N_PERS=('ORDEN','size'),N_MEN5=('EDAD',lambda x:(x<5).sum()),N_65=('EDAD',lambda x:(x>=65).sum())).reset_index()
h=h.merge(ag,on=K,how='left')
h['W']=num(h.FEX_C); h['ESTRATO']=num(h.P8520S1A1)
yes=lambda c:(h[c].str.strip()=='1')
for c,n in [('P1077S11','AC'),('P1077S12','VENT'),('P1077S2','NEVERA'),('P1077S1','LAVADORA'),('P1077S8','TV_LED'),('P1077S6','CALENTADOR')]: h['TIENE_'+n]=yes(c).astype(int)
W=h.W.sum(); print('hogares',len(h),'expandidos',round(W))
def pct(d,c): return round((d[c]*d.W).sum()/d.W.sum()*100,1)
print('global',{c:pct(h,c) for c in ['TIENE_AC','TIENE_VENT','TIENE_NEVERA','TIENE_LAVADORA','TIENE_TV_LED','TIENE_CALENTADOR']})
print('estrato dist',{int(e):(len(d),round(d.W.sum()/W*100,1)) for e,d in h.groupby('ESTRATO')})
for e in range(1,7):
    d=h[h.ESTRATO==e]; p=pct(d,'TIENE_AC'); se=1.96*np.sqrt(p/100*(1-p/100)/len(d))*100
    print(e,len(d),'AC',p,'±',round(se,1),'VENT',pct(d,'TIENE_VENT'),'NEV',pct(d,'TIENE_NEVERA'),'LAV',pct(d,'TIENE_LAVADORA'),'pers',round((num(d.CANT_PERSONAS_HOGAR)*d.W).sum()/d.W.sum(),2),'cuartos',round((num(d.P5000)*d.W).sum()/d.W.sum(),2),'sanit',round((num(d.P5024)*d.W).sum()/d.W.sum(),2))
print('pers/hogar',round((num(h.CANT_PERSONAS_HOGAR)*h.W).sum()/W,2),'tipo viv',{k:round(v/W*100,1) for k,v in h.groupby('P1070').W.sum().items()},'tenencia',{k:round(v/W*100,1) for k,v in h.groupby('P5095').W.sum().items()})
h.drop(columns=['FEX_C']).rename(columns={'W':'FEX_C','P1070':'TIPO_VIVIENDA','P5000':'CUARTOS','P5010':'DORMITORIOS','P5024':'SANITARIOS','P5095':'TENENCIA','P5018':'PAGO_ELEC','P5018S1':'MESES_PAGO'}).to_csv('/mnt/user-data/outputs/ECV2024_Barranquilla_hogares.csv',sep=';',index=False,encoding='utf-8-sig')
