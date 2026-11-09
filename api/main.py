import hashlib
import json
import os
import shlex
import subprocess
import sys
import threading
import uuid
from datetime import datetime
from importlib.util import find_spec
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi import Path as Ruta
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field

from vision.cruces import Linea

app = FastAPI(title="Ocupación del bus")

RAIZ = Path(__file__).resolve().parents[1]
# Configuración guardada junto a la predicción de 0–6 s: video, tramo, recorte, línea, pesos y rastreador.
CONFIG_DEMO = RAIZ / "evaluation/results/oficina-00-06-prediccion.config.json"
EJECUCIONES = RAIZ / "runs/panel"
ID_EJECUCION = r"^\d{8}-\d{6}-\d{6}$"
COMPLETA = "completa"  # se escribe al final de una ejecución exitosa y legible; sin ella no se publica
VIDEOS = RAIZ / "runs/videos"  # videos subidos desde el panel, uno por carpeta (id = inicio del SHA-256)
ID_VIDEO = r"^[0-9a-f]{16}$"
FORMATOS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
MAX_BYTES = 200 * 1024 * 1024  # el mismo límite de subida que trae Streamlit
MAX_DURACION_S = 300
TIMEOUT_DEMO_S, TIMEOUT_VIDEO_S = 600, 1800
SISTEMA_DE_COORDENADAS = ("Píxeles enteros, origen arriba a la izquierda, x hacia la derecha, y hacia abajo. "
                          "El recorte X,Y,ANCHO,ALTO se mide en el cuadro completo; la línea X1,Y1,X2,Y2, en el recorte.")
ORIGEN_TEMPORAL = "tiempo_s = segundos desde el primer cuadro del video, según las marcas de tiempo del archivo."
# Del comando guardado de la demo se toman solo las opciones del modelo y del rastreador (configuración de la API).
OPCIONES_DE_ESCENA = {"--video", "--inicio", "--fin", "--recorte", "--linea", "--interior", "--parada",
                      "--salida", "--video-anotado", "--capacidad", "--carga-inicial"}
_procesando = threading.Lock()  # un procesamiento a la vez: evita duplicados por reintentos o clics repetidos
_trabajo = {}  # el procesamiento en curso: {"id", "hilo"}; las pruebas esperan el hilo
CODIGO_CANCELADO = 3  # el mismo de vision.pipeline
# Dispositivo del modelo para videos y demo (cpu, cuda:0…). Sin valor, el de la configuración guardada.
DISPOSITIVO = os.getenv("VISION_DISPOSITIVO")


class Evento(BaseModel):
    tiempo_s: float = Field(ge=0, allow_inf_nan=False)
    track_id: int
    sentido: Literal["subida", "bajada"]


class Parada(BaseModel):
    nombre: str = Field(min_length=1)
    inicio_s: float = Field(ge=0, allow_inf_nan=False)


class Recorrido(BaseModel):
    capacidad: int = Field(gt=0)
    carga_inicial: int = Field(ge=0)
    paradas: list[Parada] = Field(min_length=1)
    eventos: list[Evento]


@app.post("/ocupacion")
def calcular(recorrido: Recorrido):
    """Cada parada abarca desde su inicio hasta el inicio de la siguiente."""
    inicios = [p.inicio_s for p in recorrido.paradas]
    if inicios[0] != 0 or any(a >= b for a, b in zip(inicios, inicios[1:])):
        raise HTTPException(422, "Las paradas deben empezar en 0 y avanzar en el tiempo.")

    pasajeros = recorrido.carga_inicial
    filas = []
    avisos = []
    indice = 0
    for numero, parada in enumerate(recorrido.paradas):
        fin = inicios[numero + 1] if numero + 1 < len(inicios) else float("inf")
        subidas = bajadas = 0
        while indice < len(recorrido.eventos):
            evento = recorrido.eventos[indice]
            if indice and evento.tiempo_s < recorrido.eventos[indice - 1].tiempo_s:
                raise HTTPException(422, "Los eventos deben estar en orden temporal.")
            if evento.tiempo_s >= fin:
                break
            if evento.sentido == "subida":
                subidas += 1
                pasajeros += 1
            else:
                bajadas += 1
                pasajeros -= 1
                if pasajeros < 0:
                    avisos.append(f"Conteo negativo en {parada.nombre} a los {evento.tiempo_s:g} s.")
            indice += 1
        filas.append(dict(parada=parada.nombre, subidas=subidas, bajadas=bajadas,
                          pasajeros=pasajeros, ocupacion_pct=round(100 * pasajeros / recorrido.capacidad, 2)))
    return {"paradas": filas, "avisos": avisos}


def argumentos_demo():
    """Argumentos del pipeline según la configuración guardada, sin sus destinos originales."""
    argv = shlex.split(json.loads(CONFIG_DEMO.read_text(encoding="utf-8"))["comando"])[3:]
    return [parte for clave, valor in zip(argv[::2], argv[1::2])
            if clave not in ("--salida", "--video-anotado") for parte in (clave, valor)]


def leer_ejecucion(carpeta):
    leer = lambda nombre: json.loads((carpeta / nombre).read_text(encoding="utf-8"))
    entrada = leer("entrada.json") if (carpeta / "entrada.json").is_file() else None
    return {"id": carpeta.name, "recorrido": leer("prediccion.json"), "configuracion": leer("prediccion.config.json"),
            "entrada": entrada}


def comprobar_insumos(opciones, archivos):
    faltan = [opciones[c] for c in archivos if not (RAIZ / opciones[c]).is_file()]
    if find_spec("ultralytics") is None:
        faltan.append("dependencias de vision/requirements.txt")
    if faltan:
        raise HTTPException(503, "Faltan insumos para procesar el video: " + ", ".join(faltan) + ".")


def escribir_estado(carpeta, estado, detalle=None):
    temporal = carpeta / "estado.tmp"
    temporal.write_text(json.dumps({"estado": estado, "detalle": detalle}, ensure_ascii=False), encoding="utf-8")
    os.replace(temporal, carpeta / "estado.json")


def correr_pipeline(argv, timeout, entrada=None):
    """Inicia vision.pipeline en una carpeta nueva, fuera de la petición HTTP, y devuelve su id enseguida.

    El estado y los cruces parciales se consultan en GET /procesamientos/{id}/estado. La ejecución solo se
    publica en la lista si terminó bien y su resultado se puede leer.
    """
    if not _procesando.acquire(blocking=False):
        raise HTTPException(409, "Ya hay un procesamiento en curso. Esperá a que termine o cancelalo.")
    try:
        carpeta = EJECUCIONES / datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        carpeta.mkdir(parents=True)
        if entrada is not None:
            (carpeta / "entrada.json").write_text(json.dumps(entrada, ensure_ascii=False, indent=2), encoding="utf-8")
        comando = [sys.executable, "-m", "vision.pipeline", *argv, "--progreso", str(carpeta / "progreso.json"),
                   "--salida", str(carpeta / "prediccion.json"), "--video-anotado", str(carpeta / "anotado.webm")]
        escribir_estado(carpeta, "en_curso")
        hilo = threading.Thread(target=_ejecutar, args=(carpeta, comando, timeout), daemon=True)
        _trabajo.update(id=carpeta.name, hilo=hilo)
        hilo.start()
    except BaseException:
        _procesando.release()
        raise
    return {"id": carpeta.name, "estado": "en_curso"}


def _ejecutar(carpeta, comando, timeout):
    try:
        try:
            proceso = subprocess.run(comando, cwd=RAIZ, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired as error:
            guardar_registro(carpeta, error.stdout, error.stderr)
            return escribir_estado(carpeta, "error", f"El procesamiento superó los {timeout // 60} minutos.")
        guardar_registro(carpeta, proceso.stdout, proceso.stderr)
        if proceso.returncode == CODIGO_CANCELADO:
            return escribir_estado(carpeta, "cancelado", "Cancelado a pedido del usuario. No se publica.")
        if proceso.returncode:
            return escribir_estado(carpeta, "error",
                                   f"El pipeline terminó con código {proceso.returncode}: {proceso.stderr[-800:]}")
        try:
            leer_ejecucion(carpeta)
            if (carpeta / "anotado.webm").stat().st_size == 0:
                raise ValueError("video anotado vacío")
        except (OSError, ValueError, KeyError) as error:
            return escribir_estado(carpeta, "error", f"El pipeline terminó sin un resultado legible: {error}")
        (carpeta / COMPLETA).touch()
        escribir_estado(carpeta, "completa")
    except Exception as error:  # que un fallo inesperado no deje la ejecución «en curso» para siempre
        escribir_estado(carpeta, "error", f"Error inesperado al procesar: {error}")
    finally:
        _procesando.release()


@app.post("/procesamientos", status_code=202)
def procesar_demo():
    """Inicia vision.pipeline sobre el clip de demo; guarda predicción, configuración y video anotado."""
    argv = argumentos_demo()
    comprobar_insumos(dict(zip(argv[::2], argv[1::2])), ("--video", "--pesos"))
    return correr_pipeline(argv, TIMEOUT_DEMO_S)


def guardar_registro(carpeta, salida, error):
    """Conserva la salida del pipeline para diagnóstico, también si falló o se cortó."""
    texto = lambda x: x.decode(errors="replace") if isinstance(x, bytes) else (x or "")
    (carpeta / "registro.txt").write_text(texto(salida) + texto(error), encoding="utf-8")


def video_de(carpeta):
    """Id del video subido que procesó la ejecución, o None si es la demo de oficina."""
    entrada = carpeta / "entrada.json"
    return json.loads(entrada.read_text(encoding="utf-8"))["video_id"] if entrada.is_file() else None


@app.get("/procesamientos")
def listar_procesamientos(origen: Literal["demo", "video"] | None = None,
                          video: str | None = Query(None, pattern=ID_VIDEO)):
    """Ejecuciones guardadas, de la más reciente a la más antigua; se pueden filtrar por origen o por video."""
    if not EJECUCIONES.is_dir():
        return []
    ids = []
    for carpeta in EJECUCIONES.iterdir():
        if not (carpeta / COMPLETA).is_file():
            continue
        de = video_de(carpeta)
        if (origen == "demo" and de) or (origen == "video" and not de) or (video and de != video):
            continue
        ids.append(carpeta.name)
    return sorted(ids, reverse=True)


def carpeta_de(id_ejecucion):
    carpeta = EJECUCIONES / id_ejecucion
    if not (carpeta / COMPLETA).is_file():
        raise HTTPException(404, f"No existe la ejecución {id_ejecucion}.")
    return carpeta


@app.get("/procesamientos/actual")
def procesamiento_actual():
    """Id del procesamiento en curso, o null. El panel lo usa para retomarlo después de una recarga."""
    hilo = _trabajo.get("hilo")
    return {"id": _trabajo["id"] if hilo and hilo.is_alive() else None}


def carpeta_iniciada(id_ejecucion):
    carpeta = EJECUCIONES / id_ejecucion
    if not (carpeta / "estado.json").is_file():
        raise HTTPException(404, f"No existe la ejecución {id_ejecucion}.")
    return carpeta


@app.get("/procesamientos/{id_ejecucion}/estado")
def estado_procesamiento(id_ejecucion: str = Ruta(pattern=ID_EJECUCION)):
    """Estado (en_curso, completa, error, cancelado) y, mientras se procesa, los cruces y la medición parcial."""
    carpeta = carpeta_iniciada(id_ejecucion)
    estado = json.loads((carpeta / "estado.json").read_text(encoding="utf-8"))
    try:
        estado["progreso"] = json.loads((carpeta / "progreso.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):  # todavía no se procesó el primer cuadro
        estado["progreso"] = None
    return {"id": id_ejecucion, "video_id": video_de(carpeta), **estado}


@app.post("/procesamientos/{id_ejecucion}/cancelar", status_code=202)
def cancelar_procesamiento(id_ejecucion: str = Ruta(pattern=ID_EJECUCION)):
    """Pide al pipeline que se detenga en el próximo cuadro. Lo cancelado no se publica."""
    carpeta = carpeta_iniciada(id_ejecucion)
    estado = json.loads((carpeta / "estado.json").read_text(encoding="utf-8"))["estado"]
    if estado != "en_curso":
        raise HTTPException(409, f"La ejecución {id_ejecucion} ya terminó ({estado}).")
    (carpeta / "cancelar").touch()
    return {"id": id_ejecucion, "estado": "cancelando"}


@app.get("/procesamientos/{id_ejecucion}")
def consultar_procesamiento(id_ejecucion: str = Ruta(pattern=ID_EJECUCION)):
    return leer_ejecucion(carpeta_de(id_ejecucion))


@app.get("/procesamientos/{id_ejecucion}/video")
def video_procesado(id_ejecucion: str = Ruta(pattern=ID_EJECUCION)):
    video = carpeta_de(id_ejecucion) / "anotado.webm"
    if not video.is_file():
        raise HTTPException(404, f"La ejecución {id_ejecucion} no tiene video anotado.")
    return FileResponse(video, media_type="video/webm")


# ---------- Videos nuevos subidos desde el panel ----------

def abrir_video(ruta):
    """Propiedades del video o un error 4xx comprensible. OpenCV es una dependencia de visión."""
    if find_spec("cv2") is None:
        raise HTTPException(503, "Faltan las dependencias de vision/requirements.txt para leer videos.")
    import cv2

    captura = cv2.VideoCapture(str(ruta), cv2.CAP_FFMPEG)
    try:
        fps = captura.get(cv2.CAP_PROP_FPS) if captura.isOpened() else 0
        cuadros = int(captura.get(cv2.CAP_PROP_FRAME_COUNT)) if fps else 0
        ancho, alto = int(captura.get(cv2.CAP_PROP_FRAME_WIDTH)), int(captura.get(cv2.CAP_PROP_FRAME_HEIGHT))
        legible = captura.read()[0] if fps else False
    finally:
        captura.release()
    if not (fps and fps > 0 and cuadros > 0 and ancho > 0 and alto > 0 and legible):
        raise HTTPException(422, "No se pudo leer el video: el archivo está dañado o su formato no es compatible.")
    return {"fps": round(fps, 4), "cuadros": cuadros, "duracion_s": round(cuadros / fps, 2), "ancho": ancho, "alto": alto}


def info_de(id_video):
    carpeta = VIDEOS / id_video
    if not (carpeta / "info.json").is_file():
        raise HTTPException(404, f"No existe el video {id_video}. Subilo de nuevo.")
    return json.loads((carpeta / "info.json").read_text(encoding="utf-8"))


@app.post("/videos", status_code=201)
async def subir_video(request: Request, nombre: str = Query(min_length=1, max_length=200)):
    """Recibe el archivo crudo (no multipart), lo valida y lo guarda por su SHA-256: subir dos veces lo mismo no duplica."""
    extension = Path(nombre).suffix.lower()
    if extension not in FORMATOS:
        raise HTTPException(415, f"Formato no admitido ({extension or 'sin extensión'}). Usá {', '.join(sorted(FORMATOS))}.")
    VIDEOS.mkdir(parents=True, exist_ok=True)
    temporal = VIDEOS / f".subiendo-{uuid.uuid4().hex}{extension}"
    huella, tamano = hashlib.sha256(), 0
    try:
        with temporal.open("wb") as archivo:
            async for parte in request.stream():
                tamano += len(parte)
                if tamano > MAX_BYTES:
                    raise HTTPException(413, f"El video supera {MAX_BYTES // 2**20} MB.")
                huella.update(parte)
                archivo.write(parte)
        if not tamano:
            raise HTTPException(422, "El archivo está vacío.")
        propiedades = abrir_video(temporal)
        if propiedades["duracion_s"] > MAX_DURACION_S:
            raise HTTPException(413, f"El video dura {propiedades['duracion_s']:g} s; el máximo es {MAX_DURACION_S} s.")
        sha = huella.hexdigest()
        carpeta = VIDEOS / sha[:16]
        if (carpeta / "info.json").is_file():
            return info_de(sha[:16])
        carpeta.mkdir(exist_ok=True)
        temporal.replace(carpeta / f"video{extension}")
        info = {"id": sha[:16], "nombre_original": nombre, "archivo": f"video{extension}", "sha256": sha,
                "bytes": tamano, **propiedades, "subido": datetime.now().astimezone().isoformat(timespec="seconds"),
                "sistema_de_coordenadas": SISTEMA_DE_COORDENADAS, "origen_temporal": ORIGEN_TEMPORAL}
        (carpeta / "info.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
        return info
    finally:
        temporal.unlink(missing_ok=True)


@app.get("/videos/{id_video}")
def consultar_video(id_video: str = Ruta(pattern=ID_VIDEO)):
    return info_de(id_video)


class Geometria(BaseModel):
    recorte: tuple[int, int, int, int] = Field(description="X,Y,ANCHO,ALTO en píxeles del cuadro completo.")
    linea: tuple[float, float, float, float] = Field(description="X1,Y1,X2,Y2 en píxeles del recorte.")
    interior: Literal["arriba", "abajo", "izquierda", "derecha"]


class PedidoVideo(Geometria):
    parada: str = Field("Puerta", min_length=1, max_length=100)
    capacidad: int = Field(20, gt=0)
    carga_inicial: int = Field(0, ge=0)
    # Solo con un pedido explícito: vuelve a ejecutar la misma configuración y la guarda como ejecución aparte.
    repetir_para_demostracion: bool = False
    # Lee el video a velocidad original, como una cámara, y descarta cuadros si el modelo se atrasa.
    ritmo_real: bool = False


def validar_geometria(info, geometria):
    x, y, ancho, alto = geometria.recorte
    if x < 0 or y < 0 or ancho < 32 or alto < 32 or x + ancho > info["ancho"] or y + alto > info["alto"]:
        raise HTTPException(422, f"El recorte {x},{y},{ancho},{alto} debe medir al menos 32×32 px y entrar en el "
                                 f"cuadro de {info['ancho']}×{info['alto']}.")
    x1, y1, x2, y2 = geometria.linea
    if not all(0 <= a <= ancho - 1 for a in (x1, x2)) or not all(0 <= b <= alto - 1 for b in (y1, y2)):
        raise HTTPException(422, f"Los extremos de la línea deben estar dentro del recorte (0–{ancho - 1}, 0–{alto - 1}).")
    if ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5 < 10:
        raise HTTPException(422, "La línea debe medir al menos 10 px.")
    try:
        Linea(x1, y1, x2, y2, geometria.interior)
    except ValueError as error:
        raise HTTPException(422, f"{error} Por ejemplo, con el interior arriba la línea va de izquierda a derecha.")


@app.get("/videos/{id_video}/cuadro")
def cuadro_con_geometria(id_video: str = Ruta(pattern=ID_VIDEO), t: float = Query(0, ge=0),
                         recorte: str = Query(pattern=r"^\d+,\d+,\d+,\d+$"),
                         linea: str = Query(pattern=r"^[\d.]+,[\d.]+,[\d.]+,[\d.]+$"),
                         interior: Literal["arriba", "abajo", "izquierda", "derecha"] = "arriba"):
    """Cuadro aproximado en el segundo t con el recorte (azul), la línea (amarillo) y una flecha hacia el interior.

    No ejecuta ningún modelo: sirve para revisar la geometría antes de procesar.
    """
    info = info_de(id_video)
    geometria = Geometria(recorte=recorte.split(","), linea=linea.split(","), interior=interior)
    validar_geometria(info, geometria)
    import cv2

    captura = cv2.VideoCapture(str(VIDEOS / id_video / info["archivo"]), cv2.CAP_FFMPEG)
    captura.set(cv2.CAP_PROP_POS_MSEC, min(t, info["duracion_s"]) * 1000)
    leido, imagen = captura.read()
    captura.release()
    if not leido:
        raise HTTPException(422, f"No se pudo leer el cuadro en {t:g} s.")
    x, y, ancho, alto = geometria.recorte
    x1, y1, x2, y2 = (round(v) for v in geometria.linea)
    cv2.rectangle(imagen, (x, y), (x + ancho - 1, y + alto - 1), (255, 140, 0), 2)
    cv2.line(imagen, (x + x1, y + y1), (x + x2, y + y2), (0, 255, 255), 2)
    dx, dy = {"arriba": (0, -1), "abajo": (0, 1), "izquierda": (-1, 0), "derecha": (1, 0)}[interior]
    medio = (x + (x1 + x2) // 2, y + (y1 + y2) // 2)
    punta = (medio[0] + 40 * dx, medio[1] + 40 * dy)
    cv2.arrowedLine(imagen, medio, punta, (80, 200, 80), 2, tipLength=0.3)
    cv2.putText(imagen, "interior", (punta[0] + 4, punta[1] + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (80, 200, 80), 2)
    return Response(cv2.imencode(".jpg", imagen)[1].tobytes(), media_type="image/jpeg")


def opciones_del_modelo():
    """Detector, rastreador, umbrales y dispositivo efectivos de la API (los mismos de la demo de oficina)."""
    argv = argumentos_demo()
    opciones = dict((clave, valor) for clave, valor in zip(argv[::2], argv[1::2]) if clave not in OPCIONES_DE_ESCENA)
    if DISPOSITIVO:
        opciones["--dispositivo"] = DISPOSITIVO
    return [parte for clave, valor in opciones.items() for parte in (clave, valor)]


@app.post("/videos/{id_video}/procesamientos", status_code=202)
def procesar_video(pedido: PedidoVideo, id_video: str = Ruta(pattern=ID_VIDEO)):
    """Procesa el video completo con la geometría elegida y la configuración del modelo de la API, sin filtros extra."""
    info = info_de(id_video)
    validar_geometria(info, pedido)
    modelo = opciones_del_modelo()
    comprobar_insumos(dict(zip(modelo[::2], modelo[1::2])), ("--pesos",))
    geometria = {"recorte": list(pedido.recorte), "linea": list(pedido.linea), "interior": pedido.interior}
    previas = []
    for carpeta in (EJECUCIONES.iterdir() if EJECUCIONES.is_dir() else []):
        if (carpeta / COMPLETA).is_file() and video_de(carpeta) == id_video:
            previa = json.loads((carpeta / "entrada.json").read_text(encoding="utf-8"))
            if (previa["geometria"] == geometria and previa["opciones_del_modelo"] == modelo
                    and previa.get("ritmo_real", False) == pedido.ritmo_real):
                previas.append(carpeta.name)
    if previas and not pedido.repetir_para_demostracion:
        raise HTTPException(409, f"Este video ya se procesó con la misma geometría, el mismo modelo y el mismo ritmo "
                                 f"(ejecución {min(previas)}). No se repite: se muestra el resultado guardado.")
    argv = ["--video", f"runs/videos/{id_video}/{info['archivo']}",  # con "/" en todo sistema: el comando guardado es portable
            "--recorte", ",".join(map(str, pedido.recorte)), "--linea", ",".join(f"{v:g}" for v in pedido.linea),
            "--interior", pedido.interior, "--parada", pedido.parada,
            "--capacidad", str(pedido.capacidad), "--carga-inicial", str(pedido.carga_inicial), *modelo,
            *(["--ritmo-real"] if pedido.ritmo_real else [])]
    entrada = {"tipo": "video", "video_id": id_video, "video_sha256": info["sha256"],
               "nombre_original": info["nombre_original"], "geometria": geometria, "opciones_del_modelo": modelo,
               "supresion_temporal": None, "sistema_de_coordenadas": SISTEMA_DE_COORDENADAS,
               "proposito": "repeticion para demostracion" if pedido.repetir_para_demostracion else "primera ejecucion",
               "repite_a": sorted(previas) if pedido.repetir_para_demostracion else [],
               "ritmo_real": pedido.ritmo_real, "origen_temporal": ORIGEN_TEMPORAL, "pedido": datetime.now().astimezone().isoformat(timespec="seconds")}
    return correr_pipeline(argv, TIMEOUT_VIDEO_S, entrada)
