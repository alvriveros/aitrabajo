# Resultados que respaldan el informe

Cada carpeta conserva, sin cambios de contenido, las predicciones, configuraciones y evaluaciones originales de una evaluación. Los `.config.json` registran comando, pesos, dispositivo y entorno. Las comparaciones usan `evaluation/evaluate.py` (±1 s por sentido: TP, FP, FN, precisión, exhaustividad y F1).

Las rutas que aparecen *dentro* de algunos archivos (por ejemplo `docs\relevo\…` o `runs\…`) son las de la fecha en que se generaron; no se reescribieron.

| Informe | Qué respalda | Carpeta o archivo |
|---|---|---|
| Sec. II-C, Tabla II | Entrenamiento del detector ajustado (40 épocas, mAP50 0,995 y mAP50-95 0,753 en la reserva de la misma grabación) y comparación base/ajustado en oficina, Kaggle y PAMELA A, en Windows | [`base-vs-ajustado/`](base-vs-ajustado/) (`entrenamiento.json`, `pesos-registrados.json`, `kaggle/`, `pamela/`, `oficina-control/`) y `oficina-*.json` |
| Sec. III-A | Confianza del detector en la puerta | [`base-vs-ajustado/diagnostico-confianza/`](base-vs-ajustado/diagnostico-confianza/) |
| Sec. II-C | Selección YOLO11n/l/x: 28 frente a 21 errores (Kaggle + PAMELA A, calibrado) | [`seleccion-yolo11/`](seleccion-yolo11/) (`resultados.txt`) |
| Tabla II, Sec. II-C | Prueba final en el bus real, GPU: YOLO11n frente a YOLO11l. **Influyó en la selección** | [`prueba-final-bus-real/`](prueba-final-bus-real/) |
| Tabla II, Fig. 2 | Evaluación ciega de `prueba-bus`, CPU de Windows, ejecución `20261108-200805-374934`: 24 eventos, 12/12/0 | [`prueba-bus-cpu-ciega/`](prueba-bus-cpu-ciega/) (`prediccion.json` SHA-256 `f863a01b…`, idéntico a `runs/panel/20261108-200805-374934/prediccion.json`) |
| Sec. III-A, Tabla III | Ejecuciones de desarrollo en GPU nativa (`20261109-005405-323754`): 25 eventos, 12/13/0; 680 de 686 cuadros en ritmo real; diagnóstico con los 686 cuadros | [`prueba-bus-gpu/`](prueba-bus-gpu/) |
| Tabla III | Ritmo real en CPU (`prueba-bus` y oficina) | [`ritmo-real-cpu/`](ritmo-real-cpu/) |
| Tabla II | Validación prerregistrada PAMELA B (F1 0,36 y 0,45), una sola ejecución en CPU | [`pamela-b-validacion/`](pamela-b-validacion/) |
| Sec. III-A | NMS con IoU 0,5 y salto de cuadros sobre el conjunto de selección | [`experimentos-seleccion/`](experimentos-seleccion/) |
| Sec. III-A, prueba xfail | Filtro de cajas encimadas: probado y descartado | [`filtro-cajas-encimadas/`](filtro-cajas-encimadas/) |
| `data/README.md` | Primeras pruebas prerregistradas en Kaggle y PAMELA A (CPU Linux) | [`primera-prueba-kaggle/`](primera-prueba-kaggle/), [`primera-prueba-pamela-a/`](primera-prueba-pamela-a/) |
| README | `prueba-bus` procesado dentro de Docker en Windows (8 nov.) | [`docker-windows/`](docker-windows/) |
| Fig. 2 | Curva de cambio acumulado, MAE y RMSE | `python -m evaluation.curva_ocupacion` → `docs/informe/ocupacion-prueba-bus.json` |

Los scripts `.ps1` y `.py` guardados junto a los resultados son los que se usaron entonces; pueden citar rutas anteriores a esta reorganización.

## Modelo entrenado por el equipo

- **Pesos:** `oficina-ajustado.pt`, 5.497.114 bytes, SHA-256 `69958946ba6d38702566cb6dcc5f48dedde3fc345d8f8cf0ceca25636b32de32`. Es la reproducción en Windows del entrenamiento; la original del compañero (macOS, SHA-256 `783d16c0…`, ver `vision/ajuste-detector.md`) no está en este equipo. No se versiona: queda local en `runs/oficina-ajuste-windows/oficina-ajustado.pt`.
- **Reproducción** (requiere `data/raw/oficina.mp4`):
  ```sh
  python -m vision.train --anotaciones data/annotations/oficina-cajas.json --salida runs/oficina-ajuste-windows --pesos yolo11n.pt --epocas 40 --tamano 640 --lote 16 --semilla 0 --dispositivo cpu
  ```
  El comando y el entorno originales están en `base-vs-ajustado/entrenamiento.json`. En otro equipo los pesos pueden no ser idénticos bit a bit.
- **No se despliega:** generaliza mal (0 de 6 en Kaggle, 1 de 28 en PAMELA A). La API usa `yolo11n.pt` preentrenado con el seguimiento calibrado.
