"""Experimento de la tarea 14, no incorporado: filtro de cajas encimadas.  Desde la raíz:
python -m pytest docs/relevo/2026-11-08-claude-tarea14/experimento/test_filtro.py -q"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from filtro import FiltroSuperpuestas, procesar, superposicion  # noqa: E402

from vision.cruces import ContadorCruces, Linea  # noqa: E402

LINEA = Linea(0, 100, 200, 100, interior="arriba")  # subir = moverse hacia y menor


def caja(cx, cy, mitad=20):
    return [cx - mitad, cy - mitad, cx + mitad, cy + mitad]


def contar(trayectorias, filtro):
    """trayectorias: {track_id: [(cx, cy, mitad) por cuadro o None]}; 10 cuadros por segundo."""
    cuadros = max(len(t) for t in trayectorias.values())
    secuencia = []
    for i in range(cuadros):
        secuencia.append([(tid, caja(*t[i])) for tid, t in trayectorias.items() if i < len(t) and t[i]])
    contador = ContadorCruces(LINEA, margen_px=5, confirmacion=2)
    iterador = iter(secuencia)
    procesar(((i / 10, None) for i in range(cuadros)), lambda _: next(iterador), contador, filtro=filtro)
    return [(e.track_id, e.sentido) for e in contador.eventos_ordenados()]


def bajar(x, desde=60, hasta=140, mitad=20):
    return [(x, y, mitad) for y in range(desde, hasta + 1, 10)]


def test_superposicion():
    assert superposicion([0, 0, 10, 10], [2, 2, 6, 6]) == 1
    assert superposicion([0, 0, 10, 10], [20, 20, 30, 30]) == 0


def test_cajas_encimadas_de_una_persona_cuentan_una_vez():
    personas = {1: bajar(100), 2: bajar(102, mitad=12), 3: bajar(98, mitad=30)}  # entera, parcial y más grande
    assert len(contar(personas, None)) == 3  # el fallo: un cruce por caja
    assert len(contar(personas, FiltroSuperpuestas())) == 1  # cuenta una sola de las tres cajas


def test_caja_de_grupo_no_borra_a_las_personas():
    # la caja de grupo tiene el ID más bajo: igual se procesa después de las personas del mismo cuadro
    personas = {0: [(100, y, 60) for y in range(60, 141, 10)], 1: bajar(60, mitad=15), 2: bajar(140, mitad=15)}
    assert sorted(contar(personas, FiltroSuperpuestas())) == [(1, "bajada"), (2, "bajada")]


def test_dos_personas_a_la_vez_sin_encimarse_cuentan_dos():
    assert len(contar({1: bajar(40), 2: bajar(160)}, FiltroSuperpuestas())) == 2


def test_una_persona_puede_cruzar_y_volver():
    ida_y_vuelta = bajar(100) + bajar(100)[::-1]
    assert contar({1: ida_y_vuelta}, FiltroSuperpuestas()) == [(1, "bajada"), (1, "subida")]


def test_otra_persona_en_el_mismo_lugar_despues_de_la_ventana_cuenta():
    primera = bajar(100) + [None] * 20  # sale de cuadro y su última caja queda registrada
    segunda = [None] * 20 + bajar(100)  # 2 s después, otra persona por el mismo lugar
    assert len(contar({1: primera, 2: segunda}, FiltroSuperpuestas())) == 2


def test_sentidos_opuestos_encimados_no_se_filtran():
    assert len(contar({1: bajar(100), 2: bajar(100)[::-1]}, FiltroSuperpuestas())) == 2
