"""Comprueba que las anotaciones versionadas son coherentes. Un error acá se llevaría al entrenamiento."""
import json
from pathlib import Path

from fastapi.testclient import TestClient

from api.main import app

ANOTACIONES = Path(__file__).parents[1] / "data/annotations"
CAJAS = json.loads((ANOTACIONES / "oficina-cajas.json").read_text(encoding="utf-8"))
CRUCES = json.loads((ANOTACIONES / "oficina-cruces.json").read_text(encoding="utf-8"))


def test_las_cajas_entran_en_el_recorte():
    ancho, alto = CAJAS["recorte"]["ancho"], CAJAS["recorte"]["alto"]
    for cuadro in CAJAS["cuadros"]:
        if cuadro["caja"]:
            x1, y1, x2, y2 = cuadro["caja"]
            assert 0 <= x1 < x2 <= ancho and 0 <= y1 < y2 <= alto, cuadro


def test_cada_cuadro_aparece_una_vez():
    numeros = [cuadro["cuadro"] for cuadro in CAJAS["cuadros"]]
    assert len(numeros) == len(set(numeros))


def test_el_ensayo_queda_fuera_del_entrenamiento():
    assert all(cuadro["tiempo_s"] >= 6 for cuadro in CAJAS["cuadros"])
    assert {cuadro["particion"] for cuadro in CAJAS["cuadros"]} == {"entrenamiento", "reserva"}


def test_la_particion_sigue_el_tiempo():
    for cuadro in CAJAS["cuadros"]:
        assert (cuadro["particion"] == "reserva") == (cuadro["tiempo_s"] >= 43), cuadro


def test_solo_los_cuadros_sin_persona_no_tienen_caja():
    for cuadro in CAJAS["cuadros"]:
        assert (cuadro["caja"] is None) == (cuadro["origen"] in {"vacio", "sombra"}), cuadro


def test_los_cruces_alternan_y_coinciden_con_el_contador_del_video():
    sentidos = [evento["sentido"] for evento in CRUCES["eventos"]]
    assert sentidos.count("subida") == 10 and sentidos.count("bajada") == 10
    assert all(a != b for a, b in zip(sentidos, sentidos[1:]))


def test_los_cruces_cumplen_el_contrato_de_la_api():
    respuesta = TestClient(app).post("/ocupacion", json=CRUCES)
    assert respuesta.status_code == 200, respuesta.text
    fila = respuesta.json()["paradas"][0]
    assert (fila["subidas"], fila["bajadas"], fila["pasajeros"]) == (10, 10, 0)
    assert respuesta.json()["avisos"] == []
