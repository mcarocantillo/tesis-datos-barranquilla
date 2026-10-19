"""Consumo residencial por estrato 2021-2024: SUI del repositorio frente a la Tabla 42 de CEELA (2025c).
CEELA: promedio mensual 2021-2024 con el filtro «tipo de lectura: real» del SUI (Características comunes, 3.5.1).
Repositorio: media de kWh/suscriptor de los meses 2021-2024 sin bandera y con consumo > 0.
Correr desde la raíz del repositorio: python scripts/ceela_sui.py"""
import pandas as pd

# Tabla 42 del informe de caracterización energética de CEELA, enero a diciembre (kWh/mes)
CEELA = {
    '1': [212, 216, 197, 242, 210, 265, 236, 231, 226, 226, 272, 214],
    '2': [205, 190, 194, 209, 212, 218, 221, 234, 231, 228, 217, 216],
    '3': [232, 214, 221, 241, 248, 260, 265, 279, 283, 280, 254, 269],
    '4': [311, 279, 286, 300, 327, 347, 353, 373, 387, 364, 342, 339],
    '5': [372, 347, 351, 364, 402, 431, 436, 444, 474, 447, 419, 407],
    '6': [679, 600, 614, 630, 682, 749, 753, 744, 798, 768, 715, 744],
}
s = pd.read_csv('tablas/SUI_Barranquilla_urbano_residencial_2015_2026.csv', sep=';', dtype={'estrato': str})
s = s[s.anio.between(2021, 2024) & s.bandera.isna() & (s.consumo_kWh > 0) & (s.estrato != 'total')]
rows = []
for e, g in s.groupby('estrato'):
    c = sum(CEELA[e]) / 12
    anual = g.groupby('anio').kWh_suscriptor.mean()
    r = g.kWh_suscriptor.mean()
    rows.append(dict(estrato=e, segmento_CEELA='VIS' if e in '12' else 'NO VIS',
                     kWh_mes_CEELA=round(c, 1), kWh_mes_repositorio=round(r, 1), meses_validos=len(g),
                     media_anual_min=round(anual.min(), 1), media_anual_max=round(anual.max(), 1),
                     diferencia_pct=round((r / c - 1) * 100, 1)))
t = pd.DataFrame(rows)
print(t.to_string(index=False))
t.to_csv('tablas/CEELA_SUI_2021_2024_comparacion.csv', sep=';', index=False, encoding='utf-8-sig')
