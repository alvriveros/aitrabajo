# aitrabajo · Conteo de pasajeros y ocupación del bus

Trabajo final de Inteligencia Artificial (4.º año, Ingeniería Informática; proyecto 10 de la [consigna](contexto.md)). El sistema cuenta subidas y bajadas en la puerta de un bus a partir de video, con **YOLO11n** (detección de personas), **ByteTrack** (seguimiento) y una **línea virtual** (regla de cruce). Con esos eventos calcula la carga y el porcentaje de ocupación por parada, también mientras el video se procesa.

**Estado: prototipo funcional con limitaciones medidas.** El conteo en escenas densas no está resuelto (F1 de 0,36 y 0,45), no se consiguieron grabaciones de buses de Paraguay accesibles y el tiempo real se demostró solo con GPU nativa, emulando la cámara con un archivo de video. Informe IEEE: [`docs/informe/informe.pdf`](docs/informe/informe.pdf).

## Entregables (punto 1 de la consigna)

| Entregable | Dónde | Estado |
|---|---|---|
| Dataset limpio y documentado | [`data/README.md`](data/README.md) y [`data/annotations/`](data/annotations/) | Origen, licencia, hash, partición y uso real de cada grabación; anotaciones de cruces y cajas, con quién las hizo (persona o IA) y su revisión. Los videos no se redistribuyen. **No hay datos de Paraguay.** |
| Modelo entrenado con métricas formales | [`vision/train.py`](vision/train.py), [`vision/ajuste-detector.md`](vision/ajuste-detector.md), [`evaluation/`](evaluation/) | Detector ajustado por el equipo (mAP50 0,995 y mAP50-95 0,753 en la reserva de su misma grabación) que **no generaliza**; se despliega YOLO11n preentrenado con el seguimiento calibrado. TP, FP, FN, precisión, exhaustividad y F1 por grabación; MAE y RMSE de la carga en un clip. |
| API REST | [`api/main.py`](api/main.py) (FastAPI) | Ocupación por parada, subida y validación de videos, procesamiento en segundo plano con estado, cancelación y resultados. |
| UI interactiva | [`ui/app.py`](ui/app.py) (Streamlit) | Recorridos JSON, demo de oficina y video nuevo con resultados en vivo. |
| Dockerfile y docker-compose.yml | [`Dockerfile`](Dockerfile), [`docker-compose.yml`](docker-compose.yml) | `docker compose up --build` levanta API y panel (visión en CPU) y prepara los pesos oficiales verificando su SHA-256. |

### Modelo entrenado y modelo desplegado

| | Modelo entrenado por el equipo | Modelo desplegado |
|---|---|---|
| Pesos | `oficina-ajustado.pt` (YOLO11n ajustado 40 épocas con 131 cuadros de oficina), SHA-256 `69958946…` (reproducción en Windows; la original del compañero, en macOS, tiene SHA-256 `783d16c0…`); no se versiona | `yolo11n.pt` oficial (COCO), SHA-256 `0ebbc80d…`; lo prepara `vision/pesos.py` |
| Métricas de detección | mAP50 0,995 y mAP50-95 0,753 en 34 cuadros de reserva **de la misma grabación** | — (preentrenado) |
| Conteo (F1, ±1 s) | Oficina 1,00 (su grabación); Kaggle 0,00; PAMELA A 0,07 | Oficina 0,71; Kaggle 0,53; PAMELA A 0,51; bus real 0,48; `prueba-bus` 0,67 (ciega, CPU); PAMELA B 0,36 y 0,45 |

Detalle, reproducción y procedencia de cada cifra: [`evaluation/results/README.md`](evaluation/results/README.md).

## Estructura

```text
api/main.py            FastAPI: /ocupacion, videos, procesamientos en segundo plano, estado, cancelación
ui/app.py              Streamlit: recorridos JSON, demo de oficina y video nuevo con resultados en vivo
vision/pipeline.py     Lectura del video, YOLO11n + ByteTrack, regla de cruce, video anotado, progreso en vivo
vision/cruces.py       Regla de conteo (margen y confirmación)
vision/train.py        Ajuste reproducible del detector
vision/pesos.py        Descarga y verificación de los pesos oficiales
evaluation/            Evaluador (evaluate.py), curva de ocupación y resultados que respaldan el informe
data/                  Procedencia, permisos, hashes, particiones y anotaciones (los videos no se versionan)
tests/                 Pruebas automáticas (pytest)
docs/informe/          Informe IEEE: PDF, fuente, bibliografía y figuras
docs/demo/             Recorridos simulados, guion y preparación de la defensa
docs/casos-deteccion/  Casos de error documentados
Dockerfile, docker-compose.yml
```

## Insumos que Git no versiona

- **Pesos `yolo11n.pt`** en la raíz: los oficiales de Ultralytics (release `v8.4.0` de `ultralytics/assets`, 5.613.764 bytes, SHA-256 `0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1`). `python vision/pesos.py` los descarga y verifica; si ya están, solo comprueba el hash y falla con un mensaje claro si no coincide. La imagen de Docker hace lo mismo al construirse.
- **Videos en `data/raw/`:** origen, hash e instrucciones de obtención de cada uno en [data/README.md](data/README.md). Para la demo alcanzan `prueba-bus.mp4` (se sube desde el panel) y `oficina.mp4` (demo de oficina). **No se versionan ni se redistribuyen**: `prueba-bus` es una vista previa de iStock sin licencia verificada; oficina y el bus real son de YouTube sin licencia abierta; Kaggle tiene licencia desconocida; PAMELA es solo para investigación.
- **Pesos ajustados** (`runs/oficina-ajuste-windows/oficina-ajustado.pt`): se reproducen con `vision/train.py` (comando en [`evaluation/results/README.md`](evaluation/results/README.md)).
- **Ejecuciones** (`runs/`): las genera la API. La primera evaluación de `prueba-bus` está copiada, sin cambios, en `evaluation/results/prueba-bus-cpu-ciega/`.

## Instalar y ejecutar (Python 3.12)

Windows (PowerShell), desde la raíz del repositorio:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r vision\requirements.txt
.\.venv\Scripts\python.exe vision\pesos.py
.\.venv\Scripts\python.exe -m uvicorn api.main:app --port 8000
```

En otra terminal, en la misma carpeta:

```powershell
.\.venv\Scripts\python.exe -m streamlit run ui/app.py
```

En Linux o macOS, los mismos comandos con `python3 -m venv .venv` y `.venv/bin/python`.

- **Panel:** http://localhost:8501. **Contrato de la API:** http://localhost:8000/docs.
- **Con GPU NVIDIA:** instalá en otro entorno torch para CUDA (se midió con torch 2.14.1+cu130) y las dependencias, y arrancá la API con `VISION_DISPOSITIVO=cuda:0`. Sin esa variable se usa la CPU.

## Usar el panel

1. **«Archivo JSON o demo».** Elegí «Línea simulada de 8 paradas» y mové el selector de tiempo: muestra carga, porcentaje por parada y sobreocupación (105 % en la parada 4). Es un recorrido **simulado**, no medido.
2. **«Video nuevo».**
   - Subí un video; se valida formato, tamaño (200 MB), duración (5 min) y legibilidad.
   - Ubicá recorte, línea e interior con la vista previa, que **no ejecuta el modelo**.
   - Pulsá «Procesar video».
3. **Mientras procesa,** el panel consulta la API cada segundo. Muestra subidas, bajadas, pasajeros y ocupación, el avance y el retraso respecto del video, y permite **cancelar**. Recargar la página no reinicia el trabajo: el panel lo retoma.
4. **«Simular cámara en vivo (ritmo real)»** lee el video a su velocidad original. Si el equipo no alcanza, descarta cuadros viejos en lugar de acumular retraso. La medición queda en la configuración de la ejecución (`medicion.latencia_ms`, `cuadros_descartados`).
5. **Resultados guardados.**
   - «Procesar video» no repite una configuración ya procesada: muestra el resultado guardado y lo rotula así.
   - «Reprocesar en vivo para demostración» ejecuta de nuevo y lo guarda aparte, sin tocar la primera evaluación.

**API** (detalle en `/docs`):

| Endpoint | Para qué |
|---|---|
| `POST /ocupacion` | Ocupación por parada a partir de eventos |
| `POST /videos?nombre=…` | Subir un video (cuerpo crudo) |
| `GET /videos/{id}/cuadro` | Vista previa de la geometría, sin inferencia |
| `POST /videos/{id}/procesamientos` | Iniciar un procesamiento; responde 202 con el id |
| `GET /procesamientos/{id}/estado` | Estado y cruces parciales |
| `POST /procesamientos/{id}/cancelar` | Cancelar |
| `GET /procesamientos/actual` | Procesamiento en curso |
| `GET /procesamientos[/{id}[/video]]` | Ejecuciones publicadas |

**Límites de la API:**

- un procesamiento a la vez: un segundo pedido recibe 409;
- solo se publica lo que terminó bien.

**Limpieza:** las ejecuciones (`runs/panel/`) y los videos subidos (`runs/videos/`) no se borran solos. Borrá esas carpetas a mano cuando ya no las necesites.

## Ejecutar con Docker

Con Docker Desktop (motor Linux) y acceso a internet, desde la raíz:

```sh
docker compose up --build
```

- **Panel** en http://127.0.0.1:8502; **API** en http://127.0.0.1:8001/docs. Para cerrar: `docker compose down`.
- **Imagen:** visión para CPU (torch 2.15.0+cpu, OpenCV y Ultralytics). El build descarga los pesos oficiales y verifica su SHA-256: si no coincide, falla. No hace falta `yolo11n.pt` local.
- **Volúmenes:** `runs/` guarda ejecuciones y videos subidos; `data/raw/` se monta de solo lectura (opcional, para la demo de oficina).
- **Docker usa CPU:** empaqueta y prueba el flujo, pero no alcanza el tiempo real.

**Verificaciones:**
- Windows, 8 nov.: los dos servicios `healthy` y `prueba-bus` procesado dentro del contenedor ([`evaluation/results/docker-windows/`](evaluation/results/docker-windows/)), con la versión anterior del Dockerfile, que copiaba `yolo11n.pt`.
- Copia limpia en Linux, 10 nov.: build sin `yolo11n.pt` local, pesos descargados y verificados, servicios `healthy` y `prueba-bus` procesado (24 eventos, 12/12/0). **No valida el Dockerfile tal como se entrega:** Docker Hub respondió 429 y el índice de PyTorch estaba bloqueado, así que se usaron una base Ubuntu 24.04 con Python 3.12 y torch de PyPI.

## Evaluar

```sh
python -m evaluation.evaluate --referencia data/annotations/prueba-bus-cruces.json --prediccion evaluation/results/prueba-bus-cpu-ciega/prediccion.json
python -m evaluation.curva_ocupacion
```

El primero compara cruces (±1 s por sentido); el segundo recalcula la Fig. 2 del informe (cambio acumulado de pasajeros, MAE 2,68 y RMSE 3,31 para ese clip) sin ejecutar el modelo. No se informa accuracy ni matriz de confusión: la evaluación por eventos no define verdaderos negativos.

## Pruebas

```sh
python -m pytest -q -rxs
```

Con `oficina.mp4` y `prueba-bus.mp4` en `data/raw/` y los pesos ajustados en `runs/`, el resultado esperado es **1 fallido y 1 xfail**, que se dejan visibles a propósito:

- `test_ensayo_de_oficina_…` **falla**: la bajada omitida en oficina, un defecto conocido de detección ([caso](docs/casos-deteccion/oficina-bajada-omitida/README.md)).
- `test_una_persona_con_tres_cajas_…` es **xfail**: varias cajas sobre una persona cuentan varios cruces.

Sin los videos o los pesos ajustados, las pruebas que los necesitan se omiten.

## Limitaciones conocidas

- **Calidad del conteo:** duplica eventos con cajas encimadas o filas que oscilan sobre la línea, y omite cruces cuando la detección se pierde en la puerta. No alcanza para auditar un servicio.
- **Datos:** no hay grabaciones de Paraguay; se usaron oficina, puertas de tren y pocos videos de bus. Las pruebas independientes se consumieron; PAMELA B es la misma escena que PAMELA A.
- **Plataforma:** la evaluación ciega en CPU dio 24 eventos; las ejecuciones en GPU, 25. El resultado depende de la plataforma.
- **Tiempo real:** solo en GPU nativa, con la cámara emulada por un archivo. En CPU y en Docker se descartan cuadros y se pierden cruces.

## Más documentación

- [data/README.md](data/README.md): grabaciones, permisos, revisiones y particiones.
- [vision/README.md](vision/README.md): regla de conteo, parámetros y comandos de visión.
- [evaluation/results/README.md](evaluation/results/README.md): fuente de cada cifra del informe.
- [docs/README.md](docs/README.md): índice de la documentación; [docs/demo/guion.md](docs/demo/guion.md): defensa con demo en vivo.

El historial de desarrollo (consignas para agentes, relevos por tarea y borradores) se retiró de esta versión y se conserva en el historial de Git.
