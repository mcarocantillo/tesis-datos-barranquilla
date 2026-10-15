"""Figuras del sitio. Paleta categórica fija (estrato = misma color en todas las figuras)."""
import pickle, numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
S='/home/claude/book/site/figuras/'; V2='/home/claude/v2/Traspaso_tesis_Barranquilla_v2/'; V3='/home/claude/v3/'
PAL=['#2a78d6','#eb6834','#1baf7a','#eda100','#e87ba4','#008300','#6250d6','#e34948']
EST={f'E{i+1}':PAL[i] for i in range(6)}
TXT='#0b0b0b'; TXT2='#52514e'; GRID='#e4e3df'
plt.rcParams.update({'font.size':11,'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#9a9993',
    'axes.labelcolor':TXT2,'xtick.color':TXT2,'ytick.color':TXT2,'axes.grid':True,'grid.color':GRID,'grid.linewidth':.8,'axes.axisbelow':True,
    'axes.titlelocation':'left','axes.titlesize':13,'axes.titlecolor':TXT,'legend.frameon':False,'figure.facecolor':'#fcfcfb','axes.facecolor':'#fcfcfb'})
def fmt(v,d=1): return f'{v:.{d}f}'.replace('.',',')
def save(fig,n,sub=None):
    if sub: fig.text(0.012,0.012,sub,fontsize=8.5,color=TXT2)
    fig.tight_layout(rect=(0,0.03 if sub else 0,1,1)); fig.savefig(S+n,dpi=160); plt.close(fig)
def title(ax,t,s=None):
    ax.set_title(t,pad=22 if s else 8,fontweight='bold')
    if s: ax.text(0,1.02,s,transform=ax.transAxes,fontsize=10,color=TXT2)
raw=pd.read_csv(V2+'datos_intermedios/ecv_series_raw.csv'); raw=raw[raw.grupo.isin(list('123456'))].copy(); raw['E']='E'+raw.grupo.astype(str); raw['p']=raw.w_ac/raw.w*100

# 1 tenencia por estrato C
R=pd.read_csv(V3+'Tenencia_AC_sensibilidad_AB.csv',sep=';',decimal=','); C=R[R.variante=='C']
fig,ax=plt.subplots(figsize=(9.5,5.4))
ax.axvspan(2014.6,2017.5,color='#efeee9',zorder=0,lw=0); ax.axvspan(2025.5,2027.4,color='#efeee9',zorder=0,lw=0)
for e,c in EST.items():
    d=C[C.estrato==e]; ax.fill_between(d.anio,(d.p-1.96*d.sd)*100,(d.p+1.96*d.sd)*100,color=c,alpha=.08,lw=0)
    ax.plot(d.anio,d.p*100,color=c,lw=2.2); o=raw[raw.E==e]; ax.scatter(o.anio,o.p,color=c,s=26,zorder=3,edgecolor='white',lw=1)
    ax.text(2027.55,d.p.iloc[-1]*100,e,color=c,va='center',fontweight='bold')
ax.text(2014.75,3,'sin ola ECV',color=TXT2,fontsize=9); ax.text(2025.6,3,'proyección',color=TXT2,fontsize=9)
ax.set_xlim(2014.6,2028.2); ax.set_ylim(0,102); ax.set_ylabel('% de hogares con A/C')
title(ax,'La tenencia de A/C sube con el estrato: de 13 % (E1) a 98 % (E6) en 2024','Líneas: variante C con IC 95 %; puntos: olas de la ECV en Barranquilla')
save(fig,'tenencia_estrato_C.png','Fuente: DANE, ECV 2018–2025 (P1077S11), ponderado con FEX_C.')

# 2 ciudad variantes
Cc=pd.read_csv(V3+'Tenencia_AC_ciudad_sensibilidad_AB.csv',sep=';',decimal=',')
p=Cc.pivot(index='anio',columns='variante',values='pct'); sd=Cc.pivot(index='anio',columns='variante',values='sd_pp')
fig,ax=plt.subplots(figsize=(9.5,5))
ax.fill_between(p.index,p.C-1.96*sd.C,p.C+1.96*sd.C,color=PAL[0],alpha=.15,lw=0)
ax.plot(p.index,p.A,color=PAL[1],lw=2,label='A: tendencia en todos los estratos'); ax.plot(p.index,p.B,color=PAL[2],lw=2,ls='--',label='B: tendencia solo en E1 y E3')
ax.plot(p.index,p.C,color=PAL[0],lw=3,marker='o',ms=5,label='C: mezcla (adoptada) con IC 95 %')
for v,c,dy in [('A',PAL[1],6),('C',PAL[0],0),('B',PAL[2],-6)]: ax.annotate(fmt(p[v].iloc[-1])+' %',(2027,p[v].iloc[-1]),xytext=(6,dy),textcoords='offset points',color=c,va='center',fontweight='bold')
ax.annotate(fmt(p.C.loc[2024])+' %',(2024,p.C.loc[2024]),xytext=(0,-22),textcoords='offset points',ha='center',color=PAL[0],fontweight='bold')
ax.set_xlim(2014.6,2028.3); ax.set_ylabel('% de hogares con A/C'); ax.legend(loc='upper left',fontsize=9.5)
title(ax,'Hogares con A/C en la ciudad: 31 % en 2015, 41 % en 2024 (variante C)','Postestratificado con los suscriptores del SUI de diciembre de cada año')
save(fig,'tenencia_ciudad_variantes.png','Fuente: ECV 2018–2025 (sin 2020) y SUI. A y B difieren hasta 2,9 puntos en 2015.')

# 3 AC por estrato 2019 vs 2024 con IC (deff 2024)
d19=raw[raw.anio==2019].set_index('E'); d24=raw[raw.anio==2024].set_index('E')
df=pd.read_csv(V3+'ECV2024_efecto_diseno.csv',sep=';',decimal=','); df=df[df.variable=='AC']
fig,ax=plt.subplots(figsize=(9.5,5)); x=np.arange(6); E=list(EST)
e19=1.96*np.sqrt(d19.p/100*(1-d19.p/100)/(d19.n/1.5))*100
e24=df.set_index('estrato').loc[E].ic95_conglom_pp.fillna(0).values
ax.bar(x-.2,d19.loc[E].p,.38,color=PAL[0],label='2019',yerr=e19.loc[E],ecolor='#7aa9e6',capsize=3)
ax.bar(x+.2,d24.loc[E].p,.38,color=PAL[1],label='2024',yerr=e24,ecolor='#f2a07f',capsize=3)
for i,e in enumerate(E):
    ax.text(i-.2,d19.p[e]+e19[e]+1.5,fmt(d19.p[e],0),ha='center',fontsize=9,color=TXT); ax.text(i+.2,d24.p[e]+e24[i]+1.5,fmt(d24.p[e],0),ha='center',fontsize=9,color=TXT)
ax.set_xticks(x); ax.set_xticklabels([f'Estrato {i+1}' for i in range(6)]); ax.set_ylim(0,112); ax.set_ylabel('% de hogares con A/C'); ax.legend(loc='upper left')
title(ax,'Tenencia de A/C por estrato, ECV 2019 y 2024','Barras de error: IC 95 % con efecto de diseño (2024 medido; 2019 con deff = 1,5)')
save(fig,'ac_estrato_2019_2024.png','Fuente: DANE, ECV 2019 (n = 957 en E1–E6) y 2024 (n = 646).')

# 4 quintiles de ingreso
T=pickle.load(open('/home/claude/work/deep_tables.pkl','rb'))
q19=T['ecv19_ac_quintil'].ac.values; q24=np.array([12.8,16.5,27.8,43.8,82.9])
fig,ax=plt.subplots(figsize=(9.5,4.8)); x=np.arange(5)
ax.bar(x-.2,q19,.38,color=PAL[0],label='2019'); ax.bar(x+.2,q24,.38,color=PAL[1],label='2024')
for i in range(5): ax.text(i-.2,q19[i]+1.5,fmt(q19[i],0),ha='center',fontsize=9); ax.text(i+.2,q24[i]+1.5,fmt(q24[i],0),ha='center',fontsize=9)
ax.set_xticks(x); ax.set_xticklabels(['Q1 (más bajo)','Q2','Q3','Q4','Q5 (más alto)']); ax.set_ylabel('% de hogares con A/C'); ax.set_ylim(0,95); ax.legend(loc='upper left')
title(ax,'El A/C se concentra en el quintil de mayor ingreso','Quintiles de ingreso por persona del hogar (2024 sin hogares de ingreso 0)')
save(fig,'ac_quintil.png','Fuente: DANE, ECV 2019 y 2024, Barranquilla.')

# 5 techos por grupo de estrato (2019) apilado
t=T['ecv19_TECHO_P4567'].set_index('G')[['Plancha de concreto','Asbesto-cemento','Zinc / metálica','Teja de barro','Teja plástica']]
t2=pd.DataFrame({'Plancha de concreto':[28.6,58.2,88.9],'Asbesto-cemento':[60.4,39.8,11.1],'Zinc / metálica':[11.0,0,0],'Teja de barro':[0,2.0,0],'Teja plástica':[0,0,0]},index=['1-2','3-4','5-6'])
cols={'Plancha de concreto':PAL[0],'Asbesto-cemento':PAL[3],'Zinc / metálica':PAL[1],'Teja de barro':PAL[4],'Teja plástica':PAL[2]}
rows=[]
for g,lab in [('1-2','Estratos 1–2'),('3-4','Estratos 3–4'),('5-6','Estratos 5–6')]:
    rows.append((lab+' · 2019',t.loc[g])); rows.append((lab+' · 2024',t2.loc[g]))
fig,ax=plt.subplots(figsize=(9.5,4.8)); left=np.zeros(len(rows)); yy=np.array([0,1,2.6,3.6,5.2,6.2])
for k in t.columns:
    v=np.array([r[1][k] for r in rows]); ax.barh(yy,v,left=left,color=cols[k],label=k,edgecolor='#fcfcfb',lw=1.5,height=.85)
    for i2 in range(len(rows)):
        if v[i2]>=8: ax.text(left[i2]+v[i2]/2,yy[i2],fmt(v[i2],0),ha='center',va='center',color='white',fontsize=9,fontweight='bold')
    left+=v
ax.set_yticks(yy); ax.set_yticklabels([r[0] for r in rows]); ax.invert_yaxis(); ax.set_xlim(0,100); ax.grid(axis='y',visible=False); ax.set_xlabel('% de hogares')
ax.legend(loc='upper center',bbox_to_anchor=(.45,-.14),ncol=5,fontsize=9)
title(ax,'Los techos livianos (asbesto-cemento y zinc) dominan en los estratos 1–2','Material del techo, ECV 2019 y 2024')
save(fig,'techos_estrato.png','Fuente: DANE, ECV 2019 y 2024 (P4567), % de hogares.')

# 6 forest plot OR 2024 M3
L=pd.read_csv(V2+'datos_procesados/Logit_ECV2024_modelos.csv',sep=';'); L=L[L.modelo.str.startswith('M3')&(L.variable!='const')].copy()
lab={'T3_Asbesto':'Techo asbesto-cemento (vs concreto)','T3_Zinc/otro':'Techo zinc u otro (vs concreto)','EG_E3':'Estrato 3 (vs 1–2)','EG_E4':'Estrato 4 (vs 1–2)','EG_E5-6':'Estratos 5–6 (vs 1–2)','lny':'ln(ingreso por persona), +1','TIPO2_Apartamento':'Apartamento (vs casa)'}
L['lab']=L.variable.map(lab); L=L.dropna(subset=['lab']).iloc[::-1]
fig,ax=plt.subplots(figsize=(9.5,4.6)); y=np.arange(len(L))
colr=[PAL[1] if o<1 else PAL[0] for o in L.OR]
ax.hlines(y,L.IC95_inf,L.IC95_sup,color=colr,lw=2.5); ax.scatter(L.OR,y,color=colr,s=60,zorder=3,edgecolor='white')
for i,(o,hi) in enumerate(zip(L.OR,L.IC95_sup)): ax.text(hi*1.12,i,fmt(o,2),va='center',fontsize=9.5)
ax.axvline(1,color='#9a9993',lw=1); ax.set_xscale('log'); ax.set_yticks(y); ax.set_yticklabels(L.lab); ax.set_xlabel('Razón de momios (escala logarítmica); < 1 reduce la probabilidad de tener A/C')
ax.set_xticks([.05,.1,.25,.5,1,2,5,10,20]); ax.set_xticklabels(['0,05','0,1','0,25','0,5','1','2','5','10','20'])
title(ax,'El techo liviano reduce la probabilidad de A/C','A igual estrato e ingreso. Regresión logística ponderada, ECV 2024 (n = 633), IC 95 %')
save(fig,'logit_or.png','Fuente: DANE, ECV 2024. Modelo M3; pseudo-R² 0,28; AUC 0,84.')

# 7 horas de AC distribución
A=pickle.load(open('/home/claude/work/extra_ecv19.pkl','rb')); H=A['horas_ac_hist']
gc={'E1-2':PAL[0],'E3':PAL[2],'E4':PAL[3],'E5-6':PAL[5]}
fig,ax=plt.subplots(figsize=(9.5,4.6)); x=np.arange(H.shape[1]); w=.2
for j,(g,row) in enumerate(H.iterrows()): ax.bar(x+(j-1.5)*w,row.values,w,color=gc[g],label=g.replace('E','Estrato ').replace('-','–'))
ax.set_xticks(x); ax.set_xticklabels([c+' h' for c in H.columns]); ax.set_ylabel('% de hogares con A/C'); ax.legend()
title(ax,'La mayoría de los hogares usa el A/C entre 5 y 8 horas al día','Horas diarias de uso de todos los equipos del hogar, por grupo de estrato')
save(fig,'horas_ac.png','Fuente: DANE, ECV 2019 (P5524), hogares con A/C (n = 289).')

# 8 ventilador con y sin AC
Vt=A['vent_con_sin_ac']; Vt=Vt[Vt.estrato.isin(['E1','E2','E3','E4'])]
fig,ax=plt.subplots(figsize=(9.5,4.4)); x=np.arange(4)
si=Vt[Vt.tiene_ac=='Sí'].horas_vent_media.values; no=Vt[Vt.tiene_ac=='No'].horas_vent_media.values
ax.bar(x-.2,no,.38,color=PAL[2],label='Hogares sin A/C'); ax.bar(x+.2,si,.38,color=PAL[0],label='Hogares con A/C')
for i in range(4): ax.text(i-.2,no[i]+.2,fmt(no[i]),ha='center',fontsize=9); ax.text(i+.2,si[i]+.2,fmt(si[i]),ha='center',fontsize=9)
ax.set_xticks(x); ax.set_xticklabels([f'Estrato {i+1}' for i in range(4)]); ax.set_ylabel('Horas de ventilador al día'); ax.set_ylim(0,14); ax.legend(loc='upper right')
title(ax,'El ventilador se usa casi igual con o sin A/C','Horas diarias medias de ventilador; E5–E6 casi no tienen hogares sin A/C')
save(fig,'ventilador_con_sin_ac.png','Fuente: DANE, ECV 2019 (P5526), ponderado.')

# 9 neveras tamaño por estrato
Q=T['ecv19_equipos_estrato'].set_index('estrato')
fig,ax=plt.subplots(figsize=(9.5,4.4)); left=np.zeros(6)
for k,c,l in [('nev_pequena',PAL[3],'Pequeña (≤ 1,7 m)'),('nev_mediana',PAL[2],'Mediana (> 1,7 m)'),('nev_grande',PAL[0],'Grande (2 puertas)')]:
    v=Q[k].values; ax.barh(range(6),v,left=left,color=c,label=l,edgecolor='#fcfcfb',lw=1.5)
    for i in range(6):
        if v[i]>=7: ax.text(left[i]+v[i]/2,i,fmt(v[i],0),ha='center',va='center',color='white',fontsize=9,fontweight='bold')
    left+=v
ax.set_yticks(range(6)); ax.set_yticklabels([f'Estrato {i}' for i in Q.index]); ax.invert_yaxis(); ax.set_xlim(0,100); ax.grid(axis='y',visible=False)
ax.legend(loc='upper center',bbox_to_anchor=(.5,-.08),ncol=3,fontsize=9.5)
title(ax,'Las neveras grandes pasan de 6 % en el estrato 1 a 51 % en el 6','Tamaño de la nevera, % de hogares que tienen nevera')
save(fig,'neveras_tamano.png','Fuente: DANE, ECV 2019 (P5514).')

# 10 catastro posición por estrato
Cp=pickle.load(open('/home/claude/work/extra_catastro.pkl','rb'))['cat_pos_pct'].drop(index='Total')
pc={'Casa (suelo y cubierta propia)':PAL[1],'Último piso (bajo cubierta)':PAL[3],'Primer piso con vivienda encima':PAL[2],'Piso intermedio':PAL[0]}
fig,ax=plt.subplots(figsize=(9.5,4.6)); left=np.zeros(6)
for k,c in pc.items():
    v=Cp[k].values; ax.barh(range(6),v,left=left,color=c,label=k,edgecolor='#fcfcfb',lw=1.5)
    for i in range(6):
        if v[i]>=7: ax.text(left[i]+v[i]/2,i,fmt(v[i],0),ha='center',va='center',color='white',fontsize=9,fontweight='bold')
    left+=v
ax.set_yticks(range(6)); ax.set_yticklabels([f'Estrato {i[1]}' for i in Cp.index]); ax.invert_yaxis(); ax.set_xlim(0,100); ax.grid(axis='y',visible=False)
ax.legend(loc='upper center',bbox_to_anchor=(.5,-.08),ncol=2,fontsize=9.5)
title(ax,'Casas en los estratos bajos, torres en los altos','Posición de la vivienda frente a la cubierta, % de viviendas del catastro')
save(fig,'catastro_posicion.png','Fuente: Catastro de Barranquilla, 332.718 viviendas residenciales.')

# 11 P(AC) imputada por tipo de edificio
Ic=pd.read_csv(V3+'Catastro_PAC_por_anio_estrato_tipo_C.csv',sep=';'); Ic=Ic[Ic.anio==2024]
fig,ax=plt.subplots(figsize=(9.5,4.4)); x=np.arange(6)
ax.bar(x-.2,Ic.pAC_hasta3*100,.38,color=PAL[1],label='Vivienda de hasta 3 pisos'); ax.bar(x+.2,Ic.pAC_edificio4*100,.38,color=PAL[0],label='Edificio de 4 o más pisos')
ax.scatter(x,Ic.p_objetivo*100,color=TXT,marker='_',s=500,lw=2,zorder=3,label='Tasa del estrato (variante C)')
ax.set_xticks(x); ax.set_xticklabels([f'Estrato {i+1}' for i in range(6)]); ax.set_ylabel('P(A/C) 2024, %'); ax.set_ylim(0,105); ax.legend(loc='upper left',fontsize=9.5)
title(ax,'Dentro de cada estrato, la torre tiene más A/C que la casa','Probabilidad imputada a las viviendas del catastro, 2024')
save(fig,'pac_tipo_edificio.png','Fuente: imputación con el modelo M2 de la ECV 2024 y la variante C.')

# 12 SUI kWh por suscriptor por estrato y año
sui=pd.read_csv('/mnt/user-data/outputs/SUI_Barranquilla_urbano_residencial_2015_2026.csv',sep=';',dtype={'estrato':str},keep_default_na=False)
sv=sui[(sui.bandera=='')&(sui.anio<=2025)]; an=sv.groupby(['anio','estrato']).kWh_suscriptor.mean().unstack()
fig,ax=plt.subplots(figsize=(9.5,5))
for i in range(6):
    e=str(i+1); ax.plot(an.index,an[e],color=PAL[i],lw=2.2,marker='o',ms=4); ax.text(2025.3,an[e].iloc[-1]+{'1':-9,'4':9}.get(e,0),f'E{e}',color=PAL[i],va='center',fontweight='bold')
ax.plot(an.index,an['total'],color=TXT,lw=2.5,ls='--'); ax.text(2025.3,an['total'].iloc[-1]-26,'Total',color=TXT,va='center',fontweight='bold')
ax.set_xlim(2014.6,2026); ax.set_ylabel('kWh/mes por suscriptor')
title(ax,'El consumo por suscriptor no crece aunque aumente el A/C','Promedio de los meses válidos de cada año, Barranquilla urbano residencial')
save(fig,'sui_kwh_estrato.png','Fuente: SUI, reporte ele_com_096. Nótese: E1 consume más que E2 y E3.')

# 13 estacionalidad
I=pd.read_excel(V3+'SUI_estacionalidad_2015_2025.xlsx',sheet_name='Indice_mensual_2015_2025',index_col=0); I.columns=[str(c) for c in I.columns]
fig,ax=plt.subplots(figsize=(9.5,4.8))
ax.axvspan(1.5,3.5,color='#e8f0fb',lw=0); ax.axvspan(7.5,9.5,color='#fdeee6',lw=0)
for i in range(6): ax.plot(I.index,I[str(i+1)],color=PAL[i],lw=2.2,label=f'E{i+1}')
ax.axhline(1,color='#9a9993',lw=.8); ax.set_xticks(range(1,13)); ax.set_xticklabels(['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic'])
ax.text(2.5,1.105,'base feb–mar',ha='center',color=PAL[0],fontsize=9); ax.text(8.5,1.125,'pico ago–sep',ha='center',color=PAL[1],fontsize=9)
ax.set_ylabel('kWh del mes / promedio del año'); ax.legend(ncol=6,loc='lower right',fontsize=9)
title(ax,'El alza de ago–sep crece con el estrato: +11 % en E1, +28 % en E4–E6','Índice mensual de consumo por suscriptor, 2015–2025')
save(fig,'estacionalidad_sui.png','Fuente: SUI, meses sin bandera de calidad.')

# 14 suscriptores por estrato
sub=sui[(sui.mes==12)&sui.estrato.isin(list('123456'))&(sui.anio<=2025)].pivot(index='anio',columns='estrato',values='suscriptores')
fig,ax=plt.subplots(figsize=(9.5,4.6))
ax.stackplot(sub.index,[sub[str(i+1)]/1000 for i in range(6)],colors=PAL[:6],labels=[f'E{i+1}' for i in range(6)],edgecolor='#fcfcfb',lw=.8)
ax.set_ylabel('Miles de suscriptores (diciembre)'); ax.legend(ncol=6,loc='upper left',fontsize=9,bbox_to_anchor=(0,1.0)); ax.set_xlim(2015,2025)
ax.set_ylim(0,420); ax.annotate('2021: salto de reporte (no usar)',(2021,356.6),xytext=(2021.6,395),arrowprops=dict(arrowstyle='->',color=TXT2),fontsize=9,color=TXT2)
title(ax,'De 282.000 a 330.000 suscriptores residenciales entre 2015 y 2025','Estratos 1–2 suman la mitad de los suscriptores')
save(fig,'sui_suscriptores.png','Fuente: SUI, Barranquilla urbano residencial, diciembre de cada año.')

# 15 ENUT horas por tipo
En=pd.read_csv(V2+'datos_procesados/ENUT2024_25_Atlantico_horas_por_tipo.csv',sep=';',decimal=',')
En=En[En.dia=='entre semana'].set_index('tipo')
orden=['Ocupado','Estudiante','Oficios del hogar','Mayor 65+ no ocupado','Busca trabajo']; En=En.loc[[o for o in orden if o in En.index]]
parts=[('h_dormir','Dormir',PAL[6]),('h_fuera_trabajo','Fuera por trabajo',PAL[1]),('h_viaje_est','Traslado a estudio',PAL[3]),('h_tv','TV',PAL[2]),('h_internet','Internet',PAL[0])]
fig,ax=plt.subplots(figsize=(9.5,4.6)); left=np.zeros(len(En))
for k,l,c in parts:
    v=En[k].values; ax.barh(range(len(En)),v,left=left,color=c,label=l,edgecolor='#fcfcfb',lw=1.2)
    for i in range(len(En)):
        if v[i]>=1: ax.text(left[i]+v[i]/2,i,fmt(v[i]),ha='center',va='center',color='white',fontsize=8.5,fontweight='bold')
    left+=v
ax.set_yticks(range(len(En))); ax.set_yticklabels(En.index); ax.invert_yaxis(); ax.set_xlabel('Horas en un día hábil'); ax.grid(axis='y',visible=False)
ax.legend(loc='upper center',bbox_to_anchor=(.5,-.18),ncol=5,fontsize=9)
title(ax,'Solo los ocupados pasan buena parte del día fuera de casa','Horas en actividades seleccionadas, día hábil, personas de 10 años o más')
save(fig,'enut_horas.png','Fuente: DANE, ENUT 2024–2025, Atlántico cabecera. Los estudiantes no registran horas de clase.')

# 16 GEIH trabajo en casa y alguien en casa
G=pd.read_csv(V2+'datos_procesados/GEIH2024_Barranquilla_AM_resumen_estrato.csv',sep=';',decimal=',')
G=G[G.estrato.astype(str).isin(list('123456'))]
fig,ax=plt.subplots(figsize=(9.5,4.2)); x=np.arange(6)
ax.bar(x,G.trab_casa_pct,color=[PAL[i] for i in range(6)])
for i,v in enumerate(G.trab_casa_pct): ax.text(i,v+.6,fmt(v),ha='center',fontsize=9.5)
ax.set_xticks(x); ax.set_xticklabels([f'Estrato {i+1}' for i in range(6)]); ax.set_ylabel('% de los ocupados'); ax.set_ylim(0,max(G.trab_casa_pct)*1.2)
title(ax,'El trabajo en la propia vivienda sube con el estrato','Ocupados que trabajan en su vivienda')
save(fig,'geih_trabajo_casa.png','Fuente: DANE, GEIH 2024, área metropolitana de Barranquilla.')

# 17 efecto de diseño dumbbell
D=df[df.estrato!='E6'].copy()
fig,ax=plt.subplots(figsize=(9.5,4.2)); y=np.arange(len(D))
ax.hlines(y,D.ic95_mas_pp,D.ic95_conglom_pp,color='#c9c8c2',lw=3)
ax.scatter(D.ic95_mas_pp,y,color=PAL[2],s=70,zorder=3,label='Muestreo simple'); ax.scatter(D.ic95_conglom_pp,y,color=PAL[1],s=70,zorder=3,label='Con el diseño de la ECV')
for i,(a,b,dd) in enumerate(zip(D.ic95_mas_pp,D.ic95_conglom_pp,D.deff)): ax.text(max(a,b)+.4,i,f'deff {fmt(dd,2)}',va='center',fontsize=9,color=TXT2)
ax.set_yticks(y); ax.set_yticklabels([s.replace('E','Estrato ') if s.startswith('E') else s for s in D.estrato]); ax.invert_yaxis(); ax.set_xlabel('Semiancho del IC 95 % (puntos porcentuales)'); ax.legend(loc='lower right'); ax.set_xlim(0,17)
title(ax,'Con el diseño muestral, la incertidumbre de la tenencia de A/C crece','ECV 2024, Barranquilla, 76 segmentos')
save(fig,'efecto_diseno.png','Fuente: DANE, ECV 2024 y variables de diseño muestral.')

# 18 posición estandarizada
P=pd.read_excel(V3+'PAC_por_posicion_dentro_estrato_C.xlsx',sheet_name='Total_vs_estandarizada',index_col=0)
P=P.loc[['Casa (suelo y cubierta propia)','Primer piso con vivienda encima','Último piso (bajo cubierta)','Piso intermedio']]
fig,ax=plt.subplots(figsize=(9.5,4.6)); y=np.arange(4)
ax.barh(y+.2,P.iloc[:,0],.38,color=PAL[3],label='Tal como sale del catastro'); ax.barh(y-.2,P.iloc[:,1],.38,color=PAL[0],label='A igual mezcla de estratos')
for i,(a,b) in enumerate(P.values): ax.text(a+.8,i+.2,fmt(a)+' %',va='center',fontsize=9); ax.text(b+.8,i-.2,fmt(b)+' %',va='center',fontsize=9)
ax.set_yticks(y); ax.set_yticklabels(P.index); ax.invert_yaxis(); ax.set_xlim(0,75); ax.set_xlabel('P(A/C) media, 2024'); ax.legend(loc='upper center',bbox_to_anchor=(.5,-.2),ncol=2,fontsize=9.5); ax.grid(axis='y',visible=False)
title(ax,'A igual estrato, la posición cambia poco la P(A/C)','El rango baja de 37 a 13 puntos; esos 13 vienen del supuesto de techo')
save(fig,'pac_posicion.png','Fuente: imputación al catastro, variante C.')

# 19 nevera edad
Ne=T['ecv19_nevera_edad_dist']; Ne=Ne[Ne.rango!='no sabe']
fig,ax=plt.subplots(figsize=(9.5,3.8)); seq=['#b8d3f4','#7fb0ec','#4d8fe0','#2a78d6','#1b528f']
ax.bar(range(len(Ne)),Ne.pct,color=seq)
for i,v in enumerate(Ne.pct): ax.text(i,v+.8,fmt(v)+' %',ha='center',fontsize=9.5)
ax.set_xticks(range(len(Ne))); ax.set_xticklabels([r if 'años' in r else r+' años' for r in Ne.rango]); ax.set_ylabel('% de neveras'); ax.set_ylim(0,48)
title(ax,'Edad de las neveras: mediana de 5 años, 18 % con 10 o más','Antigüedad declarada de la nevera del hogar')
save(fig,'neveras_edad.png','Fuente: DANE, ECV 2019 (P5515).')
print('ok')

# 20 diagrama de flujo de datos (horizontal)
from matplotlib.patches import FancyBboxPatch
fig,ax=plt.subplots(figsize=(16,7.6)); ax.set_xlim(0,100); ax.set_ylim(0,100); ax.axis('off')
cols=[(0.5,'Fuentes',PAL[0],[('ECV 2018–2025 (DANE)',0),('ENUT 2024–2025',0),('GEIH 2024',0),('Catastro de Barranquilla',0),('SUI 2015–2026',0),('Clima ERA5-Land / IDEAM',1),('Demanda horaria XM',1)]),
      (21,'Procesamiento',PAL[1],[('Ponderación (FEX) y\nefecto de diseño',0),('Postestratificación\ncon suscriptores SUI',0),('Serie suavizada de\ntenencia (variante C, Beta)',0),('Regresión logística e\nimputación al catastro',0),('Depuración SUI\n(banderas de calidad)',0)]),
      (41.5,'Insumos del modelo',PAL[2],[('Tenencia de A/C,\nventilador y nevera',0),('Horas de uso y tipo de equipo',0),('Presencia en casa\npor tipo de persona',0),('Envolvente: techo y\nposición bajo cubierta',0),('Hogares por estrato\n(expansión)',0),('Consumo mensual y\nestacionalidad observados',0)]),
      (62,'Modelo de la tesis',PAL[6],[('Fase 1: arquetipos\nde vivienda',0),('Fase 2: simulación\nhoraria por equipo',0),('Fase 3: calibración\n(ABC-SMC) y validación',0)]),
      (82.5,'Resultado',PAL[5],[('Perfiles horarios de\nclimatización y\nrefrigeración\npor estrato',0)])]
W_=17; centers={}
for x,head,c,items in cols:
    ax.text(x+W_/2,97,head,ha='center',va='center',fontsize=12.5,fontweight='bold',color=c)
    n=len(items); h=min(10.5,84/n-1.5); gap=(88-n*h)/(n+1); y=92-gap-h
    for k,(lab,pend) in enumerate(items):
        box=FancyBboxPatch((x,y),W_,h,boxstyle='round,pad=0.25,rounding_size=1.2',fc=c if not pend else '#fcfcfb',ec=c,lw=1.6,alpha=.92 if not pend else 1,ls='--' if pend else '-')
        ax.add_patch(box); ax.text(x+W_/2,y+h/2,lab+('\n(pendiente)' if pend else ''),ha='center',va='center',fontsize=8.3,color='white' if not pend else c,fontweight='bold' if not pend else 'normal')
        centers.setdefault(head,[]).append((x,y+h/2)); y-=h+gap
for (x0,_,_,_),(x1,_,_,_) in zip(cols[:-1],cols[1:]):
    ax.annotate('',xy=(x1-0.9,50),xytext=(x0+W_+0.9,50),arrowprops=dict(arrowstyle='-|>',color='#7a7974',lw=2.2,mutation_scale=18))
fig.savefig(S+'flujo_datos.png',dpi=160,bbox_inches='tight'); plt.close(fig)

# 21 coherencia: distribución por estrato entre fuentes
src={'Catastro (viviendas)':[32.8,21.8,21.6,14.8,5.1,4.0],'SUI dic-2019 (suscriptores)':[33.8,19.9,22.8,14.0,5.2,4.2],'SUI dic-2024 (suscriptores)':[33.3,19.3,22.9,15.0,5.4,4.1],
     'ECV 2019 (hogares)':[39.4,20.2,18.1,12.5,4.4,4.7],'ECV 2024 (hogares)':[38.6,22.5,20.6,9.0,6.0,3.4],'GEIH 2024, área metropolitana':[44.0,29.1,14.0,7.7,2.5,2.1]}
cc=[PAL[0],PAL[2],PAL[5],PAL[1],PAL[3],PAL[4]]
fig,ax=plt.subplots(figsize=(10,5)); x=np.arange(6); w=.13
for k,(lab,v) in enumerate(src.items()): ax.bar(x+(k-2.5)*w,v,w,color=cc[k],label=lab)
ax.set_xticks(x); ax.set_xticklabels([f'Estrato {i+1}' for i in range(6)]); ax.set_ylabel('% del total (estratos 1–6)'); ax.legend(fontsize=8.8,ncol=2,loc='upper right')
title(ax,'Catastro y SUI coinciden; las encuestas sobrerrepresentan el estrato 1','Distribución por estrato según la fuente')
save(fig,'coherencia_estratos.png','Fuentes: catastro, SUI, DANE (ECV, GEIH).')

# 22 coherencia: alza estacional vs tenencia de A/C
acC=[7.8,26.7,39.5,72.2,85.2,97.2]; alza=[10.9,16.5,23.5,28.0,29.1,27.6]
fig,ax=plt.subplots(figsize=(8.5,5))
for i in range(6):
    ax.scatter(acC[i],alza[i],s=140,color=PAL[i],zorder=3,edgecolor='white',lw=1.5); ax.annotate(f'E{i+1}',(acC[i],alza[i]),xytext=(8,-4),textcoords='offset points',color=PAL[i],fontweight='bold')
r=np.corrcoef(acC,alza)[0,1]
ax.set_xlabel('Hogares con A/C, 2019 (variante C), %'); ax.set_ylabel('Alza ago–sep frente a feb–mar, %'); ax.set_xlim(0,105); ax.set_ylim(5,35)
title(ax,'Más A/C, mayor alza estacional del consumo (hasta saturar en E4–E6)',f'Encuesta (ECV) frente a facturación (SUI); correlación de Pearson r = {fmt(r,2)}')
save(fig,'coherencia_alza_ac.png','Fuentes: DANE, ECV 2018–2025; SUI 2015–2025.')
print('extra ok')
