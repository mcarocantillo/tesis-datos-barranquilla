# Supuestos, sensibilidad y limitaciones

La propuesta pide que cada supuesto quede registrado con su fuente, su rango, su influencia y el dato que lo reemplazaría (Fase 3, paso 9). Este capítulo abre ese registro para los datos de entrada. La {numref}`tab-supuestos` lista los supuestos del procesamiento y la {numref}`tab-sensibilidad` cuantifica su efecto en las cifras principales. Los supuestos S14 a S17 ya corresponden al modelo de simulación (consigna, envolvente, forma horaria y clima); los demás supuestos de la simulación (umbrales de encendido, potencias) se agregarán en la Fase 2.

## Registro de supuestos

```{table} Registro de supuestos de los datos de entrada.
:name: tab-supuestos

| N.º | Supuesto | Justificación | Alternativa o rango | Dato que lo reemplazaría |
| --- | --- | --- | --- | --- |
| S1 | La tenencia de A/C por estrato y año es la mezcla, con igual peso, de un ajuste con tendencia y uno de nivel constante (variante C) | La tendencia es significativa solo en E1 ($p = 0{,}03$) y E3 ($p = 0{,}007$); en los demás estratos $p$ está entre 0,39 y 0,53 | Variante A (tendencia en todos) o B (tendencia solo en E1 y E3) | Nuevas olas de la ECV (2026 en adelante) |
| S2 | La ola 2020 no entra en el ajuste de la serie | Encuesta en parte telefónica y ocupación de las viviendas alterada por la pandemia | Incluirla | — |
| S3 | La tasa de la ciudad usa los pesos por estrato del SUI y no los de la ECV | La ECV sobrerrepresenta el estrato 1 ({numref}`tab-coherencia-estratos`) | Factores de expansión de la ECV | — |
| S4 | El efecto de diseño de 2024 (1,5 en varianza) vale para las demás olas | Solo la ola 2024 se procesó con sus segmentos (76 conglomerados) | Muestreo aleatorio simple | Variables de diseño de cada ola |
| S5 | El efecto del techo sobre el A/C (modelo M2) es el mismo en todos los años y estratos | Se estima con la ECV 2024 (633 hogares); con la ECV 2019 (944 hogares) el efecto tiene el mismo signo y es algo menor | Efectos de 2019 o del modelo M3 | Olas adicionales con techo y A/C |
| S6 | Las viviendas en edificios de 4 pisos o más tienen techo de concreto | El catastro no registra materiales; la ECV casi no capta los edificios del estrato 1 ({numref}`tab-e1-edificios`). Solo afecta al último piso, 16 % de las unidades en edificios | Último piso con teja de asbesto-cemento | Inspección o registro de materiales |
| S7 | La tenencia imputada al catastro en el estrato 1 se iguala a la de la ECV | La tenencia no se calibra (Fase 3, paso 4) | Intercepto calculado con la mezcla de la ECV; ECV reponderada a la composición de edificios del catastro | Datos de Air-e por barrio; olas de la ECV con más segmentos en edificios |
| S8 | Las horas de uso por equipo de 2019 valen para todos los años | La ECV dejó de preguntarlas después de 2019 | Rango de las horas de 2019 | Medición o encuesta de uso reciente |
| S9 | $p_c \approx 0{,}95$, igual en todos los estratos | Horas de ventilador casi iguales con y sin A/C en E1–E4 ({numref}`tab-pc`) | 0,8–1,0 | Medición en hogares con ambos equipos |
| S10 | La presencia en la vivienda de las cabeceras del Atlántico representa a Barranquilla | La ENUT no identifica el municipio | — | ENUT con municipio |
| S11 | Una proporción observada de 100 % se representa con una Beta de Jeffreys actualizada | El método de momentos no aplica con varianza cero | Beta(1; 1) actualizada | Muestras mayores en E4–E6 |
| S12 | Un suscriptor residencial del SUI equivale a un hogar | Catastro y SUI coinciden en número y distribución ({numref}`tab-coherencia-hogares`) | Hogares de la proyección demográfica | Hogares por medidor de Air-e |
| S13 | El año de construcción del catastro se usa como «año de registro catastral», no como antigüedad física; los 24 lotes con años de 1932 a 1972 se tratan como faltantes | Aporta información sobre materiales para el juicio de expertos (Fase 1, paso 6); su significado no está documentado | Excluir la variable de los arquetipos | Definición del campo por la Gerencia de Gestión Catastral; imágenes históricas |
| S14 | La consigna de refrigeración del A/C está entre 22 y 26,5 °C | El límite superior es la consigna operativa de CEELA para Barranquilla, del confort adaptativo de ASHRAE 55 {cite:p}`ceela2025c`; el límite inferior, 22 °C, es un supuesto propio de este trabajo, para cubrir consignas más bajas que la de confort | Consigna fija de 26,5 °C; rango más estrecho | Medición de consignas o temperaturas interiores en hogares de Barranquilla |
| S15 | Los parámetros de envolvente, zona climatizada y COP de CEELA son el centro de los rangos de cada arquetipo; la VIS representa los estratos 1 y 2 y la no VIS los estratos 3 a 6 | Es la única caracterización de la envolvente de Barranquilla con planos de edificios reales ({numref}`tab-ceela-envolvente`); CEELA usa esa correspondencia en su análisis del SUI | Rangos de la literatura sin centro local | Inspección de viviendas antiguas e informales; más de un edificio por tipología |
| S16 | La forma horaria del uso del A/C (hora media del encendido nocturno y su dispersión) es un supuesto con rango (capa C), no un parámetro calibrado con XM | La forma nocturna de la respuesta al calor cambia entre años ($p = 0{,}008$; [Respuesta horaria al calor](15_compuerta_horaria.md)) | Calibrarla con XM (capa B) | Curvas horarias de usuarios residenciales de Air-e; medición en hogares |
| S17 | El consumo por suscriptor responde al precio real del kWh con una elasticidad por grupo de estratos (1 a 3 y 4 a 6), con prior entre −0,4 y 0 en los estratos bajos y cercano a 0 en los altos | Con lecturas reales, el consumo de los estratos 1 a 3 siguió bajando entre 2019 y 2024 mientras el precio real subía cerca de 50 %, y el de los estratos 4 a 6 no ([Consumo del SUI por tipo de lectura](17_lecturas_reales.md)); rango de la literatura {cite:p}`labandeira2017` | Un término de nivel libre por año | Tarifa marginal por hogar; consumo medido de una muestra de hogares |
| S18 | El nivel del estrato 1 se calibra solo con los suscriptores con lectura real | Entre 50 % y 80 % de su consumo facturado es estimado o de usuarios sin medidor ([Consumo del SUI por tipo de lectura](17_lecturas_reales.md)) | Todas las lecturas | Medidores en los barrios sin medición |
| S17 | El clima horario de ERA5-Land de la copia de Open-Meteo equivale al del Climate Data Store | Open-Meteo sirve ERA5-Land sin credenciales; viento y radiación vienen de ERA5 (0,25°) | Archivo del CDS | Descarga del CDS (`01a_descargar_era5land_cds.py`) |
```

## Sensibilidad cuantificada

```{table} Efecto de los supuestos sobre las cifras principales (puntos porcentuales de hogares con A/C).
:name: tab-sensibilidad

| Supuesto | Cifra afectada | Valor adoptado | Alternativa | Diferencia |
| --- | --- | --- | --- | --- |
| S1, variante de la serie | Ciudad 2015 | 31,3 (C) | 29,8 (A); 32,7 (B) | −1,5 a +1,4 |
| S1, variante de la serie | Ciudad 2019 | 35,6 (C) | 35,1 (A); 36,1 (B) | ± 0,5 |
| S1, variante de la serie | Ciudad 2024 | 41,2 (C) | 41,8 (A); 40,6 (B) | ± 0,6 |
| S1, variante de la serie | Ciudad 2027 | 45,4 (C) | 46,7 (A); 44,1 (B) | ± 1,3 |
| S2, incluir la ola 2020 (variante A) | Ciudad 2015 / 2019 / 2024 | 29,8 / 35,1 / 41,8 | 31,2 / 35,9 / 42,1 | +0,3 a +1,4 |
| S3, pesos de la ECV en lugar del SUI | Ciudad 2019 (tasa directa) | 33,3 | 30,9 | −2,4 |
| S3, pesos de la ECV en lugar del SUI | Ciudad 2024 (tasa directa) | 41,4 | 37,1 | −4,3 |
| S4, sin efecto de diseño | Semiancho del IC 95 %, ciudad 2024 (tasa directa) | ± 4,1 | ± 3,3 | −0,8 |
| S5, modelo M3 en lugar de M2 | Razón de momios, asbesto-cemento / zinc | 0,35 / 0,14 | 0,37 / 0,15 | +0,02 / +0,01 |
| S5, ECV 2019 en lugar de 2024 (M2) | Razón de momios, asbesto-cemento / zinc | 0,35 / 0,14 | 0,48 / 0,18 | +0,13 / +0,04 |
| S7, E1 sin igualar a la ECV | Tenencia del estrato 1 en el catastro, 2024 | 13,2 | 14,4 | +1,2 (ciudad +0,7) |
| S7, ECV reponderada por tipo de edificio | Tenencia del estrato 1, 2024 (tasa directa) | 12,4 | 14,5–15,2 | +2,1 a +2,8 (ciudad +0,7 a +0,9) |
```

La elección entre variantes de la serie (S1) mueve la tenencia de la ciudad menos de 1,5 puntos en cualquier año. Es menos que el semiancho del intervalo de confianza de 2024 (± 2,9 puntos), y por eso la diferencia entre variantes se incorpora a la varianza de la serie en lugar de tratarse como una decisión. El supuesto con mayor efecto es la ponderación de la ciudad (S3), que cambia la tasa de 2024 en 4,3 puntos. Ese supuesto, sin embargo, está respaldado por la coincidencia entre el catastro y el SUI ({numref}`tab-coherencia-estratos`).

El supuesto S6 tiene un efecto que no se ve en la tasa de la ciudad, sino en el reparto entre viviendas. Antes de estandarizar por estrato, la P(A/C) imputada difiere 37 puntos entre la casa y el apartamento intermedio. Dentro de cada estrato la diferencia baja a 13 puntos, y esos 13 puntos provienen del supuesto de techo, no de una observación. Por eso la relación entre la posición frente a la cubierta y el A/C se presenta como resultado de la imputación.

## Limitaciones de los datos

1. **Muestras pequeñas en los estratos altos.** La ECV 2024 tiene 52, 38 y 20 hogares en los estratos 4, 5 y 6. Sus proporciones tienen intervalos de ± 10 a ± 14 puntos, y en el estrato 6 la tenencia observada de A/C es de 100 %. La serie suavizada y las distribuciones Beta reflejan esa incertidumbre, pero no la eliminan.
2. **Años sin encuesta utilizable.** Las ECV 2015, 2016 y 2017 no identifican el municipio en los microdatos. Los años 2015–2017 del periodo de calibración son extrapolaciones de la serie, con desviaciones estándar de 2,4 puntos en la ciudad en 2015.
3. **Sin hora de uso.** Ninguna encuesta registra a qué hora se usan los equipos. La ENUT da duraciones de las actividades, no horarios. La demanda de XM tampoco permite calibrar la forma horaria, porque su respuesta nocturna al calor cambia de forma entre años; solo restringe la respuesta por franjas (S16). La forma horaria del perfil dependerá del módulo térmico y de supuestos declarados.
4. **Sin número de equipos ni fracción climatizada medidos.** La ECV registra si el hogar tiene A/C, pero no cuántos equipos tiene. CEELA da la zona climatizada típica por tipología (una habitación en VIS, las habitaciones en E3–E4, toda la vivienda en E5–E6; {numref}`tab-ceela-climatizacion`), pero a partir de edificios nuevos del mercado formal, no de una medición en hogares.
5. **Calidad del SUI.** Hay meses faltantes, consumos nulos o negativos y tarifas atípicas; se marcaron con banderas y se excluyen ([Datos sospechosos y pendientes](07_datos_sospechosos.md)). El consumo del estrato 1 está por encima del de los estratos 2 y 3 y debe confirmarse.
6. **Materiales sin registro.** El catastro no informa materiales. El techo de cada vivienda se asigna con la ECV por estrato, y en los edificios altos con un supuesto (S6). La ECV casi no capta los edificios de estrato 1, así que su distribución de techos describe sobre todo casas.
7. **Comparaciones ecológicas.** La relación entre la tenencia de A/C y el alza estacional del consumo se mide con seis estratos agregados. Es coherente con el efecto del A/C, pero no lo identifica a nivel de hogar.
8. **Año de construcción.** El campo `anio_construccion` del catastro parece registrar el año de la última incorporación o actualización de la construcción, no su fecha original: solo 1.442 casas de toda la ciudad son anteriores a 1975, y 15.376 apartamentos de estratos 1 y 2 en bloques recientes registran años entre 1932 y 1972. Se usará como «año de registro catastral» (S13), con esos 24 lotes como faltantes, hasta confirmar su significado con el catastro.
