# tesis-datos-barranquilla

Datos de entrada de la tesis de maestría «Perfiles horarios de demanda eléctrica de climatización y refrigeración residencial por estrato socioeconómico en Barranquilla» (María Carolina Cantillo Orozco, Universidad del Norte).

Sitio: https://mcarocantillo.github.io/tesis-datos-barranquilla/

- `*.md`, `_config.yml`, `_toc.yml`: fuentes del Jupyter Book.
- `tablas/`: tablas resumen (CSV/Excel).
- `scripts/`: procesamiento en Python.

Construir: `pip install "jupyter-book>=1,<2" ghp-import && jupyter-book build . && ghp-import -n -p -f _build/html`
