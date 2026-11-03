# Referencias revisadas para la Fase 1 (2-nov-2026)

Metadatos verificados en Crossref; contenido tomado del resumen (Semantic Scholar u OpenAlex) o del texto completo
cuando se indica. Las marcadas «solo título» no se leyeron: verificar su método antes de citarlas por él.

## Arquetipos con agrupamiento

| Referencia | Qué hace | Relación con la Fase 1 |
| --- | --- | --- |
| Ali, U., Shamsi, M. H., Alshehri, F., Mangina, E. y O'Donnell, J. (2018). Comparative analysis of machine learning algorithms for building archetypes development in urban energy modeling. *2018 Building Performance Analysis Conference and SimBuild*, pp. 60–67 (ASHRAE e IBPSA-USA). | Compara K-Means, jerárquico, DBSCAN y K-Medoids sobre certificados energéticos de Irlanda (203 variables); K-Means forma mejores grupos | Comparar varios algoritmos, como en el Paso 2 |
| Dahlström, L., Johari, F., Broström, T. y Widén, J. (2024). Identification of representative building archetypes: A novel approach using multi-parameter cluster analysis applied to the Swedish residential building stock. *Energy and Buildings*, 303, 113823. doi:10.1016/j.enbuild.2023.113823 | K-Means con 10 variables, incluidas socioeconómicas; 12 y 13 arquetipos; métricas para elegir el número; validación sin consumos medidos | Precedente para incluir el nivel socioeconómico (estrato) y elegir k con métricas |
| De Jaeger, I., Reynders, G., Callebaut, C. y Saelens, D. (2020). A building clustering approach for urban energy simulations. *Energy and Buildings*, 208, 109671. doi:10.1016/j.enbuild.2019.109671 | Agrupar por propiedades del edificio da una precisión comparable a agrupar por indicadores energéticos, en demanda anual y pico | Respalda agrupar con variables del catastro y evaluar con la carga (Pasos 2 y 3) |
| Li, X., Yao, R., Liu, M., Costanzo, V., Yu, W., Wang, W., Short, A. y Li, B. (2018). Developing urban residential reference buildings using clustering analysis of satellite images. *Energy and Buildings*, 169, 417–429. doi:10.1016/j.enbuild.2018.03.064 | Agrupa rasgos geométricos (imágenes satelitales) en Chongqing; los arquetipos reproducen el consumo del parque (+0,03 % calefacción, +2,97 % enfriamiento) | Agrupamiento geométrico con validación agregada |
| Pasichnyi, O., Wallin, J. y Kordas, O. (2019). Data-driven building archetypes for urban building energy modelling. *Energy*, 181, 360–377. doi:10.1016/j.energy.2019.04.197 | Con los mismos datos, distintos problemas (renovación, calefacción eléctrica) piden arquetipos distintos | Respalda que el criterio (por vivienda o por m²) dependa del propósito (AJ5) |
| Schildt, M., Ferrando, M., Nardelli, C., Causone, F., van Treeck, C. y Frisch, J. (2025). Cross-examination of country-specific archetypes generation for urban building energy modelling (UBEM). *Sustainable Cities and Society*, 135, 106940. doi:10.1016/j.scs.2025.106940 | Revisión sistemática: los datos locales disponibles y el objetivo de la segmentación deciden el método | Marco para justificar el método con los datos del catastro |
| Fan, C., Liu, R. y Liao, Y. (2025). Archetype identification and energy consumption prediction for old residential buildings based on multi-source datasets. *Buildings*, 15, 2573. doi:10.3390/buildings15142573 | Guangzhou (clima cálido y húmedo): arquetipos por forma (lados y pisos); 17 a 21 kWh/m² de enfriamiento | Precedente en clima cálido y húmedo |
| Ghiassi, N. y Mahdavi, A. (2017). Reductive bottom-up urban energy computing supported by multivariate cluster analysis. *Energy and Buildings*, 144, 372–386. doi:10.1016/j.enbuild.2017.03.004 | Solo título: agrupamiento multivariado para reducir el parque (Viena) | Por verificar |
| Famuyibo, A. A., Duffy, A. y Strachan, P. (2012). Developing archetypes for domestic dwellings—An Irish case study. *Energy and Buildings*, 50, 150–157. doi:10.1016/j.enbuild.2012.03.033 | Solo título | Por verificar |
| Schaefer, A. y Ghisi, E. (2016). Method for obtaining reference buildings. *Energy and Buildings*, 128, 660–672. doi:10.1016/j.enbuild.2016.07.001 | Solo título: edificios de referencia en Brasil | Precedente latinoamericano, por verificar |
| Schaefer, A., Scolaro, T. P. y Ghisi, E. (2024). Cluster analysis applied to obtaining reference models for building thermal performance studies. *Journal of Building Engineering*, 89, 109273. doi:10.1016/j.jobe.2024.109273 | Solo título: análisis de conglomerados para modelos de referencia (Brasil) | Precedente latinoamericano, por verificar |

## Arquetipos por reglas (leídos completos)

- Zhang, M., Chen, S., Ren, Y., Yu, Z. y Yu, J. (2025). Hourly cooling demand prediction through a bottom-up model in London. *International Journal of Green Energy*, 22(11), 2197–2210. doi:10.1080/15435075.2025.2452220 — 4 tipos × 3 épocas, 396 perfiles; U por época; validación por m².
- Mavrogianni, A. et al. (2009). Space heating demand and heatwave vulnerability: London domestic stock. *Building Research & Information*, 37(5-6), 583–597. doi:10.1080/09613210903162597 — época × forma desde SIG; envolvente = moda de la encuesta nacional por combinación.
- Cerezo, C., Sokol, J., Reinhart, C. y Al-Mumin, A. (2015). Three methods for characterizing building archetypes in urban energy simulation. A case study in Kuwait City. *Proceedings of BS2015*, Hyderabad, pp. 2873–2880 — los arquetipos fijos aciertan el promedio pero no la dispersión (56 % de error); con distribuciones calibradas, 30 %.
- Lombardi, F. et al. (2019). Bottom-up lumped-parameters thermodynamic modelling of the Italian residential building stock. *Tecnica Italiana – Italian Journal of Engineering Science*, 63(2-4), 349–356. doi:10.18280/ti-ijes.632-434 — 4 geometrías × 5 épocas × 6 zonas; factor de sombra 0,75 (0,5 a 1). Ojo: el resumen de Scispace le asigna otra revista.
- Huang, Y. J. y Brodrick, J. (2000). A bottom-up engineering estimate of the aggregate heating and cooling loads of the entire U.S. building stock. *ACEEE Summer Study on Energy Efficiency in Buildings*, LBNL-46303 — prototipos por tipo, región y época con promedios de la RECS.

## Infiltración

| Referencia | Dato | Uso posible |
| --- | --- | --- |
| Nazaroff, W. W. (2021). Residential air-change rates: A critical review. *Indoor Air*, 31(2), 282–313. doi:10.1111/ina.12785 | Unos 40 estudios y 10.000 viviendas con gases trazadores: lognormal con media geométrica de 0,5 h⁻¹ y desviación geométrica de 2,0; medias de cada estudio entre 0,2 y 1 h⁻¹; incluye apertura de ventanas | Forma lognormal y orden de magnitud general |
| Mathur, U. y Damle, R. (2021). Impact of air infiltration rate on the thermal transmittance value of building envelope. *Journal of Building Engineering*, 40, 102302. doi:10.1016/j.jobe.2021.102302 | 20 apartamentos con A/C en la India (puerta sopladora): de 0,53 a 1,63 renovaciones por hora, según la construcción de las ventanas; la infiltración es del 10 % al 33 % de las ganancias por la envolvente | Ancla para construcción cerrada (losa, mampostería, ventanas corredizas) en clima cálido |
| Rodrigues, L., Tubelo, R., Vega Pasos, A., Gonçalves, J. C. S., Wood, C. y Gillott, M. (2021). Quantifying airtightness in Brazilian residential buildings with focus on its contribution to thermal comfort. *Building Research & Information*, 49(6), 639–660. doi:10.1080/09613218.2020.1825064 | Primeras mediciones en Brasil (São Paulo, prueba de pulso): 3 multifamiliares de 1970, 1980 y 2000, de 1 a 5,7 h⁻¹ a 4 Pa | Ancla latinoamericana; extremo alto para construcción antigua |

No se encontraron mediciones de infiltración en viviendas colombianas, ni el valor que usa la línea base de la
Resolución 549 de 2015. CEELA modela la ventilación natural, pero no publica la infiltración con ventanas cerradas.
