"""Compara configuraciones del pipeline sobre el video de oficina en el equipo actual, sin tocar evaluation/results.

Uso, desde la raíz de integracion-video:
  python docs/relevo/2026-11-07-claude-tarea09/scripts/evaluar_oficina.py SALIDA/ [--ajustado RUTA.pt]

Reutiliza las configuraciones, tramos, referencia y evaluador de evaluation/comparar_oficina.py; solo
cambia los destinos. Para cada configuración hace dos ejecuciones: 0-6 s (con video anotado) y video
completo (sin video anotado, para medir FPS como en macOS). Comprueba antes el SHA-256 del clip y de
los pesos; una configuración cuyos pesos faltan o no coinciden queda «pendiente» y no se ejecuta.
Los videos anotados van a runs/evaluacion/ (fuera de git). Nada de esto cambia umbrales ni pruebas.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))  # se ejecuta desde la raíz del proyecto

from evaluation.comparar_oficina import AJUSTADO, CONFIGURACIONES, ESCENA, REFERENCIA, TRAMOS  # noqa: E402
from evaluation.evaluate import evaluar  # noqa: E402
from vision.pipeline import entorno, guardar_json, main as ejecutar_pipeline, ruta_de_configuracion  # noqa: E402

HUELLAS = {  # documentadas en data/README.md, vision/README.md y docs/relevo/vision-ajuste-detector/README.md
    "data/raw/oficina.mp4": "02666c2e567f45015a2e73fe802db8f39c6c568d41ef42efc63997de4d15fc95",
    "yolo11n.pt": "0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1",
    AJUSTADO: "783d16c01b9dc4995ac4809dcbd0bd794fd96ad2edaf509aa296f682622d93e1",
}


def huella(ruta):
    ruta = Path(ruta)
    if not ruta.is_file():
        return None
    return {"bytes": ruta.stat().st_size, "sha256": hashlib.sha256(ruta.read_bytes()).hexdigest()}


def por_sentido(metricas):
    """TP, FP, FN y error de conteo por sentido, más los tiempos de cada error."""
    return {sentido: {"TP": m["aciertos"], "FP": m["falsos_positivos"], "FN": m["omisiones"],
                      "referencia": m["referencia"], "predichos": m["predichos"],
                      "error_conteo_abs": m["error_conteo_abs"], "f1": m["f1"],
                      "omitidos_s": m["tiempos_omitidos_s"], "extra_s": m["tiempos_falsos_s"]}
            for sentido, m in metricas["sentidos"].items()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("salida", type=Path)
    parser.add_argument("--ajustado", default=AJUSTADO, help="Ruta de los pesos ajustados del compañero.")
    parser.add_argument("--sha-ajustado", default=HUELLAS[AJUSTADO], help="SHA-256 esperado de los pesos ajustados.")
    args = parser.parse_args()
    salida = args.salida
    nombre_entorno = f"{platform.system()}-{platform.machine()}".lower()
    videos = Path("runs/evaluacion") / nombre_entorno
    referencia = json.loads(REFERENCIA.read_text(encoding="utf-8"))["eventos"]

    insumos = {ruta: huella(ruta) for ruta in ("data/raw/oficina.mp4", "yolo11n.pt")}
    insumos[args.ajustado] = huella(args.ajustado)
    validos = {ruta: bool(datos) and datos["sha256"] == (args.sha_ajustado if ruta == args.ajustado else HUELLAS.get(ruta))
               for ruta, datos in insumos.items()}
    if not validos["data/raw/oficina.mp4"]:
        raise SystemExit(f"El clip falta o no coincide con el SHA-256 documentado: {insumos['data/raw/oficina.mp4']}")

    resumen = {"aviso": "Una sola grabación, también usada para entrenar y calibrar: orienta, no es una evaluación independiente.",
               "referencia": str(REFERENCIA), "tolerancia_s": 1.0, "entorno": entorno(),
               "insumos": insumos, "insumos_validos": validos, "configuraciones": {}}
    for nombre, opciones in CONFIGURACIONES.items():
        opciones = [args.ajustado if o == AJUSTADO else o for o in opciones]
        pesos = opciones[opciones.index("--pesos") + 1]
        if not validos.get(pesos):
            resumen["configuraciones"][nombre] = {"estado": "pendiente", "motivo": f"pesos ausentes o con otra huella: {pesos}"}
            print(f"{nombre}: pendiente ({pesos})")
            continue
        datos = {"estado": "ejecutado", "opciones": opciones, "ejecuciones": {}}
        for corrida, extra in {"0-6": ["--inicio", "0", "--fin", "6", "--video-anotado", str(videos / f"{nombre}-0-6.mp4")],
                               "completo": []}.items():
            destino = salida / "eventos" / f"{nombre}-{corrida}.json"
            ejecutar_pipeline([*ESCENA, *opciones, *extra, "--salida", str(destino)])
            prediccion = json.loads(destino.read_text(encoding="utf-8"))["eventos"]
            medicion = json.loads(ruta_de_configuracion(destino).read_text(encoding="utf-8"))["medicion"]
            tramos = {"0-6": (0.0, 6.0)} if corrida == "0-6" else TRAMOS
            metricas = {tramo: evaluar(referencia, prediccion, 1.0, *limites) for tramo, limites in tramos.items()}
            guardar_json(salida / "evaluacion" / f"{nombre}-{corrida}.json", metricas)
            datos["ejecuciones"][corrida] = {
                "eventos": [(e["tiempo_s"], e["sentido"]) for e in prediccion], "medicion": medicion,
                "por_tramo": {tramo: {"total": m["total"], "por_sentido": por_sentido(m)} for tramo, m in metricas.items()}}
        resumen["configuraciones"][nombre] = datos
    guardar_json(salida / "resumen.json", resumen)

    print(f"\n{'configuración':20} {'corrida':9} {'tramo':14} {'sub TP/FP/FN':13} {'baj TP/FP/FN':13} {'FPS':6}")
    for nombre, datos in resumen["configuraciones"].items():
        for corrida, ejecucion in datos.get("ejecuciones", {}).items():
            for tramo, m in ejecucion["por_tramo"].items():
                s, b = m["por_sentido"]["subida"], m["por_sentido"]["bajada"]
                print(f"{nombre:20} {corrida:9} {tramo:14} {s['TP']}/{s['FP']}/{s['FN']:<9} {b['TP']}/{b['FP']}/{b['FN']:<9} "
                      f"{ejecucion['medicion']['fps_procesados']}")


if __name__ == "__main__":
    main()
