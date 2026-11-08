"""Valida ejecuciones de runs/panel anteriores a la marca «completa» y la agrega solo a las válidas.

Uso, desde la raíz del proyecto: python recuperar_ejecuciones.py [--aplicar]
Sin --aplicar solo informa. Una ejecución es válida si cumple lo mismo que exige POST /procesamientos
(prediccion.json y su .config.json legibles, anotado.webm no vacío) y además: el recorrido pasa el
contrato de la API, el registro termina con la salida normal del pipeline sin «Traceback», y el video
se decodifica con la cantidad de cuadros que declara la configuración. Las demás no se tocan.
"""
import sys

import cv2

from api.main import COMPLETA, EJECUCIONES, Recorrido, leer_ejecucion


def problemas(carpeta):
    try:
        datos = leer_ejecucion(carpeta)
        Recorrido(**datos["recorrido"])
        cuadros = datos["configuracion"]["medicion"]["cuadros"]
        registro = (carpeta / "registro.txt").read_text(encoding="utf-8", errors="replace")
    except Exception as error:  # cualquier fallo de lectura o de contrato invalida la ejecución
        return [f"resultado ilegible: {error}"]
    errores = []
    if "Traceback" in registro or "Video anotado:" not in registro:
        errores.append("el registro no muestra un final normal")
    video = cv2.VideoCapture(str(carpeta / "anotado.webm"))
    leidos = 0
    while video.read()[0]:
        leidos += 1
    if leidos != cuadros:
        errores.append(f"el video tiene {leidos} cuadros y la configuración declara {cuadros}")
    return errores


aplicar = "--aplicar" in sys.argv
for carpeta in sorted(EJECUCIONES.iterdir()):
    if (carpeta / COMPLETA).exists():
        print(f"{carpeta.name}: ya publicada")
        continue
    errores = problemas(carpeta)
    if errores:
        print(f"{carpeta.name}: NO se recupera: {'; '.join(errores)}")
    else:
        print(f"{carpeta.name}: válida{' -> marcada completa' if aplicar else ''}")
        if aplicar:
            (carpeta / COMPLETA).touch()
