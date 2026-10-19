# Fuentes, decisiones y glosario

## Fuentes

| Fuente | Uso | Notas |
| --- | --- | --- |
| ECV 2019 (DANE, cat. 678) | Única ola con horas y tipo de AC (P5523, P5524) y horas de ventilador (P5526); tamaño y edad de nevera | No pregunta número de equipos de AC (verificado en el DDI). 1.009 hogares en Barranquilla (P1_DEPARTAMENTO 08 + P1_MUNICIPIO 001) |
| ECV 2024 (cat. 861) | Tenencia (P1077S11 AC, S12 ventilador, S2 nevera), techo, tipo, ingreso | **709 hogares** en 698 viviendas |
| ECV 2018–2025 (cat. 607, 678, 718, 734, 793, 827, 861, 905) | Serie anual de tenencia | 2016 (456) y 2017 (544) no traen municipio. 2015 no se ha revisado |
| ENUT 2024–2025 (cat. 910) | Duraciones de actividades | Atlántico cabecera, sin municipio ni hora del día |
| GEIH 2024 (cat. 819) | Vivienda, trabajo en casa | Área metropolitana (AREA 08), 12 meses, peso FEX_C18/12 |
| SUI ele_com_096 | Suscriptores, kWh y COP por estrato y mes | Barranquilla urbano residencial, ene-2015 a ago-2026, suma de comercializadoras, con banderas de calidad |
| Catastro (repo `mcarocantillo/entregable1-ml-barranquilla`, `src/limpieza.py`) | Viviendas, estrato, pisos, uso | 332.718 viviendas |

**Llaves de hogar (importante):** en archivos de hogar de la ECV, hogar = DIRECTORIO + SECUENCIA_ENCUESTA (SECUENCIA_P vale siempre 1). En archivos de personas, SECUENCIA_P = hogar y SECUENCIA_ENCUESTA = persona.

**Regla general:** de las encuestas se usan solo las tasas dentro de cada estrato; la expansión a la ciudad se hace con suscriptores SUI o viviendas de catastro. IC con muestreo aleatorio simple; el efecto de diseño medido en 2024 es ≈ 1,5 (ver «Serie de tenencia, error de la encuesta e imputación»): multiplicar varianzas por 1,5.

---

## Decisiones metodológicas

1. **ECV 2024** (hogar = DIRECTORIO + SECUENCIA_ENCUESTA): 709 hogares, 389.372 hogares expandidos. Todas las tablas de 2024 se recalcularon (`ecv24_tablas.py`).
2. **Penetración de la ciudad = postestratificación** con suscriptores SUI de diciembre de cada año (no con los pesos de la ECV, que subestiman 1–6 pp porque la ECV tiene demasiados hogares de E1).
3. **Tenencia para el modelo = variante C de la serie suavizada por estrato y año** (mezcla de un ajuste logit-lineal y uno de nivel constante, sin la ola 2020, con sobredispersión), expresada como **Beta por estrato y año**, 2015–2027. Esto sigue la propuesta («ola de cada año, suavizada entre olas», «cada proporción como Beta»).
4. **Estrato 4**: ya no se fija un valor; se usa la serie suavizada (70,4 % en 2019, 79,0 % en 2024). El 53 % observado en 2019 se considera sospechoso.
5. **Estrato 1 en el catastro forzado a la tasa de la ECV** (suavizada), porque la propuesta dice que la tenencia viene de la ECV y no se calibra. La versión sin forzar (≈ +2 pp en E1, +0,7 pp en la ciudad) queda como **sensibilidad** en el registro de supuestos.
6. **Imputación al catastro**: tasa del estrato fija; la regresión (modelo M2 de 2024) solo reparte la tenencia según el techo dentro del estrato; edificio de 4+ pisos (uso catastral con «Apartamentos») = techo de concreto.
7. **Quintiles de ingreso**: excluir hogares con ingreso 0 (13 en 2024) al construir quintiles.

---


## Glosario

- **E1 … E6**: estrato socioeconómico 1 … 6. E1–E2 bajos (subsidiados), E3 medio-bajo, E4 medio (tarifa plena), E5–E6 altos (pagan contribución).
- **pp (puntos porcentuales)**: diferencia entre dos porcentajes restándolos (33,3 % → 44,9 % = +11,6 pp; en términos relativos sería +35 %).
- **n**: hogares de la muestra, sin ponderar. **Ponderado**: con el factor de expansión FEX_C (ECV, ENUT) o FEX_C18/12 (GEIH).
- **IC95**: intervalo de confianza del 95 %. **EE**: error estándar (IC95 ≈ 1,96 × EE). **z**: diferencia / su EE; significativo si |z| > 1,96.
- **Postestratificación**: tasa de cada estrato de la encuesta × peso real del estrato (suscriptores SUI).
- **OR**: razón de momios. **AUC**: capacidad de un modelo de ordenar hogares con y sin AC (0,5 azar, 1 perfecto).
- **Beta**: distribución de probabilidad para una proporción; se usa como prior de tenencia en el modelo.
