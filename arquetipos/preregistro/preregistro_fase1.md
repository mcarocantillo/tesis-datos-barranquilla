# Preregistro de la Fase 1: arquetipos de vivienda

**Versión 1 · 29 de octubre de 2026.** Escrito antes de calcular cualquier carga de enfriamiento y antes de correr
cualquier agrupamiento. Las cifras de este documento son conteos del catastro, no resultados de los criterios que
aquí se fijan. Cualquier cambio posterior se agrega como una versión nueva, con fecha y motivo, sin borrar esta.
Los valores en formato máquina están en `decision_fase1.json`.

**Base.** Propuesta de tesis, versión del 28 de octubre de 2026 (`Propuesta_de_Tesis_Maria_Cantillo_Orozco.pdf`),
sección 7.2, Pasos 1 a 7. Semilla 42 en todo el trabajo.

## 1. Datos y variables

- **Unidad:** la vivienda. Base: las 332.718 viviendas residenciales con estrato del catastro (Paso 1, ya hecho).
- **Edificio:** el predio matriz (`npn_edificio`, los primeros 22 dígitos del número predial); 168.044 edificios.
- **Posición frente a la cubierta.** Una unidad ocupa los pisos de `planta_ubicacion` a
  `planta_ubicacion + total_plantas − 1`; el techo del edificio es el piso más alto ocupado por sus unidades.
  - *Casa:* empieza en el primer piso y llega al techo.
  - *Último piso:* empieza por encima del primero y llega al techo.
  - *Sin cubierta:* no llega al techo (apartamento intermedio o primer piso con vivienda encima).

  La propuesta nombra tres posiciones (casa, último piso, intermedio). El primer piso con vivienda encima se une al
  intermedio porque, como él, no recibe la ganancia del techo, que es lo que motiva la variable.
  Sin dato de piso (351 viviendas): casa si el uso es de vivienda hasta 3 pisos y no está en propiedad horizontal;
  sin cubierta en los demás casos.
- **Tipo de vivienda.** Baja altura (uso «Vivienda hasta 3 pisos», con o sin PH, y recreacional) o multifamiliar
  (uso «Apartamentos 4 y más pisos»), que corresponde a la unifamiliar y la multifamiliar de CEELA. No se usa la
  clasificación VIS, VIP o no VIS porque el 79 % de las viviendas tiene «No Aplica»; se conserva como atributo
  descriptivo de las fichas. En un multifamiliar, una unidad clasificada como casa se trata como último piso.
- **Época.** El año del catastro se trata como año de registro catastral (supuesto S13) y se usa en tres épocas:
  antes de 1990, 1990–2009 y 2010 en adelante. Sin época: los años faltantes y los lotes de apartamentos de 4 o más
  pisos de los estratos 1 y 2 cuya mediana de año es anterior a 1975 (S13).
- **Bloque de estratos:** 1–2, 3–4 y 5–6.

## 2. Tipología por reglas (referencia del Paso 4)

- **Celdas:** tipo × posición × época × bloque de estratos. En baja altura hay tres posiciones y en multifamiliar
  dos, así que hay como máximo (3 + 2) × 3 × 3 = 45 celdas.
- **Viviendas sin época:** se asignan a la época con más viviendas de su misma combinación de tipo, posición y
  bloque.
- **Tamaño mínimo de una celda:** al menos el 1 % de las viviendas (3.328) y al menos 30 edificios. Las celdas que
  no lo cumplen se fusionan en este orden, y cada etapa se aplica solo a las que siguen sin cumplirlo:
  1. se juntan todas las épocas de esa combinación de tipo, posición y bloque;
  2. se une el bloque de estratos con el bloque vecino (1–2 y 5–6 con 3–4; 3–4 con el vecino de más viviendas),
     dentro del mismo tipo y posición;
  3. se juntan los dos tipos de vivienda dentro de la misma posición y bloque.

  La época va primero porque es la variable con el significado menos seguro (S13); la posición nunca se fusiona,
  porque define los arquetipos.

## 3. Carga simplificada para elegir el número de arquetipos (Paso 3)

**Qué es.** La carga anual de enfriamiento de cada vivienda con una envolvente común para todas. Por construcción,
la carga depende solo de la geometría y la posición; no es una estimación del consumo real.

**Ecuación** (régimen permanente horario, suma de grados-hora positivos, consigna $T_c$):

$$
Q = \sum_h \Big[ U_t A_t\,(T_{sa,t}-T_c)^+ + U_m A_m\,(T_{sa,m}-T_c)^+ + U_v A_v\,(T-T_c)^+
 + \dot m\,c_p\,(T-T_c)^+ + \dot m\,h_{fg}\,(w-w_c)^+ \Big]
$$

- Sol-aire en la cubierta: $T_{sa,t} = T + \alpha I_h / h_o - 3{,}9$ K (corrección de onda larga para superficies
  horizontales, ASHRAE). En los muros: $T_{sa,m} = T + \alpha\, f_v I_h / h_o$.
- Infiltración: $\dot m = \rho\, n\, V / 3600$; humedad específica exterior $w$ calculada con el punto de rocío;
  $w_c$, la de la consigna.

**Geometría supuesta** (igual regla para todas las viviendas):

| Elemento | Regla |
| --- | --- |
| Área de planta | área construida ÷ número de plantas de la unidad |
| Cubierta expuesta $A_t$ | el área de planta si la vivienda es casa o último piso; 0 si no tiene cubierta |
| Muro bruto | perímetro de un cuadrado de igual área de planta × fracción expuesta × altura de piso × plantas |
| Ventana $A_v$ y muro opaco $A_m$ | relación ventana-muro × muro bruto, y el resto |
| Volumen $V$ | área construida × altura de piso |

**Valores comunes:**

| Parámetro | Valor | Base |
| --- | --- | --- |
| $U_t$ cubierta | 4,0 W/m²K | centro del rango de CEELA para Barranquilla (3,6–6,6) |
| $U_m$ muro | 2,7 W/m²K | centro del rango de CEELA (1,9–4,1) |
| $U_v$ vidrio | 5,88 W/m²K | vidrio simple, CEELA |
| Absortancia α | 0,7 | valor genérico, igual en cubierta y muros |
| $h_o$ | 17 W/m²K | coeficiente exterior de diseño, ASHRAE |
| $f_v$ (irradiancia sobre muros ÷ horizontal) | 0,5 | supuesto; sensibilidad de 0,3 a 0,7 |
| Fracción del perímetro expuesta | 0,5 | viviendas adosadas (CEELA); supuesto |
| Relación ventana-muro | 0,25 | centro del rango de CEELA (20–40 %) |
| Altura de piso | campo `altura` del catastro (≈ 3 m), limitado a 2,4–4,0 m | catastro |
| Renovaciones de aire $n$ | 1,0 h⁻¹ | supuesto genérico |
| Consigna $T_c$ y humedad | 26,5 °C y 60 % | CEELA (consigna); humedad, supuesto |
| Clima | ERA5-Land horario 2015–2025 (copia de Open-Meteo), promedio de los 11 años | repositorio de datos |

Como la envolvente es común, la carga es una combinación lineal de cuatro magnitudes geométricas: cubierta, muro,
ventana y volumen. El clima solo fija los cuatro coeficientes.

**Criterio de selección.** R² es la fracción de la varianza de la carga entre viviendas que explican los grupos,
calculada sobre todas las viviendas. Se recorren k = 2, 3, …, y se elige el primer k tal que pasar a k + 1 aumenta
R² en menos de 0,02. No hay un máximo de k.

## 4. Plano frente a anidado (Paso 4)

Se adopta el diseño **anidado** si se cumple al menos una de estas condiciones; si no se cumple ninguna, el
**plano**:

1. **El plano es inestable:** algún grupo con más del 5 % de las viviendas tiene un Jaccard medio menor de 0,6, o el
   Jaccard medio ponderado por viviendas es menor de 0,75.
2. **El estrato aporta por sí mismo:** η² ≥ 0,06, donde η² es la fracción de la varianza de la carga *dentro de los
   grupos* que explica el estrato (1 a 6), calculada en conjunto para todos los grupos:
   η² = (SC dentro de los grupos − SC dentro de grupo × estrato) / SC dentro de los grupos.
   El η² de cada grupo se reporta, pero no decide.

La V de Cramér con corrección de sesgo se reporta y no decide. El diseño no elegido se conserva para el análisis de
sensibilidad de la Fase 3. La tipología por reglas se compara con ambos diseños por su R² al mismo número de grupos.

## 5. Análisis complementarios (no intervienen en ninguna decisión)

- **A1.** Para cada k: silueta, Calinski-Harabasz y Davies-Bouldin.
- **A2.** Un árbol de regresión sobre la carga, con k hojas, como cota de referencia del R² alcanzable con k grupos.
- **A3.** El mismo criterio de R² con la carga por metro cuadrado, para comprobar que el número de arquetipos no lo
  decide solo el tamaño.
- **A4.** Sensibilidad de la carga a $f_v$ (0,3 y 0,7) y a $n$ (0,5 y 2,0 h⁻¹).

## Nota 1 (29-oct-2026, antes de calcular la carga)

La copia de Open-Meteo trae temperatura y punto de rocío de ERA5-Land, pero no su radiación (todas las horas
vacías). La irradiancia horizontal se toma de ERA5 (0,25°) en el mismo archivo, como ya registra el supuesto S17
del repositorio de datos. Constantes físicas usadas: ρ = 1,2 kg/m³, $c_p$ = 1.006 J/kg·K,
$h_{fg}$ = 2,45 MJ/kg y presión de 101,325 kPa.

## Nota 2 (2-nov-2026): variante de las reglas con clases de tamaño

**Cuándo y por qué.** Escrita *después* de ver que la tipología por reglas explica el 41 % de la varianza de la carga
por vivienda (91 % por m²) y que un árbol de regresión parte primero por área. Por eso la variante es solo un
análisis de **sensibilidad**: no reemplaza a la tipología de la Sección 2, no interviene en la regla del Paso 4 y no
cambia el criterio del Paso 3, que sigue siendo la carga por vivienda.

**Clases de tamaño.** Terciles del área construida de las 332.718 viviendas: pequeña (< 59 m²), mediana
(59 a < 95 m²) y grande (≥ 95 m²). Se usan los terciles y no los cortes que encontró el árbol (124, 287 y 472 m²)
para no ajustar la variante al resultado.

**Celdas y fusión.** Tipo × posición × época × tamaño × bloque de estratos, con el mismo tamaño mínimo de la
Sección 2. Orden de fusión:
1. se juntan todas las épocas de la combinación;
2. se une la clase de tamaño con la adyacente de más viviendas (pequeña y grande con mediana), repitiendo mientras
   la celda no cumpla y quede una clase adyacente;
3. se une el bloque de estratos con el vecino, una sola vez;
4. se juntan los dos tipos.

El tamaño se fusiona antes que el bloque porque el bloque y el tipo son variables de la propuesta y el tamaño no.

**Aclaración que vale para ambas tipologías.** Cuando una celda se une con su vecina (por tamaño, bloque o tipo), la
unión toma todas las épocas de ambas y la celda resultante queda con «todas las épocas». En la tipología de la
Sección 2 esto no cambia nada, porque todas sus uniones fueron entre celdas que ya tenían todas las épocas.

## 6. Pendiente para una versión 2 de este preregistro (antes de correr el Paso 2)

Tamaño y diseño de la submuestra de edificios, la forma de tratar la posición en los algoritmos (como variable o
como estrato), la preparación de las variables para cada algoritmo, el rango de k explorado y el procedimiento de
las 100 submuestras para Jaccard. *Resuelto en la versión 2 (Sección 7).*

---

# Versión 2 · 2 de noviembre de 2026: agrupamiento del Paso 2

Escrita antes de correr cualquier agrupamiento. Lo único que se miró de los datos fue el número de edificios y
viviendas por posición, tipo y bloque de estratos, para dimensionar la submuestra.

## 7.1 La posición como estrato

La propuesta dice que la posición frente a la cubierta «formará parte de la definición de los arquetipos y no será
solo una variable más». Por eso los algoritmos se corren **por separado dentro de cada posición** (casa, último piso,
sin cubierta): ningún grupo mezcla viviendas con y sin techo expuesto. El número mínimo de arquetipos es 3.

## 7.2 Submuestra

- **Unidad:** dentro de cada posición, cada edificio entra **una vez**, con una de sus viviendas de esa posición
  elegida al azar. Un edificio con apartamentos de último piso e intermedios aporta una vivienda a cada posición.
- **Tamaño:** unos 4.000 edificios en casa, 3.000 en último piso y 3.000 en sin cubierta.
- **Estratificación:** dentro de cada posición, por tipo × bloque de estratos, con asignación proporcional al número
  de edificios y un mínimo de 150 por estrato (o todos, si hay menos). Sin esto, los multifamiliares de estratos 1–2,
  que son 139 a 160 edificios con más de 37.000 viviendas, casi no entrarían.
- La misma submuestra sirve para los tres algoritmos y para los dos diseños (plano y anidado).

## 7.3 Variables y preparación

Las de la propuesta: área construida, número de pisos de la construcción (`total_plantas`), piso de la unidad
(`planta_ubicacion`), antigüedad (las tres épocas de la Sección 1), tipo de vivienda y propiedad horizontal. Dentro de
cada posición se descarta la variable cuyo valor más frecuente cubra el 99 % o más de la submuestra (por ejemplo, el
tipo en las casas, que son todas de baja altura). Faltantes: época con la regla de la Sección 2; piso de la unidad y
número de pisos, con la mediana de la posición. Los factores de forma urbana, opcionales en la propuesta, no entran en
esta versión.

| Algoritmo | Preparación |
| --- | --- |
| K-Means | Área, pisos y piso de la unidad en logaritmo; época ordinal (0, 1, 2); tipo y PH binarias; todas estandarizadas dentro de la posición. k-means++, 20 arranques. |
| k-prototypes | Numéricas: área, pisos y piso de la unidad en logaritmo y estandarizadas. Categóricas: época, tipo y PH. Peso γ = 0,5 × desviación media de las numéricas (valor de Huang). 10 arranques. |
| Jerárquico con Gower | Distancia de Gower con el área, los pisos y el piso de la unidad en logaritmo, la época como ordinal y tipo y PH como nominales, todas con el mismo peso. Enlace promedio (UPGMA), porque Ward exige distancia euclidiana. |

Semilla 42 en todos.

## 7.4 Atípicos (DBSCAN)

Dentro de cada posición, sobre la distancia de Gower de la submuestra: `min_samples` = 2 × número de variables usadas,
y ε en el codo de la curva ordenada de distancias al vecino `min_samples` (el punto más alejado de la recta que une sus
extremos). Los puntos marcados como ruido no entran en el ajuste de los tres algoritmos, se asignan después a su grupo
más cercano y se reportan con su perfil.

## 7.5 Asignación de todas las viviendas y R²

Para calcular el R² del Paso 3 sobre las 332.718 viviendas, cada vivienda se asigna dentro de su posición al centroide
más cercano (K-Means), al prototipo más cercano (k-prototypes) o al medoide más cercano por Gower (jerárquico). Esta
asignación sirve solo para elegir k y comparar algoritmos; la asignación definitiva es la del Paso 5.

## 7.6 Número de grupos

Para cada posición p y cada algoritmo se calculan las soluciones con k_p = 1, …, 8. Se parte de una solución con un
grupo por posición (k = 3), y en cada paso se agrega un grupo en la posición donde más aumenta el R² de la ciudad. Se
detiene cuando el mayor aumento posible es menor de 0,02 (criterio de la Sección 3).

El k se calcula con dos medidas de carga, y se aplica la que corresponda a la decisión del director (ajuste AJ5 de
`ajustes_frente_a_la_propuesta.md`):
- **Carga por vivienda**, la de la propuesta: es la que se aplica si el director no aprueba el cambio.
- **Carga por m²**, si el director aprueba la opción 2.

Las dos se reportan siempre.

## 7.7 Estabilidad (Jaccard) y elección del algoritmo

- **Jaccard:** 100 submuestras del 80 % de los edificios de la submuestra base, sin reemplazo, dentro de cada
  posición. En cada una se vuelve a agrupar con el mismo k_p. Para cada grupo original, su Jaccard es el máximo
  |A ∩ B| / |A ∪ B| frente a los grupos nuevos, sobre los edificios comunes; se promedia en las 100. El Jaccard medio
  ponderado usa como peso la fracción de viviendas de cada grupo.
- **Algoritmo elegido:** el de mayor Jaccard medio ponderado, cada uno con su propio k. Si el segundo está a menos de
  0,02, decide la silueta con distancia de Gower sobre la submuestra (común a los tres); si vuelven a quedar a menos de
  0,02, decide el R².

## 7.8 Plano frente a anidado (Paso 4)

- **Diseño anidado:** el mismo procedimiento dentro de cada posición × bloque de estratos (9 estratos, k mínimo 9,
  k por estrato de 1 a 6).
- **Decisión:** la regla de la Sección 4, aplicada al diseño plano con el algoritmo elegido. η² se calcula con la
  misma medida de carga que decidió el número de grupos.

## Nota 3 (2-nov-2026): corrección de la regla para elegir el número de grupos

**Cuándo y por qué.** Escrita *después* de una corrida de prueba con el 10 % de la submuestra y 5 submuestras de
Jaccard, hecha solo para revisar el código. Esa prueba mostró que la regla de las Secciones 3 y 7.6 se detiene antes
de tiempo: con soluciones que no están anidadas (K-Means, k-prototypes), el R² no crece de forma pareja. Por ejemplo,
partir las casas en 2 grupos puede aportar menos de 0,02 y partirlas en 3, más de 0,2, porque la primera división
separa por época o propiedad horizontal y la siguiente por tamaño. La regla escrita («el primer k tal que pasar a k + 1
aumenta R² en menos de 0,02») se detiene en la primera ganancia pequeña.

Además, esa regla no es la de la propuesta. La propuesta elige «el número **a partir del cual** un grupo adicional
aumenta en menos de 0,02» la fracción de la varianza explicada; es decir, de ese número en adelante ningún grupo
adicional aporta 0,02. Esta nota corrige la regla para que coincida con el texto de la propuesta. Los resultados de la
prueba no se usan para nada más.

**Regla corregida** (reemplaza la Sección 3, «Criterio de selección», y la Sección 7.6 desde «Se parte de una
solución…»):

1. **Frontera óptima.** Para cada número total de grupos K se toma la combinación de k por estrato (posición, o
   posición × bloque) que da el mayor R² de la ciudad. Como el R² se suma exactamente entre estratos, esa combinación se
   calcula de forma exacta por programación dinámica.
2. **Elección.** K* es el menor K a partir del cual todas las ganancias de la frontera, R²(K + 1) − R²(K), son menores de
   0,02. Si ninguna ganancia llega a 0,02, K* es el número de estratos.
3. **Tope.** Si en la solución elegida algún estrato usa su número máximo de grupos (8 en el plano, 6 en el anidado), su
   máximo se amplía en 4 y se repite, porque la propuesta no fija un máximo. Por seguridad, ningún estrato pasa de 40
   grupos; si se llega ahí, se reporta.

Las demás reglas (Jaccard, elección del algoritmo, regla del Paso 4, análisis complementarios) no cambian.

## Nota 4 (2-nov-2026): corrección de la regla para elegir el algoritmo

**Cuándo y por qué.** Escrita mientras corría el agrupamiento completo y **antes de ver sus resultados**, a partir de
la misma prueba del 10 % de la Nota 3. La regla de la Sección 7.7 (decide el mayor Jaccard) compara la estabilidad de
soluciones con distinto número de grupos, porque cada algoritmo llega a su propio k. Una solución más tosca es casi
siempre más estable. En la prueba, el jerárquico ganaba con un grupo que reunía el 46 % de las viviendas, un Jaccard
de 1,0 y un R² de 0,34, frente a k-prototypes, estable y con R² de 0,74. Elegir así premia las soluciones que casi no
dividen las viviendas, en contra del propósito del Paso 3.

**Regla corregida** (reemplaza «Algoritmo elegido» de la Sección 7.7; vale para los dos diseños y las dos medidas de
carga):

1. **Filtro de estabilidad,** con los umbrales de Hennig de la Sección 4. Una solución es estable si su Jaccard
   medio ponderado es al menos 0,75 y ningún grupo con más del 5 % de las viviendas tiene un Jaccard menor de 0,6.
2. **Entre las estables, decide el R²** de la carga, cada algoritmo con su propio k. Si dos quedan a menos de 0,02, se
   elige la de menos grupos; si tienen los mismos, la de mayor silueta.
3. **Si ninguna es estable,** se elige la de mayor Jaccard ponderado y se reporta que ninguna solución pasó el filtro.

La silueta se reporta y se interpreta, pero solo desempata. La regla del Paso 4 (Sección 4) se aplica a la solución
plana elegida con esta regla.

## 7.9 Análisis complementarios

- **A1:** para cada k del recorrido, silueta (Gower), Calinski-Harabasz y Davies-Bouldin, estos dos sobre la matriz
  estandarizada de K-Means, para los tres algoritmos.
- **A5:** sensibilidad sin excluir los atípicos de DBSCAN.
- **A6** (agregado el 2-nov-2026 con la Nota 4, antes de ver los resultados completos): los arquetipos que daría la
  regla original de la Sección 7.7 (decide el mayor Jaccard), en cada diseño y medida de carga. Se reportan su
  algoritmo, k, R², Jaccard, silueta y la decisión del Paso 4 con esa solución, y la concordancia con la solución de la
  Nota 4, medida con el índice de Rand ajustado sobre todas las viviendas.
- **A9** (agregado el 2-nov-2026 con la Nota 8, antes de correr la variante): si gana la solución de seis variables,
  la variante ampliada del agrupamiento. Se reportan, por medida de carga, su algoritmo, diseño, k por estrato, R²,
  Jaccard y silueta, y la concordancia con la solución de seis variables (índice de Rand ajustado sobre todas las
  viviendas).

Ninguno interviene en las decisiones.

---

# Versión 3 · 2 de noviembre de 2026: asignación de las viviendas (Paso 5)

Escrita antes de entrenar cualquier clasificador. Se aplica a las dos soluciones finales del Paso 2 (carga por
vivienda y carga por m²), porque la medida que aplica depende de la decisión del director (AJ5).

## 8.1 Qué hace el clasificador

- **Etiqueta:** el arquetipo de cada vivienda según la solución final del agrupamiento. Esa asignación sigue siendo el
  arquetipo de la base; el clasificador no la reemplaza.
- **Para qué sirve:** dar reglas legibles (el árbol), asignar registros nuevos del catastro con el mismo criterio y
  entregar probabilidades de asignación para propagar la incertidumbre a la Fase 2.
- **Variables:** las del agrupamiento (área en logaritmo, número de pisos, piso de la unidad, época, tipo de vivienda y
  propiedad horizontal) más la posición frente a la cubierta y el bloque de estratos. **No se usan coordenadas**: el
  arquetipo no depende de la ubicación, y así todas las viviendas, incluidas las 10.300 sin ubicar, se asignan con la
  misma regla, «solo por sus atributos».

## 8.2 Partición y validación

- **Prueba:** los 7 bloques espaciales de 2 km del trabajo previo (65.145 viviendas). Las 10.300 viviendas sin
  coordenadas no entran ni en el entrenamiento ni en la prueba.
- **Validación cruzada:** los 5 pliegues kNNDM del trabajo previo para el escenario «zonas nuevas»: las coordenadas en
  km, el edificio como grupo, el estrato para estratificar y los edificios de prueba, ponderados por viviendas, como
  escenario de predicción. Semilla 42.

## 8.3 Modelos e hiperparámetros

| Modelo | Búsqueda con los pliegues kNNDM | Elección |
| --- | --- | --- |
| Árbol de decisión | profundidad máxima de 2 a 12; hoja mínima de 50 viviendas | la menor profundidad cuyo F1 macro de validación queda a menos de 0,01 del mejor, porque el árbol debe ser legible |
| Random Forest | 300 árboles; `max_features` en {√p, 0,5}; hoja mínima en {1, 20} | el mayor F1 macro de validación |

Sin ponderación de clases, para no distorsionar las probabilidades. Random Forest es el conjunto de mejor desempeño en
el trabajo previo.

## 8.4 Métricas

En la prueba: F1 macro (principal), exactitud, recall por arquetipo, pérdida logarítmica y puntaje de Brier
multiclase, y el rango de cada métrica entre los 7 bloques. Se reporta también la concordancia del clasificador con la
etiqueta en las viviendas sin coordenadas.

## 8.5 Probabilidades para la Fase 2

- **Viviendas de entrenamiento:** probabilidades fuera de muestra con los pliegues kNNDM (cada vivienda la predice un
  modelo que no la vio).
- **Viviendas de prueba y sin coordenadas:** las del modelo entrenado con todo el conjunto de entrenamiento.
- Se usa el conjunto (Random Forest). Por arquetipo se reporta la probabilidad media de pertenencia a su propio
  arquetipo y la fracción de viviendas con probabilidad menor de 0,8.

---

# Versión 4 · 2 de noviembre de 2026: priors de envolvente (Paso 6)

Escrita antes de calcular cualquier proporción de materiales con la ECV. De la ECV solo se miraron la lista de
variables, los códigos que aparecen en Barranquilla y las etiquetas del cuestionario. La única cifra conocida de
antemano es el reparto de techos de la ECV 2024 por grupo de estrato, ya publicado en el trabajo previo. Del catastro
solo se miró la mediana de habitaciones por posición y bloque (de 2 a 3), para comprobar que el campo cuenta
dormitorios.

## 9.1 Datos de la ECV

- **Archivos:** «Datos de la vivienda» de 2019 y 2024. Barranquilla = departamento 08 y municipio 001 (en 2019 el
  municipio viene en el archivo de aplicación de la encuesta). Cabecera y resto, como en el trabajo previo.
- **Unidad y peso:** la vivienda (el capítulo lo responde el hogar 01) con su factor de expansión `FEX_C`.
- **Estrato:** `P8520S1A1` de 1 a 6. Las viviendas con 0, 8, 9 o sin dato se excluyen y se cuentan.
- **Tipo de vivienda (`P1070`):** «casa» (casa, cuarto o cuartos y otro) o «apartamento». La ECV no pregunta el número
  de pisos del edificio, así que este es el tipo de vivienda del Paso 6, no el del catastro (AJ2).
- **Códigos:** techo (`P4567`) y pisos (`P4015`) tienen los mismos códigos en las dos olas. En las paredes (`P4005`)
  la ola 2024 separó «guadua» de «caña, esterilla, otro vegetal» (códigos 7 y 8) y movió «zinc, tela, lona, cartón,
  latas, desechos, plástico» al 9 y «sin paredes» al 10; se armonizan con las etiquetas de 2019.
- **Categorías:**

| Variable | Categoría | Códigos |
| --- | --- | --- |
| Techo | Concreto | 1 plancha de concreto, cemento u hormigón |
| Techo | Asbesto-cemento | 3 |
| Techo | Metálica o zinc | 4 |
| Techo | Otro | 2 barro, 5 plástica, 6 paja o palma, 7 desecho |
| Paredes | Mampostería | 1 bloque, ladrillo, piedra, madera pulida |
| Paredes | Otro | el resto |
| Pisos | Acabado | 1 alfombra, 2 madera pulida, 3 mármol, 4 baldosa, vinilo, tableta, ladrillo, laminado |
| Pisos | Cemento | 6 cemento o gravilla |
| Pisos | Tierra o madera burda | 5 y 7 |

- **Celdas:** bloque de estratos (1-2, 3-4, 5-6) × tipo de la ECV. En 2024 la muestra va de 20 a 250 viviendas por
  estrato; por eso se agrupa en bloques, como permite la sección 7.5 de la propuesta y como están anidados los
  arquetipos. Las proporciones por estrato se reportan solo como descripción.

## 9.2 Varianza y prueba entre olas (Rao-Scott)

- **2024:** linealización de Taylor con el segmento como unidad primaria, igual que el efecto de diseño del trabajo
  previo; la celda es un dominio.
- **2019:** los microdatos públicos no traen el diseño muestral. La varianza es la multinomial multiplicada por 1,5,
  el efecto de diseño de 2024 (sección 7.5 de la propuesta).
- **Prueba:** homogeneidad de 2019 frente a 2024 en cada celda y variable, con la χ² de Pearson y la corrección de
  segundo orden de Rao y Scott: los valores propios de la matriz de efectos de diseño de la diferencia de proporciones
  dan la media y la dispersión que corrigen el estadístico y sus grados de libertad (Satterthwaite). Se quitan las
  categorías vacías en las dos olas. Una celda con menos de 10 viviendas en alguna ola no se prueba.
- **Decisión por variable:** si ninguna de sus celdas rechaza con α = 0,05 después de la corrección de Holm entre
  celdas, se juntan las dos olas; si alguna rechaza, se usa solo la ola 2024 en esa variable y la de 2019 se reporta
  como sensibilidad.
- **Al juntar:** la proporción de la celda es el promedio de las dos olas ponderado por su número de viviendas en la
  celda (dentro de cada ola, con sus factores de expansión).

## 9.3 Prior de los materiales (Dirichlet)

- **Celda:** α_j = n_ef · p̂_j + m · q_j, con n_ef = n / 1,5 (n = viviendas de la celda en las olas usadas), q = las
  proporciones del mismo tipo en toda la ciudad y m = 1. La varianza implícita, p(1 − p) / (n_ef + m + 1), es la del
  muestreo con el efecto de diseño de 1,5; m = 1 evita probabilidades nulas sin mover las proporciones.
- **Asignación a los arquetipos:**
  - **Casa (C…):** techo, paredes y pisos de la celda «casa» de su bloque.
  - **Último piso (U…):** paredes y pisos de la celda «apartamento» de su bloque. El techo sigue el supuesto S6 del
    trabajo previo: concreto en los multifamiliares (4 pisos o más); en los de baja altura, la distribución de los
    apartamentos de la ECV sin la parte de concreto que corresponde a los multifamiliares:
    p_concreto,ba = max(p_concreto − f_mf, 0) / (1 − f_mf), con las demás categorías reescaladas para sumar el resto.
    f_mf es la fracción de las viviendas del catastro del bloque que no son casa (último piso y sin cubierta) y están
    en multifamiliares. Cada arquetipo mezcla las dos distribuciones con su propia fracción de multifamiliares, y su
    intervalo sale de 10.000 sorteos de la Dirichlet de la celda (semilla 42).
  - **Sin cubierta (S…):** sin techo exterior; paredes y pisos de la celda «apartamento».
- Como dice la propuesta, el techo se asigna solo a las viviendas bajo cubierta (casa y último piso).

## 9.4 De material a parámetros térmicos

**Transmitancia de la cubierta (ISO 6946).** U = 1 / (R_si + Σ d/λ + R_se), con R_se = 0,04 m²K/W y R_si = 0,10
(flujo hacia arriba, de noche) o 0,17 m²K/W (flujo hacia abajo, con sol) (ISO 6946:2017, Tabla 7); λ de la ISO
10456.

| Techo | Capas | Variante con cielo raso |
| --- | --- | --- |
| Concreto | losa de 0,10 a 0,15 m (λ = 2,0) y pañete de 0,015 m (λ = 1,0) | no se aplica |
| Asbesto-cemento | lámina de 6 mm (λ = 0,5) | cámara de aire no ventilada (R = 0,16 hacia arriba y 0,22 hacia abajo; ISO 6946, Tabla 8) y placa de 10 mm (λ = 0,25) |
| Metálica o zinc | lámina (R ≈ 0) | igual |
| Otro | teja de 15 mm (λ = 1,0) | igual |

Prior triangular. **Moda:** flujo hacia abajo, sin cielo raso y con la losa de 0,12 m, porque la carga de
enfriamiento se concentra en las horas de sol. **Mínimo:** flujo hacia abajo con cielo raso (techos livianos) o con
la losa de 0,15 m (concreto). **Máximo:** flujo hacia arriba sin cielo raso, con la losa de 0,10 m en el concreto.
El cielo raso entra solo como extremo del rango, porque ninguna fuente dice qué fracción de las viviendas lo tiene
(supuesto). Los valores de CEELA (losa 3,6; fibrocemento 6,6) se reportan como comparación.

**Transmitancia de los muros (CEELA).** Mampostería: prior triangular entre 1,9 y 4,1 W/m²K (el rango de los
edificios de CEELA), con moda por tipología: casas de 1-2, 2,3 (bloque de concreto); casas de 3-4 y 5-6, 2,7
(arcilla); apartamentos de 1-2, 3,85 (promedio del ladrillo en fachada, 3,6, y del sistema industrializado, 4,1);
apartamentos de 3-4 y 5-6, 3,0 (promedio de 1,9 y 4,1). Otros materiales (madera, zinc, prefabricado, tierra):
triangular(1,5; 3,5; 5,9), supuesto; 5,9 es una lámina sin resistencia propia con R_si horizontal de 0,13.

**Capacidad térmica (ISO 13790, Tabla 12).** La Fase 2 usa el modelo 5R1C, cuya capacidad se fija por clase de
masa: muy ligera 80, ligera 110, media 165, pesada 260 y muy pesada 370 kJ/K por m² de piso, con área efectiva de
2,5; 2,5; 2,5; 3,0 y 3,5 veces el área de piso. La asignación es un supuesto, con una clase de margen hacia cada lado
como prior triangular de la capacidad:

| Construcción | Moda | Rango |
| --- | --- | --- |
| Mampostería con techo liviano encima (casa con asbesto-cemento, zinc u otro) | media | ligera a pesada |
| Mampostería con losa de concreto encima (casa con plancha, último piso, sin cubierta) | pesada | media a muy pesada |
| Paredes de otro material | ligera | muy ligera a media |

Los pisos no cambian la clase: se reportan como descriptor y para el Paso 7; el intercambio con el suelo se calcula en
la Fase 2.

**Absortancia solar.** Cubierta (el color es un supuesto, porque ninguna fuente lo da por estrato): triangular(0,30;
moda; 0,95), con moda de 0,85 en el concreto y 0,60 en el asbesto-cemento (1 − la reflectancia solar de CEELA, 0,15 y
0,40) y de 0,70 en metálica y otro (valor del Paso 3). Muros: triangular(0,44; 0,70; 0,88); los extremos son las
superficies claras y oscuras de ASHRAE (α/h_o = 0,026 y 0,052 m²K/W con h_o = 17) y la moda, el valor del Paso 3.

## 9.5 Ventanas y sombreamiento (CEELA, ampliado)

| Parámetro | Arquetipos | Prior | Fuente |
| --- | --- | --- | --- |
| Relación ventana-muro | casas y apartamentos de 1-2; casas de 3-4 | triangular(0,10; 0,30; 0,50) | CEELA 20–40 %, ampliado 10 puntos por la vivienda antigua e informal (supuesto) |
| Relación ventana-muro | apartamentos de 3-4 | triangular(0,05; 0,15; 0,30) | CEELA menos de 20 %, ampliado (supuesto) |
| Relación ventana-muro | 5-6 | triangular(0,20; 0,30; 0,40) | CEELA 20–40 % |
| U de la ventana | todos | triangular(5,3; 5,88; 6,5) | CEELA, vidrio simple de 4–6 mm con marco de aluminio; ± 10 % por marco y celosías (supuesto) |
| Factor solar del vidrio | todos | triangular(0,75; 0,85; 0,87) | vidrio claro simple (supuesto) |
| Factor de sombra | casas de 1-2 (CEELA: ninguno) | triangular(0,70; 1,0; 1,0) | sombra de vecinos y aleros (supuesto) |
| Factor de sombra | el resto (CEELA: balcones) | triangular(0,50; 0,75; 0,95) | supuesto |

El factor de sombra multiplica la ganancia solar por las ventanas.

## 9.6 Fracción climatizada (CEELA)

- **Zona climatizada:** una habitación en el bloque 1-2 (todas las posiciones) y en las casas de 3-4; las habitaciones
  en los apartamentos de 3-4; toda la vivienda en el bloque 5-6.
- **Cifra:** f = min(1; n_hab · A_hab / A_vivienda), con A_hab triangular(8; 10; 14) m² (supuesto) y n_hab = 1 o las
  habitaciones del catastro (las viviendas con 0 cuentan como 1). Toda la vivienda: f triangular(0,7; 1,0; 1,0),
  porque baños y patios de ropas no se climatizan (supuesto).
- La Fase 2 la calcula con el área de cada vivienda; aquí se reporta con la mediana de área y de habitaciones de cada
  arquetipo.

## 9.7 Productos

- Proporciones de la ECV por ola, celda y categoría, con viviendas en la muestra y errores estándar; las mismas por
  estrato como descripción.
- Pruebas de Rao-Scott y decisión por variable.
- Propiedades por material (U por la ISO 6946, clase de masa, absortancia), con su fuente.
- Priors por arquetipo para las dos soluciones (por vivienda y por m²): Dirichlet del techo con su media y su intervalo
  del 90 %, U del techo y de los muros, capacidad, absortancias, ventanas, sombra y fracción climatizada; en CSV y en
  JSON para la Fase 2.
- Figura del techo por bloque y tipo, con las dos olas.

## 9.8 Fuera de esta versión

- El módulo opcional de techos con imágenes no se activa ahora.
- La consulta IDEA se hará solo si el análisis de Morris de la Fase 2 muestra que un supuesto influye.
- La infiltración no es parte del Paso 6; se fija en la Fase 2.
- **A7 (complementario):** los priors de los materiales con la otra opción de olas (2024 sola si se juntan, o las dos
  juntas si no), para mostrar cuánto cambian.

## Nota 5 (2-nov-2026): corrección del techo del último piso y del efecto de diseño

**Cuándo y por qué.** Escrita después de la primera corrida del Paso 6 y aprobada por la usuaria. A diferencia de
las Notas 3 y 4, se escribió después de ver los resultados. Corrige dos defectos de las reglas de la Sección 9.3, no
un resultado inconveniente, y las reglas originales se reportan como análisis complementario (A8).

1. **Techo del último piso.** La regla de la Sección 9.3 suponía que los apartamentos de la ECV reflejan la mezcla
   del catastro entre edificios de baja altura y multifamiliares. Los datos lo contradicen. En los bloques 1-2 y 3-4,
   la ECV 2024 registra menos concreto entre los apartamentos (36 % y 71 %) que la fracción de esas viviendas que el
   catastro ubica en multifamiliares (71 % y 80 %). Eso sería imposible si la ECV los representara y todos tuvieran
   losa (S6), y el trabajo previo ya había visto que la ECV casi no capta los edificios altos de los estratos bajos.
   Como la resta se recortaba en cero, todo el último piso de baja altura de 1-2 y 3-4 quedaba con techo liviano, y la
   fracción de concreto de U12 y U34 quedaba fija, sin incertidumbre.
   **Regla corregida:** concreto en los multifamiliares (S6) y, en los de baja altura, la Dirichlet de los
   apartamentos de la ECV de su bloque, sin restar nada; cada arquetipo mezcla las dos con su fracción de
   multifamiliares. En 3-4 y 5-6, donde la ECV sí incluye edificios altos, esta regla exagera algo el concreto de la
   baja altura.
2. **Efecto de diseño.** La Sección 9.3 usaba 1,5, el de la tenencia de A/C. En la ECV 2024 el de los materiales es
   mayor, porque las viviendas de un mismo segmento comparten la forma de construir: de 2,5 a 2,8 en el techo.
   **Regla corregida:** n_ef = n / d, donde d es el efecto de diseño de 2024 de la variable dentro de cada tipo de
   vivienda, en toda la ciudad (el de cada celda es inestable porque tiene pocos segmentos), con 1,5 como mínimo.
   La prueba de Rao-Scott no cambia, porque sigue lo que dice la sección 7.5 de la propuesta (la varianza de 2019 se
   multiplica por 1,5). Se reporta cómo cambiaría su decisión si la varianza de 2019 se multiplicara por d.

**A8 (complementario):** el techo de cada arquetipo con las reglas originales de la Sección 9.3 (resta de S6 y efecto
de diseño de 1,5).

---

# Versión 5 · 2 de noviembre de 2026: atributos del hogar, validación y fichas (Paso 7)

Escrita antes de calcular dormitorios, personas o equipos con la ECV y antes del análisis de sensibilidad. De la ECV
2024 solo se revisaron los nombres de las variables y sus etiquetas en el diccionario de datos.

## 10.1 Atributos del hogar

- **Datos:** ECV 2024 de Barranquilla, hogares de viviendas con estrato de 1 a 6 (mismas reglas de la Sección 9.1).
  Unidad: el hogar (archivos «Servicios del hogar» y «Condiciones de vida del hogar y tenencia de bienes»), con su
  factor de expansión; el estrato y el tipo vienen de la vivienda.
- **Variables:** cuartos (`P5000`), dormitorios (`P5010`, cuartos donde duermen las personas del hogar), personas
  (`CANT_PERSONAS_HOGAR`) y tenencia (código 1 = sí) de aire acondicionado (`P1077S11`), ventilador (`P1077S12`), nevera
  (`P1077S2`), lavadora (`P1077S1`), televisor plano (`P1077S8`) y calentador de agua o ducha eléctrica (`P1077S6`).
- **Por estrato**, como dice la propuesta: media o proporción ponderada, con su error estándar por linealización con
  el segmento (Sección 9.2).
- **Al arquetipo:** el promedio de los valores por estrato, ponderado por la composición de estratos del arquetipo en
  el catastro. Dos arquetipos del mismo bloque con igual composición reciben los mismos valores; es la misma limitación
  de los materiales del Paso 6.
- **Ola:** solo 2024, la única con diseño muestral. La tenencia de A/C que usará la Fase 2 es la serie suavizada de
  2018 a 2025 del trabajo previo; la de aquí es descriptiva.

## 10.2 Habitaciones: catastro frente a ECV

- Catastro: `total_habitaciones` de cada vivienda (las que tienen 0 cuentan como 1). ECV: `P5010` de cada hogar.
- Por estrato y por estrato × tipo: casa frente a casa, y apartamento de la ECV frente a último piso y sin cubierta
  del catastro. Se comparan la media y el reparto en 1, 2, 3 y 4 o más.
- Se señala cada comparación en que la media del catastro cae fuera del intervalo de confianza del 95 % de la ECV,
  calculado con el diseño muestral.

## 10.3 Representatividad frente a las encuestas

Se compara lo que el catastro dice de la ciudad con lo que estima la ECV 2024, en lo que comparten:

1. **Reparto de las viviendas por estrato** (ECV: archivo de la vivienda, viviendas expandidas).
2. **Fracción de casas por bloque.** Catastro: la posición «casa»; ECV: casa, cuarto u otro (`P1070`). Es el puente
   del Paso 6 (AJ11). Como el primer piso con otra vivienda encima es «sin cubierta» en el catastro (AJ3) y su hogar
   puede declararse casa en la ECV, se reporta también una variante del catastro que suma esos primeros pisos de baja
   altura a las casas.
3. **Habitaciones** (Sección 10.2).

Para cada comparación se reporta la diferencia y si el valor del catastro cae dentro del intervalo del 95 % de la ECV.
Es una validación, no una regla: lo que no cuadre no cambia los arquetipos y se anota como limitación en las fichas.

## 10.4 Sensibilidad a las variables de agrupamiento

- Para cada solución final y cada una de las seis variables (área, pisos de la unidad, piso, época, tipo y propiedad
  horizontal) se repite el agrupamiento de cada estrato con más de un grupo, sin esa variable: el mismo algoritmo, la
  misma submuestra, el mismo k del estrato y la semilla 42. Los atípicos se recalculan con DBSCAN sin la variable,
  porque es el procedimiento completo de la Sección 7. Las viviendas se asignan con la regla de la Sección 7.5.
- **Medidas:** índice de Rand ajustado frente a la solución final, sobre todas las viviendas, y R² de la carga con la
  misma medida de la solución.
- **Control:** primero se repite el ajuste con las seis variables; debe reproducir la solución final (Rand = 1).
- **Lectura:** una variable es influyente si quitarla deja el Rand por debajo de 0,8 o baja el R² en 0,02 o más (el
  umbral del Paso 3). Es descriptivo: no cambia los arquetipos. Si la variable ya no entraba en el estrato (su moda
  cubre el 99 %), se reporta como «no aplica».
- Los estratos con un solo grupo no dependen de las variables de agrupamiento, porque los definen la posición y el
  bloque; se reporta cuántas viviendas cubren.

## 10.5 Fichas

Una por arquetipo en cada solución (17 por vivienda y 10 por m²), en Markdown y en una tabla, con:

1. **Identificación:** posición, bloque, algoritmo, viviendas, porcentaje de la ciudad y edificios.
2. **Definición:** las reglas principales del árbol del Paso 5 y los rangos típicos (percentiles 25 a 75).
3. **Rasgos físicos:** área, pisos de la unidad, piso, época, propiedad horizontal, multifamiliar y estratos.
4. **Carga simplificada** del Paso 3: mediana por vivienda y por m².
5. **Envolvente** del Paso 6: techo (si está bajo cubierta), U del techo y del muro, capacidad, ventanas, sombra y
   fracción climatizada, con su intervalo del 90 %.
6. **Hogar:** habitaciones del catastro, dormitorios, personas y tenencia de equipos de la ECV (Sección 10.1).
7. **Calidad:** estabilidad (Jaccard), recall del árbol y del bosque en la prueba, probabilidad media de asignación.
8. **Limitaciones** que le aplican, incluidas las de las Secciones 10.2 a 10.4.

Solo agregados.

## 10.6 Productos

- Tablas: atributos del hogar por estrato y por arquetipo, habitaciones, representatividad y sensibilidad a las
  variables.
- Fichas de las dos soluciones.
- Figura de la representatividad: valor del catastro frente al intervalo de la ECV.

## Nota 6 (2-nov-2026): habitaciones climatizadas en los apartamentos de 3-4

**Cuándo y por qué.** Escrita después del Paso 7 y aprobada por la usuaria. La Sección 9.6 contaba «las habitaciones»
con el campo `total_habitaciones` del catastro, suponiendo que eran dormitorios. La validación de la Sección 10.2 lo
contradice: el catastro da de 0,5 a 1,1 habitaciones más que los dormitorios de la ECV en todos los estratos, y en
los apartamentos de los estratos 3 y 4, 2,7 a 2,8 frente a 1,9 a 2,0.

**Regla corregida** (solo cambia la zona «las habitaciones», es decir, los apartamentos de 3-4): el número de
habitaciones climatizadas de cada vivienda es el del catastro multiplicado por el cociente entre los dormitorios
medios de la ECV 2024 y las habitaciones medias del catastro, en los apartamentos (último piso y sin cubierta) de su
estrato, con 1 como mínimo. Así se conserva que las viviendas más grandes tengan más habitaciones y la media coincide
con la ECV.

## Nota 7 (2-nov-2026): prior de la infiltración

**Cuándo y por qué.** Escrita después de revisar la literatura y antes de calcular cualquier prior de infiltración;
aprobada por la usuaria. La Sección 9.8 dejaba la infiltración para la Fase 2, pero en la carga del Paso 3 es el 33 %
de la ciudad y el 62 % de las viviendas sin cubierta, y su valor (1 renovación por hora) era un supuesto sin fuente.
La propuesta pide que un dato faltante se declare como supuesto con un rango amplio para que la sensibilidad muestre
si importa.

**Regla.** Renovaciones de aire por hora con las ventanas cerradas (la infiltración mientras funciona el A/C; la
ventilación natural con las ventanas abiertas se modela aparte en la Fase 2). Prior lognormal, como la distribución
de las mediciones residenciales (Nazaroff, 2021), definido por sus percentiles 5 y 95:

| Construcción | Percentil 5 | Mediana | Percentil 95 | Ancla |
| --- | --- | --- | --- | --- |
| Cerrada: losa de concreto encima y mampostería | 0,5 | 0,89 | 1,6 | 20 apartamentos con A/C en clima cálido de la India, de 0,53 a 1,63 (Mathur y Damle, 2021) |
| Abierta: techo liviano sobre los muros o paredes de otro material | 0,8 | 2,0 | 5,0 | Multifamiliares de São Paulo de 1 a 5,7 a 4 Pa (Rodrigues et al., 2021); supuesto |

La mediana es la media geométrica de los dos percentiles y σ = ln(p95/p5) / (2 × 1,645). Cada sorteo usa la
construcción que ya define la capacidad (Sección 9.4): muro de otro material o techo liviano, abierta; losa encima,
cerrada. Que el techo liviano sea más permeable es un supuesto propio; no hay mediciones en Colombia.

## Nota 8 (2-nov-2026): variante ampliada del agrupamiento

**Cuándo y por qué.** Escrita a pedido de la usuaria y antes de correr la variante. La usuaria pidió tener en cuenta
en el agrupamiento las demás variables del catastro analizadas en el trabajo previo de predicción del estrato. La
propuesta fija seis variables (Paso 2), así que la variante se corre junto a la solución de seis variables y la
elección entre las dos sigue una regla fijada aquí (ajuste AJ19).

**Variables que se agregan** (a las seis de la Sección 7.3):

| Variable | Codificación |
| --- | --- |
| Habitaciones (`total_habitaciones`) | log(1 + x); los faltantes (0,11 %) toman la mediana de su posición |
| Baños (`total_banios`) | log(1 + x); los faltantes (0,01 %) toman la mediana de su posición |
| Área del terreno (`area_catastral_terreno`) | log(1 + x); en propiedad horizontal es la parte del lote |
| VIS o VIP (`tipo_vivienda`) | binaria: 1 si es vivienda de interés social o prioritario; 0 si no es VIS o dice «No aplica» (79 %) |

**Variables que no se agregan.** La destinación económica (100 % habitacional) y el tipo de planta (100 % «Piso»)
son constantes; la altura de piso vale 3,0 m en el 99,7 % de las viviendas y la regla del 99 % la quitaría; la
ubicación (coordenadas y distancia al centro) queda fuera por decisión de la usuaria, porque el arquetipo describe la
vivienda y no su lugar (AJ10).

**Procedimiento.** Idéntico al de la versión 2 con las Notas 3 y 4: la misma submuestra (semilla 42), DBSCAN
recalculado con las nuevas variables, los dos diseños, la frontera óptima, la estabilidad de Jaccard en 100
submuestras y la regla del 99 % para descartar variables casi constantes en cada estrato. La regla del Paso 4 (plano o
anidado) se aplica a cada conjunto de variables por separado.

**Elección entre las dos soluciones.** Para cada medida de carga se aplica la Nota 4 dentro de cada conjunto de
variables y luego la misma regla entre los dos finalistas: si solo uno es estable, ese; si los dos lo son, el de mayor
R² de la carga; si quedan a menos de 0,02, el de menos grupos; si tienen los mismos, el de seis variables (el de la
propuesta); y si aún empatan, el de mayor silueta.

**Consecuencias.** Si gana la variante ampliada en alguna medida, para esa medida se repiten los Pasos 5 a 7
(clasificador, priors, sensibilidad, validación y fichas) y el clasificador usa también las variables agregadas. Si
gana la de seis variables, los resultados no cambian y la variante se reporta como análisis complementario A9.
