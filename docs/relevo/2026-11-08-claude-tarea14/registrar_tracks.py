"""Tarea 14: guarda, cuadro por cuadro, las cajas y los IDs del rastreador (yolo11n calibrado, como la API).

Así la regla de conteo con y sin el filtro se compara sobre exactamente las mismas trayectorias, con una sola
inferencia por video. Uso, desde la raíz:
  python docs/relevo/2026-11-08-claude-tarea14/registrar_tracks.py VIDEO RECORTE SALIDA.json
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from vision.pipeline import crear_rastreador, leer_cuadros, leer_recorte  # noqa: E402

video, recorte, salida = Path(sys.argv[1]), leer_recorte(sys.argv[2]), Path(sys.argv[3])
if salida.exists():
    raise SystemExit(f"{salida} ya existe.")
rastrear = crear_rastreador("yolo11n.pt", "vision/bytetrack-cenital.yaml", 0.05, "cpu")
cuadros = [{"t": round(t, 4), "obs": [[i, [round(v, 2) for v in caja]] for i, caja in rastrear(imagen)]}
           for t, imagen in leer_cuadros(video, 0.0, None, recorte)]
salida.parent.mkdir(parents=True, exist_ok=True)
salida.write_text(json.dumps({"video": str(video), "recorte": sys.argv[2], "cuadros": cuadros}), encoding="utf-8")
print(salida, len(cuadros))
