"""Rastrea detecciones guardadas con ByteTrack y aplica la regla de conteo del proyecto (vision.cruces).

Uso, desde la raíz del proyecto:
  python contar.py DETECCIONES.json RASTREADOR.yaml CONF_MIN SALIDA.json
Misma línea, margen, confirmación y punto (centro de la caja) que la configuración guardada de 0-6 s.
No modifica el proyecto: solo importa vision.cruces y el rastreador de Ultralytics.
"""
import json
import sys

import numpy as np
from ultralytics.engine.results import Boxes
from ultralytics.trackers.byte_tracker import BYTETracker
from ultralytics.utils import IterableSimpleNamespace, YAML

from vision.cruces import ContadorCruces, Linea

detecciones, rastreador, conf_min, salida = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
datos = json.load(open(detecciones))
tracker = BYTETracker(IterableSimpleNamespace(**YAML.load(rastreador)))
contador = ContadorCruces(Linea(0, 90, 221, 90, interior="arriba"), margen_px=5.0, confirmacion=2)
ids, cuadros_con_track = set(), 0
for cuadro in datos["cuadros"]:
    filas = [c[:4] + [c[4], 0] for c in cuadro["cajas"] if c[4] >= conf_min]
    cajas = Boxes(np.array(filas, dtype=np.float32).reshape(-1, 6), (176, 222))
    salidas = tracker.update(cajas)
    cuadros_con_track += len(salidas) > 0
    for x1, y1, x2, y2, track_id, *_ in salidas:
        ids.add(int(track_id))
        contador.actualizar(int(track_id), float(x1 + x2) / 2, float(y1 + y2) / 2, cuadro["t"])
eventos = [{"tiempo_s": round(e.tiempo_s, 3), "track_id": int(e.track_id), "sentido": e.sentido}
           for e in contador.eventos_ordenados()]
json.dump({"capacidad": 20, "carga_inicial": 0, "paradas": [{"nombre": "experimento", "inicio_s": 0}],
           "eventos": eventos, "experimento": {"detecciones": detecciones, "rastreador": rastreador,
           "conf_min": conf_min, "ids_distintos": len(ids), "cuadros_con_track": cuadros_con_track}},
          open(salida, "w"), ensure_ascii=False, indent=1)
print(salida, len(eventos), "eventos,", len(ids), "IDs")
