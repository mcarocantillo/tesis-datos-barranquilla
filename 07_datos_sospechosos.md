# Datos sospechosos y pendientes

| Dato | Qué se ve | Qué se hizo / hacer |
| --- | --- | --- |
| E4 2019 | 53 % con AC vs 75 % (2018) y 73–92 % después | Resuelto con la serie suavizada (70,4 %) |
| E4 2020–2021 | 91,5 % (n = 58) y 89,2 %; 2020 en parte telefónica | 2020 fuera del ajuste |
| E1 en el SUI | Consume más que E2–E3 con 5–19 % de AC; en 2018–2020 su kWh es el más caro (656–764 COP vs 452–514 en E6) | Confirmar con Air-e; calibrar con E2–E6 mientras tanto |
| Catastro vs ECV en E1 | 29,5 % de viviendas de E1 en edificios 4+, pero solo 17 % con techo de concreto en la ECV | E1 forzado a la ECV; resolver en la Fase 1 al asignar techos |
| SUI dic-2021 | 356.575 suscriptores (E1 120.329), vuelve a 317.080 en 2022 | No usar para totales |
| Rurales ECV 2024 | 24,8 % con AC (n = 60) vs 6 % en 2019 y 2025 | Quedan fuera (estrato 0) |
| Quintiles 2024 | Q1 > Q2 por 13 hogares con ingreso 0 | Excluirlos |
| E5–E6 | 7–72 hogares por ola; E6 en 100 % | Agresti–Coull / serie suavizada |
| Meses SUI | Falta jun-2022; sep–oct 2024 y ago-2025 sin consumo; sep-2022, ene y mar 2023 negativos; mar–ago 2026 tarifa 10–20× en E5–E6 | Excluidos con banderas |
| SUI E3 dic-2024 | 449 COP/kWh vs 676–858 en meses vecinos | Revisado en v3: usar para kWh, no para tarifa (columna bandera_revision) |
| Techo concreto E1–2 | 15,5 % (2019) → 28,6 % (2024) | Posible ruido; promediar olas |
| Lavadora E1 | 62 % → 48 % | Cambio de pregunta |
| Hogares expandidos ECV | 329.000 (2019) → 399.000 (2025) | Expandir con SUI |
| Alcaldía | 13 % de viviendas en E5–6 vs 9 % catastro/SUI | Diferencia de universo |
| «Apartamento» ECV | 48 % de E1 vive en «apartamento», 68 % bajo asbesto | No usar como proxy de altura |

---


## Pendientes

**Datos por conseguir:**

1. **Clima ERA5-Land.** En Copernicus el formulario por hora solo deja un año y un mes por solicitud. Se pasó a **NCAR GDEX, dataset d633008** («Get a Subset», requiere cuenta NCAR):
   - Producto **ERA5-Land instantaneous hourly data**: 2m temperature, 2m dewpoint temperature, 10m u-component of wind, 10m v-component of wind, surface pressure.
   - Producto **ERA5-Land accumulated hourly data**: surface solar radiation downwards, surface thermal radiation downwards (opcional total precipitation).
   - Periodo: 1-ene-2015 a lo más reciente. Área (enteros, el formulario no acepta decimales): Norte 12, Sur 10, Oeste −75, Este −74 (en 0–360: 285 y 286). Formato NetCDF. NCAR avisa por correo (puede tardar horas o 1–2 días; revisar spam; descargar pronto).
   - Alternativa: en Copernicus, «ERA5-Land hourly time-series data from 1950 to present», punto lat 10.96, lon −74.80, CSV, todo el periodo en una solicitud.
2. **IDEAM**, estación 0029045190 «APTO ERNESTO CORTISSOZ», datos.gov.co: temperatura (sbwg-7ju4), humedad relativa (uext-mhny), viento (sgfv-3yp8). Registros cada pocos minutos: agregar a horario. Sin radiación.
3. **Fracción climatizada de CEELA** para el prior del número de equipos.
4. Confirmar con Air-e el consumo/tarifa de E1 y pedir curva horaria.

**Procesamiento pendiente:**

5. Procesar el clima: NetCDF → serie horaria en la celda de Barranquilla (y la del aeropuerto), hora local UTC−5, desacumular la radiación (ERA5 acumula desde 00 UTC del día de pronóstico: valor horario = acumulado(h) − acumulado(h−1), salvo a la 01 UTC), humedad relativa e índice de calor, validación contra IDEAM (sesgo, RMSE, por hora del día y mes), grados-día/grados-hora de enfriamiento, cruce con la estacionalidad del SUI por estrato.
6. Aplicar en la propuesta los seis cambios del documento «Ajustes metodológicos…».
7. Fase 1: arquetipos con catastro + GEIH (k-prototypes; ejes estrato y tipo; diseño plano vs anidado según la propuesta), asignación de techos por estrato y tipo antes del AC.
8. Fase 2–3: cadena de presencia con ENUT, módulo térmico 5R1C, calibración ABC-SMC con SUI y XM.
