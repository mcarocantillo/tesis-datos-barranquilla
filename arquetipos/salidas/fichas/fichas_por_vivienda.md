# Fichas de los arquetipos: solución con carga por vivienda (17 arquetipos)

Preregistro de la Fase 1, versión 5, Sección 10.5. Solo agregados. La carga es el índice simplificado del Paso 3, con una envolvente común para todas las viviendas; no es la carga simulada de la Fase 2. Los priors de envolvente son los del Paso 6 (media e intervalo del 90 %) y los atributos del hogar salen de la ECV 2024 por estrato, llevados a cada arquetipo con su composición de estratos.

## C12-1 · Casa, estratos 1-2

**Identificación.** 31.446 viviendas (9,4 % de la ciudad) en 26.289 edificios. Posición: casa. Agrupamiento: k-prototypes en el estrato «casa · 1-2», con 4 grupo(s).

**Definición.** Rasgos típicos (percentiles 25 a 75): área de 31 a 46 m² (mediana 39 m²); 1 piso(s) en la unidad; piso 1 del edificio (mediana).

Reglas principales del árbol de asignación (Paso 5):

- área entre 20,0 y 45,6 m² · pisos de la unidad ≤ 1 · posición: casa · bloque de estratos: 1-2 o 5-6 · sin PH (14.559 viviendas de entrenamiento)
- área entre 50,6 y 56,9 m² · pisos de la unidad ≤ 1 · posición: casa · bloque de estratos: 1-2 · época: 2010 o después (2.957 viviendas de entrenamiento)
- área entre 46,0 y 50,6 m² · pisos de la unidad ≤ 1 · posición: casa · bloque de estratos: 1-2 o 5-6 · época: 2010 o después (1.844 viviendas de entrenamiento)
- y 5 reglas más (`clf_reglas_arbol_por_vivienda.txt`)

**Rasgos físicos.**

| Rasgo | Valor |
| --- | --- |
| Área (m²), mediana (P25–P75) | 39 (31–46) |
| Pisos de la unidad, mediana | 1 |
| Piso de la unidad, mediana | 1 |
| En propiedad horizontal | 3,0 % |
| En multifamiliar (4 pisos o más) | 0,0 % |
| Época: antes de 1990 / 1990–2009 / 2010 o después | 15,7 / 21,1 / 63,2 % |
| Estratos | E1 66,5 %, E2 33,5 % |

**Carga simplificada (índice del Paso 3).** Mediana de 21.600 kWh térmicos al año por vivienda y 550 kWh por m².

**Envolvente (priors del Paso 6).**

| Parámetro | Media | Intervalo del 90 % |
| --- | --- | --- |
| Techo de concreto | 18 % | 11 %–27 % |
| Techo de asbesto-cemento | 67 % | 58 %–76 % |
| Techo metálico o de zinc | 14 % | 8 %–22 % |
| Techo de otro material | 0 % | 0 %–0 % |
| U del techo (W/m²K) | 4,32 | 2,94–5,91 |
| Absortancia del techo | 0,64 | 0,41–0,87 |
| Muros de mampostería | 98 % | 95 %–100 % |
| U del muro (W/m²K) | 2,79 | 2,11–3,68 |
| Absortancia del muro | 0,67 | 0,52–0,82 |
| Capacidad C_m (kJ/K por m² de piso) | 194 | 130–295 |
| Infiltración con ventanas cerradas (renovaciones por hora) | 2,08 | 0,65–4,72 |
| Pisos con acabado | 77 % | 70 %–85 % |
| Relación ventana-muro | 0,30 | 0,16–0,44 |
| U de la ventana (W/m²K) | 5,89 | 5,48–6,30 |
| Factor solar del vidrio | 0,82 | 0,78–0,86 |
| Factor de sombra | 0,90 | 0,77–0,99 |
| Fracción climatizada (una) | 0,32 | 0,19–0,62 |

**Hogar.**

| Atributo | Valor |
| --- | --- |
| Habitaciones según el catastro, mediana (media) | 2 (1,8) |
| Dormitorios según la ECV, media | 2,1 (± 0,1) |
| Personas por hogar según la ECV | 3,8 (± 0,2) |
| Hogares con aire acondicionado | 20 % (± 4 puntos) |
| Hogares con ventilador | 99 % (± 1 puntos) |
| Hogares con nevera | 88 % (± 4 puntos) |
| Hogares con lavadora | 56 % (± 7 puntos) |
| Hogares con televisor plano | 73 % (± 6 puntos) |
| Hogares con calentador de agua o ducha eléctrica | 1 % (± 1 puntos) |

**Calidad.** Estabilidad (Jaccard): 0,98. Fidelidad a la regla de asignación (recall en la prueba): árbol 1,000, Random Forest 1,000. Probabilidad media de pertenecer a este arquetipo al repetir el agrupamiento en las submuestras de estabilidad: 0,996 (0,0 % de las viviendas por debajo de 0,8; se confunde sobre todo con C12-2).

**Limitaciones.**

- Comparte con C12-2, C12-3, C12-4 el prior de materiales de la ECV, que no distingue tamaño ni época dentro de la misma posición y bloque; los atributos del hogar solo cambian por la composición de estratos.
- Alguna regla del árbol admite el bloque 5-6, donde el arquetipo no tiene viviendas; el árbol los junta porque casi no hay viviendas así en esos estratos. El arquetipo se define por su bloque.
- La fracción de casas del catastro en los estratos 1-2 queda fuera del intervalo de la ECV, así que el puente entre la posición y el tipo de vivienda de la ECV es aproximado; la sensibilidad de la Fase 2 lo trata como un factor (AJ22).
- Las habitaciones del catastro difieren de los dormitorios de la ECV en los estratos 1, 2 (fuera del intervalo del 95 %).
- Su frontera con los demás grupos del estrato depende de: área (Sección 10.4).

## C12-2 · Casa, estratos 1-2

**Identificación.** 52.772 viviendas (15,9 % de la ciudad) en 49.018 edificios. Posición: casa. Agrupamiento: k-prototypes en el estrato «casa · 1-2», con 4 grupo(s).

**Definición.** Rasgos típicos (percentiles 25 a 75): área de 60 a 77 m² (mediana 68 m²); 1 piso(s) en la unidad; piso 1 del edificio (mediana).

Reglas principales del árbol de asignación (Paso 5):

- área entre 56,9 y 82,7 m² · pisos de la unidad ≤ 1 · posición: casa · bloque de estratos: 1-2 (31.597 viviendas de entrenamiento)
- área entre 82,7 y 102,1 m² · pisos de la unidad ≤ 1 · posición: casa · bloque de estratos: 1-2 · época: 1990–2009 (4.579 viviendas de entrenamiento)
- área entre 51,0 y 56,9 m² · pisos de la unidad ≤ 1 · posición: casa · bloque de estratos: 1-2 · época: antes de 1990 o 1990–2009 (3.345 viviendas de entrenamiento)
- y 4 reglas más (`clf_reglas_arbol_por_vivienda.txt`)

**Rasgos físicos.**

| Rasgo | Valor |
| --- | --- |
| Área (m²), mediana (P25–P75) | 68 (60–77) |
| Pisos de la unidad, mediana | 1 |
| Piso de la unidad, mediana | 1 |
| En propiedad horizontal | 3,0 % |
| En multifamiliar (4 pisos o más) | 0,0 % |
| Época: antes de 1990 / 1990–2009 / 2010 o después | 26,1 / 42,8 / 31,0 % |
| Estratos | E1 51,5 %, E2 48,5 % |

**Carga simplificada (índice del Paso 3).** Mediana de 35.568 kWh térmicos al año por vivienda y 523 kWh por m².

**Envolvente (priors del Paso 6).**

| Parámetro | Media | Intervalo del 90 % |
| --- | --- | --- |
| Techo de concreto | 18 % | 11 %–27 % |
| Techo de asbesto-cemento | 67 % | 58 %–76 % |
| Techo metálico o de zinc | 14 % | 8 %–22 % |
| Techo de otro material | 0 % | 0 %–0 % |
| U del techo (W/m²K) | 4,33 | 2,93–5,88 |
| Absortancia del techo | 0,64 | 0,41–0,87 |
| Muros de mampostería | 98 % | 95 %–100 % |
| U del muro (W/m²K) | 2,79 | 2,11–3,69 |
| Absortancia del muro | 0,67 | 0,52–0,82 |
| Capacidad C_m (kJ/K por m² de piso) | 194 | 130–293 |
| Infiltración con ventanas cerradas (renovaciones por hora) | 2,08 | 0,64–4,72 |
| Pisos con acabado | 77 % | 69 %–85 % |
| Relación ventana-muro | 0,30 | 0,16–0,44 |
| U de la ventana (W/m²K) | 5,89 | 5,49–6,31 |
| Factor solar del vidrio | 0,82 | 0,77–0,86 |
| Factor de sombra | 0,90 | 0,77–0,99 |
| Fracción climatizada (una) | 0,16 | 0,11–0,22 |

**Hogar.**

| Atributo | Valor |
| --- | --- |
| Habitaciones según el catastro, mediana (media) | 3 (2,6) |
| Dormitorios según la ECV, media | 2,1 (± 0,1) |
| Personas por hogar según la ECV | 3,8 (± 0,2) |
| Hogares con aire acondicionado | 23 % (± 5 puntos) |
| Hogares con ventilador | 99 % (± 1 puntos) |
| Hogares con nevera | 89 % (± 3 puntos) |
| Hogares con lavadora | 59 % (± 7 puntos) |
| Hogares con televisor plano | 75 % (± 6 puntos) |
| Hogares con calentador de agua o ducha eléctrica | 1 % (± 1 puntos) |

**Calidad.** Estabilidad (Jaccard): 0,97. Fidelidad a la regla de asignación (recall en la prueba): árbol 1,000, Random Forest 1,000. Probabilidad media de pertenecer a este arquetipo al repetir el agrupamiento en las submuestras de estabilidad: 0,985 (2,3 % de las viviendas por debajo de 0,8; se confunde sobre todo con C12-1).

**Limitaciones.**

- Comparte con C12-1, C12-3, C12-4 el prior de materiales de la ECV, que no distingue tamaño ni época dentro de la misma posición y bloque; los atributos del hogar solo cambian por la composición de estratos.
- Alguna regla del árbol admite el bloque 5-6, donde el arquetipo no tiene viviendas; el árbol los junta porque casi no hay viviendas así en esos estratos. El arquetipo se define por su bloque.
- La fracción de casas del catastro en los estratos 1-2 queda fuera del intervalo de la ECV, así que el puente entre la posición y el tipo de vivienda de la ECV es aproximado; la sensibilidad de la Fase 2 lo trata como un factor (AJ22).
- Las habitaciones del catastro difieren de los dormitorios de la ECV en los estratos 1, 2 (fuera del intervalo del 95 %).
- Su frontera con los demás grupos del estrato depende de: área (Sección 10.4).

## C12-3 · Casa, estratos 1-2

**Identificación.** 9.132 viviendas (2,7 % de la ciudad) en 8.018 edificios. Posición: casa. Agrupamiento: k-prototypes en el estrato «casa · 1-2», con 4 grupo(s).

**Definición.** Rasgos típicos (percentiles 25 a 75): área de 65 a 140 m² (mediana 104 m²); 2 piso(s) en la unidad; piso 1 del edificio (mediana).

Reglas principales del árbol de asignación (Paso 5):

- área > 82,7 m² · pisos de la unidad ≥ 2 · posición: casa · bloque de estratos: 1-2 (5.249 viviendas de entrenamiento)
- área entre 50,6 y 82,7 m² · pisos de la unidad ≥ 2 · posición: casa · bloque de estratos: 1-2 (1.495 viviendas de entrenamiento)
- área entre 15,5 y 22,5 m² · pisos de la unidad ≥ 2 · posición: casa · bloque de estratos: 1-2 o 5-6 (499 viviendas de entrenamiento)
- y 4 reglas más (`clf_reglas_arbol_por_vivienda.txt`)

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
| Techo de concreto | 18 % | 11 %–27 % |
| Techo de asbesto-cemento | 67 % | 58 %–76 % |
| Techo metálico o de zinc | 14 % | 8 %–22 % |
| Techo de otro material | 0 % | 0 %–0 % |
| U del techo (W/m²K) | 4,34 | 2,90–5,93 |
| Absortancia del techo | 0,64 | 0,41–0,87 |
| Muros de mampostería | 98 % | 96 %–100 % |
| U del muro (W/m²K) | 2,79 | 2,10–3,71 |
| Absortancia del muro | 0,67 | 0,52–0,82 |
| Capacidad C_m (kJ/K por m² de piso) | 193 | 130–290 |
| Infiltración con ventanas cerradas (renovaciones por hora) | 2,06 | 0,65–4,68 |
| Pisos con acabado | 77 % | 70 %–85 % |
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

**Calidad.** Estabilidad (Jaccard): 1,00. Fidelidad a la regla de asignación (recall en la prueba): árbol 1,000, Random Forest 1,000. Probabilidad media de pertenecer a este arquetipo al repetir el agrupamiento en las submuestras de estabilidad: 1,000 (0,0 % de las viviendas por debajo de 0,8).

**Limitaciones.**

- Comparte con C12-1, C12-2, C12-4 el prior de materiales de la ECV, que no distingue tamaño ni época dentro de la misma posición y bloque; los atributos del hogar solo cambian por la composición de estratos.
- Alguna regla del árbol admite el bloque 5-6, donde el arquetipo no tiene viviendas; el árbol los junta porque casi no hay viviendas así en esos estratos. El arquetipo se define por su bloque.
- La fracción de casas del catastro en los estratos 1-2 queda fuera del intervalo de la ECV, así que el puente entre la posición y el tipo de vivienda de la ECV es aproximado; la sensibilidad de la Fase 2 lo trata como un factor (AJ22).
- Las habitaciones del catastro difieren de los dormitorios de la ECV en los estratos 1, 2 (fuera del intervalo del 95 %).
- Su frontera con los demás grupos del estrato depende de: área (Sección 10.4).

## C12-4 · Casa, estratos 1-2

**Identificación.** 35.247 viviendas (10,6 % de la ciudad) en 34.154 edificios. Posición: casa. Agrupamiento: k-prototypes en el estrato «casa · 1-2», con 4 grupo(s).

**Definición.** Rasgos típicos (percentiles 25 a 75): área de 100 a 143 m² (mediana 116 m²); 1 piso(s) en la unidad; piso 1 del edificio (mediana).

Reglas principales del árbol de asignación (Paso 5):

- área > 103,0 m² · pisos de la unidad ≤ 1 · posición: casa · bloque de estratos: 1-2 (19.570 viviendas de entrenamiento)
- área entre 82,7 y 102,1 m² · pisos de la unidad ≤ 1 · posición: casa · bloque de estratos: 1-2 · época: 2010 o después (6.387 viviendas de entrenamiento)
- área entre 93,3 y 102,1 m² · pisos de la unidad ≤ 1 · posición: casa o último piso · bloque de estratos: 1-2 · época: antes de 1990 (1.056 viviendas de entrenamiento)
- y 4 reglas más (`clf_reglas_arbol_por_vivienda.txt`)

**Rasgos físicos.**

| Rasgo | Valor |
| --- | --- |
| Área (m²), mediana (P25–P75) | 116 (100–143) |
| Pisos de la unidad, mediana | 1 |
| Piso de la unidad, mediana | 1 |
| En propiedad horizontal | 1,7 % |
| En multifamiliar (4 pisos o más) | 0,0 % |
| Época: antes de 1990 / 1990–2009 / 2010 o después | 17,5 / 20,7 / 61,9 % |
| Estratos | E1 45,6 %, E2 54,4 % |

**Carga simplificada (índice del Paso 3).** Mediana de 58.353 kWh térmicos al año por vivienda y 503 kWh por m².

**Envolvente (priors del Paso 6).**

| Parámetro | Media | Intervalo del 90 % |
| --- | --- | --- |
| Techo de concreto | 18 % | 11 %–27 % |
| Techo de asbesto-cemento | 67 % | 57 %–76 % |
| Techo metálico o de zinc | 14 % | 8 %–22 % |
| Techo de otro material | 0 % | 0 %–0 % |
| U del techo (W/m²K) | 4,33 | 2,92–5,88 |
| Absortancia del techo | 0,64 | 0,40–0,86 |
| Muros de mampostería | 98 % | 96 %–100 % |
| U del muro (W/m²K) | 2,79 | 2,12–3,68 |
| Absortancia del muro | 0,67 | 0,51–0,82 |
| Capacidad C_m (kJ/K por m² de piso) | 194 | 129–295 |
| Infiltración con ventanas cerradas (renovaciones por hora) | 2,08 | 0,66–4,73 |
| Pisos con acabado | 77 % | 70 %–85 % |
| Relación ventana-muro | 0,30 | 0,16–0,44 |
| U de la ventana (W/m²K) | 5,90 | 5,49–6,31 |
| Factor solar del vidrio | 0,82 | 0,78–0,86 |
| Factor de sombra | 0,90 | 0,77–0,99 |
| Fracción climatizada (una) | 0,09 | 0,05–0,13 |

**Hogar.**

| Atributo | Valor |
| --- | --- |
| Habitaciones según el catastro, mediana (media) | 3 (3,4) |
| Dormitorios según la ECV, media | 2,2 (± 0,1) |
| Personas por hogar según la ECV | 3,8 (± 0,2) |
| Hogares con aire acondicionado | 24 % (± 6 puntos) |
| Hogares con ventilador | 99 % (± 1 puntos) |
| Hogares con nevera | 89 % (± 3 puntos) |
| Hogares con lavadora | 61 % (± 7 puntos) |
| Hogares con televisor plano | 75 % (± 5 puntos) |
| Hogares con calentador de agua o ducha eléctrica | 1 % (± 1 puntos) |

**Calidad.** Estabilidad (Jaccard): 0,98. Fidelidad a la regla de asignación (recall en la prueba): árbol 1,000, Random Forest 1,000. Probabilidad media de pertenecer a este arquetipo al repetir el agrupamiento en las submuestras de estabilidad: 0,981 (2,4 % de las viviendas por debajo de 0,8; se confunde sobre todo con C12-2).

**Limitaciones.**

- Comparte con C12-1, C12-2, C12-3 el prior de materiales de la ECV, que no distingue tamaño ni época dentro de la misma posición y bloque; los atributos del hogar solo cambian por la composición de estratos.
- La fracción de casas del catastro en los estratos 1-2 queda fuera del intervalo de la ECV, así que el puente entre la posición y el tipo de vivienda de la ECV es aproximado; la sensibilidad de la Fase 2 lo trata como un factor (AJ22).
- Las habitaciones del catastro difieren de los dormitorios de la ECV en los estratos 1, 2 (fuera del intervalo del 95 %).
- Su frontera con los demás grupos del estrato depende de: área (Sección 10.4).

## C34-1 · Casa, estratos 3-4

**Identificación.** 7.859 viviendas (2,4 % de la ciudad) en 6.654 edificios. Posición: casa. Agrupamiento: k-prototypes en el estrato «casa · 3-4», con 6 grupo(s).

**Definición.** Rasgos típicos (percentiles 25 a 75): área de 43 a 67 m² (mediana 56 m²); 1 piso(s) en la unidad; piso 1 del edificio (mediana).

Reglas principales del árbol de asignación (Paso 5):

- área ≤ 50,6 m² · pisos de la unidad ≤ 1 · posición: casa · bloque de estratos: 3-4 (2.141 viviendas de entrenamiento)
- área entre 66,2 y 82,0 m² · pisos de la unidad ≤ 1 · posición: casa · bloque de estratos: 3-4 o 5-6 · época: 2010 o después (1.096 viviendas de entrenamiento)
- área entre 50,6 y 64,5 m² · pisos de la unidad ≤ 1 · posición: casa · bloque de estratos: 3-4 o 5-6 · época: 2010 o después (730 viviendas de entrenamiento)
- y 4 reglas más (`clf_reglas_arbol_por_vivienda.txt`)

**Rasgos físicos.**

| Rasgo | Valor |
| --- | --- |
| Área (m²), mediana (P25–P75) | 56 (43–67) |
| Pisos de la unidad, mediana | 1 |
| Piso de la unidad, mediana | 1 |
| En propiedad horizontal | 19,5 % |
| En multifamiliar (4 pisos o más) | 0,0 % |
| Época: antes de 1990 / 1990–2009 / 2010 o después | 17,4 / 28,8 / 53,7 % |
| Estratos | E3 91,1 %, E4 8,9 % |

**Carga simplificada (índice del Paso 3).** Mediana de 29.779 kWh térmicos al año por vivienda y 532 kWh por m².

**Envolvente (priors del Paso 6).**

| Parámetro | Media | Intervalo del 90 % |
| --- | --- | --- |
| Techo de concreto | 25 % | 11 %–42 % |
| Techo de asbesto-cemento | 74 % | 57 %–89 % |
| Techo metálico o de zinc | 1 % | 0 %–3 % |
| Techo de otro material | 0 % | 0 %–0 % |
| U del techo (W/m²K) | 4,28 | 2,98–5,76 |
| Absortancia del techo | 0,64 | 0,41–0,87 |
| Muros de mampostería | 100 % | 100 %–100 % |
| U del muro (W/m²K) | 2,89 | 2,20–3,70 |
| Absortancia del muro | 0,67 | 0,52–0,82 |
| Capacidad C_m (kJ/K por m² de piso) | 200 | 133–305 |
| Infiltración con ventanas cerradas (renovaciones por hora) | 1,98 | 0,61–4,65 |
| Pisos con acabado | 97 % | 89 %–100 % |
| Relación ventana-muro | 0,30 | 0,16–0,44 |
| U de la ventana (W/m²K) | 5,89 | 5,48–6,31 |
| Factor solar del vidrio | 0,82 | 0,78–0,86 |
| Factor de sombra | 0,73 | 0,57–0,88 |
| Fracción climatizada (una) | 0,23 | 0,13–0,49 |

**Hogar.**

| Atributo | Valor |
| --- | --- |
| Habitaciones según el catastro, mediana (media) | 2 (2,1) |
| Dormitorios según la ECV, media | 2,1 (± 0,2) |
| Personas por hogar según la ECV | 2,9 (± 0,3) |
| Hogares con aire acondicionado | 49 % (± 10 puntos) |
| Hogares con ventilador | 97 % (± 3 puntos) |
| Hogares con nevera | 96 % (± 4 puntos) |
| Hogares con lavadora | 91 % (± 6 puntos) |
| Hogares con televisor plano | 93 % (± 5 puntos) |
| Hogares con calentador de agua o ducha eléctrica | 4 % (± 4 puntos) |

**Calidad.** Estabilidad (Jaccard): 0,91. Fidelidad a la regla de asignación (recall en la prueba): árbol 0,939, Random Forest 1,000. Probabilidad media de pertenecer a este arquetipo al repetir el agrupamiento en las submuestras de estabilidad: 0,939 (8,3 % de las viviendas por debajo de 0,8; se confunde sobre todo con C34-2).

**Limitaciones.**

- Comparte con C34-2, C34-3, C34-4, C34-5, C34-6 el prior de materiales de la ECV, que no distingue tamaño ni época dentro de la misma posición y bloque; los atributos del hogar solo cambian por la composición de estratos.
- Alguna regla del árbol admite el bloque 5-6, donde el arquetipo no tiene viviendas; el árbol los junta porque casi no hay viviendas así en esos estratos. El arquetipo se define por su bloque.
- La fracción de casas del catastro en los estratos 3-4 queda fuera del intervalo de la ECV, así que el puente entre la posición y el tipo de vivienda de la ECV es aproximado; la sensibilidad de la Fase 2 lo trata como un factor (AJ22).
- Las habitaciones del catastro difieren de los dormitorios de la ECV en los estratos 3, 4 (fuera del intervalo del 95 %).
- Su frontera con los demás grupos del estrato depende de: área (Sección 10.4).

## C34-2 · Casa, estratos 3-4

**Identificación.** 10.725 viviendas (3,2 % de la ciudad) en 10.225 edificios. Posición: casa. Agrupamiento: k-prototypes en el estrato «casa · 3-4», con 6 grupo(s).

**Definición.** Rasgos típicos (percentiles 25 a 75): área de 85 a 108 m² (mediana 95 m²); 1 piso(s) en la unidad; piso 1 del edificio (mediana).

Reglas principales del árbol de asignación (Paso 5):

- área entre 82,7 y 114,0 m² · pisos de la unidad ≤ 1 · posición: casa · bloque de estratos: 3-4 o 5-6 · época: antes de 1990 o 1990–2009 · sin PH (3.961 viviendas de entrenamiento)
- área entre 114,0 y 136,1 m² · pisos de la unidad ≤ 1 · posición: casa · bloque de estratos: 3-4 o 5-6 · época: antes de 1990 (1.326 viviendas de entrenamiento)
- área entre 82,7 y 96,8 m² · pisos de la unidad ≤ 1 · posición: casa · bloque de estratos: 3-4 o 5-6 · época: 2010 o después (1.232 viviendas de entrenamiento)
- y 3 reglas más (`clf_reglas_arbol_por_vivienda.txt`)

**Rasgos físicos.**

| Rasgo | Valor |
| --- | --- |
| Área (m²), mediana (P25–P75) | 95 (85–108) |
| Pisos de la unidad, mediana | 1 |
| Piso de la unidad, mediana | 1 |
| En propiedad horizontal | 9,2 % |
| En multifamiliar (4 pisos o más) | 0,0 % |
| Época: antes de 1990 / 1990–2009 / 2010 o después | 56,7 / 28,2 / 15,1 % |
| Estratos | E3 90,9 %, E4 9,1 % |

**Carga simplificada (índice del Paso 3).** Mediana de 48.442 kWh térmicos al año por vivienda y 510 kWh por m².

**Envolvente (priors del Paso 6).**

| Parámetro | Media | Intervalo del 90 % |
| --- | --- | --- |
| Techo de concreto | 26 % | 11 %–43 % |
| Techo de asbesto-cemento | 74 % | 56 %–88 % |
| Techo metálico o de zinc | 0 % | 0 %–3 % |
| Techo de otro material | 0 % | 0 %–0 % |
| U del techo (W/m²K) | 4,27 | 2,96–5,79 |
| Absortancia del techo | 0,64 | 0,40–0,87 |
| Muros de mampostería | 100 % | 100 %–100 % |
| U del muro (W/m²K) | 2,90 | 2,20–3,69 |
| Absortancia del muro | 0,68 | 0,52–0,82 |
| Capacidad C_m (kJ/K por m² de piso) | 200 | 133–304 |
| Infiltración con ventanas cerradas (renovaciones por hora) | 1,99 | 0,62–4,55 |
| Pisos con acabado | 97 % | 90 %–100 % |
| Relación ventana-muro | 0,30 | 0,16–0,43 |
| U de la ventana (W/m²K) | 5,89 | 5,49–6,30 |
| Factor solar del vidrio | 0,82 | 0,77–0,86 |
| Factor de sombra | 0,73 | 0,57–0,88 |
| Fracción climatizada (una) | 0,11 | 0,08–0,15 |

**Hogar.**

| Atributo | Valor |
| --- | --- |
| Habitaciones según el catastro, mediana (media) | 3 (3,0) |
| Dormitorios según la ECV, media | 2,1 (± 0,2) |
| Personas por hogar según la ECV | 2,9 (± 0,3) |
| Hogares con aire acondicionado | 49 % (± 10 puntos) |
| Hogares con ventilador | 97 % (± 3 puntos) |
| Hogares con nevera | 96 % (± 4 puntos) |
| Hogares con lavadora | 91 % (± 6 puntos) |
| Hogares con televisor plano | 93 % (± 5 puntos) |
| Hogares con calentador de agua o ducha eléctrica | 4 % (± 4 puntos) |

**Calidad.** Estabilidad (Jaccard): 0,82. Fidelidad a la regla de asignación (recall en la prueba): árbol 1,000, Random Forest 1,000. Probabilidad media de pertenecer a este arquetipo al repetir el agrupamiento en las submuestras de estabilidad: 0,857 (25,4 % de las viviendas por debajo de 0,8; se confunde sobre todo con C34-6).

**Limitaciones.**

- Comparte con C34-1, C34-3, C34-4, C34-5, C34-6 el prior de materiales de la ECV, que no distingue tamaño ni época dentro de la misma posición y bloque; los atributos del hogar solo cambian por la composición de estratos.
- Alguna regla del árbol admite el bloque 5-6, donde el arquetipo no tiene viviendas; el árbol los junta porque casi no hay viviendas así en esos estratos. El arquetipo se define por su bloque.
- La fracción de casas del catastro en los estratos 3-4 queda fuera del intervalo de la ECV, así que el puente entre la posición y el tipo de vivienda de la ECV es aproximado; la sensibilidad de la Fase 2 lo trata como un factor (AJ22).
- Las habitaciones del catastro difieren de los dormitorios de la ECV en los estratos 3, 4 (fuera del intervalo del 95 %).
- Su frontera con los demás grupos del estrato depende de: área (Sección 10.4).

## C34-3 · Casa, estratos 3-4

**Identificación.** 6.419 viviendas (1,9 % de la ciudad) en 3.787 edificios. Posición: casa. Agrupamiento: k-prototypes en el estrato «casa · 3-4», con 6 grupo(s).

**Definición.** Rasgos típicos (percentiles 25 a 75): área de 87 a 131 m² (mediana 105 m²); 2 piso(s) en la unidad; piso 1 del edificio (mediana).

Reglas principales del árbol de asignación (Paso 5):

- área entre 82,7 y 173,5 m² · pisos de la unidad ≥ 2 · posición: casa · bloque de estratos: 3-4 (3.405 viviendas de entrenamiento)
- área entre 72,3 y 75,5 m² · pisos de la unidad ≥ 2 · posición: casa · bloque de estratos: 3-4 o 5-6 · en propiedad horizontal (388 viviendas de entrenamiento)
- área entre 75,5 y 82,7 m² · pisos de la unidad ≥ 2 · posición: casa · bloque de estratos: 3-4 o 5-6 · en propiedad horizontal (324 viviendas de entrenamiento)
- y 8 reglas más (`clf_reglas_arbol_por_vivienda.txt`)

**Rasgos físicos.**

| Rasgo | Valor |
| --- | --- |
| Área (m²), mediana (P25–P75) | 105 (87–131) |
| Pisos de la unidad, mediana | 2 |
| Piso de la unidad, mediana | 1 |
| En propiedad horizontal | 56,3 % |
| En multifamiliar (4 pisos o más) | 0,0 % |
| Época: antes de 1990 / 1990–2009 / 2010 o después | 21,0 / 32,4 / 46,6 % |
| Estratos | E3 65,4 %, E4 34,6 % |

**Carga simplificada (índice del Paso 3).** Mediana de 39.770 kWh térmicos al año por vivienda y 382 kWh por m².

**Envolvente (priors del Paso 6).**

| Parámetro | Media | Intervalo del 90 % |
| --- | --- | --- |
| Techo de concreto | 26 % | 11 %–43 % |
| Techo de asbesto-cemento | 74 % | 56 %–88 % |
| Techo metálico o de zinc | 0 % | 0 %–3 % |
| Techo de otro material | 0 % | 0 %–0 % |
| U del techo (W/m²K) | 4,27 | 2,92–5,80 |
| Absortancia del techo | 0,64 | 0,40–0,87 |
| Muros de mampostería | 100 % | 100 %–100 % |
| U del muro (W/m²K) | 2,90 | 2,19–3,71 |
| Absortancia del muro | 0,67 | 0,51–0,82 |
| Capacidad C_m (kJ/K por m² de piso) | 200 | 133–304 |
| Infiltración con ventanas cerradas (renovaciones por hora) | 1,97 | 0,63–4,62 |
| Pisos con acabado | 97 % | 89 %–100 % |
| Relación ventana-muro | 0,30 | 0,16–0,44 |
| U de la ventana (W/m²K) | 5,90 | 5,49–6,31 |
| Factor solar del vidrio | 0,82 | 0,78–0,86 |
| Factor de sombra | 0,73 | 0,57–0,88 |
| Fracción climatizada (una) | 0,11 | 0,06–0,17 |

**Hogar.**

| Atributo | Valor |
| --- | --- |
| Habitaciones según el catastro, mediana (media) | 3 (3,2) |
| Dormitorios según la ECV, media | 2,1 (± 0,2) |
| Personas por hogar según la ECV | 2,9 (± 0,3) |
| Hogares con aire acondicionado | 57 % (± 8 puntos) |
| Hogares con ventilador | 98 % (± 2 puntos) |
| Hogares con nevera | 97 % (± 3 puntos) |
| Hogares con lavadora | 91 % (± 5 puntos) |
| Hogares con televisor plano | 94 % (± 4 puntos) |
| Hogares con calentador de agua o ducha eléctrica | 4 % (± 3 puntos) |

**Calidad.** Estabilidad (Jaccard): 0,84. Fidelidad a la regla de asignación (recall en la prueba): árbol 0,988, Random Forest 0,999. Probabilidad media de pertenecer a este arquetipo al repetir el agrupamiento en las submuestras de estabilidad: 0,989 (2,8 % de las viviendas por debajo de 0,8; se confunde sobre todo con C34-6).

**Limitaciones.**

- Comparte con C34-1, C34-2, C34-4, C34-5, C34-6 el prior de materiales de la ECV, que no distingue tamaño ni época dentro de la misma posición y bloque; los atributos del hogar solo cambian por la composición de estratos.
- Alguna regla del árbol admite el bloque 5-6, donde el arquetipo no tiene viviendas; el árbol los junta porque casi no hay viviendas así en esos estratos. El arquetipo se define por su bloque.
- La fracción de casas del catastro en los estratos 3-4 queda fuera del intervalo de la ECV, así que el puente entre la posición y el tipo de vivienda de la ECV es aproximado; la sensibilidad de la Fase 2 lo trata como un factor (AJ22).
- Las habitaciones del catastro difieren de los dormitorios de la ECV en los estratos 3, 4 (fuera del intervalo del 95 %).
- Su frontera con los demás grupos del estrato depende de: área (Sección 10.4).

## C34-4 · Casa, estratos 3-4

**Identificación.** 14.936 viviendas (4,5 % de la ciudad) en 14.554 edificios. Posición: casa. Agrupamiento: k-prototypes en el estrato «casa · 3-4», con 6 grupo(s).

**Definición.** Rasgos típicos (percentiles 25 a 75): área de 120 a 157 m² (mediana 139 m²); 1 piso(s) en la unidad; piso 1 del edificio (mediana).

Reglas principales del árbol de asignación (Paso 5):

- área entre 114,0 y 181,7 m² · pisos de la unidad ≤ 1 · posición: casa · bloque de estratos: 3-4 · época: 1990–2009 o 2010 o después (7.429 viviendas de entrenamiento)
- área entre 96,8 y 114,0 m² · pisos de la unidad ≤ 1 · posición: casa · bloque de estratos: 3-4 o 5-6 · época: 2010 o después (2.104 viviendas de entrenamiento)
- área entre 136,1 y 181,7 m² · pisos de la unidad ≤ 1 · posición: casa · bloque de estratos: 3-4 o 5-6 · época: antes de 1990 (1.850 viviendas de entrenamiento)

**Rasgos físicos.**

| Rasgo | Valor |
| --- | --- |
| Área (m²), mediana (P25–P75) | 139 (120–157) |
| Pisos de la unidad, mediana | 1 |
| Piso de la unidad, mediana | 1 |
| En propiedad horizontal | 6,1 % |
| En multifamiliar (4 pisos o más) | 0,0 % |
| Época: antes de 1990 / 1990–2009 / 2010 o después | 16,5 / 19,7 / 63,8 % |
| Estratos | E3 79,5 %, E4 20,5 % |

**Carga simplificada (índice del Paso 3).** Mediana de 69.138 kWh térmicos al año por vivienda y 497 kWh por m².

**Envolvente (priors del Paso 6).**

| Parámetro | Media | Intervalo del 90 % |
| --- | --- | --- |
| Techo de concreto | 25 % | 11 %–42 % |
| Techo de asbesto-cemento | 74 % | 57 %–88 % |
| Techo metálico o de zinc | 1 % | 0 %–3 % |
| Techo de otro material | 0 % | 0 %–0 % |
| U del techo (W/m²K) | 4,26 | 2,92–5,80 |
| Absortancia del techo | 0,64 | 0,41–0,87 |
| Muros de mampostería | 100 % | 100 %–100 % |
| U del muro (W/m²K) | 2,90 | 2,19–3,71 |
| Absortancia del muro | 0,67 | 0,51–0,82 |
| Capacidad C_m (kJ/K por m² de piso) | 200 | 133–305 |
| Infiltración con ventanas cerradas (renovaciones por hora) | 1,96 | 0,61–4,48 |
| Pisos con acabado | 97 % | 89 %–100 % |
| Relación ventana-muro | 0,30 | 0,16–0,44 |
| U de la ventana (W/m²K) | 5,89 | 5,49–6,30 |
| Factor solar del vidrio | 0,82 | 0,77–0,86 |
| Factor de sombra | 0,73 | 0,57–0,88 |
| Fracción climatizada (una) | 0,08 | 0,06–0,11 |

**Hogar.**

| Atributo | Valor |
| --- | --- |
| Habitaciones según el catastro, mediana (media) | 3 (3,5) |
| Dormitorios según la ECV, media | 2,1 (± 0,2) |
| Personas por hogar según la ECV | 2,9 (± 0,3) |
| Hogares con aire acondicionado | 52 % (± 9 puntos) |
| Hogares con ventilador | 97 % (± 3 puntos) |
| Hogares con nevera | 97 % (± 3 puntos) |
| Hogares con lavadora | 91 % (± 6 puntos) |
| Hogares con televisor plano | 93 % (± 4 puntos) |
| Hogares con calentador de agua o ducha eléctrica | 4 % (± 3 puntos) |

**Calidad.** Estabilidad (Jaccard): 0,83. Fidelidad a la regla de asignación (recall en la prueba): árbol 0,999, Random Forest 0,999. Probabilidad media de pertenecer a este arquetipo al repetir el agrupamiento en las submuestras de estabilidad: 0,849 (41,5 % de las viviendas por debajo de 0,8; se confunde sobre todo con C34-6).

**Limitaciones.**

- Comparte con C34-1, C34-2, C34-3, C34-5, C34-6 el prior de materiales de la ECV, que no distingue tamaño ni época dentro de la misma posición y bloque; los atributos del hogar solo cambian por la composición de estratos.
- Alguna regla del árbol admite el bloque 5-6, donde el arquetipo no tiene viviendas; el árbol los junta porque casi no hay viviendas así en esos estratos. El arquetipo se define por su bloque.
- La fracción de casas del catastro en los estratos 3-4 queda fuera del intervalo de la ECV, así que el puente entre la posición y el tipo de vivienda de la ECV es aproximado; la sensibilidad de la Fase 2 lo trata como un factor (AJ22).
- Las habitaciones del catastro difieren de los dormitorios de la ECV en los estratos 3, 4 (fuera del intervalo del 95 %).
- Su frontera con los demás grupos del estrato depende de: área (Sección 10.4).

## C34-5 · Casa, estratos 3-4

**Identificación.** 6.288 viviendas (1,9 % de la ciudad) en 6.258 edificios. Posición: casa. Agrupamiento: k-prototypes en el estrato «casa · 3-4», con 6 grupo(s).

**Definición.** Rasgos típicos (percentiles 25 a 75): área de 198 a 277 m² (mediana 224 m²); 1 piso(s) en la unidad; piso 1 del edificio (mediana).

Reglas principales del árbol de asignación (Paso 5):

- área > 181,7 m² · pisos de la unidad ≤ 1 · posición: casa · bloque de estratos: 3-4 (4.602 viviendas de entrenamiento)

**Rasgos físicos.**

| Rasgo | Valor |
| --- | --- |
| Área (m²), mediana (P25–P75) | 224 (198–277) |
| Pisos de la unidad, mediana | 1 |
| Piso de la unidad, mediana | 1 |
| En propiedad horizontal | 2,2 % |
| En multifamiliar (4 pisos o más) | 0,0 % |
| Época: antes de 1990 / 1990–2009 / 2010 o después | 25,1 / 23,8 / 51,1 % |
| Estratos | E3 58,3 %, E4 41,7 % |

**Carga simplificada (índice del Paso 3).** Mediana de 108.576 kWh térmicos al año por vivienda y 485 kWh por m².

**Envolvente (priors del Paso 6).**

| Parámetro | Media | Intervalo del 90 % |
| --- | --- | --- |
| Techo de concreto | 25 % | 11 %–43 % |
| Techo de asbesto-cemento | 74 % | 57 %–88 % |
| Techo metálico o de zinc | 1 % | 0 %–3 % |
| Techo de otro material | 0 % | 0 %–0 % |
| U del techo (W/m²K) | 4,27 | 2,93–5,75 |
| Absortancia del techo | 0,64 | 0,41–0,87 |
| Muros de mampostería | 100 % | 100 %–100 % |
| U del muro (W/m²K) | 2,90 | 2,19–3,71 |
| Absortancia del muro | 0,67 | 0,51–0,82 |
| Capacidad C_m (kJ/K por m² de piso) | 200 | 134–304 |
| Infiltración con ventanas cerradas (renovaciones por hora) | 1,97 | 0,62–4,58 |
| Pisos con acabado | 97 % | 89 %–100 % |
| Relación ventana-muro | 0,30 | 0,16–0,44 |
| U de la ventana (W/m²K) | 5,89 | 5,49–6,30 |
| Factor solar del vidrio | 0,82 | 0,77–0,86 |
| Factor de sombra | 0,73 | 0,57–0,88 |
| Fracción climatizada (una) | 0,05 | 0,02–0,06 |

**Hogar.**

| Atributo | Valor |
| --- | --- |
| Habitaciones según el catastro, mediana (media) | 4 (4,5) |
| Dormitorios según la ECV, media | 2,1 (± 0,2) |
| Personas por hogar según la ECV | 2,9 (± 0,3) |
| Hogares con aire acondicionado | 59 % (± 8 puntos) |
| Hogares con ventilador | 98 % (± 2 puntos) |
| Hogares con nevera | 98 % (± 2 puntos) |
| Hogares con lavadora | 92 % (± 5 puntos) |
| Hogares con televisor plano | 94 % (± 4 puntos) |
| Hogares con calentador de agua o ducha eléctrica | 4 % (± 3 puntos) |

**Calidad.** Estabilidad (Jaccard): 0,91. Fidelidad a la regla de asignación (recall en la prueba): árbol 1,000, Random Forest 1,000. Probabilidad media de pertenecer a este arquetipo al repetir el agrupamiento en las submuestras de estabilidad: 0,958 (7,2 % de las viviendas por debajo de 0,8; se confunde sobre todo con C34-6).

**Limitaciones.**

- Comparte con C34-1, C34-2, C34-3, C34-4, C34-6 el prior de materiales de la ECV, que no distingue tamaño ni época dentro de la misma posición y bloque; los atributos del hogar solo cambian por la composición de estratos.
- La fracción de casas del catastro en los estratos 3-4 queda fuera del intervalo de la ECV, así que el puente entre la posición y el tipo de vivienda de la ECV es aproximado; la sensibilidad de la Fase 2 lo trata como un factor (AJ22).
- Las habitaciones del catastro difieren de los dormitorios de la ECV en los estratos 3, 4 (fuera del intervalo del 95 %).
- Su frontera con los demás grupos del estrato depende de: área (Sección 10.4).

## C34-6 · Casa, estratos 3-4

**Identificación.** 2.012 viviendas (0,6 % de la ciudad) en 1.971 edificios. Posición: casa. Agrupamiento: k-prototypes en el estrato «casa · 3-4», con 6 grupo(s).

**Definición.** Rasgos típicos (percentiles 25 a 75): área de 231 a 353 m² (mediana 280 m²); 2 piso(s) en la unidad; piso 1 del edificio (mediana).

Reglas principales del árbol de asignación (Paso 5):

- área > 213,1 m² · pisos de la unidad ≥ 2 · posición: casa · bloque de estratos: 3-4 (1.233 viviendas de entrenamiento)
- área entre 181,7 y 206,9 m² · pisos de la unidad ≥ 2 · posición: casa · bloque de estratos: 3-4 · época: antes de 1990 o 1990–2009 (163 viviendas de entrenamiento)
- área entre 178,9 y 181,7 m² · pisos de la unidad ≥ 2 · posición: casa · bloque de estratos: 3-4 (57 viviendas de entrenamiento)
- y 1 reglas más (`clf_reglas_arbol_por_vivienda.txt`)

**Rasgos físicos.**

| Rasgo | Valor |
| --- | --- |
| Área (m²), mediana (P25–P75) | 280 (231–353) |
| Pisos de la unidad, mediana | 2 |
| Piso de la unidad, mediana | 1 |
| En propiedad horizontal | 5,4 % |
| En multifamiliar (4 pisos o más) | 0,0 % |
| Época: antes de 1990 / 1990–2009 / 2010 o después | 22,7 / 37,0 / 40,3 % |
| Estratos | E3 58,8 %, E4 41,2 % |

**Carga simplificada (índice del Paso 3).** Mediana de 95.767 kWh térmicos al año por vivienda y 344 kWh por m².

**Envolvente (priors del Paso 6).**

| Parámetro | Media | Intervalo del 90 % |
| --- | --- | --- |
| Techo de concreto | 25 % | 11 %–43 % |
| Techo de asbesto-cemento | 74 % | 57 %–89 % |
| Techo metálico o de zinc | 1 % | 0 %–3 % |
| Techo de otro material | 0 % | 0 %–0 % |
| U del techo (W/m²K) | 4,26 | 2,91–5,78 |
| Absortancia del techo | 0,64 | 0,41–0,87 |
| Muros de mampostería | 100 % | 100 %–100 % |
| U del muro (W/m²K) | 2,90 | 2,19–3,70 |
| Absortancia del muro | 0,67 | 0,52–0,82 |
| Capacidad C_m (kJ/K por m² de piso) | 200 | 133–304 |
| Infiltración con ventanas cerradas (renovaciones por hora) | 1,98 | 0,63–4,61 |
| Pisos con acabado | 97 % | 89 %–100 % |
| Relación ventana-muro | 0,30 | 0,16–0,44 |
| U de la ventana (W/m²K) | 5,89 | 5,49–6,31 |
| Factor solar del vidrio | 0,82 | 0,77–0,86 |
| Factor de sombra | 0,73 | 0,57–0,88 |
| Fracción climatizada (una) | 0,04 | 0,02–0,06 |

**Hogar.**

| Atributo | Valor |
| --- | --- |
| Habitaciones según el catastro, mediana (media) | 5 (5,2) |
| Dormitorios según la ECV, media | 2,1 (± 0,2) |
| Personas por hogar según la ECV | 2,9 (± 0,3) |
| Hogares con aire acondicionado | 59 % (± 8 puntos) |
| Hogares con ventilador | 98 % (± 2 puntos) |
| Hogares con nevera | 98 % (± 2 puntos) |
| Hogares con lavadora | 92 % (± 5 puntos) |
| Hogares con televisor plano | 94 % (± 4 puntos) |
| Hogares con calentador de agua o ducha eléctrica | 4 % (± 3 puntos) |

**Calidad.** Estabilidad (Jaccard): 0,76. Fidelidad a la regla de asignación (recall en la prueba): árbol 0,991, Random Forest 0,996. Probabilidad media de pertenecer a este arquetipo al repetir el agrupamiento en las submuestras de estabilidad: 0,643 (100,0 % de las viviendas por debajo de 0,8; se confunde sobre todo con C34-3).

**Limitaciones.**

- Comparte con C34-1, C34-2, C34-3, C34-4, C34-5 el prior de materiales de la ECV, que no distingue tamaño ni época dentro de la misma posición y bloque; los atributos del hogar solo cambian por la composición de estratos.
- La fracción de casas del catastro en los estratos 3-4 queda fuera del intervalo de la ECV, así que el puente entre la posición y el tipo de vivienda de la ECV es aproximado; la sensibilidad de la Fase 2 lo trata como un factor (AJ22).
- Es inestable: al repetir el agrupamiento en las submuestras, sus viviendas caen en él en promedio el 64 % de las veces y si no, sobre todo en C34-3. La Fase 2 sortea el arquetipo de cada vivienda con esas probabilidades.
- Las habitaciones del catastro difieren de los dormitorios de la ECV en los estratos 3, 4 (fuera del intervalo del 95 %).
- Su frontera con los demás grupos del estrato depende de: área (Sección 10.4).

## C56-1 · Casa, estratos 5-6

**Identificación.** 4.216 viviendas (1,3 % de la ciudad) en 2.973 edificios. Posición: casa. Agrupamiento: k-prototypes en el estrato «casa · 5-6», con 1 grupo(s).

**Definición.** Rasgos típicos (percentiles 25 a 75): área de 153 a 304 m² (mediana 213 m²); 2 piso(s) en la unidad; piso 1 del edificio (mediana).

Reglas principales del árbol de asignación (Paso 5):

- área > 181,7 m² · posición: casa · bloque de estratos: 5-6 (2.343 viviendas de entrenamiento)
- área entre 82,7 y 181,7 m² · pisos de la unidad ≥ 2 · posición: casa · bloque de estratos: 5-6 (862 viviendas de entrenamiento)
- área entre 114,0 y 181,7 m² · pisos de la unidad ≤ 1 · posición: casa · bloque de estratos: 5-6 · época: 1990–2009 o 2010 o después (225 viviendas de entrenamiento)

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
| Techo de asbesto-cemento | 26 % | 5 %–56 % |
| Techo metálico o de zinc | 1 % | 0 %–9 % |
| Techo de otro material | 0 % | 0 %–0 % |
| U del techo (W/m²K) | 4,04 | 3,38–5,29 |
| Absortancia del techo | 0,68 | 0,42–0,89 |
| Muros de mampostería | 100 % | 100 %–100 % |
| U del muro (W/m²K) | 2,90 | 2,20–3,70 |
| Absortancia del muro | 0,67 | 0,52–0,82 |
| Capacidad C_m (kJ/K por m² de piso) | 240 | 148–331 |
| Infiltración con ventanas cerradas (renovaciones por hora) | 1,34 | 0,53–3,34 |
| Pisos con acabado | 98 % | 89 %–100 % |
| Relación ventana-muro | 0,30 | 0,23–0,37 |
| U de la ventana (W/m²K) | 5,89 | 5,49–6,31 |
| Factor solar del vidrio | 0,82 | 0,78–0,86 |
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

**Calidad.** Estabilidad (Jaccard): 1,00. Fidelidad a la regla de asignación (recall en la prueba): árbol 0,900, Random Forest 1,000. Probabilidad media de pertenecer a este arquetipo al repetir el agrupamiento en las submuestras de estabilidad: 1,000 (0,0 % de las viviendas por debajo de 0,8).

**Limitaciones.**

- La celda de la ECV (casa, estratos 5-6) tiene solo 15 viviendas: los priors de materiales son muy inciertos.
- Las habitaciones del catastro difieren de los dormitorios de la ECV en los estratos 5, 6 (fuera del intervalo del 95 %).
- Lo definen la posición y el bloque de estratos; no depende de las variables de agrupamiento.

## S12-1 · Sin cubierta, estratos 1-2

**Identificación.** 40.889 viviendas (12,3 % de la ciudad) en 2.403 edificios. Posición: sin cubierta (apartamento intermedio o primer piso con vivienda encima). Agrupamiento: k-prototypes en el estrato «sin cubierta · 1-2», con 1 grupo(s).

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
| U del muro (W/m²K) | 3,29 | 2,37–3,93 |
| Absortancia del muro | 0,67 | 0,51–0,82 |
| Capacidad C_m (kJ/K por m² de piso) | 263 | 193–337 |
| Infiltración con ventanas cerradas (renovaciones por hora) | 0,96 | 0,50–1,63 |
| Pisos con acabado | 80 % | 74 %–85 % |
| Relación ventana-muro | 0,30 | 0,16–0,44 |
| U de la ventana (W/m²K) | 5,89 | 5,48–6,31 |
| Factor solar del vidrio | 0,82 | 0,78–0,86 |
| Factor de sombra | 0,73 | 0,57–0,88 |
| Fracción climatizada (una) | 0,22 | 0,11–0,31 |
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

**Identificación.** 58.846 viviendas (17,7 % de la ciudad) en 5.114 edificios. Posición: sin cubierta (apartamento intermedio o primer piso con vivienda encima). Agrupamiento: k-prototypes en el estrato «sin cubierta · 3-4», con 1 grupo(s).

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
| U del muro (W/m²K) | 3,01 | 2,25–3,76 |
| Absortancia del muro | 0,67 | 0,52–0,82 |
| Capacidad C_m (kJ/K por m² de piso) | 263 | 192–336 |
| Infiltración con ventanas cerradas (renovaciones por hora) | 0,97 | 0,50–1,63 |
| Pisos con acabado | 100 % | 99 %–100 % |
| Relación ventana-muro | 0,17 | 0,08–0,26 |
| U de la ventana (W/m²K) | 5,90 | 5,49–6,31 |
| Factor solar del vidrio | 0,82 | 0,77–0,86 |
| Factor de sombra | 0,73 | 0,58–0,88 |
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

**Calidad.** Estabilidad (Jaccard): 1,00. Fidelidad a la regla de asignación (recall en la prueba): árbol 1,000, Random Forest 1,000. Probabilidad media de pertenecer a este arquetipo al repetir el agrupamiento en las submuestras de estabilidad: 1,000 (0,0 % de las viviendas por debajo de 0,8).

**Limitaciones.**

- La fracción de casas del catastro en los estratos 3-4 queda fuera del intervalo de la ECV, así que el puente entre la posición y el tipo de vivienda de la ECV es aproximado; la sensibilidad de la Fase 2 lo trata como un factor (AJ22).
- Las habitaciones del catastro difieren de los dormitorios de la ECV en los estratos 3, 4 (fuera del intervalo del 95 %).
- Lo definen la posición y el bloque de estratos; no depende de las variables de agrupamiento.

## S56-1 · Sin cubierta, estratos 5-6

**Identificación.** 22.034 viviendas (6,6 % de la ciudad) en 1.549 edificios. Posición: sin cubierta (apartamento intermedio o primer piso con vivienda encima). Agrupamiento: k-prototypes en el estrato «sin cubierta · 5-6», con 1 grupo(s).

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
| U del muro (W/m²K) | 3,00 | 2,25–3,75 |
| Absortancia del muro | 0,67 | 0,51–0,82 |
| Capacidad C_m (kJ/K por m² de piso) | 265 | 195–336 |
| Infiltración con ventanas cerradas (renovaciones por hora) | 0,95 | 0,50–1,59 |
| Pisos con acabado | 100 % | 97 %–100 % |
| Relación ventana-muro | 0,30 | 0,23–0,37 |
| U de la ventana (W/m²K) | 5,90 | 5,49–6,31 |
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

**Calidad.** Estabilidad (Jaccard): 1,00. Fidelidad a la regla de asignación (recall en la prueba): árbol 1,000, Random Forest 1,000. Probabilidad media de pertenecer a este arquetipo al repetir el agrupamiento en las submuestras de estabilidad: 1,000 (0,0 % de las viviendas por debajo de 0,8).

**Limitaciones.**

- Las habitaciones del catastro difieren de los dormitorios de la ECV en los estratos 5, 6 (fuera del intervalo del 95 %).
- Lo definen la posición y el bloque de estratos; no depende de las variables de agrupamiento.

## U12-1 · Último piso, estratos 1-2

**Identificación.** 11.992 viviendas (3,6 % de la ciudad) en 5.443 edificios. Posición: último piso. Agrupamiento: k-prototypes en el estrato «último piso · 1-2», con 1 grupo(s).

**Definición.** Rasgos típicos (percentiles 25 a 75): área de 43 a 106 m² (mediana 55 m²); 1 piso(s) en la unidad; piso 4 del edificio (mediana).

Reglas principales del árbol de asignación (Paso 5):

- área ≤ 50,6 m² · posición: último piso · bloque de estratos: 1-2 (3.599 viviendas de entrenamiento)
- área > 82,7 m² · pisos de la unidad ≥ 2 · posición: último piso · bloque de estratos: 1-2 (2.815 viviendas de entrenamiento)
- área entre 50,6 y 82,7 m² · posición: último piso · bloque de estratos: 1-2 (2.249 viviendas de entrenamiento)
- y 3 reglas más (`clf_reglas_arbol_por_vivienda.txt`)

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
| U del techo (W/m²K) | 4,07 | 3,38–5,37 |
| Absortancia del techo | 0,67 | 0,42–0,89 |
| Muros de mampostería | 99 % | 98 %–100 % |
| U del muro (W/m²K) | 3,28 | 2,36–3,94 |
| Absortancia del muro | 0,67 | 0,52–0,82 |
| Capacidad C_m (kJ/K por m² de piso) | 238 | 145–330 |
| Infiltración con ventanas cerradas (renovaciones por hora) | 1,38 | 0,53–3,40 |
| Pisos con acabado | 80 % | 74 %–86 % |
| Relación ventana-muro | 0,30 | 0,17–0,44 |
| U de la ventana (W/m²K) | 5,89 | 5,49–6,31 |
| Factor solar del vidrio | 0,82 | 0,77–0,86 |
| Factor de sombra | 0,73 | 0,58–0,88 |
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

**Calidad.** Estabilidad (Jaccard): 1,00. Fidelidad a la regla de asignación (recall en la prueba): árbol 0,997, Random Forest 1,000. Probabilidad media de pertenecer a este arquetipo al repetir el agrupamiento en las submuestras de estabilidad: 1,000 (0,0 % de las viviendas por debajo de 0,8).

**Limitaciones.**

- Techo: concreto en los multifamiliares (supuesto S6) y, en los de baja altura, el reparto de los apartamentos de la ECV (Nota 5).
- La fracción de casas del catastro en los estratos 1-2 queda fuera del intervalo de la ECV, así que el puente entre la posición y el tipo de vivienda de la ECV es aproximado; la sensibilidad de la Fase 2 lo trata como un factor (AJ22).
- Las habitaciones del catastro difieren de los dormitorios de la ECV en los estratos 1, 2 (fuera del intervalo del 95 %).
- Lo definen la posición y el bloque de estratos; no depende de las variables de agrupamiento.

## U34-1 · Último piso, estratos 3-4

**Identificación.** 14.105 viviendas (4,2 % de la ciudad) en 6.325 edificios. Posición: último piso. Agrupamiento: k-prototypes en el estrato «último piso · 3-4», con 1 grupo(s).

**Definición.** Rasgos típicos (percentiles 25 a 75): área de 62 a 112 m² (mediana 81 m²); 1 piso(s) en la unidad; piso 3 del edificio (mediana).

Reglas principales del árbol de asignación (Paso 5):

- área > 82,7 m² · posición: último piso · bloque de estratos: 3-4 (4.855 viviendas de entrenamiento)
- área entre 50,6 y 82,7 m² · posición: último piso · bloque de estratos: 3-4 (4.717 viviendas de entrenamiento)
- área ≤ 50,6 m² · posición: último piso · bloque de estratos: 3-4 (1.039 viviendas de entrenamiento)

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
| Techo de asbesto-cemento | 13 % | 8 %–18 % |
| Techo metálico o de zinc | 0 % | 0 %–0 % |
| Techo de otro material | 1 % | 0 %–4 % |
| U del techo (W/m²K) | 3,97 | 3,42–4,80 |
| Absortancia del techo | 0,69 | 0,43–0,89 |
| Muros de mampostería | 99 % | 97 %–100 % |
| U del muro (W/m²K) | 3,00 | 2,25–3,77 |
| Absortancia del muro | 0,67 | 0,52–0,82 |
| Capacidad C_m (kJ/K por m² de piso) | 251 | 156–335 |
| Infiltración con ventanas cerradas (renovaciones por hora) | 1,16 | 0,51–2,56 |
| Pisos con acabado | 100 % | 99 %–100 % |
| Relación ventana-muro | 0,17 | 0,08–0,26 |
| U de la ventana (W/m²K) | 5,89 | 5,49–6,31 |
| Factor solar del vidrio | 0,82 | 0,78–0,86 |
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

**Calidad.** Estabilidad (Jaccard): 1,00. Fidelidad a la regla de asignación (recall en la prueba): árbol 1,000, Random Forest 1,000. Probabilidad media de pertenecer a este arquetipo al repetir el agrupamiento en las submuestras de estabilidad: 1,000 (0,0 % de las viviendas por debajo de 0,8).

**Limitaciones.**

- Techo: concreto en los multifamiliares (supuesto S6) y, en los de baja altura, el reparto de los apartamentos de la ECV (Nota 5).
- La fracción de casas del catastro en los estratos 3-4 queda fuera del intervalo de la ECV, así que el puente entre la posición y el tipo de vivienda de la ECV es aproximado; la sensibilidad de la Fase 2 lo trata como un factor (AJ22).
- Las habitaciones del catastro difieren de los dormitorios de la ECV en los estratos 3, 4 (fuera del intervalo del 95 %).
- Lo definen la posición y el bloque de estratos; no depende de las variables de agrupamiento.

## U56-1 · Último piso, estratos 5-6

**Identificación.** 3.800 viviendas (1,1 % de la ciudad) en 1.643 edificios. Posición: último piso. Agrupamiento: k-prototypes en el estrato «último piso · 5-6», con 1 grupo(s).

**Definición.** Rasgos típicos (percentiles 25 a 75): área de 94 a 194 m² (mediana 126 m²); 1 piso(s) en la unidad; piso 5 del edificio (mediana).

Reglas principales del árbol de asignación (Paso 5):

- área > 82,7 m² · posición: último piso · bloque de estratos: 5-6 (2.709 viviendas de entrenamiento)
- área entre 50,6 y 82,7 m² · posición: último piso · bloque de estratos: 5-6 (340 viviendas de entrenamiento)
- área ≤ 50,6 m² · posición: último piso · bloque de estratos: 5-6 (143 viviendas de entrenamiento)

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
| U del techo (W/m²K) | 3,91 | 3,45–4,58 |
| Absortancia del techo | 0,70 | 0,43–0,89 |
| Muros de mampostería | 100 % | 100 %–100 % |
| U del muro (W/m²K) | 3,00 | 2,24–3,77 |
| Absortancia del muro | 0,67 | 0,52–0,82 |
| Capacidad C_m (kJ/K por m² de piso) | 264 | 193–335 |
| Infiltración con ventanas cerradas (renovaciones por hora) | 0,98 | 0,51–1,65 |
| Pisos con acabado | 100 % | 97 %–100 % |
| Relación ventana-muro | 0,30 | 0,23–0,37 |
| U de la ventana (W/m²K) | 5,89 | 5,49–6,31 |
| Factor solar del vidrio | 0,82 | 0,77–0,86 |
| Factor de sombra | 0,73 | 0,58–0,89 |
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

**Calidad.** Estabilidad (Jaccard): 1,00. Fidelidad a la regla de asignación (recall en la prueba): árbol 1,000, Random Forest 1,000. Probabilidad media de pertenecer a este arquetipo al repetir el agrupamiento en las submuestras de estabilidad: 1,000 (0,0 % de las viviendas por debajo de 0,8).

**Limitaciones.**

- Techo: concreto en los multifamiliares (supuesto S6) y, en los de baja altura, el reparto de los apartamentos de la ECV (Nota 5).
- Las habitaciones del catastro difieren de los dormitorios de la ECV en los estratos 5, 6 (fuera del intervalo del 95 %).
- Lo definen la posición y el bloque de estratos; no depende de las variables de agrupamiento.
