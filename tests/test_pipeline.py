import argparse
import json
from pathlib import Path

import pytest

from vision.cruces import ContadorCruces, Evento, Linea
from vision.pipeline import (
    Recorte,
    VideoAnotado,
    construir_recorrido,
    ejecutar,
    leer_argumentos,
    leer_cuadros,
    leer_linea,
    leer_recorte,
    procesar,
    propiedades_del_video,
    punto_de_referencia,
    recortar,
    ruta_de_configuracion,
)

MANUAL = json.loads((Path(__file__).parents[1] / "docs/demo/oficina-00-06-manual.json").read_text(encoding="utf-8"))
ENTRADAS = ["--video", "data/raw/clip.mp4", "--linea", "0,100,200,100", "--interior", "arriba"]


def argumentos(salida="salida.json", *extra):
    return leer_argumentos([*ENTRADAS, "--salida", str(salida), *extra])


def caja_centrada_en(y):
    return (90, y - 20, 110, y + 20)


def altura_en_el_ensayo(t):
    """Persona simulada que pasa la línea (y = 100) cerca de los 2 s y vuelve cerca de los 4 s."""
    if t < 1.5:
        return 130
    if t < 2.5:
        return 130 - 60 * (t - 1.5)
    if t < 3.5:
        return 70
    if t < 4.5:
        return 70 + 60 * (t - 3.5)
    return 130


def ensayo_simulado():
    """Devuelve 6 s a 30 cuadros por segundo; cada imagen es su propio instante."""
    cuadros = [(indice / 30, indice / 30) for indice in range(180)]
    return cuadros, lambda t: [(7, caja_centrada_en(altura_en_el_ensayo(t)))]


def test_leer_recorte_valida_el_formato():
    assert leer_recorte("10,20,300,400") == Recorte(10, 20, 300, 400)
    for invalido in ["10,20,300", "a,b,c,d", "10,20,0,400", "-1,0,10,10", "1.5,0,10,10", "nan,0,10,10"]:
        with pytest.raises(argparse.ArgumentTypeError):
            leer_recorte(invalido)


def test_leer_linea_valida_el_formato():
    assert leer_linea("0,100.5,200,100") == (0, 100.5, 200, 100)
    for invalido in ["0,100,200", "0,100,200,x", "0,100,200,inf"]:
        with pytest.raises(argparse.ArgumentTypeError):
            leer_linea(invalido)


def test_argumentos_validos_arman_la_linea():
    args, linea = argumentos("salida.json", "--recorte", "640,0,640,360", "--inicio", "0", "--fin", "6")
    assert linea == Linea(0, 100, 200, 100, interior="arriba")
    assert args.recorte == Recorte(640, 0, 640, 360)
    assert (args.inicio, args.fin) == (0, 6)


def test_argumentos_invalidos_se_rechazan():
    for extra in (
        ["--inicio", "5", "--fin", "5"],
        ["--inicio", "-1"],
        ["--capacidad", "0"],
        ["--carga-inicial", "-1"],
        ["--margen", "-1"],
        ["--confirmacion", "0"],
    ):
        with pytest.raises(SystemExit):
            argumentos("salida.json", *extra)


def test_linea_paralela_al_interior_se_rechaza():
    with pytest.raises(SystemExit):
        leer_argumentos(["--video", "c.mp4", "--linea", "100,0,100,200", "--interior", "arriba", "--salida", "s.json"])


def test_punto_de_referencia():
    assert punto_de_referencia((10, 20, 30, 60), "centro") == (20, 40)
    assert punto_de_referencia((10, 20, 30, 60), "pies") == (20, 60)


def test_procesar_usa_el_punto_del_cuerpo_elegido():
    cuadros = [(indice / 10, 140 - 5 * indice) for indice in range(21)]
    linea = Linea(0, 100, 200, 100, interior="arriba")
    tiempos = {}
    for punto in ("centro", "pies"):
        contador = ContadorCruces(linea, margen_px=5, confirmacion=3)
        assert procesar(cuadros, lambda y: [(1, caja_centrada_en(y))], contador, punto) == 21
        tiempos[punto] = [evento.tiempo_s for evento in contador.eventos]
    assert tiempos == {"centro": [0.9], "pies": [1.3]}


def test_procesar_avisa_cada_cuadro_con_sus_eventos():
    cuadros, rastrear = ensayo_simulado()
    linea = Linea(0, 100, 200, 100, interior="arriba")
    llamadas = []
    procesar(cuadros, rastrear, ContadorCruces(linea), "centro", lambda *datos: llamadas.append(datos))
    assert len(llamadas) == len(cuadros)
    assert [evento.sentido for *_, eventos in llamadas for evento in eventos] == ["subida", "bajada"]


def test_recortar_respeta_los_limites_del_cuadro():
    numpy = pytest.importorskip("numpy")
    imagen = numpy.zeros((720, 1280, 3), dtype="uint8")
    assert recortar(imagen, Recorte(640, 0, 640, 360)).shape == (360, 640, 3)
    assert recortar(imagen, None) is imagen
    with pytest.raises(SystemExit):
        recortar(imagen, Recorte(640, 0, 641, 360))


def test_recorrido_redondea_tiempos_y_conserva_el_id_entero():
    recorrido = construir_recorrido([Evento(2.033333, 7, "subida")], 20, 0, "Puerta")
    assert recorrido["eventos"] == [{"tiempo_s": 2.033, "track_id": 7, "sentido": "subida"}]


def test_prediccion_tiene_el_esquema_de_la_referencia_manual(tmp_path):
    salida = tmp_path / "prediccion.json"
    args, linea = argumentos(salida)
    ejecutar(args, linea, *ensayo_simulado())
    prediccion = json.loads(salida.read_text(encoding="utf-8"))
    assert set(prediccion) == set(MANUAL)
    assert set(prediccion["paradas"][0]) == set(MANUAL["paradas"][0])
    assert set(prediccion["eventos"][0]) == set(MANUAL["eventos"][0])


def test_ensayo_simulado_pasa_por_la_api_y_sigue_la_referencia_manual(tmp_path):
    # La trayectoria es simulada: esto comprueba el contrato, no el desempeño sobre el clip real.
    TestClient = pytest.importorskip("fastapi.testclient").TestClient
    from api.main import app

    salida = tmp_path / "prediccion.json"
    args, linea = argumentos(salida)
    ejecutar(args, linea, *ensayo_simulado())
    recorrido = json.loads(salida.read_text(encoding="utf-8"))

    assert [evento["sentido"] for evento in recorrido["eventos"]] == [evento["sentido"] for evento in MANUAL["eventos"]]
    for predicho, manual in zip(recorrido["eventos"], MANUAL["eventos"]):
        assert abs(predicho["tiempo_s"] - manual["tiempo_s"]) < 0.1

    cliente = TestClient(app)

    def fila(eventos):
        respuesta = cliente.post("/ocupacion", json={**recorrido, "eventos": eventos})
        assert respuesta.status_code == 200, respuesta.text
        return respuesta.json()["paradas"][0]

    tras_la_subida = fila(recorrido["eventos"][:1])
    assert (tras_la_subida["pasajeros"], tras_la_subida["ocupacion_pct"]) == (1, 5.0)
    final = fila(recorrido["eventos"])
    assert (final["subidas"], final["bajadas"], final["pasajeros"], final["ocupacion_pct"]) == (1, 1, 0, 0.0)


def test_configuracion_permite_repetir_la_ejecucion(tmp_path):
    salida = tmp_path / "resultados" / "prediccion.json"
    args, linea = argumentos(salida, "--recorte", "640,0,640,360", "--inicio", "0", "--fin", "6")
    ejecutar(args, linea, *ensayo_simulado(), comando="python -m vision.pipeline ...")
    configuracion = json.loads(ruta_de_configuracion(salida).read_text(encoding="utf-8"))
    assert configuracion["comando"] == "python -m vision.pipeline ..."
    assert configuracion["recorte"] == {"x": 640, "y": 0, "ancho": 640, "alto": 360}
    assert configuracion["linea"] == {"x1": 0, "y1": 100, "x2": 200, "y2": 100, "interior": "arriba"}
    assert configuracion["tramo_s"] == {"inicio": 0, "fin": 6}
    assert configuracion["sistema_de_coordenadas"]
    assert configuracion["medicion"]["cuadros"] == 180


def test_sin_cruces_igual_se_exportan_las_predicciones(tmp_path):
    salida = tmp_path / "prediccion.json"
    args, linea = argumentos(salida)
    ejecutar(args, linea, [(0.0, None), (0.1, None)], lambda imagen: [])
    assert json.loads(salida.read_text(encoding="utf-8"))["eventos"] == []


def test_tramo_sin_cuadros_no_escribe_una_prediccion(tmp_path):
    salida = tmp_path / "prediccion.json"
    args, linea = argumentos(salida)
    with pytest.raises(SystemExit):
        ejecutar(args, linea, [], lambda imagen: [])
    assert not salida.exists()


def video_de_prueba(ruta, cuadros=30, fps=10, ancho=320, alto=240):
    """Crea un video cuyo brillo delata el número de cada cuadro. Requiere las dependencias de visión."""
    cv2 = pytest.importorskip("cv2")
    numpy = pytest.importorskip("numpy")
    escritor = cv2.VideoWriter(str(ruta), cv2.VideoWriter_fourcc(*"mp4v"), fps, (ancho, alto))
    for indice in range(cuadros):
        escritor.write(numpy.full((alto, ancho, 3), indice * 8, dtype="uint8"))
    escritor.release()
    return ruta


def test_leer_cuadros_respeta_tramo_recorte_y_marcas_del_video(tmp_path):
    ruta = video_de_prueba(tmp_path / "clip.mp4")
    assert propiedades_del_video(ruta) == {"fps": 10, "ancho": 320, "alto": 240}

    cuadros = list(leer_cuadros(ruta, inicio_s=1.0, fin_s=2.0, recorte=Recorte(160, 0, 160, 120)))

    assert [round(tiempo, 3) for tiempo, _ in cuadros] == [indice / 10 for indice in range(10)]
    assert all(imagen.shape == (120, 160, 3) for _, imagen in cuadros)
    assert abs(cuadros[0][1].mean() - 80) < 8  # El tramo empieza en el cuadro 10, de brillo 80.


def test_leer_cuadros_sin_tramo_entrega_todo_el_video(tmp_path):
    cuadros = list(leer_cuadros(video_de_prueba(tmp_path / "clip.mp4")))
    assert len(cuadros) == 30
    assert cuadros[0][0] == 0


def test_tramo_fuera_del_video_no_entrega_cuadros(tmp_path):
    assert list(leer_cuadros(video_de_prueba(tmp_path / "clip.mp4"), inicio_s=100)) == []


def test_video_anotado_dibuja_la_linea_y_no_altera_la_imagen_original(tmp_path):
    cv2 = pytest.importorskip("cv2")
    numpy = pytest.importorskip("numpy")
    destino = tmp_path / "anotado" / "clip.mp4"
    anotador = VideoAnotado(destino, Linea(0, 60, 160, 60, interior="arriba"), fps=10, punto="centro")
    imagen = numpy.zeros((120, 160, 3), dtype="uint8")
    for indice in range(5):
        eventos = [Evento(indice / 10, 3, "subida")] if indice == 2 else []
        anotador(indice / 10, imagen, [(3, (40, 20, 80, 100))], eventos)
    anotador.cerrar()

    assert not imagen.any()
    assert (anotador.subidas, anotador.bajadas) == (1, 0)

    captura = cv2.VideoCapture(str(destino))
    leidos = []
    while True:
        leido, cuadro = captura.read()
        if not leido:
            break
        leidos.append(cuadro)
    captura.release()
    assert len(leidos) == 5
    assert leidos[0].shape == (120, 160, 3)
    assert leidos[0][60].mean() > leidos[0][110].mean() + 50  # La fila de la línea frente a una vacía.
