import copy
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import app

cliente = TestClient(app)
EJEMPLO = json.loads((Path(__file__).parents[1] / "docs/demo/recorrido.json").read_text(encoding="utf-8"))


def recorrido(**cambios):
    datos = copy.deepcopy(EJEMPLO)
    datos.update(cambios)
    return datos


def evento(t, track_id, sentido):
    return {"tiempo_s": t, "track_id": track_id, "sentido": sentido}


def calcular(datos):
    respuesta = cliente.post("/ocupacion", json=datos)
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()


def test_ejemplo_coincide_con_calculo_manual():
    # 3 + 2 subidas = 5 en Parada 1; la bajada a los 10 s cae en Parada 2: 5 - 1 = 4 (4/20 = 20 %)
    filas = calcular(EJEMPLO)["paradas"]
    assert filas == [
        {"parada": "Parada 1", "subidas": 2, "bajadas": 0, "pasajeros": 5, "ocupacion_pct": 25.0},
        {"parada": "Parada 2", "subidas": 0, "bajadas": 1, "pasajeros": 4, "ocupacion_pct": 20.0},
    ]


def test_cruces_simultaneos_y_parada_vacia():
    datos = recorrido(
        paradas=[{"nombre": "A", "inicio_s": 0}, {"nombre": "B", "inicio_s": 10}, {"nombre": "C", "inicio_s": 20}],
        eventos=[evento(3, 1, "subida"), evento(3, 2, "subida")],
    )
    respuesta = calcular(datos)
    assert [(f["subidas"], f["bajadas"], f["pasajeros"]) for f in respuesta["paradas"]] == [(2, 0, 5), (0, 0, 5), (0, 0, 5)]
    assert respuesta["avisos"] == []


def test_bajada_con_bus_vacio_deja_aviso_aunque_se_recupere():
    datos = recorrido(carga_inicial=0, eventos=[evento(1, 1, "bajada"), evento(2, 2, "subida")])
    respuesta = calcular(datos)
    assert respuesta["paradas"][0]["pasajeros"] == 0
    assert respuesta["avisos"] == ["Conteo negativo en Parada 1 a los 1 s."]


@pytest.mark.parametrize("cambios", [
    {"capacidad": 0},
    {"eventos": [evento(2, 1, "lateral")]},
    {"eventos": [evento(5, 1, "subida"), evento(2, 2, "subida")]},
    {"paradas": [{"nombre": "A", "inicio_s": 0}, {"nombre": "B", "inicio_s": 0}]},
], ids=["capacidad_cero", "sentido_desconocido", "eventos_desordenados", "inicio_repetido"])
def test_entradas_invalidas_dan_422(cambios):
    assert cliente.post("/ocupacion", json=recorrido(**cambios)).status_code == 422
