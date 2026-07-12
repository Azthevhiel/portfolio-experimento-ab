# Guía técnica del proyecto: por qué usamos esto y no lo otro

Misma lógica que las guías de los otros proyectos del portafolio: intuición
primero, fórmula como algo opcional, autoevaluación al final de cada tema con
la respuesta escondida. Esta guía asume que la estadística que viste en la
facultad fue básica -- vamos a construir cada concepto desde cero, con
ejemplos concretos, antes de aplicarlo al proyecto.

---

## Unidad 1 — Formular el experimento como una pregunta estadística

### 1.1 — Hipótesis nula y alternativa

**La idea de fondo:** cuando comparamos el cartel A contra el B, en realidad
estamos comparando dos explicaciones posibles de lo que vemos en los datos:

- **Hipótesis nula (H0):** "no hay ninguna diferencia real entre A y B; la
  diferencia que se ve en los datos es solo ruido, azar del muestreo."
- **Hipótesis alternativa (H1):** "sí hay una diferencia real entre A y B."

Un test de hipótesis es, en el fondo, un procedimiento para decidir cuál de
las dos explicaciones es más creíble a la luz de los datos observados. Es
importante notar que el test **nunca prueba que H0 es verdadera** -- en el
mejor de los casos, encuentra evidencia suficiente para rechazarla (o no
encuentra evidencia suficiente, y se queda con H0 "por default", sin que eso
signifique que quedó demostrada).

**Analogía:** es como un juicio. La hipótesis nula es "inocente" -- se asume
por defecto, y hace falta evidencia suficiente para condenar (rechazar H0).
"No condenado" no es lo mismo que "probado inocente" -- puede ser que
simplemente no hubo evidencia suficiente.

<details>
<summary>❓ Autoevaluación 1.1</summary>

1. Si un test de hipótesis "no rechaza H0", ¿significa eso que quedó
   demostrado que no hay diferencia entre A y B?

**Respuesta:** no. "No rechazar H0" significa que no hubo evidencia
suficiente en los datos para descartarla -- puede ser porque realmente no hay
diferencia, o puede ser porque el experimento no tuvo el tamaño de muestra
suficiente para detectar una diferencia que sí existe. Un test de hipótesis
nunca "prueba" H0, solo la rechaza o no la rechaza.
</details>

### 1.2 — Los dos tipos de error posibles

Como con cualquier decisión tomada con información incompleta, hay dos formas
de equivocarse:

|                          | H0 es verdadera (no hay diferencia real) | H0 es falsa (sí hay diferencia real) |
|--------------------------|:---:|:---:|
| **Rechazo H0** (digo que hay diferencia) | Error tipo I (falso positivo) | Decisión correcta |
| **No rechazo H0** (digo que no hay diferencia) | Decisión correcta | Error tipo II (falso negativo) |

- **Alpha (α)** es la probabilidad de cometer un error tipo I -- se fija de
  antemano (normalmente 5%) como el riesgo de falsa alarma que estamos
  dispuestos a aceptar.
- **Beta (β)** es la probabilidad de cometer un error tipo II. El **poder
  estadístico** del test es `1 - β`: la probabilidad de detectar una
  diferencia real, si esa diferencia realmente existe.

<details>
<summary>❓ Autoevaluación 1.2</summary>

1. Bajamos alpha de 0.05 a 0.01 (exigimos mucha más evidencia antes de
   declarar una diferencia significativa). Sin cambiar nada más, ¿qué le pasa
   a la probabilidad de cometer un error tipo II?

**Respuesta:** aumenta. Hay una tensión entre los dos tipos de error: exigir
menos falsos positivos (alpha más chico) hace, en igualdad de condiciones, que
sea más difícil rechazar H0 -- lo que aumenta la probabilidad de no detectar
una diferencia real que sí existe (más errores tipo II, menos poder). Por eso
alpha y poder se eligen juntos, no por separado.
</details>

---

## Unidad 2 — Diseñar el experimento antes de correrlo

### 2.1 — Por qué la unidad de randomización importa

**El problema:** en este experimento, el cartel se decide una vez por día en
cada sucursal -- todos los visitantes de ese día ven la misma variante. Esto
significa que los visitantes de un mismo día **no son observaciones
independientes entre sí**: comparten el mismo tratamiento, el mismo clima
comercial de ese día puntual, la misma dotación de empleados, etc.

Si se tratara a cada visitante como si fuera una observación completamente
independiente (por ejemplo, corriendo un test de proporciones sobre miles de
visitantes individuales), el test "cree" que tiene muchísima más información
de la que realmente tiene -- porque en el fondo, gran parte de esos miles de
visitantes están repitiendo la misma información de "qué pasó ese día", no
aportando cada uno un dato nuevo e independiente. Esto se llama
**pseudoreplicación**, y hace que el resultado parezca mucho más confiable
(p-valor mucho más chico) de lo que realmente es.

**La regla práctica:** la unidad de análisis tiene que coincidir con la unidad
de randomización. Como el cartel se randomiza por día, el análisis tiene que
comparar días entre sí (una conversión promedio por día), no visitantes entre
sí.

<details>
<summary>❓ Autoevaluación 2.1</summary>

1. ¿Por qué no alcanza con tener miles de visitantes para tener un
   experimento "grande" y confiable?

**Respuesta:** porque lo que importa no es la cantidad total de visitantes,
sino la cantidad de unidades *independientes* de información -- en este caso,
días. Miles de visitantes concentrados en pocos días (por ejemplo, 10 días)
siguen siendo, en el fondo, solo 10 observaciones independientes del efecto
del cartel, porque todos los visitantes de un mismo día comparten el mismo
tratamiento y contexto. Un experimento con muchos visitantes pero pocos días
tiene, en la práctica, poca información real para el test correcto.
</details>

### 2.2 — Bloqueo: neutralizar una fuente conocida de variación

**El problema:** el tráfico de clientes varía según el día de la semana
(lunes y viernes con más movimiento en este dataset, sábado con menos). Si la
asignación de variante fuera completamente al azar sin ningún control, podría
pasar -- por pura mala suerte -- que la variante B quedara asignada más veces
a días de mayor tráfico que la variante A, lo cual generaría una diferencia
observada que en realidad se debe al día, no al cartel.

**La técnica (bloqueo):** en vez de asignar la variante completamente al azar,
se agrupa ("bloquea") por día de la semana, y dentro de cada bloque se
garantiza un balance exacto -- en este proyecto, cada combinación sucursal x
día de la semana tiene exactamente la mitad de sus semanas con cada variante.
Esto elimina el día de la semana como posible explicación alternativa de
cualquier diferencia que se observe.

<details>
<summary>❓ Autoevaluación 2.2</summary>

1. Si NO se hubiera bloqueado por día de la semana, y por azar la variante B
   hubiera caído más veces en lunes (día de mayor tráfico), ¿qué problema
   concreto generaría eso al analizar los resultados?

**Respuesta:** cualquier diferencia observada en conversión o ticket a favor
de B sería ambigua -- no se podría saber si se debe al cartel nuevo o
simplemente a que B tuvo la suerte de coincidir más seguido con el día de
mayor tráfico natural. El bloqueo elimina esa ambigüedad al garantizar que
ambas variantes estuvieron expuestas a la misma mezcla de días de la semana.
</details>

---

## Unidad 3 — Cuánto tiempo hay que correr el experimento

### 3.1 — Tamaño de muestra, MDE y poder estadístico

**La pregunta de diseño:** antes de lanzar un experimento, conviene
preguntarse "¿cuántos días necesito para poder confiar en el resultado?" en
vez de correrlo un tiempo arbitrario y ver qué sale.

Tres ingredientes determinan la respuesta:

- **MDE (efecto mínimo detectable):** el tamaño de diferencia más chico que
  nos interesaría poder detectar. Un MDE más chico (queremos detectar
  diferencias sutiles) requiere más datos.
- **Alpha y poder:** definidos en la Unidad 1 -- cuánta confianza queremos en
  el resultado.
- **Variabilidad de los datos:** si la métrica varía mucho de un día a otro
  "naturalmente" (sin ningún cambio de cartel), va a ser más difícil
  distinguir un efecto real del ruido normal -- hace falta más muestra para
  compensar esa variabilidad.

<details>
<summary>❓ Autoevaluación 3.1</summary>

1. Dos negocios quieren correr un experimento parecido. El Negocio X tiene una
   conversión diaria muy estable (varía poco de un día a otro); el Negocio Y
   tiene una conversión diaria muy volátil. Con el mismo MDE, alpha y poder
   deseados, ¿cuál de los dos va a necesitar correr el experimento más
   tiempo?

**Respuesta:** el Negocio Y (el más volátil). Cuanta más variabilidad natural
tenga la métrica día a día, más difícil es distinguir si una diferencia
observada se debe al tratamiento o es simplemente parte de esa fluctuación
normal -- hace falta más tiempo (más días) para que el promedio de cada grupo
se estabilice lo suficiente como para poder comparar con confianza.
</details>

### 3.2 — Por qué el cálculo cambia según la unidad de análisis

Como se discutió en la Unidad 2, la unidad de análisis correcta acá es el
día, no el visitante. Esto tiene una consecuencia directa en el cálculo de
tamaño de muestra: hay que usar la variabilidad *día a día* (no la
variabilidad entre visitantes individuales) para estimar cuántos días hacen
falta. Usar la fórmula clásica a nivel visitante (como si cada uno fuera
independiente) da un número de "muestra necesaria" mucho menor -- pero
engañoso, por la misma razón de pseudoreplicación de la sección 2.1.

<details>
<summary>❓ Autoevaluación 3.2</summary>

1. En el notebook 02, el cálculo "ingenuo" (a nivel visitante) daba unos
   pocos miles de visitantes necesarios -- que se juntan en pocos días. El
   cálculo correcto (a nivel día) daba varias decenas de días. ¿Cuál de los
   dos number hay que usar para decidir cuánto tiempo correr el experimento
   en la práctica?

**Respuesta:** el cálculo a nivel día, porque es el que coincide con la
unidad real de randomización y con el test que efectivamente se va a usar
para analizar los resultados (Unidad 4). Guiarse por el cálculo a nivel
visitante llevaría a cortar el experimento demasiado pronto, antes de
acumular suficientes días independientes como para confiar en el resultado.
</details>

---

## Unidad 4 — Analizar los resultados

### 4.1 — El t-test: comparar dos promedios

**La idea:** el t-test de dos muestras independientes responde la pregunta
"¿la diferencia entre el promedio del grupo A y el promedio del grupo B es
más grande de lo que esperaríamos ver solo por azar, dado cuánto varían los
datos dentro de cada grupo?". El resultado es un **estadístico t**: mientras
más grande (en valor absoluto), más "sorprendente" es la diferencia observada
si en realidad no hubiera ninguna diferencia real.

En este proyecto se usa un t-test sobre la conversión diaria promedio (una
observación por día x sucursal) y otro sobre el ticket promedio diario --
exactamente la unidad de análisis correcta discutida en la Unidad 2.

<details>
<summary>❓ Autoevaluación 4.1</summary>

1. Si dos grupos tienen la misma diferencia de promedios, pero el Grupo 1
   tiene mucha menos variabilidad interna (los datos están más "apretados"
   alrededor del promedio) que el Grupo 2, ¿en cuál de los dos casos el
   t-test va a dar un resultado más "significativo"?

**Respuesta:** en el caso del Grupo 1 (menos variabilidad interna). El t-test
compara la diferencia observada contra la variabilidad de los datos -- con
menos "ruido" de fondo, la misma diferencia de promedios se destaca más
claramente y es menos probable que sea solo azar. Por eso reducir la
variabilidad de los datos (por ejemplo, con un buen diseño experimental) hace
más fácil detectar un efecto real, sin necesitar más muestra.
</details>

### 4.2 — Qué es (y qué NO es) el p-valor

**Definición intuitiva:** el p-valor responde la pregunta "si en realidad no
hubiera ninguna diferencia real entre A y B (H0 fuera verdadera), ¿qué tan
probable sería observar una diferencia tan grande (o más grande) que la que
efectivamente vimos, solo por azar del muestreo?". Un p-valor chico (por
ejemplo, menor a 0.05) significa que ese resultado sería poco probable si
realmente no hubiera diferencia -- lo cual se interpreta como evidencia en
contra de H0.

**Dos errores de interpretación muy comunes, para evitar:**

- El p-valor **no** es "la probabilidad de que H0 sea verdadera". Es la
  probabilidad de los datos observados (o algo más extremo), *asumiendo* que
  H0 es verdadera -- no al revés.
- Un p-valor chico **no** dice nada directamente sobre el tamaño del efecto.
  Con suficiente muestra, hasta una diferencia diminuta y sin ninguna
  relevancia práctica puede dar un p-valor muy chico (ver Unidad 5).

<details>
<summary>❓ Autoevaluación 4.2</summary>

1. Un colega dice: "el p-valor fue 0.03, así que hay 97% de probabilidad de
   que el cartel nuevo realmente funcione mejor". ¿Es correcta esa
   interpretación?

**Respuesta:** no. El p-valor de 0.03 significa que, *si no hubiera ninguna
diferencia real* (H0 verdadera), habría solo un 3% de probabilidad de observar
una diferencia tan grande como la vista, por puro azar. No es lo mismo que "97%
de probabilidad de que H1 sea cierta" -- esa es una interpretación
probabilística distinta (de tipo bayesiano) que el p-valor, tal como se calcula
en un test clásico, no responde directamente.
</details>

### 4.3 — Intervalo de confianza: una forma más completa de mirar el resultado

**La idea:** además de preguntarse "¿es significativa la diferencia?" (p-valor),
conviene preguntarse "¿de qué tamaño es la diferencia, y con qué margen de
incertidumbre?". El intervalo de confianza del 95% da un rango de valores
plausibles para la diferencia real entre A y B, dado lo que se observó en los
datos.

Si el intervalo completo queda por encima de cero (por ejemplo, "entre +2.7 y
+5.5 puntos porcentuales"), es consistente con una diferencia significativa y
además te dice algo que el p-valor solo no dice: **cuán grande podría ser esa
diferencia en la práctica** -- información directamente útil para decidir si
vale la pena el cambio.

<details>
<summary>❓ Autoevaluación 4.3</summary>

1. ¿Por qué el intervalo de confianza da más información para tomar una
   decisión de negocio que el p-valor solo?

**Respuesta:** porque el p-valor solo dice "sí" o "no" es significativo, sin
decir nada sobre el tamaño del efecto. El intervalo de confianza, en cambio,
muestra un rango plausible de cuán grande es la diferencia real -- lo cual
permite evaluar si ese tamaño de efecto (incluso en el escenario más
conservador del intervalo) es lo suficientemente grande como para justificar
el cambio en la práctica.
</details>

---

## Unidad 5 — De la estadística a la decisión de negocio

### 5.1 — Significancia estadística vs. significancia práctica

**El problema:** con una muestra lo suficientemente grande, casi cualquier
diferencia por más chica que sea termina siendo "estadísticamente
significativa" (p < 0.05) -- porque el p-valor depende tanto del tamaño del
efecto como de la cantidad de datos. Una diferencia real de 0.1 puntos
porcentuales de conversión puede ser estadísticamente significativa con
suficiente muestra, pero no cambiar en nada las decisiones del negocio.

**La solución práctica:** además de mirar el p-valor, hay que traducir el
efecto medido a una magnitud de negocio concreta -- en este proyecto, un
ingreso incremental estimado. Un resultado solo es realmente accionable
cuando es significativo estadísticamente **y** grande en magnitud de negocio.

<details>
<summary>❓ Autoevaluación 5.1</summary>

1. Un experimento con millones de usuarios encuentra que una variante mejora
   la conversión en un 0.001% (estadísticamente significativo, p < 0.001).
   ¿Alcanza esa información sola para recomendar implementar el cambio?

**Respuesta:** no necesariamente. Hace falta traducir ese 0.001% a un impacto
de negocio concreto (por ejemplo, cuánto ingreso incremental representa) y
compararlo contra el costo de implementar y mantener el cambio. Un efecto
estadísticamente significativo pero de magnitud despreciable puede no
justificar el esfuerzo -- la significancia estadística es una condición
necesaria pero no suficiente para tomar una decisión de negocio.
</details>

### 5.2 — Una advertencia: mirar los resultados antes de tiempo ("peeking")

**El problema:** una tentación común es ir revisando los resultados del
experimento todos los días mientras corre, y cortarlo apenas se ve un p-valor
menor a 0.05 -- pensando "ya llegamos a la significancia, no hace falta
seguir". Esto es un error: el cálculo del p-valor asume que la cantidad de
datos y el momento del análisis se definieron de antemano. Mirar los
resultados muchas veces y frenar en el primer momento "favorable" aumenta,
sin que se note, la probabilidad real de terminar con un falso positivo muy
por encima del 5% que se había fijado como alpha.

**La recomendación simple:** definir de antemano (con el cálculo de tamaño de
muestra de la Unidad 3) cuántos días va a durar el experimento, y analizar los
resultados una sola vez, al final de ese período -- no ir "espiando" y
decidiendo sobre la marcha. (Existen técnicas estadísticas específicas para
poder mirar los resultados varias veces de forma válida -- testing secuencial
-- pero quedan fuera del alcance de este proyecto.)

<details>
<summary>❓ Autoevaluación 5.2</summary>

1. ¿Por qué revisar el experimento todos los días y cortarlo apenas se ve un
   p-valor significativo aumenta el riesgo de falso positivo, aunque cada
   revisión individual use alpha = 0.05?

**Respuesta:** porque cada revisión es una nueva oportunidad de que el ruido
del muestreo cruce por casualidad el umbral de significancia -- y con muchas
oportunidades, la probabilidad de que eso pase *en algún momento*, aunque no
haya ningún efecto real, es mucho mayor al 5% fijado para una sola revisión.
Es parecido a tirar una moneda muchas veces buscando una racha "significativa"
por azar: cuantas más veces se mira, más probable es encontrar una racha así,
sin que eso signifique que la moneda está cargada.
</details>
