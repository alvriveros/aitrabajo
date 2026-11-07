"""Ajusta el detector de personas con cajas anotadas, de forma reproducible.

Se ejecuta desde la raíz: python -m vision.train --help

Arma un dataset YOLO con los cuadros anotados, entrena y guarda en un JSON los parámetros, las
versiones y la huella de los pesos. Conserva los pesos de la última época: así la partición de
reserva mide el resultado sin haber elegido el modelo.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import shutil
import sys
import time
from pathlib import Path

import cv2

from vision.pipeline import Recorte, entorno, guardar_json, leer_cuadros

CARPETAS = {"entrenamiento": "train", "reserva": "val"}


def huella(ruta):
    digesto = hashlib.sha256()
    with open(ruta, "rb") as archivo:
        for bloque in iter(lambda: archivo.read(1 << 20), b""):
            digesto.update(bloque)
    return digesto.hexdigest()


def caja_a_yolo(caja, ancho, alto):
    """Convierte [x1, y1, x2, y2] en píxeles a la línea de etiqueta de YOLO, con la clase 0."""
    x1, y1, x2, y2 = caja
    if not (0 <= x1 < x2 <= ancho and 0 <= y1 < y2 <= alto):
        raise ValueError(f"La caja {caja} no entra en una imagen de {ancho}x{alto}.")
    return (f"0 {(x1 + x2) / 2 / ancho:.6f} {(y1 + y2) / 2 / alto:.6f} "
            f"{(x2 - x1) / ancho:.6f} {(y2 - y1) / alto:.6f}")


def armar_dataset(anotacion, video, carpeta):
    """Escribe imágenes, etiquetas y dataset.yaml. Devuelve la ruta del YAML y el conteo por partición."""
    carpeta = Path(carpeta).resolve()
    por_cuadro = {c["cuadro"]: c for c in anotacion["cuadros"] if c["particion"] in CARPETAS}
    for sub in CARPETAS.values():
        (carpeta / "images" / sub).mkdir(parents=True, exist_ok=True)
        (carpeta / "labels" / sub).mkdir(parents=True, exist_ok=True)

    conteo = {particion: {"con_persona": 0, "sin_persona": 0} for particion in CARPETAS}
    escritos = set()
    for indice, (_, imagen) in enumerate(leer_cuadros(video, recorte=Recorte(**anotacion["recorte"]))):
        entrada = por_cuadro.get(indice)
        if entrada is None:
            continue
        sub = CARPETAS[entrada["particion"]]
        alto, ancho = imagen.shape[:2]
        cv2.imwrite(str(carpeta / "images" / sub / f"cuadro-{indice:05d}.png"), imagen)
        etiqueta = caja_a_yolo(entrada["caja"], ancho, alto) + "\n" if entrada["caja"] else ""
        (carpeta / "labels" / sub / f"cuadro-{indice:05d}.txt").write_text(etiqueta, encoding="utf-8")
        conteo[entrada["particion"]]["con_persona" if entrada["caja"] else "sin_persona"] += 1
        escritos.add(indice)
    faltantes = sorted(set(por_cuadro) - escritos)
    if faltantes:
        raise SystemExit(f"Estos cuadros anotados no están en el video: {faltantes}")

    yaml = carpeta / "dataset.yaml"
    yaml.write_text(
        f"path: {json.dumps(str(carpeta))}\ntrain: images/train\nval: images/val\nnames:\n  0: {anotacion['clase']}\n",
        encoding="utf-8",
    )
    return yaml, conteo


def crear_parser():
    parser = argparse.ArgumentParser(description="Ajusta el detector con cajas anotadas.")
    parser.add_argument("--anotaciones", type=Path, required=True, help="JSON de data/annotations.")
    parser.add_argument("--salida", type=Path, required=True, help="Carpeta para el dataset y los pesos.")
    parser.add_argument("--resumen", type=Path, required=True, help="JSON con parámetros, versiones y métricas.")
    parser.add_argument("--pesos", default="yolo11n.pt", help="Pesos iniciales.")
    parser.add_argument("--epocas", type=int, default=40)
    parser.add_argument("--tamano", type=int, default=640, help="Lado de entrada de la red, igual al del pipeline.")
    parser.add_argument("--lote", type=int, default=16)
    parser.add_argument("--semilla", type=int, default=0)
    parser.add_argument("--dispositivo", default="cpu", help="cpu, mps o cuda:0.")
    return parser


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    args = crear_parser().parse_args(argv)
    anotacion = json.loads(args.anotaciones.read_text(encoding="utf-8"))
    video = Path(anotacion["video"])
    if not video.is_file():
        raise SystemExit(f"No existe el video: {video}. Ver data/README.md.")
    if huella(video) != anotacion["sha256"]:
        raise SystemExit(f"{video} no es la copia anotada: su SHA-256 no coincide.")

    salida = args.salida.resolve()
    shutil.rmtree(salida / "dataset", ignore_errors=True)
    yaml, conteo = armar_dataset(anotacion, video, salida / "dataset")
    print(f"Dataset: {conteo}")

    from ultralytics import YOLO

    parametros = {
        "epochs": args.epocas, "imgsz": args.tamano, "batch": args.lote, "seed": args.semilla,
        "device": args.dispositivo, "deterministic": True, "workers": 0, "amp": False, "plots": False,
        # La cámara mira desde arriba: una persona no tiene un "arriba" fijo en la imagen.
        "flipud": 0.5, "degrees": 15.0,
    }
    inicio = time.perf_counter()
    YOLO(args.pesos).train(data=str(yaml), project=str(salida), name="entrenamiento", exist_ok=True, **parametros)
    segundos = time.perf_counter() - inicio

    pesos = salida / "oficina-ajustado.pt"
    shutil.copy2(salida / "entrenamiento" / "weights" / "last.pt", pesos)
    metricas = YOLO(str(pesos)).val(data=str(yaml), split="val", imgsz=args.tamano, device=args.dispositivo,
                                    workers=0, plots=False, verbose=False, project=str(salida), name="reserva",
                                    exist_ok=True).box
    resumen = {
        "comando": shlex.join(["python", "-m", "vision.train", *argv]),
        "anotaciones": {"ruta": str(args.anotaciones), "sha256": huella(args.anotaciones), "revision": anotacion["revision"]},
        "video_sha256": anotacion["sha256"],
        "dataset": conteo,
        "pesos_iniciales": {"ruta": args.pesos, "sha256": huella(args.pesos)},
        "parametros": parametros,
        "pesos_ajustados": {"ruta": str(pesos.relative_to(Path.cwd())), "sha256": huella(pesos), "bytes": pesos.stat().st_size},
        "metricas_reserva": {"map50": round(float(metricas.map50), 4), "map50_95": round(float(metricas.map), 4),
                             "precision": round(float(metricas.mp), 4), "exhaustividad": round(float(metricas.mr), 4),
                             "aviso": "Misma grabación que el entrenamiento: orienta, pero no sirve para el informe."},
        "segundos_de_entrenamiento": round(segundos, 1),
        "entorno": entorno(),
    }
    guardar_json(args.resumen, resumen)
    print(f"Pesos ajustados: {pesos}")
    print(f"Resumen: {args.resumen}")
    print(f"Métricas en reserva: {resumen['metricas_reserva']}")


if __name__ == "__main__":
    main()
