# Respuesta horaria al calor (compuerta horaria)

Ninguna encuesta registra a qué hora se usa el A/C ([Supuestos, sensibilidad y limitaciones](12_supuestos.md)). La única fuente horaria disponible es la demanda de energía que publica XM, y la propuesta prevé una prueba previa, la *compuerta horaria*, para decidir si esa demanda puede usarse para calibrar la forma horaria del uso del A/C. Si la demanda tiene una respuesta horaria al calor distinta de cero y estable entre años, la forma horaria se calibra contra XM (capa B). Si no es estable, la forma horaria queda como supuesto declarado, con su rango y su análisis de sensibilidad (capa C). Este capítulo documenta la estimación con los años 2021–2025 y su resultado: **la forma horaria del A/C queda en capa C**.

## Datos

**Demanda.** Demanda comercial horaria del mercado de comercialización «CARIBE SOL», mercado regulado, de la API pública de XM {cite:p}`xm_api`. Es el mercado de Air-e desde octubre de 2020 (Atlántico, Magdalena y La Guajira) e incluye las pérdidas asignadas al mercado, que son cerca de 1,5 % de la demanda y no incluyen las pérdidas de distribución ([XM](26_xm.md)). Para 2015–2019, cuando ese mercado no existía, se usó como contraste la demanda de los agentes de Electricaribe (EDCC y EDIC). El mercado COSTA CARIBE, que también se descargó, empieza el 14 de enero de 2017. También se descargó la demanda no atendida diaria de las subáreas Atlántico y GCM (Guajira, Cesar y Magdalena), que sirve para marcar los días con cortes. Son series agregadas del mercado; no hay datos por usuario.

**Clima.** Serie horaria de ERA5-Land {cite:p}`munozsabater2021` en la celda de 11,0° N y 74,8° O, la más cercana al punto de Barranquilla pedido (10,96° N; 74,80° O), convertida a hora local (UTC−5). La estimación de esta página se hizo con la copia de ERA5-Land que sirve Open-Meteo {cite:p}`openmeteo`, que no requiere credenciales, y se repitió con ERA5-Land completo descargado de GDEX, el archivo de datos del NCAR (sección {ref}`repeticion-gdex`). Como contraste se usó la estación 0029045190 del aeropuerto Ernesto Cortissoz del IDEAM {cite:p}`ideam_cortissoz`, con los registros de cada hora en punto. La humedad relativa se calcula con la fórmula de Magnus {cite:p}`alduchov1996` y el índice de calor (HI) con la regresión de Rothfusz que usa la NOAA {cite:p}`rothfusz1990`. La variable explicativa es el HI medio de cada día, $HI_d$. El algoritmo de la NOAA pasa de la fórmula simple de Steadman a la regresión de Rothfusz cerca de 26,7 °C de HI, y con humedad alta el HI salta entre 1,2 y 1,4 °C cuando el aire pasa de 26,2 a 26,3 °C, justo en las temperaturas de la noche de Barranquilla ([Clima](27_clima.md)). El salto no se ha corregido y su efecto sobre $b_h$ está pendiente de evaluar ([Datos sospechosos y pendientes](07_datos_sospechosos.md)).

## Método

Para cada hora del día $h$ se estima una regresión de la ecuación 10 de la propuesta:

$$
100\,\ln L_{d,h} = a_h + b_h\,HI_d + \boldsymbol{\gamma}_h^{\top}\mathbf{t}_d + \delta_{h,m(d)} + \varepsilon_{d,h}
$$ (eq-compuerta)

donde $L_{d,h}$ es la demanda del día $d$ en la hora $h$ (0 = de 00:00 a 01:00, hora local), $\mathbf{t}_d$ indica el tipo de día (sábado; domingo o festivo; fin de año, del 24 de diciembre al 6 de enero; Carnaval; Semana Santa) y $\delta_{h,m(d)}$ es un efecto fijo de cada año-mes. Con el logaritmo, $b_h$ es el cambio porcentual de la demanda de la hora $h$ por cada °C de HI diario, de modo que se comparan formas y no niveles. Los efectos fijos absorben el crecimiento de la demanda, la estacionalidad y los cambios del mercado, así que $b_h$ sale de la variación del calor entre días de un mismo mes. Los errores estándar son HAC con 7 rezagos diarios {cite:p}`newey1987`.

La muestra tiene 1.399 días de 2021–2025. De los 1.826 días del periodo se excluyeron 427: 221 con horas anómalas (más de 12 % por fuera de la mediana móvil de su hora y tipo de día, que indica desconexiones o fallas de medida) y 239 con demanda no atendida mayor que 0,5 % de la demanda del mercado en Atlántico y GCM (algunos días cumplen las dos condiciones). El año 2020 no se usa por la pandemia y porque en octubre el mercado pasó de siete a tres departamentos, que bajó la demanda a la mitad. La demanda regulada no cayó en la pandemia, solo creció más despacio ([XM](26_xm.md)). El año 2026 se reserva para la prueba ciega. El filtro de demanda no atendida divide la de las subáreas Atlántico y GCM por la demanda de CARIBE SOL, aunque GCM incluye el Cesar, que desde octubre de 2020 no pertenece a ese mercado, así que el filtro excluye algunos días de más.

## Respuesta por franja horaria

```{figure} figuras/b_h_compuerta.png
:name: fig-compuerta
:width: 100%
Respuesta de la demanda regulada del mercado de Air-e al índice de calor diario. (a) $b_h$ de 2021–2025 con su IC 95 %, todos los días y domingos y festivos; (b) $b_h$ por año; (c) respuesta por franja, conjunta y por año; (d) reparto horario de la respuesta en niveles (MWh/°C). El sombreado marca las horas nocturnas (22 a 5 h).
```

```{table} Respuesta de la demanda al índice de calor diario por franja horaria, 2021–2025 (% de la demanda por °C).
:name: tab-compuerta-franjas

| Franja | $b$ | IC 95 % | Diferencia en domingos y festivos | $p$ de la diferencia |
| --- | --- | --- | --- | --- |
| Noche (22 a 5 h) | 1,92 | 1,79 – 2,05 | +0,12 | 0,22 |
| Mañana (6 a 11 h) | 1,79 | 1,67 – 1,90 | +0,34 | 0,001 |
| Tarde (12 a 17 h) | 2,13 | 2,01 – 2,25 | +0,28 | 0,008 |
| Pico (18 a 21 h) | 1,97 | 1,86 – 2,08 | +0,07 | 0,45 |
```

Un grado más de HI diario sube la demanda entre 1,8 % y 2,1 % en todas las franjas ({numref}`tab-compuerta-franjas`). La respuesta nocturna es distinta de cero: las 8 horas de 22 a 5 h tienen el intervalo por encima de cero, y la franja también en cada año. El perfil es casi plano. $b_h$ va de 1,65 a las 6 h a 2,22 a las 14 h. Expresada en MWh/°C, la noche recibe entre 31 % y 34 % de la respuesta diaria según el año, casi lo mismo que un reparto uniforme de 8 de 24 horas (33 %). En domingos y festivos aumenta la respuesta diurna, no la nocturna.

```{table} Respuesta nocturna por año, 2021–2025.
:name: tab-compuerta-anios

| Año | Días | $b$ nocturno (%/°C) | IC 95 % | Noche / tarde | Reparto nocturno de la respuesta en MWh/°C (%) |
| --- | --- | --- | --- | --- | --- |
| 2021 | 276 | 2,13 | 1,85 – 2,41 | 0,98 | 34,1 |
| 2022 | 297 | 1,92 | 1,64 – 2,20 | 0,89 | 32,9 |
| 2023 | 278 | 1,97 | 1,66 – 2,28 | 0,95 | 32,5 |
| 2024 | 266 | 1,90 | 1,70 – 2,10 | 0,92 | 33,4 |
| 2025 | 282 | 1,68 | 1,40 – 1,97 | 0,77 | 31,0 |
```

## Estabilidad entre años y decisión

La regla de la compuerta tiene dos criterios:

1. **La respuesta nocturna es distinta de cero.** La franja de 22 a 5 h tiene $b > 0$ con el IC 95 % sobre cero, y al menos 6 de las 8 horas nocturnas también. Se cumple: las 8 horas y los 5 años ({numref}`tab-compuerta-anios`).
2. **La respuesta nocturna es estable entre años**, en nivel y en forma. El *nivel* nocturno es significativo en al menos 4 de los 5 años y no difiere entre años (prueba de Wald con errores HAC). Se cumple: $p = 0{,}35$. La *forma* nocturna centrada ($b_h$ menos la media nocturna del año) no difiere entre años (prueba de Wald conjunta con errores agrupados por semana). **No se cumple.**

La forma nocturna existe ($p < 10^{-17}$, con una amplitud de 0,39 puntos entre la hora de mayor y la de menor respuesta), pero cambia entre años ($p = 0{,}008$; 28 grados de libertad, 262 semanas). La señal del encendido nocturno, el exceso de las 22 y 23 h sobre la media de la noche, va de −0,13 puntos en 2023 a +0,45 puntos en 2022: la forma cambia entre años tanto como su propia amplitud. La inestabilidad se mantiene al tomar la noche contigua, de 22 h a 5 h del día siguiente ($p = 0{,}0001$), y con la demanda de Electricaribe de 2015–2019 ($p = 0{,}0001$). Una primera versión de la regla, basada en la correlación entre el perfil de cada año y el conjunto, resultó inestable con perfiles tan planos (mínima de −0,04 en 2023) y también daba capa C.

**Decisión: capa C.** La hora media del encendido nocturno del A/C y su dispersión no se calibran contra XM. Quedan como supuesto declarado, con rango y análisis de sensibilidad (supuesto S16 en [Supuestos, sensibilidad y limitaciones](12_supuestos.md)).

## Lo que XM sí restringe

Aunque la forma hora a hora no es estable, la demanda sí restringe la respuesta **por franjas**, y eso puede entrar en la Fase 3 como blanco de validación del modelo:

- La respuesta nocturna es de 1,92 %/°C (IC 95 %: 1,79 a 2,05) y su nivel no cambia entre años.
- La noche aporta entre 31 % y 34 % de la respuesta diaria en MWh/°C.
- La respuesta nocturna equivale a entre 0,77 y 0,98 veces la de la tarde, según el año.

(repeticion-gdex)=
## Repetición con ERA5-Land de GDEX

La propuesta prevé repetir la estimación con la descarga oficial de ERA5-Land y reportar las dos fuentes. ERA5-Land completo se descargó de GDEX (gdex.ucar.edu), que distribuye el mismo reanálisis del ECMWF que el Climate Data Store: pedidos 953933 (temperatura, punto de rocío, presión y viento) y 953943 (radiación de onda corta y larga y lluvia), de enero de 2015 a septiembre de 2026, en una malla de 0,1° sobre 10,0–11,9° N y 74,0–74,9° O. Se usa la celda más cercana al punto de la compuerta (11,0° N; 74,8° O), la misma que usa Open-Meteo.

Hora a hora, la temperatura y el punto de rocío de GDEX son los de Open-Meteo más una constante de 0,175 K (desviación estándar de 0,03 K; correlación 1,000), probablemente por la corrección de altura que aplica Open-Meteo. GDEX no trae el punto de rocío en 608 horas sueltas de 2019, 2022 y 2023 (el campo está vacío en toda la malla, en huecos de 1 a 9 h); se rellenaron con el de Open-Meteo más esa constante. Sin el relleno se pierden 38 días de la regresión y los resultados apenas cambian (noche: 1,89 %/°C).

```{table} Respuesta de la demanda al índice de calor diario con las dos fuentes de ERA5-Land, 2021–2025 (1.399 días, % de la demanda por °C).
:name: tab-compuerta-fuentes

| Medida | Open-Meteo | GDEX | IC 95 % con GDEX |
| --- | --- | --- | --- |
| $b$ noche (22 a 5 h) | 1,92 | 1,90 | 1,78 – 2,02 |
| $b$ mañana (6 a 11 h) | 1,79 | 1,77 | 1,65 – 1,88 |
| $b$ tarde (12 a 17 h) | 2,13 | 2,09 | 1,97 – 2,21 |
| $b$ pico (18 a 21 h) | 1,97 | 1,93 | 1,83 – 2,04 |
| $b$ noche, Electricaribe 2015–2019 | 1,92 | 1,89 | 1,78 – 2,00 |
| Nivel nocturno igual entre años ($p$) | 0,35 | 0,40 | |
| Forma nocturna igual entre años ($p$) | 0,008 | 0,012 | |
| Sesgo del HI frente al IDEAM (°C) | −2,4 | −1,9 | |
| Decisión | capa C | capa C | |
```

Con GDEX, el HI diario es 0,45 °C mayor que con Open-Meteo y las dos series correlacionan 0,999, así que la respuesta casi no cambia: baja entre 0,02 y 0,05 puntos en todas las franjas ({numref}`tab-compuerta-fuentes`). Por año, la respuesta nocturna va de 1,65 %/°C (2025) a 2,08 %/°C (2021), y la noche aporta entre 31 % y 34 % de la respuesta diaria en MWh/°C, como con Open-Meteo. Los dos criterios dan el mismo resultado: el nivel nocturno es distinto de cero y estable, y la forma nocturna cambia entre años ($p = 0{,}012$; con la noche contigua, $p = 0{,}0001$). **La decisión no cambia: capa C.** El contraste con el IDEAM mejora un poco, porque el sesgo de la temperatura pasa de −0,70 a −0,52 °C y el del HI de −2,4 a −1,9 °C, pero ERA5-Land sigue subestimando el calor del mediodía. Con el HI de IDEAM, la respuesta nocturna sigue en 0,94 %/°C.

## Cautelas

- **XM no es demanda residencial.** El mercado de Air-e mezcla usuarios residenciales, comerciales y oficiales de tres departamentos, y se usa el clima de Barranquilla como referencia de todos. Una respuesta nocturna positiva es compatible con el uso residencial del A/C, pero no lo prueba.
- **El nivel de $b$ depende de la fuente del HI.** Con el HI de IDEAM (654 días con datos suficientes) la respuesta nocturna baja a 0,94 %/°C. ERA5-Land subestima el HI de mediodía ({numref}`tab-coherencia-clima`), y el HI de IDEAM tiene más ruido de medida y menos días.
- **Fuente del clima.** La estimación se repitió con ERA5-Land de GDEX y da lo mismo que con la copia de Open-Meteo ({numref}`tab-compuerta-fuentes`). Las dos son el mismo reanálisis, así que la repetición confirma la copia, no la calidad de ERA5-Land; la diferencia que importa sigue siendo frente al IDEAM.
- **La regla es de este ejercicio.** Los umbrales (6 de 8 horas, 4 de 5 años, $p > 0{,}05$) se fijaron para esta prueba; no provienen de una norma.

## Archivos

Tablas en `tablas/`: `franjas.csv` (respuesta por franja, conjunta y por año, y diferencia de domingos y festivos), `b_h_por_hora.csv` ($b_h$ de todas las especificaciones, incluidas las de robustez), `estabilidad.csv` (criterios por año), `b_h_niveles_reparto.csv` (ecuación {eq}`eq-compuerta` en niveles y reparto horario), `contraste_era5land_ideam.csv` (sesgo y RMSE por hora y por mes) y `decision.json` (regla y resultado de la compuerta), todas con Open-Meteo. Las mismas tablas con GDEX están en `tablas/compuerta_gdex/` (figura en `figuras/b_h_compuerta_gdex.png`), y la comparación de las dos fuentes en `tablas/comparacion_fuentes_clima.csv`. Scripts en `scripts/compuerta/` ([Reproducibilidad](08_reproducibilidad.md)). Las descargas crudas de XM, Open-Meteo, GDEX e IDEAM no se publican; los scripts las reconstruyen desde las fuentes públicas, salvo GDEX, que requiere una cuenta gratuita y un pedido en gdex.ucar.edu.
