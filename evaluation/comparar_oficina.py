"""Compara el detector base y el ajustado sobre el video de oficina, con el mismo evaluador.

Se ejecuta desde la raíz: python -m evaluation.comparar_oficina

El video entero viene de una sola grabación, usada también para entrenar y calibrar. Estas cifras
orientan el trabajo, pero no sirven como métricas del informe.
"""
from __future__ import annotations

import json
from pathlib import Path

from evaluation.evaluate import evaluar
from vision.pipeline import guardar_json, main as ejecutar_pipeline, ruta_de_configuracion

RESULTADOS = Path("evaluation/results")
REFERENCIA = Path("data/annotations/oficina-cruces.json")
ESCENA = ["--video", "data/raw/oficina.mp4", "--recorte", "228,2,222,176", "--linea", "0,90,221,90",
          "--interior", "arriba", "--dispositivo", "cpu", "--parada", "Puerta de oficina · video completo"]
CALIBRADO = ["--rastreador", "vision/bytetrack-cenital.yaml", "--conf", "0.05", "--confirmacion", "2"]
AJUSTADO = "runs/oficina-ajuste/oficina-ajustado.pt"
CONFIGURACIONES = {
    "base-defecto": ["--pesos", "yolo11n.pt"],
    "base-calibrado": ["--pesos", "yolo11n.pt", *CALIBRADO],
    "ajustado-defecto": ["--pesos", AJUSTADO],
    "ajustado-calibrado": ["--pesos", AJUSTADO, *CALIBRADO],
}
TRAMOS = {"ensayo": (0.0, 6.0), "entrenamiento": (6.0, 43.0), "reserva": (43.0, None), "completo": (0.0, None)}


def leer_eventos(ruta):
    return json.loads(Path(ruta).read_text(encoding="utf-8"))["eventos"]


def resumir(metricas):
    subida, bajada = metricas["sentidos"]["subida"], metricas["sentidos"]["bajada"]
    return {
        "subidas": f"{subida['aciertos']}/{subida['referencia']}",
        "bajadas": f"{bajada['aciertos']}/{bajada['referencia']}",
        "falsos_positivos": metricas["total"]["falsos_positivos"],
        "f1": metricas["total"]["f1"],
    }


def main():
    referencia = leer_eventos(REFERENCIA)
    comparacion = {
        "aviso": "Una sola grabación, también usada para entrenar y calibrar: orienta, pero no sirve para el informe.",
        "referencia": str(REFERENCIA),
        "configuraciones": {},
    }
    for nombre, opciones in CONFIGURACIONES.items():
        salida = RESULTADOS / f"oficina-completo-{nombre}.json"
        ejecutar_pipeline([*ESCENA, *opciones, "--salida", str(salida)])
        prediccion = leer_eventos(salida)
        medicion = json.loads(ruta_de_configuracion(salida).read_text(encoding="utf-8"))["medicion"]
        tramos = {tramo: evaluar(referencia, prediccion, 1.0, *limites) for tramo, limites in TRAMOS.items()}
        comparacion["configuraciones"][nombre] = {
            "opciones": opciones,
            "fps_procesados": medicion["fps_procesados"],
            "resumen": {tramo: resumir(metricas) for tramo, metricas in tramos.items()},
            "detalle_completo": tramos["completo"],
        }
    guardar_json(RESULTADOS / "oficina-comparacion.json", comparacion)

    print(f"\n{'configuración':20} {'tramo':14} {'subidas':8} {'bajadas':8} {'falsos':7} {'F1':6}")
    for nombre, datos in comparacion["configuraciones"].items():
        for tramo, fila in datos["resumen"].items():
            print(f"{nombre:20} {tramo:14} {fila['subidas']:8} {fila['bajadas']:8} "
                  f"{fila['falsos_positivos']:<7} {fila['f1']}")
        print(f"{nombre:20} FPS: {datos['fps_procesados']}")


if __name__ == "__main__":
    main()
