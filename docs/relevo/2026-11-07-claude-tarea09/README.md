# Tarea 09 · Comparación de modelos y evaluación independiente · devolución de Claude (7 nov.)

Rama local `integracion-video` (HEAD `b511d91`), con los cambios de las tareas 08 y 09 **sin commit, push ni merge**. No se cambió el panel, la API, el detector, los umbrales ni las pruebas. No se guardaron pesos ni videos en Git. Los informes siguen aplazados.

## Evidencia 08 cerrada

La [devolución 08](../2026-11-07-claude-tarea08/README.md) ya incluye los resultados de Windows de la [revisión de Codex](../2026-11-07-claude-tarea08/revision-codex-windows.md):

- El worktree ya apuntaba a Windows y la reparación no cambió nada.
- Las pruebas de API pasan: 15 de 15.
- En visión, 84 aprobadas, 1 omitida y 1 fallida, la de la bajada omitida.
- El panel aceptó la ejecución `20261107-204212-090885`: 0, 1, 1 y 1 pasajeros a 0, 2,16, 4 y 6 s, con video reproducido.
- El gráfico pasó con 45 estados y 0 fallos.

Está separado lo que prueba la integración de lo que mide la calidad del conteo, que sigue fallando.

## 1. Comparación reproducible en el video completo

[`scripts/evaluar_oficina.py`](scripts/evaluar_oficina.py) reutiliza configuraciones, tramos, referencia y evaluador de `evaluation/comparar_oficina.py`, y escribe en otra carpeta: **no sobrescribe `evaluation/results/`**, que tiene las cifras de macOS.

- **Huellas:** antes de ejecutar comprueba el SHA-256 del clip, de `yolo11n.pt` y de los pesos ajustados. Una configuración sin pesos válidos queda «pendiente».
- **Dos ejecuciones por configuración:** 0–6 s con video anotado (en `runs/evaluacion/`, fuera de Git) y video completo sin video anotado, para medir FPS como en macOS.
- **Resultados:** `resumen.json` reúne eventos, configuración, tiempo, FPS, versiones, hashes, y TP, FP y FN y error de conteo por sentido y tramo.

```sh
python docs/relevo/2026-11-07-claude-tarea09/scripts/evaluar_oficina.py <SALIDA> [--ajustado <ruta.pt>]
```

### Resultados por entorno

Referencia `data/annotations/oficina-cruces.json` (10 subidas y 10 bajadas), tolerancia ±1 s. «Calibrado» significa `bytetrack-cenital.yaml`, `conf 0.05` y `confirmacion 2`. Cada celda es TP / FP / FN.

| Configuración | Entorno | 0–6 s subidas | 0–6 s bajadas | Completo subidas | Completo bajadas | Error de conteo (sub/baj) | FPS (completo) |
|---|---|---|---|---|---|---|---|
| Base, ByteTrack por defecto | Linux x86 (Claude) | 0/0/1 | 0/0/1 | 0/0/10 | 0/0/10 | 10 / 10 | 14,6 |
| Base calibrado | Linux x86 (Claude) | 1/0/0 | 0/0/1 | 7/0/3 | 4/0/6 | 3 / 6 | 14,4 |
| Base, ByteTrack por defecto | Windows (Ryzen 5 7535HS) | 0/0/1 | 0/0/1 | 0/0/10 | 0/0/10 | 10 / 10 | 29,0 |
| Base calibrado | Windows (Ryzen 5 7535HS) | 1/0/0 | 0/0/1 | 7/0/3 | 4/0/6 | 3 / 6 | 28,7 |
| Ajustado, por defecto o calibrado | Windows | **pendiente: faltan los pesos** | | | | | |
| *Base calibrado, guardado* | *macOS M4 (compañero)* | *1/0/0* | *1/0/0* | *—* | *—* | *12 de 20 en total* | *41,0* |

En Linux, las omisiones del base calibrado en el video completo son las subidas de 7,2, 11,88 y 43,8 s y las bajadas de 4,68, 9,6, 14,52, 19,92, 30,36 y 45,96 s, sin eventos extra. El detalle está en [`linux/`](linux/).

En macOS, según `evaluation/results/oficina-comparacion.json`, el mismo sistema base calibrado da 12 de 20 y el ajustado con ByteTrack por defecto, 20 de 20. Esas cifras son del compañero y **no se reprodujeron aquí**.

**Windows: ejecutado por Álvaro el 7 nov.** El entorno es Windows 11 10.0.26200, AMD Ryzen 5 7535HS, Python 3.12.10, ultralytics 8.4.203, torch 2.15.0, opencv-python 5.0.0.93 y lap 0.5.14, y el clip y `yolo11n.pt` tienen los SHA-256 documentados. El detalle está en [`windows/`](windows/).

**Windows y Linux x86 dan exactamente los mismos eventos** en las cuatro ejecuciones: base calibrado da 11 eventos idénticos en tiempo y sentido en el video completo, y solo la subida de 2,16 s en 0–6 s; base por defecto, ninguno. Las omisiones son las mismas:

- Subidas de 7,2, 11,88 y 43,8 s.
- Bajadas de 4,68, 9,6, 14,52, 19,92, 30,36 y 45,96 s.

En macOS, el mismo sistema base calibrado da 12 de 20, con eventos distintos. Que la diferencia esté en la plataforma sigue siendo una hipótesis, pero ahora se limita a macOS frente a x86. Los videos anotados de 0–6 s quedaron en `runs\evaluacion\windows-amd64\`, fuera de Git.

Comando, desde `TpFinal\.worktrees\integracion-video`:

```powershell
$env:PYTHONUTF8 = '1'
.\.venv\Scripts\python.exe docs\relevo\2026-11-07-claude-tarea09\scripts\evaluar_oficina.py docs\relevo\2026-11-07-claude-tarea09\windows
```

Tarda unos 4 minutos. Si los pesos ajustados están en `runs\oficina-ajuste\oficina-ajustado.pt` con el SHA-256 documentado, también ejecuta las dos configuraciones del ajustado; en otra ruta, se agrega `--ajustado <ruta>`. Ajustado con ByteTrack por defecto contra base calibrado compara **sistemas completos** (detector y rastreador), no solo detectores. El ajustado calibrado aísla el efecto del detector con el mismo rastreador.

## 2. Referencia del video de oficina

[`referencia-oficina.md`](referencia-oficina.md) explica cómo se obtuvieron las dos referencias y qué revisión humana falta:

- La manual de 0–6 s es aproximada.
- Los 20 cruces salen de cajas propuestas por resta de fondo y revisadas por Claude.
- No está documentado el origen de los cruces de 2,16 y 4,68 s, porque no hay cajas antes de 6 s.

Este video **no es una evaluación independiente**.

## 3. Ficha para una grabación nueva

[`ficha-grabacion-independiente.md`](ficha-grabacion-independiente.md) cubre:

- Consentimiento, cámara fija arriba de la puerta y una toma continua con los dos sentidos.
- Pausas sin cruces y, si es viable, dos personas y oclusiones.
- Registro de duración, FPS, resolución y orientación, y anotación de instantes por otra persona.
- Toda la toma reservada como prueba, con TP, FP y FN por sentido.

## 4. PCDS

Sigue bloqueado. No se repitieron descargas ni se cambió de dataset; ver la [propuesta de la tarea 08](../2026-11-07-claude-tarea08/propuesta-evaluacion-pcds.md).

## Pesos ajustados

**No están en esta máquina.** `runs/` del worktree solo contiene `panel/`. No se descargaron pesos de origen desconocido ni se reentrenó. El pedido está en [`mensaje-companero.md`](mensaje-companero.md), listo para copiar.

## Recomendación con el alcance demostrado

**No hay base para cambiar la configuración de la API.**

- **Base calibrado:** en Linux y Windows omite la bajada del ensayo. En el video completo cuenta 11 de 20 en los dos entornos, con 9 omisiones (6 de ellas bajadas) y 0 eventos extra.
- **Ajustado:** su 20 de 20 es de macOS, en la misma grabación con la que se entrenó, y no se reprodujo.
- **Detector de cabezas:** sus 19 de 20 son de Linux, en la misma grabación, sin licencia y con TensorFlow.

Ninguna de estas cifras muestra generalización. Hace falta la comparación en Windows con los pesos ajustados y, sobre todo, la grabación independiente.

## Archivos cambiados en esta tarea (sin commit)

- `docs/relevo/2026-11-07-claude-tarea08/README.md`: resultados de Windows.
- `resumen.md` y `docs/tareas/claude/README.md` (índice).
- Nuevos: `docs/tareas/claude/09-evaluacion-windows.md` (copia de la ficha) y `docs/relevo/2026-11-07-claude-tarea09/`, con script, resultados de Linux, referencia, ficha de grabación y mensaje.

## Pendientes

1. ~~Windows, modelo base~~: hecho, con eventos idénticos a Linux.
2. **Pesos ajustados:** que el compañero los entregue con hash y configuración, y repetir el comando con `--ajustado`.
3. **Medición de confianza en macOS** del compañero, para confirmar o descartar la hipótesis de la plataforma.
4. **Revisión humana** de `oficina-cruces.json`.
5. **Grabación independiente** según la ficha; es la única forma de evaluar generalización.
6. **La prueba `test_ensayo_de_oficina_…` sigue fallando:** es la omisión del modelo y se mantiene visible.
