"""Convierte la salida del cubo O3 del SUI (SUI_COMERCIAL_ENERGIA/VISTA_FACTURACION_ENERGIA) en un CSV.

Consulta hecha el 27-oct-2026 en bi.superservicios.gov.co (sesión anónima):
  filas = TIEMPO (mes, ene-2015 a dic-2025) x UBICACION_GEOGRAFICA (BARRANQUILLA) x ESTRATO (seis residenciales)
          x TIPO DE LECTURA_MEDICIÓN (n/a, Estimada, Real, No tiene medidor)
  filtros = UBICACION: Urbano; USO: Residencial; EMPRESA y TIPO DE USUARIO: todos (agregados)
  medidas = Número de suscriptores, Consumo total (kWh), Facturación por consumo ($), Facturación total ($)

Uso: python -I o3_a_csv.py <view_grid.html> <rows.js> <salida.csv>
"""
import ast
import csv
import re
import sys

MESES = {m: i + 1 for i, m in enumerate("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split())}
ESTRATOS = {"Residencial Bajo-Bajo": 1, "Residencial Bajo": 2, "Residencial Medio-Bajo": 3,
            "Residencial Medio": 4, "Residencial Medio-Alto": 5, "Residencial Alto": 6}


def extraer(texto, inicio):
    """Devuelve la lista JS que empieza en `inicio` (balanceando corchetes) como objeto Python."""
    i = texto.index("[", inicio)
    prof, j = 0, i
    en_cad = False
    while True:
        c = texto[j]
        if en_cad:
            if c == "\\":
                j += 1
            elif c == "'":
                en_cad = False
        elif c == "'":
            en_cad = True
        elif c == "[":
            prof += 1
        elif c == "]":
            prof -= 1
            if prof == 0:
                break
        j += 1
    return ast.literal_eval(texto[i:j + 1].replace("\\/", "/"))


def numero(s):
    s = re.sub(r"[^0-9\-]", "", s)
    return int(s) if s not in ("", "-") else None


def main(html, js, salida):
    t1 = open(html, encoding="utf-8").read()
    t2 = open(js, encoding="utf-8").read()
    # la primera página viene en el HTML de la vista; el resto llega en varios bloques «var rows = [...]»
    filas = extraer(t1, t1.index("rows = ["))
    for m in re.finditer(r"var rows = \[", t2):
        filas += extraer(t2, m.start())
    ctx = [None, None, None, None]
    out = []
    for items, valores, _ in filas:
        es_total = any(it[4] == 1 or it[3] in ("Suma", "Total") for it in items)
        k = len(items)
        for n, it in enumerate(items):
            ctx[4 - k + n] = it[3]
        if es_total:
            continue
        mes, muni, estr, lect = ctx
        nm, an = mes.split(" / ")
        out.append(dict(anio=int(an), mes=MESES[nm], municipio=muni, estrato=ESTRATOS[estr], lectura=lect,
                        suscriptores=numero(valores[0]), consumo_kWh=numero(valores[1]),
                        fact_consumo_COP=numero(valores[2]), fact_total_COP=numero(valores[3])))
    with open(salida, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]), delimiter=";")
        w.writeheader()
        w.writerows(out)
    print(len(filas), "filas leídas;", len(out), "filas de datos escritas en", salida)


if __name__ == "__main__":
    main(*sys.argv[1:4])
