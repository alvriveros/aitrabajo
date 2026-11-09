"""Mayor confianza de persona por cuadro (sin rastreador), base frente a ajustado reproducido (tarea 10, diagnóstico).

Uso, desde la raíz: python confianza_max.py VIDEO X,Y,ANCHO,ALTO PESOS_AJUSTADO SALIDA.json  (uno de cada 5 cuadros)
"""
import json, sys
import cv2
from ultralytics import YOLO
video, recorte, pesos_ajustado, salida = sys.argv[1], [int(v) for v in sys.argv[2].split(",")], sys.argv[3], sys.argv[4]
x, y, w, h = recorte
modelos = {"base": YOLO("yolo11n.pt"), "ajustado": YOLO(pesos_ajustado)}
cap = cv2.VideoCapture(video); filas = []; i = 0
while True:
    ok, im = cap.read()
    if not ok: break
    if i % 5 == 0:
        c = im[y:y+h, x:x+w]
        fila = {"t": round(i / cap.get(cv2.CAP_PROP_FPS), 2)}
        for n, m in modelos.items():
            b = m.predict(c, classes=[0], conf=0.001, verbose=False)[0].boxes
            fila[n] = round(float(b.conf.max()), 3) if len(b) else 0.0
            fila[n + "_cajas_0.25"] = int((b.conf >= 0.25).sum()) if len(b) else 0
        filas.append(fila)
    i += 1
json.dump(filas, open(salida, "w"), indent=0)
for n in modelos:
    v = [f[n] for f in filas]
    print(n, "cuadros con conf>=0.25:", sum(x >= 0.25 for x in v), "de", len(v), "| >=0.05:", sum(x >= 0.05 for x in v), "| media", round(sum(v)/len(v), 3))
