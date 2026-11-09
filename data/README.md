# Datos

Los videos van en `data/raw/`, que git ignora. Acá se documenta de dónde sale cada grabación y para qué se usa. Todos los fragmentos de una grabación quedan en la misma partición.

## Estado vigente (9 nov., cierre final)

| Grabación | Referencia | Revisión humana | Uso hasta hoy | ¿Sirve como prueba independiente? |
|---|---|---|---|---|
| `oficina.mp4` | 20 cruces y 165 cuadros con cajas (Claude) | **No** | Entrenamiento, calibración y selección | No |
| `kaggle-people-boarding-bus.mp4` | 6 subidas (Claude) | **Sí**, Álvaro, sin cambios (8 nov., 18:46) | Selección (tareas 09–14) | No |
| `puerta-tren-d800-A.mp4` | 28 bajadas (Claude) | **Sí**, Álvaro, sin cambios (8 nov., 18:46) | Selección (tareas 09–14) | No |
| `youtube-bus-real-0y08Jtqtkys.mp4` | 15 subidas y 3 bajadas (Álvaro) | Es humana | Prueba final de la tarea 11: **consumida** | No |
| `prueba-bus.mp4` | 4 subidas y 8 bajadas (Álvaro, antes de procesar) | Es humana | **Primera evaluación ciega (tarea 13)**; después, desarrollo | Solo su primera evaluación |
| `puerta-tren-d800-B-No.mp4` y `…-B-Oy.mp4` | 18 y 23 subidas (Álvaro, antes de procesar: `pamela-B-*-cruces.json`) | Es humana | **Validación prerregistrada (9 nov.)**, ejecutada una vez: F1 de 0,36 y 0,45 | Ya no: quedan consumidos. Es la misma escena que PAMELA A |

- **Dónde está la revisión:** [`revision-humana-referencias.md`](../docs/relevo/2026-11-08-claude-tarea12/revision-humana-referencias.md), con los hashes. Las anotaciones de Kaggle y PAMELA conservan, sin cambios, el campo `anotado_por` original, que dice «sin revisión humana»; la revisión posterior consta en ese archivo.
- **Contexto local: restricción central.** No se consiguieron grabaciones de cámaras de buses de Paraguay accesibles para este proyecto. Esa disponibilidad limitada de datos impidió adaptar y evaluar el sistema en el contexto local, y motivó el uso de grabaciones de otras procedencias: YouTube, Kaggle, PAMELA-UANDES (Chile) e iStock (Eslovenia). Para la próxima prueba hace falta una grabación nueva, idealmente de un colectivo del Gran Asunción. Protocolo: [`protocolo-validacion-nueva.md`](../docs/relevo/2026-11-08-claude-tarea12/protocolo-validacion-nueva.md).

## Estado anterior (8 nov., tarea 12)

- **Kaggle y PAMELA A** se usaron para **seleccionar** el detector en la tarea 11 y para explorar el filtro de la tarea 12. Ya no son pruebas independientes. Sus referencias son de Claude y siguen sin revisión humana.
- **`youtube-bus-real-0y08Jtqtkys.mp4`** se **consumió** en la prueba final de la tarea 11, con la referencia de Álvaro en `annotations/youtube-bus-real-cruces.json`.
  - No se usa para elegir parámetros ni como prueba ciega.
  - Fuente: [YouTube 0y08Jtqtkys](https://www.youtube.com/watch?v=0y08Jtqtkys), de terceros, sin licencia abierta; no se versiona.
- **`youtube-bus-demo-UYKQ1sQOIwo.mp4`** solo sirve como ejemplo cualitativo: hay una multitud que no se puede anotar. Fuente: [YouTube UYKQ1sQOIwo](https://www.youtube.com/watch?v=UYKQ1sQOIwo).
- **La próxima validación** necesita una grabación nueva (ver `docs/relevo/2026-11-08-claude-tarea12/protocolo-validacion-nueva.md`).

Las particiones de la tabla siguiente son las originales.

## Grabaciones

| Archivo | Origen | Contexto | Duración | Partición |
|---|---|---|---|---|
| `data/raw/oficina.mp4` | YouTube, ver abajo | Real, pero es una oficina que hace de puerta de bus | 52,64 s | Entrenamiento y calibración. No sirve para métricas del informe. |
| `data/raw/kaggle-people-boarding-bus.mp4` | [Kaggle, «People boarding a bus»](https://www.kaggle.com/datasets/kapilraj/people-boarding-a-bus) (`video5.mp4`), licencia desconocida | Real: puerta de bus, cámara arriba de la entrada | 59,96 s | **Prueba.** Nunca se usó para calibrar ni entrenar. |
| `data/raw/puerta-tren-d800-A.mp4`, `…-B-No.mp4`, `…-B-Oy.mp4` | [PAMELA-UANDES](https://videodatasets.org/PAMELA-UANDES/whole_data.html), muestras públicas `A_d800mm_sample`, `B_No_d800mm_sample` y `B_Oy_d800mm_sample` | Puerta de vagón de tren en laboratorio, puerta de 800 mm, cámara cenital. A = bajada; B = subida sin y con tarjeta | 30 s c/u | **Prueba**, como una sola fuente. Sin referencia todavía. |
| `data/raw/prueba-bus.mp4` | [iStock, ID 1457518529](https://www.istockphoto.com/video/ld-bus-stopping-at-the-station-and-passengers-getting-off-it-gm1457518529-492183151), vista previa con marca de agua; licencia no verificada | Real: bus en una parada, cámara alta (Eslovenia) | 27,4 s | **Prueba ciega** (tarea 13); después, desarrollo |

`kaggle-people-boarding-bus.mp4`:
- **Archivo:** H.264, 1920×1080, 25 FPS, 43.857.248 bytes, SHA-256 `5084d4b11484282f1a81368f453dfccad9860c714f1e3c9704f65b32058ffe45`. Lo descargó Álvaro el 7 nov. 2026.
- **Uso:** licencia «Unknown» en Kaggle. Solo uso local para evaluar, citando la fuente: no se versiona, no se redistribuye y no se suben capturas. Muestra personas identificables y coordenadas GPS sobreimpresas.
- **Prerregistro:** recorte, línea y configuraciones fijados antes de ejecutar, en [`docs/relevo/2026-11-07-claude-tarea09/prueba-kaggle/preregistro.md`](../docs/relevo/2026-11-07-claude-tarea09/prueba-kaggle/preregistro.md).
- **Anotación:** [`annotations/kaggle-people-boarding-bus-cruces.json`](annotations/kaggle-people-boarding-bus-cruces.json), con 6 subidas y 0 bajadas. La hizo **Claude** a pedido de Álvaro, mirando los cuadros antes de ejecutar ningún modelo. **Falta la revisión de una persona.** Resultados en [`prueba-kaggle/resultados.md`](../docs/relevo/2026-11-07-claude-tarea09/prueba-kaggle/resultados.md).

`prueba-bus.mp4` (agregado el 9 nov., cierre final):
- **Fuente:** iStock (Getty Images), video de stock **ID 1457518529**, «LD Bus stopping at the station and passengers getting off it», del colaborador `simonkr`, publicado el 28 feb. 2023: https://www.istockphoto.com/video/ld-bus-stopping-at-the-station-and-passengers-getting-off-it-gm1457518529-492183151. Según la página, es una toma alta y fija de un bus que se detiene, con gente que baja y sube, grabada en Eslovenia (no es de Paraguay).
- **Archivo local:** H.264, 768×432, 25 FPS, 686 cuadros (27,4 s), SHA-256 `0b4b8c97940c5f753880cf370046e1930121bf30dde4182905735b11b7e90d63`, con la marca de agua «iStock by Getty Images». Es una **vista previa**, no el archivo HD o 4K que se obtiene con la licencia.
- **Correspondencia:** Claude comparó el contenido del archivo local con el título y la descripción de la página, y coinciden: toma alta y fija de un bus detenido en la parada, con pasajeros que bajan y suben. **No se comparó con el archivo original de iStock** (no se descargó), así que la identificación es por contenido.
- **Permisos: no verificados.** La página ofrece una licencia estándar paga, pero no consta que se haya adquirido. No se versiona ni se redistribuye, y antes de publicar capturas hay que resolver la licencia.
- **Referencia y uso:** sin cambios. `annotations/prueba-bus-cruces.json` (SHA-256 `0640f227…`, de Álvaro, antes de procesar) y una primera evaluación ciega (tarea 13). Después se usó para desarrollo.

Muestras de PAMELA-UANDES (`puerta-tren-d800-*`):
- **Archivos:** 352×288, 25 FPS, unos 30 s cada uno. SHA-256: A `cf18411cda0d7b9de9a1c649599185b4d469c20fa2f9fc4f057d537aeb0868ab`; B-No `58d945ab2a876d563dcbdfe07b9cf9697aa842c9999458e061b5d8a3530ec650`; B-Oy `00151d75110b95fe4d1d8aff61dc5bfadaf10b83b6808acd2251c7d3802d43ea`. Los descargó Álvaro el 7 nov. 2026.
- **Condiciones:** **uso solo para investigación**, no comercial, y citando el trabajo: Velastin, Fernández, Espinosa y Bay (2020), *Sensors* 20(21): 6251, https://doi.org/10.3390/s20216251. No se redistribuye.
- **Referencia:** el dataset ofrece, con usuario y contraseña que entrega el Prof. Sergio A. Velastin, cabezas anotadas cuadro a cuadro con ID por persona para 15 videos completos (R1 a R8 de bajada, R1 a R7 de subida; R1 a R4 se usan normalmente para entrenar) y conteos manuales por video. Las muestras de 30 s no traen referencia propia, y en `B` la densidad hace poco fiable una anotación a ojo. Para la muestra `A` hay una referencia de Claude, hecha mirando los cuadros antes de ejecutar ningún modelo: [`annotations/pamela-A-cruces.json`](annotations/pamela-A-cruces.json), con 28 bajadas. Falta la revisión humana; resultados en [`prueba-pamela/resultados.md`](../docs/relevo/2026-11-07-claude-tarea09/prueba-pamela/resultados.md).

Faltan grabaciones independientes para validación y más material de prueba, sobre todo con bajadas.

## Anotaciones

- [`annotations/oficina-cajas.json`](annotations/oficina-cajas.json): cajas de personas para ajustar el detector. Dentro de la grabación separa `entrenamiento` (6–43 s) y `reserva` (desde 43 s), y deja fuera el ensayo de 0 a 6 s. Esa separación solo orienta el trabajo, porque todo viene de la misma grabación.
- [`annotations/oficina-cruces.json`](annotations/oficina-cruces.json): los 20 cruces del video, con el esquema de `POST /ocupacion`. Salen del centro de las cajas revisadas. Sus totales coinciden con el contador comercial del video.

**Las revisó Claude; falta la revisión de una persona.** Cómo revisarlas y qué se corrigió está en [el relevo del ajuste](../docs/relevo/vision-ajuste-detector/README.md).

## `oficina.mp4`

- **Fuente:** [Fast Run Test in Office- Automatic Passenger Counter System](https://www.youtube.com/watch?v=L1fkyVQbHOg), canal Mike Niel, publicado el 23 de febrero de 2017.
- **Archivo:** H.264, 450×360, 25 FPS, sin audio, 1.375.027 bytes. SHA-256 `02666c2e567f45015a2e73fe802db8f39c6c568d41ef42efc63997de4d15fc95`.
- **Escena:** cámara cenital fija. El cuadro tiene cuatro cuadrantes: la vista con las líneas de un sistema comercial, la misma vista limpia, y dos paneles negros con sus líneas y contadores. Se procesa solo el cuadrante superior derecho.
- **Condiciones de uso:** `yt-dlp` no informa una licencia abierta (`license: NA`). Se trata como contenido de terceros: no se versiona ni se redistribuye. Las condiciones de YouTube restringen las descargas, así que conviene usar grabaciones propias para la evaluación y la demo.
- **Referencia del propio video:** su contador comercial termina en 10 entradas y 10 salidas. No es una anotación manual.

Se descargó el 6 de noviembre de 2026 con `yt-dlp` 2026.10.26, sin cookies:

```sh
yt-dlp --no-playlist -f 134 -o "data/raw/oficina.%(ext)s" "https://www.youtube.com/watch?v=L1fkyVQbHOg"
```

El formato de mayor resolución (231, 600×480) respondió `403 Forbidden` ese día, así que se usó el 134. Los formatos disponibles pueden cambiar; comprobá el SHA-256 antes de comparar resultados.
