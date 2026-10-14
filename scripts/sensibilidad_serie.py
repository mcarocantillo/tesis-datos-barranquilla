"""Sensibilidad de la serie suavizada de tenencia de AC.
A (base, sesión 2): tendencia logit-lineal en todos los estratos, var_weights = n.
B: tendencia solo donde es significativa (p<0,05: E1 y E3); en E2, E4, E5 y E6 nivel constante (media de las olas);
   n efectivo = n / 1,5 (efecto de diseño medido en la ECV 2024). Sobredispersión de Pearson (mínimo 1) en ambos."""
import pandas as pd, numpy as np, statsmodels.api as sm
from scipy import stats
s=pd.read_csv('/home/claude/v2/Traspaso_tesis_Barranquilla_v2/datos_intermedios/ecv_series_raw.csv')
s=s[s.grupo.isin(list('123456'))&(s.anio!=2020)].copy(); s['p']=s.w_ac/s.w; s['E']='E'+s.grupo.astype(str)
sui=pd.read_csv('/mnt/user-data/outputs/SUI_Barranquilla_urbano_residencial_2015_2026.csv',sep=';',dtype={'estrato':str})
sui=sui[(sui.mes==12)&sui.estrato.isin(list('123456'))]; sui['W']=sui.suscriptores/sui.groupby('anio').suscriptores.transform('sum')
W=sui.pivot(index='anio',columns='estrato',values='W'); W.loc[2026]=W.loc[2025]; W.loc[2027]=W.loc[2025]; W.columns=['E'+c for c in W.columns]
anios=np.arange(2015,2028); DEFF=1.5; out=[]; fit=[]
for var in ['A','B']:
    for e,d in s.groupby('E'):
        n=d.n/(DEFF if var=='B' else 1)
        trend = True if var=='A' else e in ('E1','E3')
        X=sm.add_constant(d.anio-2021.0) if trend else np.ones((len(d),1))
        m=sm.GLM(d.p,X,family=sm.families.Binomial(),var_weights=n).fit()
        phi=max(1.0,m.pearson_chi2/m.df_resid); cov=np.atleast_2d(m.cov_params().values*phi); b=m.params.values
        if trend: fit.append(dict(variante=var,estrato=e,b1=b[1],ee=np.sqrt(cov[1,1]),p=2*stats.norm.sf(abs(b[1]/np.sqrt(cov[1,1]))),phi=phi))
        else: fit.append(dict(variante=var,estrato=e,b1=0,ee=np.nan,p=np.nan,phi=phi))
        for a in anios:
            x=np.array([1,a-2021.0]) if trend else np.array([1.0])
            eta=x@b; se=np.sqrt(x@cov@x); mu=1/(1+np.exp(-eta)); sd=mu*(1-mu)*se
            k=mu*(1-mu)/sd**2-1
            out.append(dict(variante=var,estrato=e,anio=a,p=mu,sd=sd,alfa=mu*k,beta=(1-mu)*k))
R=pd.DataFrame(out); F=pd.DataFrame(fit)
city=[]
for var,g in R.groupby('variante'):
    P=g.pivot(index='anio',columns='estrato',values='p'); S=g.pivot(index='anio',columns='estrato',values='sd')
    city.append(pd.DataFrame({'variante':var,'pct':(W*P).sum(1)*100,'sd_pp':np.sqrt((W**2*S**2).sum(1))*100}))
C=pd.concat(city).reset_index().rename(columns={'index':'anio'})
pd.set_option('display.width',220)
print(F.round(3).to_string())
print(R.pivot_table(index='anio',columns=['variante','estrato'],values='p').mul(100).round(1).to_string())
print(C.pivot(index='anio',columns='variante',values=['pct','sd_pp']).round(1))
R.to_csv('/home/claude/v3/Tenencia_AC_sensibilidad_AB.csv',sep=';',index=False,encoding='utf-8-sig',decimal=',')
C.to_csv('/home/claude/v3/Tenencia_AC_ciudad_sensibilidad_AB.csv',sep=';',index=False,encoding='utf-8-sig',decimal=',')
F.to_csv('/home/claude/v3/Tenencia_AC_ajustes_AB.csv',sep=';',index=False,encoding='utf-8-sig',decimal=',')
# C: mezcla 50/50 de A y B (recoge la incertidumbre de si hay o no tendencia)
A=R[R.variante=='A'].set_index(['estrato','anio']); Bv=R[R.variante=='B'].set_index(['estrato','anio'])
m=(A.p+Bv.p)/2; v=(A.sd**2+Bv.sd**2)/2+(A.p-Bv.p)**2/4; sd=np.sqrt(v); k=m*(1-m)/v-1
M=pd.DataFrame({'variante':'C','p':m,'sd':sd,'alfa':m*k,'beta':(1-m)*k}).reset_index()
P=M.pivot(index='anio',columns='estrato',values='p'); S=M.pivot(index='anio',columns='estrato',values='sd')
CC=pd.DataFrame({'variante':'C','pct':(W*P).sum(axis=1)*100,'sd_pp':np.sqrt((W**2*S**2).sum(axis=1))*100}).reset_index()
print(M.pivot(index='anio',columns='estrato',values='p').mul(100).round(1)); print(CC.round(1).to_string())
pd.concat([R,M]).to_csv('/home/claude/v3/Tenencia_AC_sensibilidad_AB.csv',sep=';',index=False,encoding='utf-8-sig',decimal=',')
pd.concat([C,CC]).to_csv('/home/claude/v3/Tenencia_AC_ciudad_sensibilidad_AB.csv',sep=';',index=False,encoding='utf-8-sig',decimal=',')
