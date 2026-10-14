"""Estacionalidad del SUI por estrato con 2015-2025 (meses sin bandera; años con >=10 meses válidos).
Índice del mes = kWh/suscriptor del mes / promedio del año; luego promedio entre años.
Alza = promedio(ago,sep)/promedio(feb,mar) - 1 por año; luego promedio entre años."""
import pandas as pd, numpy as np
s=pd.read_csv('/mnt/user-data/outputs/SUI_Barranquilla_urbano_residencial_2015_2026.csv',sep=';',dtype={'estrato':str})
s=s[(s.anio<=2025)&s.bandera.isna()].copy(); s['k']=s.kWh_suscriptor
ok=s.groupby(['estrato','anio']).k.transform('size')>=10; s=s[ok]
s['idx']=s.k/s.groupby(['estrato','anio']).k.transform('mean')
def per(g):
    a=g[g.mes.isin([8,9])].groupby('anio').k.mean(); b=g[g.mes.isin([2,3])].groupby('anio').k.mean()
    return (a/b-1).dropna()
rows=[]
for e,g in s.groupby('estrato'):
    for lab,yy in [('2015-2018',range(2015,2019)),('2019-2025',range(2019,2026)),('2015-2025',range(2015,2026))]:
        gg=g[g.anio.isin(yy)]; al=per(gg)
        rows.append(dict(estrato=e,periodo=lab,anios=al.size,alza_media=al.mean()*100,alza_min=al.min()*100,alza_max=al.max()*100))
A=pd.DataFrame(rows)
I=s.groupby(['estrato','mes']).idx.mean().unstack(0)
I1=s[s.anio<=2018].groupby(['estrato','mes']).idx.mean().unstack(0); I2=s[s.anio>=2019].groupby(['estrato','mes']).idx.mean().unstack(0)
pd.set_option('display.width',220)
print(A.pivot(index='estrato',columns='periodo',values='alza_media').round(1))
print(I.round(3))
print('dif max indice 2015-18 vs 2019-25:',(I1-I2).abs().max().round(3).to_dict())
with pd.ExcelWriter('/home/claude/v3/SUI_estacionalidad_2015_2025.xlsx') as xw:
    A.round(2).to_excel(xw,sheet_name='Alza_ago_sep_vs_feb_mar',index=False)
    I.round(4).to_excel(xw,sheet_name='Indice_mensual_2015_2025')
    I1.round(4).to_excel(xw,sheet_name='Indice_2015_2018'); I2.round(4).to_excel(xw,sheet_name='Indice_2019_2025')
