# Datos de entrada de la tesis: demanda de enfriamiento residencial en Barranquilla

**María Carolina Cantillo Orozco** · Maestría en Ingeniería Mecánica, Universidad del Norte · Actualizado: 27 de octubre de 2026

## Resumen

La demanda eléctrica por climatización crece en las ciudades de clima cálido húmedo a medida que más hogares adquieren aire acondicionado (A/C), y su distribución horaria condiciona la planeación de la red y el diseño de medidas de eficiencia energética. Los modelos *bottom-up* estiman esos perfiles a partir de las características y el comportamiento de cada hogar {cite:p}`paatero2006,thorve2023`. Sin embargo, suelen desarrollarse en países que cuentan con mediciones por equipo, encuestas de uso horario y bases detalladas de edificaciones. En la mayoría de las ciudades latinoamericanas no hay mediciones de consumo por uso final, las encuestas de hogares tienen muestras pequeñas por grupo socioeconómico y ninguna fuente registra a qué hora se usa el A/C.

Este trabajo plantea una metodología para construir los insumos de un modelo *bottom-up* horario en ese contexto de escasez de datos, a partir solo de fuentes públicas, y la aplica a Barranquilla, Colombia, por estrato socioeconómico. La metodología combina fuentes que por separado son insuficientes:

- tres encuestas de hogares del DANE: Calidad de Vida 2018–2025 {cite:p}`dane_ecv`, Uso del Tiempo 2024–2025 y Gran Encuesta Integrada de Hogares 2024 {cite:p}`dane_enut,dane_geih`;
- el consumo facturado del Sistema Único de Información, SUI {cite:p}`sui2026`;
- el catastro municipal {cite:p}`catastro2026`;
- la línea base de edificaciones de CEELA {cite:p}`ceela2025a`;
- la demanda horaria del mercado regulado que publica XM {cite:p}`xm_api`.

Para compensar el tamaño reducido de las muestras, las estimaciones se ponderan considerando el efecto del diseño muestral {cite:p}`kish1965,wolter2007` y se postestratifican con los suscriptores del SUI {cite:p}`holt1979`. La serie anual de tenencia de A/C se obtiene con modelos lineales generalizados binomiales con sobredispersión {cite:p}`mccullagh1989`. Se promedian dos especificaciones {cite:p}`hoeting1999` y la incertidumbre se expresa como distribuciones Beta. Una regresión logística ponderada con errores robustos {cite:p}`hosmer2013,mackinnon1985` relaciona la tenencia con el ingreso y el tipo de techo. Con ella se imputa la probabilidad de tenencia a cada una de las 332.718 viviendas del catastro. Cada parámetro se clasifica según la evidencia que lo respalda:

- estimado directamente;
- calibrado con datos agregados;
- supuesto declarado, con rango y análisis de sensibilidad.

Una prueba previa decide si la forma horaria del uso del A/C puede calibrarse. Consiste en regresiones horarias de la demanda de XM sobre el índice de calor diario, con errores robustos a la autocorrelación {cite:p}`newey1987`.

La tenencia de A/C crece de 13 % en el estrato 1 a 98 % en el 6, y en la ciudad pasa de 35,6 % en 2019 a 41,2 % en 2024. A igual estrato e ingreso, los techos livianos la reducen (razón de momios de 0,15 para zinc frente a concreto). En 82–86 % de los hogares alguien permanece en la vivienda todo el día hábil, lo que descarta el supuesto de vivienda vacía de día, habitual en los modelos europeos. La demanda regulada aumenta entre 1,8 % y 2,1 % por grado de índice de calor en todas las horas, pero la forma de su respuesta nocturna cambia entre años, así que la hora de uso del A/C queda como supuesto declarado. Los resultados muestran qué parámetros pueden estimarse con datos públicos y cuáles exigen supuestos explícitos, lo que hace la metodología transferible a otras ciudades con información similar.

**Palabras clave:** demanda de enfriamiento residencial; perfiles horarios de carga; modelado bottom-up; estratificación socioeconómica; calibración con datos agregados; Barranquilla.

## Abstract

Electricity demand for space cooling is growing in hot and humid cities as more households acquire air conditioners, and its hourly distribution shapes grid planning and the design of energy-efficiency measures. Bottom-up models estimate these profiles from the characteristics and behaviour of each household {cite:p}`paatero2006,thorve2023`. However, they are usually developed in countries with appliance-level metering, time-use surveys of appliance operation and detailed building stock databases. Most Latin American cities have no end-use consumption measurements, household surveys have small samples per socioeconomic group, and no source records when air conditioners are used.

This work proposes a methodology to build the inputs of an hourly bottom-up model in this data-scarce context, using only public sources, and applies it to Barranquilla, Colombia, by socioeconomic stratum. The methodology combines sources that are insufficient on their own:

- three household surveys by DANE, the national statistics office: the Quality of Life Survey 2018–2025 {cite:p}`dane_ecv`, the Time Use Survey 2024–2025 and the Integrated Household Survey 2024 {cite:p}`dane_enut,dane_geih`;
- billed electricity consumption from the national utility information system, SUI {cite:p}`sui2026`;
- the municipal cadastre {cite:p}`catastro2026`;
- the CEELA building energy baseline {cite:p}`ceela2025a`;
- hourly demand of the regulated market published by XM, the system operator {cite:p}`xm_api`.

To compensate for small samples, estimates are weighted accounting for the survey design effect {cite:p}`kish1965,wolter2007` and post-stratified to SUI subscribers {cite:p}`holt1979`. The annual series of air-conditioner ownership is obtained with binomial generalized linear models with overdispersion {cite:p}`mccullagh1989`. Two specifications are averaged {cite:p}`hoeting1999` and the uncertainty is expressed as Beta distributions. A weighted logistic regression with robust standard errors {cite:p}`hosmer2013,mackinnon1985` relates ownership to income and roof type. It is then used to impute the ownership probability to each of the 332,718 dwellings in the cadastre. Each parameter is classified by the evidence that supports it:

- estimated directly;
- calibrated against aggregate data;
- declared assumption, with a range and sensitivity analysis.

A preliminary test decides whether the hourly shape of air-conditioner use can be calibrated. It consists of hourly regressions of XM demand on the daily heat index, with autocorrelation-robust standard errors {cite:p}`newey1987`.

Air-conditioner ownership rises from 13 % in stratum 1 to 98 % in stratum 6, and city-wide it grows from 35.6 % in 2019 to 41.2 % in 2024. At equal stratum and income, lightweight roofs lower ownership (odds ratio of 0.15 for zinc relative to concrete). In 82–86 % of households someone stays home all weekday, which rules out the empty-home-by-day assumption common in European models. Regulated demand rises by 1.8 % to 2.1 % per degree of heat index at every hour, but the shape of its night-time response changes between years, so the timing of air-conditioner use remains a declared assumption. The results show which parameters can be estimated from public data and which require explicit assumptions, making the methodology transferable to other cities with similar information.

**Keywords:** residential cooling demand; hourly load profiles; bottom-up modelling; socioeconomic stratification; calibration with aggregate data; Barranquilla.

## Flujo de los datos

```{figure} figuras/flujo_datos.png
:name: fig-flujo
:width: 100%
Flujo de los datos de entrada hacia las tres fases del modelo de la tesis.
```

## Tenencia de aire acondicionado

Uno de los insumos centrales del modelo es la **tenencia de aire acondicionado (A/C) por estrato socioeconómico y por año**. La ECV del DANE registra esta variable, pero el tamaño de la muestra de Barranquilla en cada estrato es reducido, por lo que las proporciones anuales presentan una variabilidad muestral elevada. Para obtener una serie estable, la tenencia de cada estrato se modela con una regresión logística sobre las olas 2018–2025 de la encuesta. El modelo entrega una estimación para cada año entre 2015 y 2027; la proporción de hogares con A/C en la ciudad es de **35,6 % en 2019**, último año del periodo de calibración (2015–2019), **41,2 % en 2024**, año de referencia de la tesis, y 43,1 % en 2025, la ola más reciente.

Para cada estrato se ajustaron dos especificaciones. La primera supone que la tenencia cambia a un ritmo constante en el tiempo (tendencia lineal en escala logit) en los seis estratos. La segunda conserva esa tendencia solo donde la prueba de significancia la respalda, los estratos 1 y 3 (p < 0,05), y en los estratos 2, 4, 5 y 6, cuya pendiente estimada no se distingue de la variabilidad muestral (p entre 0,39 y 0,53), supone un nivel constante igual al promedio de las olas. Como los datos no permiten preferir una especificación sobre la otra, la serie adoptada (*variante C*) promedia ambas con igual peso. Las dos coinciden en los años con encuesta y se separan al extrapolar a 2015–2017 y 2026–2027 (hasta 2,9 puntos para la ciudad en 2015); esa diferencia se incorpora a la incertidumbre de la serie, junto con el efecto del diseño muestral de la encuesta. Para la ciudad, el intervalo de confianza del 95 % en 2024 es de ± 2,9 puntos porcentuales.

```{figure} figuras/tenencia_estrato_C.png
:name: fig-tenencia-intro
:width: 100%
Tenencia de A/C por estrato y año (variante C) con su intervalo de confianza del 95 %; los puntos son las olas de la ECV. La ola 2020 no entra en el ajuste.
```

## Cómo leer este sitio

- **Análisis y conclusiones**, **Insumos del modelo** y **Cambios a la propuesta**: los resultados principales y lo que la tesis toma de ellos.
- **Encuestas usadas y representatividad**: qué encuestas y años se usaron y qué parte de la población representa cada muestra.
- **Fuentes**, **Resultados**, **Metodología** y **Serie de tenencia, error de la encuesta e imputación**: cifras y cálculos detallados.
- **Respuesta horaria al calor** y **Línea base de CEELA**: la demanda horaria de XM frente al clima (compuerta horaria) y la envolvente, la climatización y los consumos de los edificios representativos de CEELA.
- **Consumo del SUI por tipo de lectura**: el consumo medido y el estimado por estrato, la caída del consumo por suscriptor y la comparación con otras ciudades.
- **Coherencia entre fuentes** y **Supuestos, sensibilidad y limitaciones**: la validación de los datos y el registro de supuestos.
- **Reproducibilidad** y **Referencias**: scripts, tablas y bibliografía.

Las bases por hogar y por vivienda no se publican aquí; los microdatos son públicos en el [catálogo del DANE](https://microdatos.dane.gov.co) y el [SUI](https://reportes.sui.gov.co).

## Cómo citar

Cantillo Orozco, M. C. (2026). *Datos de entrada de la tesis: demanda de enfriamiento residencial en Barranquilla* [sitio web y repositorio]. Universidad del Norte. https://github.com/mcarocantillo/tesis-datos-barranquilla
