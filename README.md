# tesis-datos-barranquilla

Datos de entrada de la tesis de maestría «Perfiles horarios de demanda eléctrica de climatización y refrigeración residencial por estrato socioeconómico en Barranquilla» (María Carolina Cantillo Orozco, Maestría en Ingeniería Mecánica, Universidad del Norte).

**Sitio:** https://mcarocantillo.github.io/tesis-datos-barranquilla/

## Contenido

- `*.md`, `_config.yml`, `_toc.yml`, `referencias.bib`, `_ext/`, `_static/`: fuentes del Jupyter Book.
- `figuras/`: figuras del sitio.
- `tablas/`: tablas resumen (CSV con separador «;» y Excel).
- `scripts/`: procesamiento en Python.

Las bases por hogar y por vivienda no se publican; los microdatos son públicos en el catálogo del DANE y en el SUI.

## Reproducir

```bash
pip install -r requirements.txt
jupyter-book build .
ghp-import -n -p -f _build/html   # publica en la rama gh-pages
```

## Cómo citar

Cantillo Orozco, M. C. (2026). *Datos de entrada de la tesis: demanda de enfriamiento residencial en Barranquilla* [sitio web y repositorio]. Universidad del Norte. https://github.com/mcarocantillo/tesis-datos-barranquilla

Los metadatos de cita están en `CITATION.cff`.

## Licencia

- Código (`scripts/`, `_ext/`): MIT (ver `LICENSE`).
- Textos, figuras y tablas resumen: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.es).
- Los microdatos originales conservan las condiciones de uso del DANE, la Superintendencia de Servicios Públicos Domiciliarios y la Alcaldía de Barranquilla.
