# Tarea 10 · prerregistro del entrenamiento y la evaluación

Registrado el 7 nov. 2026 a las 23:58 (Paraguay), **antes de entrenar**. El hash de los pesos se agrega automáticamente después de entrenar y antes de evaluar, en `windows/pesos-registrados.json` (lo escribe `entrenar-y-evaluar.ps1`). Nada de lo que sigue se cambia después de ver resultados.

## Entrenamiento

- **Datos:** solo oficina. `data/annotations/oficina-cajas.json` sin cambios (SHA-256 `95ce9391b939b5f9561819a1353e0317bcb8f4c396d3cfead76092be38b7c2ff`) y `data/raw/oficina.mp4` (SHA-256 `02666c2e…15fc95`). Álvaro eligió la **opción A**: no se corrige ninguna caja. Las dudas visuales quedan como pendientes en [`revision-anotaciones.md`](revision-anotaciones.md).
- **Comando:** el documentado en `docs/relevo/vision-ajuste-detector/README.md`, cambiando solo la salida y el resumen para no pisar los archivos del compañero:
  ```
  python -m vision.train --anotaciones data/annotations/oficina-cajas.json --salida runs/oficina-ajuste-windows --resumen docs/relevo/2026-11-08-claude-tarea10/windows/entrenamiento.json --pesos yolo11n.pt --epocas 40 --tamano 640 --lote 16 --semilla 0 --dispositivo cpu
  ```
- **Nombre:** «**ajustado reproducido en Windows**». Los pesos quedan en `runs/oficina-ajuste-windows/oficina-ajustado.pt`, fuera de Git. No se espera que su hash coincida con el del compañero (`783d16c0…`), porque el entrenamiento en otra máquina puede dar pesos distintos.

## Configuraciones a comparar

Las cuatro de `evaluation/comparar_oficina.py`, sin cambios:

| Nombre | Detector | Rastreador y umbrales |
|---|---|---|
| base-defecto | `yolo11n.pt` | ByteTrack de Ultralytics por defecto |
| base-calibrado | `yolo11n.pt` | `bytetrack-cenital.yaml`, `conf 0.05`, `confirmacion 2` (configuración actual de la API) |
| ajustado-defecto | reproducido | ByteTrack por defecto: la configuración que el compañero eligió en validación sobre oficina |
| ajustado-calibrado | reproducido | Igual que base-calibrado |

Las dos comparaciones se leen así:

- **Comparación de detectores, mismo rastreador:** base-calibrado contra ajustado-calibrado, y base-defecto contra ajustado-defecto.
- **Comparación de sistemas completos:** base-calibrado (la API actual) contra ajustado-defecto (la propuesta del compañero). Cambian el detector y el rastreador a la vez.

## Evaluación

- **Kaggle y PAMELA A:** prerregistros y referencias de la tarea 09, sin cambios (recorte, línea, tolerancia ±1 s y anotaciones de Claude). Ambas referencias **siguen pendientes de revisión humana**.
- **Base en Windows:** el base se vuelve a ejecutar en Windows, con los mismos insumos y configuración, para que la comparación con el ajustado sea en la misma plataforma. Se contrasta con los resultados de Linux de la tarea 09.
- **Oficina:** el ajustado también se ejecuta sobre oficina, solo para comprobar que la reproducción se parece al resultado del compañero (20 de 20). **No es una evaluación**, porque es su material de entrenamiento.
- **Prohibido:** entrenar o ajustar parámetros sobre Kaggle o PAMELA, y ejecutar predicciones sobre `youtube-bus-demo-UYKQ1sQOIwo.mp4` y `youtube-bus-real-0y08Jtqtkys.mp4`, que quedan reservados para la prueba final.
- **Métricas:** TP, FP y FN por sentido, error de conteo por sentido y FPS. Los videos anotados se conservan en `runs/evaluacion/windows-amd64/`.
