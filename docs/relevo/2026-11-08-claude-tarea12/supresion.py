"""Tarea 12: supresión temporal de duplicados sobre eventos ya guardados (sin inferencia). Ver prerregistro.md.

Desde la raíz del worktree:  python docs/relevo/2026-11-08-claude-tarea12/supresion.py
Escribe resultados-exploratorios/ (se niega si ya existe).
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from evaluation.evaluate import SENTIDOS, evaluar  # noqa: E402

UMBRALES = (0.0, 0.5, 1.0, 1.5)
DETECTORES = ("yolo11n-calibrado", "yolo11l-calibrado")
API = "yolo11n-calibrado"
T11 = Path("docs/relevo/2026-11-08-claude-tarea11/linux")
ESCENAS = {"kaggle": "data/annotations/kaggle-people-boarding-bus-cruces.json",
           "pamela-A": "data/annotations/pamela-A-cruces.json"}
SALIDA = Path("docs/relevo/2026-11-08-claude-tarea12/resultados-exploratorios")


def suprimir(eventos, umbral):
    """Regla prerregistrada: por sentido, descarta un evento si dista < umbral del último ACEPTADO de su sentido."""
    aceptados, descartados, ultimo = [], [], {}
    for evento in sorted(eventos, key=lambda e: e["tiempo_s"]):  # sorted es estable: empates en orden original
        previo = ultimo.get(evento["sentido"])
        if previo is not None and evento["tiempo_s"] - previo["tiempo_s"] < umbral:
            descartados.append({**evento, "suprimido_por": previo})
        else:
            aceptados.append(evento)
            ultimo[evento["sentido"]] = evento
    return aceptados, descartados


def leer(ruta):
    return json.loads(Path(ruta).read_text(encoding="utf-8"))["eventos"]


def sha(ruta):
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


def resumen_metricas(metricas):
    return {s: {"TP": m["aciertos"], "FP": m["falsos_positivos"], "FN": m["omisiones"],
                "error_conteo_abs": m["error_conteo_abs"]} for s, m in metricas["sentidos"].items()}


def main():
    if SALIDA.exists():
        raise SystemExit(f"{SALIDA} ya existe: no se sobrescriben resultados.")
    filas, insumos, cota_referencia = {}, {}, {}
    for escena, ruta_ref in ESCENAS.items():
        referencia = leer(ruta_ref)
        insumos[ruta_ref] = sha(ruta_ref)
        cota_referencia[escena] = {str(u): len(suprimir(referencia, u)[1]) for u in UMBRALES}
        for detector in DETECTORES:
            ruta = T11 / escena / "eventos" / f"{detector}.json"
            insumos[str(ruta)] = sha(ruta)
            for u in UMBRALES:
                aceptados, descartados = suprimir(leer(ruta), u)
                metricas = evaluar(referencia, aceptados, 1.0)
                fila = filas.setdefault(f"{detector}@{u}", {"detector": detector, "umbral_s": u, "escenas": {}})
                fila["escenas"][escena] = {"por_sentido": resumen_metricas(metricas), "descartados": descartados}
    for fila in filas.values():
        sentidos = [m for e in fila["escenas"].values() for m in e["por_sentido"].values()]
        fila["errores"] = sum(m["FP"] + m["FN"] for m in sentidos)
        fila["error_conteo_abs"] = sum(m["error_conteo_abs"] for m in sentidos)
        base = filas[f"{fila['detector']}@0.0"]
        fila["omisiones_no_aumentan"] = all(
            fila["escenas"][e]["por_sentido"][s]["FN"] <= base["escenas"][e]["por_sentido"][s]["FN"]
            for e in ESCENAS for s in SENTIDOS)
        fila["mejora_su_detector_sin_filtro"] = fila["umbral_s"] > 0 and fila["errores"] < base["errores"]
    validas = [f for f in filas.values() if f["omisiones_no_aumentan"] and f["mejora_su_detector_sin_filtro"]]
    elegida = min(validas, key=lambda f: (f["errores"], f["error_conteo_abs"], f["umbral_s"]), default=None)
    resultado = {
        "aviso": "EXPLORATORIO: referencias de Claude sin revisión humana. No es una selección definitiva.",
        "tolerancia_s": 1.0, "insumos_sha256": insumos, "cota_referencia_borrada": cota_referencia,
        "api_actual": f"{API}@0.0", "filas": filas,
        "elegida": f"{elegida['detector']}@{elegida['umbral_s']}" if elegida else None,
        "conclusion": ("Hay una variante que reduce errores sin aumentar omisiones." if elegida else
                       "Ninguna variante con u > 0 mejora a su detector sin aumentar omisiones: "
                       "la supresión temporal global no se justifica."),
    }
    SALIDA.mkdir(parents=True)
    (SALIDA / "resultados.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    lineas = ["| Variante | Kaggle sub. TP/FP/FN | Kaggle baj. | PAMELA sub. | PAMELA baj. | Errores | Error conteo | FN no sube |",
              "|---|---|---|---|---|---|---|---|"]
    for clave, f in filas.items():
        celdas = [f"{m['TP']}/{m['FP']}/{m['FN']}" for e in ESCENAS for m in f["escenas"][e]["por_sentido"].values()]
        lineas.append(f"| {clave} | " + " | ".join(celdas) + f" | {f['errores']} | {f['error_conteo_abs']} | "
                      f"{'sí' if f['omisiones_no_aumentan'] else 'NO'} |")
    texto = "\n".join(lineas + ["", f"Cota (eventos de la referencia que borraría la regla): {cota_referencia}",
                                f"Elegida: {resultado['elegida']}", resultado["conclusion"]])
    (SALIDA / "tabla.md").write_text(texto + "\n", encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    main()
