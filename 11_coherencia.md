# Coherencia entre fuentes y validación

Antes de usar las fuentes en el modelo se comprobó que coinciden en las magnitudes que miden en común. Las comparaciones no son una validación del modelo, que se hará en la Fase 3 con la demanda horaria de XM y el consumo de 2021–2025. Lo que muestran es si cada fuente mide la misma población y en qué casos hay que corregirla. Cuando dos fuentes difieren, se indica cuál se adopta y por qué.

## Distribución de los hogares por estrato

```{figure} figuras/coherencia_estratos.png
:name: fig-coherencia-estratos
:width: 100%
Distribución de viviendas, suscriptores u hogares por estrato según la fuente. El catastro y el SUI coinciden; las encuestas tienen más hogares de estrato 1 que la ciudad.
```

Para resumir la diferencia entre dos distribuciones se usa el índice de disimilitud {cite:p}`duncan1955`:

$$
D_{AB} = \frac{1}{2}\sum_{e=1}^{6} \left| \pi_{A,e} - \pi_{B,e} \right|
$$ (eq-disimilitud)

donde $\pi_{A,e}$ es la proporción del estrato $e$ en la fuente $A$. $D$ es el porcentaje de hogares que habría que mover de estrato para que las dos distribuciones fueran iguales.

```{table} Distribución por estrato según la fuente (%) e índice de disimilitud frente al SUI del mismo año.
:name: tab-coherencia-estratos

| Fuente | Unidad | E1 | E2 | E3 | E4 | E5 | E6 | $D$ frente al SUI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Catastro 2026 | Viviendas | 32,8 | 21,8 | 21,6 | 14,8 | 5,1 | 4,0 | 2,4 (2024) |
| SUI, diciembre de 2019 | Suscriptores | 33,8 | 19,9 | 22,8 | 14,0 | 5,2 | 4,2 | — |
| SUI, diciembre de 2024 | Suscriptores | 33,3 | 19,3 | 22,9 | 15,0 | 5,4 | 4,1 | — |
| ECV 2019 | Hogares | 39,4 | 20,2 | 18,1 | 12,5 | 4,4 | 4,7 | 6,7 |
| ECV 2024 | Hogares | 38,6 | 22,5 | 20,6 | 9,0 | 6,0 | 3,4 | 9,1 |
| GEIH 2024 (área metropolitana) | Hogares | 44,0 | 29,1 | 14,0 | 7,7 | 2,5 | 2,1 | 20,8 |
```

El catastro y el SUI, que son fuentes independientes (un registro predial y un registro de facturación), coinciden: $D = 2{,}4$ %. La mayor diferencia está en el estrato 2, con 2,5 puntos. La ECV, expandida con sus propios factores, sobrerrepresenta el estrato 1 entre 5 y 6 puntos ($D$ de 6,7 % y 9,1 %). Como el estrato 1 es el de menor tenencia de A/C, la ECV sin corregir subestima la tenencia de la ciudad: 30,9 % frente a 33,3 % en 2019 y 37,1 % frente a 41,4 % en 2024. Por eso la tasa de la ciudad se calcula con las tasas de la ECV por estrato y los pesos del SUI {cite:p}`holt1979`. La GEIH cubre el área metropolitana, que incluye municipios con más hogares de estratos bajos. Por eso se usa solo para el trabajo en casa por estrato y no para la composición de la ciudad.

## Número de hogares

```{table} Número de hogares o unidades residenciales de Barranquilla según la fuente.
:name: tab-coherencia-hogares

| Fuente | Cifra | Unidad |
| --- | --- | --- |
| Catastro 2026 | 332.718 | Viviendas residenciales con estrato |
| SUI, diciembre de 2024 | 330.101 | Suscriptores residenciales, estratos 1–6 |
| Población 2025 ÷ personas por hogar (ECV 2024) | ≈ 364.000 | Hogares (1.279.344 ÷ 3,51) |
| ECV 2024, suma de factores de expansión | 389.372 | Hogares |
```

El catastro y el SUI difieren en 0,8 %. La estimación demográfica es 10 % mayor. La diferencia es coherente con varios hogares por vivienda y con la vivienda informal sin medidor propio. La expansión de la ECV es 18 % mayor que el SUI. El modelo expande sus resultados a la ciudad con los suscriptores del SUI, porque es la población a la que corresponde el consumo facturado contra el que se calibra.

## Tenencia de equipos medida por fuentes distintas

```{table} Tenencia de nevera según la fuente (% de hogares).
:name: tab-coherencia-nevera

| Fuente | Dominio | Tenencia de nevera |
| --- | --- | --- |
| ECV 2019 | Barranquilla | 90,5 |
| ENUT 2024–2025 | Atlántico, cabeceras | 90,3 |
| ECV 2024, factores de expansión | Barranquilla | 91,4 |
| ECV 2024, postestratificada con el SUI | Barranquilla | 93,0 |
```

Tres fuentes con muestras y cuestionarios distintos dan una tenencia de nevera de entre 90 % y 93 %. La ENUT no pregunta por A/C ni ventilador, por lo que no permite contrastar esos equipos.

La imputación de la tenencia de A/C a las viviendas del catastro sirve además como control interno. Con la variante C, la proporción media en el catastro en 2024 es de 40,7 %, frente a 41,2 % con los pesos del SUI. La diferencia es de composición: el catastro tiene más viviendas de estrato 2 y menos de estrato 3 que el SUI.

## Encuesta frente a facturación

La ECV y el SUI no comparten preguntas, pero deberían ser coherentes en un aspecto: los estratos con más A/C deberían tener un alza mayor del consumo en los meses más calurosos.

```{figure} figuras/coherencia_alza_ac.png
:name: fig-coherencia-alza
:width: 100%
Tenencia de A/C de 2019 (ECV, variante C) frente al alza del consumo facturado de agosto y septiembre respecto a febrero y marzo (SUI, 2015–2025), por estrato.
```

La correlación entre las dos magnitudes es alta: $r = 0{,}93$ de Pearson ($p = 0{,}007$, seis estratos), y la relación es creciente hasta el estrato 4. En los estratos 4 a 6 el alza se estabiliza entre 28 % y 29 % aunque la tenencia sigue subiendo, de 72 % a 97 %. Esto es coherente con un uso por hogar que no crece en proporción a la tenencia, y con el número de equipos y la fracción climatizada como factores que la tenencia no captura. La comparación tiene dos limitaciones. Es ecológica, con seis puntos agregados, así que no mide el efecto del A/C en un hogar. Y la nevera también consume más con el calor, de modo que una parte del alza no es del A/C. Por eso la propuesta reporta el reparto entre A/C y nevera con su capa de incertidumbre (Fase 3, paso 7).

## Validación pendiente

- **Clima.** Las series de ERA5-Land se contrastarán con la estación del aeropuerto Ernesto Cortissoz del IDEAM, por hora del día y mes, con el sesgo y la raíz del error cuadrático medio (Fase 2, paso 1).
- **Demanda horaria.** La suma del consumo facturado del SUI y las pérdidas debe acercarse a la demanda regulada de XM del mercado de Air-e (Fase 3, paso 1).
- **Consumo del estrato 1.** El consumo por suscriptor del estrato 1 es mayor que el de los estratos 2 y 3, lo que no es coherente con su menor tenencia de A/C. Queda pendiente confirmarlo con Air-e.
