# Datos

Los videos van en `data/raw/`, que git ignora. Acá se documenta de dónde sale cada grabación y para qué se usa. Todos los fragmentos de una grabación quedan en la misma partición.

## Grabaciones

| Archivo | Origen | Contexto | Duración | Partición |
|---|---|---|---|---|
| `data/raw/oficina.mp4` | YouTube, ver abajo | Real, pero es una oficina que hace de puerta de bus | 52,64 s | Calibración. Solo como ensayo de integración, no para métricas del informe. |

Faltan grabaciones independientes para entrenamiento, validación y prueba.

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
