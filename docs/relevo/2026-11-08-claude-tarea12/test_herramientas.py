"""Pruebas de las herramientas corregidas en la tarea 12 (sin inferencia; la referencia histórica solo se lee).

Desde la raíz del worktree:  python -m pytest docs/relevo/2026-11-08-claude-tarea12/test_herramientas.py -q
"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

RAIZ = Path(__file__).resolve().parents[3]
T11 = RAIZ / "docs/relevo/2026-11-08-claude-tarea11"


def cargar(ruta):
    spec = importlib.util.spec_from_file_location(ruta.stem, ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


anotar = cargar(T11 / "anotar_cruces.py")


@pytest.fixture(scope="module")
def video(tmp_path_factory):
    """MP4 sintético (mp4v, con cuadros intermedios) de 120 cuadros a 25 FPS; el índice va en 7 bloques binarios."""
    ruta = tmp_path_factory.mktemp("v") / "sintetico.mp4"
    escritor = cv2.VideoWriter(str(ruta), cv2.VideoWriter_fourcc(*"mp4v"), 25, (112, 32))
    for i in range(120):
        imagen = np.zeros((32, 112, 3), np.uint8)
        for bit in range(7):
            imagen[:, 16 * bit:16 * bit + 16] = 255 * ((i >> bit) & 1)
        escritor.write(imagen)
    escritor.release()
    return ruta


def indice(imagen):
    return sum(1 << bit for bit in range(7) if imagen[8:24, 16 * bit + 4:16 * bit + 12].mean() > 127)


def test_navegacion_llega_al_cuadro_esperado(video):
    captura, fps, _ = anotar.abrir(video)
    navegador = anotar.Navegador(captura, fps)
    navegador.avanzar(60)

    def ir(tecla, esperado):
        assert anotar.navegar(navegador, ord(tecla), fps)
        cuadro, imagen = navegador.actual
        assert (cuadro, indice(imagen)) == (esperado, esperado), tecla

    assert navegador.actual[0] == indice(navegador.actual[1]) == 60
    assert navegador.tiempo == pytest.approx(60 / 25)  # marca del archivo = índice / FPS en un video a FPS fijo
    ir(",", 59); ir(".", 60); ir("a", 10); ir("a", 0)  # acotado al inicio
    ir("d", 50); ir("d", 100); ir("d", 119)  # acotado al final
    ir(",", 118); ir(".", 119)
    assert not anotar.navegar(navegador, ord("s"), fps)
    assert not navegador.avanzar(1)


def test_retroceso_limitado_al_buffer(video):
    captura, fps, _ = anotar.abrir(video)
    navegador = anotar.Navegador(captura, fps, segundos_atras=1)  # 25 cuadros
    navegador.avanzar(100)
    navegador.retroceder(50)
    assert navegador.actual[0] == indice(navegador.actual[1]) == 76


def test_video_invalido(tmp_path):
    with pytest.raises(SystemExit):
        anotar.abrir(tmp_path / "no-existe.mp4")


def test_no_sobrescribe(tmp_path, monkeypatch):
    salida = tmp_path / "ref.json"
    assert anotar.preparar_salida(salida, False) == {"notas": [], "eventos": []}
    salida.write_text(json.dumps({"notas": ["n"], "anotado_por": "X", "eventos": []}), encoding="utf-8")
    with pytest.raises(SystemExit, match="--continuar"):
        anotar.preparar_salida(salida, False)
    assert anotar.preparar_salida(salida, True)["notas"] == ["n"]
    monkeypatch.setattr(anotar, "PROTEGIDAS", {anotar.sha(salida)})
    with pytest.raises(SystemExit, match="protegida"):
        anotar.preparar_salida(salida, True)


def test_la_referencia_historica_esta_protegida():
    assert anotar.sha(RAIZ / "data/annotations/youtube-bus-real-cruces.json") in anotar.PROTEGIDAS


def test_guardar_conserva_metadatos(tmp_path, video):
    salida = tmp_path / "ref.json"
    previo = {"anotado_por": "Álvaro, sesión 1", "notas": ["aclaración"], "fecha": "antes", "eventos": []}
    eventos = [{"tiempo_s": 2.0, "track_id": 0, "sentido": "bajada"}, {"tiempo_s": 1.0, "track_id": 0, "sentido": "subida"}]
    anotar.guardar(salida, previo, eventos, video, "0,30,127,30", "Álvaro")
    documento = json.loads(salida.read_text(encoding="utf-8"))
    assert documento["anotado_por"] == "Álvaro, sesión 1" and documento["notas"] == ["aclaración"]
    assert documento["fecha"] == "antes" and len(documento["sesiones"]) == 1
    assert "antes de ejecutar" not in json.dumps(documento, ensure_ascii=False)
    assert [e["tiempo_s"] for e in documento["eventos"]] == [1.0, 2.0]


def test_evaluar_detectores_rechaza_destino_con_resultados(tmp_path):
    (tmp_path / "algo.json").write_text("{}")
    proceso = subprocess.run([sys.executable, str(T11 / "evaluar_detectores.py"), str(tmp_path), "--escenas", "kaggle",
                              "--modelos", "yolo11n"], cwd=RAIZ, capture_output=True, text=True)
    assert proceso.returncode != 0 and "ya tiene resultados" in proceso.stderr
