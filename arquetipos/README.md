# Arquetipos de vivienda de Barranquilla (Objetivo 1, Fase 1)

Código, preregistro y resultados agregados de la Fase 1 de la tesis: caracterizar los arquetipos de vivienda de
Barranquilla a partir del catastro (332.718 viviendas) y asignar cada vivienda a un arquetipo, según los Pasos 1 a 7
de la sección 7.2 de la propuesta.

## Estado

Los siete pasos están hechos con las dos medidas de carga del Paso 3:

| Solución | Arquetipos | Algoritmo | R² de la carga | Estabilidad (Jaccard) |
| --- | --- | --- | --- | --- |
| Carga por vivienda (como está escrito en la propuesta) | 17 | k-prototypes | 0,66 | 0,97 |
| Carga por m² | 10 | K-Means | 0,93 | 1,00 |

Las dos usan el diseño anidado: se agrupa por separado dentro de cada posición frente a la cubierta (casa, último piso,
sin cubierta) y bloque de estratos (1-2, 3-4, 5-6). El criterio definitivo está pendiente de decisión (ajuste AJ5 en
`ajustes_frente_a_la_propuesta.md`); mientras tanto aplica lo escrito en la propuesta, la carga por vivienda. Todos
los productos existen para las dos soluciones.

Se corrió además una variante del agrupamiento con cuatro variables más del catastro (habitaciones, baños, área del
terreno y VIS o VIP; preregistro, Nota 8, y ajuste AJ19). Es estable, pero explica menos varianza de la carga (0,53
por vivienda y 0,91 por m²), así que los arquetipos no cambian y la variante queda como análisis complementario A9.
Sus salidas llevan el sufijo `_ampliada`.

## Contenido

| Ruta | Qué tiene |
| --- | --- |
| `preregistro/preregistro_fase1.md` | Reglas de cada paso, fijadas antes de calcular (versiones 1 a 5 y notas 1 a 8, con fecha y motivo) |
| `preregistro/decision_fase1.json` | Las mismas reglas en formato máquina; los scripts las leen de aquí |
| `ajustes_frente_a_la_propuesta.md` | Registro de cada punto en que la ejecución precisa o ajusta la propuesta radicada (AJ1 a AJ19) |
| `referencias_revisadas.md` | Referencias de arquetipos, agrupamiento e infiltración, con metadatos verificados en Crossref |
| `src/` | Módulos comunes: rutas y variables (`comun.py`), carga simplificada (`carga.py`), agrupamiento (`agrupamiento.py`), lectura de la ECV (`ecv.py`) y estilo de figuras (`estilo.py`) |
| `scripts/` | Scripts 01 a 09, en el orden en que se corren |
| `salidas/tablas/` | Tablas agregadas de cada paso (prefijos `reglas_`, `carga_`, `agr_`, `clf_`, `env_`, `hog_`, `val_`) |
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
| `06_clasificador.py` | 5 | Árbol de decisión y Random Forest; validación espacial | 11 min |
| `07_priors_envolvente.py` | 6 | Materiales de la ECV, prueba de Rao-Scott, priors de envolvente e infiltración | segundos |
| `08_sensibilidad_variables.py` | 7 | Sensibilidad de las soluciones a cada variable de agrupamiento | 3 min |
| `09_hogar_validacion_fichas.py` | 7 | Atributos del hogar, representatividad frente a la ECV y fichas | segundos |

Desde la carpeta `arquetipos/`:

```bash
python scripts/01_tipologia_reglas.py
python scripts/02_carga_simplificada.py
# ... y así hasta 09, en orden
```

Semilla 42 en todo el trabajo. Versiones usadas: Python 3.14, numpy 2.4, pandas 3.0, scipy 1.17, scikit-learn 1.8,
kmodes 0.12.2, joblib 1.5, matplotlib 3.11 y pyarrow para leer y escribir Parquet.

## Entradas que no se publican

Los scripts buscan sus entradas con rutas relativas a la carpeta que contiene `arquetipos/` (en esta copia, la raíz
del repositorio):

| Entrada | Ruta esperada | Fuente |
| --- | --- | --- |
| Catastro procesado, una fila por vivienda | `e2_git/datos/viviendas.pkl.gz` | Catastro de Barranquilla, depurado en el trabajo previo de predicción del estrato |
| Particiones espaciales del trabajo previo | `e1_git/datos/procesados/dataset_modelado.parquet` y el módulo kNNDM en `e4/` | Trabajo previo de predicción del estrato (solo para el script 06) |
| Clima horario 2015–2025 | `compuerta_horaria/datos/crudos/openmeteo/` | ERA5-Land y ERA5 en Open-Meteo; la descarga se reconstruye con los scripts de `scripts/compuerta/` |
| ECV 2019 y 2024 de Barranquilla | `../DANE/ECV/` (una carpeta más arriba), con los ZIP tal como se descargan | Catálogo de microdatos del DANE |

## Privacidad

Solo se publican agregados. No se publican la asignación de cada vivienda a su arquetipo, las cargas por vivienda ni
los Random Forest, que pueden memorizar registros: todo eso queda en `datos_internos/`, que no se versiona. Tampoco
se versiona `consultas/`, con borradores de correspondencia. Algunas tablas de la ECV tienen celdas pequeñas (desde 6
hogares) y la tipología por reglas antes de fusionar tiene celdas desde 9 viviendas; son conteos y proporciones
agregados, sin datos personales, y se reportan con su tamaño de muestra.
