# Arquetipos de vivienda (Fase 1)

La Fase 1 de la tesis caracteriza los arquetipos de vivienda de Barranquilla a partir del catastro y asigna cada una de
las 332.718 viviendas a un arquetipo {cite:p}`catastro2026`. Cada arquetipo reúne viviendas de geometría y posición
parecidas, y por eso con un índice de carga parecido, y lleva sus priors de envolvente, sus atributos del hogar y su
ficha. Este capítulo resume
el método y los resultados; el código, el preregistro, las tablas completas y las fichas están en la carpeta
[`arquetipos/`](https://github.com/mcarocantillo/tesis-datos-barranquilla/tree/main/arquetipos) del repositorio.

:::{note}
**Estado (10 de noviembre de 2026).** Los siete pasos están hechos con las dos medidas de carga del Paso 3: por
vivienda, como está escrito en la propuesta (15 arquetipos), y por m² (10 arquetipos). Las cifras son las de la corrida
con el código corregido después de la verificación ({ref}`sec-arq-verificacion`). La elección entre las dos está
pendiente; mientras tanto aplica la carga por vivienda. Todos los productos existen para las dos soluciones. Una
variante del agrupamiento con cuatro variables más del catastro explica menos varianza de la carga en las dos medidas
y queda como análisis complementario ({numref}`tab-arq-ampliada`).
:::

## Datos y variables

Cada vivienda del catastro trae su área construida, el número de pisos de la unidad, el piso en que está, el año de
construcción, el uso, la condición de propiedad horizontal y el estrato. Con ellos se definen cuatro variables:

- **Posición frente a la cubierta:** casa (suelo y techo propios), último piso (techo expuesto en un edificio) o sin
  cubierta (otra vivienda encima, incluido el primer piso con vivienda encima). Es la variable que más pesa en la
  carga, porque el techo es la principal ganancia de calor. Una vivienda tiene el techo expuesto si su último piso es
  el más alto de su torre, identificada con los 24 primeros dígitos del número predial (predio matriz y número de
  torre). Si además empieza en el primer piso es casa, y si no, último piso.
- **Tipo de edificio:** baja altura (hasta 3 pisos) o multifamiliar (4 pisos o más), según el uso catastral.
- **Época:** antes de 1990, de 1990 a 2009, y 2010 o después.
- **Bloque de estratos:** 1-2, 3-4 y 5-6.

## Método

:::{table} Pasos de la Fase 1 y regla principal de cada uno. Las reglas se fijaron por escrito antes de calcular; los puntos en que la ejecución precisa la propuesta están en el registro de ajustes.
:name: tab-arq-pasos

| Paso | Qué se hace | Regla principal | Scripts |
| --- | --- | --- | --- |
| 1. Datos | Catastro depurado, una fila por vivienda, con la posición frente a la cubierta, la época y el bloque de estratos | Los valores imposibles quedan como faltantes; la época faltante toma la más frecuente de su tipo, posición y bloque | `src/comun.py`, `01` |
| 2. Agrupamiento | K-Means, k-prototypes y jerárquico con distancia de Gower, ajustados en una submuestra de 10.293 edificios (una vivienda por edificio en cada posición) y aplicados después a las 332.718 viviendas | Se agrupa por separado dentro de cada posición frente a la cubierta; DBSCAN aparta los atípicos del ajuste; el R² se calcula con todas las viviendas | `03`, `04` |
| 3. Número de arquetipos | Carga anual simplificada con envolvente común | El menor número de grupos a partir del cual ningún grupo adicional sube en 0,02 la varianza de la carga explicada (R²) | `02`, `03` |
| 4. Papel del estrato | Diseño plano (por posición) frente a anidado (por posición × bloque) | Anidado si el estrato explica al menos el 6 % de la varianza que queda dentro de los grupos | `03`, `04` |
| 5. Asignación | Árbol de decisión y Random Forest que resumen la regla de asignación | Fidelidad medida en 7 bloques de prueba de 2 km; la incertidumbre sale de repetir el agrupamiento en 100 submuestras | `06`, `10` |
| 6. Envolvente | Materiales de la ECV, transmitancias de la ISO 6946 y valores de CEELA | Priors con su incertidumbre, no valores únicos | `07` |
| 7. Hogar y validación | Atributos del hogar de la ECV, representatividad y sensibilidad | Una ficha por arquetipo | `05`, `08`, `09` |
| Robustez y verificación | Clima de GDEX, techo propio por vivienda, todos los edificios en lugar de la submuestra, mapas y comprobaciones automáticas | Ninguna prueba cambia las reglas | `11`, `13` a `16` |
:::

**Carga del Paso 3.** Es un índice anual de carga térmica de enfriamiento: carga sensible por cubierta y muros con la
temperatura sol-aire, por ventanas e infiltración, y carga latente por infiltración, con una consigna de 26,5 °C y 60 %
de humedad relativa, el clima horario de ERA5-Land de 2015 a 2025 {cite:p}`munozsabater2021,openmeteo` y la misma
envolvente para todas las viviendas, de modo que las diferencias vengan de la geometría y la posición. No es la carga
simulada de la Fase 2.

**Agrupamiento.** Los algoritmos se ajustan en una submuestra con una vivienda al azar por edificio dentro de cada
posición (4.074 casas, 3.139 últimos pisos y 3.080 sin cubierta), estratificada por tipo y bloque con un mínimo de 150
edificios por estrato. Así un edificio con cientos de apartamentos no pesa más que una casa, y la distancia de Gower,
que crece con el cuadrado del número de puntos, sigue siendo calculable. Después, cada una de las 332.718 viviendas se
asigna al centroide, prototipo o medoide más cercano de su posición, y el R² de la carga se mide sobre todas. Las
variables son el área, los pisos de la unidad y el piso del edificio (en logaritmo), la época, el tipo y la propiedad
horizontal. k-prototypes maneja a la vez las variables numéricas y las categóricas
{cite:p}`huang1998`, y el jerárquico usa la distancia de Gower {cite:p}`gower1971`. Para cada número total de grupos se
toma la mejor combinación entre estratos, y se elige el menor a partir del cual ninguna ganancia llega a 0,02. Entre
los algoritmos se queda el de mayor R² entre los estables, con los umbrales de Hennig {cite:p}`hennig2007`: Jaccard
ponderado de al menos 0,75 en 100 submuestras del 80 % y ningún grupo grande por debajo de 0,6. Agrupar por propiedades
del edificio y evaluar con el indicador energético es un enfoque con precedentes {cite:p}`dejaeger2020,dahlstrom2024`.

**Envolvente.** El material del techo, las paredes y los pisos sale de la ECV 2024 por bloque de estratos y por casa o
apartamento {cite:p}`dane_ecv`. Antes de juntar olas se probó con la corrección de Rao y Scott si cambiaban entre 2019 y
2024 {cite:p}`rao1981`: cambian en las casas de los estratos 1 y 2, así que se usa solo 2024. Cada material se traduce
a transmitancia con la ISO 6946 {cite:p}`iso6946`, a capacidad con las clases de masa de la ISO 13790 {cite:p}`iso13790`,
y las ventanas, la sombra y la zona climatizada parten de CEELA {cite:p}`ceela2025a,ceela2025b`. La infiltración con las
ventanas cerradas es lognormal {cite:p}`nazaroff2021`, con anclas medidas en clima cálido y en Brasil
{cite:p}`mathur2021,rodrigues2021`. El factor de sombra de 0,75 coincide con el de {cite:t}`lombardi2019`.

## Las dos soluciones

:::{table} Soluciones finales con las dos medidas de carga. Las dos usan el diseño anidado.
:name: tab-arq-soluciones

| | Carga por vivienda | Carga por m² |
| --- | --- | --- |
| Arquetipos | 15 | 10 |
| Algoritmo elegido | k-prototypes | K-Means |
| Varianza de la carga explicada (R²) | 0,63 | 0,93 |
| Estabilidad (Jaccard ponderado) | 0,98 | 1,00 |
| Silueta | 0,16 | 0,51 |
| Árbol que resume la asignación | 42 reglas; reproduce el 99,7 % de las asignaciones | 10 reglas; reproduce el 100 % |
| Qué separa, además de la posición y el bloque | las casas de los estratos 1 a 4 por tamaño | las casas de los estratos 1 y 2 de un piso o de dos o más |
:::

Como referencia, la sola partición por posición y bloque de estratos (9 grupos) explica 0,40 de la varianza por
vivienda y 0,90 por m², y la tipología por reglas (tipo × posición × época × bloque, 16 tipos), 0,40 y 0,91. El
agrupamiento suma, entonces, 0,23 por vivienda y 0,02 por m². El estrato explica entre el 12 y el 18 % de la varianza
que queda dentro de los grupos del diseño plano, por encima del umbral de 6 %, así que en las dos medidas se adoptó el
diseño anidado.

La carga del Paso 3 usa la misma envolvente para todas las viviendas, así que solo depende del área, los pisos de la
unidad, la altura y la posición; la época, el tipo, la propiedad horizontal y el estrato no entran en ella. Por eso el
R² solo premia las divisiones por tamaño y pisos, y los arquetipos son clases geométricas: la diversidad de la
envolvente entra por los priors del Paso 6, no por los arquetipos. Del mismo modo, lo que mide el estrato dentro de los
grupos son diferencias de geometría entre estratos.

La diferencia entre las dos medidas tiene una causa clara: la varianza de la carga por vivienda la dominan muy pocas
viviendas grandes (las de 300 m² o más son el 1,8 % de la ciudad y aportan el 37 % de la varianza), y por eso esa
solución separa sobre todo tamaños. Con la carga por m², los arquetipos quedan definidos por la posición y el bloque.
Qué medida conviene depende de cómo tome el área la simulación de la Fase 2, y los arquetipos deben seguir el uso que
se les dé {cite:p}`pasichnyi2019`.

```{figure} arquetipos/salidas/figuras/agr_r2_k.png
:name: fig-arq-r2-k
:width: 100%
Varianza de la carga explicada según el número de arquetipos, en el diseño plano (agrupamiento dentro de cada posición). Los puntos marcan el número elegido para cada algoritmo; el cuadrado gris, la tipología por reglas.
```

```{figure} arquetipos/salidas/figuras/carga_r2_k.png
:name: fig-arq-cota
:width: 90%
Cota de referencia: varianza explicada por un árbol de regresión con k hojas, frente a las tipologías por reglas.
```

### Arquetipos con la carga por m²

:::{table} Arquetipos de la solución por m². En el código, la letra es la posición (C casa, U último piso, S sin cubierta) y el número, el bloque de estratos. Carga: índice del Paso 3. Techo, fracción climatizada e infiltración: media del prior del Paso 6. A/C: hogares con aire acondicionado en la ECV 2024, por la composición de estratos del arquetipo.
:name: tab-arq-m2
:class: tabla-compacta

| Arquetipo | Viviendas (% de la ciudad) | Área mediana, m² (P25–P75) | Carga mediana, kWh/m²·año | Techo de concreto | Fracción climatizada | Infiltración, ren/h | Hogares con A/C |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C12-1 | 119.477 (35,9 %) | 69 (51–96) | 522 | 18 % | 0,18 | 2,07 | 22 % |
| C12-2 | 9.168 (2,8 %) | 104 (65–140) | 382 | 18 % | 0,14 | 2,11 | 26 % |
| C34-1 | 48.436 (14,6 %) | 116 (85–160) | 499 | 26 % | 0,11 | 1,98 | 53 % |
| C56-1 | 4.223 (1,3 %) | 213 (153–304) | 389 | 72 % | 0,90 | 1,34 | 87 % |
| S12-1 | 39.976 (12,0 %) | 46 (42–56) | 236 | no expuesto | 0,23 | 0,96 | 16 % |
| S34-1 | 57.711 (17,4 %) | 68 (53–86) | 219 | no expuesto | 0,31 | 0,97 | 64 % |
| S56-1 | 21.742 (6,5 %) | 117 (85–161) | 199 | no expuesto | 0,90 | 0,95 | 90 % |
| U12-1 | 12.857 (3,9 %) | 53 (42–100) | 533 | 71 % | 0,18 | 1,36 | 21 % |
| U34-1 | 15.043 (4,5 %) | 80 (61–110) | 514 | 86 % | 0,26 | 1,15 | 61 % |
| U56-1 | 4.085 (1,2 %) | 122 (92–190) | 497 | 98 % | 0,90 | 0,97 | 88 % |
:::

C12-2 agrupa las casas de estratos 1 y 2 de dos pisos o más. Las viviendas con techo expuesto (casa y último piso)
tienen más del doble de carga por m² que las que tienen otra vivienda encima.

### Arquetipos con la carga por vivienda

:::{table} Arquetipos de la solución por vivienda. Carga: índice del Paso 3 por vivienda. Los priors de envolvente y los atributos del hogar están en las fichas.
:name: tab-arq-vivienda
:class: tabla-compacta

| Arquetipo | Posición | Estratos | Viviendas (% de la ciudad) | Área mediana, m² (P25–P75) | Pisos de la unidad | Carga mediana, MWh/año |
| --- | --- | --- | --- | --- | --- | --- |
| C12-1 | Casa | 1-2 | 28.065 (8,4 %) | 38 (30–44) | 1 | 21,0 |
| C12-2 | Casa | 1-2 | 58.631 (17,6 %) | 67 (60–78) | 1 | 35,1 |
| C12-3 | Casa | 1-2 | 9.168 (2,8 %) | 104 (65–140) | 2 | 39,8 |
| C12-4 | Casa | 1-2 | 32.781 (9,8 %) | 119 (104–146) | 1 | 59,8 |
| C34-1 | Casa | 3-4 | 10.929 (3,3 %) | 64 (48–76) | 1 | 33,6 |
| C34-2 | Casa | 3-4 | 18.914 (5,7 %) | 117 (102–135) | 1 | 58,8 |
| C34-3 | Casa | 3-4 | 8.526 (2,6 %) | 120 (94–185) | 2 | 44,8 |
| C34-4 | Casa | 3-4 | 10.067 (3,0 %) | 194 (172–240) | 1 | 94,7 |
| C56-1 | Casa | 5-6 | 4.223 (1,3 %) | 213 (153–304) | 2 | 91,0 |
| S12-1 | Sin cubierta | 1-2 | 39.976 (12,0 %) | 46 (42–56) | 1 | 10,8 |
| S34-1 | Sin cubierta | 3-4 | 57.711 (17,4 %) | 68 (53–86) | 1 | 14,9 |
| S56-1 | Sin cubierta | 5-6 | 21.742 (6,5 %) | 117 (85–161) | 1 | 23,4 |
| U12-1 | Último piso | 1-2 | 12.857 (3,9 %) | 53 (42–100) | 1 | 27,8 |
| U34-1 | Último piso | 3-4 | 15.043 (4,5 %) | 80 (61–110) | 1 | 39,4 |
| U56-1 | Último piso | 5-6 | 4.085 (1,2 %) | 122 (92–190) | 1 | 57,4 |
:::

### Variante con más variables del catastro

Además de las seis variables de la propuesta, el catastro trae el número de habitaciones y de baños, el área del
terreno y la condición de vivienda de interés social o prioritario. Se repitió el agrupamiento completo con esas cuatro
variables agregadas (las tres primeras en logaritmo), con la misma submuestra y las mismas reglas. La regla que
descarta las variables casi constantes deja la condición de VIS o VIP solo en las viviendas sin cubierta y de último
piso de los estratos 1 y 2: en los demás estratos, menos del 1 % de los edificios de la submuestra son VIS o VIP. La destinación y el
tipo de planta son constantes, la altura de piso vale 3,0 m en el 99,7 % de las viviendas, y la ubicación queda fuera
porque el arquetipo describe la vivienda y no su lugar. La regla para elegir entre las dos variantes se fijó antes de
correr la nueva: entre las soluciones estables, la de mayor R² de la carga; con un empate de menos de 0,02, la de menos
grupos.

:::{table} Soluciones con seis variables (las finales) y con diez, en el diseño anidado. Grupos de casas: número de arquetipos de casa en los bloques 1-2, 3-4 y 5-6. La silueta no está definida cuando cada posición y bloque queda en un solo grupo. Concordancia: índice de Rand ajustado entre las dos asignaciones, sobre todas las viviendas.
:name: tab-arq-ampliada
:class: tabla-compacta

| Carga | Variables | Algoritmo | Arquetipos | Grupos de casas | R² | Jaccard ponderado | Silueta | Concordancia |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Por vivienda | Seis (final) | k-prototypes | 15 | 4, 4 y 1 | 0,63 | 0,98 | 0,16 | |
| Por vivienda | Diez | K-Means | 11 | 2, 2 y 1 | 0,51 | 0,98 | 0,23 | 0,66 |
| Por m² | Seis (final) | K-Means | 10 | 2, 1 y 1 | 0,93 | 1,00 | 0,51 | |
| Por m² | Diez | K-Means | 9 | 1, 1 y 1 | 0,90 | 1,00 | no definida | 0,94 |
:::

Las dos variantes son estables y la de seis variables explica más varianza en las dos medidas, así que sigue siendo
la solución final y los arquetipos no cambian. La carga del Paso 3 depende solo de la geometría (área y pisos) y de la
posición, y las variables agregadas no entran en ella. Con diez variables la distancia reparte su peso entre ellas:
por vivienda, las casas de los estratos 1 a 4 se dividen solo en pequeñas y grandes, y ningún grupo adicional sube el R² en
0,02; por m², las casas de los estratos 1 y 2 de dos pisos o más ya no se separan de las de un piso. Con este
criterio, una variable que no entra en la carga no puede subir el R², así que el resultado no dice si las habitaciones
o los baños importan para la ocupación o los equipos de la Fase 2.

## Dónde están los arquetipos

Los mapas agregan las 322.418 viviendas con coordenadas en celdas de unos 275 m y muestran, para cada arquetipo, qué
parte de las viviendas de cada celda pertenece a él ({numref}`fig-arq-mapa-vivienda` y {numref}`fig-arq-mapa-m2`). Solo
se dibujan las celdas con 10 viviendas o más, y ninguna vivienda individual. La geografía de los arquetipos sigue sobre
todo la del estrato, porque el bloque de estratos es parte de cada uno: las casas de los estratos 1 y 2 ocupan el sur,
las de 3-4 una franja central que sube hacia el norte y los arquetipos de 5-6 el norte. Dentro de cada bloque se ven
patrones propios de los arquetipos, como los focos al occidente y al sur donde casi todas las viviendas son
apartamentos sin cubierta de los estratos 1 y 2 (S12-1), o las casas de dos pisos de 1-2 (C12-3), repartidas por todo
el sur con poca participación en cada celda.

```{figure} arquetipos/salidas/figuras/mapa_arquetipos_por_vivienda.png
:name: fig-arq-mapa-vivienda
:width: 100%
Arquetipos de la solución por vivienda. Cada panel muestra la fracción de las viviendas de cada celda (0,0025°, unos 275 m) que pertenece al arquetipo. En gris, las celdas sin viviendas del arquetipo. Bajo el código, el área mediana, los pisos de la unidad y la fracción de las viviendas de la ciudad.
```

```{figure} arquetipos/salidas/figuras/mapa_arquetipos_por_m2.png
:name: fig-arq-mapa-m2
:width: 85%
Arquetipos de la solución por m², con la misma construcción.
```

## Robustez frente a la submuestra

El agrupamiento se ajustó con 10.293 edificios, que en las casas son el 2,6 % de los 155.158. Para medir cuánto
dependen los arquetipos de esa submuestra, la solución final de cada medida se volvió a ajustar con una vivienda al azar
de cada uno de los 177.093 edificios, con el mismo algoritmo, las mismas variables y la regla de la Nota 3 para el
número de grupos (script 14, análisis A10, ajuste AJ27). DBSCAN y la silueta no se repiten, porque necesitan la
distancia de Gower entre todos los pares de edificios, unos 96 GB solo en las casas.

:::{table} La solución final ajustada con la submuestra y con todos los edificios. Con el mismo número de grupos, los grupos del ajuste completo se emparejan con los arquetipos finales por el método húngaro.
:name: tab-arq-todos
:class: tabla-compacta

| | Carga por vivienda | Carga por m² |
| --- | --- | --- |
| Arquetipos con la regla de la Nota 3 (submuestra → todos) | 15 → 16 | 10 → 10 |
| Viviendas que conservan su arquetipo con el mismo número de grupos | 94,8 % | 100 % |
| Casas de 1-2 y de 3-4 que lo conservan | 88,7 % y 94,4 % | 100 % y 100 % |
| R² de la carga con el mismo número de grupos (submuestra → todos) | 0,630 → 0,620 | 0,926 → 0,926 |
:::

Con la carga por m² los arquetipos son los mismos. Con la carga por vivienda solo cambian casas, porque las demás
posiciones tienen un arquetipo por bloque, y las que cambian pasan a un grupo vecino por tamaño
({numref}`fig-arq-mapa-cambios`). La parte menos firme es el número de grupos de las casas de los estratos 3-4, que con
todos los edificios se dividen en 5 y no en 4, y que también concentran la incertidumbre de la asignación. La submuestra no empeora
el criterio del Paso 3, porque con ella el R² es algo mayor.

```{figure} arquetipos/salidas/figuras/mapa_cambios_todos_edificios.png
:name: fig-arq-mapa-cambios
:width: 60%
Casas que cambian de arquetipo en la solución por vivienda al ajustar con todos los edificios. En la solución por m² no cambia ninguna.
```

(sec-arq-verificacion)=
## Verificación y correcciones

Antes de usar los resultados se revisó el código de forma independiente y se agregó un script de comprobaciones
automáticas (script 16) que contrasta 43 propiedades de las salidas. Entre ellas están que cada vivienda tenga un
arquetipo y uno solo, que las tablas sumen las 332.718 viviendas, que los R² publicados se reproduzcan desde las bases,
que el código de cada arquetipo coincida con la posición y el bloque de sus viviendas y que el ajuste con la submuestra
reproduzca la solución final. La revisión encontró tres errores de implementación, que se corrigieron antes de volver a
correr la Fase 1 completa con las mismas reglas y la misma semilla (preregistro, Nota 11; ajuste AJ28):

1. La posición frente a la cubierta se calculaba dentro del predio matriz y no dentro de cada torre, así que el último
   piso de una torre más baja que otra del mismo conjunto quedaba como sin cubierta. Con la corrección, 2.088
   viviendas pasan de sin cubierta a último piso y 252 a casa.
2. La incertidumbre de la asignación emparejaba los grupos de cada reajuste con los arquetipos por el método húngaro,
   que asigna todos los grupos aunque no compartan ninguna vivienda, y daba probabilidades falsas de hasta 0,31 entre
   casas de tamaños muy distintos. Ahora cada grupo toma el arquetipo con el que comparte más puntos de ajuste, y la
   mayor probabilidad media de caer en otro arquetipo es 0,06.
3. En la variante con diez variables, las tres numéricas agregadas entraban también como categóricas en
   k-prototypes. No afectaba la solución final.

Además se calculan la V de Cramér entre los grupos del diseño plano y el estrato (0,26 por vivienda y 0,28 por m²) y el
η² del estrato dentro de cada grupo, que el preregistro pedía reportar. Con la nueva corrida, la solución por m² no
cambia. La solución por vivienda pasa de 17 a 15 arquetipos y su R² de 0,66 a 0,63, porque las casas de los estratos
3-4 quedan en 4 grupos y no en 6. El paso de 16 a 17 estaba justo en el umbral (subía el R² en 0,0205), y la nueva
submuestra, que cambia porque cambió el conjunto de casas, no lo alcanza (limitación 8). Las 43 comprobaciones se
cumplen.

## Priors de envolvente

El techo pesa sobre todo en las casas de los estratos 1 a 4, donde predomina el asbesto-cemento
({numref}`fig-arq-techo`). En el último piso de los multifamiliares el techo se toma como losa de concreto, y en los
de baja altura, con el reparto de los apartamentos de la ECV.

```{figure} arquetipos/salidas/figuras/env_techo_ecv.png
:name: fig-arq-techo
:width: 100%
Material del techo según la ECV 2019 y 2024, por tipo de vivienda y bloque de estratos. El prior usa solo la ola 2024.
```

:::{table} Transmitancia del techo por material (W/m²K), según la ISO 6946. Moda: flujo de calor hacia abajo y sin cielo raso; mínimo: con cielo raso (techos livianos) o losa gruesa; máximo: flujo hacia arriba.
:name: tab-arq-u-techo

| Techo | Mínimo | Moda | Máximo | CEELA |
| --- | --- | --- | --- | --- |
| Concreto | 3,33 | 3,51 | 4,88 | 3,6 |
| Asbesto-cemento | 2,07 | 4,50 | 6,58 | 6,6 |
| Metálica o zinc | 2,13 | 4,76 | 7,14 | |
| Otro | 2,06 | 4,44 | 6,45 | |
:::

Los muros de mampostería van de 1,9 a 4,1 W/m²K, el rango de los edificios de CEELA. La infiltración con las ventanas
cerradas tiene una mediana de 0,9 renovaciones por hora (de 0,5 a 1,6) en la construcción con losa encima y de 2,0 (de
0,8 a 5,0) en la de techo liviano o paredes de otro material. El color de los techos, la relación ventana-muro ampliada
para la vivienda antigua e informal, la sombra y el área de una habitación son supuestos con rango: el análisis de
Morris de la Fase 2 dirá cuáles importan. La tabla completa, con la fuente de cada valor, está en
[`env_priors_por_vivienda.csv`](https://github.com/mcarocantillo/tesis-datos-barranquilla/blob/main/arquetipos/salidas/tablas/env_priors_por_vivienda.csv)
y [`env_priors_por_m2.csv`](https://github.com/mcarocantillo/tesis-datos-barranquilla/blob/main/arquetipos/salidas/tablas/env_priors_por_m2.csv).

## Validación

```{figure} arquetipos/salidas/figuras/val_representatividad.png
:name: fig-arq-representatividad
:width: 100%
Catastro frente a la ECV 2024: viviendas por estrato, fracción de casas por bloque y habitaciones (catastro) frente a dormitorios (ECV), con el intervalo del 95 % de la ECV.
```

- **Viviendas por estrato:** las seis cifras del catastro caen dentro del intervalo de la ECV.
- **Fracción de casas:** el catastro tiene 71 % de casas en los estratos 1 y 2 y la ECV, 40 %; en 3 y 4, 40 % frente a
  27 %. Muchas viviendas que el catastro registra como casa se declaran apartamento en la ECV, así que el puente entre
  la posición y el tipo de vivienda de la ECV es aproximado. La sensibilidad de la Fase 2 lo trata como un factor: hasta
  el 44 % de las casas de los estratos 1-2 y el 31 % de las de 3-4 pueden tomar los materiales de los apartamentos.
- **Habitaciones:** el catastro da entre 0,5 y 1,1 habitaciones más que los dormitorios de la ECV en todos los estratos.
  Por eso, la fracción climatizada de los apartamentos de 3-4, que según CEELA climatizan «las habitaciones», usa el
  número del catastro llevado a los dormitorios de la ECV.
- **Sensibilidad a las variables:** al repetir el agrupamiento sin cada variable, la asignación por vivienda cambia
  sobre todo sin el área (índice de Rand ajustado de 0,65 frente a la solución final) y la de por m², sin el número de
  pisos de la unidad (0,74). Los arquetipos con un solo grupo en su posición y bloque no dependen de las variables de
  agrupamiento.
- **Asignación:** el árbol reproduce la regla de asignación en el 99,7 % de las viviendas en la solución por vivienda y
  en el 100 % en la de por m². No es una prueba de generalización, porque el arquetipo es función de los mismos atributos. La incertidumbre que pasa a
  la Fase 2 sale de repetir el agrupamiento en las 100 submuestras de la prueba de estabilidad. En la solución por m²,
  cada vivienda cae casi siempre en su arquetipo. En la solución por vivienda, la probabilidad media de caer en el
  propio arquetipo es de 0,96 o más en las casas de los estratos 1-2, y la incertidumbre se concentra en las casas de
  3-4: las de C34-1 (casas pequeñas) caen en su arquetipo con probabilidad media de 0,94 y si no, en C34-2, y el 9 % de
  ellas queda por debajo de 0,8.

## Limitaciones

1. La ECV no permite ubicar a sus hogares en los arquetipos (no trae área ni pisos). Los materiales y los atributos del
   hogar se asignan por bloque de estratos y por casa o apartamento, de modo que los arquetipos de una misma posición y
   bloque comparten esos priors.
2. Las casas de los estratos 5 y 6 tienen solo 15 viviendas en la ECV 2024, así que su prior de materiales es muy
   incierto.
3. No hay mediciones de infiltración ni del color de los techos en Barranquilla; los dos son supuestos con rango.
4. El año de construcción del catastro se usa como época, aunque su significado no está documentado. El 11,6 % de las
   viviendas tiene el año 1986, que es el 69 % de la época «antes de 1990», y hay otros picos en 2014 y 2022, así que el
   campo parece registrar el año de inscripción en el catastro más que el de construcción. Si es así, la época indica
   cuándo existía ya la vivienda, y «antes de 1990» sigue siendo correcta para las de 1986.
5. Usar solo la ola 2024 de la ECV depende de suponer para 2019 un efecto de diseño de 1,5; con el de cada material la
   prueba del techo no rechaza. Con las dos olas, el techo de concreto de las casas de los estratos 1 y 2 baja de 18 % a
   10 %, así que la elección de olas entra como factor en la sensibilidad de la Fase 2.
6. La carga usa la irradiancia de ERA5 (0,25°) porque la copia de Open-Meteo no trae la de ERA5-Land (supuesto S17).
   Con ERA5-Land completo de GDEX, la carga media sube 4,4 %, pero el R² de los arquetipos casi no cambia (0,629 por
   vivienda y 0,926 por m²; AJ24, script 11): el clima mueve el nivel de la carga, no las diferencias entre viviendas.
7. Algunas reglas cambiaron después de ver resultados de prueba o completos (preregistro, Notas 3 a 6). Cada cambio
   está registrado con su motivo, y el resultado con la regla original se reporta aparte: con la regla original de
   elección del algoritmo habría 9 arquetipos por vivienda, con un R² de 0,40.
8. El número de arquetipos de casas por vivienda depende de la submuestra. Con la submuestra anterior a las
   correcciones, el paso de 16 a 17 arquetipos subía el R² en 0,0205 y la regla daba 17. Con la actual sube 0,013 y da
   15, y con todos los edificios da 16. Lo firme es la estructura, con cuatro tamaños de casa en los estratos 1-2 y un
   solo arquetipo por bloque en las demás posiciones, mientras que las casas de 3-4 quedan en 4 a 6 grupos según la
   muestra.
9. Hay 8.753 viviendas sin cubierta sin ninguna unidad de su torre que empiece encima de ellas: 3.364 de S12-1, 3.737 de
   S34-1 y 1.652 de S56-1, entre el 6 y el 8 % de cada arquetipo. Su techo lo fija una unidad de la torre con más
   pisos, y sin la geometría de las construcciones no se sabe si está encima o al lado. En algunos multifamiliares
   `total_plantas` parece ser el número de pisos del edificio y no el de la unidad. Si alguna de ellas tiene el techo
   expuesto, su carga está subestimada.

## Archivos

Todo está en la carpeta [`arquetipos/`](https://github.com/mcarocantillo/tesis-datos-barranquilla/tree/main/arquetipos):
el preregistro y el registro de ajustes frente a la propuesta, los scripts 01 a 16, las tablas agregadas, las figuras,
las fichas de los arquetipos de cada solución (`salidas/fichas/`) y los árboles de asignación (`salidas/modelos/`). La
asignación de cada vivienda a su arquetipo y las cargas por vivienda no se publican.
