"""VARIANTE C (v3): tasa objetivo = serie mezcla A/B.
P(AC) por vivienda del catastro para cada año 2015-2027.
Tasa objetivo del estrato = serie suavizada (serie_suavizada.py). Dentro del estrato:
P(AC|techo) = logistic(a + b_techo), b de M2 (ECV 2024). El intercepto a se calibra para que la media
de las viviendas del CATASTRO del estrato sea igual a la tasa objetivo (así E1 queda forzado a la ECV).
Edificio de 4+ pisos -> concreto; hasta 3 pisos -> concreto restante + asbesto/zinc en proporción ECV 2024."""
import pandas as pd, numpy as np, pickle
from scipy.optimize import brentq
B='/home/claude/v2/Traspaso_tesis_Barranquilla_v2/datos_procesados/'
n=lambda s: pd.to_numeric(s.astype(str).str.strip().str.replace(',','.'),errors='coerce')
L=pickle.load(open('/home/claude/v2/Traspaso_tesis_Barranquilla_v2/datos_intermedios/logit24.pkl','rb'))
R=pd.read_csv('/home/claude/v3/Tenencia_AC_sensibilidad_AB.csv',sep=';',decimal=',',encoding='utf-8-sig'); R=R[R.variante=='C'].rename(columns={'p':'p_suav'}); S={'R':R}
o=L['M2: techo + estrato'][0]; bt={'Concreto':0.0,'Asbesto':o.loc['T3_Asbesto','coef'],'Zinc/otro':o.loc['T3_Zinc/otro','coef']}
b=pd.read_csv(B+'ECV2024_Barranquilla_hogares.csv',sep=';',dtype=str,encoding='utf-8-sig')
b['W']=n(b.FEX_C); b['E']=n(b.ESTRATO); b=b[b.E.between(1,6)]
b['T3']=b.P4567.str.strip().map({'1':'Concreto','3':'Asbesto'}).fillna('Zinc/otro')
sh=b.pivot_table(index='E',columns='T3',values='W',aggfunc='sum',fill_value=0); sh=sh.div(sh.sum(axis=1),axis=0)
c=pd.read_csv(B+'Catastro_posicion_cubierta.csv',sep=';',encoding='utf-8-sig',usecols=['estrato_num','uso','POSICION'])
c['ED4']=c.uso.str.contains('Apartamentos')
lg=lambda z:1/(1+np.exp(-z))
comp=[]
for e in range(1,7):
    Sx=sh.loc[e]; ce=c[c.estrato_num==e]; f4=ce.ED4.mean()
    rc=max(Sx['Concreto']-f4,0)/(1-f4); oth=Sx['Asbesto']+Sx['Zinc/otro']
    m3={'Concreto':rc,'Asbesto':(1-rc)*Sx['Asbesto']/oth,'Zinc/otro':(1-rc)*Sx['Zinc/otro']/oth}
    comp.append(dict(E=e,f4=f4,m3=m3,viv=len(ce),Sx=Sx))
rows=[]
for r in S['R'].itertuples():
    e=int(r.estrato[1]); k=comp[e-1]
    def parts(a):
        p={t:lg(a+bt[t]) for t in bt}; p4=p['Concreto']; p3=sum(k['m3'][t]*p[t] for t in bt)
        return k['f4']*p4+(1-k['f4'])*p3,p4,p3,p
    a=brentq(lambda a: parts(a)[0]-r.p_suav,-30,30); m,p4,p3,p=parts(a)
    rows.append(dict(anio=r.anio,estrato=r.estrato,p_objetivo=r.p_suav,intercepto=a,pAC_concreto=p['Concreto'],pAC_asbesto=p['Asbesto'],pAC_zinc_otro=p['Zinc/otro'],
        viviendas=k['viv'],frac_edificio4=k['f4'],concreto_resto_hasta3=k['m3']['Concreto'],asbesto_hasta3=k['m3']['Asbesto'],zinc_hasta3=k['m3']['Zinc/otro'],
        pAC_edificio4=p4,pAC_hasta3=p3,pAC_estrato_catastro=m))
I=pd.DataFrame(rows)
pd.set_option('display.width',250)
print(I[I.anio==2024].round(3).to_string())
city=I.groupby('anio').apply(lambda d:(d.pAC_estrato_catastro*d.viviendas).sum()/d.viviendas.sum()*100)
print(city.round(1).to_dict())
# P(AC) media por posición frente a la cubierta, 2024 y 2019
c['EST']='E'+c.estrato_num.astype(str)
pos=[]
for a in (2019,2024):
    m=I[I.anio==a].set_index('estrato'); P=np.where(c.ED4,c.EST.map(m.pAC_edificio4),c.EST.map(m.pAC_hasta3))
    g=pd.Series(P).groupby(c.POSICION.values).mean(); pos.append(g.rename(a))
pos=pd.concat(pos,axis=1); print(pos.round(3))
pickle.dump(dict(I=I,pos=pos,bt=bt,city=city),open('/home/claude/v3/imput_anual_C.pkl','wb'))
I.to_csv('/home/claude/v3/Catastro_PAC_por_anio_estrato_tipo_C.csv',sep=';',index=False,encoding='utf-8-sig')
