"""Cierre final: un cambio por vez contra la línea base de la API, en las mismas escenas y con la misma regla.

Configuraciones (cada una cambia UNA cosa respecto de `base`):
  base      yolo11n + bytetrack-cenital, conf 0,05, confirmación 2, margen 5 (lo que usa la API)
  iou05     NMS de Ultralytics con IoU 0,5 en lugar de 0,7: ¿se eliminan las cajas encimadas sobre una persona?
  salto2    procesa 1 de cada 2 cuadros: lo que pasa con --ritmo-real si el equipo solo alcanza la mitad de los FPS
  salto3    1 de cada 3 cuadros

Escenas: oficina, Kaggle y PAMELA A son el conjunto de selección (ya usado en las tareas 09–14); `prueba-bus`
es desarrollo desde la tarea 14. Ninguna es una prueba independiente: lo que se elija acá necesita otra grabación.

Desde la raíz:  python docs/relevo/2026-11-08-claude-cierre-final/experimentos.py --salida <carpeta> [--configs base iou05]
"""
import argparse
import json
import sys
import time
from itertools import islice
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from evaluation.evaluate import evaluar  # noqa: E402
from vision.cruces import ContadorCruces, Linea  # noqa: E402
from vision.pipeline import CLASE_PERSONA, Medicion, Recorte, entorno, leer_cuadros, procesar  # noqa: E402

ESCENAS = {  # geometrías de las tareas 09–13; interior arriba en todas
    "oficina": ("data/raw/oficina.mp4", Recorte(228, 2, 222, 176), (0, 90, 221, 90), "data/annotations/oficina-cruces.json"),
    "kaggle": ("data/raw/kaggle-people-boarding-bus.mp4", Recorte(600, 0, 840, 1080), (0, 480, 839, 480),
               "data/annotations/kaggle-people-boarding-bus-cruces.json"),
    "pamela-A": ("data/raw/puerta-tren-d800-A.mp4", Recorte(96, 64, 160, 224), (0, 96, 159, 96),
                 "data/annotations/pamela-A-cruces.json"),
    "prueba-bus (desarrollo)": ("data/raw/prueba-bus.mp4", Recorte(0, 0, 768, 432), (274, 431, 467, 242),
                                "data/annotations/prueba-bus-cruces.json"),
}
CONFIGS = {"base": {}, "iou05": {"iou": 0.5}, "salto2": {"salto": 2}, "salto3": {"salto": 3}}


def rastreador(iou=None):
    from ultralytics import YOLO

    modelo = YOLO("yolo11n.pt")
    opciones = {"persist": True, "tracker": "vision/bytetrack-cenital.yaml", "classes": [CLASE_PERSONA],
                "verbose": False, "conf": 0.05, "device": "cpu"}
    if iou is not None:
        opciones["iou"] = iou

    def rastrear(imagen):
        cajas = modelo.track(imagen, **opciones)[0].boxes
        return [] if cajas is None or cajas.id is None else list(zip(cajas.id.int().tolist(), cajas.xyxy.tolist()))

    return rastrear


def correr(escena, config):
    video, recorte, linea, referencia = ESCENAS[escena]
    contador = ContadorCruces(Linea(*linea, interior="arriba"), margen_px=5, confirmacion=2)
    cuadros = leer_cuadros(video, recorte=recorte)
    if config.get("salto"):
        cuadros = islice(cuadros, 0, None, config["salto"])
    medicion = Medicion()
    inicio = time.perf_counter()
    total = procesar(cuadros, rastreador(config.get("iou")), contador, "centro", None, medicion)
    segundos = time.perf_counter() - inicio
    eventos = [{"tiempo_s": round(e.tiempo_s, 3), "track_id": e.track_id, "sentido": e.sentido}
               for e in contador.eventos_ordenados()]
    metricas = evaluar(json.loads(Path(referencia).read_text(encoding="utf-8"))["eventos"], eventos)
    return {"cuadros": total, "segundos": round(segundos, 2), "fps": round(total / segundos, 2),
            "medicion": medicion.resumen(), "eventos": eventos, "metricas": metricas}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--salida", type=Path, required=True)
    parser.add_argument("--configs", nargs="+", default=list(CONFIGS))
    parser.add_argument("--escenas", nargs="+", default=list(ESCENAS))
    args = parser.parse_args()
    args.salida.mkdir(parents=True, exist_ok=True)
    for nombre in args.configs:
        for escena in args.escenas:
            destino = args.salida / f"{nombre}--{escena.split()[0]}.json"
            if destino.exists():
                continue
            resultado = {"config": nombre, "cambio": CONFIGS[nombre], "escena": escena, **correr(escena, CONFIGS[nombre]),
                         "entorno": entorno()}
            destino.write_text(json.dumps(resultado, ensure_ascii=False, indent=1), encoding="utf-8")
            t = resultado["metricas"]["total"]
            print(f"{nombre:7} {escena:25} TP {t['aciertos']:2} FP {t['falsos_positivos']:2} FN {t['omisiones']:2} "
                  f"F1 {t['f1']} · {resultado['fps']} FPS", flush=True)


if __name__ == "__main__":
    main()
