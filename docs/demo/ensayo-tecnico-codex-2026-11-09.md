# Ensayo técnico de Codex · 9 de noviembre de 2026

## Alcance

Recorrido real del panel en el navegador, sobre `cierre-final`, commit `8ffa96c`. Realizado por Codex, no por los expositores. Horario de Asunción (UTC−3), aproximadamente 01:33:00–01:35:30. No incluye discurso oral, lectura en voz alta ni preguntas; no certifica la duración de la defensa de 10 + 2 minutos.

No se modificó código, modelo, geometría de referencia ni evaluaciones originales. No se hizo commit, push o merge.

## Preparación

- Docker Compose no tenía servicios activos del proyecto.
- API iniciada con `VISION_DISPOSITIVO=cuda:0`, Python de `IA/venv-gpu`, en `127.0.0.1:8000`.
- Panel iniciado con `.venv`, en `127.0.0.1:8501`.
- CUDA disponible: NVIDIA GeForce RTX 2050.
- Hash del video y de `yolo11n.pt` comprobados y coincidentes con los registros.
- Plan de energía observado: **Equilibrado**, no máximo rendimiento. No se modificó. La conexión a corriente no pudo verificarse mediante CIM por permisos.
- PDF y guion no se expusieron oralmente; su presentación queda pendiente del equipo.

## Tiempos observados

Son tiempos de operación mediante herramientas, con sus pausas de observación; no representan velocidad de interacción humana ni duración del discurso.

- Selección y revisión del recorrido de ocho paradas: **10,6 s**. Se verificaron las ocho cargas, incluido 105 % en la parada 4 y 0 % al final. El selector respondió a una flecha; la tecla Home no lo llevó al inicio en este navegador.
- Subida y preparación del video hasta el clic de reprocesamiento: **52,0 s**. Incluye cargar el archivo, completar línea, capacidad, carga inicial y ritmo real, y verificar los parámetros. Una coordenada tuvo que ingresarse nuevamente tras la actualización del panel; antes de procesar se confirmó la geometría exacta.
- Clic en «Reprocesar en vivo para demostración»: **01:34:07,682**.
- Aceptación registrada en `entrada.json`: **01:34:08,064**.
- Conteo del video: **27,455 s**, según la configuración generada. El archivo de predicción quedó escrito a las **01:34:44,846**; desde la aceptación hasta ese momento transcurrieron unos **36,8 s**, incluyendo arranque/precalentamiento.
- Estado final completo: **01:35:07,039**, unos **59,0 s desde la aceptación**. La conversión/publicación posterior al conteo insumió aproximadamente **22,2 s**, calculados con las marcas de escritura de archivos.
- Resultado final observado en el navegador: **61,3 s desde el clic**. Es el instante de observación, no una medición exacta del primer render.
- Recorrido técnico total, incluyendo descarga y comprobación del bloqueo de repetición: **150,4 s (2 min 30 s)**.

La preparación y espera del video sumaron aproximadamente **1 min 53 s**. No es el tiempo completo de explicar y mostrar la demo; el bloque previsto de 3 min 30 s debe ensayarse oralmente.

## Ejecución y evidencia

Ejecución nueva: `runs/panel/20261109-013408-063084/`, marcada como **repetición para demostración**.

- Video: `prueba-bus.mp4`, 686 cuadros, 27,44 s, 768×432, 25 FPS.
- Recorte: `0,0,768,432`.
- Línea: `274,431 → 467,242`; interior arriba.
- Capacidad: 30; carga inicial: 20; ritmo real activado.
- Dispositivo registrado: `cuda:0`.
- Procesados: **682 cuadros**, **4 descartados**, **24,84 FPS**.
- Latencia interna: media **22,6 ms**, p95 **26,9 ms**, máxima **218 ms**; primer décimo **27,4 ms**, último **21,6 ms**. No hay crecimiento entre esos segmentos.
- Actualización observada durante el proceso: a los 13,6 s del video, 10 bajadas y 33,33 % de ocupación; a los 24,3 s, 8 subidas, 17 bajadas y 36,67 %.
- Resultado: **25 eventos (8 subidas y 17 bajadas)**, carga final 11 y ocupación 36,67 %.
- Comparación de desarrollo con la referencia: **12 TP, 13 FP, 0 FN; F1 0,6486**.

**Esta repetición no reprodujo los 24 eventos históricos: añadió una bajada falsa.** No se investigó la causa en este ensayo ni se atribuye automáticamente a los cuadros descartados. No prometer igualdad de conteo entre repeticiones. Las métricas de la primera evaluación siguen siendo históricas, no las de esta ejecución.

Archivos locales de evidencia: `entrada.json`, `prediccion.config.json`, `progreso.json`, `prediccion.json`, `estado.json` y `anotado.webm` dentro de la ejecución. No versionar el video.

## Comprobaciones funcionales

- [x] Subida desde el navegador y vista previa.
- [x] Parámetros verificados antes de ejecutar.
- [x] Progreso y ocupación actualizados durante la ejecución.
- [x] Resultado nuevo identificado como «Resultado procesado en vivo».
- [x] Video final cargado en el navegador, `readyState=4`, sin error de medios; duración 27,28 s. No se revisó la reproducción completa.
- [x] Descarga real de eventos a `Downloads/20261109-013408-063084-eventos.json`.
- [x] «Procesar video» posterior mostró el aviso «No se repite»; no inició otra inferencia.
- [x] Hashes de todos los archivos existentes de la primera evaluación `20261108-200805-374934` iguales antes y después.
- [ ] Recargar durante el procesamiento y cancelar: no repetidos en este ensayo; existen pruebas anteriores, no se marcan aquí como realizados.
- [ ] Descarga del video y configuración: controles visibles, no pulsados en este ensayo.

## Observaciones para la presentación

1. Durante la inferencia, el resultado anterior sigue visible más abajo. Señalar el bloque «Procesando en vivo» y su ID para no confundirlo con el respaldo.
2. Al terminar el conteo, la página permaneció cerca del 99 % mientras convertía el video. Reservar aproximadamente 20–30 s adicionales, sin prometer ese tiempo como constante.
3. El aviso «No se repite» citó una ejecución anterior (`20261109-004143-611081`), mientras el selector conservó la recién ejecutada. Leer el ID seleccionado antes de explicar cifras.
4. Los 25 eventos de esta repetición son distintos de los 24 históricos. Presentar cada resultado con su ejecución correspondiente.
5. La disponibilidad limitada de videos de cámaras de buses, no solo de Paraguay, motivó el uso de oficina y trenes. El ensayo no resuelve las limitaciones de generalización ni de oclusiones.

## Pendiente del equipo

Cronometrar problema/objetivo, arquitectura, explicación de resultados, conclusiones y preguntas. No se completó ni firmó la confirmación del equipo del checklist. La prueba técnica no sustituye ese ensayo oral.

## Aclaración posterior (Claude, 9 nov., 01:40): 25 frente a 24 eventos

Se compararon los eventos de esta ejecución con los de otras ejecuciones, sin volver a procesar nada:

| Ejecución | Eventos | TP/FP/FN |
|---|---|---|
| Este ensayo (GPU, ritmo real, 682 de 686 cuadros) | 25 | 12/13/0 |
| `20261109-005405-323754` (GPU, ritmo real) | 25 | 12/13/0 |
| `runs/diagnostico-gpu/b-todos-sin-video` (GPU, **los 686 cuadros**) | 25 | 12/13/0 |
| `20261108-200805-374934` (CPU de Windows, primera evaluación) | 24 | 12/12/0 |

- **Coincidencia:** los 25 eventos del ensayo son idénticos, en instante y sentido, a los de la GPU procesando todos los cuadros.
- **Lo que queda descartado:** la bajada adicional **no se debe a los 4 cuadros descartados ni a una variación entre repeticiones**. En GPU, el resultado se repitió igual en las tres ejecuciones.
- **Lo que no se identificó:** la diferencia está entre el resultado en GPU y la primera evaluación en CPU. Ya estaba registrado que el sistema varía según la plataforma (tarea 10, Kaggle). No se identificó el mecanismo exacto de esta bajada.
- **Para la presentación:** en GPU se esperan 25 eventos; las métricas históricas, con 24, son las de la evaluación ciega en CPU. Hay que presentar cada resultado con su ejecución.
- **Energía:** este registro observó el plan de energía en «Equilibrado», no en máximo rendimiento. Aun así, el ensayo alcanzó 24,84 FPS con 4 cuadros descartados.
