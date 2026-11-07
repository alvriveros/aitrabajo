"""Confianza máxima de "persona" por cuadro en el recorte del ensayo de oficina, sin rastreador.

Uso, desde la raíz: python docs/casos-deteccion/oficina-bajada-omitida/medir_confianza.py SALIDA.json
Necesita data/raw/oficina.mp4, yolo11n.pt y las dependencias de vision/requirements.txt.
"""
import json
import sys

import cv2
from ultralytics import YOLO

modelo = YOLO("yolo11n.pt")
captura = cv2.VideoCapture("data/raw/oficina.mp4", cv2.CAP_FFMPEG)
filas = []
while captura.grab():
    t = captura.get(cv2.CAP_PROP_POS_MSEC) / 1000
    if t >= 6:
        break
    _, imagen = captura.retrieve()
    cajas = modelo.predict(imagen[2:178, 228:450], classes=[0], conf=0.001, verbose=False)[0].boxes  # recorte 228,2,222,176
    if len(cajas):
        i = int(cajas.conf.argmax())
        x1, y1, x2, y2 = cajas.xyxy[i].tolist()
        filas.append({"t": round(t, 2), "conf_max": round(float(cajas.conf[i]), 3), "centro_y": round((y1 + y2) / 2, 1)})
    else:
        filas.append({"t": round(t, 2), "conf_max": 0.0, "centro_y": None})
with open(sys.argv[1], "w", encoding="utf-8") as archivo:
    json.dump(filas, archivo, indent=1)
