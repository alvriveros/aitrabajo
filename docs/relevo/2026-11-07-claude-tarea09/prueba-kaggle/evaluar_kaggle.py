"""Evalúa una sola vez las configuraciones prerregistradas sobre kaggle-people-boarding-bus.mp4.

Uso, desde la raíz: python docs/relevo/2026-11-07-claude-tarea09/prueba-kaggle/evaluar_kaggle.py SALIDA/ [--ajustado RUTA.pt]
Recorte, línea e interior son los de preregistro.md; las configuraciones, las de evaluation/comparar_oficina.py.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

from evaluation.comparar_oficina import AJUSTADO, CONFIGURACIONES  # noqa: E402
from evaluation.evaluate import evaluar  # noqa: E402
from vision.pipeline import entorno, guardar_json, main as ejecutar_pipeline, ruta_de_configuracion  # noqa: E402

VIDEO = "data/raw/kaggle-people-boarding-bus.mp4"
REFERENCIA = Path("data/annotations/kaggle-people-boarding-bus-cruces.json")
ESCENA = ["--video", VIDEO, "--recorte", "600,0,840,1080", "--linea", "0,480,839,480", "--interior", "arriba",
          "--dispositivo", "cpu", "--parada", "Puerta de bus (Kaggle) · 0-60 s"]
HUELLAS = {VIDEO: "5084d4b11484282f1a81368f453dfccad9860c714f1e3c9704f65b32058ffe45",
           "yolo11n.pt": "0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1",
           AJUSTADO: "783d16c01b9dc4995ac4809dcbd0bd794fd96ad2edaf509aa296f682622d93e1"}


def sha(ruta):
    ruta = Path(ruta)
    return hashlib.sha256(ruta.read_bytes()).hexdigest() if ruta.is_file() else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("salida", type=Path)
    parser.add_argument("--ajustado", default=AJUSTADO)
    parser.add_argument("--sha-ajustado", default=HUELLAS[AJUSTADO], help="SHA-256 esperado de los pesos ajustados (tarea 10: reproducidos).")
    args = parser.parse_args()
    if sha(VIDEO) != HUELLAS[VIDEO]:
        raise SystemExit("El video falta o no coincide con el SHA-256 prerregistrado.")
    referencia = json.loads(REFERENCIA.read_text(encoding="utf-8"))["eventos"]
    videos = Path("runs/evaluacion") / f"{platform.system()}-{platform.machine()}".lower()
    resumen = {"pesos_ajustados": {"ruta": args.ajustado, "sha256": sha(args.ajustado)}, "referencia": str(REFERENCIA), "referencia_sha256": sha(REFERENCIA), "tolerancia_s": 1.0,
               "entorno": entorno(), "configuraciones": {}}
    for nombre, opciones in CONFIGURACIONES.items():
        opciones = [args.ajustado if o == AJUSTADO else o for o in opciones]
        pesos = opciones[opciones.index("--pesos") + 1]
        if sha(pesos) != (args.sha_ajustado if pesos == args.ajustado else HUELLAS.get(pesos)):
            resumen["configuraciones"][nombre] = {"estado": "pendiente", "motivo": f"pesos ausentes o con otra huella: {pesos}"}
            continue
        destino = args.salida / "eventos" / f"{nombre}.json"
        ejecutar_pipeline([*ESCENA, *opciones, "--salida", str(destino),
                           "--video-anotado", str(videos / f"kaggle-{nombre}.mp4")])
        prediccion = json.loads(destino.read_text(encoding="utf-8"))["eventos"]
        metricas = evaluar(referencia, prediccion, 1.0)
        guardar_json(args.salida / "evaluacion" / f"{nombre}.json", metricas)
        resumen["configuraciones"][nombre] = {
            "estado": "ejecutado", "opciones": opciones,
            "medicion": json.loads(ruta_de_configuracion(destino).read_text(encoding="utf-8"))["medicion"],
            "eventos": [(e["tiempo_s"], e["track_id"], e["sentido"]) for e in prediccion],
            "por_sentido": {s: {"TP": m["aciertos"], "FP": m["falsos_positivos"], "FN": m["omisiones"],
                                "error_conteo_abs": m["error_conteo_abs"], "omitidos_s": m["tiempos_omitidos_s"],
                                "extra_s": m["tiempos_falsos_s"]} for s, m in metricas["sentidos"].items()}}
    guardar_json(args.salida / "resumen.json", resumen)
    for nombre, d in resumen["configuraciones"].items():
        print(nombre, d.get("estado"), d.get("por_sentido", ""), d.get("medicion", {}).get("fps_procesados", ""))


if __name__ == "__main__":
    main()
