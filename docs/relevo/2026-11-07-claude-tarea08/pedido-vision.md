# Pedido para visión · bajada omitida del ensayo de oficina

Para el compañero de visión. Lo envía Álvaro; no se mandó nada automáticamente.

## Qué pasa

Con `dd5a19a` y la configuración guardada de 0–6 s (`yolo11n.pt`, `conf 0.05`, `vision/bytetrack-cenital.yaml`), la bajada de ≈ 4 s **no se cuenta** en dos equipos:

- Linux x86, en el contenedor de Claude.
- Windows 11 con un procesador AMD, en la máquina de defensa (ejecución `20261107-194239-470039`).

En los dos queda solo la subida a 2,16 s, y `tests/test_pipeline_modelo.py::test_ensayo_de_oficina_sigue_dentro_de_la_tolerancia_de_la_referencia_manual` falla. La predicción guardada en tu Mac sí tiene la bajada a 4,60 s.

En el video completo, el mismo pipeline da 11 de 20 cruces en Linux contra 12 de 20 en tu ejecución guardada, con eventos distintos. El análisis está en [`docs/casos-deteccion/oficina-bajada-omitida/`](../../casos-deteccion/oficina-bajada-omitida/README.md). La diferencia entre plataformas es una **hipótesis**, no una causa confirmada.

## Qué necesitamos, en este orden

### 1. Tus pesos YOLO ya ajustados (prioridad)

- **Archivo:** `runs/oficina-ajuste/oficina-ajustado.pt`, o el que corresponda.
- **Tamaño y SHA-256** del archivo.
- **Commit de `vision`** con el que se entrenó y el comando exacto de `python -m vision.train`.
- **Configuración con la que lo recomendás:** rastreador (por defecto o `bytetrack-cenital.yaml`), `conf`, `confirmacion`, `margen` y punto.
- **Versiones del entorno:** Python, ultralytics, torch, opencv-python y lap, más sistema operativo y procesador.
- **Uso:** según tu relevo, el ajustado se entrenó con la misma grabación de oficina, así que la comparación en ese clip no muestra que generalice. Si se puede, indicá qué cuadros entraron al entrenamiento.

Con los pesos, en Windows comparamos base y ajustado sobre el mismo clip y con la misma referencia, y registramos aciertos, omisiones y eventos extra por separado. No vamos a ajustar umbrales sobre este clip.

### 2. Medición de confianza en tu Mac

Desde la raíz de `integracion-video`, con el mismo clip (SHA-256 `02666c2e…15fc95`) y `yolo11n.pt` (SHA-256 `0ebbc80d…644ee1`):

```sh
python docs/casos-deteccion/oficina-bajada-omitida/medir_confianza.py runs/confianza-macos.json
python -m vision.pipeline --video data/raw/oficina.mp4 --inicio 0 --fin 6 --recorte 228,2,222,176 \
  --linea 0,90,221,90 --interior arriba --rastreador vision/bytetrack-cenital.yaml --conf 0.05 \
  --confirmacion 2 --dispositivo cpu --pesos yolo11n.pt --salida runs/macos-00-06.json --video-anotado runs/macos-00-06.mp4
```

Mandanos `runs/confianza-macos.json`, `runs/macos-00-06.json` y su `.config.json`. Compararemos cuadro a cuadro con [`confianza.json`](../../casos-deteccion/oficina-bajada-omitida/confianza.json) de Linux. Lo que más interesa es el tramo de 4,04 a 4,60 s, donde las confianzas de x86 quedan en 0,081, 0,088 y 0,093, contra el umbral de 0,10. Si en tu Mac la bajada vuelve a aparecer, la diferencia entre plataformas queda medida.

### 3. Después: ¿detector de cabezas?

Hay un experimento aparte en [`docs/casos-deteccion/comparacion-repositorios/`](../../casos-deteccion/comparacion-repositorios/README.md). Con un SSD MobileNetV2 de cabezas de un repositorio externo, el mismo ByteTrack y la misma regla, se contaron 19 de 20 cruces en el video completo, con un evento extra, contra 11 de 20 del base.

**No es una recomendación de reemplazo.** El modelo no tiene licencia ni origen documentado, requiere TensorFlow, se probó en una sola grabación y la referencia no es independiente. Si hay datos y tiempo después del punto 1:

- **Etiquetas:** las cajas de `data/annotations/oficina-cajas.json` son de **persona** y no sirven directamente como etiquetas de cabeza. Hay que revisar y reanotar.
- **Punto y línea:** al pasar de caja corporal a cabeza, cambian el punto de seguimiento y el instante del cruce; con cabezas, la subida pasa de 2,16 a 2,08 s. Hay que revisar el punto y la posición de la línea.
- **Comparación:** comparar los eventos con una referencia manual independiente, en una grabación distinta de la de oficina.

## Qué no cambiamos

No se cambió el detector, los umbrales, el rastreador ni las pruebas. La omisión queda visible como limitación del modelo: el panel muestra lo que predijo el modelo y la referencia manual por separado, sin completar la bajada.
