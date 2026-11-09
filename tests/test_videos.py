"""Subida y procesamiento de videos nuevos desde el panel, con un pipeline simulado (sin modelo ni pesos reales)."""
import json
import subprocess
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import api.main as api

cv2 = pytest.importorskip("cv2")
np = pytest.importorskip("numpy")
cliente = TestClient(api.app)
GEOMETRIA = {"recorte": [10, 0, 100, 60], "linea": [0, 30, 99, 30], "interior": "arriba"}


def mp4(ruta, cuadros=50, fps=25):
    escritor = cv2.VideoWriter(str(ruta), cv2.VideoWriter_fourcc(*"mp4v"), fps, (128, 64))
    for i in range(cuadros):
        escritor.write(np.full((64, 128, 3), (i * 5) % 255, np.uint8))
    escritor.release()
    return ruta.read_bytes()


@pytest.fixture
def raiz(tmp_path, monkeypatch):
    (tmp_path / "yolo11n.pt").write_bytes(b"x")
    monkeypatch.setattr(api, "RAIZ", tmp_path)
    monkeypatch.setattr(api, "EJECUCIONES", tmp_path / "runs/panel")
    monkeypatch.setattr(api, "VIDEOS", tmp_path / "runs/videos")
    monkeypatch.setattr(api, "find_spec", lambda nombre: object())
    return tmp_path


@pytest.fixture
def video(raiz):
    return mp4(raiz / "origen.mp4")


def subir(contenido, nombre="puerta.mp4"):
    return cliente.post(f"/videos?nombre={nombre}", content=contenido)


def pipeline_simulado(comandos):
    def correr(comando, **opciones):
        comandos.append(comando)
        salida = Path(comando[comando.index("--salida") + 1])
        salida.write_text(json.dumps({"capacidad": 20, "carga_inicial": 0, "paradas": [{"nombre": "P", "inicio_s": 0}],
                                      "eventos": []}), encoding="utf-8")
        salida.with_suffix(".config.json").write_text(json.dumps({"pesos": "yolo11n.pt"}), encoding="utf-8")
        Path(comando[comando.index("--video-anotado") + 1]).write_bytes(b"webm")
        return subprocess.CompletedProcess(comando, 0, "0 eventos", "")
    return correr


def test_subida_valida_guarda_por_hash_sin_duplicar(raiz, video):
    respuesta = subir(video)
    assert respuesta.status_code == 201, respuesta.text
    info = respuesta.json()
    assert (info["ancho"], info["alto"], info["cuadros"], info["fps"]) == (128, 64, 50, 25)
    assert info["duracion_s"] == 2 and info["nombre_original"] == "puerta.mp4" and len(info["sha256"]) == 64
    assert "origen arriba a la izquierda" in info["sistema_de_coordenadas"] and "primer cuadro" in info["origen_temporal"]
    assert subir(video, "otro-nombre.mp4").json()["id"] == info["id"]
    assert [c.name for c in (raiz / "runs/videos").iterdir()] == [info["id"]]  # sin temporales
    assert cliente.get(f"/videos/{info['id']}").json() == info


@pytest.mark.parametrize("contenido, nombre, codigo", [
    (b"", "vacio.mp4", 422), (b"no es un video", "roto.mp4", 422), (b"x", "texto.txt", 415), (b"x", "sin-extension", 415),
])
def test_subidas_invalidas(raiz, contenido, nombre, codigo):
    assert subir(contenido, nombre).status_code == codigo
    assert not any((raiz / "runs/videos").glob("*")) if (raiz / "runs/videos").exists() else True


def test_limites_de_tamano_y_duracion(raiz, video, monkeypatch):
    monkeypatch.setattr(api, "MAX_BYTES", len(video) - 1)
    assert subir(video).status_code == 413
    monkeypatch.setattr(api, "MAX_BYTES", 10**9)
    monkeypatch.setattr(api, "MAX_DURACION_S", 1)
    respuesta = subir(video)
    assert respuesta.status_code == 413 and "máximo" in respuesta.json()["detail"]
    assert list((raiz / "runs/videos").iterdir()) == []


def test_vista_previa_sin_inferencia_y_geometria_invalida(raiz, video, monkeypatch):
    monkeypatch.setattr(api.subprocess, "run", lambda *a, **k: pytest.fail("la vista previa no ejecuta el modelo"))
    id_video = subir(video).json()["id"]
    parametros = "recorte=10,0,100,60&linea=0,30,99,30&interior=arriba&t=1"
    imagen = cliente.get(f"/videos/{id_video}/cuadro?{parametros}")
    assert imagen.status_code == 200 and imagen.headers["content-type"] == "image/jpeg"
    assert cv2.imdecode(np.frombuffer(imagen.content, np.uint8), cv2.IMREAD_COLOR).shape == (64, 128, 3)
    for malo, texto in [("recorte=100,0,100,60&linea=0,30,99,30", "entrar"),       # sale del cuadro
                        ("recorte=10,0,100,60&linea=0,30,150,30", "dentro"),       # línea fuera del recorte
                        ("recorte=10,0,100,60&linea=50,0,50,59", "paralela"),      # vertical con interior arriba
                        ("recorte=10,0,100,60&linea=0,30,5,30", "10 px")]:
        respuesta = cliente.get(f"/videos/{id_video}/cuadro?{malo}&interior=arriba")
        assert respuesta.status_code == 422 and texto in respuesta.json()["detail"], malo


def test_procesa_con_la_configuracion_de_la_api_y_no_repite(raiz, video, monkeypatch):
    comandos = []
    monkeypatch.setattr(api.subprocess, "run", pipeline_simulado(comandos))
    id_video = subir(video).json()["id"]
    respuesta = cliente.post(f"/videos/{id_video}/procesamientos", json={**GEOMETRIA, "parada": "Mi puerta"})
    assert respuesta.status_code == 201, respuesta.text
    cuerpo = respuesta.json()
    opciones = dict(zip(comandos[0][3::2], comandos[0][4::2]))
    assert opciones["--video"] == f"runs/videos/{id_video}/video.mp4"
    assert (opciones["--recorte"], opciones["--linea"], opciones["--interior"]) == ("10,0,100,60", "0,30,99,30", "arriba")
    assert "--inicio" not in opciones and "--fin" not in opciones and opciones["--parada"] == "Mi puerta"
    demo = dict(zip(api.argumentos_demo()[::2], api.argumentos_demo()[1::2]))
    for clave in ("--pesos", "--rastreador", "--conf", "--confirmacion", "--dispositivo"):
        assert opciones[clave] == demo[clave], clave
    assert opciones["--pesos"] == "yolo11n.pt" and opciones["--conf"] == "0.05"
    entrada = cuerpo["entrada"]
    assert entrada["video_sha256"] == cliente.get(f"/videos/{id_video}").json()["sha256"]
    assert entrada["geometria"] == GEOMETRIA and entrada["supresion_temporal"] is None

    assert cliente.get(f"/procesamientos?video={id_video}").json() == [cuerpo["id"]]
    assert cliente.get("/procesamientos?origen=demo").json() == []
    assert cliente.get("/procesamientos?origen=video").json() == [cuerpo["id"]]
    assert cliente.get(f"/procesamientos/{cuerpo['id']}/video").content == b"webm"

    repetido = cliente.post(f"/videos/{id_video}/procesamientos", json=GEOMETRIA)
    assert repetido.status_code == 409 and cuerpo["id"] in repetido.json()["detail"] and len(comandos) == 1
    otra = cliente.post(f"/videos/{id_video}/procesamientos", json={**GEOMETRIA, "linea": [0, 20, 99, 20]})
    assert otra.status_code == 201 and len(comandos) == 2


def test_un_procesamiento_a_la_vez(raiz, video, monkeypatch):
    monkeypatch.setattr(api.subprocess, "run", lambda *a, **k: pytest.fail("no debe ejecutar"))
    id_video = subir(video).json()["id"]
    assert api._procesando.acquire(blocking=False)
    try:
        assert cliente.post(f"/videos/{id_video}/procesamientos", json=GEOMETRIA).status_code == 409
        assert cliente.post("/procesamientos").status_code in (409, 503)  # la demo también espera su turno
    finally:
        api._procesando.release()


def test_procesar_valida_geometria_y_video(raiz, video):
    id_video = subir(video).json()["id"]
    malo = {**GEOMETRIA, "recorte": [0, 0, 500, 60]}
    assert cliente.post(f"/videos/{id_video}/procesamientos", json=malo).status_code == 422
    assert cliente.post("/videos/0123456789abcdef/procesamientos", json=GEOMETRIA).status_code == 404
    assert cliente.post("/videos/..%2F..%2Fapi/procesamientos", json=GEOMETRIA).status_code in (404, 422)
    assert not (raiz / "runs/panel").exists()


def test_repetir_para_demostracion_guarda_aparte_y_no_toca_la_primera(raiz, video, monkeypatch):
    comandos = []
    monkeypatch.setattr(api.subprocess, "run", pipeline_simulado(comandos))
    id_video = subir(video).json()["id"]
    primera = cliente.post(f"/videos/{id_video}/procesamientos", json=GEOMETRIA).json()
    carpeta = raiz / "runs/panel" / primera["id"]
    antes = {f.name: f.read_bytes() for f in carpeta.iterdir()}

    assert cliente.post(f"/videos/{id_video}/procesamientos", json=GEOMETRIA).status_code == 409  # sin pedirlo, no repite
    repetida = cliente.post(f"/videos/{id_video}/procesamientos", json={**GEOMETRIA, "repetir_para_demostracion": True})
    assert repetida.status_code == 201 and len(comandos) == 2
    cuerpo = repetida.json()
    assert cuerpo["id"] != primera["id"]
    assert cuerpo["entrada"]["proposito"] == "repeticion para demostracion" and cuerpo["entrada"]["repite_a"] == [primera["id"]]
    assert cuerpo["entrada"]["geometria"] == primera["entrada"]["geometria"]
    assert primera["entrada"]["proposito"] == "primera ejecucion"
    assert {f.name: f.read_bytes() for f in carpeta.iterdir()} == antes  # la primera queda intacta
    assert sorted(cliente.get(f"/procesamientos?video={id_video}").json()) == sorted([primera["id"], cuerpo["id"]])
