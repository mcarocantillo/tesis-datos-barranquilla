# Reproducibilidad

Los cálculos se hicieron en Python (pandas, numpy, scipy, statsmodels) a partir de los microdatos públicos. Las rutas de los scripts apuntan al entorno de trabajo original y deben ajustarse.

## Tablas resumen (carpeta `tablas/` del repositorio)

- `Calculos_nuevos_metodologia.xlsx`
- `Catastro_PAC_por_anio_estrato_tipo_C.csv`
- `ECV2024_efecto_diseno.csv`
- `ECV_2018_2025_AC_postestratificado_SUI.csv`
- `ECV_2018_2025_Barranquilla_tenencia_por_estrato.csv`
- `ENUT2024_25_Atlantico_horas_por_tipo.csv`
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

Separador «;», codificación UTF-8 con BOM. No se publican las bases por hogar (ECV, ENUT, GEIH) ni el catastro por vivienda.

## Scripts (carpeta `scripts/`)

- `build_ecv2019.py`
- `catastro_cubierta.py`
- `deep.py`
- `deff_ecv24.py`
- `ecv19_extra.py`
- `ecv24.py`
- `ecv24_tablas.py`
- `enut.py`
- `enut_out.py`
- `enut_stats.py`
- `estacionalidad_sui.py`
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

Orden: `build_ecv2019.py` y `ecv24.py` → `ecv24_tablas.py`, `enut*.py`, `geih*.py`, `sui*.py` → `postestrat_anual.py` → `logit_ecv24.py` → `serie_suavizada.py` → `deff_ecv24.py` → `sensibilidad_serie.py` → `imputacion_catastro_anual_C.py` → `pac_posicion_estrato_C.py`, `estacionalidad_sui.py`.

## Construir el sitio

```bash
pip install "jupyter-book>=1,<2" ghp-import
jupyter-book build .
ghp-import -n -p -f _build/html
```
