# Devolución · Tarea 03 · Gráfico de ocupación y Docker

5 de noviembre de 2026. [Ficha de la tarea](../../tareas/claude/03-panel-docker.md). Los cambios quedan sin commit para la revisión de Álvaro.

**Resultado:** gráfico y Docker implementados. Pasaron todas las comprobaciones en Linux. En Windows pasaron las pruebas, la construcción y el arranque con la imagen oficial `python:3.12-slim`, y el panel volvió a consultar la API después de detener y arrancar los servicios.

## Archivos cambiados

- `ui/app.py`: función `graficar` con Altair y su uso en el panel, más la nota de conteo parcial.
- `README.md`: sección de Docker y estado de lo implementado.
- `resumen.md`: lo implementado y lo comprobado.
- Nuevos: `Dockerfile`, `docker-compose.yml`, `.dockerignore` y esta carpeta. La lista completa está en `archivos-nuevos.txt`.

`cambios.diff` incluye también los cambios previos sin commit que ya estaban en `docs/tareas/claude/README.md` y `resumen.md`. La ficha `03-panel-docker.md` tampoco estaba commiteada. `api/` y `tests/` no cambiaron.

## Entorno

| Elemento | Valor |
|---|---|
| Sistema | Ubuntu 24.04.5, Linux 6.18, espacio de trabajo en la nube de Claude. **No es Windows.** |
| Python local | 3.12.3, con `requirements.txt` instalado en un entorno nuevo |
| Docker | Engine y cliente 29.9.2, Compose 5.7.0, sin Docker Desktop |
| Navegador | Chromium 153 con Playwright |
| Versiones de la imagen | streamlit 1.48.1, altair 5.5.0, fastapi 0.116.1, uvicorn 0.35.0 |

## Diferencia con la imagen real

Docker Hub no es accesible desde este entorno: `python:3.12-slim` da `Forbidden` en `registry-1.docker.io`. Para probar Compose de verdad armé una base local con el Python 3.12.3 de Ubuntu, sus librerías y `pip`, y la etiqueté `python:3.12-slim` ([definición](base-sustituta.Dockerfile)). Agrega el certificado del proxy de este entorno solo para instalar paquetes.

El `Dockerfile` del proyecto no se modificó para esto y `pip install -r requirements.txt` se ejecutó de verdad dentro de la construcción. Lo que **no** quedó probado es la base oficial: su sistema y sus librerías son otros, aunque el proyecto no usa dependencias del sistema.

## Comandos

```bash
python -m pytest tests -v
docker compose config
docker compose up --build -d
docker compose stop && docker compose start
docker compose logs --no-color
docker compose down
PANEL_URL=http://127.0.0.1:8502 python recorrer_panel.py casos docs/demo/oficina-00-06-manual.json SALIDA
```

`recorrer_panel.py` se ejecutó con el Python del entorno, que tiene Playwright. La misma ruta de 11 pasos corrió contra la ejecución local (8501) y contra Docker (8502).

## Esperado frente a observado

Los valores salen de `valores-docker.json`, en el mismo orden que las capturas. El gráfico se revisó a ojo en las capturas 01, 02, 06, 09, 10 y 11 de la ejecución local. Las capturas de Docker son las guardadas aquí y sus valores son idénticos a los locales, pero no las inspeccioné una por una.

| # | Caso | Esperado | Observado | Estado |
|---|---|---|---|---|
| 1 | `pytest` | 7 pruebas pasan | 7 passed, 1 aviso de Starlette | Sí |
| 2 | Demo a 10 s | 5 y 25 %, luego 4 y 20 % | Tabla y gráfico iguales; indicadores 4 y 20 % | Sí |
| 2 | Demo a 5 s | Solo la primera parada, 25 % | Una barra, 25 %, parcial | Sí |
| 3 | 22,5 s en 22 s y 22,5 s | De 5 a 4 pasajeros | 5 (25 %) y 4 (20 %) | Sí |
| 3 | Capacidad 10 | Todo se actualiza junto | Indicadores 40 %; tabla 50 y 40 | Sí |
| 4 | Nombres repetidos | Paradas distinguibles | `1 · Centro`, `2 · Terminal`, `3 (parcial) · Centro` | Sí |
| 4 | Eventos vacíos | La carga se conserva | 15 % en ambas paradas | Sí |
| 4 | Una sola parada | Una barra parcial | 5 pasajeros, 25 % | Sí |
| 4 | Capacidad 2, carga 3 | 150 % | 150 %, barra sobre la línea de 100 % | Sí |
| 4 | Carga 0, una bajada | −1, −5 % y aviso | -1, -5 %, barra bajo cero y aviso | Sí |
| 5 | `docker compose config` | Válido | Válido, puertos y healthcheck correctos | Sí |
| 5 | API en 8001 y panel en 8502 | Consultas reales | `POST /ocupacion`, `/openapi.json` y health dan 200 | Sí, en Linux |
| 5 | Demo y oficina en el navegador | Cargan | Oficina a 4 s: 0 pasajeros, 0 % | Sí, en Linux |
| 5 | Panel espera a la API | `service_healthy` | La API queda Healthy antes de iniciar el panel | Sí, en Linux |
| 6 | Detener y arrancar | El panel vuelve a consultar | Los 11 pasos dan valores iguales a antes | Sí, en Linux |
| — | `.dockerignore` | Excluye lo indicado | En una copia con archivos de prueba solo quedó lo que lista `dockerignore-contexto.txt` | Sí |

## Diferencias entre ejecución local y Docker

Los 11 pasos dieron valores idénticos en local y en Docker (`valores-local.json` y `valores-docker.json`). Las únicas diferencias previstas son los puertos y `API_URL`.

## Decisiones y hallazgos

- La marca "(parcial)" va junto al número porque el eje recorta nombres largos y, al final de la etiqueta, se perdía con el caso de oficina. El nombre completo sigue en la nota bajo el gráfico y en la tabla.
- La última parada visible siempre figura como parcial, también al final del recorrido, tal como pide la ficha.

## Comprobación en Windows

Álvaro ejecutó los comandos en PowerShell el 5 de noviembre, y Claude leyó las salidas guardadas. Docker Desktop usa el motor Linux.

| Comprobación | Observado | Estado |
|---|---|---|
| `pytest` en la `.venv` (Python 3.12.14) | 7 passed, 1 aviso de Starlette (`pytest-windows.txt`) | Sí |
| Construcción con la base oficial | `python:3.12-slim@sha256:4840d514c583…`, dependencias instaladas, imagen construida (`compose-up-windows.txt`) | Sí |
| Arranque | La API queda Healthy y luego inicia el panel | Sí |
| Consultas del panel a la API | 16 `POST /ocupacion` con 200 en la primera ejecución; ese registro fue reemplazado por el de la segunda | Sí |
| Detener y arrancar | La API reinicia y responde al healthcheck | Sí |
| El panel vuelve a consultar tras reiniciar | 4 `POST /ocupacion` con 200 después del segundo arranque, sin errores (`compose-logs-windows.txt`) | Sí |
| Demo y oficina en el navegador | Álvaro informó haber hecho la carga. Las 4 consultas coinciden con dos cargas de 2 consultas cada una, pero los registros no muestran qué archivo ni qué valores | Parcial |

El `NativeCommandError` al inicio de `compose-up-windows.txt` no es un fallo: PowerShell lo muestra al redirigir la salida de error de Docker, y el comando terminó bien. La salida de `docker compose config` en Windows no se guardó, aunque la construcción y el arranque usaron ese archivo sin errores.

Docker Hub ya responde desde el espacio de Linux, pero la descarga se detiene en `production.cloudfront.docker.com`, que no está permitido. La imagen oficial no se probó en ese entorno. No hace falta para la tarea, porque ya se construyó en Windows.

## Pendientes

### Revisión independiente en Windows · 5 de noviembre

Se comprobó la configuración de Compose y pasaron las siete pruebas de la API (un aviso de Starlette). Los servicios estaban detenidos; se arrancaron con la imagen oficial y el healthcheck de la API pasó. Se ejecutó `recorrer_panel.py` contra el puerto 8502 usando la .venv de Windows y Chromium.

Los 11 registros de [revision-windows/valores.json](revision-windows/valores.json) coinciden campo por campo con `valores-docker.json` de Linux. Incluyen indicadores, tabla, instantes, nota parcial, presencia del gráfico, errores y avisos. Se inspeccionaron las capturas de demo a 10 s, sobreocupación al 150 % y conteo negativo al −5 %; las barras y la referencia del 100 % se muestran correctamente. Esta evidencia completa la comprobación de valores en Windows, incluida la demo de oficina. Las capturas están en `revision-windows/`.

La revisión no requirió cambios de código. Los contenedores quedan activos y los cambios siguen sin commit.

1. **Resuelto · `main` al día:** el 5 de noviembre, `git ls-remote` mostró `main` remoto en `3d92072`, el mismo commit que la copia local.
2. La tarea 02 sigue esperando los eventos de visión del primer clip.
