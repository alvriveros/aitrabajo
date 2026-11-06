# Módulo de visión

Convierte un tramo de video de una puerta en eventos de subida y bajada con el formato de [`POST /ocupacion`](../api/main.py). La entrega completa está descrita en [el relevo de visión](../docs/tareas/vision/README.md).

## Estado al 6 de noviembre

| Parte | Estado |
|---|---|
| Regla de cruces (`cruces.py`) | Probada con trayectorias de ejemplo. |
| Argumentos, exportación y configuración (`pipeline.py`) | Probados. |
| Lectura de video, YOLO, ByteTrack y video anotado | Ejecutados sobre un clip sintético y sobre el clip real. |
| Primer clip | **Con predicción, pero frágil.** Subida a los 2,16 s y bajada a los 4,6 s, con una configuración calibrada sobre el mismo clip. Ver [el relevo del primer clip](../docs/relevo/vision-primer-clip/README.md). |
| API y panel | Probados por HTTP con la predicción del primer clip: 0 → 1 pasajero (5 %) → 0. |
| Ajuste del detector (`train.py`) y evaluación (`evaluate.py`) | **Pendientes.** El detector base no reconoce bien a personas vistas desde arriba. |

Las 49 pruebas pasan con `pytest` en Python 3.12.16 sobre macOS (Apple M4). Sin las dependencias de visión, 42 pasan y el resto se omite, así que el entorno de `requirements.txt` sigue funcionando. Todavía no se probó en Windows.

## Regla de conteo

- **Punto del cuerpo.** El centro de la caja decide de qué lado está la persona. `--punto pies` usa el borde inferior.
- **Lado confirmado.** Hacen falta `--confirmacion` cuadros seguidos a más de `--margen` píxeles de la línea. Dentro de ese margen el estado no cambia, así que temblar sobre la línea no cuenta.
- **Evento.** Se emite al pasar de un lado confirmado al otro. El primer lado de un track no cuenta, así que aparecer junto a la línea no alcanza. Un regreso confirmado genera un evento nuevo.
- **Tiempo.** `tiempo_s` son los segundos desde el inicio del tramo hasta el primer cuadro del lado nuevo de la línea. Salen de las marcas temporales del video, no del momento de la confirmación.
- **Línea.** Se trata como una recta infinita porque se traza de lado a lado del recorte.

Limitaciones conocidas, cubiertas por las pruebas:

- Si el ID cambia durante el cruce, el evento se omite.
- Si un track tiene menos de `--confirmacion` cuadros del lado de origen, tampoco se cuenta.

## Preparar el entorno

Desde la raíz, en macOS o Linux:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt -r vision/requirements.txt
```

En PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r vision\requirements.txt
```

- **Versiones.** Python 3.12.16 y las fijadas en [`vision/requirements.txt`](requirements.txt). El entorno ocupa cerca de 1,5 GB en macOS.
- **Pesos.** `yolo11n.pt` (5.613.764 bytes, SHA-256 `0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1`), preentrenado con COCO. Ultralytics lo descarga en la carpeta actual la primera vez, desde `https://github.com/ultralytics/assets/releases/download/v8.4.0/yolo11n.pt`. Para la defensa dejalo en la raíz, porque git lo ignora y debe estar disponible sin internet.
- **Clip.** Cómo obtenerlo y sus condiciones de uso están en [`data/README.md`](../data/README.md).
- **Telemetría.** Ultralytics envía analíticas anónimas por defecto. Se desactivan con `yolo settings sync=False`.
- **Licencia.** Ultralytics se distribuye con AGPL-3.0.

## Ejecutar

Comando exacto del primer clip, desde la raíz y con el entorno activado:

```sh
python -m vision.pipeline \
  --video data/raw/oficina.mp4 --inicio 0 --fin 6 \
  --recorte 228,2,222,176 --linea 0,90,221,90 --interior arriba \
  --rastreador vision/bytetrack-cenital.yaml --conf 0.05 --confirmacion 2 \
  --dispositivo cpu --pesos yolo11n.pt --parada "Puerta de oficina · 0-6 s" \
  --salida evaluation/results/oficina-00-06-prediccion.json \
  --video-anotado runs/oficina-00-06-anotado.mp4
```

- `--recorte` se mide en píxeles del cuadro completo y `--linea` en píxeles del recorte, con origen arriba a la izquierda.
- `--interior arriba` significa que abajo → arriba es `subida`.
- [`bytetrack-cenital.yaml`](bytetrack-cenital.yaml), `--conf` y `--confirmacion` se calibraron sobre este ensayo. Con los valores por defecto da 0 eventos. Para otra escena hay que elegirlos en validación.
- La salida usa el esquema de [la referencia manual](../docs/demo/oficina-00-06-manual.json).
- Junto a la salida queda `oficina-00-06-prediccion.config.json`, con el comando, el recorte, la línea, el sistema de coordenadas, los parámetros, los FPS medidos y las versiones.
- `runs/` y los `.mp4` están fuera de git, así que el video anotado se regenera con este comando.

## Pruebas

```sh
python -m pytest tests -v
```

[`tests/test_pipeline_modelo.py`](../tests/test_pipeline_modelo.py) ejecuta el camino completo con el modelo real, sobre un clip sintético y sobre el ensayo de oficina. Cada prueba se omite si falta lo que necesita: las dependencias de visión, los pesos o el clip.

## Velocidad de referencia

Con `yolo11n.pt` en un Apple M4:

- **Clip sintético** (180 cuadros, recorte de 640×360, sin video anotado): 46 FPS con `--dispositivo cpu` y 28 FPS con `--dispositivo mps`.
- **Ensayo de oficina** (150 cuadros, recorte de 222×176, CPU, con video anotado): 34,7 FPS.

Sirve solo para comprobar que corre. Los FPS del informe se miden en la máquina de defensa.
