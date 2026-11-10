# Propuesta de evaluación con PCDS

Para el compañero de visión. Es una propuesta: no bloquea la tarea 08 ni se implementó.

## Por qué PCDS

El clip de oficina es la única grabación del proyecto, se usó para calibrar el rastreador y ajustar el detector, y no sirve para métricas del informe (`data/README.md`). [PCDS](https://github.com/shijieS/people-counting-dataset) (commit `be8913477e9eb89a9280cadfe044cfa2327d1fc9`) tiene videos de puertas de bus reales con la cámara arriba de la entrada.

Según su README, que no verificamos:
- Tiene 5.464 pares de videos de profundidad y color, de 30 escenas nombradas `BUS_FECHA_[front|back]`.
- Cada escena trae un `label.txt` con entradas y salidas por video y un tipo de iluminación y multitud: `N-C-`, `N-C+`, `N+C-` y `N+C+`.
- Licencia CC BY-NC-SA 3.0. Hay que citar a Sun et al., *IEEE T-ITS*, 2019.

## Estado de la descarga

Se intentó el 7 nov., a las 23:20 UTC, desde los entornos de Claude. **Bloqueado:** Baidu Pan no responde, por la lista de sitios permitidos, y el enlace de Google Drive fue dado de baja por los autores. Habría que intentarlo desde una máquina propia; Baidu Pan suele pedir cuenta y cliente para archivos grandes. Si no se consigue en 30 minutos, conviene pasar a la alternativa.

## Cómo usarlo

1. **Muestra pequeña y trazable.** Solo videos **color**: los autores advierten que color y profundidad no están sincronizados, y nuestro pipeline usa color. Registrar escena, archivo, tipo, entradas y salidas de `label.txt`, licencia y SHA-256 de cada video, en `data/README.md`, en una sección nueva.
2. **Partición por escena o sesión, no por cuadro.**
   - Asignar escenas completas a validación o a prueba. Nunca repartir cuadros vecinos, ni videos de la misma escena, entre conjuntos.
   - Si se usa algo para elegir umbrales o línea, va a validación; la prueba se mira una sola vez.
   - Los metadatos no alcanzan para demostrar que dos escenas sean de lugares o días independientes. Con nombres como `25_20160411_front` y `25_20160411_back`, tratar el mismo bus y la misma fecha como un solo grupo.
3. **Configurar la escena.** La cámara tiene inclinación, no es cenital pura. Hay que definir el recorte, la línea y el interior por escena, en validación, y guardarlos como el `.config.json` actual.
4. **Métricas posibles con lo que trae PCDS.**
   - **Por clip:** error absoluto de subidas y de bajadas **por separado**, y su media por tipo de escena (`N±C±`).
   - **No usar solo el saldo neto:** una subida extra y una bajada omitida se cancelan y ocultan dos errores.
   - **No se puede sin anotar más:** aciertos y omisiones por cruce dentro de ±1 s, F1 por sentido o error temporal. Las etiquetas son totales por video. Para eso habría que anotar los tiempos de cruce de un subconjunto con `evaluation/evaluate.py`.
5. **Qué comparar.** El detector base contra el ajustado; y un detector de cabezas solo si existe con licencia clara. En los dos casos, con la configuración elegida en validación.
6. **Alcance de las conclusiones.** Una muestra chica de pocas escenas no demuestra que el sistema generalice. Hay que informar el número de escenas y videos, y los tipos de escena cubiertos.

## Alternativa si PCDS no se consigue

Grabar una sesión nueva e independiente. Por ejemplo, la puerta de un aula o de una casa, con cámara fija desde arriba, varias personas, algún cruce simultáneo y sin usarla para calibrar. Anotar a mano los tiempos de cruce con otra persona revisando, y documentarla en `data/README.md` con el mismo formato. Esto sí permite las métricas por cruce del evaluador actual.
