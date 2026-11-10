"""Limitación conocida (tarea 14): varias cajas encimadas sobre una misma persona cuentan un cruce cada una.

Se observó en el video de la tarea 13: a los 8,20, 8,24 y 8,36 s una sola persona baja con tres cajas
(IDs distintos) y se registran tres bajadas. La corrección probada (filtro de cajas encimadas) bajó los falsos
positivos pero borró cruces reales en PAMELA A, así que no se incorporó: ver evaluation/results/filtro-cajas-encimadas/.
Mientras el defecto exista, la prueba se informa como «xfail» (visible en el resumen de pytest); cuando se
corrija, pasa sola.
"""
import pytest

from vision.cruces import ContadorCruces, Linea
from vision.pipeline import procesar


def test_una_persona_con_tres_cajas_cuenta_un_cruce():
    def cajas(y):  # entera, parcial y una más grande, centradas en la misma persona
        return [(1, [80, y - 20, 120, y + 20]), (2, [90, y - 10, 110, y + 10]), (3, [70, y - 30, 130, y + 30])]

    recorrido = [cajas(y) for y in range(60, 141, 10)]
    contador = ContadorCruces(Linea(0, 100, 200, 100, interior="arriba"), margen_px=5, confirmacion=2)
    iterador = iter(recorrido)
    procesar(((i / 10, None) for i in range(len(recorrido))), lambda _: next(iterador), contador)
    eventos = contador.eventos_ordenados()
    if len(eventos) != 1:
        pytest.xfail(f"limitación conocida: {len(eventos)} cruces para una sola persona con cajas encimadas")
    assert [e.sentido for e in eventos] == ["bajada"]
