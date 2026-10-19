"""Descarga ERA5-Land horario en el punto de Barranquilla desde el Climate Data Store (Copernicus).

LO CORRE LA USUARIA con su propia cuenta: requiere el archivo ~/.cdsapirc con su clave personal
(https://cds.climate.copernicus.eu/how-to-api) y haber aceptado la licencia de ERA5-Land en la web del CDS.
Este script no pide ni guarda credenciales.

Usa el conjunto 'reanalysis-era5-land-timeseries' (serie en un punto, descarga rápida). El archivo queda en
datos/crudos/era5land_cds/ y luego 01_clima.py lo usa en lugar de la copia provisional de Open-Meteo.

Uso:  pip install cdsapi   y luego   python 01a_descargar_era5land_cds.py
"""
import cdsapi
import pandas as pd

from comun import CRUDOS, INICIO, LAT, LON

DESTINO = CRUDOS / "era5land_cds"
DESTINO.mkdir(parents=True, exist_ok=True)
# ERA5-Land se publica con unos 5 días de rezago
FIN = (pd.Timestamp.utcnow().normalize() - pd.Timedelta(days=7)).strftime("%Y-%m-%d")

pedido = {
    "variable": [
        "2m_temperature",
        "2m_dewpoint_temperature",
        "10m_u_component_of_wind",
        "10m_v_component_of_wind",
        "surface_solar_radiation_downwards",
    ],
    "location": {"longitude": LON, "latitude": LAT},
    "date": [f"{INICIO}/{FIN}"],
    "data_format": "netcdf",
}

if __name__ == "__main__":
    salida = DESTINO / f"era5land_barranquilla_{INICIO}_{FIN}.zip"
    cdsapi.Client().retrieve("reanalysis-era5-land-timeseries", pedido).download(str(salida))
    print(f"Guardado en {salida}. Ahora corra: python 01_clima.py procesar")
