"""Convierte un tramo de video de una puerta en eventos de subida y bajada.

Se ejecuta desde la raíz del repositorio; el comando y sus dependencias están en vision/README.md.
OpenCV y Ultralytics se importan al usarlos para poder probar el resto sin instalarlos.
"""
from __future__ import annotations

import argparse
import json
import math
import platform
import shlex
import sys
import time
from dataclasses import asdict, dataclass
from importlib import metadata
from pathlib import Path

from vision.cruces import DIRECCIONES, ContadorCruces, FiltroSuperpuestas, Linea

SISTEMA_DE_COORDENADAS = "Píxeles: origen arriba a la izquierda, x hacia la derecha, y hacia abajo."
CLASE_PERSONA = 0  # Índice de "person" en COCO.
SEGUNDOS_DE_ROTULO = 1.5
COLORES = {None: (255, 255, 255), "subida": (80, 200, 80), "bajada": (60, 140, 255)}  # En BGR.


@dataclass(frozen=True)
class Recorte:
    x: int
    y: int
    ancho: int
    alto: int


def _numeros(texto, cantidad, formato):
    try:
        valores = [float(parte) for parte in texto.split(",")]
    except ValueError:
        valores = []
    if len(valores) != cantidad or not all(map(math.isfinite, valores)):
        raise argparse.ArgumentTypeError(f"Se esperaba {formato}: {texto}")
    return valores


def leer_recorte(texto):
    valores = _numeros(texto, 4, "X,Y,ANCHO,ALTO")
    if not all(valor.is_integer() for valor in valores):
        raise argparse.ArgumentTypeError(f"El recorte debe usar píxeles enteros: {texto}")
    x, y, ancho, alto = map(int, valores)
    if x < 0 or y < 0 or ancho <= 0 or alto <= 0:
        raise argparse.ArgumentTypeError(f"El recorte debe empezar dentro de la imagen y tener tamaño: {texto}")
    return Recorte(x, y, ancho, alto)


def leer_linea(texto):
    return tuple(_numeros(texto, 4, "X1,Y1,X2,Y2"))


def crear_parser():
    parser = argparse.ArgumentParser(description="Cuenta subidas y bajadas en un tramo de video.")
    parser.add_argument("--video", type=Path, required=True, help="Video local.")
    parser.add_argument("--inicio", type=float, default=0.0, help="Inicio del tramo, en segundos.")
    parser.add_argument("--fin", type=float, help="Fin del tramo, en segundos. Sin valor, hasta el final del video.")
    parser.add_argument("--recorte", type=leer_recorte, help="X,Y,ANCHO,ALTO en píxeles del cuadro completo.")
    parser.add_argument("--linea", type=leer_linea, required=True, help="X1,Y1,X2,Y2 en píxeles del recorte.")
    parser.add_argument("--interior", choices=sorted(DIRECCIONES), required=True,
                        help="Dirección del interior en la imagen: cruzar hacia ahí es una subida.")
    parser.add_argument("--salida", type=Path, required=True, help="JSON de predicciones.")
    parser.add_argument("--video-anotado", type=Path, help="MP4 con la línea, los IDs y el sentido de cada cruce.")
    parser.add_argument("--punto", choices=["centro", "pies"], default="centro",
                        help="Punto de la caja que decide de qué lado está la persona.")
    parser.add_argument("--margen", type=float, default=5.0, help="Banda en píxeles alrededor de la línea.")
    parser.add_argument("--confirmacion", type=int, default=3, help="Cuadros seguidos para confirmar un lado.")
    parser.add_argument("--pesos", default="yolo11n.pt", help="Pesos del detector. Ultralytics descarga los oficiales.")
    parser.add_argument("--rastreador", default="bytetrack.yaml", help="Configuración del rastreador.")
    parser.add_argument("--conf", type=float, help="Confianza mínima. Sin valor, la de Ultralytics para rastrear.")
    parser.add_argument("--dispositivo", help="cpu, mps o cuda:0. Sin valor, lo elige Ultralytics.")
    parser.add_argument("--filtro-superpuestas", type=float, metavar="UMBRAL",
                        help="Descarta el cruce de una caja encimada (intersección/área menor >= UMBRAL) con otra que "
                             "contó el mismo sentido en el último segundo. Sin valor, no filtra.")
    parser.add_argument("--capacidad", type=int, default=20)
    parser.add_argument("--carga-inicial", type=int, default=0)
    parser.add_argument("--parada", help="Nombre de la parada. Sin valor, el nombre del archivo de video.")
    return parser


def leer_argumentos(argv):
    parser = crear_parser()
    args = parser.parse_args(argv)
    if args.inicio < 0 or (args.fin is not None and args.fin <= args.inicio):
        parser.error("El tramo debe empezar en 0 o después, y --fin debe ser mayor que --inicio.")
    if args.capacidad <= 0 or args.carga_inicial < 0:
        parser.error("La capacidad debe ser positiva y la carga inicial no puede ser negativa.")
    if args.margen < 0 or args.confirmacion < 1:
        parser.error("El margen no puede ser negativo y la confirmación requiere al menos un cuadro.")
    if args.filtro_superpuestas is not None and not 0 < args.filtro_superpuestas <= 1:
        parser.error("--filtro-superpuestas debe estar entre 0 (excluido) y 1.")
    try:
        linea = Linea(*args.linea, interior=args.interior)
    except ValueError as error:
        parser.error(str(error))
    return args, linea


def punto_de_referencia(caja, punto):
    x1, y1, x2, y2 = caja
    return (x1 + x2) / 2, y2 if punto == "pies" else (y1 + y2) / 2


def procesar(cuadros, rastrear, contador, punto="centro", al_procesar=None, filtro=None):
    """Recorre pares (tiempo_s, imagen), actualiza el contador y devuelve cuántos cuadros procesó."""
    total = 0
    for tiempo_s, imagen in cuadros:
        observaciones = rastrear(imagen)
        if filtro:
            filtro.observar(observaciones)
            # Las cajas chicas primero: si en el mismo cuadro cruzan una persona y una caja que abarca a varias,
            # cuenta la persona y se descarta la caja grande.
            observaciones = sorted(observaciones, key=lambda o: (o[1][2] - o[1][0]) * (o[1][3] - o[1][1]))
        eventos = []
        for track_id, caja in observaciones:
            evento = contador.actualizar(track_id, *punto_de_referencia(caja, punto), tiempo_s)
            if evento and filtro and not filtro.aceptar(evento, tiempo_s):
                contador.eventos.remove(evento)
                evento = None
            if evento:
                eventos.append(evento)
        if al_procesar:
            al_procesar(tiempo_s, imagen, observaciones, eventos)
        total += 1
    return total


def construir_recorrido(eventos, capacidad, carga_inicial, parada):
    """Arma el JSON con el esquema de POST /ocupacion y de la referencia manual."""
    return {
        "capacidad": capacidad,
        "carga_inicial": carga_inicial,
        "paradas": [{"nombre": parada, "inicio_s": 0}],
        "eventos": [
            {"tiempo_s": round(evento.tiempo_s, 3), "track_id": int(evento.track_id), "sentido": evento.sentido}
            for evento in eventos
        ],
    }


def guardar_json(ruta, datos):
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ruta_de_configuracion(salida):
    return Path(salida).with_suffix(".config.json")


def entorno():
    datos = {"python": platform.python_version(), "plataforma": platform.platform(), "procesador": platform.processor()}
    for paquete in ("ultralytics", "torch", "opencv-python", "lap"):
        try:
            datos[paquete] = metadata.version(paquete)
        except metadata.PackageNotFoundError:
            datos[paquete] = None
    return datos


def ejecutar(args, linea, cuadros, rastrear, al_procesar=None, comando="", propiedades=None):
    """Recorre el tramo y guarda las predicciones junto con lo necesario para repetirlas."""
    contador = ContadorCruces(linea, margen_px=args.margen, confirmacion=args.confirmacion)
    filtro = FiltroSuperpuestas(args.filtro_superpuestas) if args.filtro_superpuestas is not None else None
    inicio = time.perf_counter()
    total = procesar(cuadros, rastrear, contador, args.punto, al_procesar, filtro)
    segundos = time.perf_counter() - inicio
    if not total:
        raise SystemExit("El tramo no tiene cuadros: no se escribió ninguna predicción.")

    recorrido = construir_recorrido(
        contador.eventos_ordenados(), args.capacidad, args.carga_inicial, args.parada or args.video.stem
    )
    guardar_json(args.salida, recorrido)
    guardar_json(ruta_de_configuracion(args.salida), {
        "comando": comando,
        "video": str(args.video),
        "propiedades_del_video": propiedades,
        "tramo_s": {"inicio": args.inicio, "fin": args.fin},
        "recorte": asdict(args.recorte) if args.recorte else None,
        "linea": asdict(linea),
        "sistema_de_coordenadas": SISTEMA_DE_COORDENADAS,
        "punto_del_cuerpo": args.punto,
        "margen_px": args.margen,
        "confirmacion_cuadros": args.confirmacion,
        "filtro_superpuestas": None if filtro is None else {
            "umbral": filtro.umbral, "ventana_s": filtro.ventana_s, "descartados": filtro.descartados},
        "pesos": args.pesos,
        "rastreador": args.rastreador,
        "conf": args.conf,
        "dispositivo": args.dispositivo,
        "medicion": {
            "cuadros": total,
            "segundos": round(segundos, 3),
            "fps_procesados": round(total / segundos, 2) if segundos else None,
            "con_video_anotado": args.video_anotado is not None,
        },
        "entorno": entorno(),
    })
    return recorrido


def propiedades_del_video(video):
    import cv2

    captura = cv2.VideoCapture(str(video), cv2.CAP_FFMPEG)
    if not captura.isOpened():
        raise SystemExit(f"No se pudo abrir el video: {video}")
    propiedades = {
        "fps": captura.get(cv2.CAP_PROP_FPS),
        "ancho": int(captura.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "alto": int(captura.get(cv2.CAP_PROP_FRAME_HEIGHT)),
    }
    captura.release()
    return propiedades


def recortar(imagen, recorte):
    if recorte is None:
        return imagen
    alto, ancho = imagen.shape[:2]
    if recorte.x + recorte.ancho > ancho or recorte.y + recorte.alto > alto:
        raise SystemExit(f"El recorte {recorte} no entra en un cuadro de {ancho}x{alto}.")
    return imagen[recorte.y:recorte.y + recorte.alto, recorte.x:recorte.x + recorte.ancho]


def leer_cuadros(video, inicio_s=0.0, fin_s=None, recorte=None):
    """Entrega (segundos desde el inicio del tramo, imagen recortada) según las marcas del video."""
    import cv2

    captura = cv2.VideoCapture(str(video), cv2.CAP_FFMPEG)
    if not captura.isOpened():
        raise SystemExit(f"No se pudo abrir el video: {video}")
    try:
        while captura.grab():
            tiempo = captura.get(cv2.CAP_PROP_POS_MSEC) / 1000
            if tiempo < inicio_s:
                continue
            if fin_s is not None and tiempo >= fin_s:
                break
            leido, imagen = captura.retrieve()
            if not leido:
                break
            yield tiempo - inicio_s, recortar(imagen, recorte)
    finally:
        captura.release()


def crear_rastreador(pesos, rastreador="bytetrack.yaml", conf=None, dispositivo=None):
    """Devuelve una función que recibe una imagen y entrega pares (track_id, caja xyxy) de personas."""
    from ultralytics import YOLO

    modelo = YOLO(pesos)
    opciones = {"persist": True, "tracker": rastreador, "classes": [CLASE_PERSONA], "verbose": False}
    if conf is not None:
        opciones["conf"] = conf
    if dispositivo:
        opciones["device"] = dispositivo

    def rastrear(imagen):
        cajas = modelo.track(imagen, **opciones)[0].boxes
        if cajas is None or cajas.id is None:
            return []
        return list(zip(cajas.id.int().tolist(), cajas.xyxy.tolist()))

    return rastrear


class VideoAnotado:
    """Guarda cada cuadro con la línea, los tracks y los cruces para revisar discrepancias."""

    def __init__(self, destino, linea, fps, punto):
        self.destino = Path(destino)
        self.linea = linea
        self.fps = fps
        self.punto = punto
        self.subidas = 0
        self.bajadas = 0
        self._rotulos = {}
        self._escritor = None

    def __call__(self, tiempo_s, imagen, observaciones, eventos):
        import cv2

        for evento in eventos:
            self.subidas += evento.sentido == "subida"
            self.bajadas += evento.sentido == "bajada"
            self._rotulos[evento.track_id] = (evento.sentido, tiempo_s + SEGUNDOS_DE_ROTULO)

        lienzo = imagen.copy()
        extremos = (int(self.linea.x1), int(self.linea.y1)), (int(self.linea.x2), int(self.linea.y2))
        cv2.line(lienzo, *extremos, (0, 255, 255), 2)
        for track_id, caja in observaciones:
            x1, y1, x2, y2 = map(int, caja)
            sentido, hasta = self._rotulos.get(track_id, (None, 0.0))
            sentido = sentido if tiempo_s <= hasta else None
            color = COLORES[sentido]
            punto = tuple(map(int, punto_de_referencia(caja, self.punto)))
            cv2.rectangle(lienzo, (x1, y1), (x2, y2), color, 2)
            cv2.circle(lienzo, punto, 4, color, -1)
            rotulo = f"ID {track_id} {sentido}" if sentido else f"ID {track_id}"
            cv2.putText(lienzo, rotulo, (x1, max(y1 - 6, 14)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        resumen = f"t={tiempo_s:.2f}s subidas={self.subidas} bajadas={self.bajadas}"
        cv2.putText(lienzo, resumen, (8, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        if self._escritor is None:
            self.destino.parent.mkdir(parents=True, exist_ok=True)
            alto, ancho = lienzo.shape[:2]
            # Los navegadores no reproducen mp4v; el panel pide .webm (VP8).
            formato = cv2.VideoWriter_fourcc(*("VP80" if self.destino.suffix == ".webm" else "mp4v"))
            self._escritor = cv2.VideoWriter(str(self.destino), formato, self.fps, (ancho, alto))
            if not self._escritor.isOpened():
                raise SystemExit(f"No se pudo crear el video anotado: {self.destino}")
        self._escritor.write(lienzo)

    def cerrar(self):
        if self._escritor is not None:
            self._escritor.release()


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    args, linea = leer_argumentos(argv)
    if not args.video.is_file():
        raise SystemExit(f"No existe el video: {args.video}")

    propiedades = propiedades_del_video(args.video)
    rastrear = crear_rastreador(args.pesos, args.rastreador, args.conf, args.dispositivo)
    anotador = VideoAnotado(args.video_anotado, linea, propiedades["fps"], args.punto) if args.video_anotado else None
    comando = shlex.join(["python", "-m", "vision.pipeline", *argv])
    cuadros = leer_cuadros(args.video, args.inicio, args.fin, args.recorte)
    try:
        recorrido = ejecutar(args, linea, cuadros, rastrear, anotador, comando, propiedades)
    finally:
        if anotador:
            anotador.cerrar()

    eventos = recorrido["eventos"]
    subidas = sum(evento["sentido"] == "subida" for evento in eventos)
    print(f"{len(eventos)} eventos: {subidas} subidas y {len(eventos) - subidas} bajadas.")
    print(f"Predicciones: {args.salida}")
    print(f"Configuración: {ruta_de_configuracion(args.salida)}")
    if args.video_anotado:
        print(f"Video anotado: {args.video_anotado}")


if __name__ == "__main__":
    main()
