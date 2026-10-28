# Línea base de CEELA para Barranquilla

En 2025 el proyecto CEELA (Fortalecimiento de capacidades para la eficiencia energética en edificios de América Latina), financiado por la Cooperación Suiza (COSUDE) y ejecutado por el consorcio de EBP, Carbon Trust y Colbún para la UPME, publicó la línea base de desempeño energético de las edificaciones residenciales y de oficinas de Colombia. La línea base tiene tres informes: las características comunes de las edificaciones {cite:p}`ceela2025a`, la caracterización energética de los edificios seleccionados {cite:p}`ceela2025b` y el informe de resultados {cite:p}`ceela2025c`. CEELA simula un edificio real representativo por tipología en cuatro climas, y Barranquilla representa el clima cálido húmedo. Este capítulo resume lo que la tesis toma de CEELA para Barranquilla, compara sus consumos con el SUI del repositorio y señala sus límites.

CEELA trabaja con cuatro tipologías residenciales: unifamiliar y multifamiliar, cada una de vivienda de interés social (VIS) y no VIS. En su análisis del SUI, la VIS corresponde a los estratos 1 y 2 y la no VIS a los estratos 3 a 6 {cite:p}`ceela2025b`.

## Edificios representativos

:::{table} Edificios representativos de Barranquilla y consumo de refrigeración simulado climatizando toda la vivienda {cite:p}`ceela2025c`.
:name: tab-ceela-edificios

| Tipología | Edificio | Características | Consumo de refrigeración (kWh/m²·año) |
| --- | --- | --- | --- |
| Unifamiliar VIS | Adelita Char | Vivienda de dos plantas, adosada | 107 |
| Multifamiliar VIS | Palmanova | Edificio de más de 12 pisos, adosado | 90 |
| Unifamiliar no VIS | Casas de Portobelo | Vivienda de dos plantas, adosada | 77 |
| Multifamiliar no VIS | Riverside | Edificio de más de 12 pisos, adosado | 64 |
:::

El consumo de la {numref}`tab-ceela-edificios` es el de refrigeración en el escenario de «energía virtual para confort»: un sistema estándar de bomba de calor compacta (PTHP, según el apéndice G de ASHRAE 90.1) climatiza todos los espacios de la vivienda y garantiza el confort cuando hay ocupantes {cite:p}`ceela2025c`. Es, por tanto, la energía necesaria para mantener el confort en toda la vivienda, no el consumo observado de los hogares, que en su mayoría no tienen A/C o climatizan una sola habitación ({numref}`tab-ceela-climatizacion`). El consumo por metro cuadrado es mayor en la vivienda unifamiliar VIS, la de cubierta más liviana, y menor en la multifamiliar no VIS; CEELA atribuye la diferencia entre las dos multifamiliares a la mayor área de la no VIS {cite:p}`ceela2025c`.

## Envolvente

:::{table} Parámetros de la envolvente de los edificios representativos de Barranquilla {cite:p}`ceela2025a,ceela2025b`.
:name: tab-ceela-envolvente

| Parámetro | Unifamiliar VIS | Unifamiliar no VIS | Multifamiliar VIS | Multifamiliar no VIS |
| --- | --- | --- | --- | --- |
| Relación ventana-muro | 20–40 % | 20–40 % | 20–40 % | 20–40 % (E5–E6); menos de 20 % (E3–E4) |
| Vidrio | Simple, 4–6 mm, marco de aluminio, U = 5,88 W/m²K | Igual | Igual | Igual |
| Sombreamiento | Ninguno | Balcones | Balcones | Balcones |
| Muro exterior (U, W/m²K) | Mampostería estructural de bloque de concreto, 2,3 | Mampostería estructural de arcilla, 2,7 | Ladrillo en fachada, 3,6, o sistema industrializado con pantalla de concreto, 4,1 | Ladrillo en fachada, 1,9, o sistema industrializado, 4,1 |
| Cubierta (U, W/m²K) | Teja de fibrocemento de 6 mm, 6,6 | Panel sándwich revestido en aluminio de 40 mm, 4,4 | Losa de concreto vaciada con impermeabilización, 3,6 | Igual que la multifamiliar VIS, 3,6 |
| Índice de reflectancia solar de la cubierta (SRI) | 0,4 | 0,4 | 0,15 | 0,15 |
:::

Los valores de SRI se transcriben en la escala en que los reporta CEELA {cite:p}`ceela2025b`. El vidrio simple de 4 a 6 mm con marco de aluminio predomina en todas las tipologías de vivienda {cite:p}`ceela2025a`. La U de los muros va de 1,9 a 4,1 W/m²K y la de las cubiertas de 3,6 (losa) a 6,6 W/m²K (fibrocemento). La teja de fibrocemento de la vivienda unifamiliar VIS coincide con la cubierta de asbesto-cemento que declara 60 % de los hogares de los estratos 1 y 2 en la ECV 2024 ({numref}`tab-techo`).

## Climatización

:::{table} Zonas climatizadas típicas por tipología en Barranquilla {cite:p}`ceela2025a`.
:name: tab-ceela-climatizacion

| Tipología | Segmento | Zona con A/C | Equipo |
| --- | --- | --- | --- |
| Unifamiliar VIS | VIS | Una habitación | Minisplit |
| Unifamiliar no VIS | E3–E4 | Una habitación | Minisplit |
| Unifamiliar no VIS | E5–E6 | Toda la vivienda | Minisplit |
| Multifamiliar VIS | VIS | Habitación principal; las demás habitaciones y áreas comunes con ventilación forzada | Minisplit |
| Multifamiliar no VIS | E3–E4 | Solo las habitaciones; áreas comunes con ventilación forzada | Minisplit |
| Multifamiliar no VIS | E5–E6 | Toda la vivienda | Minisplit, multitubería o VRF |
:::

CEELA no da una fracción climatizada numérica. Da la zona climatizada típica por tipología y segmento ({numref}`tab-ceela-climatizacion`): una habitación en la vivienda VIS, las habitaciones en los estratos 3 y 4, y toda la vivienda en los estratos 5 y 6. Es el insumo que faltaba para el prior del número de equipos ([Insumos del modelo](10_insumos.md)), y es coherente con la ECV 2019: la fracción de hogares con A/C que lo usa más de 12 h al día, un indicio de más de un equipo, es de 0 % a 2,7 % en los estratos 1 a 4 y de 8 % a 9 % en los estratos 5 y 6 ({numref}`tab-uso-ac`).

En las simulaciones, la consigna de refrigeración de Barranquilla es de **26,5 °C de temperatura operativa**, la temperatura operativa óptima del modelo de confort adaptativo de ASHRAE 55 para la ciudad, y no la temperatura del aire. El COP de refrigeración de las viviendas es **3,0**, y el sistema solo funciona cuando hay personas en la vivienda {cite:p}`ceela2025c`.

## Consumo facturado: CEELA frente al repositorio

CEELA validó sus modelos con el consumo promedio mensual del SUI de 2021–2024 por estrato, y logró diferencias menores de 8 % entre el consumo simulado sin asegurar confort y el facturado {cite:p}`ceela2025b`. Para extraer ese consumo usó la herramienta O3 del SUI con el filtro «tipo de lectura/medición» en datos reales, y eliminó las muestras con desviaciones marcadas de la media {cite:p}`ceela2025a`. El repositorio usa el reporte consolidado ele_com_096, que no separa el tipo de lectura {cite:p}`sui2026`. La {numref}`tab-ceela-sui` compara los dos promedios para los mismos años.

```{table} Consumo residencial por suscriptor, promedio mensual 2021–2024 (kWh/mes): CEELA (Tabla 42, solo lecturas reales) frente al SUI del repositorio (meses sin bandera y con consumo positivo).
:name: tab-ceela-sui

| Estrato | Segmento en CEELA | CEELA | Repositorio | Diferencia del repositorio | Meses válidos del repositorio | Medias anuales del repositorio |
| --- | --- | --- | --- | --- | --- | --- |
| E1 | VIS | 228,9 | 311,2 | +35,9 % | 42 | 292,8–325,4 |
| E2 | VIS | 214,6 | 208,2 | −3,0 % | 44 | 200,9–213,2 |
| E3 | No VIS | 253,8 | 242,5 | −4,5 % | 44 | 228,0–250,3 |
| E4 | No VIS | 334,0 | 321,2 | −3,8 % | 45 | 311,9–340,3 |
| E5 | No VIS | 407,8 | 386,1 | −5,3 % | 45 | 360,3–418,7 |
| E6 | No VIS | 706,3 | 657,5 | −6,9 % | 45 | 599,0–727,2 |
```

En los estratos 2 a 6 los dos promedios difieren entre 3 % y 7 %, y el de CEELA es siempre algo mayor. En el estrato 1 el repositorio da 36 % más. Con solo lecturas reales, el estrato 1 consume algo más que el 2 (229 frente a 215 kWh/mes), como señala CEELA, pero menos que el 3 (254), lo que sí es coherente con su menor tenencia de A/C. La diferencia sugiere que buena parte del exceso de consumo del estrato 1 en el repositorio ([Datos sospechosos y pendientes](07_datos_sospechosos.md)) proviene de consumos que no son lecturas reales, como los estimados o promediados. La consulta del SUI por tipo de lectura lo confirmó: con solo lecturas reales, el estrato 1 consume 209 kWh/mes en 2023–2025, lo mismo que el estrato 2 ([Consumo del SUI por tipo de lectura](17_lecturas_reales.md)). El CSV de la comparación es `tablas/CEELA_SUI_2021_2024_comparacion.csv` y el script, `scripts/ceela_sui.py`.

## Limitaciones de CEELA para este trabajo

1. **Edificios nuevos del mercado formal.** Las características comunes salen de 80 edificaciones postuladas por constructoras, la mayoría con menos de 5 años desde su entrega {cite:p}`ceela2025a`. No representan la vivienda antigua ni la informal, que pesan en los estratos 1 a 3 de Barranquilla.
2. **Un edificio por tipología.** Cada tipología y ciudad se representa con un solo edificio real {cite:p}`ceela2025b,ceela2025c`; no hay dispersión entre edificios.
3. **Ocupación de Bucaramanga.** Todas las tipologías de vivienda usan los perfiles de ocupación de Bucaramanga, obtenidos con encuestas de un proyecto anterior, por falta de información de otras ciudades {cite:p}`ceela2025b`. El repositorio tiene la presencia en la vivienda de la ENUT para el Atlántico ({numref}`tab-presencia`).
4. **Cargas de 2018.** Los equipos de las viviendas de Barranquilla se toman de las encuestas de {cite:t}`estrada2018`, y CEELA reconoce que falta información para algunas tipologías de la ciudad {cite:p}`ceela2025a`.

## Uso en la tesis

- Los parámetros de la {numref}`tab-ceela-envolvente` son el **centro de los rangos** de la envolvente de cada arquetipo en la Fase 1, con la correspondencia VIS para los estratos 1 y 2 y no VIS para los estratos 3 a 6 (supuesto S15).
- La consigna de 26,5 °C es el **límite superior** del rango de consigna del A/C; el límite inferior, 22 °C, es un supuesto propio (S14).
- El COP de 3,0 es el valor central del rendimiento del A/C en la Fase 2.
- La zona climatizada de la {numref}`tab-ceela-climatizacion` es el prior del número de equipos y de la fracción climatizada por estrato.
- El consumo de 64 a 107 kWh/m²·año es una **cota superior** de referencia: corresponde a climatizar toda la vivienda siempre que hay ocupantes.
