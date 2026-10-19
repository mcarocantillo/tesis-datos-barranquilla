# Insumos del modelo

Este capítulo resume los insumos que el procesamiento entrega al modelo. Para cada parámetro se indica el valor o la distribución adoptada, su incertidumbre, la fuente y el paso de la propuesta donde se usa. La {numref}`tab-insumos-resumen` es el índice. Las tablas siguientes dan el detalle por estrato. E1 a E6 son los estratos socioeconómicos; los porcentajes se refieren a hogares, salvo que se indique otra unidad.

Las proporciones (tenencia de equipos, material del techo) entran al modelo como distribuciones Beta {cite:p}`gelman2013`. Sus parámetros se obtienen por el método de momentos a partir de la media $\bar p$ y la desviación estándar $s$ de cada estimación:

$$
\alpha = \bar p\,\kappa, \qquad \beta = (1-\bar p)\,\kappa, \qquad \kappa = \frac{\bar p\,(1-\bar p)}{s^{2}} - 1
$$ (eq-beta-momentos)

Si una proporción observada es de 100 % (por ejemplo, la tenencia de nevera en los estratos 4 a 6), el método de momentos no aplica. En ese caso se propone una Beta$(n + 0{,}5;\ 0{,}5)$, que equivale al prior de Jeffreys actualizado con los $n$ hogares de la muestra {cite:p}`gelman2013`.

## Índice de insumos

```{table} Insumos del modelo, fuente y paso de la propuesta en que se usan.
:name: tab-insumos-resumen

| Insumo | Valor o distribución | Incertidumbre | Fuente | Fase y paso |
| --- | --- | --- | --- | --- |
| Tenencia de A/C por estrato y año | Beta por estrato y año, 2015–2027 ({numref}`tab-ac-beta`) | DE de 1,5 a 6,6 puntos por estrato en 2024; ciudad ± 2,9 puntos (IC 95 %) | ECV 2018–2025 sin 2020; SUI | Fase 2, paso 2 |
| Efecto del techo sobre la tenencia de A/C | Razón de momios frente a concreto: 0,35 asbesto-cemento, 0,14 zinc ({numref}`tab-techo`) | IC 95 % de cada razón | ECV 2024 | Fase 1, paso 6; Fase 2, paso 2 |
| Material del techo por estrato | Proporciones por grupo de estrato ({numref}`tab-techo`) | Tamaño de muestra de cada celda | ECV 2024 | Fase 1, paso 6 |
| Posición frente a la cubierta | Casa, último piso, intermedio, primer piso por estrato ({numref}`tab-posicion`) | Censal (catastro) | Catastro | Fase 1, paso 2; Fase 2, paso 4 |
| Tenencia de ventilador y nevera | Beta por estrato ({numref}`tab-vent-nevera`) | IC 95 % con efecto de diseño | ECV 2024 | Fase 2, pasos 2, 6 y 7 |
| Tipo de A/C | 82–97 % minisplit; central 0–18 % ({numref}`tab-uso-ac`) | Muestras de 33 a 66 hogares con A/C | ECV 2019 | Fase 2, paso 2 |
| Horas diarias de A/C del hogar | Mediana 6–8 h por estrato ({numref}`tab-uso-ac`) | P25–P75 | ECV 2019 | Fase 2, paso 5; Fase 3, paso 5 |
| Número de equipos de A/C | Prior ligado a la fracción de hogares con más de 12 h de uso ({numref}`tab-uso-ac`) y a la zona climatizada de CEELA | Rango del prior por estrato | ECV 2019; CEELA | Fase 2, paso 2 |
| Relación ventilador–A/C ($p_c$) | ≈ 0,95 ({numref}`tab-pc`) | Rango 0,8–1,0 | ECV 2019 | Fase 2, paso 6 |
| Tamaño y antigüedad de la nevera | Distribución por estrato ({numref}`tab-nevera`) | Muestra por estrato | ECV 2019 | Fase 2, paso 7 |
| Personas y cuartos por hogar | Media por estrato ({numref}`tab-hogar`) | Muestra por estrato | ECV 2024 | Fase 1, paso 7 |
| Composición y presencia en la vivienda | Tipo de persona, sueño y presencia diurna por grupo de estrato ({numref}`tab-presencia`) | Muestra por grupo | ENUT 2024–2025 | Fase 2, paso 3 |
| Trabajo en la propia vivienda | 15,6 % (E1) a 28,5 % (E6) de los ocupados ({numref}`tab-hogar`) | Muestra por estrato | GEIH 2024 | Fase 2, paso 3 |
| Hogares por estrato | Suscriptores residenciales de diciembre ({numref}`tab-calibracion`) | Diferencia con el catastro menor de 2,5 puntos | SUI; catastro | Fase 2, paso 9; Fase 3, paso 1 |
| Consumo facturado por suscriptor | kWh/mes por estrato, 2015–2019 ({numref}`tab-calibracion`) | Rango interanual | SUI | Fase 3, paso 4 |
| Alza estacional del consumo | 10,9 % (E1) a 29,1 % (E5) ({numref}`tab-calibracion`) | Variación entre años | SUI 2015–2025 | Fase 3, pasos 2 y 5 |
| Clima horario | Temperatura, humedad e índice de calor en hora local, 2015–2026 | Sesgo frente al IDEAM: −0,7 °C en temperatura (≈ 0 de noche, −2,2 °C a mediodía) ({numref}`tab-coherencia-clima`) | ERA5-Land (copia de Open-Meteo, provisional); IDEAM | Fase 2, paso 1 |
| Fracción climatizada | Una habitación en E1–E2 (VIS) y en casas de E3–E4; las habitaciones en apartamentos de E3–E4; toda la vivienda en E5–E6 ({numref}`tab-ceela-insumos`) | Sin medición en hogares | CEELA | Fase 1, paso 6; Fase 2, paso 2 |
| Envolvente de los arquetipos | Relación ventana-muro, U de vidrio, muros y cubierta, SRI y sombreamiento por tipología ({numref}`tab-ceela-insumos`) | Centro de los rangos (S15); un edificio por tipología | CEELA | Fase 1, paso 6; Fase 2, paso 4 |
| Consigna de refrigeración | Rango de 22 a 26,5 °C ({numref}`tab-ceela-insumos`) | 26,5 °C de CEELA; 22 °C supuesto propio (S14) | CEELA | Fase 2, paso 5 |
| Rendimiento del A/C | COP de 3,0 | Valor central | CEELA | Fase 2, paso 5 |
| Respuesta horaria de la demanda al calor | Noche 1,92 %/°C (1,79–2,05); la noche aporta 31–34 % de la respuesta diaria; noche/tarde 0,77–0,98 ({numref}`tab-compuerta-franjas`) | Forma hora a hora inestable entre años: capa C (S16) | XM; ERA5-Land | Fase 3, pasos 1 y 4 (blanco de validación) |
```

## Tenencia de aire acondicionado

La tenencia de A/C proviene de la serie suavizada por estrato y año descrita en el capítulo [Serie de tenencia, error de la encuesta e imputación](05_ajustes_v3.md). Los años con encuesta (2018, 2019 y 2021–2025) se estiman con las olas de la ECV. Los años 2015–2017 y 2026–2027 se extrapolan, y por eso su incertidumbre es mayor.

```{table} Tenencia de A/C por estrato, variante C: media y desviación estándar (puntos porcentuales).
:name: tab-ac-media

| Año | E1 | E2 | E3 | E4 | E5 | E6 | Ciudad |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2015 | 5,0 (1,9) | 25,3 (4,7) | 32,7 (4,6) | 68,1 (13,0) | 83,1 (9,8) | 95,5 (5,1) | 31,3 (2,4) |
| 2019 | 7,8 (1,5) | 26,7 (2,7) | 39,5 (2,5) | 72,2 (6,0) | 85,2 (4,5) | 97,2 (1,4) | 35,6 (1,3) |
| 2024 | 13,2 (2,0) | 28,6 (2,7) | 48,5 (2,6) | 76,4 (6,6) | 87,4 (3,7) | 98,1 (1,5) | 41,2 (1,5) |
| 2025 | 14,7 (2,7) | 29,0 (3,3) | 50,3 (3,2) | 77,2 (7,5) | 87,7 (4,2) | 98,2 (1,6) | 43,1 (1,8) |
| 2027 | 17,9 (4,5) | 29,8 (4,7) | 54,0 (4,5) | 78,5 (9,2) | 88,4 (5,2) | 98,3 (1,6) | 45,4 (2,5) |
```

:::{table} Parámetros de la distribución Beta(α, β) de la tenencia de A/C, variante C, según la ecuación {eq}`eq-beta-momentos`.
:name: tab-ac-beta

| Año | E1 | E2 | E3 | E4 | E5 | E6 |
| --- | --- | --- | --- | --- | --- | --- |
| 2019 | (24,8; 293,6) | (73,2; 201,3) | (147,2; 225,8) | (39,2; 15,1) | (53,3; 9,2) | (144,3; 4,2) |
| 2024 | (37,3; 244,3) | (80,1; 200,4) | (178,8; 190,0) | (30,7; 9,5) | (68,0; 9,8) | (79,2; 1,6) |
:::

Los parámetros de todos los años están en `tablas/Tenencia_AC_sensibilidad_AB.csv` (filas con variante C). La proporción de la ciudad es la suma de las tasas por estrato ponderadas con los suscriptores del SUI de diciembre de cada año.

## Envolvente y posición de la vivienda

```{table} Material del techo por grupo de estrato (ECV 2024) y efecto sobre la tenencia de A/C.
:name: tab-techo

| Concepto | E1–2 | E3–4 | E5–6 |
| --- | --- | --- | --- |
| Concreto (plancha), % de hogares | 28,6 | 58,2 | 88,9 |
| Asbesto-cemento, % | 60,4 | 39,8 | 11,1 |
| Zinc o lámina metálica, % | 11,0 | 0,0 | 0,0 |
| Razón de momios del A/C, asbesto-cemento frente a concreto (M2) | 0,35 (0,23–0,53) | | |
| Razón de momios del A/C, zinc frente a concreto (M2) | 0,14 (0,05–0,44) | | |
```

Las razones de momios provienen del modelo M2 (techo y estrato), que es el que se usa en la imputación al catastro. Al añadir el ingreso per cápita y el tipo de vivienda (modelo M3), los valores casi no cambian: 0,37 (0,24–0,57) y 0,15 (0,04–0,54). La regresión es logística ponderada con errores robustos HC1 {cite:p}`hosmer2013,mackinnon1985`, con 633 hogares. En el estrato 1, la muestra de la ECV casi no capta los edificios de 4 o más pisos, por lo que las proporciones de techo del grupo E1–2 describen sobre todo casas ({numref}`tab-e1-edificios`).

```{table} Viviendas del catastro por estrato y posición frente a la cubierta (% de las viviendas de cada estrato).
:name: tab-posicion

| Concepto | E1 | E2 | E3 | E4 | E5 | E6 |
| --- | --- | --- | --- | --- | --- | --- |
| Viviendas | 108.985 | 72.493 | 72.000 | 49.190 | 16.843 | 13.207 |
| Casa (suelo y cubierta propios) | 62,1 | 84,0 | 52,7 | 21,3 | 17,5 | 10,2 |
| Apartamento en el último piso | 6,6 | 6,5 | 10,5 | 13,0 | 14,0 | 10,3 |
| Apartamento intermedio | 19,7 | 4,8 | 27,3 | 55,7 | 57,8 | 71,9 |
| Primer piso con vivienda encima | 11,6 | 4,7 | 9,3 | 9,8 | 10,5 | 7,4 |
| Bajo cubierta (casa + último piso) | 68,7 | 90,5 | 63,2 | 34,3 | 31,5 | 20,5 |
| En edificios de 4 pisos o más | 29,5 | 7,3 | 33,9 | 69,4 | 73,8 | 84,2 |
```

Según la propuesta (Fase 2, paso 4), el techo es superficie exterior solo en las viviendas bajo cubierta. En los estratos 4 a 6 eso ocurre en una de cada tres viviendas o menos, de modo que el material del techo pesa sobre todo en los estratos 1 a 3.

## Envolvente, climatización y consigna (CEELA)

```{table} Insumos de la línea base de CEELA para los arquetipos de Barranquilla.
:name: tab-ceela-insumos

| Insumo | E1–E2 (VIS) | E3–E4 | E5–E6 | Fuente en CEELA |
| --- | --- | --- | --- | --- |
| Relación ventana-muro | 20–40 % | 20–40 % (casas); menos de 20 % (apartamentos) | 20–40 % | Características comunes, Tabla 9 |
| Vidrio | Simple de 4–6 mm, U = 5,88 W/m²K | Igual | Igual | Características comunes, 2.3 |
| Sombreamiento | Ninguno en casas; balcones en apartamentos | Balcones | Balcones | Características comunes, Tabla 9 |
| U del muro (W/m²K) | 2,3 (casas); 3,6–4,1 (apartamentos) | 2,7 (casas); 1,9–4,1 (apartamentos) | Igual que E3–E4 | Caracterización, Tablas 33–37 |
| Cubierta: U (W/m²K) y SRI | Fibrocemento 6,6 y 0,4 (casas); losa 3,6 y 0,15 (apartamentos) | Sándwich 4,4 y 0,4 (casas); losa 3,6 y 0,15 (apartamentos) | Igual que E3–E4 | Caracterización, Tablas 38–40 |
| Zona climatizada | Una habitación (habitación principal en apartamentos) | Una habitación (casas); las habitaciones (apartamentos) | Toda la vivienda | Características comunes, Tabla 37 |
| Consigna de refrigeración | 22–26,5 °C | 22–26,5 °C | 22–26,5 °C | Informe, Tabla 2 (26,5 °C operativa); 22 °C supuesto propio |
| COP de refrigeración | 3,0 | 3,0 | 3,0 | Informe, texto que sigue a la Tabla 2 |
```

La {numref}`tab-ceela-insumos` traduce las tipologías de CEELA a estratos con la correspondencia VIS = E1–E2 y no VIS = E3–E6 (supuesto S15), y separa casas y apartamentos con la posición frente a la cubierta del catastro ({numref}`tab-posicion`). En CEELA la vivienda unifamiliar no VIS es de estratos 5 y 6 en la tabla de ventanas y de estratos 3 a 6 en la de climatización; aquí se usa para las casas de E3 a E6. Los valores son el centro de los rangos de cada arquetipo; el detalle por tipología y las limitaciones están en [Línea base de CEELA](16_ceela.md).

## Equipos y uso

```{table} Tenencia de ventilador y nevera por estrato, ECV 2024 (% de hogares; entre paréntesis, semiancho del IC 95 % con efecto de diseño).
:name: tab-vent-nevera

| Equipo | E1 | E2 | E3 | E4 | E5 | E6 | Ciudad |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Ventilador | 99,7 (0,5) | 97,7 (2,0) | 96,8 (3,2) | 100 | 96,5 (6,1) | 100 | 98,6 (0,9) |
| Nevera | 87,5 (4,8) | 90,2 (4,6) | 95,9 (3,9) | 100 | 100 | 100 | 93,0 (2,2) |
| Hogares en la muestra | 250 | 161 | 125 | 52 | 38 | 20 | 646 |
```

```{table} Uso del A/C según la ECV 2019, hogares con A/C.
:name: tab-uso-ac

| Concepto | E1 | E2 | E3 | E4 | E5 | E6 |
| --- | --- | --- | --- | --- | --- | --- |
| Hogares con A/C en la muestra | 33 | 34 | 59 | 66 | 40 | 57 |
| Horas diarias, mediana (P25–P75) | 8 (6–12) | 8 (5–8) | 6 (4–10) | 7 (3–9) | 8 (8–10) | 8 (6–10) |
| Más de 12 h al día, % | 2,7 | 0,0 | 2,3 | 1,2 | 8,1 | 8,6 |
| Minisplit, % | 96,6 | 92,6 | 95,8 | 92,9 | 94,1 | 82,3 |
| Central, % | 0,0 | 0,0 | 2,2 | 2,3 | 5,9 | 17,7 |
```

La ECV 2019 no pregunta el número de equipos de A/C. Las horas declaradas son la suma de los equipos del hogar, así que más de 12 h al día indica, con probabilidad alta, más de un equipo. Esa fracción es de 0 % a 2,7 % en los estratos 1 a 4 y de 8 % a 9 % en los estratos 5 y 6. El prior del número de equipos se construirá con esa fracción y con la zona climatizada de CEELA (Fase 1, paso 6; {numref}`tab-ceela-insumos`).

```{table} Horas diarias de ventilador en hogares con y sin A/C (ECV 2019) y valor implícito de $p_c$.
:name: tab-pc

| Concepto | E1 | E2 | E3 | E4 |
| --- | --- | --- | --- | --- |
| Horas de ventilador, hogares sin A/C | 11,5 | 11,9 | 9,7 | 9,1 |
| Horas de ventilador, hogares con A/C | 11,2 | 10,7 | 9,3 | 9,7 |
| Horas de A/C, media | 7,9 | 7,0 | 6,6 | 6,3 |
| Hogares (sin A/C / con A/C) | 396 / 33 | 119 / 35 | 85 / 59 | 46 / 66 |
| $p_c$ implícito | 0,96 | 0,83 | 0,94 | 1,00 |
```

En la propuesta, $p_c$ es la probabilidad de que el ventilador de la zona siga encendido mientras funciona el A/C (Tabla 5 de la propuesta). Si el A/C funciona dentro de las horas en que el hogar usaría el ventilador, las horas de ventilador que se pierden son la fracción $1-p_c$ de las horas de A/C:

$$
1 - p_c \approx \frac{\bar h_{v}^{\,\text{sin A/C}} - \bar h_{v}^{\,\text{con A/C}}}{\bar h_{\text{A/C}}}
$$ (eq-pc)

Con la ecuación {eq}`eq-pc`, el A/C desplaza menos de media hora de ventilador al día en los estratos 1, 3 y 4, y 1,2 h en el estrato 2. Se propone un prior centrado en $p_c \approx 0{,}95$ con rango de 0,8 a 1,0. Los estratos 5 y 6 no permiten la comparación, porque solo 7 y 1 hogares de la muestra no tienen A/C. Para ellos se usa el mismo prior.

```{table} Tamaño y antigüedad de la nevera, ECV 2019 (% de los hogares con nevera).
:name: tab-nevera

| Concepto | E1 | E2 | E3 | E4 | E5 | E6 | Ciudad |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Pequeña | 19,3 | 16,8 | 8,1 | 10,8 | 0,0 | 1,7 | 13,6 |
| Mediana | 74,5 | 71,0 | 72,3 | 74,7 | 69,2 | 46,9 | 71,7 |
| Grande | 6,2 | 12,2 | 19,6 | 14,5 | 30,8 | 51,4 | 14,6 |
```

La antigüedad de la nevera no se desagrega por estrato por el tamaño de la muestra. En la ciudad, la mediana es de 5 años: 21,1 % de las neveras tiene 2 años o menos, 41,3 % entre 3 y 5 años, 19,3 % entre 6 y 9 años y 17,9 % 10 años o más.

## Hogar y presencia en la vivienda

```{table} Atributos del hogar por estrato.
:name: tab-hogar

| Concepto | E1 | E2 | E3 | E4 | E5 | E6 | Fuente |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Personas por hogar | 3,91 | 3,67 | 2,95 | 2,87 | 2,49 | 3,49 | ECV 2024 |
| Cuartos por vivienda | 3,32 | 3,76 | 3,83 | 3,93 | 3,91 | 4,98 | ECV 2024 |
| Ocupados que trabajan en la propia vivienda, % | 15,6 | 14,9 | 16,2 | 19,9 | 27,7 | 28,5 | GEIH 2024 |
```

```{table} Composición de las personas de 10 años o más y presencia en la vivienda por grupo de estrato, ENUT 2024–2025 (Atlántico, cabeceras).
:name: tab-presencia

| Concepto | E1–2 | E3–4 | E5–6 |
| --- | --- | --- | --- |
| Ocupados, % | 41,0 | 48,0 | 53,3 |
| Dedicados a oficios del hogar, % | 22,0 | 13,7 | 6,9 |
| Estudiantes, % | 17,9 | 15,9 | 10,7 |
| Mayores de 65 años no ocupados, % | 8,6 | 14,2 | 15,7 |
| Horas de sueño por día | 8,1 | 7,9 | 7,8 |
| Hogares con alguien en casa todo el día hábil, % | 86,0 | 81,7 | 84,5 |
| Hogares con alguien en casa todo el día de fin de semana, % | 92,4 | 94,3 | 96,2 |
```

Un ocupado pasa en promedio 7,7 h fuera de la vivienda en un día hábil y 4,9 h en el fin de semana, sumando trabajo y traslados. Los estudiantes se reparten entre las jornadas de la mañana (57,6 %), la tarde (24,9 %), única (11,1 %) y de la noche (5,1 %). La ENUT no identifica el municipio. Por eso se usa el dominio de cabeceras del Atlántico, que incluye a Barranquilla, Soledad, Malambo y Puerto Colombia.

## Expansión y calibración

```{table} Hogares por estrato y consumo facturado residencial (SUI, Barranquilla urbano).
:name: tab-calibracion

| Concepto | E1 | E2 | E3 | E4 | E5 | E6 | Total |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Suscriptores, diciembre de 2024 | 109.983 | 63.711 | 75.704 | 49.536 | 17.720 | 13.447 | 330.101 |
| Viviendas en el catastro | 108.985 | 72.493 | 72.000 | 49.190 | 16.843 | 13.207 | 332.718 |
| kWh por suscriptor y mes, media 2015–2019 | 308 | 245 | 278 | 353 | 442 | 735 | 318 |
| Rango de las medias anuales 2015–2019 | 286–342 | 231–256 | 265–286 | 330–367 | 410–466 | 681–776 | 300–336 |
| kWh por suscriptor y mes, 2024 | 318 | 205 | 245 | 319 | 396 | 690 | — |
| Alza de agosto–septiembre frente a febrero–marzo, 2015–2025, % | 10,9 | 16,5 | 23,5 | 28,0 | 29,1 | 27,6 | — |
```

Los años 2015 a 2019 son el periodo de calibración de la propuesta (Fase 3, paso 4). El consumo de 2021 a 2025 se reserva para la validación. El año 2020 se excluye por el cambio en la ocupación de las viviendas durante la pandemia. El consumo del estrato 1 es mayor que el de los estratos 2 y 3 pese a su menor tenencia de A/C. Este dato está señalado en [Datos sospechosos y pendientes](07_datos_sospechosos.md) y se revisará con Air-e antes de la calibración.
