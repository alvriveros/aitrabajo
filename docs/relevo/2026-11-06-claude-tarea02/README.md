# Devolución · Tarea 02 · Contraste del primer clip

6 de noviembre de 2026. [Ficha de la tarea](../../tareas/claude/02-verificar-clip.md). Rama de trabajo: `tareas-03-04-panel-informe` (`5c3155a`). Los cambios quedan sin commit.

**Resultado:** la predicción coincide con la referencia manual dentro de ±1 s y la API da el resultado esperado. Los indicadores y la tabla del panel dan 0 → 1 → 0 pasajeros. **El gráfico no coincide:** a 2,16 s y 4 s siguió mostrando 0 % mientras indicadores y tabla mostraban 5 %. Es un defecto del panel, reproducido también en Linux.

Es un **ensayo de integración** del detector base `yolo11n.pt` con ByteTrack calibrado (`vision/bytetrack-cenital.yaml`, `conf 0.05`), según el archivo de configuración. No reproduje la inferencia localmente y no es una evaluación en grabaciones independientes: son comprobaciones distintas, todavía pendientes.

## Origen

- `origin/vision` en `dd5a19a719cf8cabce772bc4b238f2e9705d088d` ("Preparar el material de visión para el informe", Ander Porath, 6 nov. 13:01).
- Extraídos sin cambiar de rama ni fusionar, con `git show origin/vision:evaluation/results/<archivo>`. Copias UTF-8 en [insumos/](insumos/).
- Tu copia local no tiene credenciales de GitHub desde esta sesión, así que el `fetch` se hizo en una copia del mismo remoto en el espacio de trabajo en la nube. Tu rama local `vision` y `remotes/origin/vision` no se tocaron.
- Referencia manual: `docs/demo/oficina-00-06-manual.json`, sin cambios.

Configuración relevante: recorte `228,2,222,176` (cuadrante superior derecho), línea horizontal en y = 90, interior arriba, confirmación de 2 cuadros, video a 25 fps (450 × 360), 150 cuadros procesados en 4,32 s (34,7 FPS) en macOS arm64 con CPU.

## Comparación de cruces

Emparejamiento por sentido, un evento manual por predicción, tolerancia ±1 s ([comparacion-cruces.json](comparacion-cruces.json)).

| Sentido | Manual | Predicho | Diferencia | ID manual | ID predicho |
|---|---|---|---|---|---|
| Subida | 2 s | 2,16 s | +0,16 s | 1 | 1 |
| Bajada | 4 s | 4,60 s | +0,60 s | 1 | 5 |

Sin eventos extra ni omitidos. El cambio de ID de 1 a 5 entre ida y vuelta es esperable según la ficha y no afecta el conteo. La referencia manual es aproximada, así que las diferencias no son un error medido.

**Revisión visual del video pendiente:** no reproduje el video. El contraste se hizo entre archivos.

## API

`POST http://127.0.0.1:8001/ocupacion` con el JSON predicho completo, desde el navegador integrado en la máquina de Álvaro (Docker en Windows). Respuesta HTTP 200 ([respuesta-api.json](respuesta-api.json)): una parada, 1 subida, 1 bajada, 0 pasajeros, 0 % y sin avisos. Coincide con lo esperado.

No ejecuté `docker compose up --build -d`: no tengo terminal en Windows. Usé los servicios que estaban activos, construidos el 5 de noviembre desde el mismo código de la rama (`ui/app.py` idéntico, sha256 `dcb74a44…`).

## Panel

Cargué el mismo archivo predicho en `http://127.0.0.1:8502`. El contenido es el del commit; la carga se hizo por script en el selector de archivos, porque el navegador integrado no abre el diálogo de archivos. Agregué 2 s y 4 s, los tiempos manuales.

| Instante | Indicadores | Tabla (subidas, bajadas, pasajeros, %) | Gráfico | ¿Coincide? |
|---|---|---|---|---|
| 0 s | 0 · 0 % | 0, 0, 0, 0 | 0 % | Sí |
| 2 s (manual) | 0 · 0 % | 0, 0, 0, 0 | 0 % | Sí |
| **2,16 s** | **1 · 5 %** | 1, 0, 1, 5 | **0 %** | **No** |
| **4 s (manual)** | **1 · 5 %** | 1, 0, 1, 5 | **0 %** | **No** |
| 4,60 s | 0 · 0 % | 1, 1, 0, 0 | 0 % | Sí |

Sin errores ni avisos. Valores en [valores-panel-windows.json](valores-panel-windows.json) y capturas en [capturas-windows/](capturas-windows/). Esperado según la ficha: 0, 1 y 0 pasajeros (0, 5 y 0 %) en 0, 2,16 y 4,60 s. Indicadores y tabla cumplen; el gráfico no.

Las capturas se tomaron con el navegador a 772 px de ancho, por eso la página muestra el final del bloque de indicadores, el gráfico, la nota con el instante y la tabla. La primera captura salió con un fotograma viejo porque el panel del navegador estaba oculto; se repitió y se descartó.

## Defecto del gráfico

**El gráfico de barras a veces conserva los valores de una ejecución anterior.** Indicadores y tabla siempre muestran el valor correcto.

- Lo reproduje en Linux con Docker, Chromium 153 y Playwright, con el mismo archivo: según la corrida, el gráfico quedó en 0 % con indicador 5 %, o en 5 % con indicador 0 % ([reproduccion-linux/](reproduccion-linux/)). No depende del navegador de Windows.
- El servidor genera bien el gráfico: `graficar` produce datos distintos y correctos para cada instante. El fallo está en cómo el componente de gráficos de Streamlit 1.48.1 actualiza los datos en el navegador.
- Probé tres correcciones en mi copia de Linux y ninguna fue confiable: una clave por datos en `st.altair_chart`, datos como `DataFrame` y una huella de datos en `usermeta`. La segunda redujo los fallos de 18 a 6 en 30 pasos, pero no los eliminó. Restauré `ui/app.py`; tu copia nunca cambió.
- **Esto corrige la tarea 03:** allí comprobé que el gráfico estuviera presente, no que su valor coincidiera con la tabla después de mover el selector. Las capturas revisadas entonces eran de cargas iniciales, que se dibujan bien.
- Efecto en el informe: la Fig. 2 es una carga inicial y es correcta. La frase de la sección II-D, que dice que el gráfico muestra los resultados, es cierta al cargar pero no en todos los cambios.

## Comandos

```sh
git fetch origin vision
git rev-parse origin/vision
git show origin/vision:evaluation/results/oficina-00-06-prediccion.json
git show origin/vision:evaluation/results/oficina-00-06-prediccion.config.json
# POST desde el navegador en http://127.0.0.1:8001 (mismo origen):
# fetch('/ocupacion', {method:'POST', headers:{'Content-Type':'application/json'}, body: <JSON predicho>})
python reproduccion-linux/reproducir.py <JSON predicho>   # con el panel en 127.0.0.1:8502
```

## Pendientes

1. **Corregir el gráfico** antes de la defensa. Opciones: renderizarlo de otra forma (por ejemplo, `st.bar_chart` o una imagen) o investigar el componente de Streamlit. Requiere decisión de Álvaro.
2. Revisión visual del video en los cruces de 2,16 s y 4,60 s.
3. Reproducir la inferencia localmente según `vision/README.md`.
4. Evaluación en grabaciones independientes, a cargo del compañero.
5. Ejecutar `docker compose up --build -d` en Windows si se cambia el código.
