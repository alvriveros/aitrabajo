# Módulo de visión

Convierte un tramo de video de una puerta en eventos de subida y bajada con el formato de [`POST /ocupacion`](../api/main.py). La entrega completa está descrita en [el relevo de visión](../docs/tareas/vision/README.md).

## Estado vigente (9 nov., cierre final)

- **Lo que usa la API:** `yolo11n.pt` preentrenado con [`bytetrack-cenital.yaml`](bytetrack-cenital.yaml), `--conf 0.05`, `--confirmacion 2` y margen de 5 px. El ajustado de oficina **no se despliega**: en Kaggle y PAMELA rinde peor que el base (tarea 10).
- **Resultados en vivo:** `--progreso RUTA.json` reescribe, durante la ejecución, los cruces confirmados y la medición parcial. Si aparece un archivo `cancelar` en la misma carpeta, el pipeline se detiene con código 3. La API usa esto para su estado y su cancelación.
- **Ritmo real:** `--ritmo-real` lee el video a su velocidad original, como una cámara. Si el modelo se atrasa, toma el cuadro más reciente y descarta los viejos, así el retraso queda acotado.
  - **Costo en calidad:** en CPU se pierden cruces (ver [la medición](../docs/relevo/2026-11-08-claude-cierre-final/README.md)).
- **Medición:** el `.config.json` incluye, en `medicion`, ms por cuadro de cada etapa (`lectura`, `rastreo`, `conteo`, `entrega`), la latencia por cuadro (media, p95, máxima, primer y último décimo) y los cuadros descartados.
- **Calidad y limitaciones:** en [`data/README.md`](../data/README.md) y en el informe.

## Estado al 6 de noviembre (histórico)

| Parte | Estado |
|---|---|
| Regla de cruces (`cruces.py`) | Probada con trayectorias de ejemplo. |
| Pipeline (`pipeline.py`) | Ejecutado sobre un clip sintético y sobre el clip real. |
| Primer clip | Entregado con el detector base. Ver [su relevo](../docs/relevo/vision-primer-clip/README.md). |
| API y panel | Primer clip probado por HTTP y en el panel: 0 → 1 pasajero (5 %) → 0. Las demás predicciones pasan el contrato de la API en las pruebas. |
| Ajuste del detector (`train.py`) | **Hecho sobre el video de oficina: 20 de 20 cruces, sin falsos positivos, pero en una sola grabación.** Ver [su relevo](../docs/relevo/vision-ajuste-detector/README.md). |
| Evaluador (`evaluation/evaluate.py`) | Probado. |
| Material para el informe | Redactado para Álvaro en [`aportes-vision.md`](../docs/informe/aportes-vision.md): metodología, tabla, caso de pérdida de ID, limitaciones y referencias. Falta compilarlo. |
| Métricas para el informe | **Pendientes.** Faltan grabaciones independientes y casos con varias personas a la vez. |
| Revisión humana de las cajas y los cruces | **Pendiente.** |

Las pruebas pasan con `pytest` en Python 3.12.16 sobre macOS (Apple M4). Sin las dependencias de visión se omiten las que las necesitan, así que el entorno de `requirements.txt` sigue funcionando. Todavía no se probó en Windows.

## Regla de conteo

- **Punto del cuerpo.** El centro de la caja decide de qué lado está la persona. `--punto pies` usa el borde inferior.
- **Lado confirmado.** Hacen falta `--confirmacion` cuadros seguidos a más de `--margen` píxeles de la línea. Dentro de ese margen el estado no cambia, así que temblar sobre la línea no cuenta. Una oscilación que sale del margen y confirma ambos lados **sí** genera eventos. Es compatible con los falsos de PAMELA B, aunque no se verificó caso por caso.
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
- **Pesos base.** `yolo11n.pt` (5.613.764 bytes, SHA-256 `0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1`), preentrenado con COCO. Ultralytics lo descarga en la carpeta actual la primera vez, desde `https://github.com/ultralytics/assets/releases/download/v8.4.0/yolo11n.pt`. Para la defensa dejalo en la raíz, porque git lo ignora y debe estar disponible sin internet.
- **Pesos ajustados.** Se obtienen con `train.py`. Tamaño y huella en [el relevo del ajuste](../docs/relevo/vision-ajuste-detector/README.md).
- **Clip.** Cómo obtenerlo y sus condiciones de uso están en [`data/README.md`](../data/README.md).
- **Telemetría.** Ultralytics envía analíticas anónimas por defecto. Se desactivan con `yolo settings sync=False`.
- **Licencia.** Ultralytics se distribuye con AGPL-3.0.

## Ejecutar

Con el detector ajustado sobre el video de oficina, desde la raíz y con el entorno activado:

```sh
python -m vision.pipeline \
  --video data/raw/oficina.mp4 --inicio 0 --fin 6 \
  --recorte 228,2,222,176 --linea 0,90,221,90 --interior arriba \
  --dispositivo cpu --pesos runs/oficina-ajuste/oficina-ajustado.pt \
  --salida runs/oficina-00-06.json --video-anotado runs/oficina-00-06.mp4
```

- `--recorte` se mide en píxeles del cuadro completo y `--linea` en píxeles del recorte, con origen arriba a la izquierda.
- `--interior arriba` significa que abajo → arriba es `subida`.
- La salida usa el esquema de [la referencia manual](../docs/demo/oficina-00-06-manual.json).
- Junto a la salida queda un `.config.json` con el comando, el recorte, la línea, el sistema de coordenadas, los parámetros, los FPS medidos y las versiones.
- `runs/` y los `.mp4` están fuera de git, así que el video anotado se regenera con el comando.
- Este modelo se especializó en esta escena: con otras cámaras, compará con `yolo11n.pt` antes de usarlo.
- [`bytetrack-cenital.yaml`](bytetrack-cenital.yaml) se calibró para el detector base y agrega falsos positivos con el ajustado.

## Ajustar el detector

1. **Proponer cajas:** `python -m vision.proponer_cajas` resta el fondo de una cámara fija y genera propuestas. Sirve para una persona a la vez.
2. **Revisarlas:** `python -m vision.revisar_cajas` genera hojas con cada cuadro numerado. Se corrige el JSON en `data/annotations/`.
3. **Entrenar:** `python -m vision.train` arma el dataset, entrena y guarda parámetros, versiones y métricas.
4. **Comparar:** `python -m evaluation.evaluate` compara una predicción con los cruces de referencia. `python -m evaluation.comparar_oficina` repite la comparación completa de este video.

Los comandos exactos están en [el relevo del ajuste](../docs/relevo/vision-ajuste-detector/README.md).

## Pruebas

```sh
python -m pytest tests -v
```

[`tests/test_pipeline_modelo.py`](../tests/test_pipeline_modelo.py) ejecuta el camino completo con el modelo real, sobre un clip sintético y sobre el ensayo de oficina. Cada prueba se omite si falta lo que necesita: las dependencias de visión, los pesos o el clip.

## Velocidad de referencia

Con `yolo11n` en un Apple M4:

- **Clip sintético** (180 cuadros, recorte de 640×360, sin video anotado): 46 FPS con `--dispositivo cpu` y 28 FPS con `--dispositivo mps`.
- **Video de oficina** (1316 cuadros, recorte de 222×176, CPU, sin video anotado): 41 FPS, con el detector base y con el ajustado.

Sirve solo para comprobar que corre. Los FPS del informe se miden en la máquina de defensa.
