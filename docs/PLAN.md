# Plan de entrega · 3 al 8 de noviembre de 2026

**Cierre interno: domingo 8 a las 18:00, hora de Paraguay.** El entregable decisivo es una demo en vivo de una puerta y un recorrido. Una persona debe poder iniciar el sistema, ver una subida y una bajada en video y explicar cómo cambió la ocupación. La defensa vale 50 puntos, el desarrollo 30 y el informe 20.

## Dos personas, dos entregas que encajan

- **Álvaro · main.** Implementa FastAPI, el panel Streamlit, la capacidad configurable, la ocupación por parada y el arranque con Docker. Redacta contexto y arquitectura. Revisa los PR de visión y conserva una versión ejecutable en main.
- **Compañero · vision.** Selecciona y documenta los clips, prepara anotaciones, ajusta un detector de personas y conecta ByteTrack con una línea de conteo. Entrega pesos o instrucciones reproducibles para obtenerlos, métricas, ejemplos de errores y las secciones de metodología y resultados.
- **Ambos.** Hoy cuentan a mano un clip y acuerdan qué constituye un cruce. Cada tarde prueban el mismo clip durante 15 minutos. El compañero abre PR pequeños, Álvaro integra tras reproducir el resultado y el compañero incorpora main a vision antes del siguiente cambio. Ambos preparan preguntas y ensayan.
- **Claude.** Álvaro puede darle el contrato y pedir casos de prueba para la API mientras su compañero desarrolla visión. El compañero puede pedirle que revise el evaluador buscando dobles conteos o mezcla de clips entre particiones. Cada autor ejecuta y valida las sugerencias en su propia rama. Las cifras del informe salen del evaluador.

## Contrato del martes

Álvaro entrega al módulo de visión la ruta a un clip, los extremos de la línea y qué lado corresponde al interior. Visión entrega eventos en orden con `tiempo_s`, `track_id` y `sentido` (`subida` o `bajada`), más el video anotado para la demo. Ejemplo de evento: `{"tiempo_s":4.2,"track_id":7,"sentido":"subida"}`. Un cruce confirmado genera un solo evento aunque la persona permanezca sobre la línea. Una persona que vuelve a cruzar en sentido contrario genera un evento nuevo.

Álvaro asigna cada evento a una parada según los intervalos del recorrido simulado. El panel muestra pasajeros actuales = carga inicial + subidas − bajadas, y ocupación (%) = 100 × pasajeros actuales / capacidad. Para probar la integración, usen capacidad 20 y carga inicial 3: tras dos subidas y una bajada deben quedar 4 pasajeros (20 %). Si la cuenta queda negativa, registren la inconsistencia para revisar el conteo.

## Calendario y prueba de cierre de cada día

| Día | Álvaro en main | Compañero en vision | Qué deben poder comprobar juntos |
|---|---|---|---|
| Mar 3 | Fijar contrato, preparar ejemplo y boceto del panel. | Conseguir clips utilizables, documentar origen, elegir línea y contar un clip a mano. | Ambos reproducen el mismo clip e identifican los mismos cruces. Si falta material de bus, grabar un ensayo local con voluntarios y documentar que simula la puerta. |
| Mié 4 | Conectar API y panel con eventos de ejemplo. | Ejecutar detector preentrenado + ByteTrack en un clip. Separar clips completos en entrenamiento, validación y prueba. Anotar cajas y eventos. | El panel pasa el ejemplo de 4 pasajeros y visión entrega su primer archivo de eventos reales. |
| Jue 5 | Integrar visión con la API y actualizar el panel durante la reproducción. | Ajustar el detector con las cajas de entrenamiento, elegir configuración en validación y guardar pesos y parámetros. | Desde la interfaz, procesar un clip y explicar una subida y una bajada observando video y contador. |
| Vie 6 | Graficar carga por parada y arrancar API/UI con Docker Compose. | Comparar modelo base y ajustado en clips reservados. Guardar errores por sentido, tiempos y un caso de oclusión. | Congelar la versión de la demo y su dataset. Si el ajuste rinde peor, mostrar la mejor versión según validación y reportar ambas mediciones. |
| Sáb 7 | Preparar guion, contexto y arquitectura del informe. | Incorporar método, métricas, figura, limitaciones y referencias verificadas. | PDF IEEE de exactamente 3 páginas, abstract ≤150 palabras y primer ensayo de 10 minutos en la máquina de defensa. |
| Dom 8 | Probar arranque desde un clon limpio. Preparar clips, pesos y copia de respaldo local. | Repetir evaluación según el README, verificar cifras del PDF y preparar respuestas. | Segundo ensayo con 2 minutos de preguntas. Antes de las 18:00, verificar desde main el PDF, la demo en vivo y los pasos reproducibles. |

## Evidencia mínima de evaluación

Conserven el identificador de cada clip, origen, si es real o simulado, parada, duración y partición. Mantengan todos los fragmentos de una misma grabación en la misma partición. Reserven ejemplos con cruces individuales y simultáneos. Para la prueba, anoten manualmente segundo y sentido del cruce. Emparejen cada predicción con un único evento manual del mismo sentido dentro de una tolerancia acordada antes de evaluar (propuesta: ±1 s). Reporten F1 por sentido, error absoluto medio de conteo por clip y cuadros procesados por segundo en la máquina de defensa. Comparen esos FPS con los del video antes de afirmar que funciona en tiempo real.

## Guion de defensa

Álvaro presenta el problema y la arquitectura (2 min). Su compañero muestra el seguimiento y explica un caso de oclusión (3 min). Álvaro ejecuta la demo y muestra cómo dos paradas alteran la ocupación (3 min). Su compañero compara el resultado con el conteo manual y expone una limitación (2 min). Dejen los clips y los pesos disponibles sin internet, y el video del ensayo como respaldo.
