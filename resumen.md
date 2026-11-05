# Relevo para Claude · 5 de noviembre de 2026

## Tarea actual · 5 de noviembre

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
