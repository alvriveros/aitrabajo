"""Genera hojas para revisar las cajas de un archivo de anotaciones.

Se ejecuta desde la raíz: python -m vision.revisar_cajas --help

Cada imagen lleva el número de su cuadro. Para corregir una caja, editá el campo `caja` de ese
cuadro en el JSON, en píxeles del recorte; para descartar un cuadro, borrá su entrada. Después
hay que volver a entrenar y a comparar.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from vision.pipeline import Recorte, leer_cuadros
from vision.proponer_cajas import guardar_hojas


def main(argv=None):
    parser = argparse.ArgumentParser(description="Genera hojas para revisar cajas anotadas.")
    parser.add_argument("--anotaciones", type=Path, required=True, help="JSON de data/annotations.")
    parser.add_argument("--hojas", type=Path, required=True, help="Carpeta para las hojas.")
    args = parser.parse_args(argv)

    anotacion = json.loads(args.anotaciones.read_text(encoding="utf-8"))
    imagenes = [imagen for _, imagen in leer_cuadros(anotacion["video"], recorte=Recorte(**anotacion["recorte"]))]
    con_persona = [cuadro for cuadro in anotacion["cuadros"] if cuadro["caja"]]
    sin_persona = [cuadro for cuadro in anotacion["cuadros"] if not cuadro["caja"]]
    rutas = guardar_hojas(con_persona, imagenes, args.hojas, nombre="con-persona")
    rutas += guardar_hojas(sin_persona, imagenes, args.hojas, nombre="sin-persona", por_hoja=30)
    print(f"{len(con_persona)} cuadros con persona y {len(sin_persona)} sin persona en {len(rutas)} hojas: {args.hojas}")


if __name__ == "__main__":
    main()
