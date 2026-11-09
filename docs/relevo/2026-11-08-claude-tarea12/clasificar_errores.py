"""Tarea 12, descriptivo: clasifica los errores ya conocidos de la tarea 11. No elige ni puntúa nada nuevo.

Desde la raíz:  python docs/relevo/2026-11-08-claude-tarea12/clasificar_errores.py
Definiciones (en este orden; cada error recibe la primera que cumple):
  FP «error de tiempo»: hay una omisión de referencia del mismo sentido a ≤ 2,5 s (el cruce existe, pero fuera de ±1 s).
  FP «oscilación»: el mismo track_id tiene un evento del sentido opuesto a ≤ 1,5 s.
  FP «fragmentación»: otro evento predicho del mismo sentido, con otro track_id, a ≤ 1,5 s (posible cambio de ID).
  FP «otro»: ninguno de los anteriores.
  FN «con evento cercano»: el FN que explica un FP de «error de tiempo»; el resto, «omisión».
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from evaluation.evaluate import SENTIDOS, evaluar  # noqa: E402

T11 = Path("docs/relevo/2026-11-08-claude-tarea11")
CASOS = {
    "kaggle (selección)": ("data/annotations/kaggle-people-boarding-bus-cruces.json", T11 / "linux/kaggle/eventos"),
    "pamela-A (selección)": ("data/annotations/pamela-A-cruces.json", T11 / "linux/pamela-A/eventos"),
    "youtube-bus-real (consumido)": ("data/annotations/youtube-bus-real-cruces.json", T11 / "final-windows/final/eventos"),
}
OPUESTO = {"subida": "bajada", "bajada": "subida"}


def clasificar(referencia, prediccion):
    metricas = evaluar(referencia, prediccion, 1.0)
    conteo = {"error_tiempo": [], "oscilacion": [], "fragmentacion": [], "otro_fp": [], "omision": [], "fn_con_evento_cercano": []}
    for sentido in SENTIDOS:
        omitidos = list(metricas["sentidos"][sentido]["tiempos_omitidos_s"])
        for t in metricas["sentidos"][sentido]["tiempos_falsos_s"]:
            evento = next(e for e in prediccion if e["sentido"] == sentido and e["tiempo_s"] == t)
            cercanos = [o for o in omitidos if abs(o - t) <= 2.5]
            if cercanos:
                omitidos.remove(min(cercanos, key=lambda o: abs(o - t)))
                conteo["error_tiempo"].append((sentido, t))
                conteo["fn_con_evento_cercano"].append((sentido, t))
            elif any(e["track_id"] == evento["track_id"] and e["sentido"] == OPUESTO[sentido]
                     and abs(e["tiempo_s"] - t) <= 1.5 for e in prediccion):
                conteo["oscilacion"].append((sentido, t))
            elif any(e is not evento and e["sentido"] == sentido and e["track_id"] != evento["track_id"]
                     and abs(e["tiempo_s"] - t) <= 1.5 for e in prediccion):
                conteo["fragmentacion"].append((sentido, t))
            else:
                conteo["otro_fp"].append((sentido, t))
        conteo["omision"] += [(sentido, o) for o in omitidos]
    return conteo


def main():
    salida = {}
    for caso, (ruta_ref, carpeta) in CASOS.items():
        referencia = json.loads(Path(ruta_ref).read_text(encoding="utf-8"))["eventos"]
        for detector in ("yolo11n-calibrado", "yolo11l-calibrado"):
            prediccion = json.loads((carpeta / f"{detector}.json").read_text(encoding="utf-8"))["eventos"]
            conteo = clasificar(referencia, prediccion)
            salida[f"{caso} · {detector}"] = conteo
            print(f"{caso:30} {detector:18} " + "  ".join(f"{k}={len(v)}" for k, v in conteo.items()))
    destino = Path("docs/relevo/2026-11-08-claude-tarea12/clasificacion-errores.json")
    if destino.exists():
        raise SystemExit(f"{destino} ya existe.")
    destino.write_text(json.dumps(salida, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
