"""Tarea 14: cuenta cruces sobre las trayectorias guardadas, sin y con el filtro de cajas encimadas.

Usa ContadorCruces tal cual y la copia de procesar con filtro de experimento/filtro.py (sin filtro es idéntica a la de vision.pipeline), con los parámetros de la API (margen 5 px, confirmación 2).
El filtro se evalúa con un único valor fijado antes de medir: umbral 0,6 y ventana 1 s.
Desde la raíz:  python docs/relevo/2026-11-08-claude-tarea14/comparar.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from evaluation.evaluate import evaluar  # noqa: E402
from vision.cruces import ContadorCruces, Linea  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent / "experimento"))
from filtro import FiltroSuperpuestas, procesar  # noqa: E402

T14 = Path("docs/relevo/2026-11-08-claude-tarea14")
T11 = Path("docs/relevo/2026-11-08-claude-tarea11/linux")
ESCENAS = {  # línea en píxeles del recorte, interior arriba en todas
    "oficina": ((0, 90, 221, 90), "data/annotations/oficina-cruces.json", T11 / "oficina/eventos/yolo11n-calibrado.json"),
    "kaggle": ((0, 480, 839, 480), "data/annotations/kaggle-people-boarding-bus-cruces.json",
               T11 / "kaggle/eventos/yolo11n-calibrado.json"),
    "pamela-A": ((0, 96, 159, 96), "data/annotations/pamela-A-cruces.json", T11 / "pamela-A/eventos/yolo11n-calibrado.json"),
    "prueba-bus (desarrollo)": ((274, 431, 467, 242), "data/annotations/prueba-bus-cruces.json",
                                Path("docs/relevo/2026-11-08-claude-tarea13/primera-evaluacion/prediccion.json")),
}


def contar(cuadros, linea, filtro):
    contador = ContadorCruces(Linea(*linea, interior="arriba"), margen_px=5.0, confirmacion=2)
    observaciones = iter([[(i, tuple(c)) for i, c in cuadro["obs"]] for cuadro in cuadros])
    procesar(((c["t"], None) for c in cuadros), lambda _: next(observaciones), contador, filtro=filtro)
    return [{"tiempo_s": round(e.tiempo_s, 3), "track_id": int(e.track_id), "sentido": e.sentido}
            for e in contador.eventos_ordenados()]


def resumen(metricas):
    return {s: {"TP": m["aciertos"], "FP": m["falsos_positivos"], "FN": m["omisiones"]}
            for s, m in metricas["sentidos"].items()}


def main():
    salida = T14 / "resultados"
    if salida.exists():
        raise SystemExit(f"{salida} ya existe.")
    resultados = {}
    for escena, (linea, ruta_ref, ruta_original) in ESCENAS.items():
        nombre = escena.split(" ")[0]
        cuadros = json.loads((T14 / "tracks" / f"{nombre}.json").read_text(encoding="utf-8"))["cuadros"]
        referencia = json.loads(Path(ruta_ref).read_text(encoding="utf-8"))["eventos"]
        original = json.loads(ruta_original.read_text(encoding="utf-8"))["eventos"]
        base = contar(cuadros, linea, None)
        filtro = FiltroSuperpuestas(0.6, 1.0)
        filtrado = contar(cuadros, linea, filtro)
        resultados[escena] = {
            "base_reproduce_la_ejecucion_original": [(e["sentido"], e["track_id"]) for e in base]
                                                     == [(e["sentido"], e["track_id"]) for e in original],
            "base": {"eventos": base, "metricas": resumen(evaluar(referencia, base, 1.0))},
            "filtrado": {"eventos": filtrado, "descartados": filtro.descartados,
                         "metricas": resumen(evaluar(referencia, filtrado, 1.0))},
        }
        r = resultados[escena]
        print(f"{escena:24} reproduce={r['base_reproduce_la_ejecucion_original']}  base={r['base']['metricas']}  "
              f"filtrado={r['filtrado']['metricas']}")
    salida.mkdir()
    (salida / "comparacion.json").write_text(json.dumps(resultados, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
