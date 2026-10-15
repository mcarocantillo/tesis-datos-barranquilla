# Datos de entrada de la tesis: demanda de enfriamiento residencial en Barranquilla

**María Carolina Cantillo Orozco** · Maestría en Ingeniería Mecánica, Universidad del Norte · Actualizado: 14 de octubre de 2026

Este sitio reúne el procesamiento de las fuentes públicas que alimentan el modelo *bottom-up* horario de aire acondicionado (A/C), ventiladores y neveras de la tesis «Perfiles horarios de demanda eléctrica de climatización y refrigeración residencial por estrato socioeconómico en Barranquilla»: la Encuesta Nacional de Calidad de Vida (ECV) del DANE, la Encuesta Nacional de Uso del Tiempo (ENUT), la Gran Encuesta Integrada de Hogares (GEIH), el consumo del Sistema Único de Información de servicios públicos (SUI) y el catastro de Barranquilla.

Uno de los insumos centrales del modelo es **cuántos hogares tienen aire acondicionado (A/C)** en cada estrato y en cada año. La ECV del DANE lo pregunta, pero en Barranquilla encuesta pocos hogares por estrato, así que la cifra sube y baja de un año a otro más por azar que por cambios reales. Por eso se estima una curva que suaviza esos saltos. Según ella, **el 35,6 % de los hogares de la ciudad tenía A/C en 2019 y el 41,2 % en 2024**.

Los datos no permiten saber si la tenencia viene creciendo en todos los estratos o solo en algunos, así que la curva promedia las dos posibilidades (en este sitio se llama *variante C*). Su margen de error incluye esa duda y la forma en que se diseñó la muestra de la encuesta: para la ciudad en 2024 es de unos ± 4 puntos.

```{figure} figuras/tenencia_estrato_C.png
:width: 100%
Serie de tenencia que usa el modelo (variante C). La ola 2020 no entra en el ajuste.
```

## Cómo leer este sitio

- **Análisis y conclusiones**: qué dicen los datos y qué implican para el modelo.
- **Fuentes y decisiones**, **Resultados** y **Metodología**: cifras y cálculos detallados.
- **Serie de tenencia, error de la encuesta e imputación** y **Cambios a la propuesta**: los métodos más recientes y los textos listos para la propuesta.
- **Reproducibilidad**: scripts y tablas resumen de este repositorio.

Las bases por hogar y por vivienda no se publican aquí; los microdatos son públicos en el [catálogo del DANE](https://microdatos.dane.gov.co) y el [SUI](https://reportes.sui.gov.co).
