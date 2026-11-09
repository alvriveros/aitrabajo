# Prueba independiente · PAMELA-UANDES `A_d800mm_sample` · prerregistro

Registrado el 7 nov. 2026 a las 23:20 (Paraguay), **antes de ejecutar ningún modelo sobre este video**. Lo de abajo no se cambia después de ver resultados.

## Video

| Campo | Valor |
|---|---|
| Fuente | [PAMELA-UANDES](https://videodatasets.org/PAMELA-UANDES/whole_data.html), muestra pública `A_d800mm_sample.mp4`. A = bajada; puerta de 800 mm; vagón de tren de laboratorio. |
| Condiciones | Solo investigación, no comercial y sin redistribuir. Citar: Velastin, Fernández, Espinosa y Bay (2020), *Sensors* 20(21): 6251, https://doi.org/10.3390/s20216251. |
| Archivo local | `data/raw/puerta-tren-d800-A.mp4`, que Git ignora. |
| SHA-256 | `cf18411cda0d7b9de9a1c649599185b4d469c20fa2f9fc4f057d537aeb0868ab` |
| Formato | H.264, 352×288, 25 FPS, 760 cuadros, 30,4 s. |
| Independencia | Otra escena, cámara y personas; nunca se usó para calibrar ni entrenar. **Prueba.** Los otros dos videos de esta fuente (`B-No` y `B-Oy`) son de la misma cámara y no se usarán para ajustar nada. |

## Geometría, fijada antes de ejecutar

- **Recorte:** `96,64,160,224` en píxeles del cuadro: la puerta y una franja del andén.
- **Línea:** `0,96,159,96` en píxeles del recorte: el umbral de la puerta, en y = 160 del cuadro.
- **Interior:** `arriba`, que es el vagón. De arriba hacia abajo es `bajada`.

## Configuraciones, una sola vez

Las de `evaluation/comparar_oficina.py`, sin cambios:

1. **Base, ByteTrack por defecto.**
2. **Base calibrado:** `bytetrack-cenital.yaml`, `conf 0.05` y `confirmacion 2`.
3. **Ajustado:** solo si llegan los pesos con el SHA-256 documentado.

## Referencia y métrica

- **Referencia:** `data/annotations/pamela-A-cruces.json`, con 28 bajadas y 0 subidas.
  - **Quién la hizo:** **Claude**, mirando los cuadros antes de ejecutar ningún modelo. **Falta la revisión de una persona.**
  - **No es la referencia oficial** del dataset, que tiene acceso restringido y ya fue solicitada.
- **Métrica:** `evaluation.evaluate` con tolerancia ±1 s. Se registran TP, FP y FN y el error de conteo por sentido.
- **Si llegan las anotaciones oficiales:** se repite la evaluación con esa referencia y se informan las dos.
