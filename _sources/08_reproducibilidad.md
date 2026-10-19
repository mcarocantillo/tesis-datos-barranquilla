# Reproducibilidad

Los cálculos se hicieron en Python (pandas, numpy, scipy, statsmodels) a partir de los microdatos públicos. Las rutas de los scripts apuntan al entorno de trabajo original y deben ajustarse.

## Tablas resumen (carpeta `tablas/` del repositorio)

- `b_h_niveles_reparto.csv`
- `b_h_por_hora.csv`
- `Calculos_nuevos_metodologia.xlsx`
- `Catastro_E1_edificios_4pisos_por_lote.csv`
- `Catastro_ECV_E1_edificios_resumen.csv`
- `Catastro_PAC_por_anio_estrato_tipo_C.csv`
- `CEELA_SUI_2021_2024_comparacion.csv`
- `contraste_era5land_ideam.csv`
- `decision.json`
- `ECV2024_efecto_diseno.csv`
- `ECV_2018_2025_AC_postestratificado_SUI.csv`
- `ECV_2018_2025_Barranquilla_tenencia_por_estrato.csv`
- `ENUT2024_25_Atlantico_horas_por_tipo.csv`
- `estabilidad.csv`
- `franjas.csv`
- `GEIH2024_Barranquilla_AM_resumen_estrato.csv`
- `Logit_ECV2024_modelos.csv`
- `PAC_por_posicion_dentro_estrato_C.xlsx`
- `Postestratificacion_AC_2018_2025.xlsx`
- `SUI_Barranquilla_urbano_NO_residencial_2019_2026.csv`
- `SUI_Barranquilla_urbano_residencial_2015_2026.csv`
- `SUI_estacionalidad_2015_2025.xlsx`
- `Serie_suavizada_AC_2015_2027.xlsx`
- `Tenencia_AC_ajustes_AB.csv`
- `Tenencia_AC_ciudad_sensibilidad_AB.csv`
- `Tenencia_AC_sensibilidad_AB.csv`

Separador «;», codificación UTF-8 con BOM. No se publican las bases por hogar (ECV, ENUT, GEIH) ni el catastro por vivienda. Las tablas de la compuerta horaria (`b_h_*.csv`, `franjas.csv`, `estabilidad.csv`, `contraste_era5land_ideam.csv` y `decision.json`) son las salidas de `scripts/compuerta/03_estimar.py` y `01_clima.py`; los scripts las escriben con separador «,» y aquí se publicaron con «;».

## Scripts (carpeta `scripts/`)

- `build_ecv2019.py`
- `catastro_cubierta.py`
- `catastro_e1_edificios.py`
- `ceela_sui.py`
- `deep.py`
- `deff_ecv24.py`
- `ecv19_extra.py`
- `ecv24.py`
- `ecv24_tablas.py`
- `enut.py`
- `enut_out.py`
- `enut_stats.py`
- `estacionalidad_sui.py`
- `figuras.py`
- `geih.py`
- `geih2.py`
- `imputacion_catastro_anual.py`
- `imputacion_catastro_anual_C.py`
- `logit_ecv24.py`
- `pac_posicion_estrato.py`
- `pac_posicion_estrato_C.py`
- `postestrat_anual.py`
- `postestrat_xlsx.py`
- `sensibilidad_serie.py`
- `serie_suavizada.py`
- `stats.py`
- `suavizada_xlsx.py`
- `sui.py`
- `sui2.py`
- `sui3.py`
- `xlsx.py`

`ceela_sui.py` se corre desde la raíz del repositorio y compara el SUI con la Tabla 42 de CEELA.

Orden: `build_ecv2019.py` y `ecv24.py` → `ecv24_tablas.py`, `enut*.py`, `geih*.py`, `sui*.py` → `postestrat_anual.py` → `logit_ecv24.py` → `serie_suavizada.py` → `deff_ecv24.py` → `sensibilidad_serie.py` → `imputacion_catastro_anual_C.py` → `pac_posicion_estrato_C.py`, `estacionalidad_sui.py`, `catastro_e1_edificios.py` → `figuras.py`.

## Compuerta horaria (carpeta `scripts/compuerta/`)

| Paso | Script | Qué hace |
| --- | --- | --- |
| 1 | `01_clima.py descargar procesar` | Descarga ERA5-Land (copia de Open-Meteo) e IDEAM 0029045190; humedad relativa, índice de calor y contraste por hora y mes |
| 1b | `01a_descargar_era5land_cds.py` | Descarga ERA5-Land del Climate Data Store con la cuenta personal del CDS (`~/.cdsapirc`, `pip install cdsapi`); después se repite `01_clima.py procesar` |
| 2 | `02_descargar_xm.py` | API pública de XM: mercados CARIBE SOL y COSTA CARIBE, agentes de Air-e y Electricaribe, demanda no atendida por subárea |
| 3 | `03_estimar.py` | $b_h$, franjas, estabilidad entre años, decisión de la compuerta y figura |

`comun.py` reúne las rutas y funciones compartidas. Los scripts se corren desde `scripts/compuerta/` y guardan las descargas en `scripts/compuerta/datos/` (unos 150 MB) y las salidas en `scripts/compuerta/salidas/`; ninguna de las dos carpetas se versiona.

## Entorno

Python 3.13 con las versiones fijadas en `requirements.txt` (pandas 3.0, numpy 2.5, scipy 1.18, statsmodels 0.15 y matplotlib 3.11). La compuerta horaria usa además requests, holidays, xarray y netCDF4, y se corrió con Python 3.14.

## Construir el sitio

```bash
pip install -r requirements.txt
jupyter-book build .
ghp-import -n -p -f _build/html
```

Las figuras se generan con `figuras.py` y las citas se resuelven desde `referencias.bib` con sphinxcontrib-bibtex.

## Licencia y cita

El código se distribuye con licencia MIT y los textos, figuras y tablas resumen con licencia CC BY 4.0. Los metadatos de cita están en `CITATION.cff`.
