# Encuestas usadas y representatividad

Este capítulo indica qué encuestas y qué años se usaron, para qué se usó cada una y qué parte de la población de Barranquilla representa su muestra. Las encuestas son muestras: unos cientos de hogares entrevistados representan a toda la ciudad mediante los factores de expansión del DANE. Por eso se reportan dos cifras. La primera es la **fracción de muestreo**, es decir, qué porcentaje de los hogares de la ciudad fue entrevistado. La segunda es la **población expandida**, que es el total de hogares o personas que la encuesta dice representar y que se compara con una cifra de referencia independiente.

Como referencia del número de hogares se usan los suscriptores residenciales de energía de los estratos 1 a 6 en diciembre de cada año (SUI), que coinciden con las 332.718 viviendas del catastro ({numref}`tab-coherencia-hogares`). Como referencia de personas se usa la población de Barranquilla en 2025, 1.279.344 habitantes (DANE, publicada por la Alcaldía) {cite:p}`alcaldia2026`.

## Encuestas y años usados

```{table} Encuestas, años y dominio geográfico usados en la tesis.
:name: tab-encuestas-usadas

| Encuesta | Años usados | Dominio geográfico | Unidad | Para qué se usa |
| --- | --- | --- | --- | --- |
| ECV, DANE {cite:p}`dane_ecv` | 2018, 2019, 2021, 2022, 2023, 2024 y 2025 | Barranquilla (cabecera y resto) | Hogar | Serie anual de tenencia de A/C, ventilador y nevera por estrato |
| ECV, módulo de uso de energéticos | 2019 | Barranquilla | Hogar | Horas diarias de A/C y ventilador, tipo de A/C, tamaño y edad de la nevera |
| ECV, diseño muestral | 2024 | Barranquilla | Hogar | Efecto de diseño, material del techo, regresión logística, personas y cuartos |
| ENUT, DANE {cite:p}`dane_enut` | 2024–2025 (septiembre de 2024 a septiembre de 2025) | Cabeceras del Atlántico | Persona | Composición del hogar, sueño, tiempo fuera de casa y presencia diurna |
| GEIH, DANE {cite:p}`dane_geih` | 2024 (12 meses) | Área metropolitana de Barranquilla | Hogar y persona | Trabajo en la propia vivienda por estrato |

```

No se usan las ECV 2015, 2016 y 2017, porque sus microdatos no identifican el municipio, ni la ECV 2020, que se hizo en parte por teléfono durante la pandemia. Además de las encuestas, el trabajo usa dos registros administrativos que cubren toda la población y no son muestras: el consumo facturado del SUI de 2015 a 2026 {cite:p}`sui2026` y el catastro de 2026, con 332.718 viviendas {cite:p}`catastro2026`.

## ECV: muestra de Barranquilla por año

```{table} Hogares de Barranquilla en la muestra de la ECV, y población que representan.
:name: tab-ecv-muestra

| Año | Hogares en la muestra | Hogares expandidos | Suscriptores residenciales (SUI, dic.) | Fracción de muestreo | Hogares representados por cada hogar entrevistado | Expandidos frente al SUI |
| --- | --- | --- | --- | --- | --- | --- |
| 2018 | 1.003 | 338.861 | 300.745 | 0,33 % | 300 | 112,7 % |
| 2019 | 1.022 | 329.059 | 319.399 | 0,32 % | 313 | 103,0 % |
| 2020* | 778 | 341.102 | 323.568 | 0,24 % | 416 | 105,4 % |
| 2021 | 834 | 358.886 | 356.575 | 0,23 % | 428 | 100,6 % |
| 2022 | 774 | 368.614 | 317.080 | 0,24 % | 410 | 116,3 % |
| 2023 | 728 | 378.731 | 327.032 | 0,22 % | 449 | 115,8 % |
| 2024 | 709 | 389.372 | 330.101 | 0,21 % | 466 | 118,0 % |
| 2025 | 693 | 399.248 | 329.892 | 0,21 % | 476 | 121,0 % |
```

\*La ola 2020 no se usa en la tesis.

En cada ola se entrevistan entre 700 y 1.000 hogares de Barranquilla, entre 0,21 % y 0,33 % de los hogares de la ciudad: cada hogar entrevistado representa a entre 300 y 480 hogares. La muestra es pequeña en términos absolutos, pero está diseñada para ser representativa de la ciudad mediante los factores de expansión. La suma de esos factores es entre 1 % y 21 % mayor que el número de suscriptores, porque la ECV cuenta hogares (puede haber varios por vivienda y viviendas sin medidor propio) y porque sus proyecciones de población difieren de las del registro de facturación. Por eso la tasa de la ciudad se calcula con los pesos del SUI ({numref}`tab-coherencia-estratos`).

En personas, la ECV 2019 entrevistó a 3.865 personas y la ECV 2024 a 2.436, que expandidas representan 1.257.767 y 1.347.343 personas. Frente a los 1.279.344 habitantes de 2025, la muestra de 2024 equivale a 0,19 % de la población, y su expansión, a 105 % de ella.

Por estrato la muestra es mucho menor. En 2024 hubo 250 hogares en el estrato 1, 161 en el 2, 125 en el 3, 52 en el 4, 38 en el 5 y 20 en el 6 ({numref}`tab-vent-nevera`). Por eso los estratos 4 a 6 tienen los intervalos de confianza más amplios y la tenencia se suaviza entre olas.

## ENUT y GEIH

```{table} Muestra y población representada por la ENUT y la GEIH.
:name: tab-enut-geih-muestra

| Encuesta | Dominio | Hogares en la muestra | Personas en la muestra | Hogares expandidos | Personas expandidas | Barranquilla dentro del dominio |
| --- | --- | --- | --- | --- | --- | --- |
| ENUT 2024–2025 | Cabeceras del Atlántico | 1.894 | 6.347 | ≈ 756.700 | 2.739.561 | ≈ 47 % de las personas (1.279.344 de 2.739.561) |
| GEIH 2024 | Área metropolitana de Barranquilla | 7.772 | 27.445 | 583.558 | 2.039.666 | ≈ 63 % de las personas (1.279.344 de 2.039.666) |
```

Ninguna de las dos identifica a Barranquilla por separado. La ENUT solo distingue el departamento y la zona (cabecera o resto); su dominio incluye Barranquilla, Soledad, Malambo, Puerto Colombia y las demás cabeceras del Atlántico. Si la muestra se reparte en proporción a la población, unos 890 de sus 1.894 hogares serían de Barranquilla, alrededor de 0,27 % de los hogares de la ciudad. La GEIH cubre el área metropolitana (Barranquilla, Soledad, Malambo, Puerto Colombia y Galapa) durante los 12 meses de 2024; con el mismo supuesto, unos 4.900 de sus hogares serían de Barranquilla, alrededor de 1,5 % de los hogares de la ciudad. En ambos casos se supone que el comportamiento del dominio representa al de la ciudad (supuesto S10 en {numref}`tab-supuestos`). Las comparaciones por estrato de la GEIH muestran que el área metropolitana tiene más hogares de estratos bajos que Barranquilla ({numref}`tab-coherencia-estratos`), y por eso solo se usa para el trabajo en casa dentro de cada estrato.
