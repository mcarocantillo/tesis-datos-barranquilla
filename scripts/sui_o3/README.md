# Consumo del SUI por tipo de lectura (cubo O3)

Scripts del capítulo «Consumo del SUI por tipo de lectura». Se corrieron desde la carpeta de trabajo `ml_trabajo/analisis_consumo_sui`, con los datos de O3 en `datos_o3/` y el clima de la compuerta horaria; las rutas al inicio de cada script apuntan a esa estructura.

| Script | Qué hace |
| --- | --- |
| `o3_a_csv.py` | Convierte la respuesta de la vista de O3 (página y filas) en un CSV mes × estrato × tipo de lectura. |
| `caida_consumo.py` | Consumo por suscriptor del consolidado, ajuste por clima y precio real del estrato 4. |
| `lecturas_reales.py` | Lo mismo con solo lecturas reales; parte del consumo sin lectura real. |
| `comparacion_municipios.py` | Barranquilla, Soledad, Santa Marta, Cartagena y Medellín. |
