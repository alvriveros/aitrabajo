# Cierre de la versión de entrega (8 nov., noche)

Rama `integracion-video`, sin commit. Reúne las tareas 13 y 14.

## Qué se entrega

- **API** (`api/main.py`):
  - `/ocupacion`;
  - la demo de oficina (`/procesamientos`);
  - videos nuevos (`/videos…`): subida validada, vista previa de la geometría sin inferencia, procesamiento explícito y sin duplicados, y resultados descargables.
- **Panel** (`ui/app.py`), con tres orígenes: «Archivo JSON o demo», «Predicción automática del video de oficina» y «Video nuevo».
- **Conteo:** `vision/` sin cambios. Usa `yolo11n.pt` y ByteTrack cenital, con confianza 0,05, margen de 5 px y confirmación de 2 cuadros, en CPU.
  - **No se agregó ningún filtro.** El de cajas encimadas (tarea 14) se descartó porque borraba cruces reales.
  - **No se bajó el umbral de confianza.** Bajarlo sin una evaluación podría sumar detecciones falsas.

## Arranque (Windows)

Dos ventanas de PowerShell, **en `TpFinal\.worktrees\integracion-video`**. Desde `TpFinal` hay otra rama y otro entorno, y falla.

```
.\.venv\Scripts\python.exe -m uvicorn api.main:app --port 8000
.\.venv\Scripts\python.exe -m streamlit run ui/app.py
```

La página queda en `http://localhost:8501`.

## Resultado de las pruebas automáticas

Primera corrida en Windows: Álvaro, 8 nov., 20:42, con `.\.venv\Scripts\python.exe -m pytest -q -rx`.

**No está todo aprobado.** El resultado es: **129 aprobados, 1 fallido, 1 omitido y 1 xfail**.

Después se agregó un test de la repetición para demostración (`tests/test_videos.py`).

**Verificación final de Codex en Windows** (8 nov., noche): **130 aprobados, 1 fallido (bajada omitida en oficina), 1 omitido y 1 xfail (cajas encimadas)**. El test de reprocesamiento pasó y confirma que la primera ejecución queda intacta.

| Estado | Prueba | Motivo |
|---|---|---|
| **Fallido** | `tests/test_pipeline_modelo.py::test_ensayo_de_oficina_sigue_dentro_de_la_tolerancia_de_la_referencia_manual` | **Defecto conocido de detección y seguimiento,** que se decidió conservar visible: la bajada de 4,68 s del clip de oficina no se cuenta. No se cambió el tramo ni la expectativa. |
| **Omitido** | `tests/test_pipeline_modelo.py`, la prueba que compara con los **pesos ajustados** del compañero | Esos pesos no están en esta máquina. |
| **Xfail** (fallo esperado) | `tests/test_cajas_encimadas.py::test_una_persona_con_tres_cajas_cuenta_un_cruce` | **Limitación conocida:** varias cajas encimadas sobre una persona cuentan un cruce cada una. |

## Demo principal: `prueba-bus` desde la página

Es el único video que muestra el flujo completo en una escena real de bus, con ambos sentidos y una referencia hecha por una persona.

**Preparado en la máquina de Álvaro:** el video está en `data\raw\prueba-bus.mp4` y la primera ejecución en `runs\panel\20261108-200805-374934`. Las dos carpetas están fuera de Git; en otra máquina no existen, y hay que copiarlas o procesar desde cero.

**Guion definitivo (unos 4 minutos):**

1. **«Archivo JSON o demo»:** qué hace el sistema. Mover el selector de segundos y ver cómo cambia la ocupación por parada.
2. **«Video nuevo»:** subir `prueba-bus.mp4`.
   - Mostrar la información del video (resolución, FPS, duración y hash).
   - Explicar las coordenadas: origen arriba a la izquierda; el recorte en el cuadro completo y la línea dentro del recorte.
   - Cargar la geometría usada: recorte X 0, Y 0, ancho 768, alto 432 (es el cuadro completo, ya viene así); línea X1 274, Y1 431, X2 467, Y2 242; interior arriba. Apretar Enter después de cada número. Debajo tiene que leerse «la línea va de (274, 431) a (467, 242)».
   - Mover la vista previa: no ejecuta el modelo.
3. **Procesar.** Hay dos acciones distintas, y no hay que presentar una como la otra:
   - **Mostrar el resultado guardado:** «Procesar video». Como esa configuración ya se procesó, la página avisa «No se repite» y muestra la **primera ejecución** (`20261108-200805-374934`) con el rótulo «Resultado guardado». **No es inferencia en vivo.**
   - **Procesar en vivo:** «Reprocesar en vivo para demostración». Vuelve a ejecutar el modelo con **el mismo video y la misma configuración** (sin mover la línea) y guarda una ejecución **aparte**, marcada como «repetición para demostración». La primera evaluación no se modifica.
     - El resultado aparece rotulado «Resultado procesado en vivo».
     - Tarda alrededor de 80 s en CPU: ese tiempo sirve para explicar la arquitectura (panel → API → `vision.pipeline` → YOLO + ByteTrack → regla de cruce → `/ocupacion`).
     - En la misma máquina debería dar los mismos eventos. Las métricas presentadas son las de la primera ejecución.
   - Recargar la página o mover controles no vuelve a procesar: se sigue mostrando el resultado guardado.
4. **Resultado:** en «Ejecución», elegir `20261108-200805-374934`, la primera evaluación. Si se reprocesó en vivo, la lista muestra primero la repetición. Mostrar el video anotado, la tabla de eventos y las descargas (JSON, video y configuración). Bajar a la ocupación.
5. **Errores medidos**, contra la referencia hecha a mano por Álvaro antes de procesar (12 cruces, tolerancia ±1 s):
   - **detectó los 12 cruces reales**, sin omisiones;
   - pero registró **24 eventos: 12 falsos** (4 subidas y 8 bajadas de más);
   - la ocupación neta da −8 en lugar de −4;
   - **causas observadas** al inspeccionar los 12 falsos en el video anotado (detalle en el README de la tarea 14):
     - **8** son una segunda o tercera caja sobre una persona ya contada, a veces una caja de grupo; cada caja tiene su propio ID y su propio cruce;
     - **1** es una de esas cajas, que primero «sube» y después «baja»;
     - **2** son un ID que salta a otra persona;
     - **1** es un segundo ID sobre la misma persona, sin poder distinguir si es otra caja o un cambio de ID;
   - un filtro para eso se probó y se descartó, porque borraba pasajeros reales.
6. **Otros resultados medidos,** para el contexto:
   - bus real de YouTube: 6 de 18 cruces;
   - PAMELA A: 10 de 28 bajadas;
   - Kaggle: 5 de 6 subidas, con 8 eventos falsos.

**Advertencias:**
- `prueba-bus` es un video de stock con marca de agua de iStock; antes de publicar capturas, revisar su licencia.
- Después de esa primera evaluación, el video se usó para desarrollo (tarea 14). **La evaluación válida es la primera**; lo posterior no es una validación independiente.

## Caso documentado: oficina

- **La demo de oficina sigue disponible:** clip `data\raw\oficina.mp4`, tramo 0–6 s.
- **Qué muestra:** cuenta la subida a 2,16 s, pero **omite la bajada de 4,68 s**.
- **Lo comprobado:** la bajada está dentro del tramo y del recorte, y cruza la línea. La confianza del detector cae a 0,02–0,09 justo en la puerta, el rastreador pierde a la persona y la regla no cuenta un ID que aparece del otro lado. Tampoco se cuenta con el video completo.

Detalle: `docs/casos-deteccion/oficina-bajada-omitida/README.md`.

## Limitaciones de la versión

- **Duplicados:** en `prueba-bus`, la mayoría de los falsos son cajas encimadas o de grupo, comprobado al inspeccionar cada uno. Los demás son saltos de ID y oscilaciones. En Kaggle no se inspeccionaron uno por uno.
- **Omisiones:** cuando la confianza del detector cae (oficina, PAMELA A).
- **Velocidad:** CPU, unos 9 a 14 cuadros por segundo, con un procesamiento a la vez.
- **Resultados distintos entre sistemas:** Linux, Windows y macOS pueden dar IDs y eventos algo distintos.
- **Docker:** la imagen no trae las librerías de visión, así que subir un video responde 503.
- **Espacio en disco:** los videos subidos quedan en `runs\videos\`, fuera de Git, y no se borran solos.

## Versionado

Commits autorizados por Álvaro en `integracion-video`, sin push:

| Commit | Contenido |
|---|---|
| `93406d7` | Pruebas independientes con Kaggle y PAMELA A (tarea 09) |
| `18e3efd` | Reproducción del ajuste en Windows (tarea 10) |
| `5c20575` | Detectores más grandes y prueba final con YouTube (tarea 11) |
| `70ac559` | Supresión temporal y trazabilidad (tarea 12) |
| `9af1680` | Video nuevo desde el panel y primera evaluación de `prueba-bus` (tarea 13) |
| este commit | Diagnóstico de duplicados, test xfail, caso de oficina, cierre y estado (tarea 14) |

**Line endings:** los archivos se versionaron sin convertirlos (`core.autocrlf=false`). Así se conservan byte a byte y coinciden los SHA-256 registrados de las referencias; por ejemplo, `youtube-bus-real-cruces.json` y `prueba-bus-cruces.json` tienen CRLF.

**Fuera de Git:**
- videos (`data/raw/`), pesos (`*.pt`), `runs/` (ejecuciones y videos subidos) y entornos;
- `.pytest-local-verificacion-20261108/`, una carpeta temporal de pytest que dejó la verificación de Codex: se puede borrar.
