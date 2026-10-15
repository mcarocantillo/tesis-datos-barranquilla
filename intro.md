# Datos de entrada de la tesis: demanda de enfriamiento residencial en Barranquilla

**María Carolina Cantillo Orozco** · Maestría en Ingeniería Mecánica, Universidad del Norte · Actualizado: 14 de octubre de 2026

Este sitio reúne el procesamiento de las fuentes públicas que alimentan el modelo *bottom-up* horario de aire acondicionado (A/C), ventiladores y neveras de la tesis «Perfiles horarios de demanda eléctrica de climatización y refrigeración residencial por estrato socioeconómico en Barranquilla»: la Encuesta Nacional de Calidad de Vida (ECV) del DANE, la Encuesta Nacional de Uso del Tiempo (ENUT), la Gran Encuesta Integrada de Hogares (GEIH), el consumo del Sistema Único de Información de servicios públicos (SUI) y el catastro de Barranquilla.

Uno de los insumos centrales del modelo es la **tenencia de aire acondicionado (A/C) por estrato socioeconómico y por año**. La ECV del DANE registra esta variable, pero el tamaño de la muestra de Barranquilla en cada estrato es reducido, por lo que las proporciones anuales presentan una variabilidad muestral elevada. Para obtener una serie estable, la tenencia de cada estrato se modela con una regresión logística sobre las olas 2018–2025 de la encuesta. El modelo entrega una estimación para cada año entre 2015 y 2027; la proporción de hogares con A/C en la ciudad es de **35,6 % en 2019**, último año del periodo de calibración (2015–2019), **41,2 % en 2024**, año de referencia de la tesis, y 43,1 % en 2025, la ola más reciente.

Para cada estrato se ajustaron dos especificaciones. La primera supone que la tenencia cambia a un ritmo constante en el tiempo (tendencia lineal en escala logit) en los seis estratos. La segunda conserva esa tendencia solo donde la prueba de significancia la respalda, los estratos 1 y 3 (p < 0,05), y en los estratos 2, 4, 5 y 6, cuya pendiente estimada no se distingue de la variabilidad muestral (p entre 0,39 y 0,53), supone un nivel constante igual al promedio de las olas. Como los datos no permiten preferir una especificación sobre la otra, la serie adoptada (*variante C*) promedia ambas con igual peso. Las dos coinciden en los años con encuesta y se separan al extrapolar a 2015–2017 y 2026–2027 (hasta 2,9 puntos para la ciudad en 2015); esa diferencia se incorpora a la incertidumbre de la serie, junto con el efecto del diseño muestral de la encuesta. Para la ciudad, el intervalo de confianza del 95 % en 2024 es de ± 2,9 puntos porcentuales.

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
