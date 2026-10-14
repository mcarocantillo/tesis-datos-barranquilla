import csv, statistics as st
from collections import defaultdict
L=list(csv.DictReader(open('/mnt/user-data/outputs/SUI_Barranquilla_urbano_residencial_2019_2026.csv',encoding='utf-8-sig'),delimiter=';'))
for o in L:
    for k in ('anio','mes','suscriptores','consumo_kWh','valor_COP'): o[k]=int(o[k])
    o['kWh_suscriptor']=float(o['kWh_suscriptor']) if o['kWh_suscriptor'] else None
    o['COP_kWh']=float(o['COP_kWh']) if o['COP_kWh'] else None
bad={(o['anio'],o['mes']) for o in L if o['estrato']=='total' and 'consumo' in o['bandera']}
badval={(o['anio'],o['mes']) for o in L if o['estrato']=='total' and o['bandera']}|{(o['anio'],o['mes']) for o in L if o['bandera']}
print('bad consumo months',sorted(bad))
E=['1','2','3','4','5','6','total']
# seasonal index per estrato: within each clean full-ish year, month value / year mean; average across years 2019,2020,2021,2023(no),2025
idx=defaultdict(list)
for y in range(2019,2026):
    for e in E:
        ser={o['mes']:o['kWh_suscriptor'] for o in L if o['anio']==y and o['estrato']==e and (y,o['mes']) not in bad and 'consumo' not in o['bandera']}
        if len(ser)<11: continue
        mu=st.mean(ser.values())
        for m,v in ser.items(): idx[(e,m)].append(v/mu)
print('Indice estacional (mes/mean anual) promedio años con >=11 meses:')
for e in E:
    print(e,[round(st.mean(idx[(e,m)]),3) if idx[(e,m)] else None for m in range(1,13)])
yrs=defaultdict(int)
for y in range(2019,2026):
    n=len([1 for o in L if o['anio']==y and o['estrato']=='total' and (y,o['mes']) not in bad])
    print(y,'meses validos',n)
# tariff COP/kWh by estrato per year (clean)
print('COP/kWh')
for y in range(2019,2027):
    row=[]
    for e in E:
        v=[o['COP_kWh'] for o in L if o['anio']==y and o['estrato']==e and not o['bandera'] and o['COP_kWh']]
        row.append(round(st.mean(v)) if v else None)
    print(y,row)
# annual residential GWh (clean months scaled to 12)
nr=list(csv.DictReader(open('/home/claude/work/sui/sui_noresidencial_raw.csv'),delimiter=';'))
for y in range(2019,2027):
    res=[o['consumo_kWh'] for o in L if o['anio']==y and o['estrato']=='total' and (y,o['mes']) not in bad]
    com=[float(r['kWh_com']) for r in nr if int(r['anio'])==y]
    print(y,'res GWh/mes medio',round(st.mean(res)/1e6,1),'n',len(res),'com GWh/mes mediana',round(st.median(com)/1e6,1))
# subscriber growth
def S(y,m,e): return next(o['suscriptores'] for o in L if o['anio']==y and o['mes']==m and o['estrato']==e)
for e in E: print('susc',e,S(2019,12,e),S(2025,12,e),round((S(2025,12,e)/S(2019,12,e)-1)*100,1))
# Aug-Sep vs Feb-Mar ratio by estrato per year
print('ratio pico/valle')
for e in E:
    r=[]
    for y in range(2019,2027):
        g=lambda ms:[o['kWh_suscriptor'] for o in L if o['anio']==y and o['estrato']==e and o['mes'] in ms and (y,o['mes']) not in bad and 'consumo' not in o['bandera']]
        a,b=g((8,9)),g((2,3))
        r.append(round(st.mean(a)/st.mean(b),2) if a and b else None)
    print(e,r)
# commercial seasonality 2021-2025 robust
