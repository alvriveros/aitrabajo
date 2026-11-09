"""Casos de la regla prerregistrada.  python -m pytest docs/relevo/2026-11-08-claude-tarea12/test_supresion.py -q"""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("supresion", Path(__file__).with_name("supresion.py"))
supresion = importlib.util.module_from_spec(spec)
spec.loader.exec_module(supresion)


def ev(t, sentido="subida", track=1):
    return {"tiempo_s": t, "track_id": track, "sentido": sentido}


def tiempos(eventos):
    return [e["tiempo_s"] for e in eventos]


def test_sin_filtro_no_descarta_ni_simultaneos():
    eventos = [ev(19.8, "bajada", 1), ev(19.8, "bajada", 2), ev(1.0)]
    aceptados, descartados = supresion.suprimir(eventos, 0.0)
    assert tiempos(aceptados) == [1.0, 19.8, 19.8] and descartados == []


def test_cadena_se_mide_desde_el_ultimo_aceptado():
    aceptados, descartados = supresion.suprimir([ev(t) for t in (0, 1, 2, 3)], 1.5)
    assert tiempos(aceptados) == [0, 2] and tiempos(descartados) == [1, 3]
    assert descartados[0]["suprimido_por"]["tiempo_s"] == 0


def test_limite_exacto_se_conserva():
    assert tiempos(supresion.suprimir([ev(0.0), ev(1.5)], 1.5)[0]) == [0.0, 1.5]
    assert tiempos(supresion.suprimir([ev(0.0), ev(1.49)], 1.5)[0]) == [0.0]


def test_simultaneos_conserva_el_primero_del_archivo():
    aceptados, descartados = supresion.suprimir([ev(5.0, track=7), ev(5.0, track=3)], 0.5)
    assert [e["track_id"] for e in aceptados] == [7] and [e["track_id"] for e in descartados] == [3]


def test_sentidos_opuestos_no_interactuan():
    aceptados, _ = supresion.suprimir([ev(34.12, "subida", 10), ev(34.32, "bajada", 10)], 1.5)
    assert [e["sentido"] for e in aceptados] == ["subida", "bajada"]


def test_desordenados_se_ordenan():
    assert tiempos(supresion.suprimir([ev(2.0), ev(0.0), ev(0.4)], 0.5)[0]) == [0.0, 2.0]
