# Datos sospechosos y pendientes

| Dato | Qué se ve | Qué se hizo / hacer |
| --- | --- | --- |
| E4 2019 | 53 % con AC vs 75 % (2018) y 73–92 % después | Resuelto con la serie suavizada (70,4 %) |
| E4 2020–2021 | 91,5 % (n = 58) y 89,2 %; 2020 en parte telefónica | 2020 fuera del ajuste |
| E1 en el SUI | Consume más que E2–E3 con 5–19 % de AC; en 2018–2020 su kWh es el más caro (656–764 COP vs 452–514 en E6). En 2021–2024, con solo lecturas reales, CEELA da 229 kWh/mes frente a 311 en el repositorio (+36 %); en E2–E6 la diferencia es de 3–7 % ({numref}`tab-ceela-sui`) | Parte del exceso vendría de consumos que no son lecturas reales. Descargar el SUI con el filtro de tipo de lectura; confirmar con Air-e; calibrar con E2–E6 mientras tanto |
| Catastro vs ECV en E1 | 29,5 % de viviendas de E1 en edificios 4+, pero solo 17 % con techo de concreto en la ECV | Revisado: la altura del catastro es coherente (74 lotes de bloques de 5 pisos, 43 m² de mediana); la ECV casi no capta esos edificios (2 de 26 segmentos con hogares de E1, 7,7 esperados). Usar los techos de la ECV solo para casas; A/C de E1 2024 reponderado 14,5–15,2 % como sensibilidad. Script `catastro_e1_edificios.py` |
| Año de construcción en edificios de E1–E2 | 15.376 apartamentos en edificios de 4+ pisos con años 1932–1972 (ninguno en E3–E6 antes de 1975) | Muy probablemente erróneos (un solo año por lote, vienen así en la descarga original); confirmar con Catastro o imágenes históricas y, mientras tanto, tratar como faltantes en la Fase 1 |
| SUI dic-2021 | 356.575 suscriptores (E1 120.329), vuelve a 317.080 en 2022 | No usar para totales |
| Rurales ECV 2024 | 24,8 % con AC (n = 60) vs 6 % en 2019 y 2025 | Quedan fuera (estrato 0) |
| Quintiles 2024 | Q1 > Q2 por 13 hogares con ingreso 0 | Excluirlos |
| E5–E6 | 7–72 hogares por ola; E6 en 100 % | Agresti–Coull / serie suavizada |
| Meses SUI | Falta jun-2022; sep–oct 2024 y ago-2025 sin consumo; sep-2022, ene y mar 2023 negativos; mar–ago 2026 tarifa 10–20× en E5–E6 | Excluidos con banderas |
| SUI E3 dic-2024 | 449 COP/kWh vs 676–858 en meses vecinos | Usar para kWh, no para tarifa (columna bandera_revision) |
| Techo concreto E1–2 | 15,5 % (2019) → 28,6 % (2024) | Posible ruido; promediar olas |
| Lavadora E1 | 62 % → 48 % | Cambio de pregunta |
| Hogares expandidos ECV | 329.000 (2019) → 399.000 (2025) | Expandir con SUI |
| Alcaldía | 13 % de viviendas en E5–6 vs 9 % catastro/SUI | Diferencia de universo |
| «Apartamento» ECV | 48 % de E1 vive en «apartamento», 68 % bajo asbesto | No usar como proxy de altura |

---


## Pendientes

**Datos por conseguir:**

1. **ERA5-Land del Climate Data Store.** El clima horario ya se procesó con la copia de ERA5-Land de Open-Meteo ([Respuesta horaria al calor](15_compuerta_horaria.md)). Falta descargar la serie oficial con `scripts/compuerta/01a_descargar_era5land_cds.py`, que usa el conjunto «reanalysis-era5-land-timeseries» (serie en el punto lat 10,96, lon −74,80, 2015 a la fecha, en una sola solicitud) y requiere la cuenta personal del CDS (`~/.cdsapirc`) y aceptar la licencia de ERA5-Land. Después hay que repetir `01_clima.py procesar` y `03_estimar.py`. La alternativa por área sigue siendo NCAR GDEX, dataset d633008.
2. **SUI con el filtro de tipo de lectura.** Descargar de la herramienta O3 del SUI el consumo residencial de Barranquilla urbano por estrato con el filtro «tipo de lectura/medición» en datos reales, como hizo CEELA, para separar los consumos estimados y confirmar el consumo del estrato 1 ({numref}`tab-ceela-sui`).
3. Confirmar con Air-e el consumo/tarifa de E1 y pedir curva horaria.
4. **Año de construcción del catastro.** Preguntar a la Gerencia de Gestión Catastral qué registra `anio_construccion` (¿fecha original o última incorporación/actualización?). Solo 1.442 casas de la ciudad son anteriores a 1975 y 15.376 apartamentos de E1–E2 en bloques recientes tienen años 1932–1972. Mientras tanto se usa como «año de registro catastral» (supuesto S13); revisar también la variable `antiguedad` del entregable de ML.

**Ya procesado:**

- **IDEAM**, estación 0029045190 «APTO ERNESTO CORTISSOZ» (temperatura sbwg-7ju4 y humedad relativa uext-mhny de datos.gov.co), agregada a horario y contrastada con ERA5-Land ({numref}`tab-coherencia-clima`).
- **Clima horario** de ERA5-Land (copia de Open-Meteo) en hora local, con humedad relativa e índice de calor.
- **Demanda horaria de XM** del mercado de Air-e (2021–2025) y de Electricaribe (2015–2019), con la compuerta horaria: la forma horaria del A/C queda en capa C ([Respuesta horaria al calor](15_compuerta_horaria.md)).
- **Línea base de CEELA**: envolvente, zona climatizada, consigna y COP de los edificios representativos de Barranquilla ([Línea base de CEELA](16_ceela.md)).

**Procesamiento pendiente:**

5. Con el archivo del CDS: desacumular la radiación (ERA5 acumula desde las 00 UTC: valor horario = acumulado(h) − acumulado(h−1), salvo a la 01 UTC), repetir el contraste con IDEAM y la compuerta, y calcular grados-día y grados-hora de enfriamiento para cruzarlos con la estacionalidad del SUI por estrato.
6. Aplicar en la propuesta los seis cambios del documento «Ajustes metodológicos…».
7. Fase 1: arquetipos con catastro + GEIH (k-prototypes; ejes estrato y tipo; diseño plano vs anidado según la propuesta), asignación de techos por estrato y tipo antes del AC, con la envolvente de CEELA como centro de los rangos (S15).
8. Fase 2–3: cadena de presencia con ENUT, módulo térmico 5R1C, calibración ABC-SMC con SUI y XM; de XM se usa la respuesta por franjas como blanco de validación, no la forma hora a hora (S16).
