"""P(AC) 2024 imputada por posición frente a la cubierta, total y DENTRO de cada estrato, y estandarizada por estrato.
Muestra cuánto de la diferencia entre posiciones es efecto del estrato y cuánto del supuesto de techo."""
import pandas as pd, numpy as np
cat=pd.read_csv('/mnt/user-data/outputs/Catastro_posicion_cubierta.csv',sep=';',usecols=['estrato_num','uso','POSICION'])
cat=cat[cat.POSICION!='Sin dato de piso']
cat['tipo']=np.where(cat.uso.str.contains('Apartamentos'),'pAC_edificio4','pAC_hasta3'); cat['estrato']='E'+cat.estrato_num.astype(str)
p=pd.read_csv('/home/claude/v3/Catastro_PAC_por_anio_estrato_tipo_C.csv',sep=';')
p=p[p.anio==2024].melt(id_vars=['estrato'],value_vars=['pAC_edificio4','pAC_hasta3'],var_name='tipo',value_name='pac')
cat=cat.merge(p,on=['estrato','tipo'])
tot=cat.groupby('POSICION').pac.mean()*100
dentro=cat.pivot_table(index='estrato',columns='POSICION',values='pac',aggfunc='mean')*100
mix=cat.groupby('estrato').size()/len(cat)
std=(dentro.mul(mix,axis=0)).sum()  # estandarizado a la mezcla de estratos de la ciudad
share=pd.crosstab(cat.POSICION,cat.estrato,normalize='index')*100
pd.set_option('display.width',220)
out=pd.DataFrame({'PAC_observada_total':tot,'PAC_estandarizada_por_estrato':std})
print(out.round(1)); print(dentro.round(1)); print(share.round(1))
with pd.ExcelWriter('/home/claude/v3/PAC_por_posicion_dentro_estrato_C.xlsx') as xw:
    out.round(2).to_excel(xw,sheet_name='Total_vs_estandarizada')
    dentro.round(2).to_excel(xw,sheet_name='Dentro_de_estrato')
    share.round(2).to_excel(xw,sheet_name='Estrato_de_cada_posicion')
