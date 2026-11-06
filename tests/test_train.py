import json

import pytest

cv2 = pytest.importorskip("cv2")
numpy = pytest.importorskip("numpy")

from vision.proponer_cajas import calcular_fondo, guardar_hojas, proponer_caja, unir_piezas_cercanas  # noqa: E402
from vision.revisar_cajas import main as revisar_cajas  # noqa: E402
from vision.train import armar_dataset, caja_a_yolo, huella  # noqa: E402


def crear_video(ruta, cuadros=12, fps=10, ancho=120, alto=80):
    escritor = cv2.VideoWriter(str(ruta), cv2.VideoWriter_fourcc(*"mp4v"), fps, (ancho, alto))
    for _ in range(cuadros):
        escritor.write(numpy.full((alto, ancho, 3), 120, dtype="uint8"))
    escritor.release()
    return ruta


def anotacion(cuadros):
    return {"recorte": {"x": 0, "y": 0, "ancho": 100, "alto": 60}, "clase": "person", "cuadros": cuadros}


def test_caja_a_yolo_normaliza_centro_y_tamano():
    assert caja_a_yolo([25, 10, 75, 30], 100, 40) == "0 0.500000 0.500000 0.500000 0.500000"


def test_caja_a_yolo_rechaza_cajas_invalidas():
    for caja in ([0, 0, 101, 40], [-1, 0, 50, 40], [50, 0, 50, 40], [60, 0, 50, 40]):
        with pytest.raises(ValueError):
            caja_a_yolo(caja, 100, 40)


def test_huella_es_el_sha256_del_archivo(tmp_path):
    ruta = tmp_path / "archivo"
    ruta.write_bytes(b"abc")
    assert huella(ruta) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_armar_dataset_separa_particiones_y_deja_fuera_el_ensayo(tmp_path):
    video = crear_video(tmp_path / "clip.mp4")
    cuadros = [
        {"cuadro": 2, "particion": "entrenamiento", "caja": [10, 10, 60, 50]},
        {"cuadro": 4, "particion": "entrenamiento", "caja": None},
        {"cuadro": 6, "particion": "reserva", "caja": [0, 0, 100, 60]},
        {"cuadro": 8, "particion": "ensayo", "caja": [0, 0, 50, 30]},
    ]
    yaml, conteo = armar_dataset(anotacion(cuadros), video, tmp_path / "dataset")

    assert conteo == {"entrenamiento": {"con_persona": 1, "sin_persona": 1}, "reserva": {"con_persona": 1, "sin_persona": 0}}
    carpeta = tmp_path / "dataset"
    assert sorted(p.name for p in (carpeta / "images/train").iterdir()) == ["cuadro-00002.png", "cuadro-00004.png"]
    assert [p.name for p in (carpeta / "images/val").iterdir()] == ["cuadro-00006.png"]
    assert (carpeta / "labels/train/cuadro-00002.txt").read_text() == "0 0.350000 0.500000 0.500000 0.666667\n"
    assert (carpeta / "labels/train/cuadro-00004.txt").read_text() == ""
    assert (carpeta / "labels/val/cuadro-00006.txt").read_text() == "0 0.500000 0.500000 1.000000 1.000000\n"
    assert cv2.imread(str(carpeta / "images/val/cuadro-00006.png")).shape == (60, 100, 3)
    texto = yaml.read_text(encoding="utf-8")
    assert f"path: {json.dumps(str(carpeta.resolve()))}" in texto
    assert "train: images/train" in texto and "val: images/val" in texto and "0: person" in texto


def test_armar_dataset_avisa_si_falta_un_cuadro_anotado(tmp_path):
    video = crear_video(tmp_path / "clip.mp4", cuadros=5)
    with pytest.raises(SystemExit, match="99"):
        armar_dataset(anotacion([{"cuadro": 99, "particion": "reserva", "caja": None}]), video, tmp_path / "dataset")


def escena():
    """Fondo con franja oscura y ruido, como referencia sin personas."""
    generador = numpy.random.default_rng(0)
    fondo = numpy.full((176, 222), 150, dtype="uint8")
    fondo[80:95, :] = 70
    return fondo, generador


def con_persona(fondo, generador, x=80, y=40, ancho=50, alto=70):
    imagen = fondo.copy()
    textura = generador.integers(20, 220, size=(alto // 6 + 1, ancho // 6 + 1), dtype="uint8")
    imagen[y:y + alto, x:x + ancho] = cv2.resize(textura, (ancho, alto), interpolation=cv2.INTER_NEAREST)
    return imagen


def con_sombra(fondo, x=110, y=60):
    """Sombra suave: oscurece sin dejar bordes definidos."""
    malla_y, malla_x = numpy.mgrid[0:fondo.shape[0], 0:fondo.shape[1]]
    factor = 1 - 0.4 * numpy.exp(-(((malla_x - x) / 40) ** 2 + ((malla_y - y) / 40) ** 2))
    return (fondo * factor).astype("uint8")


def test_calcular_fondo_ignora_a_quien_pasa_una_minoria_del_tiempo():
    fondo, generador = escena()
    grises = [fondo.copy() for _ in range(40)]
    for indice in (0, 20):  # Dos de los ocho cuadros que toma la muestra.
        grises[indice] = con_persona(fondo, generador)
    assert numpy.array_equal(calcular_fondo(grises), fondo)


def test_proponer_caja_encuentra_a_la_persona():
    fondo, generador = escena()
    caja = proponer_caja(con_persona(fondo, generador), fondo)
    assert caja is not None
    x1, y1, x2, y2 = caja
    assert abs(x1 - 80) <= 6 and abs(y1 - 40) <= 6 and abs(x2 - 130) <= 6 and abs(y2 - 110) <= 6


def test_proponer_caja_ignora_una_sombra_suave():
    fondo, _ = escena()
    assert proponer_caja(con_sombra(fondo), fondo) is None


def test_proponer_caja_sin_cambios_no_propone_nada():
    fondo, _ = escena()
    assert proponer_caja(fondo.copy(), fondo) is None


def test_proponer_caja_descarta_objetos_diminutos():
    fondo, generador = escena()
    assert proponer_caja(con_persona(fondo, generador, ancho=14, alto=14), fondo, lado_minimo=60) is None


def test_unir_piezas_cercanas_suma_solo_lo_cercano():
    piezas = [(900, [50, 50, 90, 90]), (300, [55, 100, 85, 130]), (300, [180, 10, 210, 40]), (50, [52, 40, 60, 48])]
    assert unir_piezas_cercanas(piezas) == [50, 50, 90, 130]


def test_unir_piezas_cercanas_encadena_piezas():
    piezas = [(900, [50, 50, 90, 90]), (300, [55, 100, 85, 130]), (300, [55, 140, 85, 170])]
    assert unir_piezas_cercanas(piezas) == [50, 50, 90, 170]


def test_revisar_cajas_genera_hojas_con_y_sin_persona(tmp_path, capsys):
    video = crear_video(tmp_path / "clip.mp4")
    datos = {**anotacion([{"cuadro": 2, "caja": [10, 10, 60, 50]}, {"cuadro": 4, "caja": None}]), "video": str(video)}
    ruta = tmp_path / "cajas.json"
    ruta.write_text(json.dumps(datos), encoding="utf-8")

    revisar_cajas(["--anotaciones", str(ruta), "--hojas", str(tmp_path / "hojas")])

    assert sorted(p.name for p in (tmp_path / "hojas").iterdir()) == ["con-persona-01.png", "sin-persona-01.png"]
    assert "1 cuadros con persona y 1 sin persona" in capsys.readouterr().out


def test_guardar_hojas_arma_una_hoja_con_las_dimensiones_esperadas(tmp_path):
    imagenes = [numpy.zeros((40, 60, 3), dtype="uint8") for _ in range(5)]
    entradas = [{"cuadro": 0, "caja": [5, 5, 30, 30]}, {"cuadro": 1, "caja": None}, {"cuadro": 2, "caja": None},
                {"cuadro": 3, "caja": None}]
    rutas = guardar_hojas(entradas, imagenes, tmp_path, por_hoja=3, por_fila=2, escala=1.0)
    assert [ruta.name for ruta in rutas] == ["hoja-01.png", "hoja-02.png"]
    assert cv2.imread(str(rutas[0])).shape == (80, 120, 3)
    assert cv2.imread(str(rutas[1])).shape == (40, 120, 3)
