"""Mayor confianza de "cabeza" por cuadro, 0-6 s, con el .pb de darshan8850. Primera prueba comunicada el 7 nov.

Uso: python -I confianza_cabezas_0_6.py MODELO.pb data/raw/oficina.mp4 SALIDA.json (entorno con tensorflow-cpu).
"""
import json, sys
import cv2, numpy as np
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
pb, video, salida = sys.argv[1:4]
g = tf.Graph()
with g.as_default():
    gd = tf.GraphDef(); gd.ParseFromString(open(pb, "rb").read()); tf.import_graph_def(gd, name="")
s = tf.Session(graph=g)
t_img, t_box, t_sc, t_cl = (g.get_tensor_by_name(n + ":0") for n in ("image_tensor", "detection_boxes", "detection_scores", "detection_classes"))
cap = cv2.VideoCapture(video); filas = []
while cap.grab():
    t = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
    if t >= 6: break
    _, im = cap.retrieve(); crop = im[2:178, 228:450]
    b, sc, cl = s.run([t_box, t_sc, t_cl], {t_img: cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)[None]})
    sc, b, cl = sc[0], b[0], cl[0]
    m = [i for i in range(len(sc)) if int(cl[i]) == 1]
    if m:
        i = max(m, key=lambda k: sc[k]); y = (b[i][0] + b[i][2]) / 2 * crop.shape[0]
        filas.append({"t": round(t, 2), "conf_max": round(float(sc[i]), 3), "centro_y": round(float(y), 1)})
    else:
        filas.append({"t": round(t, 2), "conf_max": 0.0, "centro_y": None})
json.dump(filas, open(salida, "w"), indent=1)
