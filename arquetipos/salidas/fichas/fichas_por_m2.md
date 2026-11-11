# Fichas de los arquetipos: solución con carga por m² (10 arquetipos)

Preregistro de la Fase 1, versión 5, Sección 10.5. Solo agregados. La carga es el índice simplificado del Paso 3, con una envolvente común para todas las viviendas; no es la carga simulada de la Fase 2. Los priors de envolvente son los del Paso 6 (media e intervalo del 90 %) y los atributos del hogar salen de la ECV 2024 por estrato, llevados a cada arquetipo con su composición de estratos.

## C12-1 · Casa, estratos 1-2

**Identificación.** 119.477 viviendas (35,9 % de la ciudad) en 102.690 edificios. Posición: casa. Agrupamiento: K-Means en el estrato «casa · 1-2», con 2 grupo(s).

**Definición.** Rasgos típicos (percentiles 25 a 75): área de 51 a 96 m² (mediana 69 m²); 1 piso(s) en la unidad; piso 1 del edificio (mediana).

Reglas principales del árbol de asignación (Paso 5):

- pisos de la unidad ≤ 1 · posición: casa · bloque de estratos: 1-2 (93.945 viviendas de entrenamiento)

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
| Techo de concreto | 18 % | 11 %–26 % |
| Techo de asbesto-cemento | 67 % | 58 %–76 % |
| Techo metálico o de zinc | 14 % | 8 %–22 % |
| Techo de otro material | 0 % | 0 %–0 % |
| U del techo (W/m²K) | 4,34 | 2,94–5,91 |
| Absortancia del techo | 0,64 | 0,41–0,86 |
| Muros de mampostería | 98 % | 96 %–100 % |
| U del muro (W/m²K) | 2,77 | 2,11–3,65 |
| Absortancia del muro | 0,67 | 0,51–0,82 |
| Capacidad C_m (kJ/K por m² de piso) | 194 | 130–292 |
| Infiltración con ventanas cerradas (renovaciones por hora) | 2,07 | 0,65–4,71 |
| Pisos con acabado | 77 % | 69 %–85 % |
| Relación ventana-muro | 0,30 | 0,16–0,44 |
| U de la ventana (W/m²K) | 5,89 | 5,48–6,30 |
| Factor solar del vidrio | 0,82 | 0,78–0,86 |
| Factor de sombra | 0,90 | 0,77–0,99 |
| Fracción climatizada (una) | 0,18 | 0,07–0,38 |

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

**Calidad.** Estabilidad (Jaccard): 0,99. Fidelidad a la regla de asignación (recall en la prueba): árbol 1,000, Random Forest 1,000. Probabilidad media de pertenecer a este arquetipo al repetir el agrupamiento en las submuestras de estabilidad: 1,000 (0,0 % de las viviendas por debajo de 0,8).

**Limitaciones.**

- Comparte con C12-2 el prior de materiales de la ECV, que no distingue tamaño ni época dentro de la misma posición y bloque; los atributos del hogar solo cambian por la composición de estratos.
- La fracción de casas del catastro en los estratos 1-2 queda fuera del intervalo de la ECV, así que el puente entre la posición y el tipo de vivienda de la ECV es aproximado; la sensibilidad de la Fase 2 lo trata como un factor (AJ22).
- Las habitaciones del catastro difieren de los dormitorios de la ECV en los estratos 1, 2 (fuera del intervalo del 95 %).
- Su frontera con los demás grupos del estrato depende de: pisos de la unidad (Sección 10.4).

## C12-2 · Casa, estratos 1-2

**Identificación.** 9.168 viviendas (2,8 % de la ciudad) en 8.019 edificios. Posición: casa. Agrupamiento: K-Means en el estrato «casa · 1-2», con 2 grupo(s).

**Definición.** Rasgos típicos (percentiles 25 a 75): área de 65 a 140 m² (mediana 104 m²); 2 piso(s) en la unidad; piso 1 del edificio (mediana).

Reglas principales del árbol de asignación (Paso 5):

- pisos de la unidad ≥ 2 · posición: casa · bloque de estratos: 1-2 (7.472 viviendas de entrenamiento)

**Rasgos físicos.**

| Rasgo | Valor |
| --- | --- |
| Área (m²), mediana (P25–P75) | 104 (65–140) |
| Pisos de la unidad, mediana | 2 |
| Piso de la unidad, mediana | 1 |
| En propiedad horizontal | 16,1 % |
| En multifamiliar (4 pisos o más) | 0,0 % |
| Época: antes de 1990 / 1990–2009 / 2010 o después | 40,7 / 25,8 / 33,5 % |
| Estratos | E1 39,1 %, E2 60,9 % |

**Carga simplificada (índice del Paso 3).** Mediana de 39.770 kWh térmicos al año por vivienda y 382 kWh por m².

**Envolvente (priors del Paso 6).**

| Parámetro | Media | Intervalo del 90 % |
| --- | --- | --- |
| Techo de concreto | 18 % | 11 %–26 % |
| Techo de asbesto-cemento | 67 % | 57 %–76 % |
| Techo metálico o de zinc | 14 % | 8 %–22 % |
| Techo de otro material | 0 % | 0 %–0 % |
| U del techo (W/m²K) | 4,35 | 2,91–5,92 |
| Absortancia del techo | 0,64 | 0,41–0,87 |
| Muros de mampostería | 98 % | 95 %–100 % |
| U del muro (W/m²K) | 2,79 | 2,11–3,69 |
| Absortancia del muro | 0,67 | 0,52–0,82 |
| Capacidad C_m (kJ/K por m² de piso) | 193 | 129–291 |
| Infiltración con ventanas cerradas (renovaciones por hora) | 2,11 | 0,63–4,83 |
| Pisos con acabado | 77 % | 69 %–85 % |
| Relación ventana-muro | 0,30 | 0,16–0,44 |
| U de la ventana (W/m²K) | 5,89 | 5,49–6,31 |
| Factor solar del vidrio | 0,82 | 0,77–0,86 |
| Factor de sombra | 0,90 | 0,77–0,99 |
| Fracción climatizada (una) | 0,14 | 0,04–0,46 |

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

**Calidad.** Estabilidad (Jaccard): 0,99. Fidelidad a la regla de asignación (recall en la prueba): árbol 1,000, Random Forest 1,000. Probabilidad media de pertenecer a este arquetipo al repetir el agrupamiento en las submuestras de estabilidad: 0,990 (0,0 % de las viviendas por debajo de 0,8; se confunde sobre todo con C12-1).

**Limitaciones.**

- Comparte con C12-1 el prior de materiales de la ECV, que no distingue tamaño ni época dentro de la misma posición y bloque; los atributos del hogar solo cambian por la composición de estratos.
- La fracción de casas del catastro en los estratos 1-2 queda fuera del intervalo de la ECV, así que el puente entre la posición y el tipo de vivienda de la ECV es aproximado; la sensibilidad de la Fase 2 lo trata como un factor (AJ22).
- Las habitaciones del catastro difieren de los dormitorios de la ECV en los estratos 1, 2 (fuera del intervalo del 95 %).
- Su frontera con los demás grupos del estrato depende de: pisos de la unidad (Sección 10.4).

## C34-1 · Casa, estratos 3-4

**Identificación.** 48.436 viviendas (14,6 % de la ciudad) en 41.576 edificios. Posición: casa. Agrupamiento: K-Means en el estrato «casa · 3-4», con 1 grupo(s).

**Definición.** Rasgos típicos (percentiles 25 a 75): área de 85 a 160 m² (mediana 116 m²); 1 piso(s) en la unidad; piso 1 del edificio (mediana).

Reglas principales del árbol de asignación (Paso 5):

- posición: casa · bloque de estratos: 3-4 (36.477 viviendas de entrenamiento)

**Rasgos físicos.**

| Rasgo | Valor |
| --- | --- |
| Área (m²), mediana (P25–P75) | 116 (85–160) |
| Pisos de la unidad, mediana | 1 |
| Piso de la unidad, mediana | 1 |
| En propiedad horizontal | 15,5 % |
| En multifamiliar (4 pisos o más) | 0,0 % |
| Época: antes de 1990 / 1990–2009 / 2010 o después | 27,5 / 26,0 / 46,5 % |
| Estratos | E3 78,4 %, E4 21,6 % |

**Carga simplificada (índice del Paso 3).** Mediana de 56.000 kWh térmicos al año por vivienda y 499 kWh por m².

**Envolvente (priors del Paso 6).**

| Parámetro | Media | Intervalo del 90 % |
| --- | --- | --- |
| Techo de concreto | 26 % | 11 %–43 % |
| Techo de asbesto-cemento | 74 % | 57 %–89 % |
| Techo metálico o de zinc | 0 % | 0 %–3 % |
| Techo de otro material | 0 % | 0 %–0 % |
| U del techo (W/m²K) | 4,28 | 2,95–5,80 |
| Absortancia del techo | 0,64 | 0,40–0,87 |
| Muros de mampostería | 100 % | 100 %–100 % |
| U del muro (W/m²K) | 2,89 | 2,19–3,69 |
| Absortancia del muro | 0,67 | 0,52–0,82 |
| Capacidad C_m (kJ/K por m² de piso) | 200 | 133–303 |
| Infiltración con ventanas cerradas (renovaciones por hora) | 1,98 | 0,61–4,54 |
| Pisos con acabado | 97 % | 89 %–100 % |
| Relación ventana-muro | 0,30 | 0,16–0,44 |
| U de la ventana (W/m²K) | 5,89 | 5,49–6,31 |
| Factor solar del vidrio | 0,82 | 0,77–0,86 |
| Factor de sombra | 0,73 | 0,57–0,88 |
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

**Calidad.** Estabilidad (Jaccard): 1,00. Fidelidad a la regla de asignación (recall en la prueba): árbol 1,000, Random Forest 1,000. Probabilidad media de pertenecer a este arquetipo al repetir el agrupamiento en las submuestras de estabilidad: 1,000 (0,0 % de las viviendas por debajo de 0,8).

**Limitaciones.**

- La fracción de casas del catastro en los estratos 3-4 queda fuera del intervalo de la ECV, así que el puente entre la posición y el tipo de vivienda de la ECV es aproximado; la sensibilidad de la Fase 2 lo trata como un factor (AJ22).
- Las habitaciones del catastro difieren de los dormitorios de la ECV en los estratos 3, 4 (fuera del intervalo del 95 %).
- Lo definen la posición y el bloque de estratos; no depende de las variables de agrupamiento.

## C56-1 · Casa, estratos 5-6

**Identificación.** 4.223 viviendas (1,3 % de la ciudad) en 2.977 edificios. Posición: casa. Agrupamiento: K-Means en el estrato «casa · 5-6», con 1 grupo(s).

**Definición.** Rasgos típicos (percentiles 25 a 75): área de 153 a 304 m² (mediana 213 m²); 2 piso(s) en la unidad; piso 1 del edificio (mediana).

Reglas principales del árbol de asignación (Paso 5):

- posición: casa · bloque de estratos: 5-6 (3.619 viviendas de entrenamiento)

**Rasgos físicos.**

| Rasgo | Valor |
| --- | --- |
| Área (m²), mediana (P25–P75) | 213 (153–304) |
| Pisos de la unidad, mediana | 2 |
| Piso de la unidad, mediana | 1 |
| En propiedad horizontal | 35,7 % |
| En multifamiliar (4 pisos o más) | 0,0 % |
| Época: antes de 1990 / 1990–2009 / 2010 o después | 11,0 / 39,3 / 49,7 % |
| Estratos | E5 68,8 %, E6 31,2 % |

**Carga simplificada (índice del Paso 3).** Mediana de 91.010 kWh térmicos al año por vivienda y 389 kWh por m².

**Envolvente (priors del Paso 6).**

| Parámetro | Media | Intervalo del 90 % |
| --- | --- | --- |
| Techo de concreto | 72 % | 42 %–94 % |
| Techo de asbesto-cemento | 27 % | 5 %–56 % |
| Techo metálico o de zinc | 1 % | 0 %–9 % |
| Techo de otro material | 0 % | 0 %–0 % |
| U del techo (W/m²K) | 4,04 | 3,39–5,29 |
| Absortancia del techo | 0,68 | 0,42–0,89 |
| Muros de mampostería | 100 % | 100 %–100 % |
| U del muro (W/m²K) | 2,90 | 2,20–3,71 |
| Absortancia del muro | 0,67 | 0,52–0,82 |
| Capacidad C_m (kJ/K por m² de piso) | 241 | 148–331 |
| Infiltración con ventanas cerradas (renovaciones por hora) | 1,34 | 0,52–3,40 |
| Pisos con acabado | 98 % | 89 %–100 % |
| Relación ventana-muro | 0,30 | 0,23–0,37 |
| U de la ventana (W/m²K) | 5,89 | 5,49–6,31 |
| Factor solar del vidrio | 0,82 | 0,78–0,86 |
| Factor de sombra | 0,73 | 0,58–0,88 |
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

**Calidad.** Estabilidad (Jaccard): 1,00. Fidelidad a la regla de asignación (recall en la prueba): árbol 1,000, Random Forest 1,000. Probabilidad media de pertenecer a este arquetipo al repetir el agrupamiento en las submuestras de estabilidad: 1,000 (0,0 % de las viviendas por debajo de 0,8).

**Limitaciones.**

- La celda de la ECV (casa, estratos 5-6) tiene solo 15 viviendas: los priors de materiales son muy inciertos.
- Las habitaciones del catastro difieren de los dormitorios de la ECV en los estratos 5, 6 (fuera del intervalo del 95 %).
- Lo definen la posición y el bloque de estratos; no depende de las variables de agrupamiento.

## S12-1 · Sin cubierta, estratos 1-2

**Identificación.** 39.976 viviendas (12,0 % de la ciudad) en 2.395 edificios. Posición: sin cubierta (apartamento intermedio o primer piso con vivienda encima). Agrupamiento: K-Means en el estrato «sin cubierta · 1-2», con 1 grupo(s).

**Definición.** Rasgos típicos (percentiles 25 a 75): área de 42 a 56 m² (mediana 46 m²); 1 piso(s) en la unidad; piso 2 del edificio (mediana).

Reglas principales del árbol de asignación (Paso 5):

- posición: sin cubierta · bloque de estratos: 1-2 (24.412 viviendas de entrenamiento)

**Rasgos físicos.**

| Rasgo | Valor |
| --- | --- |
| Área (m²), mediana (P25–P75) | 46 (42–56) |
| Pisos de la unidad, mediana | 1 |
| Piso de la unidad, mediana | 2 |
| En propiedad horizontal | 80,7 % |
| En multifamiliar (4 pisos o más) | 76,1 % |
| Época: antes de 1990 / 1990–2009 / 2010 o después | 6,6 / 12,5 / 80,9 % |
| Estratos | E1 83,4 %, E2 16,6 % |

**Carga simplificada (índice del Paso 3).** Mediana de 10.841 kWh térmicos al año por vivienda y 236 kWh por m².

**Envolvente (priors del Paso 6).**

| Parámetro | Media | Intervalo del 90 % |
| --- | --- | --- |
| Muros de mampostería | 99 % | 98 %–100 % |
| U del muro (W/m²K) | 3,30 | 2,38–3,94 |
| Absortancia del muro | 0,67 | 0,52–0,82 |
| Capacidad C_m (kJ/K por m² de piso) | 264 | 194–336 |
| Infiltración con ventanas cerradas (renovaciones por hora) | 0,96 | 0,51–1,61 |
| Pisos con acabado | 80 % | 74 %–85 % |
| Relación ventana-muro | 0,30 | 0,16–0,44 |
| U de la ventana (W/m²K) | 5,89 | 5,48–6,30 |
| Factor solar del vidrio | 0,82 | 0,78–0,86 |
| Factor de sombra | 0,73 | 0,57–0,88 |
| Fracción climatizada (una) | 0,23 | 0,11–0,32 |
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

**Calidad.** Estabilidad (Jaccard): 1,00. Fidelidad a la regla de asignación (recall en la prueba): árbol 1,000, Random Forest 1,000. Probabilidad media de pertenecer a este arquetipo al repetir el agrupamiento en las submuestras de estabilidad: 1,000 (0,0 % de las viviendas por debajo de 0,8).

**Limitaciones.**

- La fracción de casas del catastro en los estratos 1-2 queda fuera del intervalo de la ECV, así que el puente entre la posición y el tipo de vivienda de la ECV es aproximado; la sensibilidad de la Fase 2 lo trata como un factor (AJ22).
- Las habitaciones del catastro difieren de los dormitorios de la ECV en los estratos 1, 2 (fuera del intervalo del 95 %).
- Lo definen la posición y el bloque de estratos; no depende de las variables de agrupamiento.

## S34-1 · Sin cubierta, estratos 3-4

**Identificación.** 57.711 viviendas (17,4 % de la ciudad) en 5.019 edificios. Posición: sin cubierta (apartamento intermedio o primer piso con vivienda encima). Agrupamiento: K-Means en el estrato «sin cubierta · 3-4», con 1 grupo(s).

**Definición.** Rasgos típicos (percentiles 25 a 75): área de 53 a 86 m² (mediana 68 m²); 1 piso(s) en la unidad; piso 4 del edificio (mediana).

Reglas principales del árbol de asignación (Paso 5):

- posición: sin cubierta · bloque de estratos: 3-4 (48.032 viviendas de entrenamiento)

**Rasgos físicos.**

| Rasgo | Valor |
| --- | --- |
| Área (m²), mediana (P25–P75) | 68 (53–86) |
| Pisos de la unidad, mediana | 1 |
| Piso de la unidad, mediana | 4 |
| En propiedad horizontal | 98,4 % |
| En multifamiliar (4 pisos o más) | 87,4 % |
| Época: antes de 1990 / 1990–2009 / 2010 o después | 8,0 / 22,7 / 69,4 % |
| Estratos | E3 44,9 %, E4 55,1 % |

**Carga simplificada (índice del Paso 3).** Mediana de 14.947 kWh térmicos al año por vivienda y 219 kWh por m².

**Envolvente (priors del Paso 6).**

| Parámetro | Media | Intervalo del 90 % |
| --- | --- | --- |
| Muros de mampostería | 99 % | 97 %–100 % |
| U del muro (W/m²K) | 3,01 | 2,25–3,77 |
| Absortancia del muro | 0,67 | 0,51–0,82 |
| Capacidad C_m (kJ/K por m² de piso) | 263 | 193–337 |
| Infiltración con ventanas cerradas (renovaciones por hora) | 0,97 | 0,50–1,63 |
| Pisos con acabado | 100 % | 99 %–100 % |
| Relación ventana-muro | 0,17 | 0,09–0,26 |
| U de la ventana (W/m²K) | 5,90 | 5,49–6,31 |
| Factor solar del vidrio | 0,82 | 0,77–0,86 |
| Factor de sombra | 0,73 | 0,57–0,88 |
| Fracción climatizada (habitaciones) | 0,31 | 0,15–0,50 |
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

**Calidad.** Estabilidad (Jaccard): 1,00. Fidelidad a la regla de asignación (recall en la prueba): árbol 1,000, Random Forest 1,000. Probabilidad media de pertenecer a este arquetipo al repetir el agrupamiento en las submuestras de estabilidad: 1,000 (0,0 % de las viviendas por debajo de 0,8).

**Limitaciones.**

- La fracción de casas del catastro en los estratos 3-4 queda fuera del intervalo de la ECV, así que el puente entre la posición y el tipo de vivienda de la ECV es aproximado; la sensibilidad de la Fase 2 lo trata como un factor (AJ22).
- Las habitaciones del catastro difieren de los dormitorios de la ECV en los estratos 3, 4 (fuera del intervalo del 95 %).
- Lo definen la posición y el bloque de estratos; no depende de las variables de agrupamiento.

## S56-1 · Sin cubierta, estratos 5-6

**Identificación.** 21.742 viviendas (6,5 % de la ciudad) en 1.536 edificios. Posición: sin cubierta (apartamento intermedio o primer piso con vivienda encima). Agrupamiento: K-Means en el estrato «sin cubierta · 5-6», con 1 grupo(s).

**Definición.** Rasgos típicos (percentiles 25 a 75): área de 85 a 161 m² (mediana 117 m²); 1 piso(s) en la unidad; piso 4 del edificio (mediana).

Reglas principales del árbol de asignación (Paso 5):

- posición: sin cubierta · bloque de estratos: 5-6 (18.696 viviendas de entrenamiento)

**Rasgos físicos.**

| Rasgo | Valor |
| --- | --- |
| Área (m²), mediana (P25–P75) | 117 (85–161) |
| Pisos de la unidad, mediana | 1 |
| Piso de la unidad, mediana | 4 |
| En propiedad horizontal | 98,7 % |
| En multifamiliar (4 pisos o más) | 93,0 % |
| Época: antes de 1990 / 1990–2009 / 2010 o después | 4,0 / 33,7 / 62,3 % |
| Estratos | E5 51,9 %, E6 48,1 % |

**Carga simplificada (índice del Paso 3).** Mediana de 23.372 kWh térmicos al año por vivienda y 199 kWh por m².

**Envolvente (priors del Paso 6).**

| Parámetro | Media | Intervalo del 90 % |
| --- | --- | --- |
| Muros de mampostería | 100 % | 100 %–100 % |
| U del muro (W/m²K) | 3,00 | 2,26–3,75 |
| Absortancia del muro | 0,67 | 0,52–0,82 |
| Capacidad C_m (kJ/K por m² de piso) | 266 | 196–337 |
| Infiltración con ventanas cerradas (renovaciones por hora) | 0,95 | 0,50–1,61 |
| Pisos con acabado | 100 % | 97 %–100 % |
| Relación ventana-muro | 0,30 | 0,23–0,37 |
| U de la ventana (W/m²K) | 5,89 | 5,48–6,30 |
| Factor solar del vidrio | 0,82 | 0,77–0,86 |
| Factor de sombra | 0,73 | 0,58–0,88 |
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
| Hogares con lavadora | 95 % (± 6 puntos) |
| Hogares con televisor plano | 97 % (± 4 puntos) |
| Hogares con calentador de agua o ducha eléctrica | 35 % (± 13 puntos) |

**Calidad.** Estabilidad (Jaccard): 1,00. Fidelidad a la regla de asignación (recall en la prueba): árbol 1,000, Random Forest 1,000. Probabilidad media de pertenecer a este arquetipo al repetir el agrupamiento en las submuestras de estabilidad: 1,000 (0,0 % de las viviendas por debajo de 0,8).

**Limitaciones.**

- Las habitaciones del catastro difieren de los dormitorios de la ECV en los estratos 5, 6 (fuera del intervalo del 95 %).
- Lo definen la posición y el bloque de estratos; no depende de las variables de agrupamiento.

## U12-1 · Último piso, estratos 1-2

**Identificación.** 12.857 viviendas (3,9 % de la ciudad) en 5.443 edificios. Posición: último piso. Agrupamiento: K-Means en el estrato «último piso · 1-2», con 1 grupo(s).

**Definición.** Rasgos típicos (percentiles 25 a 75): área de 42 a 100 m² (mediana 53 m²); 1 piso(s) en la unidad; piso 4 del edificio (mediana).

Reglas principales del árbol de asignación (Paso 5):

- posición: último piso · bloque de estratos: 1-2 (9.776 viviendas de entrenamiento)

**Rasgos físicos.**

| Rasgo | Valor |
| --- | --- |
| Área (m²), mediana (P25–P75) | 53 (42–100) |
| Pisos de la unidad, mediana | 1 |
| Piso de la unidad, mediana | 4 |
| En propiedad horizontal | 64,3 % |
| En multifamiliar (4 pisos o más) | 54,9 % |
| Época: antes de 1990 / 1990–2009 / 2010 o después | 19,5 / 18,3 / 62,1 % |
| Estratos | E1 61,6 %, E2 38,4 % |

**Carga simplificada (índice del Paso 3).** Mediana de 27.836 kWh térmicos al año por vivienda y 533 kWh por m².

**Envolvente (priors del Paso 6).**

| Parámetro | Media | Intervalo del 90 % |
| --- | --- | --- |
| Techo de concreto | 71 % | 67 %–75 % |
| Techo de asbesto-cemento | 26 % | 22 %–30 % |
| Techo metálico o de zinc | 3 % | 1 %–6 % |
| Techo de otro material | 0 % | 0 %–0 % |
| U del techo (W/m²K) | 4,05 | 3,38–5,30 |
| Absortancia del techo | 0,68 | 0,42–0,89 |
| Muros de mampostería | 99 % | 98 %–100 % |
| U del muro (W/m²K) | 3,29 | 2,37–3,94 |
| Absortancia del muro | 0,67 | 0,52–0,82 |
| Capacidad C_m (kJ/K por m² de piso) | 239 | 146–329 |
| Infiltración con ventanas cerradas (renovaciones por hora) | 1,36 | 0,52–3,39 |
| Pisos con acabado | 80 % | 74 %–86 % |
| Relación ventana-muro | 0,30 | 0,16–0,44 |
| U de la ventana (W/m²K) | 5,89 | 5,49–6,31 |
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

**Calidad.** Estabilidad (Jaccard): 1,00. Fidelidad a la regla de asignación (recall en la prueba): árbol 1,000, Random Forest 1,000. Probabilidad media de pertenecer a este arquetipo al repetir el agrupamiento en las submuestras de estabilidad: 1,000 (0,0 % de las viviendas por debajo de 0,8).

**Limitaciones.**

- Techo: concreto en los multifamiliares (supuesto S6) y, en los de baja altura, el reparto de los apartamentos de la ECV (Nota 5).
- La fracción de casas del catastro en los estratos 1-2 queda fuera del intervalo de la ECV, así que el puente entre la posición y el tipo de vivienda de la ECV es aproximado; la sensibilidad de la Fase 2 lo trata como un factor (AJ22).
- Las habitaciones del catastro difieren de los dormitorios de la ECV en los estratos 1, 2 (fuera del intervalo del 95 %).
- Lo definen la posición y el bloque de estratos; no depende de las variables de agrupamiento.

## U34-1 · Último piso, estratos 3-4

**Identificación.** 15.043 viviendas (4,5 % de la ciudad) en 6.328 edificios. Posición: último piso. Agrupamiento: K-Means en el estrato «último piso · 3-4», con 1 grupo(s).

**Definición.** Rasgos típicos (percentiles 25 a 75): área de 61 a 110 m² (mediana 80 m²); 1 piso(s) en la unidad; piso 3 del edificio (mediana).

Reglas principales del árbol de asignación (Paso 5):

- posición: último piso · bloque de estratos: 3-4 (11.385 viviendas de entrenamiento)

**Rasgos físicos.**

| Rasgo | Valor |
| --- | --- |
| Área (m²), mediana (P25–P75) | 80 (61–110) |
| Pisos de la unidad, mediana | 1 |
| Piso de la unidad, mediana | 3 |
| En propiedad horizontal | 85,6 % |
| En multifamiliar (4 pisos o más) | 53,7 % |
| Época: antes de 1990 / 1990–2009 / 2010 o después | 16,8 / 28,9 / 54,3 % |
| Estratos | E3 53,8 %, E4 46,2 % |

**Carga simplificada (índice del Paso 3).** Mediana de 39.401 kWh térmicos al año por vivienda y 514 kWh por m².

**Envolvente (priors del Paso 6).**

| Parámetro | Media | Intervalo del 90 % |
| --- | --- | --- |
| Techo de concreto | 86 % | 81 %–91 % |
| Techo de asbesto-cemento | 12 % | 8 %–17 % |
| Techo metálico o de zinc | 0 % | 0 %–0 % |
| Techo de otro material | 1 % | 0 %–3 % |
| U del techo (W/m²K) | 3,97 | 3,43–4,80 |
| Absortancia del techo | 0,69 | 0,43–0,89 |
| Muros de mampostería | 99 % | 97 %–100 % |
| U del muro (W/m²K) | 3,01 | 2,25–3,76 |
| Absortancia del muro | 0,67 | 0,51–0,81 |
| Capacidad C_m (kJ/K por m² de piso) | 253 | 162–333 |
| Infiltración con ventanas cerradas (renovaciones por hora) | 1,15 | 0,50–2,54 |
| Pisos con acabado | 100 % | 99 %–100 % |
| Relación ventana-muro | 0,17 | 0,09–0,26 |
| U de la ventana (W/m²K) | 5,90 | 5,49–6,32 |
| Factor solar del vidrio | 0,82 | 0,77–0,86 |
| Factor de sombra | 0,73 | 0,57–0,88 |
| Fracción climatizada (habitaciones) | 0,26 | 0,11–0,46 |

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

**Calidad.** Estabilidad (Jaccard): 1,00. Fidelidad a la regla de asignación (recall en la prueba): árbol 1,000, Random Forest 1,000. Probabilidad media de pertenecer a este arquetipo al repetir el agrupamiento en las submuestras de estabilidad: 1,000 (0,0 % de las viviendas por debajo de 0,8).

**Limitaciones.**

- Techo: concreto en los multifamiliares (supuesto S6) y, en los de baja altura, el reparto de los apartamentos de la ECV (Nota 5).
- La fracción de casas del catastro en los estratos 3-4 queda fuera del intervalo de la ECV, así que el puente entre la posición y el tipo de vivienda de la ECV es aproximado; la sensibilidad de la Fase 2 lo trata como un factor (AJ22).
- Las habitaciones del catastro difieren de los dormitorios de la ECV en los estratos 3, 4 (fuera del intervalo del 95 %).
- Lo definen la posición y el bloque de estratos; no depende de las variables de agrupamiento.

## U56-1 · Último piso, estratos 5-6

**Identificación.** 4.085 viviendas (1,2 % de la ciudad) en 1.648 edificios. Posición: último piso. Agrupamiento: K-Means en el estrato «último piso · 5-6», con 1 grupo(s).

**Definición.** Rasgos típicos (percentiles 25 a 75): área de 92 a 190 m² (mediana 122 m²); 1 piso(s) en la unidad; piso 5 del edificio (mediana).

Reglas principales del árbol de asignación (Paso 5):

- posición: último piso · bloque de estratos: 5-6 (3.459 viviendas de entrenamiento)

**Rasgos físicos.**

| Rasgo | Valor |
| --- | --- |
| Área (m²), mediana (P25–P75) | 122 (92–190) |
| Pisos de la unidad, mediana | 1 |
| Piso de la unidad, mediana | 5 |
| En propiedad horizontal | 91,3 % |
| En multifamiliar (4 pisos o más) | 81,3 % |
| Época: antes de 1990 / 1990–2009 / 2010 o después | 8,6 / 39,8 / 51,6 % |
| Estratos | E5 64,9 %, E6 35,1 % |

**Carga simplificada (índice del Paso 3).** Mediana de 57.412 kWh térmicos al año por vivienda y 497 kWh por m².

**Envolvente (priors del Paso 6).**

| Parámetro | Media | Intervalo del 90 % |
| --- | --- | --- |
| Techo de concreto | 98 % | 96 %–100 % |
| Techo de asbesto-cemento | 2 % | 0 %–4 % |
| Techo metálico o de zinc | 0 % | 0 %–0 % |
| Techo de otro material | 0 % | 0 %–0 % |
| U del techo (W/m²K) | 3,91 | 3,45–4,56 |
| Absortancia del techo | 0,70 | 0,43–0,89 |
| Muros de mampostería | 100 % | 100 %–100 % |
| U del muro (W/m²K) | 3,00 | 2,25–3,75 |
| Absortancia del muro | 0,67 | 0,51–0,82 |
| Capacidad C_m (kJ/K por m² de piso) | 264 | 192–337 |
| Infiltración con ventanas cerradas (renovaciones por hora) | 0,97 | 0,50–1,63 |
| Pisos con acabado | 100 % | 97 %–100 % |
| Relación ventana-muro | 0,30 | 0,23–0,37 |
| U de la ventana (W/m²K) | 5,89 | 5,48–6,31 |
| Factor solar del vidrio | 0,82 | 0,77–0,86 |
| Factor de sombra | 0,73 | 0,58–0,88 |
| Fracción climatizada (toda) | 0,90 | 0,77–0,99 |

**Hogar.**

| Atributo | Valor |
| --- | --- |
| Habitaciones según el catastro, mediana (media) | 3 (3,1) |
| Dormitorios según la ECV, media | 2,1 (± 0,4) |
| Personas por hogar según la ECV | 2,8 (± 0,5) |
| Hogares con aire acondicionado | 88 % (± 9 puntos) |
| Hogares con ventilador | 98 % (± 4 puntos) |
| Hogares con nevera | 100 % (± 0 puntos) |
| Hogares con lavadora | 93 % (± 8 puntos) |
| Hogares con televisor plano | 96 % (± 5 puntos) |
| Hogares con calentador de agua o ducha eléctrica | 29 % (± 11 puntos) |

**Calidad.** Estabilidad (Jaccard): 1,00. Fidelidad a la regla de asignación (recall en la prueba): árbol 1,000, Random Forest 1,000. Probabilidad media de pertenecer a este arquetipo al repetir el agrupamiento en las submuestras de estabilidad: 1,000 (0,0 % de las viviendas por debajo de 0,8).

**Limitaciones.**

- Techo: concreto en los multifamiliares (supuesto S6) y, en los de baja altura, el reparto de los apartamentos de la ECV (Nota 5).
- Las habitaciones del catastro difieren de los dormitorios de la ECV en los estratos 5, 6 (fuera del intervalo del 95 %).
- Lo definen la posición y el bloque de estratos; no depende de las variables de agrupamiento.
