# Metodología

```{note}
La ECV 2024 se procesa con 709 hogares. La serie de tenencia que usa el modelo y el efecto de diseño están en «Serie de tenencia, error de la encuesta e imputación».
```

## Procesamiento de cada fuente

Esta pestaña explica, paso a paso, cómo se obtuvo cada cifra del informe: qué archivos se usaron, cómo se unieron, qué filtros se aplicaron, cómo se construyó cada variable y con qué fórmula se calculó cada estadística. Todo se procesó en Python (pandas) a partir de los microdatos originales del DANE y de los reportes del SUI.

### 1. Principios generales

Toda cifra de encuesta del informe es **ponderada** con el factor de expansión de la encuesta, salvo que se diga lo contrario; los tamaños de muestra (n) se reportan **sin ponderar**.

**Factor de expansión (w).** Cada registro representa w hogares o personas de la población: FEX\_C en ECV y ENUT, FEX\_C18 en GEIH. En la GEIH cada mes está expandido a la población completa, así que al juntar 12 meses se usa w = FEX\_C18 / 12. En la ECV 2019 el factor viene con coma decimal («364,91») y se convirtió a número.

**Fórmulas usadas** (sumas sobre los registros i del grupo analizado, por ejemplo un estrato):

```{math}
\text{Proporción ponderada: } \hat p = \frac{\sum_i w_i \, \mathbb{1}[\text{condición}_i]}{\sum_i w_i}
```

```{math}
\text{Media ponderada: } \bar x = \frac{\sum_i w_i x_i}{\sum_i w_i} \quad (\text{solo registros con } x_i \text{ válido})
```

- **Mediana y percentiles ponderados:** se ordenan los registros por x, se acumulan los pesos y se toma el primer valor cuyo peso acumulado alcanza 50 % (o 25 %, 75 %, 90 %) del total.
- **Distribuciones por estrato:** suma de w de cada estrato dividida por la suma de w de los estratos 1–6. Los códigos 0 (sin estrato), 8 (planta eléctrica) y 9 (no sabe) se excluyen de las tablas por estrato.
- **Intervalo de confianza del 95 %** de una proporción por estrato: p ± 1,96·√(p(1−p)/n), con n = hogares de la muestra en ese estrato. Supone muestreo aleatorio simple; como la ECV es una muestra por conglomerados, el intervalo real es más ancho (efecto de diseño no aplicado).
- **Valores faltantes:** una pregunta vacía se trata como «no aplica» y se excluye del denominador de las medias; en las variables de tenencia, vacío = no tiene (ver cada encuesta).
- **Redondeo:** porcentajes a un decimal; horas a un decimal; pesos colombianos a miles.

### 2. ECV 2019 (DANE, catálogo 678)

**Archivos usados:** Datos de la vivienda, Servicios del hogar, Uso de energéticos del hogar, Tenencia y financiación de la vivienda, Características y composición del hogar, Fuerza de trabajo y Municipio de aplicación.

**Unión de archivos (llaves):**

- Hogar = DIRECTORIO + SECUENCIA\_ENCUESTA + SECUENCIA\_P (archivos de vivienda, servicios, energéticos y tenencia).
- Personas → hogar = DIRECTORIO + SECUENCIA\_P. En los archivos de personas SECUENCIA\_ENCUESTA numera a la persona, no al hogar; usar la llave de tres campos perdía casi todas las personas.
- Municipio = archivo «Municipio de aplicación», unido por DIRECTORIO.

**Filtro de Barranquilla:** P1\_DEPARTAMENTO = 08 y P1\_MUNICIPIO = 001 → 1.009 hogares (901 en cabecera y 108 en centros poblados o rural). Las tablas incluyen todo el municipio.

**Variables derivadas:**

| Variable del informe | Cómo se construyó |
| --- | --- |
| Estrato | P8520S1A1 (estrato para tarifa de energía); 0, 8 y 9 fuera de las tablas por estrato |
| Tiene AC | P5523 (tipo de AC) respondido = 1; vacío = 0. Tipo: 1 mini-split, 2 pared/ventana, 3 central |
| Horas de AC | P5524, horas al día sumadas de todos los equipos; se resumen solo entre hogares con AC |
| Tiene ventilador | alguna de P5525S1–S4 = 1 (techo, pared, mesa, pedestal) o P5526 > 0 |
| Horas de ventilador | P5526 entre hogares con P5526 > 0 |
| Tiene nevera | P5514 (tamaño) respondido; no hay pregunta directa de tenencia |
| Tamaño y antigüedad de nevera | P5514 (1 pequeña, 2 mediana, 3 grande); P5515 en años, 99 = no sabe → excluido |
| Lavadora, TV, PC, calentador | tenencia inferida de que el hogar responda el uso: P5509 (lavadora), P5522S1 (TV LCD/LED), P5521S1 (TV convencional), P5527 (PC), P5529 > 0 (portátiles), P5518 (calentador) |
| Bombillas | P5533S1 incandescente, S2 fluorescente compacta, S3 LED; % LED = Σw·LED / Σw·total de bombillas |
| Pago mensual de electricidad | P5018 (último pago) ÷ P5018S1 (meses que cubre); se descartan valores < 1.000 o > 3.000.000 COP/mes |
| Personas del hogar | CANT\_PERSONAS\_HOGAR (Servicios) |
| Edades | P6040 de cada persona, agregada por hogar: menores de 5, 5–14, 15–64, 65+ |
| Jefatura | P6051 = 1 (jefe); sexo P6020 y edad P6040 de esa persona |
| Ocupados y actividad | P6240 de Fuerza de trabajo (1 trabajó, 2 buscó trabajo, 3 estudió, 4 oficios del hogar, 5 incapacitado, 6 otra), contados por hogar; hogar sin ocupados = 0 personas con P6240 = 1 |
| Personas por dormitorio y hacinamiento | CANT\_PERSONAS\_HOGAR ÷ P5010; hacinamiento = más de 3 personas por dormitorio |
| Ingreso | I\_HOGAR y PERCAPITA (imputados por el DANE) |
| Quintiles de ingreso | cortes en los percentiles ponderados 20, 40, 60 y 80 del ingreso per cápita de los hogares de estratos 1–6 de Barranquilla (ingreso faltante = 0) |
| Tenencia de la vivienda | P5095: 1–2 propia, 3 arriendo, 4–6 otra (usufructo, posesión, colectiva) |
| Techo, pisos, paredes | P4567, P4015, P4005 con las categorías del diccionario DANE |
| Combustible para cocinar | P8536 |

- **Gasto con y sin AC:** mediana ponderada del pago mensual dentro de cada grupo de estrato (1–2, 3–4, 5–6), separando hogares con P5523 respondido y sin él. Diferencia = mediana con AC / mediana sin AC − 1.

### 3. ECV 2024 (DANE, catálogo 861)

**Archivos usados:** Datos de la vivienda, Condiciones de vida del hogar y tenencia de bienes, Servicios del hogar, Tenencia y financiación de la vivienda y Características y composición del hogar. Se descargaron pero no se usaron: Variables de diseño muestral, factores PDET, programas, beneficiarios y escritura.

**Filtro y llaves:** en 2024 el municipio viene en «Datos de la vivienda» (P1\_DEPARTAMENTO = 08 y P1\_MUNICIPIO = 001 → 698 viviendas). Los hogares de esas viviendas se toman del archivo de bienes (por DIRECTORIO) y se unen a los demás archivos por DIRECTORIO + SECUENCIA\_ENCUESTA (en los archivos de hogar SECUENCIA\_P vale siempre 1) → 709 hogares: 649 en cabecera y 60 rurales, todos con estrato 0, que por eso no entran en las tablas por estrato. El factor de expansión viene con punto decimal.

| Variable del informe | Cómo se construyó |
| --- | --- |
| Tiene AC, ventilador, nevera, lavadora, TV LED, TV convencional, PC, portátil, calentador | P1077S11, S12, S2, S1, S8, S7, S21, S22, S6 = 1 (pregunta directa ¿cuáles de los siguientes bienes posee este hogar?) |
| Estrato | P8520S1A1 de la vivienda |
| Cuartos, dormitorios, sanitarios | P5000, P5010, P5024 |
| Personas, ingreso | CANT\_PERSONAS\_HOGAR, I\_HOGAR, PERCAPITA |
| Menores de 5 y mayores de 65 | conteo por hogar de P6040 en Características y composición |
| Pago mensual de electricidad | P5018 ÷ P5018S1; se descartan valores < 1.000 o > 5.000.000 COP/mes |
| Tenencia, techo, tipo de vivienda | P5095, P4567, P1070 (mismas categorías que 2019) |
| Quintiles de ingreso | percentiles ponderados 20–40–60–80 del ingreso per cápita de 2024 |

- **Diferencia con 2019:** en 2019 la tenencia de electrodomésticos se infiere de las preguntas de uso; en 2024 es pregunta directa. Por eso las comparaciones de lavadora y TV entre años deben leerse con cautela; la de AC es comparable porque en ambos años se basa en una pregunta específica sobre el equipo.

### 4. ENUT 2024–2025 (DANE, catálogo 910)

**Archivos usados:** C1 (vivienda), C2 (hogar y bienes), C3 (personas), C6 (educación), C7 y C7\_1 (trabajo) y C8 (uso del tiempo). Las etiquetas de cada variable se tomaron de los metadatos DDI del catálogo.

**Filtro y llaves:** DPTO = 08 (Atlántico) y CLASE = 1 (cabecera). La ENUT no trae municipio, así que incluye Barranquilla, Soledad, Malambo y las demás cabeceras. Vivienda = DIRECTORIO; hogar = DIRECTORIO + SECUENCIA\_P; persona = DIRECTORIO + SECUENCIA\_P + ORDEN. Las estadísticas de tiempo son de las 5.533 personas de 10 años o más, ponderadas con FEX\_C.

**Día de referencia:** DIA\_REF está en días desde el 1-ene-1970; se convirtió a fecha (17-sep-2024 a 13-sep-2025), día de la semana y mes. Fin de semana = sábado o domingo.

**Minutos por actividad:** para cada actividad, minutos = horas (…A1) × 60 + minutos (…A2), sumando los ítems que la componen. Quien no realizó la actividad cuenta como 0.

| Actividad | Ítems de C8 sumados |
| --- | --- |
| Dormir, comer, asearse, descansar | P1144S1, S2, S3, S6 |
| Cocinar, lavar loza | P1143S1, S2 |
| Ropa, limpiar la vivienda | P1142S1, P1136S1 |
| TV | P1110S1 (solo TV) + S2 (TV haciendo otra cosa) |
| Internet recreativo | P1110S5 + S6 |
| Música o radio | P1110S3 + S4 |

| Variable de trabajo y estudio | Cómo se construyó |
| --- | --- |
| Trabajo del día | P1150S1/S2 (empleo principal) + P6535S1A1/A2 (segundo empleo) + P6530S1A1/A2 (colaboró en un negocio) |
| Viajes al trabajo | 2 × (P1099S1/S2 + P6534S1/S2): la ENUT pregunta el viaje de ida y se supone igual el de vuelta |
| Viajes al estudio | 2 × P1159S1/S2 (C6) |
| Trabaja en su vivienda | P6880 = 2 (C7\_1) |
| Fuera por trabajo | trabajo del día (si no trabaja en su vivienda) + viajes al trabajo |
| Fuera por trabajo o estudio | lo anterior + viajes al estudio. **No incluye las horas de clase**, que la ENUT no mide; para estudiantes es una subestimación |

**Tipo de persona** (en este orden): ocupado si P1152 = 1; mayor de 65 no ocupado si edad ≥ 65 y P1152 ≠ 1; estudiante si P1152 = 3; oficios del hogar si P1152 = 4; busca trabajo si P1152 = 2; el resto, otro o incapacitado.

- **Hogar con alguien en casa todo el día:** por hogar (todos sus miembros reportan el mismo día), al menos una persona de 10+ con 0 minutos fuera por trabajo o estudio. Ponderado con el factor del hogar. No captura salidas por compras, trámites u ocio.
- **Distribución del tiempo fuera:** proporción ponderada de personas en cada tramo (0 h, hasta 4 h, 4–8 h, 8–10 h, más de 10 h).
- **Estrato:** P4030S1A1 de la vivienda (C1), agrupado en 1–2, 3–4 y 5–6.
- **Bienes:** P1176S1 (lavadora), S2 (secadora), S3 (nevera) = 1, a nivel de hogar.

### 5. GEIH 2024 (DANE, catálogo 819)

**Archivos usados:** de cada uno de los 12 zips mensuales, los módulos «Datos del hogar y la vivienda», «Características generales, seguridad social en salud y educación» y «Ocupados» (en marzo y abril los CSV venían en un zip anidado).

**Filtro y llaves:** AREA = 08, que corresponde al área metropolitana de Barranquilla (todos los registros son cabecera). Hogar = MES + DIRECTORIO + SECUENCIA\_P; persona = hogar + ORDEN. Ningún hogar se repite entre meses (verificado), así que los 12 meses se apilan: 7.772 hogares. Factor anual = FEX\_C18 / 12.

| Variable del informe | Cómo se construyó |
| --- | --- |
| Estrato | P4030S1A1 |
| Apartamento / casa | P4000 = 2 / 1 |
| Paredes, pisos | P4010, P4020; «piso de cerámica o mejor» = códigos 4–7 |
| Cuartos, dormitorios | P5000, P5010 |
| Tenencia | P5090: 1–2 propia, 3 arriendo |
| Valor de la vivienda | P5110 (precio mínimo de venta estimado por el hogar). **Mediana sin ponderar** de los hogares que responden, que son sobre todo propietarios |
| Personas | P6008 |
| Grupos de edad | conteo de P6040 por hogar (menores de 5, 5–17, 18–64, 65+) |
| Ocupados por hogar | número de personas del hogar en el módulo Ocupados |
| Horas normales de trabajo | P6800; promedio por ocupado = Σ w·(horas del hogar) / Σ w·(ocupados del hogar) |
| Trabajo en la vivienda | P6880 = 1 («en esta vivienda»); % = Σ w·(ocupados en casa) / Σ w·(ocupados) |
| Hogares sin ocupados | hogares con 0 personas en el módulo Ocupados |

### 6. SUI (Superservicios)

**Extracción:** reporte ele\_com\_096 «Consolidado Energía por Empresa, Departamento y Municipio» de reportes.sui.gov.co, en formato HTML, consultado mes a mes (ene-2019 a ago-2026) con los filtros: ubicación = Urbano, departamento = Atlántico, municipio = Barranquilla, y variable = suscriptores, consumo (kWh) o valor del consumo (COP). Son 92 meses × 3 variables; el reporte no trae datos residenciales de junio de 2022.

**Suma de comercializadoras:** cada consulta devuelve una fila por empresa (Electricaribe hasta sep-2020, luego Air-e, más Vatia, Qi Energy, Enertotal y otras menores). Se conservaron las filas con dato en «Total residencial», «ND» se tomó como 0 y se sumaron las empresas para cada estrato (1–6) y para el total residencial.

**Indicadores derivados por mes y estrato:**

- kWh por suscriptor = consumo / suscriptores.
- COP por kWh = valor del consumo / consumo (no separa subsidios ni contribuciones).

**Banderas de calidad** (columna «bandera» del CSV y del Excel), calculadas por estrato:

| Bandera | Regla |
| --- | --- |
| consumo\_atipico | kWh por suscriptor < 0,5 × o > 1,5 × la mediana de todos los meses de ese estrato |
| valor\_negativo | valor del consumo < 0 (refacturaciones) |
| valor\_atipico | COP/kWh > 3 × o < 0,3 × la mediana del estrato |

Un mes queda fuera de un cálculo de consumo si su fila tiene bandera de consumo; fuera de un cálculo de tarifa si tiene cualquier bandera. Meses afectados en el total: sep-2022, ene-2023, mar-2023, sep-2024, oct-2024 y ago-2025 (consumo) y mar–ago 2026 (valor).

**Cálculos del informe:**

| Cifra | Fórmula |
| --- | --- |
| Participación por estrato | suscriptores del estrato / suma de estratos 1–6, en diciembre del año |
| kWh/mes por suscriptor de un año | promedio simple de los meses válidos de ese año |
| COP/kWh de un año | promedio simple de los meses sin bandera |
| Alza ago–sep vs feb–mar | para cada año: promedio (ago, sep) / promedio (feb, mar) − 1, con meses válidos; luego promedio de 2019–2025 |
| Índice estacional del mes | para cada año con 10 o más meses válidos: kWh del mes / promedio del año; luego promedio entre años (2019–2025) |
| Consumo sobre la base feb–mar | para cada año: 1 − promedio (feb, mar) / promedio del año; en kWh: promedio del año − promedio (feb, mar); luego promedio, mínimo y máximo entre años |
| Consumo residencial anual (GWh) | promedio mensual del total en meses válidos × 12 / 10⁶ |

**No residencial:** misma consulta, columnas Industrial, Comercial, Oficial y Otros sumadas sobre todas las empresas (incluye usuarios no regulados) y sin banderas; se reporta la mediana anual del consumo comercial.

### 7. Cálculos que combinan fuentes

### 7.1 Representatividad por estrato

Para cada fuente se calculó la participación de cada estrato sobre los estratos 1–6: en encuestas con pesos (Σw del estrato / Σw total), en el SUI con suscriptores de diciembre y en catastro con los predios residenciales de la base limpia de la tesis (332.718, cifras entregadas por la autora). La cifra de la Alcaldía se tomó tal cual del tablero (solo viene en tres grupos).

### 7.2 Penetración de AC en la ciudad (post-estratificación)

Las encuestas tienen más hogares de estrato 1 que la ciudad real, y el estrato 1 es el que menos AC tiene; el promedio directo de la encuesta sale sesgado hacia abajo. Por eso se combinan la tasa de cada estrato (encuesta) con el peso real de cada estrato (SUI):

```{math}
P_{\text{ciudad}} = \sum_{e=1}^{6} W_e \, p_e, \qquad W_e = \frac{\text{suscriptores}_e}{\sum_{k=1}^{6}\text{suscriptores}_k}
```

| Estrato | W 2019 (SUI dic) | p 2019 (ECV) | W·p | W 2024 (SUI dic) | p 2024 (ECV) | W·p |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 0,338 | 0,077 | 0,026 | 0,333 | 0,124 | 0,041 |
| 2 | 0,199 | 0,251 | 0,050 | 0,193 | 0,342 | 0,066 |
| 3 | 0,228 | 0,427 | 0,097 | 0,229 | 0,458 | 0,105 |
| 4 | 0,140 | 0,538 | 0,075 | 0,150 | 0,782 | 0,118 |
| 5 | 0,052 | 0,867 | 0,045 | 0,054 | 0,813 | 0,044 |
| 6 | 0,042 | 0,983 | 0,041 | 0,041 | 1,000 | 0,041 |
| **Total** | 1 |  | **0,335** | 1 |  | **0,414** |

**Incertidumbre** (muestreo aleatorio simple, n = hogares de la ECV en cada estrato):

```{math}
SE(P) = \sqrt{\sum_e W_e^2 \, \frac{p_e (1-p_e)}{n_e}}
```

- 2019: SE ≈ 1,4 puntos → 33,5 % ± 2,8.
- 2024: SE ≈ 1,7 puntos → 41,4 % ± 3,3 (± 4,1 con el efecto de diseño; ver «Serie de tenencia, error de la encuesta e imputación»).
- Diferencia: 7,9 puntos, con SE ≈ √(1,4² + 1,7²) ≈ 2,2 → z ≈ 3,6.

### 7.3 Chequeo del número de hogares

Población 2025 (DANE, tablero de la Alcaldía) ÷ personas por hogar (ECV 2024) = 1.279.344 / 3,51 ≈ 364.000 hogares. Se compara con suscriptores SUI (≈ 330.000) y predios de catastro (332.718). La ECV 2024 expande a 389.372 hogares (plausible); aun así la expansión a la ciudad se hace con el SUI.

### 7.4 Cota de consumo de AC (supuesto, no medido)

kWh/mes por hogar con AC ≈ potencia × horas × días = 1 kW × 8 h × 30 = 240 kWh. Por suscriptor del estrato: 240 × p\_e (tenencia 2024), por ejemplo 240 × 0,124 ≈ 30 kWh en estrato 1 y 240 × 1,00 = 240 kWh en estrato 6. La potencia de 1 kW para un mini-split de 12.000 BTU/h es un supuesto de orden de magnitud que debe reemplazarse por datos de etiqueta (RETIQ) o de mercado.

### 7.5 Gasto con y sin AC y cruces de tenencia

Todos los cruces (AC por quintil, tenencia de la vivienda, tamaño del hogar, techo y tipo de vivienda) son proporciones ponderadas de hogares con AC dentro de cada celda; las celdas con menos de 30 hogares se señalan como indicativas en el texto.



## Serie anual, regresión e imputación


### 5.1 Postestratificación anual (`postestrat_anual.py`, `postestrat_xlsx.py`)

- Datos: tasas ponderadas por estrato (`ECV_2018_2025_Barranquilla_tenencia_por_estrato.csv`, columnas w y w_ac) y suscriptores SUI de diciembre de cada año (estratos 1–6). Se excluye el grupo 0 (sin estrato, sobre todo rural).
- Fórmula: P = Σ W_e · p_e, con W_e = suscriptores_e / Σ suscriptores (E1–E6).
- EE = √Σ W_e² · p_e(1 − p_e) / n_e (muestreo simple). Control Agresti–Coull: p̃ = (x + 2)/(n + 4), var = p̃(1 − p̃)/(n + 4); cambia el IC como mucho 0,2 pp.
- z entre años: (P_t − P_2019) / √(EE_t² + EE_2019²), años independientes.
- Descomposición frente a 2019: efecto tasas = Σ W_e^2019 (p_e^t − p_e^2019); efecto composición = Σ (W_e^t − W_e^2019) p_e^t.
- Tendencia: mínimos cuadrados ponderados de P contra el año con pesos 1/EE².
- Ejemplo 2024: W = 0,333 / 0,193 / 0,229 / 0,150 / 0,054 / 0,041; p = 0,124 / 0,342 / 0,458 / 0,782 / 0,813 / 1,000 → P = 0,414, EE = 1,70 pp.
- El Excel `Postestratificacion_AC_2018_2025.xlsx` hace el cálculo con fórmulas (hojas Resumen_anual y Detalle_estrato).

### 5.2 Recalculo de tablas ECV 2024 (`ecv24_tablas.py`)

Con la base (709 hogares, 646 en E1–E6): tenencia por estrato, pago mediano (P5018 ÷ P5018S1, válidos 1.000–5.000.000 COP/mes), pago con/sin AC por grupo de estrato, AC por tenencia de vivienda (P5095) y tipo (P1070), quintiles de ingreso por persona (percentiles ponderados 20–40–60–80), techo (P4567: 1 concreto, 2 barro, 3 asbesto, 4 zinc, 5 plástica). Se verificó que 13 hogares con ingreso 0 (sobre todo E3–E5, 53 % con AC) distorsionan Q1.

### 5.3 Regresión logística ECV 2024 (`logit_ecv24.py`)

- n = 633 (E1–E6 sin ingreso 0). Techo en 3 categorías: concreto (P4567 = 1), asbesto (3), «zinc u otro» (4 zinc, 42 hogares, y 2 barro, 3). Estrato agrupado E1–2 (ref.), E3, E4, E5–6. Apartamento: P1070 = 2. ln(ingreso pc) con piso de 10.000 COP. M4 agrega tenencia (P5095: 1–2 propia, 3 arriendo, resto otra) y hogar de 5+ personas.
- Estimación: GLM binomial (statsmodels), var_weights = FEX_C normalizado a media 1, errores HC1. Se reportan OR = e^β con IC95, pseudo-R² de McFadden y AUC ponderado.
- El modelo de imputación «I» (estrato + apartamento, n = 646) se estimó pero no se usa: el tipo de vivienda de la ECV no corresponde al tipo de edificio del catastro.

### 5.4 Serie suavizada y Beta (`serie_suavizada.py`)

1. Olas usadas por estrato: 2018, 2019, 2021, 2022, 2023, 2024, 2025 (2020 excluida: encuesta en parte telefónica y año fuera de la calibración de la propuesta).
2. Modelo por estrato: logit(p_e,año) = b0_e + b1_e (año − 2021). GLM binomial con la tasa ponderada como respuesta y var_weights = n de cada ola.
3. Sobredispersión: φ = χ² de Pearson / gl, mínimo 1; la matriz de covarianza de (b0, b1) se multiplica por φ.
4. Para cada año: η = b0 + b1 (año − 2021); m = 1/(1 + e^−η); EE(η) = √(x' Σ x); DE = m(1 − m) EE(η) (método delta); IC90 = logística(η ± 1,645 EE(η)).
5. Beta por momentos: α = m (m(1 − m)/DE² − 1), β = (1 − m)(m(1 − m)/DE² − 1). El Excel comprueba que α/(α + β) = m.
6. Ciudad: Σ W_e m_e con pesos SUI de diciembre de cada año (2026–2027 con los de 2025); DE = √Σ W_e² DE_e².
7. Limitaciones: tendencia lineal en logit (no capta el bache de E1 en 2020–2021), 2015–2017 y 2026–2027 extrapolados, estratos ajustados por separado (un modelo jerárquico sería una mejora).

### 5.5 Imputación de P(AC) al catastro por año (`imputacion_catastro_anual.py`, `suavizada_xlsx.py`)

1. Tasa objetivo p_e,año = media de la serie suavizada.
2. Dentro del estrato: P(AC | e, techo t) = 1/(1 + e^−(a_e + b_t)), con b_t del modelo M2 2024 (concreto 0, asbesto −1,061, zinc/otro −1,954). Se usa M2 y no M3 porque el catastro no tiene ingreso: interesa la asociación total del techo dentro del estrato.
3. Catastro: si el uso contiene «Apartamentos» (edificio 4+), techo = concreto. Si no (hasta 3 pisos), concreto restante c' = máx(s_concreto − f_e, 0)/(1 − f_e), con f_e = fracción de viviendas del estrato en edificios 4+ y s_t = mezcla de techos de la ECV 2024 en el estrato; el resto (1 − c') se reparte entre asbesto y zinc en la proporción de la ECV.
4. a_e se calcula (método de Brent) para que la P(AC) media **de las viviendas del catastro** del estrato sea exactamente p_e,año (E1 queda forzado; control = 0 en el Excel).
5. Simplificación: la mezcla de techos es la de la ECV 2024 en todos los años (afecta el reparto dentro del estrato, no su total).
6. Salidas: `Catastro_PAC_por_anio_estrato_tipo.csv` (unir por estrato_num + tipo de edificio) y hojas Imputacion_catastro, Ciudad_catastro y Por_posicion del Excel.
7. Sensibilidad E1 sin forzar (2024): a_E1 calibrado con la mezcla de la ECV → P(AC) E1 en catastro 14,4 % (edificio 4+ 25,8 %, hasta 3 pisos 9,7 %).



**Referencias de los métodos:** factores de expansión y estimación por dominios (Lohr, 2019); intervalos de Agresti y Coull (1998); regresión logística ponderada (Hosmer et al., 2013; [Rubio, notas de clase, sección 3.8](https://lihkir.github.io/MachineLearning/linear_model.html#modelos-lineales-para-clasificacion)); errores robustos HC1 (White, 1980; MacKinnon y White, 1985); pseudo-R² (McFadden, 1974); AUC (Hanley y McNeil, 1982; [Rubio, sección 9.4](https://lihkir.github.io/MachineLearning/model_evaluation.html#curvas-precision-recall-y-roc)); Beta por momentos (Gelman et al., 2013). Ver [Referencias](09_referencias.md).
