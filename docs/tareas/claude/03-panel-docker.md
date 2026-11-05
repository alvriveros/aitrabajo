# 03 · Gráfico de ocupación y arranque con Docker

Disponible desde el 5 de noviembre de 2026. Trabajá en la copia actualizada de `main`. El objetivo es completar la visualización por parada y arrancar API y panel con un solo comando. Podés realizar esta tarea con los JSON existentes mientras el compañero prepara los eventos de visión.

## Gráfico del panel

- Agregá un gráfico de barras de ocupación (%) por parada usando los resultados de `POST /ocupacion` hasta el segundo seleccionado. Conservá la carga de archivos, los controles, los indicadores y la tabla.
- Respetá el orden del recorrido. Identificá las paradas por número y nombre para distinguir nombres repetidos. Indicá que la última parada visible tiene conteo parcial al instante seleccionado.
- Mostrá los ejes de parada y ocupación (%), y una línea horizontal rotulada como capacidad del 100 %. Ajustá la escala para mostrar también porcentajes negativos o superiores al 100 %. Los valores del gráfico deben coincidir con la tabla.
- Reutilizá las herramientas de gráficos disponibles con Streamlit. Mantené el cálculo y la validación del recorrido en la API.

## Arranque reproducible

- Creá un `Dockerfile` basado en Python 3.12 que instale las dependencias y copie los archivos necesarios para API, panel y ejemplos.
- Creá `docker-compose.yml` con servicios `api` y `panel`, usando la misma imagen. Ejecutá Uvicorn en `0.0.0.0:8000` y Streamlit en `0.0.0.0:8501`. Configurá `API_URL=http://api:8000` en el panel.
- Publicá la API en `127.0.0.1:8001` y el panel en `127.0.0.1:8502`. Estos puertos permiten mantener la ejecución manual existente.
- Configurá un healthcheck HTTP de la API contra `/openapi.json` usando Python, con intervalo de 5 s, timeout de 3 s, período inicial de 10 s y hasta 12 intentos. El panel debe depender de que la API esté saludable.
- Creá `.dockerignore` para excluir `.venv`, `.git`, cachés, archivos de entorno, videos, pesos, datos crudos y capturas/evidencias de pruebas. Incluí los JSON de `docs/demo/` que consume la aplicación.
- Documentá en el README el arranque con `docker compose up --build`, las URLs, los registros con `docker compose logs` y el cierre con `docker compose down`.

Docker y Compose están instalados en Windows. En la revisión del 5 de noviembre el motor no respondió. **Iniciá Docker Desktop y esperá a que el motor Linux esté disponible antes de probar los contenedores.** Si verificás desde Linux, identificá ese entorno y dejá explícita la comprobación pendiente de Windows.

## Aceptación

1. Ejecutá `python -m pytest tests -v` y guardá la salida. Deben pasar las siete pruebas existentes.
2. En la demo, verificá los 5 pasajeros y 25 % de la primera parada y los 4 pasajeros y 20 % de la segunda al llegar a 10 s. Al elegir 5 s, el gráfico debe mostrar solo la primera parada con 25 %.
3. Cargá el caso de 22,5 s de la tarea 01 y comprobá la transición de 5 a 4 pasajeros. Cambiá la capacidad y verificá que tabla, indicadores y gráfico se actualicen juntos.
4. Comprobá nombres repetidos, eventos vacíos y una sola parada. Para sobreocupación usá capacidad 2 y carga inicial 3 sin eventos, que da 150 %. Para conteo negativo usá carga inicial 0, capacidad 20 y una bajada, que da −1 pasajero y −5 %, junto al aviso correspondiente.
5. Ejecutá `docker compose config`, construí y arrancá ambos servicios. Verificá la API en el puerto 8001 y el panel en 8502 mediante consultas reales. Cargá la demo y `docs/demo/oficina-00-06-manual.json` desde el navegador.
6. Detené y arrancá nuevamente los servicios, y comprobá que el panel vuelva a consultar la API. Registrá cualquier diferencia entre ejecución local y Docker.

## Devolución

Dejá los cambios **sin commit** para la revisión de Álvaro. Guardá en `docs/relevo/2026-11-05-claude-tarea03/` un README con archivos cambiados, entorno y versiones, comandos, esperado frente a observado y pendientes. Adjuntá salidas de pytest y Compose, capturas del gráfico y los casos utilizados. El diff debe acompañarse de una lista de archivos nuevos.

Actualizá `resumen.md` con lo implementado y lo efectivamente comprobado. Si Docker no puede ejecutarse, indicá el error y conservá esa verificación como pendiente. La tarea 02 sigue esperando los eventos de visión del primer clip.
