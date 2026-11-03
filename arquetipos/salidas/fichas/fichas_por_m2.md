# Fichas de los arquetipos: solución con carga por m² (10 arquetipos)

Preregistro de la Fase 1, versión 5, Sección 10.5. Solo agregados. La carga es el índice simplificado del Paso 3, con una envolvente común para todas las viviendas; no es la carga simulada de la Fase 2. Los priors de envolvente son los del Paso 6 (media e intervalo del 90 %) y los atributos del hogar salen de la ECV 2024 por estrato, llevados a cada arquetipo con su composición de estratos.

## C12-1 · Casa, estratos 1-2

**Identificación.** 119.465 viviendas (35,9 % de la ciudad) en 102.682 edificios. Posición: casa. Agrupamiento: K-Means en el estrato «casa · 1-2», con 2 grupo(s).

**Definición.** Rasgos típicos (percentiles 25 a 75): área de 51 a 96 m² (mediana 69 m²); 1 piso(s) en la unidad; piso 1 del edificio (mediana).

Reglas principales del árbol de asignación (Paso 5):

- pisos de la unidad ≤ 1 · posición: casa · bloque de estratos: 1-2 (93.944 viviendas de entrenamiento)

**Rasgos físicos.**

| Rasgo | Valor |
| --- | --- |
| Área (m²), mediana (P25–P75) | 69 (51–96) |
| Pisos de la unidad, mediana | 1 |
| Piso de la unidad, mediana | 1 |
| En propiedad horizontal | 2,6 % |
| En multifamiliar (4 pisos o más) | 0,0 % |
| Época: antes de 1990 / 1990–2009 / 2010 o después | 20,8 / 30,6 / 48,6 % |
| Estratos | E1 53,7 %, E2 46,3 % |

**Carga simplificada (índice del Paso 3).** Mediana de 36.048 kWh térmicos al año por vivienda y 522 kWh por m².

**Envolvente (priors del Paso 6).**

| Parámetro | Media | Intervalo del 90 % |
| --- | --- | --- |
| Techo de concreto | 18 % | 11 %–27 % |
| Techo de asbesto-cemento | 67 % | 58 %–76 % |
| Techo metálico o de zinc | 14 % | 8 %–22 % |
| Techo de otro material | 0 % | 0 %–0 % |
| U del techo (W/m²K) | 4,34 | 2,92–5,91 |
| Absortancia del techo | 0,64 | 0,40–0,86 |
| Muros de mampostería | 98 % | 96 %–100 % |
| U del muro (W/m²K) | 2,78 | 2,11–3,69 |
| Absortancia del muro | 0,67 | 0,52–0,82 |
| Capacidad C_m (kJ/K por m² de piso) | 193 | 130–290 |
| Infiltración con ventanas cerradas (renovaciones por hora) | 2,06 | 0,65–4,59 |
| Pisos con acabado | 77 % | 69 %–85 % |
| Relación ventana-muro | 0,30 | 0,16–0,44 |
| U de la ventana (W/m²K) | 5,89 | 5,48–6,31 |
| Factor solar del vidrio | 0,82 | 0,77–0,86 |
| Factor de sombra | 0,90 | 0,77–0,99 |
| Fracción climatizada (una) | 0,18 | 0,07–0,39 |

**Hogar.**

| Atributo | Valor |
| --- | --- |
| Habitaciones según el catastro, mediana (media) | 3 (2,6) |
| Dormitorios según la ECV, media | 2,1 (± 0,1) |
| Personas por hogar según la ECV | 3,8 (± 0,2) |
| Hogares con aire acondicionado | 22 % (± 5 puntos) |
| Hogares con ventilador | 99 % (± 1 puntos) |
| Hogares con nevera | 89 % (± 3 puntos) |
| Hogares con lavadora | 59 % (± 7 puntos) |
| Hogares con televisor plano | 75 % (± 6 puntos) |
| Hogares con calentador de agua o ducha eléctrica | 1 % (± 1 puntos) |

**Calidad.** Estabilidad (Jaccard): 1,00. Recall en la prueba: árbol 1,000, Random Forest 1,000. Probabilidad media de asignación: 1,000 (0,0 % de las viviendas por debajo de 0,8).

**Limitaciones.**

- Comparte con C12-2 el prior de materiales de la ECV, que no distingue tamaño ni época dentro de la misma posición y bloque; los atributos del hogar solo cambian por la composición de estratos.
- La fracción de casas del catastro en los estratos 1-2 queda fuera del intervalo de la ECV, así que el puente entre la posición y el tipo de vivienda de la ECV es aproximado.
- Las habitaciones del catastro difieren de los dormitorios de la ECV en los estratos 1, 2 (fuera del intervalo del 95 %).
- Su frontera con los demás grupos del estrato depende de: pisos de la unidad (Sección 10.4).

## C12-2 · Casa, estratos 1-2

**Identificación.** 9.132 viviendas (2,7 % de la ciudad) en 8.018 edificios. Posición: casa. Agrupamiento: K-Means en el estrato «casa · 1-2», con 2 grupo(s).

**Definición.** Rasgos típicos (percentiles 25 a 75): área de 65 a 140 m² (mediana 104 m²); 2 piso(s) en la unidad; piso 1 del edificio (mediana).

Reglas principales del árbol de asignación (Paso 5):

- pisos de la unidad ≥ 2 · posición: casa · bloque de estratos: 1-2 (7.472 viviendas de entrenamiento)

**Rasgos físicos.**

| Rasgo | Valor |
| --- | --- |
| Área (m²), mediana (P25–P75) | 104 (65–140) |
| Pisos de la unidad, mediana | 2 |
| Piso de la unidad, mediana | 1 |
| En propiedad horizontal | 15,7 % |
| En multifamiliar (4 pisos o más) | 0,0 % |
| Época: antes de 1990 / 1990–2009 / 2010 o después | 40,9 / 25,5 / 33,6 % |
| Estratos | E1 39,3 %, E2 60,7 % |

**Carga simplificada (índice del Paso 3).** Mediana de 39.770 kWh térmicos al año por vivienda y 382 kWh por m².

**Envolvente (priors del Paso 6).**

| Parámetro | Media | Intervalo del 90 % |
| --- | --- | --- |
| Techo de concreto | 18 % | 11 %–26 % |
| Techo de asbesto-cemento | 67 % | 58 %–76 % |
| Techo metálico o de zinc | 14 % | 8 %–22 % |
| Techo de otro material | 0 % | 0 %–0 % |
| U del techo (W/m²K) | 4,33 | 2,94–5,91 |
| Absortancia del techo | 0,64 | 0,41–0,86 |
| Muros de mampostería | 98 % | 95 %–100 % |
| U del muro (W/m²K) | 2,79 | 2,11–3,70 |
| Absortancia del muro | 0,67 | 0,52–0,82 |
| Capacidad C_m (kJ/K por m² de piso) | 193 | 130–290 |
| Infiltración con ventanas cerradas (renovaciones por hora) | 2,08 | 0,66–4,66 |
| Pisos con acabado | 78 % | 69 %–85 % |
| Relación ventana-muro | 0,30 | 0,16–0,43 |
| U de la ventana (W/m²K) | 5,90 | 5,48–6,31 |
| Factor solar del vidrio | 0,82 | 0,77–0,86 |
| Factor de sombra | 0,90 | 0,77–0,99 |
| Fracción climatizada (una) | 0,14 | 0,04–0,45 |

**Hogar.**

| Atributo | Valor |
| --- | --- |
| Habitaciones según el catastro, mediana (media) | 3 (3,5) |
| Dormitorios según la ECV, media | 2,2 (± 0,1) |
| Personas por hogar según la ECV | 3,8 (± 0,2) |
| Hogares con aire acondicionado | 26 % (± 6 puntos) |
| Hogares con ventilador | 99 % (± 1 puntos) |
| Hogares con nevera | 89 % (± 3 puntos) |
| Hogares con lavadora | 62 % (± 7 puntos) |
| Hogares con televisor plano | 76 % (± 5 puntos) |
| Hogares con calentador de agua o ducha eléctrica | 1 % (± 1 puntos) |

**Calidad.** Estabilidad (Jaccard): 1,00. Recall en la prueba: árbol 1,000, Random Forest 1,000. Probabilidad media de asignación: 0,999 (0,0 % de las viviendas por debajo de 0,8).

**Limitaciones.**

- Comparte con C12-1 el prior de materiales de la ECV, que no distingue tamaño ni época dentro de la misma posición y bloque; los atributos del hogar solo cambian por la composición de estratos.
- La fracción de casas del catastro en los estratos 1-2 queda fuera del intervalo de la ECV, así que el puente entre la posición y el tipo de vivienda de la ECV es aproximado.
- Las habitaciones del catastro difieren de los dormitorios de la ECV en los estratos 1, 2 (fuera del intervalo del 95 %).
- Su frontera con los demás grupos del estrato depende de: pisos de la unidad (Sección 10.4).

## C34-1 · Casa, estratos 3-4

**Identificación.** 48.239 viviendas (14,5 % de la ciudad) en 41.491 edificios. Posición: casa. Agrupamiento: K-Means en el estrato «casa · 3-4», con 1 grupo(s).

**Definición.** Rasgos típicos (percentiles 25 a 75): área de 85 a 160 m² (mediana 116 m²); 1 piso(s) en la unidad; piso 1 del edificio (mediana).

Reglas principales del árbol de asignación (Paso 5):

- posición: casa · bloque de estratos: 3-4 (36.350 viviendas de entrenamiento)

**Rasgos físicos.**

| Rasgo | Valor |
| --- | --- |
| Área (m²), mediana (P25–P75) | 116 (85–160) |
| Pisos de la unidad, mediana | 1 |
| Piso de la unidad, mediana | 1 |
| En propiedad horizontal | 15,1 % |
| En multifamiliar (4 pisos o más) | 0,0 % |
| Época: antes de 1990 / 1990–2009 / 2010 o después | 27,6 / 26,0 / 46,4 % |
| Estratos | E3 78,4 %, E4 21,6 % |

**Carga simplificada (índice del Paso 3).** Mediana de 56.000 kWh térmicos al año por vivienda y 499 kWh por m².

**Envolvente (priors del Paso 6).**

| Parámetro | Media | Intervalo del 90 % |
| --- | --- | --- |
| Techo de concreto | 26 % | 11 %–43 % |
| Techo de asbesto-cemento | 74 % | 56 %–89 % |
| Techo metálico o de zinc | 1 % | 0 %–3 % |
| Techo de otro material | 0 % | 0 %–0 % |
| U del techo (W/m²K) | 4,28 | 2,94–5,81 |
| Absortancia del techo | 0,64 | 0,41–0,86 |
| Muros de mampostería | 100 % | 100 %–100 % |
| U del muro (W/m²K) | 2,90 | 2,20–3,69 |
| Absortancia del muro | 0,67 | 0,51–0,82 |
| Capacidad C_m (kJ/K por m² de piso) | 201 | 134–305 |
| Infiltración con ventanas cerradas (renovaciones por hora) | 1,98 | 0,61–4,65 |
| Pisos con acabado | 97 % | 89 %–100 % |
| Relación ventana-muro | 0,30 | 0,16–0,43 |
| U de la ventana (W/m²K) | 5,90 | 5,48–6,31 |
| Factor solar del vidrio | 0,82 | 0,78–0,86 |
| Factor de sombra | 0,73 | 0,58–0,88 |
| Fracción climatizada (una) | 0,11 | 0,04–0,24 |

**Hogar.**

| Atributo | Valor |
| --- | --- |
| Habitaciones según el catastro, mediana (media) | 3 (3,3) |
| Dormitorios según la ECV, media | 2,1 (± 0,2) |
| Personas por hogar según la ECV | 2,9 (± 0,3) |
| Hogares con aire acondicionado | 53 % (± 9 puntos) |
| Hogares con ventilador | 98 % (± 2 puntos) |
| Hogares con nevera | 97 % (± 3 puntos) |
| Hogares con lavadora | 91 % (± 5 puntos) |
| Hogares con televisor plano | 93 % (± 4 puntos) |
| Hogares con calentador de agua o ducha eléctrica | 4 % (± 3 puntos) |

**Calidad.** Estabilidad (Jaccard): 1,00. Recall en la prueba: árbol 1,000, Random Forest 1,000. Probabilidad media de asignación: 1,000 (0,0 % de las viviendas por debajo de 0,8).

**Limitaciones.**

- La fracción de casas del catastro en los estratos 3-4 queda fuera del intervalo de la ECV, así que el puente entre la posición y el tipo de vivienda de la ECV es aproximado.
- Las habitaciones del catastro difieren de los dormitorios de la ECV en los estratos 3, 4 (fuera del intervalo del 95 %).
- Lo definen la posición y el bloque de estratos; no depende de las variables de agrupamiento.

## C56-1 · Casa, estratos 5-6

**Identificación.** 4.216 viviendas (1,3 % de la ciudad) en 2.973 edificios. Posición: casa. Agrupamiento: K-Means en el estrato «casa · 5-6», con 1 grupo(s).

**Definición.** Rasgos típicos (percentiles 25 a 75): área de 153 a 304 m² (mediana 213 m²); 2 piso(s) en la unidad; piso 1 del edificio (mediana).

Reglas principales del árbol de asignación (Paso 5):

- posición: casa · bloque de estratos: 5-6 (3.616 viviendas de entrenamiento)

**Rasgos físicos.**

| Rasgo | Valor |
| --- | --- |
| Área (m²), mediana (P25–P75) | 213 (153–304) |
| Pisos de la unidad, mediana | 2 |
| Piso de la unidad, mediana | 1 |
| En propiedad horizontal | 35,6 % |
| En multifamiliar (4 pisos o más) | 0,0 % |
| Época: antes de 1990 / 1990–2009 / 2010 o después | 11,0 / 39,4 / 49,6 % |
| Estratos | E5 68,8 %, E6 31,2 % |

**Carga simplificada (índice del Paso 3).** Mediana de 91.026 kWh térmicos al año por vivienda y 389 kWh por m².

**Envolvente (priors del Paso 6).**

| Parámetro | Media | Intervalo del 90 % |
| --- | --- | --- |
| Techo de concreto | 72 % | 43 %–94 % |
| Techo de asbesto-cemento | 27 % | 5 %–55 % |
| Techo metálico o de zinc | 1 % | 0 %–9 % |
| Techo de otro material | 0 % | 0 %–0 % |
| U del techo (W/m²K) | 4,04 | 3,39–5,29 |
| Absortancia del techo | 0,68 | 0,42–0,88 |
| Muros de mampostería | 100 % | 100 %–100 % |
| U del muro (W/m²K) | 2,90 | 2,18–3,71 |
| Absortancia del muro | 0,67 | 0,52–0,82 |
| Capacidad C_m (kJ/K por m² de piso) | 241 | 147–330 |
| Infiltración con ventanas cerradas (renovaciones por hora) | 1,33 | 0,52–3,33 |
| Pisos con acabado | 98 % | 89 %–100 % |
| Relación ventana-muro | 0,30 | 0,23–0,37 |
| U de la ventana (W/m²K) | 5,89 | 5,48–6,30 |
| Factor solar del vidrio | 0,82 | 0,77–0,86 |
| Factor de sombra | 0,73 | 0,57–0,88 |
| Fracción climatizada (toda) | 0,90 | 0,77–0,99 |

**Hogar.**

| Atributo | Valor |
| --- | --- |
| Habitaciones según el catastro, mediana (media) | 3 (3,7) |
| Dormitorios según la ECV, media | 2,1 (± 0,4) |
| Personas por hogar según la ECV | 2,8 (± 0,5) |
| Hogares con aire acondicionado | 87 % (± 10 puntos) |
| Hogares con ventilador | 98 % (± 4 puntos) |
| Hogares con nevera | 100 % (± 0 puntos) |
| Hogares con lavadora | 93 % (± 8 puntos) |
| Hogares con televisor plano | 96 % (± 6 puntos) |
| Hogares con calentador de agua o ducha eléctrica | 27 % (± 11 puntos) |

**Calidad.** Estabilidad (Jaccard): 1,00. Recall en la prueba: árbol 1,000, Random Forest 1,000. Probabilidad media de asignación: 1,000 (0,0 % de las viviendas por debajo de 0,8).

**Limitaciones.**

- La celda de la ECV (casa, estratos 5-6) tiene solo 15 viviendas: los priors de materiales son muy inciertos.
- Las habitaciones del catastro difieren de los dormitorios de la ECV en los estratos 5, 6 (fuera del intervalo del 95 %).
- Lo definen la posición y el bloque de estratos; no depende de las variables de agrupamiento.

## S12-1 · Sin cubierta, estratos 1-2

**Identificación.** 40.889 viviendas (12,3 % de la ciudad) en 2.403 edificios. Posición: sin cubierta (apartamento intermedio o primer piso con vivienda encima). Agrupamiento: K-Means en el estrato «sin cubierta · 1-2», con 1 grupo(s).

**Definición.** Rasgos típicos (percentiles 25 a 75): área de 42 a 56 m² (mediana 46 m²); 1 piso(s) en la unidad; piso 2 del edificio (mediana).

Reglas principales del árbol de asignación (Paso 5):

- posición: sin cubierta · bloque de estratos: 1-2 (24.772 viviendas de entrenamiento)

**Rasgos físicos.**

| Rasgo | Valor |
| --- | --- |
| Área (m²), mediana (P25–P75) | 46 (42–56) |
| Pisos de la unidad, mediana | 1 |
| Piso de la unidad, mediana | 2 |
| En propiedad horizontal | 81,1 % |
| En multifamiliar (4 pisos o más) | 76,5 % |
| Época: antes de 1990 / 1990–2009 / 2010 o después | 6,7 / 12,4 / 80,9 % |
| Estratos | E1 83,2 %, E2 16,8 % |

**Carga simplificada (índice del Paso 3).** Mediana de 10.841 kWh térmicos al año por vivienda y 236 kWh por m².

**Envolvente (priors del Paso 6).**

| Parámetro | Media | Intervalo del 90 % |
| --- | --- | --- |
| Muros de mampostería | 99 % | 98 %–100 % |
| U del muro (W/m²K) | 3,29 | 2,38–3,93 |
| Absortancia del muro | 0,67 | 0,51–0,82 |
| Capacidad C_m (kJ/K por m² de piso) | 263 | 193–337 |
| Infiltración con ventanas cerradas (renovaciones por hora) | 0,97 | 0,50–1,64 |
| Pisos con acabado | 80 % | 74 %–86 % |
| Relación ventana-muro | 0,30 | 0,16–0,44 |
| U de la ventana (W/m²K) | 5,90 | 5,49–6,31 |
| Factor solar del vidrio | 0,82 | 0,78–0,86 |
| Factor de sombra | 0,73 | 0,57–0,88 |
| Fracción climatizada (una) | 0,22 | 0,12–0,31 |
| Techo | no expuesto (hay otra vivienda encima) | |

**Hogar.**

| Atributo | Valor |
| --- | --- |
| Habitaciones según el catastro, mediana (media) | 2 (2,5) |
| Dormitorios según la ECV, media | 2,1 (± 0,1) |
| Personas por hogar según la ECV | 3,9 (± 0,2) |
| Hogares con aire acondicionado | 16 % (± 4 puntos) |
| Hogares con ventilador | 99 % (± 1 puntos) |
| Hogares con nevera | 88 % (± 4 puntos) |
| Hogares con lavadora | 52 % (± 8 puntos) |
| Hogares con televisor plano | 72 % (± 7 puntos) |
| Hogares con calentador de agua o ducha eléctrica | 0 % (± 1 puntos) |

**Calidad.** Estabilidad (Jaccard): 1,00. Recall en la prueba: árbol 1,000, Random Forest 1,000. Probabilidad media de asignación: 0,999 (0,0 % de las viviendas por debajo de 0,8).

**Limitaciones.**

- La fracción de casas del catastro en los estratos 1-2 queda fuera del intervalo de la ECV, así que el puente entre la posición y el tipo de vivienda de la ECV es aproximado.
- Las habitaciones del catastro difieren de los dormitorios de la ECV en los estratos 1, 2 (fuera del intervalo del 95 %).
- Lo definen la posición y el bloque de estratos; no depende de las variables de agrupamiento.

## S34-1 · Sin cubierta, estratos 3-4

**Identificación.** 58.846 viviendas (17,7 % de la ciudad) en 5.114 edificios. Posición: sin cubierta (apartamento intermedio o primer piso con vivienda encima). Agrupamiento: K-Means en el estrato «sin cubierta · 3-4», con 1 grupo(s).

**Definición.** Rasgos típicos (percentiles 25 a 75): área de 53 a 86 m² (mediana 68 m²); 1 piso(s) en la unidad; piso 4 del edificio (mediana).

Reglas principales del árbol de asignación (Paso 5):

- posición: sin cubierta · bloque de estratos: 3-4 (48.933 viviendas de entrenamiento)

**Rasgos físicos.**

| Rasgo | Valor |
| --- | --- |
| Área (m²), mediana (P25–P75) | 68 (53–86) |
| Pisos de la unidad, mediana | 1 |
| Piso de la unidad, mediana | 4 |
| En propiedad horizontal | 98,4 % |
| En multifamiliar (4 pisos o más) | 87,3 % |
| Época: antes de 1990 / 1990–2009 / 2010 o después | 8,0 / 22,6 / 69,3 % |
| Estratos | E3 45,1 %, E4 54,9 % |

**Carga simplificada (índice del Paso 3).** Mediana de 14.947 kWh térmicos al año por vivienda y 219 kWh por m².

**Envolvente (priors del Paso 6).**

| Parámetro | Media | Intervalo del 90 % |
| --- | --- | --- |
| Muros de mampostería | 99 % | 97 %–100 % |
| U del muro (W/m²K) | 3,00 | 2,25–3,77 |
| Absortancia del muro | 0,67 | 0,52–0,82 |
| Capacidad C_m (kJ/K por m² de piso) | 264 | 193–336 |
| Infiltración con ventanas cerradas (renovaciones por hora) | 0,96 | 0,50–1,64 |
| Pisos con acabado | 100 % | 99 %–100 % |
| Relación ventana-muro | 0,17 | 0,09–0,26 |
| U de la ventana (W/m²K) | 5,90 | 5,48–6,32 |
| Factor solar del vidrio | 0,82 | 0,77–0,86 |
| Factor de sombra | 0,73 | 0,57–0,88 |
| Fracción climatizada (habitaciones) | 0,31 | 0,15–0,49 |
| Techo | no expuesto (hay otra vivienda encima) | |

**Hogar.**

| Atributo | Valor |
| --- | --- |
| Habitaciones según el catastro, mediana (media) | 3 (2,8) |
| Dormitorios según la ECV, media | 2,1 (± 0,3) |
| Personas por hogar según la ECV | 2,9 (± 0,3) |
| Hogares con aire acondicionado | 64 % (± 8 puntos) |
| Hogares con ventilador | 99 % (± 1 puntos) |
| Hogares con nevera | 98 % (± 2 puntos) |
| Hogares con lavadora | 92 % (± 6 puntos) |
| Hogares con televisor plano | 95 % (± 4 puntos) |
| Hogares con calentador de agua o ducha eléctrica | 4 % (± 3 puntos) |

**Calidad.** Estabilidad (Jaccard): 1,00. Recall en la prueba: árbol 1,000, Random Forest 1,000. Probabilidad media de asignación: 1,000 (0,0 % de las viviendas por debajo de 0,8).

**Limitaciones.**

- La fracción de casas del catastro en los estratos 3-4 queda fuera del intervalo de la ECV, así que el puente entre la posición y el tipo de vivienda de la ECV es aproximado.
- Las habitaciones del catastro difieren de los dormitorios de la ECV en los estratos 3, 4 (fuera del intervalo del 95 %).
- Lo definen la posición y el bloque de estratos; no depende de las variables de agrupamiento.

## S56-1 · Sin cubierta, estratos 5-6

**Identificación.** 22.034 viviendas (6,6 % de la ciudad) en 1.549 edificios. Posición: sin cubierta (apartamento intermedio o primer piso con vivienda encima). Agrupamiento: K-Means en el estrato «sin cubierta · 5-6», con 1 grupo(s).

**Definición.** Rasgos típicos (percentiles 25 a 75): área de 84 a 161 m² (mediana 117 m²); 1 piso(s) en la unidad; piso 4 del edificio (mediana).

Reglas principales del árbol de asignación (Paso 5):

- posición: sin cubierta · bloque de estratos: 5-6 (18.966 viviendas de entrenamiento)

**Rasgos físicos.**

| Rasgo | Valor |
| --- | --- |
| Área (m²), mediana (P25–P75) | 117 (84–161) |
| Pisos de la unidad, mediana | 1 |
| Piso de la unidad, mediana | 4 |
| En propiedad horizontal | 98,7 % |
| En multifamiliar (4 pisos o más) | 93,1 % |
| Época: antes de 1990 / 1990–2009 / 2010 o después | 4,1 / 33,6 / 62,3 % |
| Estratos | E5 52,3 %, E6 47,7 % |

**Carga simplificada (índice del Paso 3).** Mediana de 23.372 kWh térmicos al año por vivienda y 199 kWh por m².

**Envolvente (priors del Paso 6).**

| Parámetro | Media | Intervalo del 90 % |
| --- | --- | --- |
| Muros de mampostería | 100 % | 100 %–100 % |
| U del muro (W/m²K) | 3,00 | 2,24–3,75 |
| Absortancia del muro | 0,67 | 0,51–0,82 |
| Capacidad C_m (kJ/K por m² de piso) | 265 | 196–336 |
| Infiltración con ventanas cerradas (renovaciones por hora) | 0,96 | 0,50–1,63 |
| Pisos con acabado | 100 % | 97 %–100 % |
| Relación ventana-muro | 0,30 | 0,23–0,37 |
| U de la ventana (W/m²K) | 5,89 | 5,49–6,31 |
| Factor solar del vidrio | 0,82 | 0,77–0,86 |
| Factor de sombra | 0,73 | 0,57–0,88 |
| Fracción climatizada (toda) | 0,90 | 0,77–0,99 |
| Techo | no expuesto (hay otra vivienda encima) | |

**Hogar.**

| Atributo | Valor |
| --- | --- |
| Habitaciones según el catastro, mediana (media) | 3 (3,0) |
| Dormitorios según la ECV, media | 2,2 (± 0,4) |
| Personas por hogar según la ECV | 3,0 (± 0,5) |
| Hogares con aire acondicionado | 90 % (± 7 puntos) |
| Hogares con ventilador | 98 % (± 3 puntos) |
| Hogares con nevera | 100 % (± 0 puntos) |
| Hogares con lavadora | 94 % (± 6 puntos) |
| Hogares con televisor plano | 97 % (± 4 puntos) |
| Hogares con calentador de agua o ducha eléctrica | 35 % (± 13 puntos) |

**Calidad.** Estabilidad (Jaccard): 1,00. Recall en la prueba: árbol 1,000, Random Forest 1,000. Probabilidad media de asignación: 1,000 (0,0 % de las viviendas por debajo de 0,8).

**Limitaciones.**

- Las habitaciones del catastro difieren de los dormitorios de la ECV en los estratos 5, 6 (fuera del intervalo del 95 %).
- Lo definen la posición y el bloque de estratos; no depende de las variables de agrupamiento.

## U12-1 · Último piso, estratos 1-2

**Identificación.** 11.992 viviendas (3,6 % de la ciudad) en 5.443 edificios. Posición: último piso. Agrupamiento: K-Means en el estrato «último piso · 1-2», con 1 grupo(s).

**Definición.** Rasgos típicos (percentiles 25 a 75): área de 43 a 106 m² (mediana 55 m²); 1 piso(s) en la unidad; piso 4 del edificio (mediana).

Reglas principales del árbol de asignación (Paso 5):

- posición: último piso · bloque de estratos: 1-2 (9.417 viviendas de entrenamiento)

**Rasgos físicos.**

| Rasgo | Valor |
| --- | --- |
| Área (m²), mediana (P25–P75) | 55 (43–106) |
| Pisos de la unidad, mediana | 1 |
| Piso de la unidad, mediana | 4 |
| En propiedad horizontal | 61,7 % |
| En multifamiliar (4 pisos o más) | 51,6 % |
| Época: antes de 1990 / 1990–2009 / 2010 o después | 20,2 / 19,5 / 60,3 % |
| Estratos | E1 60,5 %, E2 39,5 % |

**Carga simplificada (índice del Paso 3).** Mediana de 28.808 kWh térmicos al año por vivienda y 529 kWh por m².

**Envolvente (priors del Paso 6).**

| Parámetro | Media | Intervalo del 90 % |
| --- | --- | --- |
| Techo de concreto | 69 % | 65 %–73 % |
| Techo de asbesto-cemento | 28 % | 23 %–32 % |
| Techo metálico o de zinc | 3 % | 2 %–6 % |
| Techo de otro material | 0 % | 0 %–0 % |
| U del techo (W/m²K) | 4,07 | 3,37–5,43 |
| Absortancia del techo | 0,68 | 0,42–0,88 |
| Muros de mampostería | 99 % | 98 %–100 % |
| U del muro (W/m²K) | 3,28 | 2,35–3,94 |
| Absortancia del muro | 0,67 | 0,52–0,82 |
| Capacidad C_m (kJ/K por m² de piso) | 237 | 143–329 |
| Infiltración con ventanas cerradas (renovaciones por hora) | 1,40 | 0,53–3,50 |
| Pisos con acabado | 80 % | 74 %–86 % |
| Relación ventana-muro | 0,30 | 0,17–0,44 |
| U de la ventana (W/m²K) | 5,90 | 5,49–6,31 |
| Factor solar del vidrio | 0,82 | 0,77–0,86 |
| Factor de sombra | 0,73 | 0,57–0,88 |
| Fracción climatizada (una) | 0,18 | 0,05–0,30 |

**Hogar.**

| Atributo | Valor |
| --- | --- |
| Habitaciones según el catastro, mediana (media) | 3 (2,9) |
| Dormitorios según la ECV, media | 2,1 (± 0,1) |
| Personas por hogar según la ECV | 3,8 (± 0,2) |
| Hogares con aire acondicionado | 21 % (± 5 puntos) |
| Hogares con ventilador | 99 % (± 1 puntos) |
| Hogares con nevera | 89 % (± 3 puntos) |
| Hogares con lavadora | 57 % (± 7 puntos) |
| Hogares con televisor plano | 74 % (± 6 puntos) |
| Hogares con calentador de agua o ducha eléctrica | 1 % (± 1 puntos) |

**Calidad.** Estabilidad (Jaccard): 1,00. Recall en la prueba: árbol 1,000, Random Forest 1,000. Probabilidad media de asignación: 0,998 (0,0 % de las viviendas por debajo de 0,8).

**Limitaciones.**

- Techo: concreto en los multifamiliares (supuesto S6) y, en los de baja altura, el reparto de los apartamentos de la ECV (Nota 5).
- La fracción de casas del catastro en los estratos 1-2 queda fuera del intervalo de la ECV, así que el puente entre la posición y el tipo de vivienda de la ECV es aproximado.
- Las habitaciones del catastro difieren de los dormitorios de la ECV en los estratos 1, 2 (fuera del intervalo del 95 %).
- Lo definen la posición y el bloque de estratos; no depende de las variables de agrupamiento.

## U34-1 · Último piso, estratos 3-4

**Identificación.** 14.105 viviendas (4,2 % de la ciudad) en 6.325 edificios. Posición: último piso. Agrupamiento: K-Means en el estrato «último piso · 3-4», con 1 grupo(s).

**Definición.** Rasgos típicos (percentiles 25 a 75): área de 62 a 112 m² (mediana 81 m²); 1 piso(s) en la unidad; piso 3 del edificio (mediana).

Reglas principales del árbol de asignación (Paso 5):

- posición: último piso · bloque de estratos: 3-4 (10.611 viviendas de entrenamiento)

**Rasgos físicos.**

| Rasgo | Valor |
| --- | --- |
| Área (m²), mediana (P25–P75) | 81 (62–112) |
| Pisos de la unidad, mediana | 1 |
| Piso de la unidad, mediana | 3 |
| En propiedad horizontal | 84,7 % |
| En multifamiliar (4 pisos o más) | 50,8 % |
| Época: antes de 1990 / 1990–2009 / 2010 o después | 17,0 / 29,4 / 53,6 % |
| Estratos | E3 54,1 %, E4 45,9 % |

**Carga simplificada (índice del Paso 3).** Mediana de 39.903 kWh térmicos al año por vivienda y 514 kWh por m².

**Envolvente (priors del Paso 6).**

| Parámetro | Media | Intervalo del 90 % |
| --- | --- | --- |
| Techo de concreto | 86 % | 80 %–91 % |
| Techo de asbesto-cemento | 13 % | 8 %–19 % |
| Techo metálico o de zinc | 0 % | 0 %–0 % |
| Techo de otro material | 1 % | 0 %–4 % |
| U del techo (W/m²K) | 3,97 | 3,42–4,82 |
| Absortancia del techo | 0,69 | 0,43–0,89 |
| Muros de mampostería | 99 % | 97 %–100 % |
| U del muro (W/m²K) | 3,01 | 2,25–3,77 |
| Absortancia del muro | 0,67 | 0,51–0,82 |
| Capacidad C_m (kJ/K por m² de piso) | 251 | 158–332 |
| Infiltración con ventanas cerradas (renovaciones por hora) | 1,15 | 0,52–2,51 |
| Pisos con acabado | 100 % | 99 %–100 % |
| Relación ventana-muro | 0,17 | 0,08–0,26 |
| U de la ventana (W/m²K) | 5,89 | 5,48–6,30 |
| Factor solar del vidrio | 0,82 | 0,77–0,86 |
| Factor de sombra | 0,73 | 0,57–0,88 |
| Fracción climatizada (habitaciones) | 0,26 | 0,10–0,45 |

**Hogar.**

| Atributo | Valor |
| --- | --- |
| Habitaciones según el catastro, mediana (media) | 3 (2,9) |
| Dormitorios según la ECV, media | 2,1 (± 0,2) |
| Personas por hogar según la ECV | 2,9 (± 0,3) |
| Hogares con aire acondicionado | 61 % (± 8 puntos) |
| Hogares con ventilador | 98 % (± 2 puntos) |
| Hogares con nevera | 98 % (± 2 puntos) |
| Hogares con lavadora | 92 % (± 5 puntos) |
| Hogares con televisor plano | 94 % (± 4 puntos) |
| Hogares con calentador de agua o ducha eléctrica | 4 % (± 3 puntos) |

**Calidad.** Estabilidad (Jaccard): 1,00. Recall en la prueba: árbol 1,000, Random Forest 1,000. Probabilidad media de asignación: 1,000 (0,0 % de las viviendas por debajo de 0,8).

**Limitaciones.**

- Techo: concreto en los multifamiliares (supuesto S6) y, en los de baja altura, el reparto de los apartamentos de la ECV (Nota 5).
- La fracción de casas del catastro en los estratos 3-4 queda fuera del intervalo de la ECV, así que el puente entre la posición y el tipo de vivienda de la ECV es aproximado.
- Las habitaciones del catastro difieren de los dormitorios de la ECV en los estratos 3, 4 (fuera del intervalo del 95 %).
- Lo definen la posición y el bloque de estratos; no depende de las variables de agrupamiento.

## U56-1 · Último piso, estratos 5-6

**Identificación.** 3.800 viviendas (1,1 % de la ciudad) en 1.643 edificios. Posición: último piso. Agrupamiento: K-Means en el estrato «último piso · 5-6», con 1 grupo(s).

**Definición.** Rasgos típicos (percentiles 25 a 75): área de 94 a 194 m² (mediana 126 m²); 1 piso(s) en la unidad; piso 5 del edificio (mediana).

Reglas principales del árbol de asignación (Paso 5):

- posición: último piso · bloque de estratos: 5-6 (3.192 viviendas de entrenamiento)

**Rasgos físicos.**

| Rasgo | Valor |
| --- | --- |
| Área (m²), mediana (P25–P75) | 126 (94–194) |
| Pisos de la unidad, mediana | 1 |
| Piso de la unidad, mediana | 5 |
| En propiedad horizontal | 90,6 % |
| En multifamiliar (4 pisos o más) | 80,0 % |
| Época: antes de 1990 / 1990–2009 / 2010 o después | 8,7 / 40,7 / 50,6 % |
| Estratos | E5 63,4 %, E6 36,6 % |

**Carga simplificada (índice del Paso 3).** Mediana de 59.190 kWh térmicos al año por vivienda y 496 kWh por m².

**Envolvente (priors del Paso 6).**

| Parámetro | Media | Intervalo del 90 % |
| --- | --- | --- |
| Techo de concreto | 98 % | 95 %–100 % |
| Techo de asbesto-cemento | 2 % | 0 %–5 % |
| Techo metálico o de zinc | 0 % | 0 %–0 % |
| Techo de otro material | 0 % | 0 %–0 % |
| U del techo (W/m²K) | 3,92 | 3,45–4,58 |
| Absortancia del techo | 0,70 | 0,43–0,89 |
| Muros de mampostería | 100 % | 100 %–100 % |
| U del muro (W/m²K) | 3,00 | 2,25–3,76 |
| Absortancia del muro | 0,67 | 0,52–0,82 |
| Capacidad C_m (kJ/K por m² de piso) | 263 | 191–335 |
| Infiltración con ventanas cerradas (renovaciones por hora) | 0,98 | 0,50–1,69 |
| Pisos con acabado | 100 % | 98 %–100 % |
| Relación ventana-muro | 0,30 | 0,23–0,37 |
| U de la ventana (W/m²K) | 5,89 | 5,48–6,31 |
| Factor solar del vidrio | 0,82 | 0,78–0,86 |
| Factor de sombra | 0,73 | 0,57–0,88 |
| Fracción climatizada (toda) | 0,90 | 0,77–0,99 |

**Hogar.**

| Atributo | Valor |
| --- | --- |
| Habitaciones según el catastro, mediana (media) | 3 (3,1) |
| Dormitorios según la ECV, media | 2,1 (± 0,4) |
| Personas por hogar según la ECV | 2,9 (± 0,5) |
| Hogares con aire acondicionado | 88 % (± 9 puntos) |
| Hogares con ventilador | 98 % (± 4 puntos) |
| Hogares con nevera | 100 % (± 0 puntos) |
| Hogares con lavadora | 93 % (± 8 puntos) |
| Hogares con televisor plano | 96 % (± 5 puntos) |
| Hogares con calentador de agua o ducha eléctrica | 30 % (± 12 puntos) |

**Calidad.** Estabilidad (Jaccard): 1,00. Recall en la prueba: árbol 1,000, Random Forest 1,000. Probabilidad media de asignación: 0,999 (0,0 % de las viviendas por debajo de 0,8).

**Limitaciones.**

- Techo: concreto en los multifamiliares (supuesto S6) y, en los de baja altura, el reparto de los apartamentos de la ECV (Nota 5).
- Las habitaciones del catastro difieren de los dormitorios de la ECV en los estratos 5, 6 (fuera del intervalo del 95 %).
- Lo definen la posición y el bloque de estratos; no depende de las variables de agrupamiento.
