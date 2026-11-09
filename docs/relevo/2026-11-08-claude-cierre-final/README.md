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
| `405d523` | Docker con visión en CPU, pesos en la imagen, volúmenes y healthchecks | **Sin construir** (ver «Pendiente») |
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

## Suite (Linux, contenedor de Claude)

`pytest -q -rxs`: **138 aprobados, 1 fallido y 1 xfail.**

- **Fallido:** `test_ensayo_de_oficina_…`, la bajada omitida a los 4,68 s. Es el defecto conocido, que se deja visible.
- **Xfail:** `test_una_persona_con_tres_cajas_…`, la limitación de las cajas encimadas.
- **Omitidos:** ninguno, porque ahora se encuentran los pesos ajustados.

## Pendiente (causa → acción)

| Pendiente | Causa | Acción |
|---|---|---|
| Autores y universidad en el informe | Faltan los datos | Álvaro: completar `\autores` y `\afiliacion` |
| Compilar el informe y verificar 3 páginas | A este TeX Live le faltan `IEEEtran` y `babel-spanish`, y la red no permite instalarlos | Compilar en Windows (MiKTeX) o en un TeX Live completo, y revisar las 3 páginas |
| `docker compose up --build` con visión | Docker Hub está bloqueado en el entorno de Claude | Álvaro: construir, subir `prueba-bus` y procesarlo |
| Tiempo real en la máquina de defensa | Solo hay CPU en el entorno de Claude | Álvaro: procesar `prueba-bus` con ritmo real en la RTX 2050 y compartir `runs\panel\<id>\prediccion.config.json` |
| Prueba manual del panel en el navegador | Sin navegador hacia el contenedor | Álvaro: seguir el guion completo |
| Validación independiente y datos de Paraguay | No hay grabaciones nuevas | Grabar según `../2026-11-08-claude-tarea12/protocolo-validacion-nueva.md` |
| Duplicados y omisiones del conteo | No hay corrección robusta | Más datos anotados (cabezas en vista cenital) |
| Origen de `prueba-bus.mp4` | No está documentado | Álvaro: URL o identificador de iStock y licencia |
