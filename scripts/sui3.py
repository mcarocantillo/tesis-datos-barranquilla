"""SUI ele_com_096, Barranquilla urbano, residencial 2015-2026 (une 2015-2018 nuevo con 2019-2026)."""
import csv, json, statistics as st
from collections import defaultdict
rows = list(csv.DictReader(open('/home/claude/work/sui/sui_agg_raw.csv'), delimiter=';'))
E = ['e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'res']
raw = {}
for r in rows:
    raw[(int(r['anio']), int(r['mes']))] = {e: (float(r['S_' + e]), float(r['kWh_' + e]), float(r['COP_' + e])) for e in E}
new = json.load(open('/home/claude/work/extra/sui_1518.json'))
for y in range(2015, 2019):
    for m in range(1, 13):
        a, b, c = new[f'{y}-{m}-1'], new[f'{y}-{m}-2'], new[f'{y}-{m}-3']
        raw[(y, m)] = {e: (a[i], b[i], c[i]) for i, e in enumerate(E)}
out = []
for (y, m), d in sorted(raw.items()):
    for e in E:
        S, k, c = d[e]
        out.append(dict(anio=y, mes=m, estrato=e.replace('e', '') if e != 'res' else 'total', suscriptores=int(S), consumo_kWh=round(k), valor_COP=round(c),
                        kWh_suscriptor=round(k / S, 1) if S else '', COP_kWh=round(c / k, 1) if k else ''))
med = defaultdict(list); cmed = defaultdict(list)
for o in out:
    if o['kWh_suscriptor'] != '': med[o['estrato']].append(o['kWh_suscriptor'])
    if o['COP_kWh'] != '' and o['COP_kWh'] > 0: cmed[o['estrato']].append(o['COP_kWh'])
med = {k: st.median(v) for k, v in med.items()}; cmed = {k: st.median(v) for k, v in cmed.items()}
for o in out:
    f = []; k = o['kWh_suscriptor']
    if k == '' or k < 0.5 * med[o['estrato']] or k > 1.5 * med[o['estrato']]: f.append('consumo_atipico')
    if o['valor_COP'] < 0: f.append('valor_negativo')
    elif o['COP_kWh'] != '' and (o['COP_kWh'] > 3 * cmed[o['estrato']] or o['COP_kWh'] < 0.3 * cmed[o['estrato']]): f.append('valor_atipico')
    o['bandera'] = '|'.join(f)
w = csv.DictWriter(open('/mnt/user-data/outputs/SUI_Barranquilla_urbano_residencial_2015_2026.csv', 'w', newline='', encoding='utf-8-sig'), fieldnames=list(out[0]), delimiter=';')
w.writeheader(); w.writerows(out)
print('meses con bandera (total):', sorted({(o['anio'], o['mes'], o['bandera']) for o in out if o['bandera'] and o['estrato'] == 'total'}))
print('medianas', {k: round(v) for k, v in med.items()})
for y in range(2015, 2027):
    line = []
    for e in ['1', '2', '3', '4', '5', '6', 'total']:
        v = [o['kWh_suscriptor'] for o in out if o['anio'] == y and o['estrato'] == e and not o['bandera']]
        line.append(round(st.mean(v)) if v else None)
    n = len([o for o in out if o['anio'] == y and o['estrato'] == 'total' and not o['bandera']])
    S = [o['suscriptores'] for o in out if o['anio'] == y and o['estrato'] == 'total' and o['mes'] == 12]
    print(y, n, line, S)
for y in range(2015, 2019):
    print(y, [(o['mes'], o['kWh_suscriptor'], o['bandera']) for o in out if o['anio'] == y and o['estrato'] == 'total'])
