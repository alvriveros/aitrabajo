# Para Codex · estado de `integracion-video` tras las tareas 08 y 09 (Claude, 7 nov. 2026)

## Dónde está

- **Worktree:** `TpFinal\.worktrees\integracion-video`, rama local `integracion-video`, HEAD `b511d91`.
  - Historial: `e85fb75` es el merge `--no-ff` de `d0a658a` con `origin/vision` en `dd5a19a`; `d2cf58d` es la integración y `b511d91` el caso de detección.
- **Sin commit, push ni merge:** todo lo de las tareas 08 y 09. `main` no se tocó.
- **Carpeta principal:** sigue en `tareas-03-04-panel-informe`, con los cambios del informe sin tocar.
- **Fuera de Git:** pesos, clips y videos están en `data/raw/`, `yolo11n.pt` y `runs/`.

## Cambios pendientes de revisión (`git status`)

| Archivo | Tarea | Qué cambió |
|---|---|---|
| `ui/app.py` | 08 | Con la fuente de video, el selector incluye el final del tramo (`fin − inicio` de la configuración; sin `--fin`, `cuadros / fps`). Los JSON no cambian. |
| `api/main.py` | 08 | Solo se publican las ejecuciones con la marca `completa`. Se escribe tras código 0, `prediccion.json` y `.config.json` legibles y un `anotado.webm` no vacío. `registro.txt` se conserva también tras un timeout. |
| `tests/test_procesamientos.py` | 08 | Casos de éxito, fallo después de escribir archivos, timeout y resultado ilegible. Con la versión anterior de `listar_procesamientos`, fallan 3 de las 8 pruebas. |
| `docs/casos-deteccion/oficina-bajada-omitida/README.md` | 08 | Las explicaciones por COCO y por Mac contra x86 pasaron a hipótesis. |
| `docs/casos-deteccion/comparacion-repositorios/` | 08 | Experimento con los cuatro repositorios externos: commits, hashes, scripts propios, salidas por cuadro y por evento. Separa lo medido de lo que afirman terceros. |
| `docs/relevo/2026-11-07-claude-tarea07/README.md` | 08 | La frase «sin commit» se corrigió según el historial. |
| `docs/relevo/2026-11-07-claude-tarea08/` | 08 | Devolución completa con los resultados de Windows y tu revisión (se conserva tu bloque). Incluye scripts de verificación, `verificar-windows.ps1`, pedido a visión y propuesta PCDS. |
| `docs/relevo/2026-11-07-claude-tarea09/` | 09 | Script de evaluación, resultados de Linux y Windows, revisión de la referencia, ficha de grabación y mensaje al compañero. |
| `resumen.md`, `docs/tareas/claude/README.md` | 08–09 | Estado actual. Se mantienen tus agregados. |
| `docs/tareas/claude/08-…md`, `09-…md` | — | Copias de las fichas. |

**No se cambió:** el detector de la API, los umbrales, el rastreador, las pruebas existentes, Docker, el panel (ninguna función nueva en la 09) ni los informes. No se agregó TensorFlow ni el SSD externo.

## Tarea 09: lo hecho

### 1. Comparación reproducible del modelo base en el video completo

- **Script:** `docs/relevo/2026-11-07-claude-tarea09/scripts/evaluar_oficina.py`.
  - Reutiliza `CONFIGURACIONES`, `TRAMOS`, `REFERENCIA` y el evaluador de `evaluation/comparar_oficina.py`.
  - Escribe en otra carpeta: **no sobrescribe `evaluation/results/`**, que tiene las cifras de macOS.
  - Antes de ejecutar comprueba el SHA-256 del clip, de `yolo11n.pt` y de los pesos ajustados (`783d16c0…`). Una configuración sin pesos válidos queda «pendiente».
  - Hace dos corridas por configuración: 0–6 s con video anotado (en `runs/evaluacion/`) y video completo sin video anotado.
  - Guarda TP, FP y FN y error de conteo por sentido y tramo, eventos, configuración, tiempo, FPS, versiones y hashes en `resumen.json`.
- **Comando**, desde la raíz del worktree:
  ```powershell
  $env:PYTHONUTF8 = '1'
  .\.venv\Scripts\python.exe docs\relevo\2026-11-07-claude-tarea09\scripts\evaluar_oficina.py docs\relevo\2026-11-07-claude-tarea09\windows [--ajustado <ruta.pt>]
  ```

### Resultados

Referencia `data/annotations/oficina-cruces.json` (10 subidas y 10 bajadas), tolerancia ±1 s. Cada celda es TP/FP/FN.

| Configuración | Entorno | 0–6 subidas | 0–6 bajadas | Completo subidas | Completo bajadas | FPS (completo) |
|---|---|---|---|---|---|---|
| Base, ByteTrack por defecto | Linux x86 (contenedor de Claude) | 0/0/1 | 0/0/1 | 0/0/10 | 0/0/10 | 14,6 |
| Base calibrado | Linux x86 | 1/0/0 | 0/0/1 | 7/0/3 | 4/0/6 | 14,4 |
| Base, ByteTrack por defecto | Windows 11, Ryzen 5 7535HS (Álvaro) | 0/0/1 | 0/0/1 | 0/0/10 | 0/0/10 | 29,0 |
| Base calibrado | Windows 11, Ryzen 5 7535HS | 1/0/0 | 0/0/1 | 7/0/3 | 4/0/6 | 28,7 |
| Ajustado (por defecto y calibrado) | — | pendiente: faltan los pesos | | | | |
| *Base calibrado, guardado* | *macOS M4 (compañero)* | *1/0/0* | *1/0/0* | *12 de 20 en total* | | *41,0* |

- **Windows y Linux x86 dan eventos idénticos** en tiempo y sentido en las cuatro ejecuciones; comparado archivo por archivo en `linux/eventos/` y `windows/eventos/`.
- **Omisiones del base calibrado:** subidas de 7,2, 11,88 y 43,8 s; bajadas de 4,68, 9,6, 14,52, 19,92, 30,36 y 45,96 s. No hay eventos extra.
- **macOS** da eventos distintos. La diferencia por plataforma sigue siendo una **hipótesis**, ahora acotada a macOS frente a x86.
- **Versiones en Windows:** Python 3.12.10, ultralytics 8.4.203, torch 2.15.0, opencv-python 5.0.0.93 y lap 0.5.14. El clip y `yolo11n.pt` tienen los SHA-256 documentados.

### 2. Referencia del video de oficina

`referencia-oficina.md`:

- **La manual de 0–6 s es aproximada,** redondeada al segundo.
- **Los 20 cruces de `oficina-cruces.json`** salen del centro de cajas propuestas por resta de fondo y revisadas por Claude, no por una persona. Los totales coinciden con el contador del video (10 y 10).
- **No está documentado el origen de los cruces de 2,16 y 4,68 s,** porque `oficina-cajas.json` no tiene cuadros antes de 6 s.
- **No es una evaluación independiente:** el video se usó para calibrar el rastreador y entrenar el ajustado.
- **Pasos de revisión humana:** están enumerados en el mismo archivo.

### 3. Ficha de grabación independiente

`ficha-grabacion-independiente.md`:

- **Antes de grabar:** consentimiento, cámara fija arriba de la puerta y registro de duración, FPS, resolución y orientación interior/exterior.
- **La toma:** continua, con los dos sentidos y pausas sin cruces, y si es viable, dos personas y oclusiones.
- **Anotación:** una persona que no ejecutó el sistema marca los instantes, y otra revisa una muestra.
- **Uso:** toda la toma queda como prueba, sin repartir fragmentos con el entrenamiento. Se miden TP, FP y FN por sentido, no solo el saldo.

### 4. Otros

- **PCDS** sigue bloqueado; no se repitieron descargas ni se cambió de dataset.
- **Pesos ajustados:** no están en la máquina (`runs/` solo tiene `panel/` y `evaluacion/`). No se descargaron ni se reentrenaron. El mensaje para el compañero está listo en `mensaje-companero.md`, sin enviar.
- **El compañero todavía no respondió.** Se le planteó a Álvaro reentrenar con `vision.train` como opción, rotulándolo como «ajustado reproducido» con su propio hash. **No se hizo:** la tarea 09 dice no reentrenar por defecto, y Álvaro aún no decidió.

## Recomendación con el alcance demostrado

**No cambiar la configuración de la API.**

- **Base calibrado:** cuenta 11 de 20 en el video completo, con 0 eventos extra, en Linux y Windows, y omite la bajada del ensayo.
- **Ajustado:** su 20 de 20 es de macOS, en la misma grabación con la que se entrenó, y no se reprodujo.
- **Detector de cabezas:** sus 19 de 20 son de Linux, en una sola grabación, sin licencia y con TensorFlow.

Ninguna cifra muestra generalización.

## Pruebas: estado conocido

- **API:** 15/15 en Windows y Linux.
- **Visión:** 84 aprobadas, 1 omitida (sin pesos ajustados) y **1 fallida**, `test_ensayo_de_oficina_sigue_dentro_de_la_tolerancia_de_la_referencia_manual`, por la bajada omitida del modelo base. No se debilitó ni se omitió.
- **Panel:** `verificar_video.py` sale con exit 0 en Windows (ejecución `20261107-204212-090885`), con 0, 1, 1 y 1 pasajeros a 0, 2,16, 4 y 6 s. El gráfico pasa con 45 estados y 0 fallos.

## Para revisar en particular

1. **Ejecuciones previas:** se recuperaron las tres que se pudieron validar con `docs/relevo/2026-11-07-claude-tarea08/scripts/recuperar_ejecuciones.py`. Ver la devolución 08.
2. **Las rutas absolutas del contenedor son solo procedencia.** `evaluar_oficina.py` se probó en Linux y Windows; los `"comando"` de los `.config.json` de Linux incluyen rutas del contenedor.
3. **`verificar_grafico.py` de la tarea 08 tiene una espera más.** Es la del 07 con una espera adicional del selector de archivo, que en Linux hacía fallar la primera carga.
4. **Dónde mirar los números:** `docs/relevo/2026-11-07-claude-tarea09/README.md` y `windows/resumen.json`.

## Pendientes concretos

1. **Pesos ajustados del compañero,** con hash, commit, comando de entrenamiento, configuración y versiones. Después, repetir `evaluar_oficina.py --ajustado <ruta>` en Windows.
2. **Medición de confianza en macOS** con `medir_confianza.py`, para confirmar o descartar la hipótesis de plataforma.
3. **Revisión humana** de `oficina-cruces.json` y del origen de 2,16 y 4,68 s.
4. **Grabación independiente** según la ficha, y una sola evaluación de prueba.
5. **Decisión de Álvaro** sobre reentrenar el ajustado o dejarlo pendiente.
6. **Revisión y commit** de las tareas 08 y 09.
7. **Informes:** aplazados; el cierre interno es el domingo 8 a las 18:00.
