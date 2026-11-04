"""Fase 2, Paso 1: archivo EPW de un año para la verificación del módulo térmico contra EnergyPlus.

Toma la serie de 01_serie_clima.py. El EPW usa la hora estándar local que termina en la hora indicada (1 a 24), la
misma convención de la serie. La onda larga de ERA5-Land va en el campo de radiación infrarroja horizontal, que
EnergyPlus usa directamente para el intercambio con el cielo cuando trae un valor válido. Los campos que ERA5-Land no
da (iluminancias, nubosidad, visibilidad, techo de nubes) quedan con el código de dato faltante del formato.

Uso:  python scripts/02_epw.py [AÑO]   (por defecto, 2024)
Salida: salidas/BAQ_ERA5Land_GDEX_{AÑO}.epw, y una lectura de control con pvlib.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pvlib

RAIZ = Path(__file__).resolve().parents[1]
SALIDAS = RAIZ / "salidas"
LAT, LON, ALTURA, ZONA = 11.0, -74.8, 50.0, -5.0
FUENTE = "?9?9?9?9E0?9?9?9?9?9?9?9?9?9?9?9?9?9*9*9?9?9?9"


def encabezado(anio, bisiesto, primer_dia):
    return [
        f"LOCATION,Barranquilla ERA5-Land,ATL,COL,ERA5-Land GDEX (NCAR),000000,{LAT:.2f},{LON:.2f},{ZONA:.1f},"
        f"{ALTURA:.1f}",
        "DESIGN CONDITIONS,0",
        "TYPICAL/EXTREME PERIODS,0",
        "GROUND TEMPERATURES,0",
        f"HOLIDAYS/DAYLIGHT SAVINGS,{'Yes' if bisiesto else 'No'},0,0,0",
        f"COMMENTS 1,Año real {anio} de ERA5-Land (ECMWF) descargado de GDEX (NCAR); celda 11.0N 74.8W; "
        "radiación separada con Erbs (pvlib)",
        "COMMENTS 2,Infrarrojo horizontal = onda larga descendente de ERA5-Land; sin iluminancias ni nubosidad",
        f"DATA PERIODS,1,1,Data,{primer_dia},1/1,12/31",
    ]


def main():
    anio = int(sys.argv[1]) if len(sys.argv) > 1 else 2024
    s = pd.read_parquet(SALIDAS / "clima_horario_barranquilla.parquet")
    # La hora que termina a las 00:00 del 1 de enero del año siguiente es la hora 24 del 31 de diciembre
    inicio, fin = pd.Timestamp(anio, 1, 1, 1), pd.Timestamp(anio + 1, 1, 1, 0)
    a = s.loc[inicio:fin]
    esperadas = len(pd.date_range(inicio, fin, freq="h"))
    if len(a) != esperadas:
        raise ValueError(f"{anio}: {len(a)} horas de {esperadas}; el año no está completo en la serie")
    etiqueta = a.index - pd.Timedelta(hours=1)  # inicio de la hora: da el día y la hora 0–23
    bisiesto = pd.Timestamp(anio, 12, 31).dayofyear == 366
    dias = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    filas = []
    for t, r in zip(etiqueta, a.itertuples()):
        filas.append(",".join(str(x) for x in [
            t.year, t.month, t.day, t.hour + 1, 60, FUENTE,
            f"{r.T:.1f}", f"{r.Td:.1f}", int(round(r.HR)), int(round(r.p_kPa * 1000)),
            int(round(r.ETR_horizontal)), int(round(r.ETR_normal)) if r.ETR_horizontal > 0 else 0,
            int(round(r.L_onda_larga)),
            int(round(r.GHI)), int(round(r.DNI)), int(round(r.DHI)),
            999999, 999999, 999999, 9999,
            int(round(r.dir_viento)) % 360, f"{r.viento:.1f}",
            99, 99, 9999, 99999, 9, 999999999, 999, 0.999, 999, 99, 999,
            f"{r.lluvia_mm:.1f}", 1,
        ]))
    salida = SALIDAS / f"BAQ_ERA5Land_GDEX_{anio}.epw"
    texto = "\n".join(encabezado(anio, bisiesto, dias[pd.Timestamp(anio, 1, 1).dayofweek]) + filas) + "\n"
    salida.write_text(texto, encoding="latin-1", newline="\r\n")

    # Control: se lee con pvlib y se compara con la serie
    leido, meta = pvlib.iotools.read_epw(salida)
    control = {
        "horas": len(leido), "lat": meta["latitude"], "lon": meta["longitude"], "TZ": meta["TZ"],
        "T_media_epw": round(float(leido["temp_air"].mean()), 3), "T_media_serie": round(float(a["T"].mean()), 3),
        "GHI_media_epw": round(float(leido["ghi"].mean()), 2), "GHI_media_serie": round(float(a["GHI"].mean()), 2),
        "IR_media_epw": round(float(leido["ghi_infrared"].mean()), 2),
        "primera_hora": str(leido.index[0]), "ultima_hora": str(leido.index[-1]),
    }
    print(salida.name, control)
    assert control["horas"] == esperadas
    assert np.isclose(control["T_media_epw"], control["T_media_serie"], atol=0.05)


if __name__ == "__main__":
    main()
