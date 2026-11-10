# Tarea 14 · Duplicados en el conteo y cierre de la demo · devolución (8 nov., noche)

Rama `integracion-video`, sin commit. La primera evaluación de `prueba-bus` (tarea 13) se conservó intacta: queda en `runs/panel/20261108-200805-374934/` y hay copia en `tarea13/primera-evaluacion/`.

## Respuesta corta

**La corrección probada no entra en la entrega:**

- **Lo que logra:** reduce los falsos positivos, en Kaggle de 8 a 4 y en `prueba-bus` de 12 a 5.
- **Por qué se descarta:** **borra un cruce real en PAMELA A** y otro en `prueba-bus`. Por el criterio de cierre, la entrega mantiene el conteo de siempre, sin cambios en `vision/`.
- **La limitación queda visible:** hay una prueba específica (`tests/test_cajas_encimadas.py`) que pytest informa como *xfail*.

## 1. Diagnóstico

Se usó el video anotado ya existente, sin inferencia nueva para inspeccionar. Se miraron tres casos:

| Caso | Qué se ve | Causa |
|---|---|---|
| 8,20, 8,24 y 8,36 s, 3 bajadas (IDs 14, 22 y 10) | **Una persona** baja con **tres cajas encimadas** a la vez: una parcial (torso), una entera y una más grande. Cada una tiene su ID y su centro cruza la línea. | Cajas duplicadas |
| 10,16 a 10,60 s, 4 bajadas (IDs 33, 38, 37 y 39) | Bajan dos personas (33 y 38). La caja 37 **abarca a las dos**, y la 39 aparece encimada sobre 38. | Caja de grupo + caja duplicada |
| 15,04 a 16,04 s, mezcla de sentidos | Un hombre baja con 3 o 4 cajas (77, 79 y 83). La caja 55 empieza sobre él y termina sobre una mujer que sube. La 77 «sube» y después «baja». | Cajas duplicadas + una caja que salta de persona + oscilación |

**Revisión de los 12 falsos de la primera evaluación** (agregado después, el 8 nov. a la noche). Se inspeccionaron todos en el video anotado; los tres grupos de la tabla anterior más 11,88, 14,80, 18,08 y 21,12 s:

| Tipo | Falsos (tiempo, ID) | Cantidad |
|---|---|---|
| Segunda o tercera caja sobre una persona ya contada (incluye caja de grupo) | 8,24 (22) · 8,36 (10) · 10,60 (39) · 11,88 (43 sobre 45) · 15,76 (77) · 15,88 bajada (79) · 16,04 (88) · 21,12 (97 sobre 67) | 8 |
| Caja duplicada que primero «sube» y después «baja» | 15,28 subida (77) | 1 |
| Un ID que salta a otra persona | 18,08 (ID 2 pasa de la mujer que subió al hombre que camina afuera) · 15,88 subida (la subida de la mujer se adjudicó al ID 55, que venía del hombre que bajaba, y su propia caja, 78, quedó como falso) | 2 |
| Ambiguo: segundo ID sobre la misma persona | 14,80 (59, después de 73): no se distingue si es otra caja o un cambio de ID | 1 |

**Las cajas encimadas son la causa más frecuente, pero no la única.** El *xfail* sintético documenta ese mecanismo; por sí solo no prueba la causa en el video. Lo que la respalda es esta inspección.

**La regla de cruce no es la causa:**

- `ContadorCruces` ya exige un lado confirmado (2 cuadros fuera de un margen de 5 px) y después el otro.
- Aparecer junto a la línea no cuenta.

**Tampoco son cambios de ID de una sola caja.** El origen es que el detector, con confianza 0,05, deja varias cajas sobre la misma persona, y ByteTrack, con umbrales bajos, sigue cada una como un track distinto.

## 2. Corrección probada (experimento)

- **Regla:** se descarta el cruce de un track si su caja está encimada con la de otro track que ya contó el **mismo sentido** hace menos de 1 s.
  - Encimada quiere decir que la intersección dividida por el área de la caja menor es ≥ 0,6.
  - En cada cuadro se procesan primero las cajas chicas.
- **Lo que no hace:** no es una supresión temporal global. Nunca filtra al propio track (se puede cruzar y volver), ni el sentido opuesto, ni a personas sin cajas encimadas.
- **Parámetros:** se fijó un único valor (0,6 y 1 s) antes de medir, sin búsqueda.
- **Pruebas:** 7, en `experimento/test_filtro.py`.
- **Comparación:**
  - Para comparar sobre **exactamente las mismas trayectorias**, se guardaron una sola vez las cajas e IDs por cuadro de cada video (`registrar_tracks.py` → `tracks/`; `yolo11n` calibrado, CPU, Linux). Después se contó con y sin filtro (`comparar.py` → `resultados/comparacion.json`).
  - Sin filtro, oficina, Kaggle y PAMELA A reproducen exactamente los eventos de la tarea 11.

| Escena | Sin filtro TP/FP/FN (subidas · bajadas) | Con filtro | Efecto |
|---|---|---|---|
| Oficina | 7/0/3 · 4/0/6 | 7/0/3 · 4/0/6 | igual |
| Kaggle | 5/4/1 · 0/4/0 | 5/1/1 · 0/3/0 | −4 FP |
| PAMELA A | 0/1/0 · 10/0/18 | 0/1/0 · **9**/0/**19** | **−1 cruce real** |
| `prueba-bus` (**desarrollo, no validación**) | 4/5/0 · 8/7/0 | 4/2/0 · **7**/3/**1** | −7 FP, **−1 cruce real** |

- **PAMELA A:** dos personas reales que bajan a menos de 1 s, con cajas que se tocan, quedaron como una sola.
- **`prueba-bus`:** en Linux el rastreador da IDs y algunos eventos distintos de la ejecución de Windows (24 eventos en las dos, 17 FP en Linux contra 12 en Windows). Ya se había visto esta diferencia entre sistemas. Lo que importa es la comparación con y sin filtro sobre las mismas trayectorias de Linux.
- **Decisión:** borra cruces reales, así que **no se incorpora**.
  - `vision/cruces.py` y `vision/pipeline.py` quedaron byte a byte como antes: los SHA-256 `c8ea687b…` y `7ad496f6…` son los mismos.
  - El código probado está en `experimento/`: las copias completas `*.con-filtro.py` y el módulo aislado `filtro.py`, que es el que usa `comparar.py`.

**Siguiente paso sugerido, sin hacer:** atacar la causa más frecuente, las cajas duplicadas del detector, y además los saltos de ID. Por ejemplo, otro umbral de NMS o un detector entrenado con escenas cenitales, evaluado en escenas nuevas.

## 3. Verificación

- **Suite:** `pytest`, con 1 *xfail* (la limitación documentada) y el fallo conocido de siempre (la bajada de oficina).
- **Experimento:** `experimento/test_filtro.py` pasa sus 7 pruebas.
- **Windows** (Álvaro, 8 nov., 20:42): `pytest -q -rx` dio 129 aprobados, 1 omitido, 1 *xfail* (cajas encimadas) y solo el fallo conocido de oficina.

## 4. Demo en la página

Se verificó en Chrome sin pantalla, contra la API y el panel reales; ver la sección de la tarea 13. Además:

- Subir `oficina.mp4` como «Video nuevo», cargar la geometría a mano y pulsar «Procesar video» una vez.
- Después, mover controles («Capacidad del bus», «Nombre de la parada») y **recargar la página**: no se lanzó ningún procesamiento nuevo, porque la API registró un solo `POST …/procesamientos`.
- Al volver a subir el mismo archivo, se muestra la ejecución existente.

## Archivos

- `README.md`, `registrar_tracks.py`, `comparar.py`, `tracks/` (cajas e IDs por cuadro) y `resultados/comparacion.json`, que incluye los eventos descartados.
- `experimento/`: `filtro.py`, `test_filtro.py`, `cruces.con-filtro.py` y `pipeline.con-filtro.py`.
- `tests/test_cajas_encimadas.py`, en la suite del proyecto.
- `tarea13/primera-evaluacion/`: copia de la evaluación original de `prueba-bus`.

## Versión de entrega

**Qué contiene:** API y panel con el modo «Video nuevo» (tarea 13); la demo de oficina y la carga de JSON, sin cambios; el conteo de siempre (`yolo11n` calibrado), sin filtros.

**Arranque**, en Windows, con dos ventanas de PowerShell abiertas en `TpFinal\.worktrees\integracion-video` (no en `TpFinal`):
```
.\.venv\Scripts\python.exe -m uvicorn api.main:app --port 8000
.\.venv\Scripts\python.exe -m streamlit run ui/app.py
```
La página queda en `http://localhost:8501`. Tests: `.\.venv\Scripts\python.exe -m pytest -q -rx`. Resultado: 129 aprobados, **1 fallido** (oficina, limitación confirmada), **1 omitido** (pesos ajustados ausentes) y **1 xfail** (cajas encimadas). El cierre final está en `../2026-11-08-claude-cierre/README.md`.

**Guion de demo (unos 3 minutos):**
1. **«Archivo JSON o demo»:** mover el selector de segundos y ver cómo cambia la ocupación.
2. **«Video nuevo»:** subir `prueba-bus.mp4`. La geometría ya usada es recorte `0,0,768,432`, línea `274,431,467,242` e interior arriba. Mostrar la vista previa (sin modelo) y las coordenadas.
3. **Ejecución existente:** esa geometría ya se procesó, así que pulsar «Procesar video» muestra «No se repite» y el **resultado guardado**, que no es inferencia en vivo. Para procesar en vivo, usar «Reprocesar en vivo para demostración». El guion vigente está en el cierre. Mostrar el video anotado, los eventos y las descargas.
4. **Ocupación** por parada.
5. **Cierre honesto:**
   - en este video el sistema detectó los 12 cruces, pero registró 24 eventos: cuenta varias veces a la misma persona porque el detector pone varias cajas sobre ella;
   - una corrección probada bajaba esos duplicados, pero borraba pasajeros reales y quedó fuera;
   - en el bus de YouTube contó 6 de 18.

**Limitaciones conocidas:**
- **Duplicados:** cajas duplicadas o de grupo cuentan de más (xfail en la suite).
- **Omisiones** en escenas densas: PAMELA A cuenta 10 de 28.
- **Velocidad:** CPU, unos 9 a 14 cuadros por segundo.
- **Un procesamiento a la vez.**
- **Docker:** la imagen no trae las librerías de visión, así que subir un video responde 503.
- **Resultados distintos entre sistemas:** Linux y Windows pueden dar IDs y eventos algo distintos.
- **`prueba-bus`** ya se usó para desarrollo. Es evidencia de desarrollo, no una validación independiente; solo la primera evaluación (tarea 13) se hizo a ciegas.
