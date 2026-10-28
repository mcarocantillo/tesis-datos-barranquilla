# Cambios a la propuesta

**Estado (27 de octubre de 2026).** Los seis cambios de la tabla se incorporaron a la propuesta, con dos ajustes: el alza estacional de la Tabla 10 se calcula ahora con lecturas reales (+16 / +19 / +27 / +31 / +31 / +29 %), y la tenencia de la ciudad sin suavizar se reporta como 33 % (2019) y 41 % (2024).

Con la consulta del SUI por tipo de lectura ([Consumo del SUI por tipo de lectura](17_lecturas_reales.md)) se agregaron estos cambios:

- La calibración usa el consumo por suscriptor con lectura real y excluye las cuentas «n/a» sin consumo; el estrato 1 se calibra solo con sus lecturas reales.
- La Ecuación (5) incluye un factor de precio con una elasticidad por grupo de estratos (supuesto S17).
- Se calibra con 2015 a 2025, salvo 2020, y se reservan 2023 y 2025 para la validación; la Tabla 6 se ajustó a esos años.
- La Ecuación (10) es la que se estimó en la compuerta horaria (logaritmo de la demanda y efectos fijos de cada hora en cada mes), y en la Ecuación (9) el efecto de mes es el del mes calendario.
- La Tabla 10 usa el consumo con lecturas reales de 2024 y la sección de avances describe el estrato 1 y la caída del consumo por suscriptor.

La tabla siguiente conserva los seis cambios originales sobre la versión v3; los números salen del capítulo «Serie de tenencia, error de la encuesta e imputación».

| # | Dónde | Texto actual (resumido) | Texto propuesto |
| --- | --- | --- | --- |
| 1 | Fase 2, Paso 2 (Tenencia de equipos) | «para cada año simulado se usará la ola de la ECV de ese año, suavizada entre olas… la tenencia saldrá de la tendencia de cada estrato ajustada a las olas disponibles, con mayor incertidumbre» | «Para cada año simulado, la tenencia de cada estrato será una distribución Beta construida con las olas de la ECV 2018–2025 de Barranquilla (sin 2020). Como la tendencia entre olas solo es significativa en los estratos 1 y 3, la Beta mezcla en partes iguales un ajuste con tendencia y uno con nivel constante, de modo que su ancho incluye la duda sobre la tendencia; los años sin ola (2015–2017, 2026–2027) quedan con la mayor incertidumbre.» |
| 2 | Fase 2, Paso 2 (variables de la regresión) | «con las variables que existen tanto en la encuesta como en la vivienda simulada: estrato, tipo de vivienda, material del techo… y tamaño del hogar» | «La tasa de cada estrato se fija con la Beta anterior y, dentro del estrato, la regresión logística de la ECV 2024 reparte la tenencia según el material del techo (razón de momios 0,35 para asbesto-cemento y 0,14 para zinc frente a concreto). El tipo de vivienda y el tamaño del hogar no mejoran la predicción y no se usan.» |
| 3 | Sección de avance (párrafo de la Tabla 10) | «pasó de cerca de 33 % en 2019 a 41 % en 2024» | «pasó de 33 % en 2019 a 41 % en 2024 (± 4 puntos con el diseño muestral de la encuesta)» |
| 4 | Consideraciones sobre los datos (diseño por conglomerados) | «Las encuestas del DANE tienen un diseño por conglomerados con factores de expansión que se respetarán en todas las estimaciones» | Añadir: «En la ECV 2024 de Barranquilla el efecto de diseño medido para la tenencia de A/C es 1,5 (76 segmentos); las varianzas de las demás olas se multiplicarán por ese factor.» |
| 5 | Tabla 10, columna «Alza ago.–sep. frente a feb.–mar.» y su nota | +11 / +16 / +24 / +26 / +27 / +28 %; nota «meses válidos de 2019 a 2025» | +11 / +17 / +24 / +28 / +29 / +28 %; nota «meses válidos de 2015 a 2025» (opcional: el patrón no cambia) |
| 6 | Fase 3, Paso 4 (Calibración con 2015–2019) | Sin mención de la tenencia en esos años | Añadir: «La tenencia de 2015–2017 no tiene ola propia; su incertidumbre (± 2 puntos en la ciudad) se propaga con la Beta de cada estrato y se reportará en la banda de los resultados calibrados.» |

Si en la tesis se menciona la relación entre la posición frente a la cubierta y el A/C, usar la redacción del capítulo «Serie de tenencia, error de la encuesta e imputación».
