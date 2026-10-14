"""Regresión logística de tenencia de AC con la ECV 2024 (Barranquilla, E1-E6, base corregida 709 hogares)
y modelo de imputación con variables disponibles en el catastro."""
import pandas as pd, numpy as np, statsmodels.api as sm, pickle, warnings
warnings.filterwarnings('ignore')
B='/home/claude/work/Traspaso_tesis_Barranquilla/datos_procesados/'
n=lambda s: pd.to_numeric(s.astype(str).str.strip().str.replace(',','.'),errors='coerce')
b=pd.read_csv(B+'ECV2024_Barranquilla_hogares.csv',sep=';',dtype=str,encoding='utf-8-sig')
b['W']=n(b.FEX_C); b['E']=n(b.ESTRATO); b=b[b.E.between(1,6)].copy()
b['AC']=n(b.TIENE_AC).fillna(0)
b['T3']=b.P4567.str.strip().map({'1':'Concreto','3':'Asbesto'}).fillna('Zinc/otro')
b['EG']=b.E.map({1:'E1-2',2:'E1-2',3:'E3',4:'E4',5:'E5-6',6:'E5-6'})
b['APTO']=(b.TIPO_VIVIENDA.str.strip()=='2').astype(float)
pc=n(b.PERCAPITA); b['ING0']=(pc.fillna(0)<=0)
b['lny']=np.log(pc.clip(lower=1e4))
b['TEN']=b.TENENCIA.str.strip().map(lambda x:'Propia' if x in('1','2') else('Arriendo' if x=='3' else 'Otra'))
b['PERS']=n(b.CANT_PERSONAS_HOGAR)
b['P5']=(b.PERS>=5).astype(float)
b['wn']=b.W/b.W.mean()
print('n',len(b),'ingreso<=0',b.ING0.sum(),'techo',b.T3.value_counts().to_dict(),'P4567',b.P4567.value_counts().to_dict())
def auc(y,p,w):
    o=np.argsort(p); y=np.asarray(y)[o]; w=np.asarray(w)[o]
    pos=w*y; neg=w*(1-y); cn=np.cumsum(neg)
    return float((pos*(cn-neg/2)).sum()/(pos.sum()*neg.sum()))
def logit(data,cats,num=[]):
    X=pd.get_dummies(data[cats],drop_first=False).astype(float)
    drop=[c for c in X.columns if c in('T3_Concreto','EG_E1-2','TEN_Propia')]
    X=X.drop(columns=drop)
    for v in num: X[v]=data[v]
    X=sm.add_constant(X)
    r=sm.GLM(data.AC,X,family=sm.families.Binomial(),var_weights=data.wn).fit(cov_type='HC1')
    ci=r.conf_int()
    out=pd.DataFrame({'coef':r.params,'OR':np.exp(r.params),'IC95_inf':np.exp(ci[0]),'IC95_sup':np.exp(ci[1]),'p':r.pvalues})
    p=r.predict(X)
    return out,dict(n=int(r.nobs),pseudoR2=1-r.llf/r.llnull,AUC=auc(data.AC,p,data.W)),r,X
M={}
d=b[~b.ING0].copy()
M['M1: techo']=logit(d,['T3'])
M['M2: techo + estrato']=logit(d,['T3','EG'])
M['M3: techo + estrato + apto + ln ingreso']=logit(d,['T3','EG'],['APTO','lny'])
M['M4: M3 + tenencia + hogar 5+']=logit(d,['T3','EG','TEN'],['APTO','lny','P5'])
M['I: imputación (estrato + apto)']=logit(b,['EG'],['APTO'])
for k,(o,s,r,X) in M.items():
    print('\n',k,{a:round(v,3) for a,v in s.items()}); print(o.round(3).to_string())
pickle.dump({k:(o,s) for k,(o,s,r,X) in M.items()},open('/home/claude/work/logit24.pkl','wb'))
