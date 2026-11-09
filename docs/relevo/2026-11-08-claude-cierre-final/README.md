# Cierre final · 8–9 nov. (Claude)

Rama `cierre-final`, creada desde `integracion-video` (`24d873d`). `integracion-video` queda intacta como respaldo. No se hizo push ni merge.

- [`matriz.md`](matriz.md): matriz de requisitos con evidencia.
- [`experimentos.py`](experimentos.py): arnés de los cambios acotados; resultados en [`resultados/`](resultados/).

## Qué cambió

| Commit | Cambio | Prueba |
|---|---|---|
| `a781402` | Recorrido simulado de 8 paradas (`docs/demo/recorrido-linea.json`), con selector en el panel | `test_recorrido_simulado_de_la_linea_…` |
| `9814abb` | **Procesamiento progresivo:** `--progreso` y `--ritmo-real` en el pipeline; API en segundo plano con estado, cancelación y procesamiento actual; panel con sondeo cada 1 s, cancelación y retomar tras recargar; medición por etapas y de latencia | `test_estado_progresivo_y_cancelacion`, `test_ritmo_real_…`, `test_progreso_…` y `test_procesar_mide_…` |
| `09e6f39` | El test del detector ajustado acepta los pesos reproducidos en Windows (antes se omitía) | Pasa en Linux |
| `405d523` | Docker con visión en CPU, pesos en la imagen, volúmenes y healthchecks | **Verificado por Álvaro en Windows** (ver «Docker en Windows») |
| Commit de documentación | Matriz, experimentos, `data/README.md`, README, informe y guion | — |

## Línea base reproducible

Contenedor Linux de Claude: 2 núcleos, CPU, Python 3.13, torch 2.15.0, ultralytics 8.4.203 y opencv 5.0.0. En esas condiciones, la configuración de la API reproduce **exactamente** las cifras registradas en Windows:

| Escena | TP/FP/FN | Registro previo |
|---|---|---|
| `prueba-bus` | 12/12/0 | Tarea 13, Windows |
| Oficina | 11/0/9 | Tarea 10 |
| Kaggle | 5/8/1 | Tarea 11, Linux |
| PAMELA A | 10/1/18 | Tareas 09–11 |

## Cambios acotados (un cambio por vez)

En las tres escenas de selección se suman los errores (FN + FP). `prueba-bus` es desarrollo desde la tarea 14.

| Config | Oficina | Kaggle | PAMELA A | **Selección** | `prueba-bus` (desarrollo) |
|---|---|---|---|---|---|
| `base` (API) | 11/0/9 | 5/8/1 | 10/1/18 | **37** | 12/12/0 |
| `iou05` (NMS con IoU 0,5) | 11/0/9 | 5/5/1 | 9/3/19 | **37** | 12/8/0 |
| `salto2` (1 de cada 2 cuadros) | 5/1/15 | 5/6/1 | 10/1/18 | **42** | 12/8/0 |
| `salto3` (1 de cada 3 cuadros) | 2/0/18 | 4/4/2 | 7/1/21 | **47** | 11/3/1 |

**Decisiones:**

- **`iou05` no se adopta.** El total de selección no mejora, y en PAMELA hay una regresión: una bajada omitida más y dos falsos.
- **La mejora en `prueba-bus` no cuenta,** porque ese video ya es de desarrollo.
- **Sin corrección robusta,** se conserva la API tal como está. **Las cajas duplicadas siguen pendientes.**
- **Saltar cuadros empeora el conteo,** sobre todo en oficina, con cruces rápidos.

## Tiempo real

Se midió en el mismo contenedor, con el CLI de la API y `--ritmo-real`. Los resultados están en [`resultados/ritmo-real/`](resultados/ritmo-real/).

| Video | Cuadros procesados | Latencia media / p95 / máx. | Primer / último décimo | Duración: video → ejecución | Conteo |
|---|---|---|---|---|---|
| `prueba-bus`, 768×432, con video anotado | 209 de 686 (30 %) | 148 / 180 / 1298 ms | 206 / 129 ms | 27,4 s → 27,5 s | 12/2/0 (desarrollo) |
| Oficina, 222×176, con video anotado | 543 de 1316 (41 %) | 116 / 141 / 1243 ms | 136 / 123 ms | 52,6 s → 52,7 s | **4/2/16**, frente a 11/0/9 sin ritmo real |

- **La latencia no crece:** el último décimo es menor o igual que el primero. La máxima corresponde al primer cuadro, mientras el modelo carga.
- **La calidad no se sostiene en CPU:** en oficina se pierden 7 cruces más. El 12/2/0 de `prueba-bus` depende de qué cuadros se descartan, que a su vez depende de la velocidad del equipo. Además, ese video es de desarrollo: no es evidencia de mejora.
- **Etapas,** en ms por cuadro, sin ritmo real:
  - detección y seguimiento: 70–90;
  - lectura: menos de 3;
  - regla: menos de 0,1;
  - entrega: menos de 1 sin video anotado y unos 50 al codificar VP8 a 768×432.
- **GPU:** en la RTX 2050, `yolo11n` procesó 65,9 FPS con video anotado (tarea 11).

**Falta medir el ritmo real en esa GPU.** Es lo que cierra el criterio de aceptación en la máquina de defensa.

## Prueba de extremo a extremo (HTTP, `prueba-bus`)

Con la API en ese contenedor. El script es [`e2e_api.py`](e2e_api.py) y su salida, [`resultados/e2e-api.txt`](resultados/e2e-api.txt).

- **Inicio:** la subida responde 201 y el procesamiento, 202 en 0,00 s. Un segundo pedido recibe 409, y `/procesamientos/actual` devuelve el id.
- **Ocupación durante la ejecución** (capacidad 30, carga inicial 20):

  | Tiempo de ejecución | Video procesado | Pasajeros | Ocupación |
  |---|---|---|---|
  | 4 s | 0,4 s | 20 | 66,7 % |
  | 28 s | 9 s | 17 | 56,7 % |
  | 52 s | 17 s | 10 | 33,3 % |
  | 76 s | 26 s | 14 | 46,7 % |

- **Resultado final:** 24 eventos (igual que la primera evaluación) a 8,85 FPS, con latencia media de 112 ms. Repetir sin pedirlo da 409 con el id de la ejecución anterior.
- **Cancelación:** responde 202, el estado queda en `cancelado` y la ejecución no se publica.

**Panel** (`streamlit.testing.AppTest`):

- la línea de 8 paradas da 35, 55, 75, **105**, 97,5, 75, 55 y 0 %;
- la demo de oficina mostró «Procesando en vivo» y, al terminar, quedó elegida la ejecución recién hecha.

**No se probó:** la subida de archivos desde el navegador. `AppTest` no la soporta, y no había un navegador que llegara al contenedor. Queda para Álvaro.

## Docker en Windows (Álvaro, 8 nov., 23:24)

**Arranque:** `docker compose up --build -d` dejó `api` y `panel` en `healthy`. `openapi.json` respondió 200 y `_stcore/health`, `ok`.

**Procesamiento en el contenedor:** desde el panel, `prueba-bus` con ritmo real. Es la ejecución `20261109-022232-332657`, copiada en [`resultados/docker-windows/`](resultados/docker-windows/).

- **Entorno:** Linux WSL2, torch 2.15.0+cpu, en el Ryzen 5 7535HS.
- **Cuadros:** 332 de 686 procesados (se descartaron 354) en 27,5 s, para un video de 27,4 s.
- **Tiempo por cuadro:** detección y seguimiento, 43 ms; entrega con VP8, 38 ms.
- **Latencia:** 102 ms de media y 137 ms de p95. Entre el primer y el último décimo bajó de 160 a 81 ms, así que **no crece**. La máxima, 2056 ms, corresponde a la carga del modelo.
- **Conteo:** 11/5/1, con subidas 4/3/0 y bajadas 7/2/1. **Es desarrollo:** `prueba-bus` ya se usó, así que no es una validación. Además, depende de qué cuadros se descarten.
- **Aviso de OpenCV:** `tag 'VP80' is not supported with codec id 139`. El `anotado.webm` igual se genera: 10,9 MB, con cabecera WebM válida.

## Tiempo real en la RTX 2050 (Álvaro, 9 nov.)

Las pruebas se hicieron con la notebook enchufada y en máximo rendimiento.

| Ejecución | FPS | Detección y seguimiento | Entrega | Descartados | Latencia media / p95 |
|---|---|---|---|---|---|
| Panel, ritmo real, VP8 en el conteo (`20261109-004143`) | 10,3 | 43 ms | 53 ms | 404 de 686 | 117 / 143 ms |
| (b) CLI, todos los cuadros, sin video | 58,0 | 17 ms | — | 0 | 17 / 19 ms |
| (a) CLI, ritmo real, sin video | 23,0 | 22 ms | — | 54, todos al arrancar | 23 / 21 ms |
| (c) CLI, todos los cuadros, con VP8 | 11,6 | 37 ms | 49 ms | 0 | 86 / 122 ms |
| **Panel, ritmo real, con la corrección `c272311`** (`20261109-005405`) | **24,75** | 27 ms | 3 ms | **6 de 686** | **32 / 47 ms** |

- **Diagnóstico:** la GPU no era el cuello de botella. Lo eran la codificación VP8 dentro del bucle, que además le quita CPU al seguimiento, y la carga del modelo en el primer cuadro.
- **Corrección:**
  - el video se escribe en mp4v y se convierte a VP8 al terminar;
  - se agrega una inferencia de precalentamiento.
- **Conteo:** 12/13/0, igual al de procesar todos los cuadros en la GPU (b). La diferencia con 12/12/0 en CPU se debe a la plataforma. `prueba-bus` es desarrollo.
- **Detalle:** en esa ejecución, el último `progreso.json` muestra un «retraso» de 30 s porque se escribió después de convertir el video. Se corrigió después: ahora se escribe antes.
- **Evidencia:** [`resultados/gpu-windows/`](resultados/gpu-windows/), con las mediciones a, b y c en `diagnostico/`.

## Validación con PAMELA B (Álvaro, 9 nov., 00:16–00:19)

Se siguió [el prerregistro](validacion-pamela-b/prerregistro.md):

1. Álvaro anotó las referencias antes de la ejecución: `pamela-B-No-cruces.json`, guardada a las 00:16, y `pamela-B-Oy-cruces.json`, a las 00:18.
2. `prueba-pamela-b.ps1` se ejecutó una vez, a las 00:18–00:19, con el commit `1533328`, en la CPU de Windows y a unos 27 FPS.
3. La salida quedó en [`validacion-pamela-b/resultado/`](validacion-pamela-b/resultado/).

| Video | Referencia | Subidas TP/FP/FN | Bajadas TP/FP/FN | F1 | Saldo predicho / real |
|---|---|---|---|---|---|
| B-No | 18 subidas | 15/20/3 | 0/30/0 | 0,36 | +5 / +18 |
| B-Oy | 23 subidas | 19/13/4 | 0/30/0 | 0,45 | +2 / +23 |

**Lectura:**

- **Causa principal: identidades que van y vienen.** De los 127 eventos, 105 (83 %) son de identificadores que cruzan más de una vez y alternan subida y bajada (13 de 24 ids en B-No y 15 de 26 en B-Oy). Concuerda con la fila que espera parada sobre el borde del andén. No se revisó cada caso en el video anotado (`runs/evaluacion/pamela-b/`).
- **Detección:** la mayoría de las subidas reales se detecta (34 de 41). El problema son los eventos de más, no las omisiones.
- **Uso posterior:** desde este resultado, B-No y B-Oy pasan a ser de desarrollo. Si se prueba una corrección mirándolos, se rotula así.

## Suite

**Windows** (Álvaro, 9 nov., 01:06, commit `b60b615`): 139 aprobados, 1 fallido y 1 xfail; ningún omitido; 31,37 s.

### Linux (contenedor de Claude)

`pytest -q -rxs`: **138 aprobados, 1 fallido y 1 xfail.**

- **Fallido:** `test_ensayo_de_oficina_…`, la bajada omitida a los 4,68 s. Es el defecto conocido, que se deja visible.
- **Xfail:** `test_una_persona_con_tres_cajas_…`, la limitación de las cajas encimadas.
- **Omitidos:** ninguno, porque ahora se encuentran los pesos ajustados.

## Pendiente (vigente al 9 nov., 01:20)

**Lista para entregar como prototipo funcional con limitaciones medidas; no están resueltos todos los objetivos.**

| Pendiente | Causa | Acción |
|---|---|---|
| Oclusiones y duplicados del conteo | No hay corrección robusta (F1 de 0,36 y 0,45 en la validación con PAMELA B) | Más datos anotados (cabezas en vista cenital) y una nueva prueba reservada |
| Datos de Paraguay | No se consiguieron grabaciones de cámaras de buses de Paraguay accesibles (restricción central) | Grabar según `../2026-11-08-claude-tarea12/protocolo-validacion-nueva.md` |
| Licencia de `prueba-bus.mp4` | Solo hay una vista previa con marca de agua | No publicar capturas; adquirir la licencia si se van a publicar |
| Ensayo cronometrado de la defensa | Le corresponde al equipo | [`docs/demo/checklist-ensayo.md`](../../demo/checklist-ensayo.md) |
| Publicar `cierre-final` | Falta autorización | Propuesta en el resumen final al equipo |

Lo resuelto (autores, compilación, tiempo real en GPU, Docker, suite en Windows y origen de `prueba-bus`) está registrado en las secciones anteriores.
