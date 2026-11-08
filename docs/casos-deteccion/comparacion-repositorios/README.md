# Comparación de repositorios externos · 7 de noviembre de 2026

Álvaro compartió cuatro repositorios para ver si algo sirve al proyecto. Esta carpeta guarda qué se revisó, cómo, y qué se midió. Es evidencia técnica, no el informe académico.

**No se copió código ni pesos externos al proyecto, y no se cambió el detector de producción.** El modelo de cabezas se usó solo en un entorno aparte, fuera del repositorio. Los scripts de [`scripts/`](scripts/) son propios.

## Repositorios revisados

Se clonaron con `git clone --depth 1 <URL>` en una carpeta separada del proyecto. Se leyó su contenido y solo se ejecutó el modelo de darshan8850, nada de su código.

| Repositorio | Commit (HEAD) | Fecha | Licencia | Qué contiene (lectura propia) |
|---|---|---|---|---|
| [PhanHuyy/Bus-Passenger-Counter](https://github.com/PhanHuyy/Bus-Passenger-Counter) | `582115716d9665a03a80afb08ad1c6a1b0acdcee` | 2024-07-01 | Sin archivo de licencia | YOLOv8 + ByteTrack con conteo por dos zonas poligonales: un ID visto en la zona A y luego en la B. Interfaz PyQt5. Sin pruebas. |
| [darshan8850/bus_passanager_counter](https://github.com/darshan8850/bus_passanager_counter) | `b71082567d9e8ae9ed9135114fcced52bc9b9ffd` | 2024-09-04 | Sin archivo de licencia | Grafo TensorFlow 1 congelado `models/HEAD_DETECTION_300x300_ssd_mobilenetv2.pb`. App Flask que cuenta caras y cabezas en un cuadro por segundo; no cuenta cruces. |
| [Mau-FTL/Bus-Passenger-Counter](https://github.com/Mau-FTL/Bus-Passenger-Counter) | `f398df9f50958429082f33722f253023400d131e` | 2026-05-05 | MIT | Contador manual en un solo `index.html`: botones de subida y bajada, GPS y exportación CSV. Sin visión por computadora. |
| [shijieS/people-counting-dataset](https://github.com/shijieS/people-counting-dataset) (PCDS) | `be8913477e9eb89a9280cadfe044cfa2327d1fc9` | 2024-02-15 | CC BY-NC-SA 3.0 (según su README) | Solo la descripción del dataset. Los videos se descargan aparte. |

### Afirmaciones de terceros, no verificadas

- **darshan8850:** su README dice que el modelo es SSD MobileNetV2 "preentrenado en COCO y ajustado para detectar cabezas", robusto a iluminación y orientación. No indica el origen de los pesos, los datos de ajuste ni la licencia.
- **PCDS:** su README describe 5.464 pares de videos (profundidad y color) en puertas de buses, unas 20.900 personas, cámara Kinect V1 arriba de la entrada con inclinación, y etiquetas de entradas y salidas por video. Los autores advierten que color y profundidad no están sincronizados. Pide citar a Sun et al., IEEE T-ITS 2019.

### Intento de obtener una muestra de PCDS

Se probó el 7 nov., a las 23:20 UTC. Baidu Pan (`https://pan.baidu.com/s/10O2JJrTC3WJJvweW8XGWVA`) y la carpeta de Google Drive, que el README da por eliminada, no responden desde ninguno de los dos entornos disponibles: el contenedor de Claude y la máquina virtual del equipo de Álvaro. La red de ambos solo permite una lista de sitios. **Bloqueado.** No se obtuvo ningún video, así que no hay identificadores ni partición que registrar. La propuesta de evaluación está en [la devolución de la tarea 08](../../relevo/2026-11-07-claude-tarea08/propuesta-evaluacion-pcds.md).

## Lo medido por Claude

### Entorno e insumos

- **Equipo:** contenedor Linux x86_64, Intel Xeon a 2,30 GHz, 2 vCPU, sin GPU.
- **Proyecto:** Python 3.12.3, ultralytics 8.4.203, torch 2.15.0 y opencv-python 5.0.0.93, con la rama `integracion-video` en `b511d91`.
- **Entorno aparte para el modelo externo:** Python 3.12.3, tensorflow-cpu 2.21.0, opencv-python-headless 5.0.0.93 y numpy 2.5.4. Se ejecutó con `python -I` y no se instaló en el proyecto.
- **Clip:** `data/raw/oficina.mp4`, 1.375.027 bytes, SHA-256 `02666c2e567f45015a2e73fe802db8f39c6c568d41ef42efc63997de4d15fc95`. Recorte `228,2,222,176`, 1316 cuadros a 25 FPS.
- **Detector de personas:** `yolo11n.pt`, 5.613.764 bytes, SHA-256 `0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1`.
- **Detector de cabezas:** `HEAD_DETECTION_300x300_ssd_mobilenetv2.pb`, 15.730.208 bytes, SHA-256 `7b111e1dde41573917d6a7c86b37d15da464f0c841dcbf9868c1d03d91a9630b`, del commit `b710825` de darshan8850. No se copió al proyecto.
- **Referencia:** `data/annotations/oficina-cruces.json`, con 20 cruces y una sola persona. Salió de cajas revisadas por Claude y todavía no la revisó una persona. Es la misma grabación con la que se calibró el rastreador, así que **no es una referencia independiente**.

### Procedimiento

Desde la raíz del proyecto:

```sh
# 1. Detecciones por cuadro en el recorte, sin rastreador
python -I scripts/detectar_cabezas.py HEAD_DETECTION_300x300_ssd_mobilenetv2.pb data/raw/oficina.mp4 resultados/detecciones-cabezas.json   # entorno tensorflow
python scripts/detectar_personas.py yolo11n.pt data/raw/oficina.mp4 resultados/detecciones-personas.json
# 2. ByteTrack y la regla de conteo del proyecto (vision.cruces), misma línea, margen 5 px, confirmación 2, centro de caja
python scripts/contar.py resultados/detecciones-cabezas.json vision/bytetrack-cenital.yaml 0.05 resultados/eventos/cabezas-cenital.json
python scripts/contar.py resultados/detecciones-cabezas.json <ultralytics>/cfg/trackers/bytetrack.yaml 0.1 resultados/eventos/cabezas-defecto.json
#    (lo mismo con detecciones-personas.json)
# 3. Control: el pipeline real del proyecto sobre el video completo
python -m vision.pipeline --video data/raw/oficina.mp4 --recorte 228,2,222,176 --linea 0,90,221,90 --interior arriba \
  --rastreador vision/bytetrack-cenital.yaml --conf 0.05 --confirmacion 2 --dispositivo cpu --pesos yolo11n.pt \
  --salida resultados/eventos/pipeline-base-calibrado-completo.json
# 4. Evaluación con el evaluador del proyecto, tolerancia de 1 s
python -m evaluation.evaluate --referencia data/annotations/oficina-cruces.json --prediccion resultados/eventos/<x>.json [--hasta 6]
# 5. Detecciones frente a cajas de persona anotadas (6-52 s)
python scripts/cuadros_anotados.py resultados/detecciones-<x>.json <umbral>
```

Las rutas de `scripts/` y `resultados/` son relativas a esta carpeta. **Control del arnés:** `contar.py` con las detecciones de personas reproduce exactamente los 11 eventos del pipeline real (mismos tiempos y sentidos), así que el arnés no introduce diferencias. `confianza_cabezas_0_6.py` es la primera prueba, de 0 a 6 s, cuyos resultados se comunicaron antes de ampliar el experimento.

### Resultados en el video completo

| Detector + rastreador | Aciertos (de 20) | Omisiones | Eventos extra | F1 | IDs distintos | Cuadros con track |
|---|---|---|---|---|---|---|
| `yolo11n` + ByteTrack cenital, conf 0,05 (pipeline real, x86) | 11 | 9 | 0 | 0,71 | 33 | 226 |
| `yolo11n` + ByteTrack por defecto, conf 0,1 | 0 | 20 | 0 | 0 | 17 | 55 |
| Cabezas SSD + ByteTrack cenital, conf 0,05 | **19** | 1 (bajada 30,36 s) | 1 (subida 12,16 s) | **0,95** | 34 | 232 |
| Cabezas SSD + ByteTrack por defecto, conf 0,1 | 17 | 3 (subidas 32,76 y 43,8; bajada 30,36) | 0 | 0,92 | 31 | 202 |
| *Guardado en macOS: `yolo11n` + cenital (`evaluation/results/oficina-completo-base-calibrado.json`)* | *12* | *8* | *0* | *0,75* | — | — |

**Tramo de 0 a 6 s:** con cabezas, las dos configuraciones dan la subida a 2,08 s y la bajada a 4,64 s (2 de 2). El pipeline base da 1 de 2. Detalle por sentido, con tiempos omitidos y extra, en [`resultados/evaluacion/`](resultados/evaluacion/).

**Continuidad de IDs.** Toda la referencia corresponde a una sola persona que cruza 20 veces, y aun así cada configuración usa entre 17 y 34 IDs. El seguimiento se corta entre cruces en todos los casos. El evento extra con cabezas (subida a 12,16 s, 0,36 s después de la de 11,8 s) es compatible con un cambio de ID cerca de la línea, pero no se inspeccionó cuadro por cuadro.

**Detecciones contra cajas anotadas** ([`cuadros-anotados.jsonl`](resultados/cuadros-anotados.jsonl)): 143 cuadros con persona y 22 vacíos o con sombra, entre 6 y 52 s.

| Detector | Umbral | Cuadros con persona sin detección | Cuadros vacíos con detección | Detecciones fuera de la caja |
|---|---|---|---|---|
| `yolo11n` | 0,05 | 61 | 1 | 48 |
| `yolo11n` | 0,10 | 78 | 0 | 3 |
| Cabezas | 0,05 | 63 | 0 | 0 |
| Cabezas | 0,10 | 63 | 0 | 0 |

Las cajas son de **persona**, no de cabeza, así que es una aproximación. Una cabeza siempre cae dentro de la caja de su persona, y "sin detección" puede incluir cuadros donde la cabeza quedó fuera del recorte. El detector de cabezas no tuvo ninguna detección fuera de las cajas, pero tampoco ve a la persona en 63 de 143 cuadros. Con este material, que la cuente bien depende de que la vea en los cuadros cercanos a la línea.

## Límites de estas mediciones

- **Una sola grabación, con una sola persona y sin multitud.** No dice nada sobre generalización, oclusiones ni cruces simultáneos.
- **Referencia no independiente:** salió de las mismas cajas del proyecto y falta la revisión humana.
- **Confianzas no comparables.** Las de los dos detectores no son probabilidades calibradas entre sí. Que el de cabezas dé 0,9 donde `yolo11n` da 0,02 muestra que uno detecta y el otro no en esos cuadros, no cuánto "más seguro" es.
- **Línea y punto no revisados.** Se usó la línea de y = 90 y el centro de la caja, pensados para el cuerpo. Con cabezas, el punto de seguimiento queda más arriba y el instante del cruce cambia; por ejemplo, la subida pasa de 2,16 a 2,08 s.
- **Sin evidencia de la causa.** Estos datos no confirman por qué falla `yolo11n` (composición de COCO, punto de vista cenital u otra razón) ni por qué cambia entre macOS y x86.
  - Sí se observa que el mismo pipeline da eventos distintos en macOS (12 de 20) y en este equipo (11 de 20). Por ejemplo, macOS tiene la bajada de 4,6 s y la subida de 7,12 s, y no tiene la subida de 48,32 s.
  - La explicación numérica sigue siendo una hipótesis.
- **El modelo de cabezas no es utilizable tal como está:** no tiene licencia, su origen no está documentado y requiere TensorFlow.

## Conclusión

No es todavía una recomendación de reemplazo.

- **El detector de cabezas sí ve los cruces donde el detector actual falla.** En esta grabación, con el mismo rastreador y la misma regla, lleva el conteo de 11 a 19 aciertos sobre 20, con un evento extra.
- **Antes de cambiar el detector** hacen falta pesos con licencia clara (propios, ajustados a cabezas), revisar la línea y el punto de seguimiento, y evaluar en grabaciones distintas de esta.
- **PhanHuyy y Mau-FTL** no aportan nada directamente utilizable.
- **PCDS** es el mejor candidato para una evaluación independiente, pero su descarga quedó bloqueada desde estos entornos.
