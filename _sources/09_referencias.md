# Referencias

Este capítulo reúne las fuentes de los datos, los métodos estadísticos y el software usados en el sitio. La {numref}`tab-metodos-refs` indica qué referencia respalda cada método y en qué capítulo se aplica. Las secciones de las notas de clase del profesor Lihki Rubio {cite:p}`rubio_ml` se enlazan directamente al final.

## Métodos y su respaldo

```{table} Métodos usados en el procesamiento y referencias que los respaldan.
:name: tab-metodos-refs

| Método | Uso en este trabajo | Referencia |
| --- | --- | --- |
| Estimación ponderada por dominios | Proporciones y medias por estrato con los factores de expansión | {cite:t}`lohr2019` |
| Efecto de diseño | Error de la ECV 2024 con 76 segmentos como conglomerados | {cite:t}`kish1965` |
| Linealización de Taylor | Varianza de una razón con conglomerados | {cite:t}`wolter2007` |
| Postestratificación | Tasa de la ciudad con los pesos del SUI | {cite:t}`holt1979` |
| Intervalos de Agresti y Coull | Proporciones con muestras pequeñas (E5, E6) | {cite:t}`agresti1998` |
| Modelo lineal generalizado binomial con sobredispersión | Serie anual de tenencia por estrato | {cite:t}`mccullagh1989` |
| Método delta | Desviación estándar de la tenencia suavizada | {cite:t}`oehlert1992` |
| Promedio de especificaciones | Variante C de la serie y varianza entre modelos | {cite:t}`hoeting1999` |
| Distribución Beta por momentos | Insumos de tenencia como distribuciones | {cite:t}`gelman2013` |
| Regresión logística ponderada | Tenencia de A/C según techo, estrato e ingreso | {cite:t}`hosmer2013`; {cite:t}`rubio_ml`, sección 3.8 |
| Errores estándar robustos HC1 | Inferencia de la regresión logística | {cite:t}`white1980`; {cite:t}`mackinnon1985` |
| Pseudo-R² de McFadden | Ajuste de la regresión logística | {cite:t}`mcfadden1974` |
| Área bajo la curva ROC | Discriminación de la regresión logística | {cite:t}`hanley1982`; {cite:t}`rubio_ml`, sección 9.4 |
| Método de Brent | Intercepto de la imputación al catastro | {cite:t}`brent1973` |
| Índice de disimilitud | Comparación de la distribución por estrato entre fuentes | {cite:t}`duncan1955` |
| Humedad relativa por la fórmula de Magnus | Humedad a partir de la temperatura y el punto de rocío de ERA5-Land | {cite:t}`alduchov1996` |
| Índice de calor de la NOAA | Variable climática de la compuerta horaria | {cite:t}`rothfusz1990` |
| Errores estándar HAC | Inferencia de la respuesta horaria de la demanda al calor | {cite:t}`newey1987` |
```

## Bibliografía

```{bibliography}
:all:
```

## Notas de clase: secciones usadas

Rubio, L. (2026). *Machine Learning: notas de clase*. Universidad del Norte. <https://lihkir.github.io/MachineLearning/>

- Sección 2.6, [Análisis exploratorio de datos](https://lihkir.github.io/MachineLearning/knn_model.html#analisis-exploratorio-de-datos): descripción y depuración de las bases.
- Sección 3.8, [Modelos lineales para clasificación](https://lihkir.github.io/MachineLearning/linear_model.html#modelos-lineales-para-clasificacion): regresión logística de la tenencia de A/C.
- Secciones 9.3 y 9.4, [Métricas de evaluación](https://lihkir.github.io/MachineLearning/model_evaluation.html#metricas-de-evaluacion-y-scoring) y [curvas ROC](https://lihkir.github.io/MachineLearning/model_evaluation.html#curvas-precision-recall-y-roc): AUC del modelo logístico.
- Sección 10.3, [Data leakage](https://lihkir.github.io/MachineLearning/chains_pipelines.html#data-leakage): separación entre los datos de calibración (2015–2019) y los de validación.
- Secciones 8.1, 8.2 y 8.5, [K-Means](https://lihkir.github.io/MachineLearning/clustering.html#k-means), [selección de k](https://lihkir.github.io/MachineLearning/clustering.html#seleccion-automatica-de-k) y [DBSCAN](https://lihkir.github.io/MachineLearning/clustering.html#dbscan): base de la construcción de arquetipos (Fase 1).
