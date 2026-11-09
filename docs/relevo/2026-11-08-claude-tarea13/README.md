# Subir y procesar un video nuevo desde el panel · devolución (8 nov., noche)

Pedido de Álvaro: la consigna exige subir y procesar un video desde la página. Se trabajó en `integracion-video`, se conservaron los cambios pendientes y no hubo commit. **El video nuevo de validación no se usó**: las pruebas se hicieron con PAMELA A y oficina, que ya estaban usados.

## Qué cambió

**API (`api/main.py`).** La demo de oficina y `/ocupacion` siguen igual. Los endpoints nuevos son:

| Endpoint | Qué hace |
|---|---|
| `POST /videos?nombre=…` | Recibe el archivo crudo. Valida la extensión (mp4, avi, mov, mkv o webm), un tamaño de hasta 200 MB, que se pueda leer y que dure hasta 5 min. Lo guarda en `runs/videos/<id>/` con su SHA-256, y subir dos veces el mismo archivo no lo duplica. |
| `GET /videos/{id}` | Propiedades, SHA-256, sistema de coordenadas y origen temporal. |
| `GET /videos/{id}/cuadro?t=&recorte=&linea=&interior=` | Cuadro aproximado con el recorte, la línea y una flecha hacia el interior. **No ejecuta el modelo.** Valida la geometría. |
| `POST /videos/{id}/procesamientos` | Procesa el video completo con la geometría pedida y **las mismas opciones de modelo de la API**, tomadas del comando guardado de la demo: `yolo11n`, ByteTrack cenital, confianza 0,05, confirmación de 2 cuadros, CPU. No usa supresión temporal. |
| `GET /procesamientos?origen=demo\|video&video=<id>` | Lista filtrada; sin filtros, igual que antes. |

- **Ejecuciones aisladas:** cada una va en su propia carpeta de `runs/panel/`, con `entrada.json`, que guarda el video, el SHA, la geometría y las opciones del modelo. La configuración y el registro son los de siempre.
- **Sin duplicados:** hay un procesamiento a la vez (409 si hay otro en curso), y la misma geometría con el mismo modelo sobre el mismo video no se repite (409, indicando la ejecución existente).
- **Errores:** son mensajes en castellano con el código HTTP correspondiente: 413, 415, 422, 404, 409, 503 o 504.

**Panel (`ui/app.py`).** Hay un tercer origen, **«Video nuevo»**:

1. Subir el archivo; se envía a la API una sola vez por archivo.
2. Explicación de coordenadas y origen temporal; controles de recorte, línea e interior; vista previa del cuadro elegido. La línea también se muestra en coordenadas del cuadro completo.
3. «Procesar video», que solo corre al pulsarlo.
4. Resultado:
   - video anotado y tabla de eventos;
   - descargas del **JSON de eventos**, del **video anotado** y de la **configuración** (entrada + configuración efectiva);
   - la ocupación de siempre más abajo.

**Sin cambios:** la demo de oficina, que ahora solo lista sus propias ejecuciones, y la carga de JSON.

**Anotador (`tarea11/anotar_cruces.py`):**
- el tiempo de cada marca ahora usa la marca de tiempo del archivo, igual que el pipeline y el panel;
- acepta una línea cualquiera, `--linea X1,Y1,X2,Y2`, en coordenadas del cuadro completo, las mismas que muestra el panel.

## Cómo se verificó

Contenedor Linux de Claude, CPU.

- **Tests:**
  - `python -m pytest`: 122 aprobados, 1 omitido y **1 fallo conocido**, `test_ensayo_de_oficina_…`, la bajada de oficina, igual que antes;
  - `tests/test_videos.py`, nuevo, con 10 tests: subida válida y duplicada, archivos vacíos, rotos o de otra extensión, límites de tamaño y duración, vista previa sin inferencia, cuatro geometrías inválidas, opciones del modelo iguales a las de la demo, filtros de listado, no repetir, un procesamiento a la vez y video inexistente.
- **En el navegador** (Chrome sin pantalla, contra la API y el panel reales):
  - **Video nuevo con PAMELA A:** con la geometría de las tareas 09 y 11, los eventos procesados desde la página son **idénticos** a los de `tarea11/linux/pamela-A/eventos/yolo11n-calibrado.json` (11 eventos; bajadas 10/0/18).
  - **Repetición:** un segundo clic en «Procesar video» mostró el aviso «No se repite» y no lanzó otra ejecución.
  - **Descargas:** JSON con 11 eventos, configuración con SHA y `conf` 0,05, y video webm de 5,7 MB.
  - **Geometría inválida:** con el recorte fuera del cuadro aparece el error claro y no se procesa nada.
  - **Demo de oficina:** «Procesar clip de oficina» terminó bien (201) y muestra la predicción y la referencia manual.
  - **JSON o demo:** carga la demo y muestra la ocupación.
- **Windows** (Álvaro, 8 nov., 19:54, `.venv` del worktree): `pytest -q` dio 122 aprobados, 1 omitido y solo el fallo conocido de oficina.
  - Antes había un segundo fallo, solo en Windows: la ruta del video se armaba con `\`.
  - Se corrigió para que use siempre `/`, así el comando guardado es portable.
- **Página en Windows** (Álvaro, 8 nov., 19:55): hizo el recorrido manual con PAMELA A. Salieron 11 eventos (10 bajadas y 1 subida) y el segundo clic avisó «No se repite». Según Álvaro, el resto de los pasos funcionaron como estaba previsto.

## Arranque (Windows, PowerShell, dos ventanas)

```
cd C:\Users\Alvaro\Desktop\Facultad\4to\IA\TpFinal\.worktrees\integracion-video
.\.venv\Scripts\python.exe -m uvicorn api.main:app --port 8000
```
```
cd C:\Users\Alvaro\Desktop\Facultad\4to\IA\TpFinal\.worktrees\integracion-video
.\.venv\Scripts\python.exe -m streamlit run ui/app.py
```
El panel abre en `http://localhost:8501`. Tests: `.\.venv\Scripts\python.exe -m pytest -q`.

## Pasos exactos para la validación con el video nuevo

Sigue `tarea12/protocolo-validacion-nueva.md`. **No mires ningún resultado del modelo hasta el paso 4.**

1. **Copiar el video** a `data\raw\validacion-nueva-<fecha>.mp4`.
2. **Fijar la geometría sin inferencia:**
   - en el panel, «Video nuevo» → subirlo → ajustar recorte, línea e interior mirando la vista previa;
   - **no pulsar «Procesar video»**;
   - anotar los valores y la línea «en el cuadro completo» que muestra el panel.

   Se hace antes de anotar porque el anotador necesita saber dónde está la línea. Mirar cuadros sueltos no revela nada del modelo.
3. **Anotar los cruces** con esa misma línea:
   ```
   .\.venv\Scripts\python.exe docs\relevo\2026-11-08-claude-tarea11\anotar_cruces.py --video data\raw\validacion-nueva-<fecha>.mp4 --salida data\annotations\validacion-nueva-cruces.json --linea X1,Y1,X2,Y2
   ```
   Al terminar, agregá en `notas` lo que haya que aclarar y guardá el SHA-256 del JSON (`Get-FileHash`).
4. **Procesar una sola vez:** en el panel, con la misma geometría, pulsar «Procesar video». Descargar el JSON y la configuración.
5. **Pedir la comparación** a Claude o Codex: TP, FP y FN por sentido, con ±1 s. **No cambiar la geometría ni los parámetros después de ver el resultado.**

## Guion corto para la demo en vivo (unos 3 minutos)

1. **Inicio:** «Ocupación del bus»: la API calcula la ocupación por parada a partir de los cruces.
2. **Archivo JSON o demo:** mover el selector de segundos y ver cómo cambia la ocupación.
3. **Video nuevo:**
   - subir un video corto;
   - explicar las coordenadas (origen arriba a la izquierda, línea dentro del recorte, flecha verde hacia el interior);
   - mostrar que la vista previa no ejecuta el modelo.
4. **Procesar video:** mientras procesa, contar que usa YOLO11n, ByteTrack y la regla de cruce con confirmación. Mostrar el video anotado, la tabla de eventos y las descargas.
5. **Ocupación:** bajar a la ocupación por parada; cerrar con las limitaciones medidas: en la prueba final se contaron 6 de 18 cruces.

Para que la demo no dependa del tiempo de proceso, conviene haber procesado el video antes: la ejecución queda en la lista «Ejecución» y se muestra al instante.

## Limitaciones pendientes

- **Velocidad:** se procesa en **CPU**, como fija la configuración de la API. Un video de 5 min puede tardar varios minutos (en el contenedor, unos 12 FPS). El límite es de 30 min.
- **Espera del panel:** espera la respuesta. Si se recarga la página durante el proceso, la API termina igual y la ejecución aparece en la lista; otro clic recibe 409.
- **Un solo proceso:** el bloqueo de «un procesamiento a la vez» vale para una API con un único proceso de uvicorn, como se arranca hoy.
- **Vista previa aproximada:** salta al segundo pedido y puede caer en un cuadro vecino. Sirve para ubicar la línea, no para anotar.
- **Docker:** la imagen no tiene las dependencias de visión, así que subir un video responde 503 con el motivo, igual que la demo de oficina.
- **Espacio en disco:** los videos subidos quedan en `runs\videos\` (fuera de Git) y no se borran solos.
- **Calidad del conteo:** sigue siendo la medida: la API cuenta mal en escenas reales. Esta tarea agrega la funcionalidad, no mejora el conteo.
