# Diseño de experimentos A/B — cadena mayorista (Argentina)

Proyecto de portafolio de ciencia de datos: diseño y análisis de un experimento
A/B en una cadena mayorista (mismo tipo de negocio que Maxiconsumo, donde
trabajé), que testea un cartel de promoción nuevo contra el actual en la
góndola de una categoría, midiendo el efecto en conversión y en ticket
promedio.

## Por qué este proyecto

En mi paso por Maxiconsumo (supermercado mayorista) se probaban cambios en la
exhibición y la comunicación de precios/promociones sin un marco formal para
medir si realmente funcionaban mejor que lo anterior. Este proyecto está
inspirado en esa realidad: cómo diseñar un experimento controlado, calcular
cuánto tiempo hace falta correrlo, analizarlo correctamente, y traducir el
resultado en una recomendación de negocio -- no solo "correr un test y mirar
el p-valor".

**Nota sobre los datos:** el dataset (`data/raw/`) es 100% sintético, generado
con [`src/generate_data.py`](src/generate_data.py). Simula 10 semanas de
visitantes en 4 sucursales, con un efecto real inyectado (+4 puntos
porcentuales de conversión y +8% de ticket promedio para el cartel nuevo) que
el análisis debe poder recuperar. Este repo es autocontenido: no depende de
los otros proyectos del portafolio.

## Decisiones de diseño que vale la pena destacar

**La unidad de randomización determina la unidad de análisis.** El cartel se
asigna una vez por día en cada sucursal -- no se le puede mostrar una variante
distinta a cada visitante individual el mismo día. Por eso la randomización
(y todo el análisis posterior) se hace a nivel día, no a nivel visitante. El
proyecto muestra explícitamente, como contraste, qué pasaría si se analizara
por error a nivel visitante: un p-valor artificialmente mucho más chico que da
una falsa sensación de seguridad (pseudoreplicación).

**Bloqueo por día de la semana.** El tráfico varía fuerte según el día (lunes
y viernes con más movimiento, sábado con menos). Para que esa variación no
desbalanceara la comparación, la asignación de variante se bloqueó por día de
semana: cada combinación sucursal x día de semana tiene exactamente la mitad
de sus semanas con cada variante.

**Cálculo de tamaño de muestra antes del análisis.** Se calcula cuántos días
de experimento hacen falta para detectar un efecto de cierta magnitud, usando
la variabilidad día a día real de los datos -- la pregunta que hay que
hacerse *antes* de lanzar un experimento, no después.

**De la significancia estadística a la decisión de negocio.** Un resultado
significativo no alcanza por sí solo -- el proyecto traduce el efecto medido a
un impacto de negocio estimado (ingreso incremental proyectado) para poder
tomar una decisión informada.

## Objetivo del proyecto

1. Explorar el experimento, validar que el bloqueo por día de semana funcionó,
   y entender por qué la unidad de análisis es el día
   (`notebooks/01_eda.ipynb`).
2. Calcular el tamaño de muestra (en días) necesario para detectar distintos
   efectos, y contrastarlo contra el cálculo ingenuo a nivel visitante
   (`notebooks/02_tamano_muestra.ipynb`).
3. Correr el test de hipótesis correcto, comparar contra el enfoque ingenuo, y
   llegar a una recomendación de negocio (`notebooks/03_analisis_resultados.ipynb`).
4. Explorar los resultados de forma interactiva y calcular tamaño de muestra
   para futuros experimentos, en una demo con Streamlit (`app/`).

## Stack tecnológico

- **Lenguaje:** Python 3.10+
- **Análisis:** pandas, numpy
- **Estadística:** scipy, statsmodels
- **Visualización:** matplotlib, seaborn, plotly
- **Demo:** Streamlit
- **Entorno:** venv + `requirements.txt`, desarrollado en VS Code + Jupyter

## Estructura del repo

```
portfolio-experimento-ab/
├── data/
│   ├── raw/              # datos sintéticos generados (csv)
│   └── processed/        # métricas diarias agregadas (no versionadas)
├── notebooks/
│   ├── 01_eda.ipynb                    # exploración y chequeo de balance
│   ├── 02_tamano_muestra.ipynb         # poder estadístico y tamaño de muestra
│   └── 03_analisis_resultados.ipynb    # test de hipótesis y decisión
├── src/
│   └── generate_data.py    # generador del dataset sintético
├── app/
│   └── streamlit_app.py    # dashboard + calculadora de tamaño de muestra
├── docs/
│   └── guia_tecnica_conceptos.md
├── requirements.txt
└── README.md
```

## Cómo correrlo

```bash
python -m venv .venv
source .venv/bin/activate  # en Windows: .venv\Scripts\activate
pip install -r requirements.txt

# (opcional) regenerar el dataset sintético
python src/generate_data.py

# abrir los notebooks 01, 02 y 03 en VS Code o Jupyter, en orden

# correr la demo interactiva (después de correr el notebook 01)
streamlit run app/streamlit_app.py
```

## Estado del proyecto

- [x] Generación del dataset sintético
- [x] Notebook 01: EDA y chequeo de balance del diseño
- [x] Notebook 02: tamaño de muestra y poder estadístico
- [x] Notebook 03: análisis de resultados y decisión
- [x] Demo en Streamlit

## Para entender el porqué de cada decisión técnica

[`docs/guia_tecnica_conceptos.md`](docs/guia_tecnica_conceptos.md) es una guía
de estudio que explica, con intuición primero y fórmulas como extra, por qué
se usó cada técnica del proyecto (hipótesis nula/alternativa, errores tipo
I/II, unidad de randomización, bloqueo, tamaño de muestra y poder, t-test,
p-valor e intervalo de confianza, significancia estadística vs. práctica),
con preguntas de autoevaluación por tema.

## Autor

Agustín Vignau — Data Analyst Jr en formación (Tecnicatura en Ciencia de Datos e IA, IFTS N°18).
[LinkedIn](https://www.linkedin.com/in/agustinvignau/)
