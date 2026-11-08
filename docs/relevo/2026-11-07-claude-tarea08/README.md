# Tarea 08 · Cierre de integración en Windows · devolución de Claude (7 nov.)

Rama local `integracion-video`, en `.worktrees/integracion-video`, sobre `b511d91`. Los cambios quedan **sin commit ni push** para revisión. No se tocó `main` ni la carpeta principal: siguen en `tareas-03-04-panel-informe` con los cambios del informe. Docker conserva su alcance (JSON; la visión se arranca a mano). No se cambió el detector ni se agregó TensorFlow, y los informes académicos no se editaron.

## Historial verificado

Desde la máquina virtual del equipo de Álvaro se verificó lo siguiente:

- `git fsck --connectivity-only` no reporta errores.
- Existen los commits `b511d91` (caso de detección), `d2cf58d` (integración), `e85fb75` (merge `--no-ff` de `d0a658a` con `origin/vision` en `dd5a19a`), `dd5a19a` y `d0a658a`.
- Ninguno se publicó.

La devolución 07 decía «sin commit»; se corrigió para reflejar estos commits locales.

**Vínculo del worktree.** `.worktrees/integracion-video/.git` y `.git/worktrees/integracion-video/gitdir` apuntan a rutas `/sessions/...` de Linux, porque el worktree se creó desde esa máquina virtual. La reparación es el primer paso de [`verificar-windows.ps1`](verificar-windows.ps1): `git worktree repair` desde el repositorio principal, sin prune, reset ni borrados. **Resultado en Windows** ([`windows/01-worktree.txt`](windows/01-worktree.txt)): al ejecutarse, los dos archivos ya apuntaban a rutas de Windows y la reparación no cambió nada. La rama es `integracion-video`, el HEAD `b511d91` y los cambios de esta tarea siguen sin commit. La carpeta principal sigue en `tareas-03-04-panel-informe` con sus modificaciones.

## 1. Consultar todo el tramo procesado (`ui/app.py`)

- Con la fuente de video, el selector suma el final del tramo, tomado de la configuración de la ejecución.
- Usa la misma base que `tiempo_s`, segundos desde el inicio del tramo: `fin − inicio`. Sin `--fin`, toma `cuadros / fps`.
- Los JSON cargados no declaran duración y conservan la lógica anterior.
- No se agregan ni se reemplazan eventos.

## 2. Publicar solo ejecuciones terminadas (`api/main.py`)

- Cada ejecución lleva una marca `completa`, que se escribe al final y solo si se cumplen tres cosas: el pipeline terminó con código 0, `prediccion.json` y `prediccion.config.json` se leen, y `anotado.webm` existe y no está vacío.
- `GET /procesamientos`, `GET /procesamientos/{id}` y `/video` exigen esa marca. Una ejecución en curso, fallida, cortada por tiempo o ilegible no se lista y da 404.
- `registro.txt` se conserva siempre, también tras un timeout.
- Las ejecuciones anteriores a este cambio no tenían la marca. Se recuperaron solo las que se pudieron validar, con [`scripts/recuperar_ejecuciones.py`](scripts/recuperar_ejecuciones.py), que exige lo siguiente:
  - las mismas condiciones que la API;
  - un recorrido que cumpla el contrato de `POST /ocupacion`;
  - un registro con el final normal del pipeline y sin `Traceback`;
  - un video que se decodifique con los 150 cuadros que declara la configuración.

  Cumplieron las tres: `20261107-192800-383466` y `20261107-193104-352371`, de Linux, y `20261107-194239-470039`, la manual de Álvaro en Windows. Ahora se listan, con consulta y video en 200. Los controles negativos (registro con `Traceback`, video truncado y JSON roto) se rechazan. Ver [`recuperacion-ejecuciones.txt`](recuperacion-ejecuciones.txt).

**Pruebas** (`tests/test_procesamientos.py`): éxito, fallo después de escribir archivos, timeout con salida parcial y resultado ilegible. Con la versión anterior de `listar_procesamientos`, fallan 3 de las 8 pruebas del archivo.

## 3. Verificación

### Linux: contenedor de Claude, Intel Xeon x86_64, Python 3.12.3, ultralytics 8.4.203, torch 2.15.0, opencv-python 5.0.0.93

| Comprobación | Resultado | Evidencia |
|---|---|---|
| `pytest tests -v` | 99 aprobadas, 1 omitida (detector ajustado, sin pesos) y 1 fallida: `test_ensayo_de_oficina_…` (bajada omitida; ver abajo). | [`linux/pytest.txt`](linux/pytest.txt) |
| Panel: procesar, video y tramo completo ([`scripts/verificar_video.py`](scripts/verificar_video.py)) | **Exit 0, sin fallos.** Ejecución `20261107-202407-103973`, evento 2,16 s subida. Video sin error, 6 s, 222×176, avanzó 1,5 s. Selector de 0 a 6 s: a 0, 2,16, 4 y 6 s, indicadores y tabla dan 0, 1, 1 y 1 pasajeros (0, 5, 5 y 5 %), iguales a lo derivado de los eventos. | [`linux/video/`](linux/video/) |
| Control negativo: el mismo script contra el panel de `b511d91` | Exit 1: «el selector no ofrece los instantes [4.0, 6.0]» y «termina en 2.16 s». | [`linux/control-panel-anterior/`](linux/control-panel-anterior/) |
| Ejecución sin eventos (sintética, carga inicial 3, copia temporal en `runs/panel`, borrada después) | Selector hasta 6 s; 3 pasajeros (15 %). | [`linux/sin-eventos.json`](linux/sin-eventos.json) |
| Carga de JSON y gráfico, 45 estados | **0 fallos, 32 transiciones.** | [`linux/grafico/`](linux/grafico/) |

**Cambios en los scripts de verificación:**

- [`scripts/verificar_video.py`](scripts/verificar_video.py) amplía el de la tarea 07. Ahora acepta o rechaza: deriva lo esperado de los eventos de la propia ejecución (`GET /procesamientos/<id>`), nunca de la referencia manual, y comprueba la reproducción real del video. Guarda la respuesta de la API.
- [`scripts/verificar_grafico.py`](scripts/verificar_grafico.py) es el de la tarea 07 con una espera más: los indicadores pueden aparecer antes que el selector de archivo. Sin esa espera, la primera carga fallaba con «Cannot set properties of null».

### Windows: máquina de defensa

Desde el chat no puedo escribir en terminales de Windows, así que la verificación queda en un script. Álvaro lo ejecuta y el resultado se guarda en `windows/`:

```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\Alvaro\Desktop\Facultad\4to\IA\TpFinal\.worktrees\integracion-video\docs\relevo\2026-11-07-claude-tarea08\verificar-windows.ps1
```

El script hace lo siguiente:

1. Repara el worktree y registra rama, HEAD y estado.
2. Copia la ficha 08 al worktree.
3. Registra el sistema, el procesador, las versiones del `.venv` existente y el tamaño y SHA-256 del clip y los pesos.
4. Ejecuta por separado las pruebas de API y las de visión.
5. Lista qué servicios ocupan los puertos 8000, 8001, 8010, 8501, 8502 y 8511, con su línea de comando, y elige puertos libres.
6. Instala Playwright en el `.venv` solo si falta (hoy falta).
7. Levanta la API y el panel del worktree.
8. Ejecuta los dos verificadores y detiene solo los procesos que inició.

**Resultado:** ejecutado por Codex el 7 nov. a las 20:41; ver su [revisión](revision-codex-windows.md).

- **Entorno:** Windows 11 IoT Enterprise LTSC 10.0.26200, AMD Ryzen 5 7535HS, 15,2 GB de RAM, Python 3.12.10, ultralytics 8.4.203, torch 2.15.0, opencv-python 5.0.0.93 y playwright 1.64.1. El clip y `yolo11n.pt` tienen los SHA-256 documentados ([`windows/02-entorno.txt`](windows/02-entorno.txt)).
- **Puertos:** ningún servicio ocupaba los puertos revisados. La verificación usó la API en 8010 y el panel en 8511, y al terminar detuvo solo esos procesos.

| Comprobación (Windows) | Resultado | Evidencia |
|---|---|---|
| Pruebas de API | 15 aprobadas | [`windows/03-pytest-api.txt`](windows/03-pytest-api.txt) |
| Pruebas de visión | 84 aprobadas, 1 omitida (sin pesos ajustados) y **1 fallida**: `test_ensayo_de_oficina_…`, por la bajada omitida del modelo base | [`windows/04-pytest-vision.txt`](windows/04-pytest-vision.txt) |
| Panel: procesar, video y tramo completo | **Exit 0, sin fallos.** Ejecución `20261107-204212-090885`, 150 cuadros en 7,644 s (19,62 FPS, con video anotado), una subida a 2,16 s. Video de 6 s y 222×176, sin error, avanzó 1,52 s. A 0, 2,16, 4 y 6 s: 0, 1, 1 y 1 pasajeros, iguales a lo derivado de los eventos. | [`windows/video/`](windows/video/) |
| Carga de JSON y gráfico, 45 estados | **0 fallos, 32 transiciones.** | [`windows/grafico/`](windows/grafico/), [`windows/08-verificar-grafico.txt`](windows/08-verificar-grafico.txt) |

**En total: 99 aprobadas, 1 omitida y 1 fallida. La batería no está completa en verde.** Estas comprobaciones prueban la **integración**: el panel y la API muestran y calculan correctamente lo que predice el modelo. **No miden la calidad del conteo:** la bajada sigue sin detectarse. El caso sintético sin eventos solo se comprobó en Linux. La ejecución manual previa de Álvaro, `20261107-194239-470039`, dio la misma predicción.

## 4. Omisión de la bajada: coordinación con visión

- **Pedido al compañero:** [`pedido-vision.md`](pedido-vision.md). Incluye los pesos ajustados con hash, configuración y versiones, y la medición de confianza en macOS con el mismo clip. No se envió nada.
- **Propuesta de evaluación:** [`propuesta-evaluacion-pcds.md`](propuesta-evaluacion-pcds.md). PCDS como candidato, con su descarga bloqueada desde estos entornos y una grabación nueva independiente como alternativa.
- **Comparación de repositorios:** [`docs/casos-deteccion/comparacion-repositorios/`](../../casos-deteccion/comparacion-repositorios/README.md), con URLs, commits, scripts propios, versiones, hashes y salidas por cuadro y por evento. Lo medido está separado de lo que afirman terceros. Se ampliaron las mediciones sobre continuidad de IDs, eventos finales y detecciones fuera de las cajas anotadas. Es un experimento y no una recomendación de reemplazo.
- **Caso de la bajada:** en [`oficina-bajada-omitida/README.md`](../../casos-deteccion/oficina-bajada-omitida/README.md) se rebajaron a hipótesis dos afirmaciones que no estaban demostradas: la causa vinculada a COCO y la explicación por la diferencia entre Mac y x86.

La omisión sigue visible como limitación: la prueba del compañero falla y no se debilitó ni se omitió. El panel no completa la bajada.

## Archivos cambiados (sin commit)

- `ui/app.py`, `api/main.py` y `tests/test_procesamientos.py`.
- `resumen.md`, `docs/tareas/claude/README.md` (índice), `docs/tareas/claude/08-cierre-integracion-windows.md` (la copia la hace el script tras la reparación).
- `docs/relevo/2026-11-07-claude-tarea07/README.md` (frase de commits).
- `docs/casos-deteccion/oficina-bajada-omitida/README.md` (hipótesis).
- Nuevos: `docs/casos-deteccion/comparacion-repositorios/` y `docs/relevo/2026-11-07-claude-tarea08/`.

## Pendientes

**Integración**

1. ~~Ejecutar `verificar-windows.ps1`~~. Hecho por Codex: la integración queda aceptada para la demo fija de 0–6 s.
2. Revisar los cambios y decidir el commit.

**Detector**

1. Los pesos ajustados y la medición en macOS (pedido a visión). Con los pesos, comparar base y ajustado en Windows.
2. La evaluación independiente: PCDS, bloqueado, o una grabación nueva.
3. La prueba `test_ensayo_de_oficina_…` sigue fallando en Linux y en Windows. Es la omisión del modelo, no un fallo de la integración.

## Actualización de Codex · verificación Windows completada
Ver [revision-codex-windows.md](revision-codex-windows.md): 15 pruebas API aprobadas; visión 84 aprobadas, 1 omitida y 1 fallida por bajada omitida. Video aceptado, selector hasta 6 s y gráfico de 45 estados sin fallos. Este bloque reemplaza el estado pendiente de Windows anterior. Los cambios siguen sin commit.

## Revisión previa al commit (7 nov., 22 h)

`pytest tests -v` en Linux da **99 aprobadas, 1 omitida y 1 fallida** ([`pytest-previo-al-commit.txt`](pytest-previo-al-commit.txt)):

- **Omitida:** `test_detector_ajustado_cuenta_el_ensayo_con_el_rastreador_por_defecto`, porque faltan los pesos ajustados del compañero.
- **Fallida:** `test_ensayo_de_oficina_sigue_dentro_de_la_tolerancia_de_la_referencia_manual`. El modelo base predice `['subida']` frente a `['subida', 'bajada']` de la referencia manual: la bajada omitida.

La prueba fallida queda **sin modificar ni marcar como esperada**. Es un fallo real del detector base en x86 (Linux y Windows), no de la integración. Se cierra cuando visión entregue un modelo o una configuración que cuente esa bajada sin ajustarla sobre este mismo clip.
