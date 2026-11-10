# Validación nueva `prueba-bus` · registro previo a procesar

Lo registró Claude el 8 nov. a las 20:06 (hora de Asunción), a pedido de Álvaro. En ese momento **no había ninguna ejecución del modelo sobre este video**: las únicas carpetas de `runs/panel/` con `entrada.json` son de PAMELA A (`cf18411c…`).

- **Video:** `data/raw/prueba-bus.mp4`, SHA-256 `0b4b8c97940c5f753880cf370046e1930121bf30dde4182905735b11b7e90d63`. Ya está subido al panel como `runs/videos/0b4b8c97940c5f75/`.
- **Referencia de Álvaro:** `data/annotations/prueba-bus-cruces.json`, SHA-256 `0640f227a6f90feea0fa35e94fe58b055c1591cb466257214f5045ae1d1870c4`, con 12 cruces. Se guardó a las 20:06; el archivo es del 8 nov., 23:06:27 UTC.
- **Línea de la referencia, en el cuadro completo:** `274,431 → 467,242`. La geometría del panel tiene que dar esa misma línea. El recorte y el interior se registran en `entrada.json` al procesar.
- **Lo que sigue:** un solo procesamiento desde el panel con esa geometría. Se compara con tolerancia de ±1 s, con TP, FP y FN por sentido. El candidato es la API actual. No se cambian parámetros después de ver el resultado.

## Resultado (procesado por Álvaro desde el panel, 8 nov., 20:08)

- **Ejecución y geometría:** ejecución `runs/panel/20261108-200805-374934`, la única sobre este video. Recorte `0,0,768,432` (cuadro completo); línea `274,431 → 467,242`, igual a la de la referencia; interior arriba.
- **Configuración:** `yolo11n` calibrado en CPU, sin filtros: 686 cuadros en 78,3 s, a 8,76 FPS.
- **Comparación** con la referencia de hash `0640f227…`, tolerancia ±1 s:

| Sentido | Referencia | Predichos | TP | FP | FN |
|---|---|---|---|---|---|
| Subidas | 4 | 8 | 4 | 4 | 0 |
| Bajadas | 8 | 16 | 8 | 8 | 0 |
| **Total** | 12 | 24 | **12** | **12** | **0** |

**Lectura:**

- **Cruces reales:** la API **detecta los 12 cruces**, sin ninguna omisión.
- **Conteo duplicado:** registra **el doble de eventos**, 12 de ellos falsos.
- **Cómo son los falsos:** casi todos aparecen a menos de 0,5 s de un acierto del mismo sentido y con otro `track_id`; por ejemplo 8,20, 8,24 y 8,36 s, o 10,36, 10,40 y 10,60 s. Encaja con fragmentación (la misma persona con un ID nuevo) o con varias detecciones de una misma persona.
- **Oscilación:** también hay un caso, el ID 77, que sube a 15,28 s y baja a 15,76 s.
- **Ocupación:** el saldo predicho es −8 contra −4 reales.

**Decisión:**

- **No se cambia ningún parámetro** después de este resultado.
- **No se aplica a posteriori** la supresión temporal de la tarea 12. No se justificó en Kaggle y PAMELA, y ajustarla mirando este video lo invalidaría como prueba.
- **Sin candidato alternativo:** no había un candidato congelado, así que solo se midió la API.

## Uso posterior (8 nov., noche, tarea 14)

Después de esta primera evaluación, el video se usó para **depurar y comparar** una corrección: el filtro de cajas encimadas, que no se incorporó.

- **Rotulado:** esos resultados son **evaluación de desarrollo**, no validación independiente.
- **Primera evaluación:** queda como estaba, en `runs/panel/20261108-200805-374934/`, con copia en `primera-evaluacion/`.

Ver `docs/relevo/2026-11-08-claude-tarea14/README.md`.
