# aitrabajo · Conteo de pasajeros y ocupación del bus

TP final de Inteligencia Aplicada (proyecto 10 de [`contexto.md`](contexto.md)). El sistema cuenta subidas y bajadas en la puerta de un bus a partir de video, con YOLO11n, ByteTrack y una línea virtual. Con esos eventos calcula la carga y el porcentaje de ocupación por parada, también mientras el video se procesa.

**Estado al 9 nov.:** qué cumple y qué falta de la consigna, con evidencia, en [la matriz de requisitos](docs/relevo/2026-11-08-claude-cierre-final/matriz.md). Las cifras de calidad, en [data/README.md](data/README.md) y en el informe ([`docs/informe/`](docs/informe/)).

## Componentes

```text
vision/pipeline.py     Lectura del video, YOLO11n + ByteTrack, regla de cruce, video anotado, progreso en vivo
vision/cruces.py       Regla de conteo (margen y confirmación), probada con trayectorias escritas a mano
vision/train.py        Ajuste reproducible del detector (se evaluó y no se despliega: ver data/README.md)
evaluation/evaluate.py Aciertos, omisiones, falsos positivos, precisión, exhaustividad y F1 por sentido (±1 s)
api/main.py            FastAPI: /ocupacion, videos, procesamientos en segundo plano, estado, cancelación
ui/app.py              Streamlit: recorridos JSON, demo de oficina y video nuevo con resultados en vivo
data/                  Origen, permisos, hashes, particiones y anotaciones (los videos no se versionan)
docs/demo/             Recorridos simulados y guion de la defensa
docs/informe/          Informe IEEE (fuente y PDF)
Dockerfile, docker-compose.yml   API y panel con visión en CPU
```

## Insumos que Git no versiona

- **Pesos `yolo11n.pt`** en la raíz: los oficiales de Ultralytics 8.4.0, 5.613.764 bytes. Ultralytics los descarga solo con `python -c "from ultralytics import YOLO; YOLO('yolo11n.pt')"`.
- **Videos en `data/raw/`:** origen y hash de cada uno en [data/README.md](data/README.md). Para la demo alcanzan `prueba-bus.mp4` (se sube desde el panel) y `oficina.mp4` (demo de oficina).

## Ejecutar en Windows (PowerShell, Python 3.12)

Desde la raíz del repo:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r vision\requirements.txt
.\.venv\Scripts\python.exe -m uvicorn api.main:app --port 8000
```

En otra terminal, en la misma carpeta:

```powershell
.\.venv\Scripts\python.exe -m streamlit run ui/app.py
```

Después:

- El **panel** queda en http://localhost:8501.
- El **contrato de la API** queda en http://localhost:8000/docs.

**Con GPU NVIDIA:** usá un entorno con torch para CUDA, por ejemplo `..\..\venv-gpu` (torch 2.14.1+cu130), el de la prueba final de la tarea 11. La primera vez, instalale también `requirements.txt`. Después arrancá la API con la GPU:

```powershell
$env:VISION_DISPOSITIVO = "cuda:0"
C:\Users\Alvaro\Desktop\Facultad\4to\IA\venv-gpu\Scripts\python.exe -m uvicorn api.main:app --port 8000
```

Sin esa variable, se usa la CPU de la configuración guardada.

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

**Antes:** con Docker Desktop iniciado y el motor Linux disponible, dejá `yolo11n.pt` en la raíz. Opcional: `data/raw/oficina.mp4`, para la demo de oficina.

Desde la raíz:

```powershell
docker compose up --build
```

- **Panel** en http://127.0.0.1:8502; **API** en http://127.0.0.1:8001/docs.
- **Imagen:** trae visión para CPU (torch 2.15.0+cpu, OpenCV y Ultralytics) y los pesos.
- **Volúmenes:** `runs/` guarda ejecuciones y videos subidos; `data/raw/` se monta de solo lectura.
- **Arranque:** los dos servicios tienen comprobación de salud, y el panel espera a la API.
- **Para cerrar:** `docker compose down`.

**Comprobación pendiente:** en la máquina donde se escribió esta versión no se pudo construir la imagen, porque la red bloqueaba Docker Hub. Para comprobarla:

1. Ejecutá `docker compose up --build`.
2. Subí `prueba-bus.mp4` en «Video nuevo».
3. Procesalo y confirmá que aparezcan cruces mientras corre y el video anotado al final.

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest -q -rxs
```

**Fallos que quedan, a propósito:**

- `test_ensayo_de_oficina_…` **falla**: es la bajada omitida en oficina, un defecto conocido de detección que se dejó visible ([caso](docs/casos-deteccion/oficina-bajada-omitida/README.md)).
- `test_una_persona_con_tres_cajas_…` es **xfail**: varias cajas sobre una persona cuentan varios cruces.

## Más documentación

- [vision/README.md](vision/README.md): regla de conteo, parámetros y comandos de visión.
- [data/README.md](data/README.md): grabaciones, permisos, revisiones y qué sigue reservado.
- [docs/demo/guion.md](docs/demo/guion.md): defensa de 10 + 2 minutos, con la demo en vivo y el respaldo.
- [`docs/relevo/`](docs/relevo/): registro fechado de cada tarea. Los registros antiguos describen el estado de su fecha.
