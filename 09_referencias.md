# Referencias

Fuentes de los datos, de los métodos estadísticos y del software usados en este sitio. Las secciones de las notas de clase del profesor Lihki Rubio se citan con su enlace directo.

## Datos

- Alcaldía de Barranquilla, Gerencia de Gestión Catastral. *Catastro: servicio de datos abiertos* (capas 305, 315, 500, 505, 601 y 602). https://miciudad.barranquilla.gov.co/gis/rest/services/catastro/datosabiertos/MapServer. Consultado: 15 sep. 2026.
- Alcaldía de Barranquilla, Gerencia de Ciudad. *Tablero Estadísticas de Ciudad*. https://barranquilla.gov.co/gerencia-de-ciudad/tablero-estadisticas-de-ciudad. Consultado: 14 oct. 2026.
- DANE (2016–2026). *Encuesta Nacional de Calidad de Vida (ECV)*, microdatos 2015 (cat. 419), 2016 (456), 2017 (544), 2018 (607), 2019 (678), 2020 (718), 2021 (734), 2022 (793), 2023 (827), 2024 (861) y 2025 (905). https://microdatos.dane.gov.co/index.php/catalog/861
- DANE (2025). *Encuesta Nacional de Uso del Tiempo (ENUT) 2024–2025*, cat. 910. https://microdatos.dane.gov.co/index.php/catalog/910
- DANE (2025). *Gran Encuesta Integrada de Hogares (GEIH) 2024*, cat. 819. https://microdatos.dane.gov.co/index.php/catalog/819
- Superintendencia de Servicios Públicos Domiciliarios. *SUI, reporte ele_com_096: consolidado de energía por empresa, departamento y municipio*. https://reportes.sui.gov.co/fabricaReportes/frameSet.jsp?idreporte=ele_com_096. Consultado: oct. 2026.
- Cantillo Orozco, M. C., y Oñoro Araujo, J. C. (2026). *Estrato socioeconómico y características catastrales de la vivienda en Barranquilla. Entregable 1*, curso de aprendizaje automático, Universidad del Norte. https://mcarocantillo.github.io/entregable1-ml-barranquilla/

## Notas de clase

- Rubio, L. (2026). *Machine Learning: notas de clase*. Universidad del Norte. https://lihkir.github.io/MachineLearning/
  - Sección 2.6, [Análisis exploratorio de datos](https://lihkir.github.io/MachineLearning/knn_model.html#analisis-exploratorio-de-datos): descripción y depuración de las bases.
  - Sección 3.8, [Modelos lineales para clasificación](https://lihkir.github.io/MachineLearning/linear_model.html#modelos-lineales-para-clasificacion): regresión logística de la tenencia de A/C.
  - Secciones 9.3 y 9.4, [Métricas de evaluación](https://lihkir.github.io/MachineLearning/model_evaluation.html#metricas-de-evaluacion-y-scoring) y [curvas ROC](https://lihkir.github.io/MachineLearning/model_evaluation.html#curvas-precision-recall-y-roc): AUC del modelo logístico.
  - Sección 10.3, [Data leakage](https://lihkir.github.io/MachineLearning/chains_pipelines.html#data-leakage): separación entre datos de calibración (2015–2019) y de validación.
  - Secciones 8.1, 8.2 y 8.5, [K-Means](https://lihkir.github.io/MachineLearning/clustering.html#k-means), [selección de k](https://lihkir.github.io/MachineLearning/clustering.html#seleccion-automatica-de-k) y [DBSCAN](https://lihkir.github.io/MachineLearning/clustering.html#dbscan): base de la construcción de arquetipos (siguiente fase).

## Muestreo y estimación con encuestas

- Kish, L. (1965). *Survey Sampling*. Wiley. — Efecto de diseño (deff) y tamaño efectivo de muestra.
- Holt, D., y Smith, T. M. F. (1979). Post stratification. *Journal of the Royal Statistical Society, Series A*, 142(1), 33–46. — Postestratificación con los suscriptores del SUI.
- Wolter, K. M. (2007). *Introduction to Variance Estimation* (2.ª ed.). Springer. — Linealización de Taylor para la varianza de una razón con conglomerados.
- Lohr, S. L. (2019). *Sampling: Design and Analysis* (2.ª ed.). CRC Press. — Estimación por dominios, factores de expansión y postestratificación.
- Agresti, A., y Coull, B. A. (1998). Approximate is better than "exact" for interval estimation of binomial proportions. *The American Statistician*, 52(2), 119–126. — Intervalos de proporciones con muestras pequeñas (estratos 5 y 6).

## Modelos estadísticos

- McCullagh, P., y Nelder, J. A. (1989). *Generalized Linear Models* (2.ª ed.). Chapman & Hall. — Modelo binomial con enlace logit y estimación de la sobredispersión con el χ² de Pearson.
- Hosmer, D. W., Lemeshow, S., y Sturdivant, R. X. (2013). *Applied Logistic Regression* (3.ª ed.). Wiley. — Regresión logística ponderada y razones de momios.
- White, H. (1980). A heteroskedasticity-consistent covariance matrix estimator and a direct test for heteroskedasticity. *Econometrica*, 48(4), 817–838.
- MacKinnon, J. G., y White, H. (1985). Some heteroskedasticity-consistent covariance matrix estimators with improved finite sample properties. *Journal of Econometrics*, 29(3), 305–325. — Errores estándar robustos HC1.
- McFadden, D. (1974). Conditional logit analysis of qualitative choice behavior. En P. Zarembka (Ed.), *Frontiers in Econometrics* (pp. 105–142). Academic Press. — Pseudo-R².
- Hanley, J. A., y McNeil, B. J. (1982). The meaning and use of the area under a receiver operating characteristic (ROC) curve. *Radiology*, 143(1), 29–36. — AUC.
- Oehlert, G. W. (1992). A note on the delta method. *The American Statistician*, 46(1), 27–29. — Desviación estándar de la tenencia suavizada.
- Hoeting, J. A., Madigan, D., Raftery, A. E., y Volinsky, C. T. (1999). Bayesian model averaging: a tutorial. *Statistical Science*, 14(4), 382–401. — Promedio de especificaciones (variante C) y varianza entre modelos.
- Gelman, A., Carlin, J. B., Stern, H. S., Dunson, D. B., Vehtari, A., y Rubin, D. B. (2013). *Bayesian Data Analysis* (3.ª ed.). CRC Press. — Distribución Beta como prior de una proporción.
- Brent, R. P. (1973). *Algorithms for Minimization without Derivatives*. Prentice-Hall. — Búsqueda del intercepto en la imputación al catastro.

## Software

- McKinney, W. (2010). Data structures for statistical computing in Python. *Proceedings of the 9th Python in Science Conference*, 56–61. — pandas.
- Seabold, S., y Perktold, J. (2010). statsmodels: Econometric and statistical modeling with Python. *Proceedings of the 9th Python in Science Conference*, 92–96.
- Virtanen, P., et al. (2020). SciPy 1.0: Fundamental algorithms for scientific computing in Python. *Nature Methods*, 17, 261–272.
- Hunter, J. D. (2007). Matplotlib: A 2D graphics environment. *Computing in Science & Engineering*, 9(3), 90–95.
- Executable Books Community (2020). *Jupyter Book*. https://jupyterbook.org
