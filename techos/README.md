# Piloto: color de los techos con la ortoimagen

Piloto del módulo opcional del Paso 6 de la propuesta, que estima el tono de los techos de Barranquilla con la ortoimagen WorldView Legion de 2026 y las construcciones del catastro. El método y los resultados están en el capítulo «Color de los techos con la ortoimagen (piloto)» del sitio (`19_techos.md`).

| Archivo | Contenido |
| --- | --- |
| `piloto_techos.ipynb` | Notebook para Colab (versión 2): techos unidos por predio, máscara de árboles y sombra, etiquetado de tono y color, tono automático, bosque aleatorio y ResNet50 con validación por zona, proporciones corregidas por estrato y demostración de color |
| `scripts/ejemplos_techos.py` | Figuras de ejemplo con la misma regla de la sección 3 del notebook, sin aprendizaje. Uso: `python scripts/ejemplos_techos.py <carpeta piloto_techos> figuras` |
| `figuras/` | Figuras del capítulo. `0_v1_matrices_confusion.png` es la salida de la primera versión del notebook |

Las imágenes y los polígonos no se versionan. Salen del servidor ArcGIS de la Gerencia de Gestión Catastral (`miciudad.barranquilla.gov.co`, licencia CC BY-SA 4.0): ortoimagen `orto/orto35_worldview_08001barranquilla_2026`, ortofoto `orto8_MAS_08001urbano_2016`, construcciones `catastro/datosabiertos` capa 310 y manzanas `ordenamiento/estratificacion` capa 1. Se descargaron el 20-nov-2026 con el navegador, en seis recortes de 200 × 200 m (EPSG:9377), uno por estrato. El notebook espera esos recortes empaquetados en `piloto_techos.tar` dentro de `MyDrive/piloto_techos/`.

Las etiquetas por techo se guardan en Drive y no se publican. Semilla 42.
