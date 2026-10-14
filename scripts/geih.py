import pandas as pd, glob, os
D='/home/claude/work/geih24/'
hs=[]
for d in sorted(glob.glob(D+'*/')):
    f=glob.glob(d+'Datos del hogar*')[0]
    x=pd.read_csv(f,sep=';',dtype=str,encoding='latin-1',low_memory=False)
    x.columns=[c.replace('ï»¿','').strip('﻿') for c in x.columns]
    hs.append(x)
h=pd.concat(hs)
print(h.shape, sorted(h.MES.unique()))
print('AREA values sample', h.AREA.value_counts().head(30).to_dict())
b=h[h.AREA.str.strip()=='08']
print('AREA 08 hogares',len(b),'por mes',b.groupby('MES').size().to_dict(),'clase',b.CLASE.value_counts().to_dict(),'dpto',b.DPTO.value_counts().to_dict())
print('estrato', b.P4030S1A1.value_counts().sort_index().to_dict())
print('dup directorio+secuencia across months', b.duplicated(['DIRECTORIO','SECUENCIA_P']).sum())
b.to_pickle('/home/claude/work/geih_bq_hog.pkl')
