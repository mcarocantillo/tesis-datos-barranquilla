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
| 4 | `scripts/04_cdh_sui.py` | Grados-hora por base, temperatura base por punto de quiebre y Ecuación 9 por estrato con el SUI de lecturas reales |
| 5 | `scripts/05_celdas_vecinas.py [carpeta]` | Clima y carga del Paso 3 en las celdas vecinas (relee los NetCDF de GDEX, unos 10 min) |
| 6 | `scripts/06_onda_larga_paso3.py` | Corrección de onda larga del sol-aire de la cubierta con ERA5-Land y su efecto en la carga y el R² del Paso 3 (necesita el catastro, que no se publica) |
| 7 | `scripts/07_dias_representativos.py` | Tres días representativos por mes de cada año (k-medoides) con su peso y validación frente al mes completo |

## Salidas (`salidas/`)

- `clima_horario_barranquilla.parquet` y `.csv.gz`: 102.984 horas, del 1-ene-2015 al 30-sep-2026 (en hora local, de las 20:00 del 31-dic-2014 a las 19:00 del
  30-sep-2026, porque GDEX empieza a la 01 UTC). Ninguna hora falta en la serie, pero la lluvia está vacía en 529 horas
  (93 en mayo de 2019 y 436 entre febrero y junio de 2022): `tp` viene vacío en toda la malla en algunas horas y la
  desacumulación deja vacía también la hora siguiente. Eso subestima la lluvia de 2022. El viento de ERA5-Land de
  GDEX (5,5 m/s de media) es 91 % mayor que el de ERA5 de Open-Meteo (2,9 m/s) y no se ha contrastado con una medición.
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
  95: 3,6 y 11,6 K), frente a los 11 K por defecto de la ISO 13790 para el 5R1C. Esta diferencia no se compara con los
  3,9 K del sol-aire del Paso 3, que son otra magnitud (ε·ΔR/h_o; ver la sección de onda larga).
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
  carga 10,6 %; el de 2015–2016 (muy fuerte, ONI 2,59) solo 0,24 °C y 1,9 % (el 0,5 °C y 3,9 % del grupo «muy fuerte» suma
  ese episodio y el de 2026), y el moderado de 2018–2019 la
  bajó (−1,3 %).
- **Por año ENSO** (julio a junio, `enso_anios.csv`), la carga va de −5,8 % (2021–2022, La Niña) a +8,7 %
  (2023–2024, El Niño) frente a la media. Para el escenario «año de El Niño» de la Fase 3, 2023–2024 es el caso más
  exigente observado; para La Niña, 2021–2022.
- **Para la Fase 3:** el criterio N6 usa los errores de 2023, cuyo segundo semestre es El Niño fuerte. Además, el
  ONI llegó a 2,46 en agosto–octubre de 2026, así que la prueba con datos de 2027 caerá probablemente en un episodio
  de El Niño fuerte o muy fuerte, como ya anticipa la propuesta con el pronóstico del IDEAM.

## Grados-hora y consumo del SUI (`scripts/04_cdh_sui.py`)

Avance de la Ecuación 9 con el consumo por suscriptor con lectura real del SUI (cubo O3, Barranquilla, 2015–2025 sin
2020, unos 118 meses por estrato). El clima de cada mes de facturación se prueba como el del mismo mes, el del mes
anterior o la mitad de cada uno; la mitad de cada uno ajusta mejor, como se espera de lecturas repartidas en el mes.

**Temperatura base (punto de quiebre).** Con ln C = β·CDH + efecto del año, el R² dentro del año cambia poco con la
base: de 0,143 a 0,157 entre 24 y 32 °C (máximo en 30,5 °C). En los estratos 4 a 6, donde el ajuste es bueno (R² de
0,54 a 0,74), el máximo está en 28,5–29 °C, pero el R² varía menos de 0,03 entre 24 y 30 °C. Con datos mensuales la
base queda mal identificada, así que conviene tratarla como parámetro con rango (por ejemplo, 26,5 a 30 °C) y no fijarla
con esta prueba.

**Respuesta mensual al calor (Ecuación 9, con efectos fijos de año y de mes; HAC):**

| Estrato | β (% por °C de HI medio del mes) | IC 95 % |
| --- | --- | --- |
| 1 | −6,0 | −12,6 – 0,6 |
| 2 | 2,3 | 0,1 – 4,5 |
| 3 | 1,4 | −1,4 – 4,2 |
| 4 | 3,3 | 2,5 – 4,1 |
| 5 | 4,2 | 2,9 – 5,5 |
| 6 | 4,7 | 3,5 – 5,9 |

La respuesta crece con el estrato, como la tenencia de A/C (13 % en el estrato 1 y 98 % en el 6), y es clara en los
estratos 4 a 6. En los estratos 1 a 3 los intervalos son anchos: con los efectos fijos de mes, β sale solo de las
anomalías interanuales, y en el estrato 1 la fracción de suscriptores con lectura real cambia mucho entre años. Es lo
que la propuesta anticipa: si el intervalo es muy amplio, extender la estimación a otros municipios del Caribe.

## Sensibilidad a la celda (`scripts/05_celdas_vecinas.py`)

Repite el clima y la carga del Paso 3 de la vivienda media en las seis celdas de tierra de la ventana de 3 × 3
alrededor de la celda de referencia, en 2015–2025 (la fila de 11,1° N es mar).

| Celda | T (°C) | HI (°C) | Grados-hora (26,5 °C) | Carga del Paso 3 |
| --- | --- | --- | --- | --- |
| 11,0 N; 74,9 O | −0,12 | −0,26 | −5,6 % | −1,4 % |
| **11,0 N; 74,8 O (referencia)** | 27,46 | 30,92 | 38.839 K·h/año | 37.702 kWh/año |
| 11,0 N; 74,7 O | +0,25 | +0,50 | +10,7 % | +1,7 % |
| 10,9 N; 74,9 O | −0,27 | −0,77 | −16,1 % | −2,7 % |
| 10,9 N; 74,8 O | 0,00 | −0,09 | −1,6 % | +0,9 % |
| 10,9 N; 74,7 O | +0,32 | +0,66 | +14,4 % | +3,4 % |

Las celdas del este, hacia el río Magdalena y Soledad, son más calurosas que las del oeste. Entre celdas, el índice de
calor medio cambia hasta 1,4 °C y los grados-hora hasta 30 puntos porcentuales, pero la carga del Paso 3 solo entre
−2,7 % y +3,4 %, porque la cubierta (la mitad de la carga) depende sobre todo de la radiación, que casi no cambia. Es una
cota de la elección de celda, no de la isla de calor: ERA5-Land no representa la ciudad como superficie urbana.

## Onda larga del sol-aire de la cubierta (`scripts/06_onda_larga_paso3.py`)

El Paso 3 de la Fase 1 resta 3,9 K al sol-aire de la cubierta: la corrección de ASHRAE ε·ΔR/h_o para superficies
horizontales, con ΔR ≈ 63–66 W/m² en un cielo templado. Con la onda larga de ERA5-Land, ΔR = σ·T_aire⁴ − L vale en
Barranquilla 43 W/m² en promedio (46 de día y 40 de noche), porque el cielo húmedo del trópico emite más. Con ε = 0,9
y h_o = 17 W/m²K la corrección es de 2,3 K (2,0 a 2,4 K con ε entre 0,8 y 0,95), no 3,9 K.

| Variante | Corrección media (K) | Carga de la cubierta | Carga total | R² por vivienda | R² por m² |
| --- | --- | --- | --- | --- | --- |
| Constante, 3,9 K (Paso 3) | 3,90 | 18.033 kWh/año | 37.932 kWh/año | 0,661 | 0,927 |
| Horaria, ε = 0,8 | 2,03 | +8,8 % | +4,2 % | 0,667 | 0,931 |
| Horaria, ε = 0,9 | 2,28 | +7,3 % | +3,5 % | 0,666 | 0,930 |
| Horaria, ε = 0,95 | 2,41 | +6,6 % | +3,1 % | 0,665 | 0,930 |

Los 3,9 K sobrestiman el enfriamiento de la cubierta hacia el cielo en Barranquilla: con la corrección horaria, la
carga de la cubierta sube 7 % y la total 3,5 %. Como en AJ24, el R² de los arquetipos casi no cambia (sube 0,005), así
que la corrección mueve el nivel de la carga, no los arquetipos. Para la Fase 2, el 5R1C debe usar la onda larga
horaria y no la constante.

## Días representativos (`scripts/07_dias_representativos.py`)

La propuesta (sección 7.6) prevé simular con 36 días representativos por año (tres por mes) cuando el cómputo lo
exija. Como la validación usa la respuesta mensual al calor, que sale de las anomalías interanuales, los días se eligen
dentro de cada mes de cada año: k-medoides exacto con k = 3 (todas las ternas de días del mes) sobre la temperatura
media y máxima, el índice de calor máximo, la irradiancia diaria y la humedad específica media, estandarizados. Cada
día pesa el número de días de su grupo. Resultado: 423 días para los 141 meses de 2015 a septiembre de 2026
(`dias_representativos.csv`).

| Medida reconstruida por mes | Error medio | Error máximo | Tres días al azar (mediana) |
| --- | --- | --- | --- |
| Temperatura media | 0,06 °C | 0,26 °C | 0,22 °C |
| Índice de calor medio | 0,15 °C | 0,53 °C | 0,52 °C |
| Irradiancia media | 3,2 W/m² | 14 W/m² | 11,6 W/m² |
| Grados-hora (26,5 °C) | 3,7 % | 16 % | 12 % |
| Carga del Paso 3 | 1,2 % | 5,0 % | 4,7 % |

- **Por año**, la carga reconstruida queda entre −0,1 % y +1,4 % de la del año completo (sesgo medio +0,7 %).
- **Las anomalías mensuales**, que identifican la Ecuación 9, se conservan: correlación de 0,98 con las del mes
  completo, tanto en el índice de calor como en la carga.
- **Para la Fase 2:** los días se eligen solo por el clima. El tipo de día (laboral, sábado, domingo o festivo) cambia
  la ocupación, así que cada día representativo deberá simularse con los tipos de día de su mes en proporción. Además,
  el 5R1C tiene inercia térmica: cada día necesita un precalentamiento (por ejemplo, repetirlo dos o tres veces o
  simular los días anteriores) antes de registrar su resultado.

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
- Días representativos: ya elegidos (script 07). Falta decidir, con el costo real de la simulación, si se usan, y
  fijar el precalentamiento del 5R1C.
- Usar en el 5R1C la onda larga horaria en lugar de la corrección constante de 3,9 K (script 06).
