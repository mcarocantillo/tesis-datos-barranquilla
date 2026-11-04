# Fase 2, Paso 1: clima y calendario

Serie horaria de clima de Barranquilla para el modelo de simulación (5R1C) y archivo EPW para la verificación del
módulo térmico contra EnergyPlus (hito del mes 7, enero de 2027).

## Orden de ejecución

Con el entorno de la compuerta horaria (`compuerta_horaria/.venv`, que tiene pvlib 0.16.1, holidays y pyarrow), desde
esta carpeta:

| Paso | Script | Qué hace |
| --- | --- | --- |
| 0 | `compuerta_horaria/scripts/01b_extraer_era5land_gdex.py` | Extrae la celda de Barranquilla de los pedidos de GDEX 953933 y 953943 |
| 1 | `scripts/01_serie_clima.py` | Serie horaria con humedad, radiación en muros y cubierta, cielo, viento y calendario |
| 2 | `scripts/02_epw.py [AÑO]` | EPW de un año (por defecto, 2024) y lectura de control con pvlib |
| 3 | `scripts/03_enso.py` | Fase ENSO de cada mes (ONI de la NOAA) y anomalías de clima y carga por fase; usa las tablas del script 11 de arquetipos |

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

## El Niño y La Niña (`scripts/03_enso.py`)

Clasifica cada mes con el índice ONI de la NOAA (`datos/noaa/oni.ascii.txt`, descargado el 3-nov-2026 del Climate
Prediction Center) y la regla de la NOAA: episodio cuando el ONI es ≥ +0,5 (≤ −0,5) en al menos cinco trimestres
móviles seguidos. De enero de 2015 a septiembre de 2026 hay 49 meses de El Niño (cinco episodios), 30 de La Niña (tres)
y 62 neutros. Se compara la anomalía de cada mes frente a la media de su mes calendario en 2015–2025.

| Fase | Meses | Temperatura (°C) | Índice de calor (°C) | Lluvia | Grados-hora (base 26,5 °C) | Carga del Paso 3 |
| --- | --- | --- | --- | --- | --- | --- |
| El Niño | 49 | +0,23 | +0,56 | −29 % | +13 % | +4,4 % (± 0,9) |
| La Niña | 30 | −0,25 | −0,68 | +20 % | −17 % | −4,5 % (± 0,9) |
| Neutro | 62 | 0,00 | +0,03 | +8 % | +1 % | −0,4 % (± 0,7) |

- **Por unidad de ONI**, el índice de calor sube 0,62 °C y la carga 4,4 %, con una tendencia aparte de +1,0 °C y
  +4,7 % por década (`enso_regresion.json`). La década empezó con La Niña (2020–2023) y terminó con El Niño, así que
  sin la tendencia el ONI absorbería parte del calentamiento. Con 141 meses y ocho episodios, las dos cosas no se
  separan bien; los errores estándar suponen meses independientes y son optimistas.
- **No todos los episodios pesan igual.** El de 2023–2024 (fuerte, ONI 1,99) subió el índice de calor 1,7 °C y la
  carga 10,6 %; el de 2015–2016 (muy fuerte, ONI 2,59) solo 0,5 °C y 3,9 % en promedio, y el moderado de 2018–2019 la
  bajó (−1,3 %).
- **Por año ENSO** (julio a junio, `enso_anios.csv`), la carga va de −5,8 % (2021–2022, La Niña) a +8,7 %
  (2023–2024, El Niño) frente a la media. Para el escenario «año de El Niño» de la Fase 3, 2023–2024 es el caso más
  exigente observado; para La Niña, 2021–2022.
- **Para la Fase 3:** el criterio N6 usa los errores de 2023, cuyo segundo semestre es El Niño fuerte. Además, el
  ONI llegó a 2,46 en agosto–octubre de 2026, así que la prueba con datos de 2027 caerá probablemente en un episodio
  de El Niño fuerte o muy fuerte, como ya anticipa la propuesta con el pronóstico del IDEAM.

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
