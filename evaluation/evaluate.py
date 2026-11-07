"""Compara predicciones con cruces de referencia: aciertos, omisiones, falsos positivos y F1 por sentido.

Cada cruce de referencia se empareja con una única predicción de igual sentido dentro de la tolerancia.

Se ejecuta desde la raíz: python -m evaluation.evaluate --help
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

SENTIDOS = ("subida", "bajada")


def emparejar(referencia, prediccion, tolerancia=1.0):
    """Empareja dos listas de tiempos. Recorrerlas en orden logra el máximo de pares con esta tolerancia."""
    referencia, prediccion = sorted(referencia), sorted(prediccion)
    pares, omitidos, sobrantes = [], [], []
    i = j = 0
    while i < len(referencia) and j < len(prediccion):
        if abs(referencia[i] - prediccion[j]) <= tolerancia:
            pares.append((referencia[i], prediccion[j]))
            i += 1
            j += 1
        elif prediccion[j] < referencia[i]:
            sobrantes.append(prediccion[j])
            j += 1
        else:
            omitidos.append(referencia[i])
            i += 1
    return pares, omitidos + referencia[i:], sobrantes + prediccion[j:]


def _razon(a, b):
    return round(a / b, 4) if b else None


def _f1(aciertos, omisiones, falsos):
    return _razon(2 * aciertos, 2 * aciertos + omisiones + falsos)


def _en_tramo(evento, desde, hasta):
    return evento["tiempo_s"] >= desde and (hasta is None or evento["tiempo_s"] < hasta)


def evaluar(referencia, prediccion, tolerancia=1.0, desde=0.0, hasta=None):
    """Recibe listas de eventos del contrato de la API y devuelve las métricas del tramo [desde, hasta)."""
    resultado = {"tolerancia_s": tolerancia, "tramo_s": {"desde": desde, "hasta": hasta}, "sentidos": {}}
    aciertos_totales = omisiones_totales = falsos_totales = 0
    for sentido in SENTIDOS:
        tiempos_referencia = [e["tiempo_s"] for e in referencia if e["sentido"] == sentido and _en_tramo(e, desde, hasta)]
        tiempos_prediccion = [e["tiempo_s"] for e in prediccion if e["sentido"] == sentido and _en_tramo(e, desde, hasta)]
        pares, omitidos, sobrantes = emparejar(tiempos_referencia, tiempos_prediccion, tolerancia)
        aciertos_totales += len(pares)
        omisiones_totales += len(omitidos)
        falsos_totales += len(sobrantes)
        resultado["sentidos"][sentido] = {
            "referencia": len(tiempos_referencia),
            "predichos": len(tiempos_prediccion),
            "aciertos": len(pares),
            "omisiones": len(omitidos),
            "falsos_positivos": len(sobrantes),
            "precision": _razon(len(pares), len(tiempos_prediccion)),
            "exhaustividad": _razon(len(pares), len(tiempos_referencia)),
            "f1": _f1(len(pares), len(omitidos), len(sobrantes)),
            "error_conteo_abs": abs(len(tiempos_prediccion) - len(tiempos_referencia)),
            "error_tiempo_medio_s": _razon(sum(abs(a - b) for a, b in pares), len(pares)),
            "tiempos_omitidos_s": omitidos,
            "tiempos_falsos_s": sobrantes,
        }
    resultado["total"] = {
        "aciertos": aciertos_totales,
        "omisiones": omisiones_totales,
        "falsos_positivos": falsos_totales,
        "f1": _f1(aciertos_totales, omisiones_totales, falsos_totales),
    }
    return resultado


def main(argv=None):
    parser = argparse.ArgumentParser(description="Compara predicciones con cruces de referencia.")
    parser.add_argument("--referencia", type=Path, required=True)
    parser.add_argument("--prediccion", type=Path, required=True)
    parser.add_argument("--tolerancia", type=float, default=1.0, help="Segundos. Acordada antes de evaluar.")
    parser.add_argument("--desde", type=float, default=0.0, help="Inicio del tramo, en segundos.")
    parser.add_argument("--hasta", type=float, help="Fin del tramo, en segundos, sin incluirlo.")
    parser.add_argument("--salida", type=Path, help="JSON con el detalle.")
    args = parser.parse_args(argv)

    referencia = json.loads(args.referencia.read_text(encoding="utf-8"))["eventos"]
    prediccion = json.loads(args.prediccion.read_text(encoding="utf-8"))["eventos"]
    resultado = evaluar(referencia, prediccion, args.tolerancia, args.desde, args.hasta)
    for sentido, metricas in resultado["sentidos"].items():
        print(f"{sentido}: {metricas['aciertos']}/{metricas['referencia']} aciertos, "
              f"{metricas['falsos_positivos']} falsos positivos, F1 {metricas['f1']}")
    print(f"total: {resultado['total']}")
    if args.salida:
        args.salida.parent.mkdir(parents=True, exist_ok=True)
        args.salida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
