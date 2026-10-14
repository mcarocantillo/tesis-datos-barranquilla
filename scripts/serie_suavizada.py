"""Tenencia de AC suavizada por estrato y año (2015-2027), Barranquilla.
Para cada estrato: GLM binomial logit(p) = b0 + b1*(año-2021), con las tasas ponderadas de la ECV
(P1077S11) y var_weights = n hogares; olas 2018, 2019, 2021-2025 (2020 se excluye: encuesta en parte
telefónica y año excluido de la calibración). La varianza se infla por la sobredispersión entre olas
(escala de Pearson, mínimo 1). Cada año se resume como Beta(alfa, beta) por momentos."""
import pandas as pd, numpy as np, statsmodels.api as sm, pickle
B='/home/claude/work/Traspaso_tesis_Barranquilla/datos_procesados/'
s=pd.read_csv(B+'ECV_2018_2025_Barranquilla_tenencia_por_estrato.csv',sep=';',encoding='utf-8-sig',dtype={'grupo':str})
s=s[s.grupo.isin(list('123456'))].copy(); s['p']=s.w_ac/s.w; s['E']=s.grupo.astype(int)
anios=np.arange(2015,2028); rows=[]; fits=[]
for e,d in s.groupby('E'):
    f=d[d.anio!=2020]
    X=sm.add_constant(f.anio-2021.0)
    m=sm.GLM(f.p,X,family=sm.families.Binomial(),var_weights=f.n).fit()
    phi=max(1.0,m.pearson_chi2/m.df_resid)
    cov=m.cov_params()*phi
    fits.append(dict(estrato=f'E{e}',b0=m.params.iloc[0],b1=m.params.iloc[1],se_b1=np.sqrt(cov.iloc[1,1]),p_b1=2*(1-__import__('scipy').stats.norm.cdf(abs(m.params.iloc[1]/np.sqrt(cov.iloc[1,1])))),
                     sobredispersion=phi,olas=len(f),n_total=int(f.n.sum())))
    for a in anios:
        x=np.array([1,a-2021.0]); eta=x@m.params.values; se=np.sqrt(x@cov.values@x)
        mu=1/(1+np.exp(-eta)); sd=mu*(1-mu)*se
        k=mu*(1-mu)/sd**2-1; al,be=mu*k,(1-mu)*k
        lo,hi=1/(1+np.exp(-(eta-1.645*se))),1/(1+np.exp(-(eta+1.645*se)))
        ob=d[d.anio==a]
        rows.append(dict(estrato=f'E{e}',anio=a,n=int(ob.n.iloc[0]) if len(ob) else np.nan,p_obs=float(ob.p.iloc[0]) if len(ob) else np.nan,
            p_suav=mu,sd=sd,ic90_inf=lo,ic90_sup=hi,beta_alfa=al,beta_beta=be,
            tipo='observado y ajustado' if (len(ob) and a!=2020) else ('observado, no usado en el ajuste' if len(ob) else ('extrapolado' if a<2018 or a>2025 else 'interpolado'))))
R=pd.DataFrame(rows); Fz=pd.DataFrame(fits)
pd.set_option('display.width',250)
print(Fz.round(3).to_string())
print(R.pivot(index='anio',columns='estrato',values='p_suav').mul(100).round(1))
print(R.pivot(index='anio',columns='estrato',values='sd').mul(100).round(1))
# postestratificación con SUI dic (2026-2027: pesos de dic-2025)
sui=pd.read_csv(B+'SUI_Barranquilla_urbano_residencial_2015_2026.csv',sep=';',encoding='utf-8-sig',dtype={'estrato':str})
sui=sui[(sui.mes==12)&sui.estrato.isin(list('123456'))]; sui['W']=sui.suscriptores/sui.groupby('anio').suscriptores.transform('sum')
W=sui.pivot(index='anio',columns='estrato',values='W')
for a in (2026,2027): W.loc[a]=W.loc[2025]
W.columns=['E'+c for c in W.columns]
P=R.pivot(index='anio',columns='estrato',values='p_suav'); S=R.pivot(index='anio',columns='estrato',values='sd')
city=pd.DataFrame({'pct_suav':(W*P).sum(1)*100,'sd_pp':np.sqrt((W**2*S**2).sum(1))*100})
raw=pd.read_pickle('/home/claude/work/post_res.pkl')[['pct_ac','ic95_ac']]
city=city.join(raw)
print(city.round(1))
pickle.dump(dict(R=R,F=Fz,W=W,city=city),open('/home/claude/work/suav.pkl','wb'))
