"""Compara detectores de la misma familia (yolo11n, yolo11l, yolo11x) sin entrenar, con el pipeline y la regla
de conteo del proyecto, en las escenas con referencia de cruces. Tarea 11 (ver preregistro.md).

Uso, desde la raíz de integracion-video:
  python docs/relevo/2026-11-08-claude-tarea11/evaluar_detectores.py SALIDA/ --dispositivo cuda:0

No usa los videos reservados (youtube-*). No cambia la configuración de la API.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

from evaluation.comparar_oficina import CALIBRADO  # noqa: E402
from evaluation.evaluate import evaluar  # noqa: E402
from vision.pipeline import entorno, guardar_json, main as ejecutar_pipeline, ruta_de_configuracion  # noqa: E402

MODELOS = {  # pesos oficiales de Ultralytics, release v8.4.0
    "yolo11n": ("yolo11n.pt", "0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1"),
    "yolo11l": ("yolo11l.pt", "9ebd0e09d59811db4b1d61e2bc6730649608b1ac47f8dd01e2da6bca7c20023f"),
    "yolo11x": ("yolo11x.pt", "7bc158aa95c0ebfdd87f70f01653c1131b93e92522dbe15c228bcd742e773a24"),
}
RASTREADORES = {"defecto": [], "calibrado": CALIBRADO}
ESCENAS = {  # mismas geometrías y referencias que las tareas 09 y 10
    "kaggle": {"video": "data/raw/kaggle-people-boarding-bus.mp4",
               "sha256": "5084d4b11484282f1a81368f453dfccad9860c714f1e3c9704f65b32058ffe45",
               "referencia": "data/annotations/kaggle-people-boarding-bus-cruces.json",
               "argumentos": ["--recorte", "600,0,840,1080", "--linea", "0,480,839,480"]},
    "pamela-A": {"video": "data/raw/puerta-tren-d800-A.mp4",
                 "sha256": "cf18411cda0d7b9de9a1c649599185b4d469c20fa2f9fc4f057d537aeb0868ab",
                 "referencia": "data/annotations/pamela-A-cruces.json",
                 "argumentos": ["--recorte", "96,64,160,224", "--linea", "0,96,159,96"]},
    "oficina": {"video": "data/raw/oficina.mp4",
                "sha256": "02666c2e567f45015a2e73fe802db8f39c6c568d41ef42efc63997de4d15fc95",
                "referencia": "data/annotations/oficina-cruces.json",
                "argumentos": ["--recorte", "228,2,222,176", "--linea", "0,90,221,90"]},
}


def sha(ruta):
    ruta = Path(ruta)
    return hashlib.sha256(ruta.read_bytes()).hexdigest() if ruta.is_file() else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("salida", type=Path)
    parser.add_argument("--dispositivo", default="cuda:0")
    parser.add_argument("--escenas", nargs="+", default=list(ESCENAS), help="Subconjunto de escenas (por defecto, todas).")
    parser.add_argument("--modelos", nargs="+", default=list(MODELOS), help="Subconjunto de modelos (por defecto, todos).")
    args = parser.parse_args()
    escenas = {n: ESCENAS[n] for n in args.escenas}
    modelos = {n: MODELOS[n] for n in args.modelos}
    for nombre, (ruta, huella) in modelos.items():
        if sha(ruta) != huella:
            raise SystemExit(f"{ruta} falta o no coincide con el SHA-256 esperado ({nombre}).")
    for nombre, escena in escenas.items():
        if sha(escena["video"]) != escena["sha256"]:
            raise SystemExit(f"{escena['video']} falta o no coincide con su SHA-256.")
    videos = Path("runs/evaluacion") / f"tarea11-{platform.system()}".lower()
    resumen = {"dispositivo": args.dispositivo, "entorno": entorno(),
               "modelos": {n: {"ruta": r, "sha256": h} for n, (r, h) in modelos.items()}, "resultados": {}}
    for escena_nombre, escena in escenas.items():
        referencia = json.loads(Path(escena["referencia"]).read_text(encoding="utf-8"))["eventos"]
        resumen["resultados"][escena_nombre] = {"referencia_sha256": sha(escena["referencia"])}
        for modelo, (pesos, _) in modelos.items():
            for rastreador, opciones in RASTREADORES.items():
                nombre = f"{modelo}-{rastreador}"
                destino = args.salida / escena_nombre / "eventos" / f"{nombre}.json"
                ejecutar_pipeline(["--video", escena["video"], *escena["argumentos"], "--interior", "arriba",
                                   "--dispositivo", args.dispositivo, "--pesos", pesos, *opciones,
                                   "--salida", str(destino), "--video-anotado", str(videos / f"{escena_nombre}-{nombre}.mp4")])
                prediccion = json.loads(destino.read_text(encoding="utf-8"))["eventos"]
                metricas = evaluar(referencia, prediccion, 1.0)
                guardar_json(args.salida / escena_nombre / "evaluacion" / f"{nombre}.json", metricas)
                medicion = json.loads(ruta_de_configuracion(destino).read_text(encoding="utf-8"))["medicion"]
                resumen["resultados"][escena_nombre][nombre] = {
                    "fps": medicion["fps_procesados"], "eventos": len(prediccion),
                    "por_sentido": {s: {"TP": m["aciertos"], "FP": m["falsos_positivos"], "FN": m["omisiones"],
                                        "error_conteo_abs": m["error_conteo_abs"]} for s, m in metricas["sentidos"].items()},
                    "errores": metricas["total"]["omisiones"] + metricas["total"]["falsos_positivos"]}
                print(escena_nombre, nombre, resumen["resultados"][escena_nombre][nombre], flush=True)
    guardar_json(args.salida / f"resumen-{'-'.join(escenas)}-{'-'.join(modelos)}.json", resumen)


if __name__ == "__main__":
    main()
