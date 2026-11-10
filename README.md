# aitrabajo · Conteo de pasajeros y ocupación del bus

TP final de Inteligencia Artificial (proyecto 10 de [`contexto.md`](contexto.md)). El sistema cuenta subidas y bajadas en la puerta de un bus a partir de video, con YOLO11n, ByteTrack y una línea virtual. Con esos eventos calcula la carga y el porcentaje de ocupación por parada, también mientras el video se procesa.

**Estado al 9 nov.: prototipo funcional con limitaciones medidas.** El conteo en escenas densas no está resuelto (F1 de 0,36 y 0,45), no se consiguieron grabaciones de buses de Paraguay accesibles y el tiempo real se demostró solo con GPU nativa, emulando la cámara con un archivo de video.

**Versión que se entrega:** la punta de la rama `cierre-final` en `TpFinal\.worktrees\integracion-video` (no la raíz `TpFinal`, que tiene una versión antigua). El informe es `docs/informe/informe.pdf`. qué cumple y qué falta de la consigna, con evidencia, en [la matriz de requisitos](docs/relevo/2026-11-08-claude-cierre-final/matriz.md). Las cifras de calidad, en [data/README.md](data/README.md) y en el informe ([`docs/informe/`](docs/informe/)).

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

- **Pesos `yolo11n.pt`** en la raíz: los oficiales de Ultralytics (release `v8.4.0` de `ultralytics/assets`, 5.613.764 bytes, SHA-256 `0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1`). `python vision/pesos.py` los descarga y verifica; si ya están, solo comprueba el hash y falla con un mensaje claro si no coincide. La imagen de Docker hace lo mismo al construirse.
- **Videos en `data/raw/`:** origen y hash de cada uno en [data/README.md](data/README.md). Para la demo alcanzan `prueba-bus.mp4` (se sube desde el panel) y `oficina.mp4` (demo de oficina). **No se versionan ni se redistribuyen**: `prueba-bus` es una vista previa de iStock sin licencia verificada; oficina y el bus real son de YouTube sin licencia abierta; Kaggle tiene licencia desconocida; PAMELA es solo para investigación. Cada equipo tiene que conseguirlos por su cuenta.
- **Entorno con GPU** (`venv-gpu`, torch 2.14.1+cu130): fuera del repositorio; es el único donde se demostró tiempo real.

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

**Antes:** con Docker Desktop iniciado, el motor Linux disponible y acceso a internet (el build descarga paquetes y los pesos oficiales de GitHub, y verifica su SHA-256; si el hash no coincide, el build falla). Ya no hace falta dejar `yolo11n.pt` en la raíz. Opcional: `data/raw/oficina.mp4`, para la demo de oficina.

Desde la raíz:

```powershell
docker compose up --build
```

- **Panel** en http://127.0.0.1:8502; **API** en http://127.0.0.1:8001/docs.
- **Imagen:** trae visión para CPU (torch 2.15.0+cpu, OpenCV y Ultralytics) y los pesos verificados.
- **GPU en Docker:** `docker-compose.gpu.yml` existe en la copia local de Álvaro, **sin versionar ni validar**. No es parte de la entrega.
- **Volúmenes:** `runs/` guarda ejecuciones y videos subidos; `data/raw/` se monta de solo lectura.
- **Arranque:** los dos servicios tienen comprobación de salud, y el panel espera a la API.
- **Para cerrar:** `docker compose down`.

**Docker usa CPU:** sirve para empaquetar y probar el flujo, pero no alcanza el tiempo real. Para eso, usá la ejecución nativa con GPU de la sección anterior.

**Verificado en Windows** (8 nov., 23:24, con la versión anterior que copiaba `yolo11n.pt`): los dos servicios quedaron `healthy`, y `prueba-bus` se subió y se procesó dentro del contenedor (`docs/relevo/2026-11-08-claude-cierre-final/resultados/docker-windows/`). OpenCV avisa `tag 'VP80' is not supported`, pero el `.webm` se genera bien.

**Verificado desde una copia limpia** (10 nov., Claude, contenedor Linux sin GPU): se extrajeron solo los archivos versionados, sin `yolo11n.pt` ni `runs/`. El build descargó los pesos y verificó su SHA-256; los dos servicios quedaron `healthy`; `prueba-bus` se subió y procesó por la API (24 eventos, 12/12/0, F1 0,67; el doble pedido y la repetición respondieron 409, y la cancelación no se publicó). **Dos desvíos del entorno, no del proyecto:** Docker Hub respondió 429, así que `python:3.12-slim` se sustituyó por una base Ubuntu 24.04 con Python 3.12.3; y `download.pytorch.org` estaba bloqueado, así que se usó `--build-arg TORCH_INDEX=https://pypi.org/simple` (torch 2.15.0 de PyPI, ejecutado en CPU). Falta repetir `docker compose up --build` en Windows con la base y el índice oficiales.

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest -q -rxs
```

**Resultado histórico** (Windows, 9 nov., commit `b60b615`): 139 aprobados, **1 fallido** y **1 xfail**, ningún omitido. Es el registro de esa fecha, no una ejecución nueva.

**Ejecución del cierre** (10 nov., Claude, copia limpia en Linux, Python 3.12.3, torch 2.15.0 en CPU, con `prueba-bus.mp4` y `oficina.mp4`): **142 aprobados, 1 fallido, 1 omitido y 1 xfail**. Hay 4 pruebas nuevas (curva de ocupación y pesos) y aprueban. El omitido necesita los pesos ajustados de oficina, que no se versionan; en Windows existen y esa prueba aprobaba. **La suite no está completamente verde.**

**Fallos que quedan, a propósito:**

- `test_ensayo_de_oficina_…` **falla**: es la bajada omitida en oficina, un defecto conocido de detección que se dejó visible ([caso](docs/casos-deteccion/oficina-bajada-omitida/README.md)).
- `test_una_persona_con_tres_cajas_…` es **xfail**: varias cajas sobre una persona cuentan varios cruces.

## Más documentación

- [vision/README.md](vision/README.md): regla de conteo, parámetros y comandos de visión.
- [data/README.md](data/README.md): grabaciones, permisos, revisiones y qué sigue reservado.
- [docs/demo/guion.md](docs/demo/guion.md): defensa de 10 + 2 minutos, con la demo en vivo y el respaldo.
- [docs/README.md](docs/README.md): índice de la documentación, que separa lo vigente de lo histórico.
- [`docs/relevo/`](docs/relevo/): registro fechado de cada tarea. Los registros antiguos describen el estado de su fecha.
