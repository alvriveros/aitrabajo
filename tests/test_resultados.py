"""Comprueba que los resultados versionados siguen siendo coherentes con la API y con el evaluador."""
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import app
from evaluation.evaluate import evaluar

RAIZ = Path(__file__).parents[1]
RESULTADOS = RAIZ / "evaluation/results"
PREDICCIONES = sorted(
    ruta for ruta in RESULTADOS.glob("oficina-*.json")
    if "eventos" in json.loads(ruta.read_text(encoding="utf-8"))
)
COMPARACION = json.loads((RESULTADOS / "oficina-comparacion.json").read_text(encoding="utf-8"))
REFERENCIA = json.loads((RAIZ / "data/annotations/oficina-cruces.json").read_text(encoding="utf-8"))["eventos"]


def test_hay_predicciones_para_revisar():
    assert len(PREDICCIONES) == 5


@pytest.mark.parametrize("ruta", PREDICCIONES, ids=lambda ruta: ruta.stem)
def test_cada_prediccion_cumple_el_contrato_de_la_api(ruta):
    respuesta = TestClient(app).post("/ocupacion", content=ruta.read_bytes(), headers={"Content-Type": "application/json"})
    assert respuesta.status_code == 200, respuesta.text


@pytest.mark.parametrize("nombre", COMPARACION["configuraciones"])
def test_la_comparacion_coincide_con_las_predicciones_guardadas(nombre):
    ruta = RESULTADOS / f"oficina-completo-{nombre}.json"
    eventos = json.loads(ruta.read_text(encoding="utf-8"))["eventos"]
    assert evaluar(REFERENCIA, eventos) == COMPARACION["configuraciones"][nombre]["detalle_completo"]


def test_el_detector_ajustado_termina_con_la_carga_correcta_y_sin_avisos():
    ruta = RESULTADOS / "oficina-completo-ajustado-defecto.json"
    respuesta = TestClient(app).post("/ocupacion", content=ruta.read_bytes(), headers={"Content-Type": "application/json"})
    cuerpo = respuesta.json()
    assert cuerpo["avisos"] == []
    fila = cuerpo["paradas"][0]
    assert (fila["subidas"], fila["bajadas"], fila["pasajeros"], fila["ocupacion_pct"]) == (10, 10, 0, 0.0)
