# Tarea 07 · Video conectado con el conteo · relevo de Claude (7 nov.)

Rama `integracion-video`, en el worktree `.worktrees/integracion-video`. Sale de `d0a658a` porque la copia principal tenía cambios sin commit. Incorpora `origin/vision` en `dd5a19a` con una fusión `--no-ff` (`e85fb75`), sin conflictos, así que los dos historiales quedan conservados. No se fusionó nada en `main`. Los cambios de integración quedan **sin commit** para revisión. El informe académico no se tocó.

> La copia local de `origin/vision` estaba en `3d92072`, sin el pipeline. `dd5a19a` se trajo de GitHub mediante un bundle y quedó en `refs/remotes/origin/vision`. La rama local `vision` (`2078f2a`) no se modificó.

## Resultado

**El recorrido completo funciona desde el panel.** El modelo genera la predicción y el video anotado, el panel los muestra y la ocupación se calcula con esos eventos.

**El detector base no reprodujo la bajada en este equipo.** Detectó la subida a 2,16 s, igual que en macOS, pero omitió la bajada de 4,60 s. La predicción se guarda tal como salió del modelo.

| | Referencia manual | Predicción guardada (macOS, `dd5a19a`) | **Esta ejecución (Linux x86)** |
|---|---|---|---|
| Subida | ≈ 2 s | 2,16 s, track 1 | **2,16 s, track 1** (+0,16 s) |
| Bajada | ≈ 4 s | 4,60 s, track 5 | **omitida** |
| Ocupación a 0 s | 0 · 0 % | 0 · 0 % | **0 · 0 %** |
| Tras la subida | 1 · 5 % | 1 · 5 % | **1 · 5 %** (a 2,16 s) |
| Tras la bajada | 0 · 0 % | 0 · 0 % | **1 · 5 %** (no hay bajada predicha; queda así hasta los 6 s) |

**Por qué falta la bajada.** En el video anotado ([`cuadros-cruces.png`](cuadros-cruces.png)), la persona cruza la línea hacia abajo entre 4,44 y 4,80 s sin ninguna caja. El detector recién la toma a 4,92 s, ya debajo de la línea y con un ID nuevo (9). Sin lado de origen confirmado no hay evento: es la limitación documentada en `vision/README.md`.

La causa parece una diferencia numérica de CPU en detecciones con confianza cercana a 0,05–0,1. La configuración es `conf 0.05` con ByteTrack cenital. Lo indican tres cosas:

- El código de `vision` **sin mis cambios** (`e85fb75`) da el mismo resultado.
- La prueba del compañero `test_ensayo_de_oficina_sigue_dentro_de_la_tolerancia_de_la_referencia_manual` también falla acá.
- Dos ejecuciones seguidas desde el panel dieron el mismo JSON.

Falta comprobar qué ocurre en la máquina de defensa (Windows). No se probó el detector ajustado: sus pesos (`runs/oficina-ajuste/oficina-ajustado.pt`) no estaban disponibles.

## Qué cambió

- **API** (`api/main.py`):
  - `POST /procesamientos` ejecuta `python -m vision.pipeline` en un subproceso. Usa los argumentos de `evaluation/results/oficina-00-06-prediccion.config.json` y solo cambia los destinos.
  - Cada ejecución queda en `runs/panel/<id>/`: `prediccion.json`, `prediccion.config.json`, `registro.txt` y `anotado.webm`.
  - `GET /procesamientos`, `GET /procesamientos/{id}` y `GET /procesamientos/{id}/video` permiten consultarlas. El `id` se valida con un patrón.
  - Si faltan el clip, los pesos o las dependencias de visión, responde 503 con el nombre de lo que falta. Si el pipeline falla, responde 500 con su error.
- **Panel** (`ui/app.py`):
  - Agrega el selector **Origen de los eventos**. "Archivo JSON o demo" es el comportamiento anterior y sigue siendo el predeterminado.
  - En "Predicción automática del video de oficina" hay un botón para procesar, un selector de ejecuciones guardadas y el video anotado. La **Predicción automática** y la **Referencia manual** se muestran en tablas separadas y rotuladas.
  - La ocupación usa solo la predicción.
- **Pipeline** (`vision/pipeline.py`, 1 línea): si el destino termina en `.webm`, el video anotado se escribe en VP8. Los navegadores no reproducen `mp4v`. Por terminal sigue saliendo `.mp4`.
- **Docker** (`Dockerfile`): copia `vision/` y la configuración. La imagen **no** instala las dependencias de visión, así que ahí `POST /procesamientos` responde 503.
- **Pruebas:** `tests/test_procesamientos.py` cubre los endpoints con un pipeline simulado: argumentos, consulta, video, 503, 500 e IDs inválidos.
- **Documentación:** `README.md` tiene una sección nueva, **Procesar el video desde el panel**.

## Equipo y versiones

Contenedor Linux de Claude, en la nube y no en tu máquina:

- **Hardware:** Intel Xeon a 2,30 GHz, 2 vCPU y 7 GB de RAM, sin GPU.
- **Software:** Python 3.12.3, ultralytics 8.4.203, torch 2.15.0, opencv-python 5.0.0.93, lap 0.5.14, fastapi 0.116.1, streamlit 1.48.1, Chromium 153 con Playwright 1.63.0.

Archivos requeridos, que git ignora:

| Archivo | Bytes | SHA-256 | Origen |
|---|---|---|---|
| `data/raw/oficina.mp4` | 1.375.027 | `02666c2e567f45015a2e73fe802db8f39c6c568d41ef42efc63997de4d15fc95` | Descargado por Álvaro con `yt-dlp` 2026.10.26, formato 134. El hash coincide. |
| `yolo11n.pt` | 5.613.764 | `0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1` | Release v8.4.0 de Ultralytics. El hash coincide. |

Ambos están copiados en la raíz del worktree. El clip no se versiona ni se redistribuye (ver `data/README.md`), y tampoco el video anotado: queda en `runs/panel/`.

## Tiempos de procesamiento

Son 150 cuadros, con 222×176 de recorte, en CPU y con video anotado:

| Ejecución | Pipeline | FPS | Pared |
|---|---|---|---|
| Panel, 1.ª (`20261107-192800-383466`) | 21,6 s | 6,9 | 93 s, con arranque de Chromium y primera carga de torch |
| Panel, 2.ª (`20261107-193104-352371`) | 12,5 s | 12,0 | 40 s para todo el script del panel |
| Terminal, mismo comando | — | — | 12,6 s |
| Referencia de macOS (Apple M4) | 4,3 s | 34,7 | — |

## Comandos y verificaciones

Desde la raíz del worktree, con `.venv` de Python 3.12 y `requirements.txt` + `vision/requirements.txt`:

```sh
python -m uvicorn api.main:app --port 8000
python -m streamlit run ui/app.py --server.port 8501 --server.headless true
PANEL_URL=http://127.0.0.1:8501 python docs/relevo/2026-11-07-claude-tarea07/scripts/verificar_video.py SALIDA/
PANEL_URL=http://127.0.0.1:8501 python docs/relevo/2026-11-07-claude-tarea07/scripts/verificar_grafico.py \
  docs/relevo/2026-11-06-claude-tarea05/casos/oficina-00-06-prediccion.json docs/relevo/2026-11-06-claude-tarea05/casos SALIDA/
python -m pytest tests -v
```

| Verificación | Resultado | Evidencia |
|---|---|---|
| Recorrido del panel: procesar, video, tablas y ocupación | Exit 0. El video VP8 de 222×176 y 6 s se reprodujo en Chromium sin error. Ocupación a 0, 1, 2 y 2,16 s: 0, 0, 0 y 1 pasajero (0, 0, 0 y 5 %). | [`panel/`](panel/) |
| Predicciones de ambas ejecuciones | Idénticas: 1 subida a 2,16 s. | [`ejecuciones/`](ejecuciones/) |
| `POST /ocupacion` con la predicción | 200: 1 subida, 0 bajadas, 1 pasajero, 5 %, sin avisos. | [`ocupacion-api.json`](ocupacion-api.json) |
| Consulta de ejecuciones y video | 200 y `video/webm` en ambas. | [`consultas-api.txt`](consultas-api.txt) |
| Sin clip ni pesos | El panel muestra el 503 con `data/raw/oficina.mp4, yolo11n.pt`. | [`sin-insumos/`](sin-insumos/) |
| Carga de JSON y gráfico: 45 estados de la tarea 05 | 45 estados, 32 transiciones, **0 fallos**, en el panel nuevo y en el de `d0a658a`. | [`grafico/`](grafico/) |
| `pytest` | 97 aprobadas, 1 omitida (detector ajustado, sin pesos) y **1 fallida**: la del ensayo de oficina del compañero, por la bajada omitida. | [`pytest.txt`](pytest.txt) |

**Ajuste del script de la tarea 05.** El script original da un fallo en el panel nuevo: "conteo-negativo: barra 1: sin color en la captura" ([`grafico/script-original-panel-nuevo/`](grafico/script-original-panel-nuevo/)). Es un problema del script, no del gráfico. El selector nuevo alarga la página y el script medía el SVG antes de que la captura la desplazara. La captura es idéntica a la del panel base. La copia en [`scripts/verificar_grafico.py`](scripts/verificar_grafico.py) agrega una línea que desplaza antes de medir, y con ella ambos paneles dan 0 fallos.

El análisis completo del caso, con la confianza del detector cuadro a cuadro, está en [`docs/casos-deteccion/oficina-bajada-omitida/`](../../casos-deteccion/oficina-bajada-omitida/README.md).

## Observación en Windows (Álvaro, 7 nov. 19:45)

En la máquina de defensa, desde el panel, la subida se marca en verde y se cuenta, pero la bajada no se detecta. Coincide con Linux x86; la bajada de 4,60 s solo apareció en macOS. Falta guardar `windows/resultado.json` con el script.

## Pendientes

1. **Máquina de defensa (Windows).** No la pude ejecutar. Bloque para PowerShell, desde `TpFinal\.worktrees\integracion-video`:

   ```powershell
   py -3.12 -m venv .venv
   .\.venv\Scripts\python.exe -m ensurepip
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt -r vision\requirements.txt playwright
   .\.venv\Scripts\python.exe -m playwright install chromium
   $env:PYTHONUTF8 = '1'
   $t07 = 'docs/relevo/2026-11-07-claude-tarea07'
   .\.venv\Scripts\python.exe -m pytest tests -v > "$t07/windows-pytest.txt"
   # En dos terminales aparte:
   #   .\.venv\Scripts\python.exe -m uvicorn api.main:app --port 8000
   #   .\.venv\Scripts\python.exe -m streamlit run ui/app.py
   $env:PANEL_URL = 'http://127.0.0.1:8501'
   .\.venv\Scripts\python.exe "$t07/scripts/verificar_video.py" "$t07/windows"
   ```

   Hay que confirmar tres cosas: que `windows/resultado.json` diga `"procesado": true`, que el video se vea en el navegador (VP8 con el OpenCV de Windows) y qué eventos predice. Si aparece la bajada, la diferencia con este equipo queda confirmada como dependiente de la plataforma.
2. **Decidir qué hacer con la omisión.** No cambié parámetros para forzar el resultado. Las opciones son del compañero: revisar `conf` o el rastreador en validación, o usar el detector ajustado con el rastreador por defecto. Esta segunda vía necesita sus pesos.
3. **Docker con visión.** No se incluyó; la demo con video usa el arranque manual.
