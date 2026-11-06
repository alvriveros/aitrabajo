"""Camino completo con el detector y ByteTrack reales sobre un clip sintético.

Ejecuta el código de video y del modelo, pero no dice nada sobre el desempeño en un clip real.
Se omite si faltan las dependencias de visión o los pesos, para no descargar nada durante las pruebas.
"""
import json
from pathlib import Path

import pytest

pytest.importorskip("ultralytics")

import cv2  # noqa: E402
import numpy as np  # noqa: E402
from ultralytics import ASSETS, YOLO  # noqa: E402

from vision.pipeline import main  # noqa: E402

RAIZ = Path(__file__).parents[1]
PESOS = RAIZ / "yolo11n.pt"
OFICINA = RAIZ / "data/raw/oficina.mp4"
FPS = 30
pytestmark = pytest.mark.skipif(not PESOS.exists(), reason="Faltan los pesos yolo11n.pt en la raíz.")


def centro_y(t):
    """Altura de la persona: pasa la línea (y = 180) a los 2 s y vuelve a los 4 s."""
    if t < 1.5:
        return 240
    if t < 2.5:
        return 240 - 120 * (t - 1.5)
    if t < 3.5:
        return 120
    if t < 4.5:
        return 120 + 120 * (t - 3.5)
    return 240


@pytest.fixture(scope="module")
def clip(tmp_path_factory):
    """Cuadro de 1280x720 como el del ensayo: la misma persona en las dos vistas superiores y un tablero debajo."""
    imagen = cv2.imread(str(ASSETS / "bus.jpg"))
    cajas = YOLO(str(PESOS)).predict(imagen, classes=[0], verbose=False)[0].boxes.xyxy.tolist()
    x1, y1, x2, y2 = map(int, max(cajas, key=lambda caja: caja[3] - caja[1]))
    escala = 230 / (y2 - y1)
    persona = cv2.resize(imagen[y1:y2, x1:x2], None, fx=escala, fy=escala)
    alto, ancho = persona.shape[:2]
    fondo = cv2.GaussianBlur(cv2.resize(imagen, (640, 360)), (0, 0), 25)

    ruta = tmp_path_factory.mktemp("sintetico") / "clip.mp4"
    escritor = cv2.VideoWriter(str(ruta), cv2.VideoWriter_fourcc(*"mp4v"), FPS, (1280, 720))
    for indice in range(6 * FPS):
        vista = fondo.copy()
        arriba = int(centro_y(indice / FPS)) - alto // 2
        izquierda = 320 - ancho // 2
        vista[arriba:arriba + alto, izquierda:izquierda + ancho] = persona
        cuadro = np.zeros((720, 1280, 3), dtype="uint8")
        cuadro[:360, :640] = vista
        cuadro[:360, 640:] = vista
        cv2.putText(cuadro, f"IN 0 OUT 0  {indice}", (60, 560), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4)
        escritor.write(cuadro)
    escritor.release()
    return ruta


def ejecutar_pipeline(clip, salida, *extra):
    main(["--video", str(clip), "--inicio", "0", "--fin", "6", "--interior", "arriba",
          "--salida", str(salida), "--pesos", str(PESOS), *extra])
    return json.loads(salida.read_text(encoding="utf-8"))["eventos"]


def test_el_recorte_cuenta_una_subida_y_una_bajada_con_el_mismo_id(clip, tmp_path):
    anotado = tmp_path / "anotado.mp4"
    eventos = ejecutar_pipeline(clip, tmp_path / "prediccion.json", "--recorte", "640,0,640,360",
                                "--linea", "0,180,640,180", "--video-anotado", str(anotado))
    assert [evento["sentido"] for evento in eventos] == ["subida", "bajada"]
    assert eventos[0]["track_id"] == eventos[1]["track_id"]
    assert abs(eventos[0]["tiempo_s"] - 2) < 0.1
    assert abs(eventos[1]["tiempo_s"] - 4) < 0.1
    assert anotado.stat().st_size > 0


def test_sin_recorte_se_cuentan_las_dos_vistas(clip, tmp_path):
    # Por esto el relevo pide procesar un solo cuadrante: la misma persona contaría dos veces.
    eventos = ejecutar_pipeline(clip, tmp_path / "prediccion.json", "--linea", "0,180,1280,180")
    assert sorted(evento["sentido"] for evento in eventos) == ["bajada", "bajada", "subida", "subida"]


@pytest.mark.skipif(not OFICINA.exists(), reason="Falta el clip en data/raw/oficina.mp4.")
def test_ensayo_de_oficina_sigue_dentro_de_la_tolerancia_de_la_referencia_manual(tmp_path):
    # Protege la calibración de este ensayo. No mide el desempeño: el clip se usó para calibrar.
    manual = json.loads((RAIZ / "docs/demo/oficina-00-06-manual.json").read_text(encoding="utf-8"))["eventos"]
    eventos = ejecutar_pipeline(OFICINA, tmp_path / "prediccion.json", "--recorte", "228,2,222,176",
                                "--linea", "0,90,221,90", "--rastreador", str(RAIZ / "vision/bytetrack-cenital.yaml"),
                                "--conf", "0.05", "--confirmacion", "2", "--dispositivo", "cpu")
    assert [evento["sentido"] for evento in eventos] == [evento["sentido"] for evento in manual]
    for predicho, referencia in zip(eventos, manual):
        assert abs(predicho["tiempo_s"] - referencia["tiempo_s"]) <= 1
