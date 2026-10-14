import csv, collections, math
rows=list(csv.DictReader(open('/mnt/user-data/outputs/ECV2019_Barranquilla_consolidado.csv',encoding='utf-8-sig'),delimiter=';'))
def n(x):
    try: return float(x.replace(',','.'))
    except: return None
for r in rows: r['w']=n(r['FEX_C'])
W=sum(r['w'] for r in rows)
def dist(var,rs=None,label=None):
    rs=rs or rows; T=sum(r['w'] for r in rs); c=collections.Counter(); u=collections.Counter()
    for r in rs: c[r[var]]+=r['w']; u[r[var]]+=1
    print(var,{k:(u[k],round(v/T*100,1)) for k,v in sorted(c.items())})
print('N',len(rows),'W',round(W), 'neff',round(W**2/sum(r['w']**2 for r in rows)))
for v in ['ESTRATO','TENENCIA_P5095','TIPO_VIVIENDA_P1070','TIPO_AC_P5523','SEXO_JEFE_P6020','PAGO_ELEC_P5018'][:5]: dist(v)
# AC by estrato
print('--AC por estrato (1-6)')
for e in '123456':
    rs=[r for r in rows if r['ESTRATO']==e]; T=sum(r['w'] for r in rs)
    ac=[r for r in rs if r['TIPO_AC_P5523']!='']; Ta=sum(r['w'] for r in ac)
    h=[(n(r['HORAS_AC_P5524']),r['w']) for r in ac if n(r['HORAS_AC_P5524']) is not None]
    hm=sum(a*b for a,b in h)/sum(b for a,b in h) if h else 0
    fan=[r for r in rs if r['HORAS_VENTILADOR_P5526'] not in ('','0')]; Tf=sum(r['w'] for r in fan)
    fh=[(n(r['HORAS_VENTILADOR_P5526']),r['w']) for r in fan if n(r['HORAS_VENTILADOR_P5526']) is not None]
    fm=sum(a*b for a,b in fh)/sum(b for a,b in fh) if fh else 0
    p=Ta/T; se=math.sqrt(p*(1-p)/len(rs))
    print(e,'n',len(rs),'hog',round(T),'AC%',round(p*100,1),'±',round(1.96*se*100,1),'hAC',round(hm,1),'fan%',round(Tf/T*100,1),'hFan',round(fm,1))
# overall AC
ac=[r for r in rows if r['TIPO_AC_P5523']!='']; p=sum(r['w'] for r in ac)/W
print('AC global',round(p*100,1),'n',len(ac))
# persons, income, cuartos
def wmean(var,rs=rows):
    x=[(n(r[var]),r['w']) for r in rs if n(r[var]) is not None]; return sum(a*b for a,b in x)/sum(b for a,b in x)
for v in ['PERSONAS_HOGAR','CUARTOS_P5000','CUARTOS_DORMIR_P5010','INGRESO_HOGAR','INGRESO_PERCAPITA','EDAD_MEDIA','N_MENORES_5','N_65_MAS','EDAD_JEFE']: print(v,round(wmean(v),2))
for e in '123456':
    rs=[r for r in rows if r['ESTRATO']==e]
    print(e,'pers',round(wmean('PERSONAS_HOGAR',rs),2),'ingr',round(wmean('INGRESO_HOGAR',rs)),'rooms',round(wmean('CUARTOS_P5000',rs),2),'65+',round(wmean('N_65_MAS',rs),2))
# hours distribution AC
hs=sorted(n(r['HORAS_AC_P5524']) for r in ac if n(r['HORAS_AC_P5524']) is not None)
print('AC hours q',[hs[int(len(hs)*q)] for q in (.1,.25,.5,.75,.9)],'max',hs[-1],'n',len(hs))
fh=sorted(n(r['HORAS_VENTILADOR_P5526']) for r in rows if n(r['HORAS_VENTILADOR_P5526']) not in (None,0))
print('fan hours q',[fh[int(len(fh)*q)] for q in (.1,.25,.5,.75,.9)],'max',fh[-1],'n',len(fh))
# tenencia by estrato groups
for e in '123456':
    rs=[r for r in rows if r['ESTRATO']==e]; T=sum(r['w'] for r in rs)
    c=collections.Counter()
    for r in rs: c[r['TENENCIA_P5095']]+=r['w']
    print(e,{k:round(v/T*100) for k,v in sorted(c.items())})
# activity
lab=collections.Counter()
