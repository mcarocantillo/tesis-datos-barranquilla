# Recalcula todas las tablas del informe que usan ECV 2024, con la base corregida (709 hogares)
import pandas as pd, numpy as np
B='/home/claude/work/Traspaso_tesis_Barranquilla/datos_procesados/'
n=lambda s: pd.to_numeric(s.astype(str).str.strip().str.replace(',','.'),errors='coerce')
def wpct(d,m): return d.W[m].sum()/d.W.sum()*100
def wmean(d,c):
    x=d[c]; m=x.notna(); return (x[m]*d.W[m]).sum()/d.W[m].sum()
def wq(x,w,q):
    x=np.asarray(x);w=np.asarray(w);i=np.argsort(x);x,w=x[i],w[i];c=np.cumsum(w)/w.sum();return x[np.searchsorted(c,q)]
b0=pd.read_csv(B+'ECV2024_Barranquilla_hogares.csv',sep=';',dtype=str,encoding='utf-8-sig')
b0['W']=n(b0.FEX_C); b0['E']=n(b0.ESTRATO)
print('hogares',len(b0),'viviendas',b0.DIRECTORIO.nunique(),'suma W',round(b0.W.sum()))
print('clase',b0.CLASE.value_counts().to_dict(),'estrato0',(~b0.E.between(1,6)).sum())
for c in ['TIENE_AC','TIENE_VENT','TIENE_NEVERA','TIENE_LAVADORA','TIENE_TV_LED','TIENE_CALENTADOR','CANT_PERSONAS_HOGAR','PERCAPITA','CUARTOS','DORMITORIOS','SANITARIOS','N_65','N_MEN5']: b0[c]=n(b0[c])
yes=lambda d,c: d[c].str.strip()=='1'
# Totales ciudad (todo el municipio)
a=b0
print('ciudad: apto',round(wpct(a,a.TIPO_VIVIENDA.str.strip()=='2'),1),'casa',round(wpct(a,a.TIPO_VIVIENDA.str.strip()=='1'),1),
 'TIPO vals',a.TIPO_VIVIENDA.value_counts().to_dict())
ten=a.TENENCIA.str.strip()
print('tenencia propia',round(wpct(a,ten.isin(['1','2'])),1),'arriendo',round(wpct(a,ten=='3'),1),'otra',round(wpct(a,~ten.isin(['1','2','3'])),1))
print('personas',round(wmean(a,'CANT_PERSONAS_HOGAR'),2),'nevera',round(wpct(a,a.TIENE_NEVERA==1),1),'lav',round(wpct(a,a.TIENE_LAVADORA==1),1),'tvled',round(wpct(a,a.TIENE_TV_LED==1),1),'cal',round(wpct(a,a.TIENE_CALENTADOR==1),1),'vent',round(wpct(a,a.TIENE_VENT==1),1),'ac',round(wpct(a,a.TIENE_AC==1),1))
b=b0[b0.E.between(1,6)].copy()
print('dist estrato %',(b.groupby('E').W.sum()/b.W.sum()*100).round(1).to_dict())
b['PAGO_MES']=n(b.PAGO_ELEC)/n(b.MESES_PAGO).replace(0,np.nan)
b['G']=b.E.map({1:'1-2',2:'1-2',3:'3-4',4:'3-4',5:'5-6',6:'5-6'})
rows=[]
for e,d in b.groupby('E'):
    p=d[d.PAGO_MES.between(1000,5e6)]
    rows.append(dict(E=int(e),n=len(d),ac=wpct(d,d.TIENE_AC==1),vent=wpct(d,d.TIENE_VENT==1),nev=wpct(d,d.TIENE_NEVERA==1),lav=wpct(d,d.TIENE_LAVADORA==1),tvled=wpct(d,d.TIENE_TV_LED==1),tvconv=wpct(d,yes(d,'P1077S7')),pc=wpct(d,yes(d,'P1077S21')),port=wpct(d,yes(d,'P1077S22')),cal=wpct(d,d.TIENE_CALENTADOR==1),pago=wq(p.PAGO_MES,p.W,.5),pers=wmean(d,'CANT_PERSONAS_HOGAR'),san=wmean(d,'SANITARIOS')))
print(pd.DataFrame(rows).round(1).to_string())
pay=b[b.PAGO_MES.between(1000,5e6)]
print(pay.groupby(['G','TIENE_AC']).apply(lambda d: pd.Series(dict(n=len(d),med=wq(d.PAGO_MES,d.W,.5)))).to_string())
b['TEN']=b.TENENCIA.str.strip().map(lambda x:'Propia' if x in('1','2') else('Arriendo' if x=='3' else 'Otra'))
print(b.groupby(['G','TEN']).apply(lambda d: pd.Series(dict(n=len(d),ac=round(wpct(d,d.TIENE_AC==1),1)))).to_string())
b['TIPO']=b.TIPO_VIVIENDA.str.strip().map({'1':'Casa','2':'Apto'}).fillna('Otro')
print(b.groupby(['G','TIPO']).apply(lambda d: pd.Series(dict(n=len(d),ac=round(wpct(d,d.TIENE_AC==1),1)))).to_string())
q=[wq(b.PERCAPITA.fillna(0),b.W,p) for p in (.2,.4,.6,.8)]
b['Q']=np.digitize(b.PERCAPITA.fillna(0),q)+1
print(pd.DataFrame([dict(Q=k,n=len(d),ac=round(wpct(d,d.TIENE_AC==1),1),ing=round(float(wq(d.PERCAPITA.fillna(0),d.W,.5)),-3)) for k,d in b.groupby('Q')]).to_string())
mt={'1':'Concreto','2':'Barro','3':'Asbesto','4':'Zinc','5':'Plastica'}
print(b.groupby('G').apply(lambda d: pd.Series({v:round(wpct(d,d.P4567.str.strip()==k),1) for k,v in mt.items()})).to_string())
