"""Genera la figura del caso de pérdida de identidad del informe.

Se ejecuta desde la raíz: python -m evaluation.figura_perdida_id

Recorre el video desde el inicio, porque los IDs dependen de todo lo que el rastreador vio antes.
Compara el detector base calibrado con el ajustado en la subida de los 43,8 s.
"""
from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from vision.pipeline import Recorte, crear_rastreador, leer_cuadros

VIDEO = "data/raw/oficina.mp4"
RECORTE = Recorte(228, 2, 222, 176)
LINEA_Y = 90
ESCALA = 3
DESTINO = Path("docs/informe/fig-perdida-id.png")
AMARILLO, BLANCO, VERDE, NARANJA = (0, 255, 255), (255, 255, 255), (80, 200, 80), (60, 140, 255)
BASE = {"pesos": "yolo11n.pt", "rastreador": "vision/bytetrack-cenital.yaml", "conf": 0.05, "dispositivo": "cpu"}
AJUSTADO = {"pesos": "runs/oficina-ajuste/oficina-ajustado.pt", "dispositivo": "cpu"}
PANELES = [
    {"letra": "a", "modelo": "base", "tiempo_s": 43.80, "id": 59, "color": NARANJA},
    {"letra": "b", "modelo": "base", "tiempo_s": 43.92, "id": 62, "color": NARANJA},
    {"letra": "c", "modelo": "ajustado", "tiempo_s": 43.92, "id": 106, "color": VERDE},
]


def observar(modelo, instantes, hasta_s):
    """Corre el rastreador hasta `hasta_s` y guarda la imagen y los tracks de los instantes pedidos."""
    rastrear = crear_rastreador(**modelo)
    guardados = {}
    for tiempo, imagen in leer_cuadros(VIDEO, 0, hasta_s, RECORTE):
        tracks = dict(rastrear(imagen))
        clave = round(tiempo, 2)
        if clave in instantes:
            guardados[clave] = (imagen, tracks)
    return guardados


def dibujar(panel, imagen, tracks):
    if panel["id"] not in tracks:
        raise SystemExit(f"Sin ID {panel['id']} a los {panel['tiempo_s']} s; IDs presentes: {sorted(tracks)}")
    lienzo = cv2.resize(imagen, None, fx=ESCALA, fy=ESCALA, interpolation=cv2.INTER_CUBIC)
    alto, ancho = lienzo.shape[:2]
    cv2.line(lienzo, (0, LINEA_Y * ESCALA), (ancho, LINEA_Y * ESCALA), AMARILLO, 3)
    x1, y1, x2, y2 = (int(valor * ESCALA) for valor in tracks[panel["id"]])
    cv2.rectangle(lienzo, (x1, y1), (x2, y2), panel["color"], 4)
    rotulo = f"ID {panel['id']}"
    (ancho_rotulo, alto_rotulo), _ = cv2.getTextSize(rotulo, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 4)
    x_rotulo = min(max(x1, 6), ancho - ancho_rotulo - 6)
    y_rotulo = y1 - 12 if y1 > alto_rotulo + 18 else y1 + alto_rotulo + 12
    cv2.putText(lienzo, rotulo, (x_rotulo, y_rotulo), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 10)
    cv2.putText(lienzo, rotulo, (x_rotulo, y_rotulo), cv2.FONT_HERSHEY_SIMPLEX, 1.5, panel["color"], 4)
    cv2.rectangle(lienzo, (0, 0), (70, 58), (0, 0, 0), -1)
    cv2.putText(lienzo, f"{panel['letra']}", (14, 44), cv2.FONT_HERSHEY_SIMPLEX, 1.5, BLANCO, 3)
    return lienzo


def main():
    instantes = {panel["tiempo_s"] for panel in PANELES}
    hasta_s = max(instantes) + 0.1
    observaciones = {"base": observar(BASE, instantes, hasta_s), "ajustado": observar(AJUSTADO, instantes, hasta_s)}
    paneles = []
    for panel in PANELES:
        imagen, tracks = observaciones[panel["modelo"]][panel["tiempo_s"]]
        print(f"({panel['letra']}) {panel['modelo']} a los {panel['tiempo_s']} s: IDs {sorted(tracks)}")
        paneles.append(dibujar(panel, imagen, tracks))
    separador = np.full((paneles[0].shape[0], 12, 3), 255, dtype="uint8")
    figura = np.hstack([paneles[0], separador, paneles[1], separador, paneles[2]])
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(DESTINO), figura)
    print(f"Figura: {DESTINO} {figura.shape[1]}x{figura.shape[0]}")


if __name__ == "__main__":
    main()
