# Relevo para Claude · 5 de noviembre de 2026

> **Aclaración (9 nov., cierre final):** este resumen describe etapas anteriores. El estado vigente está en [la matriz de requisitos](docs/relevo/2026-11-08-claude-cierre-final/matriz.md) y en [el cierre final](docs/relevo/2026-11-08-claude-cierre-final/README.md).

## Estado de entrega · 8 de noviembre (noche)

- **Versión cerrada:** API y panel con «Video nuevo»; conteo `yolo11n` calibrado, sin filtros.
- **Demo principal:** `prueba-bus` desde la página. Detecta los 12 cruces, pero registra 24 eventos. Según la inspección de cada uno de los 12 falsos, 8 son cajas encimadas o de grupo y el resto, saltos de ID u oscilaciones. La página separa «resultado guardado» de «reprocesar en vivo para demostración».
- **Oficina:** caso documentado de bajada omitida, una limitación confirmada.
- **Tests (Windows):** 129 aprobados, **1 fallido** (oficina), **1 omitido** (pesos ajustados ausentes) y **1 xfail** (cajas encimadas).

Arranque y guion: [cierre](docs/relevo/2026-11-08-claude-cierre/README.md). Sin commit.

## Tareas 13 y 14

- **Validación a ciegas con `prueba-bus`** (referencia de Álvaro): 12 de 12 cruces detectados, pero 24 eventos (12 FP). La inspección de los 12 falsos encontró sobre todo cajas encimadas (8), además de saltos de ID y una oscilación.
- **Filtro de cajas encimadas:** probado y descartado, porque borraba cruces reales. La entrega mantiene el conteo de siempre.
- **Página:** el modo «Video nuevo» funciona.
- **Arranque y guion de demo:** en la [devolución de la tarea 14](docs/relevo/2026-11-08-claude-tarea14/README.md). Sin commit.

## Tarea anterior · 8 de noviembre (noche) · Tarea 13

El panel suma el modo **«Video nuevo»**:
- subir un video (hasta 200 MB y 5 min);
- fijar recorte, línea e interior con vista previa sin inferencia;
- procesar con la configuración de la API (`yolo11n` calibrado);
- ver el resultado y descargar el JSON, el video anotado y la configuración.

La demo de oficina y la carga de JSON siguen igual. Hay 10 tests nuevos de endpoints, y la verificación en el navegador dio eventos idénticos al pipeline en PAMELA A. Falta probar el arranque en Windows y hacer la validación con el video nuevo de Álvaro. [Devolución](docs/relevo/2026-11-08-claude-tarea13/README.md).

## Tarea anterior · 8 de noviembre · Tareas 11 y 12

- **Tarea 11:**
  - **Selección** en Kaggle y PAMELA A: `yolo11l` calibrado sumó 21 errores, contra 28 de la API.
  - **Prueba final** en `youtube-bus-real`, con referencia de Álvaro de 18 cruces: `yolo11n` tuvo 13 errores, con 6 de 18 cruces y 66 FPS, y `yolo11l` 18 errores, con 12 de 18 y 24 FPS.
  - **La API no cambia.** El video quedó consumido. [Devolución](docs/relevo/2026-11-08-claude-tarea11/README.md).
- **Tarea 12:** resultado exploratorio, con referencias de Claude sin revisión humana.
  - **El filtro no se justifica.** Un filtro temporal de duplicados por sentido no mejora sin borrar cruces reales. Los falsos de Kaggle y PAMELA son sobre todo oscilaciones de un mismo ID, y en PAMELA dominan las omisiones.
  - **Corregido:** el anotador (navegación, protección de la referencia final) y el arnés (no sobrescribe resultados).
  - **Preparado:** el protocolo para una grabación nueva y el manifiesto de qué versionar.
  - **Pendientes de Álvaro:** aclarar los 18 cruces contra 16 del contador, revisar las referencias, conseguir un video nuevo y aprobar el manifiesto. [Devolución](docs/relevo/2026-11-08-claude-tarea12/README.md).

## Tarea anterior · 8 de noviembre · Tarea 10 *(histórico: «YouTube reservado» ya no rige)*

Ajuste del detector reproducido en Windows, entrenado solo con oficina: 19,5 min, SHA-256 `69958946…`, pesos fuera de Git. En oficina, su material de entrenamiento, cuenta 19 o 20 de 20. Pero **no se transfiere**:

- en Kaggle no produce ningún evento (0 de 6 subidas); sin rastreador, ningún cuadro supera 0,05 de confianza;
- en PAMELA A cuenta 0 o 1 de 28 bajadas.

El base calibrado de la API sigue igual: Kaggle con subidas 5/5/1 y bajadas 0/3/0, y PAMELA con bajadas 10/0/18. **No hay evidencia para cambiar de modelo.** Hace falta entrenar con varias escenas y evaluar en otras. En Kaggle, el base dio eventos algo distintos entre Linux y Windows. Las referencias de Kaggle y PAMELA siguen pendientes de revisión humana, y los videos de YouTube siguen reservados. [Devolución](docs/relevo/2026-11-08-claude-tarea10/README.md).

## Tarea anterior · 7 de noviembre · Tarea 09

[Tarea 09 · Comparar modelos en Windows](docs/tareas/claude/09-evaluacion-windows.md), en `integracion-video`, sin commit.

- **Comparación reproducible:** `docs/relevo/2026-11-07-claude-tarea09/scripts/evaluar_oficina.py` reúne los TP, FP y FN por sentido, los hashes y los FPS, sin tocar `evaluation/results`.
- **Linux x86:** en el video completo, el modelo base calibrado da subidas 7/0/3 y bajadas 4/0/6 (TP/FP/FN), y el base por defecto no cuenta ningún cruce.
- **Windows (Ryzen 5 7535HS):** da los mismos eventos que Linux; solo macOS difiere. Los pesos ajustados del compañero no están en esta máquina.
- **Video de oficina:** no es una evaluación independiente; se revisó su referencia y falta la revisión humana.
- **Preparado:** la ficha para una grabación nueva y un mensaje para el compañero.
- **Primera prueba independiente** (video de Kaggle, prerregistrada, 6 subidas anotadas por Claude): el base calibrado da subidas 5/4/1 y bajadas 0/4/0 (TP/FP/FN). Inventa tantos eventos como acierta en una escena concurrida. Ver `docs/relevo/2026-11-07-claude-tarea09/prueba-kaggle/resultados.md`.
- **Segunda prueba independiente** (PAMELA-UANDES, muestra A, 28 bajadas anotadas por Claude): el base calibrado da bajadas 10/0/18. En escenas nuevas omite muchos cruces o inventa eventos según la escena. Ya se pidió la referencia oficial del dataset.
- **Sin cambios:** la configuración de la API, que todavía no tiene base para cambiarse.

[Devolución](docs/relevo/2026-11-07-claude-tarea09/README.md).

## Tarea anterior · 7 de noviembre · Tarea 08

[Tarea 08 · Cierre de integración en Windows](docs/tareas/claude/08-cierre-integracion-windows.md), en `integracion-video`, con cambios sin commit para revisión. En Linux quedó verificado lo siguiente:

- El panel permite consultar el tramo completo de un clip procesado: 0, 2,16, 4 y 6 s dan 0, 1, 1 y 1 pasajeros.
- La API solo publica ejecuciones terminadas y legibles; las fallidas y cortadas conservan su registro.
- Los 45 estados del gráfico siguen sin fallos.

La verificación en Windows se hace con `docs/relevo/2026-11-07-claude-tarea08/verificar-windows.ps1`. La bajada omitida sigue como limitación del modelo, y el pedido a visión está preparado. La comparación de repositorios externos (experimento, sin cambios en el detector) está en `docs/casos-deteccion/comparacion-repositorios/`. [Devolución](docs/relevo/2026-11-07-claude-tarea08/README.md).

## Tarea anterior · 6 de noviembre

Álvaro pospuso todo el trabajo del informe hasta el cierre del proyecto. La prioridad siguiente es la [tarea 07 · Conectar el video con el conteo automático](docs/tareas/claude/07-demo-video.md). Las menciones anteriores a figuras y PDF son históricas.

Acuerdo con Álvaro: hasta completar el proyecto, cada revisión de Codex termina con la próxima tarea para Claude y un mensaje listo para copiar. Al cerrar la última revisión, indicar que el proyecto está completo.

Verificación técnica final de las tareas 05–06 en Windows: se reconstruyeron ambos servicios con Docker Desktop y pasaron las siete pruebas de la API. En Chromium el gráfico coincidió con tabla e indicadores en los 45 estados, incluidas las 32 transiciones de la predicción. A los 2,16 s la barra y su rótulo muestran 5 %. [Resultados de Windows](docs/relevo/2026-11-06-claude-tarea06/windows/resultado.json).

### Verificado el 7 de noviembre · Tarea 07

Esto es en la rama local `integracion-video`: `d0a658a` más `origin/vision` en `dd5a19a` (merge `e85fb75`), con la integración en `d2cf58d` y el caso de detección en `b511d91`, sin push.

El panel procesa el clip de oficina (0–6 s) mediante `POST /procesamientos`, muestra el video anotado y separa la predicción automática de la referencia manual. Con los eventos de esa ejecución calcula la ocupación.

En Linux x86 el detector base predijo la subida a 2,16 s pero **omitió la bajada**: la persona cruza sin caja entre 4,44 y 4,80 s. La ocupación queda en 0 → 1 pasajero (5 %) y no vuelve a 0. El código de `vision` sin cambios da lo mismo, y su prueba del ensayo falla acá. La carga de JSON y los 45 estados del gráfico pasan sin fallos. En Windows, Álvaro observó lo mismo desde el panel: subida contada, bajada sin detectar. **Pendiente:** guardar la salida del script en Windows. [Evidencias](docs/relevo/2026-11-07-claude-tarea07/README.md) y [análisis del caso](docs/casos-deteccion/oficina-bajada-omitida/README.md).

### Verificado el 6 de noviembre · Tarea 06

La figura 2 del informe se reemplazó con una captura del gráfico corregido: demo a 10 s, capacidad 20 y carga 3, con barras de 25 % y 20 %, nombres de parada y la línea del 100 %. Para que se lea a ancho de columna, `ui/app.py` agranda la letra del gráfico a 15 px y reduce el área de datos. Con eso, el texto mide unos 6 pt en el PDF, antes unos 4 pt. `informe-borrador.pdf` sigue en 3 páginas, sin desbordes y con un resumen de 138 palabras. Con este código, en Linux pasan los 45 estados de `verificar_grafico.py` sin fallos, con 32 transiciones, y pasan las 7 pruebas. **Windows sigue pendiente:** Álvaro debe reconstruir Docker y ejecutar el verificador con el bloque de PowerShell del relevo. [Evidencias](docs/relevo/2026-11-06-claude-tarea06/README.md).

### Verificado el 6 de noviembre · Tarea 05

Se corrigió el gráfico que conservaba valores anteriores. `ui/app.py` ahora dibuja la misma especificación de Altair como SVG en el servidor, con `vl-convert-python==1.8.0`, agregado a `requirements.txt`. Lo inserta en la página con las mismas filas que la tabla. En Linux con Docker, en una sesión de Chromium, 32 transiciones del recorrido predicho más 13 estados adicionales dieron barra y rótulo dibujados iguales a la tabla. Los estados adicionales incluyen demo, cambio de capacidad, alternancia de archivos, nombres repetidos, 150 % y −5 %. La prueba falla si se altera el rótulo, el render funciona sin red y pasan las 7 pruebas. Falta reconstruir y verificar en Windows, y actualizar la Fig. 2 del informe, porque cambiaron los colores. [Evidencias](docs/relevo/2026-11-06-claude-tarea05/README.md).

### Verificado el 6 de noviembre · Tarea 02

Ensayo de integración del detector base `yolo11n.pt` con ByteTrack calibrado, desde `origin/vision` en `dd5a19a`. La predicción tiene una subida a 2,16 s (+0,16 s respecto de la referencia manual de 2 s) y una bajada a 4,60 s (+0,60 s respecto de 4 s), ambas dentro de ±1 s, sin eventos extra ni omitidos. `POST /ocupacion` en Docker sobre Windows respondió 200: 1 subida, 1 bajada, 0 pasajeros, 0 % y sin avisos. En el panel, indicadores y tabla dieron 0, 1 y 0 pasajeros (0, 5 y 0 %) a 0, 2,16 y 4,60 s.

**El gráfico no coincidió:** a 2,16 s y 4 s mostró 0 % con indicadores y tabla en 5 %. El defecto se reprodujo en Linux: el gráfico de Streamlit a veces conserva valores anteriores al mover el selector. La verificación de la tarea 03 solo había comprobado que el gráfico estuviera presente. No se cambió el código; falta decidir la corrección. Quedan pendientes la revisión visual del video, la reproducción local de la inferencia y la evaluación en grabaciones independientes. [Evidencias](docs/relevo/2026-11-06-claude-tarea02/README.md).

## Estado histórico · 5 de noviembre

La [tarea 04, informe IEEE y guion](docs/tareas/claude/04-informe-demo.md) está entregada sin commit, a la espera de la revisión de Álvaro y de las mediciones de visión. La [tarea 03](docs/tareas/claude/03-panel-docker.md) está completada y revisada, también sin commit. La tarea 01 está completada y la tarea 02 sigue pendiente de los eventos de visión. Ya existe la referencia manual aproximada del clip de oficina en `docs/demo/oficina-00-06-manual.json`.

Revisión del 5 de noviembre de la tarea 03: siete pruebas de API aprobadas y 11 registros del panel Docker en Windows idénticos a Linux. Capturas y valores guardados en `docs/relevo/2026-11-05-claude-tarea03/revision-windows/`. La entrega queda revisada, con los cambios sin commit.

Álvaro trabaja en `main` y su compañero en `vision`. El cierre interno es el domingo 8 a las 18:00 (Paraguay). Lean [la consigna](contexto.md), [el plan](docs/PLAN.md) y [el arranque en Windows](README.md). La prioridad es integrar el primer clip el jueves 5.

## Punto de partida

- `api/main.py` expone `POST /ocupacion`. Recibe capacidad, carga inicial, paradas y eventos. Devuelve filas con subidas, bajadas, pasajeros y porcentaje, además de avisos si el conteo resulta negativo. El cálculo es independiente para cada solicitud.
- `docs/demo/recorrido.json` es un ejemplo sintético editable. Cada evento tiene segundo, ID de seguimiento y sentido. Los eventos llegan ordenados y pueden compartir segundo. Un cruce justo al comenzar una parada pertenece a esa parada.
- `ui/app.py` consulta la API por HTTP. Se puede cambiar la capacidad, la carga inicial y el segundo del recorrido. El panel representa los cruces ocurridos hasta ese instante. Falta la integración con video, el modelo y la evaluación. El arranque con Docker y el borrador del informe se agregaron después.

Verificación realizada: con la API corriendo y el panel de Streamlit consultándola por HTTP, se movió el selector a los segundos 0, 5 y 10. Se observaron 3, 5 y 4 pasajeros respectivamente (15 %, 25 % y 20 %). La bajada quedó en la segunda parada.

## Primera tarea para Claude

Prepará pruebas de contrato para la API en `tests/test_ocupacion.py`. Usá el JSON de ejemplo como punto de partida y verificá los resultados contra cálculos manuales. Trabajá con Álvaro en su copia actualizada de main y dejá la rama vision al compañero.

1. Con carga 3 y capacidad 20, exigir 5 pasajeros al final de la primera parada y 4 (20 %) al final de la segunda. La bajada del segundo 10 debe aparecer en la segunda.
2. Probar dos cruces simultáneos de personas distintas y una parada sin cruces. Ambos eventos cuentan y la parada vacía conserva la carga.
3. Probar una bajada con el bus vacío: verificar que queda registrada la inconsistencia incluso si una subida posterior recupera la carga.
4. Comprobar que la API responde HTTP 422 a capacidad cero, sentido desconocido, eventos desordenados o inicios de parada repetidos.

Entregá el comando para ejecutar las pruebas y su resultado. Si una prueba descubre un defecto, indicá la entrada, el valor esperado y el obtenido. Después de integrar un cambio, actualizá este resumen con lo verificado y la próxima tarea.

## Verificado el 4 de noviembre

`tests/test_ocupacion.py` cubre los cuatro puntos de la primera tarea (7 pruebas, todas pasan). No apareció ningún defecto en la API. Se agregaron `pytest` y `httpx` a `requirements.txt`. Para ejecutar desde la raíz del repo: `python -m pytest tests -v`.

La ejecución se confirmó en Linux y en la `.venv` de Windows con Python 3.12.14. En ambos entornos pasaron las 7 pruebas con un aviso de obsolescencia de Starlette. [Evidencias](docs/relevo/2026-11-04-claude/README.md).

Próxima tarea: cuando llegue el primer clip, enviar sus eventos reales a `POST /ocupacion` y contrastar los resultados por parada con el conteo manual antes de conectarlos al panel.

## Verificado el 4 de noviembre · Tarea 01

El panel carga un recorrido JSON (sin archivo usa la demo), inicializa los controles con los valores del archivo y recorre el tiempo hasta la última parada o evento, incluidas fracciones. Valida el recorrido completo con la API antes de filtrarlo. Se comprobó con Playwright sobre la API y Streamlit reales: el caso de 22,5 s da 5 pasajeros (25 %) a los 22 s y 4 (20 %) a los 22,5 s. También se comprobaron un recorrido sin eventos y tres archivos inválidos. Las 7 pruebas de la API siguen pasando. En la .venv de Windows pasaron las siete pruebas y los valores de los 14 pasos del navegador coincidieron con los de Linux. [Evidencias](docs/relevo/2026-11-04-claude-tarea01/README.md).

La [tarea 02](docs/tareas/claude/02-verificar-clip.md) espera los eventos de visión. Mientras tanto, revisá la tarea 03.

## Verificado el 5 de noviembre · Tarea 03

El panel muestra un gráfico de barras de ocupación por parada con Altair, usando los mismos resultados de `POST /ocupacion` que la tabla. Numera las paradas, marca la última como parcial, dibuja la línea de capacidad del 100 % y ajusta la escala a valores negativos o superiores a 100 %. Se agregaron `Dockerfile`, `docker-compose.yml`, `.dockerignore` y la sección de Docker del README.

Comprobado en Linux (Ubuntu 24.04, Python 3.12.3, Docker 29.9.2, Compose 5.7.0): pasan las 7 pruebas y los 11 pasos del navegador dan los valores de la ficha, iguales en local, en Docker y tras detener y arrancar los servicios. El navegador también cargó la demo y `oficina-00-06-manual.json`. La API respondió en 8001 y el panel en 8502.

En Linux la imagen se construyó sobre una base local sustituta, porque Docker Hub no era accesible. En Windows pasaron las 7 pruebas en la `.venv` y Docker Desktop construyó y arrancó ambos servicios con la imagen oficial `python:3.12-slim`; el panel consultó la API sin errores y volvió a hacerlo después de detener y arrancar los servicios (4 respuestas 200). Una revisión posterior recorrió el panel en Docker sobre Windows: los 11 registros, incluida la demo de oficina, coinciden campo por campo con los de Linux. [Evidencias](docs/relevo/2026-11-05-claude-tarea03/README.md).

## Verificado el 5 de noviembre · Tarea 04

`docs/informe/` contiene el borrador IEEEtran con sus referencias y `informe-borrador.pdf`: 3 páginas A4, resumen de 138 palabras y revisión visual sin defectos pendientes. Documenta la ruta implementada, las pruebas funcionales y deja las métricas de visión marcadas como pendientes, sin cifras. `docs/demo/guion.md` tiene tiempos, responsables, material del compañero y seis preguntas.

El bloque de Álvaro se ensayó contra Docker en Windows sin errores: la demo dio 3 → 5 → 4 pasajeros, capacidad 40 dio 10 % y la oficina dio 0 → 1 → 0. El ensayo fue automático, sin voz. Falta cronometrar a Álvaro y hacer el ensayo completo con el compañero.

El ensayo detectó que, en tema oscuro, el rótulo de valor de las barras casi no se leía. Se corrigió el color en `ui/app.py` y el tema claro quedó como predeterminado con `.streamlit/config.toml`. En Linux, los 11 registros no cambiaron en ninguno de los dos temas y pasan las 7 pruebas. Falta reconstruir la imagen en Windows y comprobarlo. Siguen pendientes la lista de datos de [docs/informe/README.md](docs/informe/README.md) y volver a comprobar las 3 páginas al incorporar métricas. [Evidencias](docs/relevo/2026-11-05-claude-tarea04/README.md).

## Cuando llegue el primer clip

Para el trabajo de Claude, consultá la [carpeta de tareas](docs/tareas/claude/README.md). La primera ficha prepara el panel mientras llega el clip y la segunda describe cómo contrastar los eventos reales.

El compañero aporta el video, la orientación de la línea y los eventos reales con el mismo formato que el ejemplo. Álvaro conecta esa salida al panel y ambos contrastan el contador con una anotación manual. Las cifras de esta demo sintética sirven para probar la integración. Las métricas del informe se calculan con clips reservados para evaluación.

## Revisión tarea 08 · 7 de noviembre
Windows verificado: 15 pruebas API y 84 de visión aprobadas; 1 omitida y 1 fallida por la bajada del modelo. Video reproducible y selector hasta 6 s; gráfico 45 estados sin fallos. Evidencias en docs/relevo/2026-11-07-claude-tarea08/revision-codex-windows.md dentro del worktree integracion-video. Siguiente tarea: docs/tareas/claude/09-evaluacion-windows.md. Informes aplazados; sin commit ni push.
