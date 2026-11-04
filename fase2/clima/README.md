# Fase 2, Paso 1: clima y calendario

Serie horaria de clima de Barranquilla para el modelo de simulación (5R1C) y archivo EPW para la verificación del
módulo térmico contra EnergyPlus (hito del mes 7, enero de 2027).

## Orden de ejecución

Con un entorno que tenga pvlib 0.16.1, holidays y pyarrow (en la carpeta de trabajo, `compuerta_horaria/.venv`), desde
esta carpeta:

| Paso | Script | Qué hace |
| --- | --- | --- |
| 0 | `compuerta_horaria/scripts/01b_extraer_era5land_gdex.py` | Extrae la celda de Barranquilla de los pedidos de GDEX 953933 y 953943 (en el repositorio, `scripts/compuerta/01b_extraer_era5land_gdex.py`) |
| 1 | `scripts/01_serie_clima.py` | Serie horaria con humedad, radiación en muros y cubierta, cielo, viento y calendario |
| 2 | `scripts/02_epw.py [AÑO]` | EPW de un año (por defecto, 2024) y lectura de control con pvlib |

## Salidas (`salidas/`)

- `clima_horario_barranquilla.parquet` y `.csv.gz`: 102.984 horas, del 1-ene-2015 al 30-sep-2026, sin horas faltantes.
  Cada fila es la hora que termina en `hora_local` (UTC−5).
- `comprobaciones_clima.json`: huecos, cierre de la radiación, cielo despejado, simetría del mediodía y cielo.
- `BAQ_ERA5Land_GDEX_2024.epw`: 8.784 horas de 2024 (año bisiesto).

| Columna | Unidad | Origen |
| --- | --- | --- |
| `T`, `Td` | °C | ERA5-Land; `Td` rellenado en 608 h (`td_relleno`) con Open-Meteo + 0,175 K |
| `HR`, `w_kgkg`, `HI` | %, kg/kg, °C | Magnus; humedad específica con la presión horaria; índice de calor de la NOAA |
| `p_kPa` | kPa | ERA5-Land; 8 h interpoladas (`p_interpolada`) |
| `GHI`, `DNI`, `DHI` | W/m² | Onda corta de ERA5-Land desacumulada; separación de Erbs |
| `I_cubierta`, `I_muro_N/E/S/O` | W/m² | Cielo isótropo, albedo 0,2 |
| `ETR_horizontal`, `ETR_normal`, `cenit_sol`, `azimut_sol` | W/m², ° | pvlib (NREL SPA) a mitad de la hora |
| `L_onda_larga`, `T_cielo`, `dT_cielo` | W/m², °C, K | Onda larga descendente de ERA5-Land; T_cielo = (L/σ)^¼ |
| `viento`, `dir_viento` | m/s, ° | Viento a 10 m de ERA5-Land; dirección de donde viene |
| `lluvia_mm` | mm | Precipitación de ERA5-Land desacumulada |
| `tipo_dia`, `festivo`, `carnaval`, `semana_santa`, `fin_anio` | | Calendario de la compuerta horaria |
| `vacaciones_escolares` | | Aproximación del calendario A (supuesto, abajo) |
| `anio_pandemia` | | 2020, que la calibración excluye |

## Comprobaciones

- **Cierre:** DNI·cos(cenit) + DHI = GHI con error máximo de 10⁻¹³ W/m² con el sol alto.
- **Cielo despejado** (Ineichen): solo 0,2 % de las horas supera 1,1 veces el cielo despejado cuando este pasa de
  300 W/m² (percentil 99 de la razón: 1,07). Con el sol bajo, el cielo despejado calculado a mitad de la hora
  subestima la hora completa, por eso no se compara ahí.
- **Hora:** la irradiancia media de las horas que terminan a las 12 y a las 13 es casi igual (835 y 831 W/m²), igual
  que la de las 7 y las 18 (66 y 65 W/m²). Es lo esperado con el mediodía solar cerca de las 12:00 local, así que la
  desacumulación y el paso a hora local están bien alineados.
- **Muros:** irradiancia media de 85 W/m² al norte y de 116 a 123 W/m² al sur, este y oeste. La difusa es 40 % de la
  global diurna.
- **Cielo:** el aire está en promedio 7,3 K por encima de la temperatura del cielo (6,8 K de noche; percentiles 5 y
  95: 3,6 y 11,6 K). El Paso 3 de la Fase 1 usó 3,9 K y la ISO 13790 propone 11 K por defecto.
- **EPW:** al leerlo con pvlib, la temperatura media (27,90 °C) y la irradiancia media (235,5 W/m²) coinciden con las
  de la serie.

## Supuestos

- **Vacaciones escolares aproximadas.** Las 12 semanas de receso del calendario A de Colombia se ubican así: del 1 de
  diciembre al 25 de enero, la Semana Santa, tres semanas desde el lunes siguiente al 15 de junio y la semana del
  festivo de octubre (82 días por año). No vienen de las resoluciones de calendario académico de Barranquilla de cada
  año. Los años de pandemia (2020 y parte de 2021) no siguieron este calendario.
- **Altura de 50 m** en el EPW, la del modelo de terreno que reporta Open-Meteo para el punto; EnergyPlus la usa poco
  porque el archivo trae la presión horaria.
- **Una sola celda** para toda la ciudad (la propuesta lo prueba en la sensibilidad por la isla de calor).
- El EPW no trae nubosidad, iluminancias ni visibilidad; EnergyPlus usa el infrarrojo horizontal para el cielo.

## Pendiente

- Contrastar la radiación con una medición en Barranquilla.
- Pedir a GDEX los meses desde octubre de 2026 a medida que se publiquen.
- Días representativos (tres por mes) cuando se conozca el costo de cómputo de la simulación.
