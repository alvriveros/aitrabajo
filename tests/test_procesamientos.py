"""Endpoints de procesamiento de video con un pipeline simulado: no necesitan el modelo, el clip ni los pesos."""
import json
import subprocess
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import api.main as api

cliente = TestClient(api.app)
PREDICCION = {"capacidad": 20, "carga_inicial": 0, "paradas": [{"nombre": "Puerta", "inicio_s": 0}],
              "eventos": [{"tiempo_s": 2.16, "track_id": 1, "sentido": "subida"}]}


@pytest.fixture
def raiz(tmp_path, monkeypatch):
    """Raíz falsa con el video y los pesos de la configuración guardada."""
    for nombre in ("data/raw/oficina.mp4", "yolo11n.pt"):
        (tmp_path / nombre).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / nombre).write_bytes(b"x")
    monkeypatch.setattr(api, "RAIZ", tmp_path)
    monkeypatch.setattr(api, "EJECUCIONES", tmp_path / "runs/panel")
    monkeypatch.setattr(api, "find_spec", lambda nombre: object())
    return tmp_path


def pipeline_simulado(comandos, codigo=0):
    def correr(comando, **opciones):
        comandos.append(comando)
        salida = Path(comando[comando.index("--salida") + 1])
        salida.write_text(json.dumps(PREDICCION), encoding="utf-8")
        salida.with_suffix(".config.json").write_text(json.dumps({"pesos": "yolo11n.pt"}), encoding="utf-8")
        Path(comando[comando.index("--video-anotado") + 1]).write_bytes(b"webm")
        return subprocess.CompletedProcess(comando, codigo, "2 eventos", "" if not codigo else "falló")
    return correr


def test_usa_la_configuracion_guardada_con_destinos_propios(raiz, monkeypatch):
    comandos = []
    monkeypatch.setattr(api.subprocess, "run", pipeline_simulado(comandos))
    respuesta = cliente.post("/procesamientos")
    assert respuesta.status_code == 201, respuesta.text
    cuerpo = respuesta.json()
    assert cuerpo["recorrido"] == PREDICCION

    comando = comandos[0]
    opciones = dict(zip(comando[3::2], comando[4::2]))
    assert opciones["--video"] == "data/raw/oficina.mp4"
    assert (opciones["--inicio"], opciones["--fin"]) == ("0", "6")
    assert opciones["--recorte"] == "228,2,222,176" and opciones["--linea"] == "0,90,221,90"
    assert opciones["--pesos"] == "yolo11n.pt" and opciones["--conf"] == "0.05"
    assert comando.count("--salida") == 1 and comando.count("--video-anotado") == 1
    assert opciones["--salida"].startswith(str(raiz / "runs/panel" / cuerpo["id"]))

    assert cliente.get("/procesamientos").json() == [cuerpo["id"]]
    assert cliente.get(f"/procesamientos/{cuerpo['id']}").json() == cuerpo
    video = cliente.get(f"/procesamientos/{cuerpo['id']}/video")
    assert video.status_code == 200 and video.content == b"webm"


def test_sin_video_ni_pesos_responde_503_con_los_archivos_faltantes(raiz, monkeypatch):
    (raiz / "data/raw/oficina.mp4").unlink()
    (raiz / "yolo11n.pt").unlink()
    monkeypatch.setattr(api.subprocess, "run", lambda *a, **k: pytest.fail("no debe ejecutar el pipeline"))
    respuesta = cliente.post("/procesamientos")
    assert respuesta.status_code == 503
    assert "data/raw/oficina.mp4" in respuesta.json()["detail"] and "yolo11n.pt" in respuesta.json()["detail"]


def sin_publicar(raiz):
    """La ejecución no aparece ni se puede consultar, pero conserva su registro."""
    carpeta, = (raiz / "runs/panel").iterdir()
    assert cliente.get("/procesamientos").json() == []
    assert cliente.get(f"/procesamientos/{carpeta.name}").status_code == 404
    assert cliente.get(f"/procesamientos/{carpeta.name}/video").status_code == 404
    return (carpeta / "registro.txt").read_text(encoding="utf-8")


def test_un_fallo_despues_de_escribir_archivos_no_se_publica(raiz, monkeypatch):
    monkeypatch.setattr(api.subprocess, "run", pipeline_simulado([], codigo=1))
    respuesta = cliente.post("/procesamientos")
    assert respuesta.status_code == 500 and "falló" in respuesta.json()["detail"]
    assert (next((raiz / "runs/panel").iterdir()) / "prediccion.json").is_file()
    assert "falló" in sin_publicar(raiz)


def test_un_timeout_no_se_publica_y_conserva_la_salida_parcial(raiz, monkeypatch):
    def cortar(comando, **opciones):
        pipeline_simulado([])(comando)
        raise subprocess.TimeoutExpired(comando, 600, output=b"cuadro 120", stderr=None)
    monkeypatch.setattr(api.subprocess, "run", cortar)
    assert cliente.post("/procesamientos").status_code == 504
    assert sin_publicar(raiz) == "cuadro 120"


def test_un_resultado_ilegible_no_se_publica(raiz, monkeypatch):
    def ilegible(comando, **opciones):
        resultado = pipeline_simulado([])(comando)
        Path(comando[comando.index("--salida") + 1]).write_text("{incompleto", encoding="utf-8")
        return resultado
    monkeypatch.setattr(api.subprocess, "run", ilegible)
    respuesta = cliente.post("/procesamientos")
    assert respuesta.status_code == 500 and "legible" in respuesta.json()["detail"]
    sin_publicar(raiz)


@pytest.mark.parametrize("ruta, codigo", [
    ("/procesamientos/20261107-120000-000000", 404),
    ("/procesamientos/..%2F..%2Fapi", 404),
    ("/procesamientos/abc/video", 422),
])
def test_ids_desconocidos_o_invalidos(raiz, ruta, codigo):
    assert cliente.get(ruta).status_code == codigo
