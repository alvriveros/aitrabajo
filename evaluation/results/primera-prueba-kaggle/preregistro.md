# Prueba independiente · `kaggle-people-boarding-bus.mp4` · prerregistro

Registrado el 7 nov. 2026 a las 22:30 (Paraguay), **antes de ejecutar ningún modelo sobre este video y antes de tener la anotación manual**. Nada de lo que sigue se cambia después de ver resultados.

## Video

| Campo | Valor |
|---|---|
| Fuente | Kaggle, «People boarding a bus», de Kapil Raj y un colaborador (`https://www.kaggle.com/datasets/kapilraj/people-boarding-a-bus`), archivo `video5.mp4`. |
| Licencia | **Desconocida** («Unknown» en Kaggle). Uso local para evaluar, citando la fuente. No se versiona ni se redistribuye. Tampoco se versionan capturas, porque muestran personas identificables y coordenadas GPS sobreimpresas. |
| Archivo local | `data/raw/kaggle-people-boarding-bus.mp4`, que Git ignora. |
| SHA-256 | `5084d4b11484282f1a81368f453dfccad9860c714f1e3c9704f65b32058ffe45` (43.857.248 bytes) |
| Formato | H.264, 1920×1080, 25 FPS, 1500 cuadros, 59,96 s. |
| Escena | Puerta de un bus real con cámara arriba de la entrada. Varias personas suben entre 10 y 33 s aproximadamente, con oclusiones; el resto es la puerta sin cruces. A los costados hay pasajeros sentados. |
| Independencia | Otra escena, cámara y personas. Nunca se usó para calibrar, entrenar ni elegir umbrales. **Partición: prueba.** |

## Geometría, fijada antes de ejecutar

- **Recorte:** `600,0,840,1080` (x, y, ancho, alto en píxeles del cuadro). Deja fuera a los pasajeros sentados de los costados.
- **Línea:** `0,480,839,480` en píxeles del recorte: el borde superior de la escalera.
- **Interior:** `arriba`. De abajo hacia arriba es `subida`.
- **Punto del cuerpo, margen y confirmación:** los de cada configuración (centro de la caja, 5 px y la confirmación de la configuración).

## Configuraciones a evaluar, una sola vez

Las de `evaluation/comparar_oficina.py`, sin cambios:

1. **Base, ByteTrack por defecto:** `yolo11n.pt`.
2. **Base calibrado:** `yolo11n.pt`, `vision/bytetrack-cenital.yaml`, `--conf 0.05` y `--confirmacion 2`. Es la configuración que hoy usa la API para el video de oficina.
3. **Ajustado**, solo si llegan los pesos del compañero con el SHA-256 documentado, con ByteTrack por defecto y calibrado.

Hay que tener en cuenta dos cosas al leer los resultados. El calibrado y el ajustado se eligieron con el video de oficina, así que esta prueba mide **cuánto se transfieren a otra escena**. Y una cámara y resolución distintas pueden favorecer o perjudicar a cada configuración: no es una comparación sobre la misma escena.

## Referencia y métrica

- **Referencia:** anotación manual de Álvaro, sin ver predicciones, siguiendo `runs/anotacion-kaggle/INSTRUCCIONES.md`, en `data/annotations/kaggle-people-boarding-bus-cruces.json`. Los casos dudosos se anotan aparte.
- **Métrica:** `evaluation.evaluate` con tolerancia ±1 s, video completo. Se registran TP, FP y FN y el error de conteo **por sentido**, más los instantes omitidos y los extra. No se usa solo el saldo final.
- **Control no independiente:** el contador comercial sobreimpreso en el video pasa de `U:17` a `U:22` y de `D:4` a `D:4` entre 0 y 59,9 s. Leído cada 5 s: U pasa a 19 hacia los 20 s, a 20 hacia los 25 s, a 21 hacia los 30 s y a 22 hacia los 35 s. Es decir, 5 subidas y 0 bajadas según **otro sistema**, que puede equivocarse. Se informa al lado, pero no es la referencia.

## Lo que esta prueba no dice

- **Es un solo video de 60 s,** con casi solo subidas. Las bajadas quedan prácticamente sin medir.
- **No demuestra generalización amplia.** Es una primera señal de cómo funciona el sistema fuera del clip de oficina.
