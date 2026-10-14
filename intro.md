# Datos de entrada de la tesis: demanda de enfriamiento residencial en Barranquilla

**María Carolina Cantillo Orozco** · Maestría en Ingeniería Mecánica, Universidad del Norte · Actualizado: 14 de octubre de 2026

Este sitio reúne el procesamiento de las fuentes públicas que alimentan el modelo *bottom-up* horario de aire acondicionado (A/C), ventiladores y neveras de la tesis «Perfiles horarios de demanda eléctrica de climatización y refrigeración residencial por estrato socioeconómico en Barranquilla»: la Encuesta Nacional de Calidad de Vida (ECV) del DANE, la Encuesta Nacional de Uso del Tiempo (ENUT), la Gran Encuesta Integrada de Hogares (GEIH), el consumo del Sistema Único de Información de servicios públicos (SUI) y el catastro de Barranquilla.

La tenencia de aire acondicionado (A/C) que usará el modelo cambia a la **variante C**: una mezcla de la serie con tendencia y la serie sin tendencia, que da 35,6 % de hogares con A/C en la ciudad en 2019 y 41,2 % en 2024. Además, el margen de error de la ECV es 1,5 veces mayor en varianza de lo que se suponía (41,4 % ± 4,1 puntos en 2024, no ± 3,3), y la relación entre posición frente a la cubierta y A/C debe presentarse como resultado de la imputación, no como un dato observado.

```{figure} figuras/tenencia_estrato_C.png
:width: 100%
Serie de tenencia que usa el modelo (variante C). La ola 2020 no entra en el ajuste.
```

## Cómo leer este sitio

- **Análisis y conclusiones**: qué dicen los datos y qué implican para el modelo.
- **Fuentes y decisiones**, **Resultados** y **Metodología**: cifras y cálculos detallados.
- **Ajustes v3** y **Cambios a la propuesta**: las correcciones más recientes, listas para llevar a la propuesta.
- **Reproducibilidad**: scripts y tablas resumen de este repositorio.

Las bases por hogar y por vivienda no se publican aquí; los microdatos son públicos en el [catálogo del DANE](https://microdatos.dane.gov.co) y el [SUI](https://reportes.sui.gov.co).
