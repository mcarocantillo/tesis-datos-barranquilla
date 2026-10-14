"""Efecto de diseño de la ECV 2024 en Barranquilla: varianza por conglomerados (SEGMENTO = unidad primaria
de muestreo, linealización de Taylor para una razón, con reemplazo) frente a la de muestreo aleatorio simple."""
import pandas as pd, numpy as np
d=pd.read_csv('/home/claude/work/ecv24/c/dis.csv',sep=';',dtype=str,encoding='latin-1')[['DIRECTORIO','SEGMENTO']].drop_duplicates()
h=pd.read_csv('/mnt/user-data/outputs/ECV2024_Barranquilla_hogares.csv',sep=';',dtype={'DIRECTORIO':str})
h=h.merge(d,on='DIRECTORIO',how='left'); assert h.SEGMENTO.notna().all()
h['w']=pd.to_numeric(h.FEX_C.astype(str).str.replace(',','.'))
sui=pd.read_csv('/mnt/user-data/outputs/SUI_Barranquilla_urbano_residencial_2015_2026.csv',sep=';',dtype={'estrato':str})
W=sui[(sui.anio==2024)&(sui.mes==12)&sui.estrato.isin(list('123456'))].set_index('estrato').suscriptores; W=W/W.sum()
C=h.SEGMENTO.nunique()
def lin(y,dom):
    """varianza por conglomerados de la razón sum(w*y*dom)/sum(w*dom), sobre toda la muestra (dominio)."""
    wd=h.w*dom; p=(wd*y).sum()/wd.sum(); z=wd*(y-p)/wd.sum()
    tc=z.groupby(h.SEGMENTO).sum(); v=C/(C-1)*((tc-tc.mean())**2).sum()
    return p,v
rows=[]; zc=0
for v_name,col in [('AC','TIENE_AC'),('Ventilador','TIENE_VENT'),('Nevera','TIENE_NEVERA')]:
    y=h[col].astype(float); Z=pd.Series(0.0,index=h.index)
    for e in '123456':
        dom=(h.ESTRATO==int(e)).astype(float); p,v=lin(y,dom); n=int(dom.sum())
        vs=p*(1-p)/n; rows.append(dict(variable=v_name,estrato='E'+e,n=n,segmentos=h[dom>0].SEGMENTO.nunique(),p=p,ee_mas=np.sqrt(vs),ee_conglom=np.sqrt(v),deff=v/vs if vs>0 else np.nan))
        wd=h.w*dom; Z+=W[e]*wd*(y-p)/wd.sum()
    P=sum(W[e]*r['p'] for e,r in zip('123456',rows[-6:]))
    tc=Z.groupby(h.SEGMENTO).sum(); vc=C/(C-1)*((tc-tc.mean())**2).sum()
    vs=sum(W[e]**2*r['p']*(1-r['p'])/r['n'] for e,r in zip('123456',rows[-6:]))
    rows.append(dict(variable=v_name,estrato='Ciudad (postestr.)',n=int(h.ESTRATO.between(1,6).sum()),segmentos=C,p=P,ee_mas=np.sqrt(vs),ee_conglom=np.sqrt(vc),deff=vc/vs))
R=pd.DataFrame(rows); R['ic95_mas_pp']=1.96*R.ee_mas*100; R['ic95_conglom_pp']=1.96*R.ee_conglom*100
pd.set_option('display.width',200); print(R.round(3).to_string()); print('segmentos', C)
R.to_csv('/home/claude/v3/ECV2024_efecto_diseno.csv',sep=';',index=False,encoding='utf-8-sig',decimal=',')
