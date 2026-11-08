"""Detecciones de 'cabeza' por cuadro con el .pb de darshan8850, en el recorte del ensayo de oficina.

Uso: python -I detectar_cabezas.py MODELO.pb VIDEO.mp4 SALIDA.json
Entorno aparte con tensorflow-cpu y opencv; no forma parte del proyecto.
Guarda todas las cajas de la clase 1 con confianza >= 0.01, en píxeles del recorte 228,2,222,176.
"""
import json
import sys

import cv2
import tensorflow.compat.v1 as tf

tf.disable_v2_behavior()
modelo, video, salida = sys.argv[1:4]
grafo = tf.Graph()
with grafo.as_default():
    definicion = tf.GraphDef()
    definicion.ParseFromString(open(modelo, "rb").read())
    tf.import_graph_def(definicion, name="")
sesion = tf.Session(graph=grafo)
tensores = [grafo.get_tensor_by_name(n + ":0") for n in ("detection_boxes", "detection_scores", "detection_classes")]
entrada = grafo.get_tensor_by_name("image_tensor:0")
captura = cv2.VideoCapture(video, cv2.CAP_FFMPEG)
cuadros = []
while captura.grab():
    t = captura.get(cv2.CAP_PROP_POS_MSEC) / 1000
    _, imagen = captura.retrieve()
    recorte = imagen[2:178, 228:450]
    alto, ancho = recorte.shape[:2]
    cajas, puntajes, clases = (x[0] for x in sesion.run(tensores, {entrada: cv2.cvtColor(recorte, cv2.COLOR_BGR2RGB)[None]}))
    cuadros.append({"t": round(t, 3), "cajas": [
        [round(float(c[1]) * ancho, 1), round(float(c[0]) * alto, 1), round(float(c[3]) * ancho, 1),
         round(float(c[2]) * alto, 1), round(float(p), 4)]
        for c, p, k in zip(cajas, puntajes, clases) if int(k) == 1 and p >= 0.01]})
json.dump({"modelo": modelo, "video": video, "recorte": [228, 2, 222, 176], "cuadros": cuadros}, open(salida, "w"))
print(len(cuadros), "cuadros")
