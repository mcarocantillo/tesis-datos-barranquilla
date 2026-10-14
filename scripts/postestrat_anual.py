import pandas as pd, numpy as np
B='/home/claude/work/Traspaso_tesis_Barranquilla/datos_procesados/'
e=pd.read_csv(B+'ECV_2018_2025_Barranquilla_tenencia_por_estrato.csv',sep=';',encoding='utf-8-sig',dtype={'grupo':str})
s=pd.read_csv(B+'SUI_Barranquilla_urbano_residencial_2015_2026.csv',sep=';',encoding='utf-8-sig',dtype={'estrato':str})
s=s[(s.mes==12)&(s.estrato.isin(list('123456')))]
s['W']=s.suscriptores/s.groupby('anio').suscriptores.transform('sum')
e=e[e.grupo.isin(list('123456'))].rename(columns={'grupo':'estrato'})
d=e.merge(s[['anio','estrato','suscriptores','W']],on=['anio','estrato'])
for v in ['ac','vent','nevera']:
    d['p_'+v]=d['w_'+v]/d.w
    d['var_'+v]=d.W**2*d['p_'+v]*(1-d['p_'+v])/d.n
    # Agresti-Coull: evita varianza 0 cuando p=0 o 1 (E6)
    pt=(d.n*d['p_'+v]+2)/(d.n+4)
    d['varAC_'+v]=d.W**2*pt*(1-pt)/(d.n+4)
d['Wp_ac']=d.W*d.p_ac
g=d.groupby('anio')
r=pd.DataFrame({'n_E1_6':g.n.sum(),'suscriptores_dic':g.suscriptores.sum()})
for v in ['ac','vent','nevera']:
    r['pct_'+v]=(g.apply(lambda x:(x.W*x['p_'+v]).sum())*100)
    r['se_'+v]=np.sqrt(g['var_'+v].sum())*100
    r['se_AgCoull_'+v]=np.sqrt(g['varAC_'+v].sum())*100
r['ic95_ac']=1.96*r.se_ac; r['ic95_ac_AgCoull']=1.96*r.se_AgCoull_ac
# pesos crudos ECV (estratos 1-6)
r['pct_ac_pesosECV']=g.apply(lambda x:x.w_ac.sum()/x.w.sum()*100)
# descomposición del cambio vs 2019: efecto tasa vs efecto composición
b=d[d.anio==2019].set_index('estrato')
dec=[]
for a,x in d.groupby('anio'):
    x=x.set_index('estrato')
    tasa=(b.W*(x.p_ac-b.p_ac)).sum()*100
    comp=((x.W-b.W)*x.p_ac).sum()*100
    dec.append((a,tasa,comp))
dec=pd.DataFrame(dec,columns=['anio','efecto_tasas_pp','efecto_composicion_pp']).set_index('anio')
r=r.join(dec)
se19=r.loc[2019,'se_ac']; p19=r.loc[2019,'pct_ac']
r['dif_vs_2019_pp']=r.pct_ac-p19
r['z_vs_2019']=np.where(r.index==2019,np.nan,r.dif_vs_2019_pp/np.sqrt(r.se_ac**2+se19**2))
pd.set_option('display.width',250)
print(d[['anio','estrato','n','p_ac','W']].pivot(index='anio',columns='estrato',values='W').round(3))
print(r.round(2).T)
d.to_pickle('/home/claude/work/post_det.pkl'); r.to_pickle('/home/claude/work/post_res.pkl')
