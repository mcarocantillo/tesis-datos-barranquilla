import csv, statistics as st
rows=list(csv.DictReader(open('/home/claude/work/sui/sui_agg_raw.csv'),delimiter=';'))
E=['e1','e2','e3','e4','e5','e6','res']
out=[]
for r in rows:
    y,m=int(r['anio']),int(r['mes'])
    for e in E:
        S=float(r['S_'+e]); k=float(r['kWh_'+e]); c=float(r['COP_'+e])
        kps=k/S if S else None
        out.append(dict(anio=y,mes=m,estrato=e.replace('e','') if e!='res' else 'total',suscriptores=int(S),consumo_kWh=round(k),valor_COP=round(c),kWh_suscriptor=round(kps,1) if kps else '',COP_kWh=round(c/k,1) if k else ''))
# flags: compare kWh/suscriptor to median for estrato
from collections import defaultdict
med=defaultdict(list)
for o in out:
    if o['kWh_suscriptor']!='': med[o['estrato']].append(o['kWh_suscriptor'])
med={k:st.median(v) for k,v in med.items()}
cmed=defaultdict(list)
for o in out:
    if o['COP_kWh'] not in ('',) and o['COP_kWh']>0: cmed[o['estrato']].append(o['COP_kWh'])
for o in out:
    f=[]
    k=o['kWh_suscriptor']
    if k=='' or k<0.5*med[o['estrato']] or k>1.5*med[o['estrato']]: f.append('consumo_atipico')
    if o['valor_COP']<0: f.append('valor_negativo')
    elif o['COP_kWh']!='' and (o['COP_kWh']>3*st.median(cmed[o['estrato']]) or o['COP_kWh']<0.3*st.median(cmed[o['estrato']])): f.append('valor_atipico')
    o['bandera']='|'.join(f)
# subscriber spike
for o in out:
    pass
f=open('/mnt/user-data/outputs/SUI_Barranquilla_urbano_residencial_2019_2026.csv','w',newline='',encoding='utf-8-sig')
w=csv.DictWriter(f,fieldnames=list(out[0].keys()),delimiter=';'); w.writeheader(); w.writerows(out); f.close()
bad=sorted({(o['anio'],o['mes'],o['bandera']) for o in out if o['bandera'] and o['estrato']=='total'})
print('meses con bandera (total):',bad)
print('medianas kWh/susc:',{k:round(v) for k,v in med.items()})
# annual summary using clean months
ok=lambda o:o['bandera']=='' 
for y in range(2019,2027):
    line=[]
    for e in ['1','2','3','4','5','6','total']:
        v=[o['kWh_suscriptor'] for o in out if o['anio']==y and o['estrato']==e and ok(o)]
        line.append(round(st.mean(v)) if v else None)
    n=len([o for o in out if o['anio']==y and o['estrato']=='total' and ok(o)])
    print(y,n,line)
# subscriber shares Dec 2019, and latest
for y,m in [(2019,12),(2023,12),(2025,12)]:
    d={o['estrato']:o['suscriptores'] for o in out if o['anio']==y and o['mes']==m}
    T=sum(d[e] for e in '123456')
    print(y,m,T,{e:round(d[e]/T*100,1) for e in '123456'})
# seasonality 2019 clean, total kWh/susc by month
for y in (2019,2023,2025):
    print(y,[ (o['mes'],o['kWh_suscriptor']) for o in out if o['anio']==y and o['estrato']=='total'])
