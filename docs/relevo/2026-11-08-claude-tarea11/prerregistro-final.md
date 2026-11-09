# Prueba final · prerregistro (8 nov., antes de anotar y de ejecutar)

Se escribe antes de que exista la referencia y antes de ejecutar ningún modelo sobre el video.

## Video

- **Archivo:** `data/raw/youtube-bus-real-0y08Jtqtkys.mp4`, fuera de Git.
- **SHA-256:** `15a9d7c3e6a560e692196f7439bc99fb49d2ff36b2fa3c1dc2bc2bf2ded0de79`.
- **Formato:** 586×480, 25 FPS, 13.836 cuadros (553,4 s).
- **Escena:** cámara cenital sobre la puerta de un bus real, en blanco y negro, con contador comercial sobreimpreso abajo.

## Geometría

Se fija ahora, mirando solo los cuadros y sin ejecutar modelos:

- **Recorte:** `0,20,586,420`, que deja fuera el texto sobreimpreso.
- **Línea:** `0,290,585,290` en coordenadas del recorte. Es el borde del escalón donde el fabricante dibuja su línea verde.
- **Interior:** `arriba`, es decir, subir es moverse hacia arriba en la imagen.

## Referencia

La hace **una persona**, no Claude, en `data/annotations/youtube-bus-real-cruces.json`, con el mismo formato que `kaggle-people-boarding-bus-cruces.json`.

- **Evento:** cada cruce de la línea por el centro del torso, con `t` en segundos y sentido `subida` o `bajada`.
- **Personas detenidas en la escalera:** quien se detiene sobre la línea cuenta solo cuando termina de cruzar.
- **Control:** el contador comercial marca 14 entradas (97 → 111) y 2 salidas (31 → 33). Si la referencia difiere, se anota el motivo en `notas`, pero manda lo que se ve.

## Qué se ejecuta

Se ejecuta **una sola vez**, en la GPU de Álvaro, con `prueba-final.ps1`:

| Configuración | Papel |
|---|---|
| `yolo11n` con rastreador calibrado | API actual, línea de base |
| `yolo11l` con rastreador calibrado | candidato elegido en Kaggle y PAMELA A |

- **Métrica:** TP, FP y FN por sentido con tolerancia de ±1 s; errores = FN + FP; error de conteo; FPS.
- **Cómo se decide:** el candidato reemplaza a la API solo si tiene menos errores totales que la línea de base **y** su velocidad en la GPU es de al menos 10 FPS. Si no cumple las dos condiciones, la API queda como está.
- **Después de ejecutar:** no se cambian umbrales, recorte, línea ni referencia. Si hay un error en la referencia, se corrige, se documenta y se informa que el resultado ya no es una prueba ciega.
