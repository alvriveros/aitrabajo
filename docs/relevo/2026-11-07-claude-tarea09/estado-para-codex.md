# Estado de la integración y del conteo · 7 nov. 2026, 23:45 · para analizar con Codex

Resumen de lo trabajado con Claude en la sesión de hoy. Trabajo en `TpFinal\.worktrees\integracion-video`, rama `integracion-video`.

## 1. Pregunta central: ¿el sistema funciona?

**La integración funciona. El conteo con el detector base no es confiable.**

- **Integración (verificada en Linux y en Windows):** el panel procesa el clip, la API ejecuta `vision.pipeline`, el video anotado se reproduce, se distinguen la predicción y la referencia manual, y la ocupación se calcula bien con los eventos que produce el modelo. Codex la aceptó para la demo fija de 0–6 s.
- **Calidad del conteo:** con `yolo11n.pt` base y la configuración calibrada que usa la API (`bytetrack-cenital.yaml`, `conf 0.05`, `confirmacion 2`), el sistema omite muchos cruces o inventa eventos, según la escena (sección 4).

## 2. Git

- **`main`:** sin cambios, en `3d92072`.
- **`origin/integracion-video`:** en `27fd3ce`, con push hecho.
  - `e85fb75`: merge `--no-ff` de `d0a658a` (trabajo de Álvaro) con `origin/vision` en `dd5a19a` (compañero).
  - `d2cf58d` y `b511d91`: integración del video y caso de la bajada omitida (tarea 07).
  - `bc18608`: tarea 08. Solo se publican ejecuciones completas y validadas, el selector llega al final del tramo, y se recuperaron 3 ejecuciones antiguas tras validarlas.
  - `27fd3ce`: tarea 09. Comparación del modelo base en Linux y Windows, ficha de grabación independiente, revisión de la referencia de oficina y mensaje al compañero.
- **Sin commit todavía, después de `27fd3ce`:** `data/README.md`, `resumen.md`, `docs/relevo/2026-11-07-claude-tarea09/README.md`, `data/annotations/kaggle-people-boarding-bus-cruces.json`, `data/annotations/pamela-A-cruces.json`, `docs/relevo/2026-11-07-claude-tarea09/prueba-kaggle/` y `.../prueba-pamela/`.
- **Pruebas:** 99 aprobadas, 1 omitida (faltan los pesos ajustados) y **1 fallida**, `test_ensayo_de_oficina_…`, por la bajada omitida del modelo base. Es la misma en Linux y Windows, y no se debilitó.

## 3. Videos disponibles

Todos en `data/raw/` del worktree, ignorados por Git. Ninguno se sube.

| Archivo | Fuente y condiciones | Escena | SHA-256 (inicio) | Estado |
|---|---|---|---|---|
| `oficina.mp4` | YouTube, canal Mike Niel; terceros | Oficina que simula una puerta, 52,6 s | `02666c2e` | Usado para **calibrar y entrenar**: no sirve como evaluación |
| `kaggle-people-boarding-bus.mp4` | Kaggle «People boarding a bus», licencia **desconocida** | Bus real, cámara arriba, 1080p, 60 s, 6 subidas | `5084d4b1` | **Prueba hecha** (sección 4) |
| `puerta-tren-d800-A.mp4` | PAMELA-UANDES (Velastin et al., *Sensors* 2020), **solo investigación** | Vagón de laboratorio, 352×288, 30 s, bajadas | `cf18411c` | **Prueba hecha** (sección 4) |
| `puerta-tren-d800-B-No.mp4`, `…-B-Oy.mp4` | PAMELA-UANDES | Subidas muy densas, 30 s cada uno | `58d945ab`, `00151d75` | Sin anotar: demasiado densos para marcar a ojo |
| `youtube-bus-demo-UYKQ1sQOIwo.mp4` | YouTube, Mike Niel; terceros | Bus real, cámara arriba, blanco y negro, 854×454, 31,4 s; solo texto sobreimpreso | `d68bba25` | **Recién descargado**, sin prerregistro ni anotación |
| `youtube-bus-real-0y08Jtqtkys.mp4` | YouTube, Mike Niel; terceros | Bus real, cámara arriba, 586×480, 9 min 13 s, pocos pasajeros. Trae líneas finas dibujadas y el contador comercial en la franja inferior | `15a9d7c3` | **Recién descargado**, sin prerregistro ni anotación |

**Descartados:**
- STONKAM (`v8ltNiOwN_Q`): montaje promocional con cajas dibujadas encima.
- Motion Array (`2V-UKh8tsdk`): vista aérea lateral de 10 s, de un banco comercial con marca de agua. Primero dije que se veían solo un par de personas; al revisar más cuadros hay entre 8 y 10. Se descarta igual por el ángulo y la duración.
- `hrj2TtMgrOE` y `qSKM_YSNhOI`: traen dibujados el recuadro rojo y la línea verde del producto comercial.
- PCDS (Baidu Pan): para descargar hay que iniciar sesión con una cuenta de Baidu; además, sus etiquetas son solo totales por video.

**PAMELA-UANDES:** Álvaro pidió por correo al Prof. Velastin usuario y contraseña para acceder a la referencia oficial: cabezas anotadas cuadro a cuadro con ID por persona en 15 videos completos (R1–R4 para entrenar, el resto para probar), más conteos por video. Si llega, sirve para:
- evaluar con una referencia oficial;
- entrenar un detector de cabezas sin anotar a mano.

## 4. Resultados del conteo

Tolerancia ±1 s. Cada celda es TP / FP / FN.

| Video | Referencia | Base, ByteTrack por defecto | Base calibrado (API) |
|---|---|---|---|
| Oficina, video completo (Linux = Windows) | 10 subidas y 10 bajadas, de cajas revisadas por Claude | 0/0/10 y 0/0/10 | Subidas 7/0/3, bajadas 4/0/6 |
| Oficina 0–6 s | 1 subida y 1 bajada | Ninguna detectada | Subida sí, bajada omitida |
| Kaggle | 6 subidas, anotadas por Claude | Subidas 1/0/5, bajadas 0/1/0 | **Subidas 5/4/1, bajadas 0/4/0** |
| PAMELA A | 28 bajadas, anotadas por Claude | Bajadas 1/0/27, subidas 0/1/0 | **Bajadas 10/0/18, subidas 0/1/0** |

- **Oficina, por plataforma:** Linux x86 y Windows (Ryzen 5 7535HS) dan **eventos idénticos**. Solo la ejecución guardada en macOS (12 de 20) difiere. La explicación numérica entre plataformas sigue siendo una hipótesis.
- **Kaggle:** en escenas concurridas el sistema inventa eventos. Aparecen cajas que abarcan a dos personas y su centro oscila sobre la línea, así que un mismo track da «subió, bajó, subió». El saldo final (+5 contra +6) parece bueno pero esconde 9 errores.
- **PAMELA:** a baja resolución y con un flujo continuo de personas, el sistema pierde casi dos de cada tres.
- **Hipótesis, sin probar:**
  - `conf 0.05` acepta cajas de mala calidad.
  - El margen de 5 px se calibró para un recorte de 176 px de alto y no escala.
  - `yolo11n` base ve mal a las personas desde arriba.
- **Sin ajustes:** no se ajustó nada sobre Kaggle ni PAMELA, porque son de prueba. Los dos se **prerregistraron** antes de ejecutar: recorte, línea y configuraciones, en `prueba-*/preregistro.md`.
- **Límite de estas pruebas:** las referencias de Kaggle y PAMELA las hizo Claude mirando cuadros, sin ver predicciones, y **falta la revisión de una persona**.

## 5. Detector alternativo (experimento, no está en producción)

- **Qué se probó:** el SSD MobileNetV2 de cabezas del repo `darshan8850/bus_passanager_counter`, en un entorno aparte con TensorFlow. Con el mismo ByteTrack y la misma regla, contó **19 de 20** cruces de oficina, con 1 extra, contra 11 de 20 del base.
- **Por qué no se recomienda reemplazar:**
  - el modelo no tiene licencia ni origen documentado;
  - requiere TensorFlow;
  - se probó en una sola grabación;
  - la referencia no es independiente;
  - la línea y el punto de seguimiento no se revisaron para cabezas.
- **Evidencia:** `docs/casos-deteccion/comparacion-repositorios/`.

## 6. Pendientes y decisiones abiertas

1. **Decisión de Álvaro:** ¿reentrenar el detector ajustado con `vision.train` y las anotaciones del repositorio? Sería «ajustado reproducido», con su propio hash, para probarlo **una vez** en Kaggle, PAMELA y los videos nuevos de Mike Niel. Es la prueba que responde si el sistema puede funcionar. La tarea 09 pedía no reentrenar por defecto, así que Claude no lo hizo.
2. **Pedidos al compañero** (`docs/relevo/2026-11-07-claude-tarea09/mensaje-companero.md`, sin enviar):
   - los pesos ajustados `oficina-ajustado.pt` (SHA-256 `783d16c0…`), con commit, comando, configuración y versiones;
   - la medición de confianza en su Mac;
   - la revisión de la referencia de oficina, cuyo origen en 2,16 y 4,68 s no está documentado.
3. **Los dos videos nuevos de Mike Niel:** prerregistrar recorte y línea (dejando fuera el texto sobreimpreso), anotar sin ver predicciones y ejecutar una vez. Por ser del mismo fabricante cuentan como una sola fuente.
4. **Revisión humana** de las anotaciones de Kaggle (6) y PAMELA A (28), aunque sea de una muestra.
5. **Credenciales de PAMELA,** si llegan: repetir con la referencia oficial y los videos completos de prueba.
6. **Commit** de lo que está sin registrar después de `27fd3ce`.
7. **Informes:** aplazados por decisión de Álvaro.

## 7. Documentos clave

- `resumen.md`
- `docs/relevo/2026-11-07-claude-tarea08/README.md` y `revision-codex-windows.md`
- `docs/relevo/2026-11-07-claude-tarea09/README.md`, `referencia-oficina.md`, `ficha-grabacion-independiente.md` y `mensaje-companero.md`
- `docs/relevo/2026-11-07-claude-tarea09/prueba-kaggle/` y `prueba-pamela/`: `preregistro.md`, `resultados.md` y scripts
- `docs/casos-deteccion/oficina-bajada-omitida/` y `comparacion-repositorios/`
- `data/README.md`: fuentes, licencias, hashes y particiones

## Actualización · tarea 10 (8 nov.)

Se reprodujo el ajuste en Windows, con SHA-256 `69958946…`, y se comparó contra el base. **El ajustado no se transfiere:**
- en Kaggle, 0 de 6 subidas, sin ningún evento;
- en PAMELA A, 0 o 1 de 28 bajadas;
- en oficina, su propio entrenamiento, 19 o 20 de 20.

No hay evidencia para cambiar de modelo. Ver `docs/relevo/2026-11-08-claude-tarea10/README.md`.

## Actualización · tarea 11 (8 nov.)

Se probaron detectores más grandes sin entrenar: `yolo11l` y `yolo11x`, cada uno con el rastreador por defecto y con el calibrado.

- **Ganador según el prerregistro:** `yolo11l` calibrado, con 21 errores entre Kaggle y PAMELA A, contra 28 de la API actual.
  - En Kaggle cuenta las 6 de 6 subidas, con 4 eventos falsos.
  - En PAMELA cuenta 13 de 28 bajadas.
- **`yolo11x`** no mejora.
- **Velocidad:** 1,5 FPS en CPU; en la GPU no está medida.
- **API sin cambios.** La prueba final con `youtube-bus-real` espera una referencia humana; está en `prerregistro-final.md` y `prueba-final.ps1`.

Ver `docs/relevo/2026-11-08-claude-tarea11/README.md`.

**Prueba final (8 nov., 04:37):** la referencia es de Álvaro, a mano, con 18 cruces.
- `yolo11n` calibrado: 13 errores, 6 de 18 cruces, 66 FPS.
- `yolo11l` calibrado: 18 errores, 12 de 18 cruces, 24 FPS; casi todos los falsos son la misma persona contada dos o tres veces.

La API no cambia, según lo prerregistrado.

## Actualización · tarea 12 (8 nov.)

Resultado exploratorio, porque las referencias de Kaggle y PAMELA son de Claude y no tienen revisión humana.

- **Filtro:** la supresión temporal por sentido, con `u ∈ {0; 0,5; 1; 1,5}` y prerregistrada, no se justifica. Lo que mejora el total borra bajadas reales de PAMELA; por ejemplo, `yolo11n` con 1,5 s pasa de 28 a 23 errores, pero suma 1 FN.
- **Diagnóstico:**
  - en Kaggle y PAMELA, los falsos son sobre todo oscilaciones del mismo ID;
  - en PAMELA, y con `yolo11n` en YouTube, dominan las omisiones puras;
  - en YouTube con `yolo11l` (solo descriptivo) predominan la fragmentación y la oscilación, más 2 errores de tiempo.
- **Herramientas:** se guardaron en `tarea12/historico/` las versiones de los scripts que produjeron la evidencia y se corrigieron el anotador y el arnés.
- **Siguiente paso propuesto:** registrar las posiciones y trayectorias de cada track cerca de la línea.
- **Para versionar:** ver `docs/relevo/2026-11-08-claude-tarea12/manifiesto.md`.

## Actualización · tarea 13 (8 nov., noche)

Álvaro pidió el camino B: subir y procesar un video desde la página. Está implementado en `api/main.py` (`/videos…`) y en `ui/app.py` («Video nuevo»).

- **Tests:** `tests/test_videos.py`, con 10. Toda la suite da 122 aprobados, 1 omitido y el fallo conocido de oficina.
- **Navegador:** con PAMELA A, la página da eventos idénticos a los del pipeline de la tarea 11.
- **No se usó** el video nuevo de validación.
- **Arranque, pasos y guion de demo:** en `docs/relevo/2026-11-08-claude-tarea13/README.md`.

## Actualización · tarea 14 (8 nov., noche)

**Diagnóstico** sobre el video anotado de `prueba-bus`: de los 12 falsos, inspeccionados uno por uno, 8 son cajas encimadas o de grupo con IDs propios, 1 es una oscilación de una de esas cajas, 2 son un ID que salta de persona y 1 queda ambiguo. No vienen de la regla de cruce.

**Filtro probado:** de cajas encimadas, con umbral 0,6 y ventana de 1 s fijados antes de medir. Se evaluó sobre trayectorias guardadas (`tarea14/tracks`).

| Escena | Efecto del filtro |
|---|---|
| Oficina | Sin cambios |
| Kaggle | −4 FP |
| PAMELA A | **−1 cruce real** |
| `prueba-bus` (desarrollo) | −7 FP, **−1 cruce real** |

**Decisión:** queda fuera.
- `vision/` sigue byte a byte igual.
- El experimento está en `tarea14/experimento/`.
- La prueba `tests/test_cajas_encimadas.py` queda en xfail.

**Página:** subir, ubicar la geometría, procesar, descargar y recargar sin reprocesar: verificado en Chrome sin pantalla. Con oficina subida como video nuevo, los eventos son idénticos a los de la tarea 11.

## Cierre (8 nov., noche)

Ver `docs/relevo/2026-11-08-claude-cierre/README.md`.

- **Versión:** sin cambios en `vision/` y sin filtros.
- **Oficina:** queda como limitación confirmada; su test se conserva fallando.
- **Demo principal:** `prueba-bus` desde la página, con los errores medidos.
- **Tests (Windows):** 129 aprobados, 1 fallido, 1 omitido y 1 xfail.

**Repetición para demostración (8 nov., noche):** se agregó a la página. «Reprocesar en vivo para demostración» envía `repetir_para_demostracion: true` y vuelve a ejecutar la misma configuración en una carpeta aparte, con `proposito` y `repite_a` en `entrada.json`. «Procesar video» sigue sin repetir y muestra el resultado guardado. Hay un test nuevo en `tests/test_videos.py`.
