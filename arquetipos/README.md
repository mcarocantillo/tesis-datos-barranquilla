# Arquetipos de vivienda de Barranquilla (Objetivo 1, Fase 1)

Código, preregistro y resultados agregados de la Fase 1 de la tesis: caracterizar los arquetipos de vivienda de
Barranquilla a partir del catastro (332.718 viviendas) y asignar cada vivienda a un arquetipo, según los Pasos 1 a 7
de la sección 7.2 de la propuesta.

## Estado

Los siete pasos están hechos con las dos medidas de carga del Paso 3:

| Solución | Arquetipos | Algoritmo | R² de la carga | Estabilidad (Jaccard) |
| --- | --- | --- | --- | --- |
| Carga por vivienda (como está escrito en la propuesta) | 15 | k-prototypes | 0,63 | 0,98 |
| Carga por m² | 10 | K-Means | 0,93 | 1,00 |

Las dos usan el diseño anidado: se agrupa por separado dentro de cada posición frente a la cubierta (casa, último piso,
sin cubierta) y bloque de estratos (1-2, 3-4, 5-6). El criterio definitivo está pendiente de decisión (ajuste AJ5 en
`ajustes_frente_a_la_propuesta.md`); mientras tanto aplica lo escrito en la propuesta, la carga por vivienda. Todos
los productos existen para las dos soluciones.

Se corrió además una variante del agrupamiento con cuatro variables más del catastro (habitaciones, baños, área del
terreno y VIS o VIP; preregistro, Nota 8, y ajuste AJ19). Es estable, pero explica menos varianza de la carga (0,51
por vivienda y 0,90 por m²), así que los arquetipos no cambian y la variante queda como análisis complementario A9.
Sus salidas llevan el sufijo `_ampliada`.

Una revisión metodológica del 3 de noviembre agregó los ajustes AJ20 a AJ23 (preregistro, Nota 9). Los arquetipos se
describen como clases geométricas, porque la carga del Paso 3 solo depende del área, los pisos, la altura y la
posición. La incertidumbre de la asignación sale de repetir el agrupamiento en las 100 submuestras de estabilidad
(script 10), no de las probabilidades del clasificador. Y el puente entre las casas del catastro y las de la ECV y la
elección de olas de la ECV entran como factores en la sensibilidad de la Fase 2.

Tres pruebas de robustez dejan la solución igual. Con el clima completo de ERA5-Land de GDEX la carga sube 4,4 % y el
R² no cambia (AJ24, script 11). Con un techo propio por vivienda, sorteado de los priors del Paso 6, el techo solo
entraría al agrupamiento si los techos livianos tienen cielo raso, que ni el catastro ni la ECV registran (AJ25,
script 13). Y con todos los edificios en lugar de la submuestra, la solución por m² es idéntica y en la de por vivienda
el 94,8 % de las viviendas conserva su arquetipo, aunque las casas de 3-4 quedan en 5 grupos y no en 4 (AJ27, Nota 10,
script 14). Los mapas de los arquetipos están en `salidas/figuras/mapa_*.png` (script 15), y el script 16 verifica la
coherencia de todas las salidas con 43 comprobaciones.

La verificación del 9 de noviembre encontró tres errores de implementación, corregidos antes de volver a correr la
Fase 1 completa (preregistro, Nota 11, y ajuste AJ28). La posición frente a la cubierta se calcula ahora dentro de
cada torre (24 dígitos del número predial) y no del predio matriz, lo que pasa 2.088 viviendas de sin cubierta a
último piso y 252 a casa. La incertidumbre de la asignación ya no empareja los grupos por el método húngaro, que daba
probabilidades falsas. Y en la variante ampliada las variables numéricas dejaron de entrar también como categóricas.
Con la nueva corrida la solución por m² no cambia, y la de por vivienda pasa de 17 a 15 arquetipos (casas de 3-4 en 4
grupos y no en 6), porque el paso de 16 a 17 estaba en el umbral de 0,02 y la submuestra cambió con el conjunto de
casas. Los resultados anteriores se guardan en `datos_internos/antes_nota11/`, que no se publica.

## Contenido

| Ruta | Qué tiene |
| --- | --- |
| `preregistro/preregistro_fase1.md` | Reglas de cada paso, fijadas antes de calcular (versiones 1 a 5 y notas 1 a 11, con fecha y motivo) |
| `preregistro/decision_fase1.json` | Las mismas reglas en formato máquina; los scripts las leen de aquí |
| `ajustes_frente_a_la_propuesta.md` | Registro de cada punto en que la ejecución precisa o ajusta la propuesta radicada (AJ1 a AJ28) |
| `referencias_revisadas.md` | Referencias de arquetipos, agrupamiento e infiltración, con metadatos verificados en Crossref |
| `src/` | Módulos comunes: rutas y variables (`comun.py`), carga simplificada (`carga.py`), agrupamiento (`agrupamiento.py`), lectura de la ECV (`ecv.py`) y estilo de figuras (`estilo.py`) |
| `scripts/` | Scripts 01 a 16 (el 10 se corre antes del 09; el 12, que unirá los materiales del catastro, se agregará cuando lleguen los datos) |
| `salidas/tablas/` | Tablas agregadas de cada paso (prefijos `reglas_`, `carga_`, `agr_`, `clf_`, `asg_`, `env_`, `hog_`, `val_`, `clima_`, `techo_`, `todos_`) y la verificación (`verificacion.csv`) |
| `salidas/figuras/` | Figuras con el estilo de la propuesta |
| `salidas/fichas/` | Una ficha por arquetipo para cada solución, en Markdown y en CSV |
| `salidas/modelos/` | Árboles de decisión que asignan una vivienda a su arquetipo (hojas de al menos 50 viviendas) |

Los productos de la Fase 1 que pide la propuesta son la base de arquetipos con su clasificador
(`salidas/tablas/arquetipos_*.csv` y `salidas/modelos/`), las fichas (`salidas/fichas/`) y la tabla de priors de
envolvente con su fuente (`salidas/tablas/env_priors_*.csv` y `.json`, y `env_propiedades_materiales.csv`).

## Scripts

| Script | Paso | Qué hace | Tiempo aproximado |
| --- | --- | --- | --- |
| `01_tipologia_reglas.py` | 4 (referencia) | Tipología por reglas: tipo × posición × época × bloque | segundos |
| `02_carga_simplificada.py` | 3 | Carga anual simplificada de cada vivienda con envolvente común | 30 s |
| `03_agrupamiento.py` | 2 a 4 | K-Means, k-prototypes y jerárquico con Gower; número de grupos y estabilidad. Con `--ampliada`, la variante de la Nota 8 | 1,5 h; 1,2 h la variante |
| `04_eleccion.py` | 2 y 3 | Elección del algoritmo (Nota 4), elección entre las dos variantes si existe la ampliada (Nota 8) y base final de arquetipos | segundos |
| `05_sensibilidad_atipicos.py` | complementario | Agrupamiento sin excluir los atípicos de DBSCAN (A5) | minutos |
| `06_clasificador.py` | 5 | Árbol de decisión y Random Forest que resumen la regla de asignación; su fidelidad en los bloques de prueba | 11 min |
| `07_priors_envolvente.py` | 6 | Materiales de la ECV, prueba de Rao-Scott, priors de envolvente e infiltración | segundos |
| `08_sensibilidad_variables.py` | 7 | Sensibilidad de las soluciones a cada variable de agrupamiento | 3 min |
| `10_incertidumbre_asignacion.py` | 5 | Incertidumbre de la asignación: repite el agrupamiento en las 100 submuestras de estabilidad (Nota 9) | 20 min |
| `09_hogar_validacion_fichas.py` | 7 | Atributos del hogar, representatividad frente a la ECV y fichas; usa la salida del 10 | segundos |
| `11_contraste_clima_gdex.py` | 3 (robustez) | Carga del Paso 3 y R² de los arquetipos con ERA5-Land de GDEX en lugar de la copia de Open-Meteo (AJ24) | 1 min con la serie extraída |
| `13_sensibilidad_techo.py` | 3 (robustez) | Carga del Paso 3 con un techo propio por vivienda, sin y con cielo raso, y cuánto sube el R² si el techo se agrega a los arquetipos (AJ25) | minutos |
| `14_agrupamiento_todos_edificios.py` | 2 a 4 (robustez) | La solución final ajustada con los 177.093 edificios en lugar de la submuestra (AJ27, Nota 10). Con `--prueba`, el 10 % de los edificios | 42 min |
| `15_mapas_arquetipos.py` | 7 | Mapas de los arquetipos y de las casas que cambian con el script 14, en celdas de unos 275 m | 1 min |
| `16_verificacion.py` | todos | Comprobaciones automáticas de coherencia y reproducibilidad de las salidas | 1 min |

Desde la carpeta `arquetipos/`:

```bash
python scripts/01_tipologia_reglas.py
python scripts/02_carga_simplificada.py
# ... y así hasta 08, en orden; luego 10 y 09; después 11, 13, 14 y 15
python scripts/16_verificacion.py
```

Semilla 42 en todo el trabajo. Versiones usadas: Python 3.14, numpy 2.4, pandas 3.0, scipy 1.17, scikit-learn 1.8,
kmodes 0.12.2, joblib 1.5, matplotlib 3.11 y pyarrow para leer y escribir Parquet.

## Entradas que no se publican

Los scripts buscan sus entradas con rutas relativas a la carpeta que contiene `arquetipos/` (en esta copia, la raíz
del repositorio):

| Entrada | Ruta esperada | Fuente |
| --- | --- | --- |
| Catastro procesado, una fila por vivienda | `e2_git/datos/viviendas.pkl.gz` | Catastro de Barranquilla, depurado en el trabajo previo de predicción del estrato |
| Número predial de cada vivienda, para identificar la torre (Nota 11) | `e1_git/datos/procesados/dataset_modelado.parquet` y `sin_coordenadas.parquet` | Trabajo previo de predicción del estrato; las leen todos los scripts a través de `src/comun.py` |
| Particiones espaciales del trabajo previo | `e1_git/datos/procesados/dataset_modelado.parquet` y el módulo kNNDM en `e4/` | Trabajo previo de predicción del estrato (solo para el script 06) |
| Clima horario 2015–2025 | `compuerta_horaria/datos/crudos/openmeteo/` | ERA5-Land y ERA5 en Open-Meteo; la descarga se reconstruye con los scripts de `scripts/compuerta/` |
| Clima horario de GDEX (robustez, script 11) | `compuerta_horaria/datos/crudos/era5land_gdex/` | ERA5-Land de NCAR GDEX en la celda de Barranquilla, extraído con `scripts/compuerta/01b_extraer_era5land_gdex.py` |
| ECV 2019 y 2024 de Barranquilla | `../DANE/ECV/` (una carpeta más arriba), con los ZIP tal como se descargan | Catálogo de microdatos del DANE |

## Privacidad

Solo se publican agregados. No se publican la asignación de cada vivienda a su arquetipo ni sus probabilidades, las
cargas por vivienda ni los Random Forest, que pueden memorizar registros: todo eso queda en `datos_internos/`, que no se versiona. Tampoco
se versiona `consultas/`, con borradores de correspondencia. Algunas tablas de la ECV tienen celdas pequeñas (desde 6
hogares) y la tipología por reglas antes de fusionar tiene celdas desde 9 viviendas; son conteos y proporciones
agregados, sin datos personales, y se reportan con su tamaño de muestra.
