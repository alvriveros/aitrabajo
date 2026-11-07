import json
import shlex
import subprocess
import sys
from datetime import datetime
from importlib.util import find_spec
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi import Path as Ruta
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

app = FastAPI(title="Ocupación del bus")

RAIZ = Path(__file__).resolve().parents[1]
# Configuración guardada junto a la predicción de 0–6 s: video, tramo, recorte, línea, pesos y rastreador.
CONFIG_DEMO = RAIZ / "evaluation/results/oficina-00-06-prediccion.config.json"
EJECUCIONES = RAIZ / "runs/panel"
ID_EJECUCION = r"^\d{8}-\d{6}-\d{6}$"


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
    return {"id": carpeta.name, "recorrido": leer("prediccion.json"), "configuracion": leer("prediccion.config.json")}


@app.post("/procesamientos", status_code=201)
def procesar_demo():
    """Ejecuta vision.pipeline sobre el clip de demo y guarda predicción, configuración y video anotado."""
    argv = argumentos_demo()
    opciones = dict(zip(argv[::2], argv[1::2]))
    faltan = [opciones[c] for c in ("--video", "--pesos") if not (RAIZ / opciones[c]).is_file()]
    if find_spec("ultralytics") is None:
        faltan.append("dependencias de vision/requirements.txt")
    if faltan:
        raise HTTPException(503, "Faltan insumos para procesar el video: " + ", ".join(faltan) + ".")

    carpeta = EJECUCIONES / datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    carpeta.mkdir(parents=True)
    comando = [sys.executable, "-m", "vision.pipeline", *argv,
               "--salida", str(carpeta / "prediccion.json"), "--video-anotado", str(carpeta / "anotado.webm")]
    try:
        proceso = subprocess.run(comando, cwd=RAIZ, capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        raise HTTPException(504, "El procesamiento superó los 10 minutos.")
    (carpeta / "registro.txt").write_text(proceso.stdout + proceso.stderr, encoding="utf-8")
    if proceso.returncode:
        raise HTTPException(500, f"El pipeline terminó con código {proceso.returncode}: {proceso.stderr[-800:]}")
    return leer_ejecucion(carpeta)


@app.get("/procesamientos")
def listar_procesamientos():
    """Ejecuciones guardadas, de la más reciente a la más antigua."""
    if not EJECUCIONES.is_dir():
        return []
    return sorted((c.name for c in EJECUCIONES.iterdir() if (c / "prediccion.json").is_file()), reverse=True)


def carpeta_de(id_ejecucion):
    carpeta = EJECUCIONES / id_ejecucion
    if not (carpeta / "prediccion.json").is_file():
        raise HTTPException(404, f"No existe la ejecución {id_ejecucion}.")
    return carpeta


@app.get("/procesamientos/{id_ejecucion}")
def consultar_procesamiento(id_ejecucion: str = Ruta(pattern=ID_EJECUCION)):
    return leer_ejecucion(carpeta_de(id_ejecucion))


@app.get("/procesamientos/{id_ejecucion}/video")
def video_procesado(id_ejecucion: str = Ruta(pattern=ID_EJECUCION)):
    video = carpeta_de(id_ejecucion) / "anotado.webm"
    if not video.is_file():
        raise HTTPException(404, f"La ejecución {id_ejecucion} no tiene video anotado.")
    return FileResponse(video, media_type="video/webm")
