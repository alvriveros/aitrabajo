"""Detecciones de 'persona' por cuadro con yolo11n.pt (sin rastreador), mismo formato que detectar_cabezas.py.

Uso, desde la raíz del proyecto: python detectar_personas.py yolo11n.pt data/raw/oficina.mp4 SALIDA.json
"""
import json
import sys

import cv2
from ultralytics import YOLO

pesos, video, salida = sys.argv[1:4]
modelo = YOLO(pesos)
captura = cv2.VideoCapture(video, cv2.CAP_FFMPEG)
cuadros = []
while captura.grab():
    t = captura.get(cv2.CAP_PROP_POS_MSEC) / 1000
    _, imagen = captura.retrieve()
    cajas = modelo.predict(imagen[2:178, 228:450], classes=[0], conf=0.01, verbose=False)[0].boxes
    cuadros.append({"t": round(t, 3), "cajas": [[round(v, 1) for v in c] + [round(float(p), 4)]
                                                 for c, p in zip(cajas.xyxy.tolist(), cajas.conf.tolist())]})
json.dump({"modelo": pesos, "video": video, "recorte": [228, 2, 222, 176], "cuadros": cuadros}, open(salida, "w"))
print(len(cuadros), "cuadros")
