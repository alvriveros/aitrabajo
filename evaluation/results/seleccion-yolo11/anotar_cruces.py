"""Anotador manual de cruces: mirás el video y marcás cada cruce con una tecla.

Uso, desde la raíz del worktree:
  python docs/relevo/2026-11-08-claude-tarea11/anotar_cruces.py --video data/raw/NUEVO.mp4 \
      --salida data/annotations/NUEVO-cruces.json (--linea-y 310 | --linea X1,Y1,X2,Y2) [--continuar]
Teclas:  espacio pausa/sigue · S subida · B bajada · Z deshace el último · A / D retrocede / avanza 2 s
         , / . un cuadro atrás / adelante (hacia atrás, hasta 4 s) · + / - velocidad · G guarda y sale · Q o Esc sale sin guardar

Tarea 12: corrige la navegación (`,` retrocedía dos cuadros; A/D se quedaban un cuadro cortos), conserva notas y
metadatos al continuar, no se adjudica «antes de ejecutar modelos» y nunca sobrescribe la referencia histórica de
la tarea 11. La versión con la que se anotó esa referencia está en tarea12/historico/.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import deque
from datetime import datetime
from pathlib import Path

import cv2

# referencia de la prueba final de tarea 11 (ejecución consumida): no se sobrescribe nunca
PROTEGIDAS = {"ad73d9d8f11feaf69696e58f042367de5bbdeedee9e3623a1fc52889262502f6"}
SALTO_S = 2


def abrir(video):
    captura = cv2.VideoCapture(str(video), cv2.CAP_FFMPEG)
    fps = captura.get(cv2.CAP_PROP_FPS)
    total = int(captura.get(cv2.CAP_PROP_FRAME_COUNT))
    if not captura.isOpened() or not fps or fps <= 0 or total <= 0:
        raise SystemExit(f"No se pudo abrir {video} o no informa FPS y cantidad de cuadros.")
    return captura, fps, total


class Navegador:
    """Lee el video solo hacia adelante y guarda los últimos cuadros para retroceder.

    No usa CAP_PROP_POS_FRAMES: en algunos MP4 (por ejemplo el de Kaggle) ese salto cae en otro cuadro.
    El tiempo de cada cuadro es su marca en el archivo (CAP_PROP_POS_MSEC), la misma base que usa vision.pipeline
    y el panel: segundos desde el primer cuadro del video.
    """

    def __init__(self, captura, fps, segundos_atras=4):
        self.captura = captura
        self.buffer = deque(maxlen=max(2, round(segundos_atras * fps)))  # (índice, tiempo_s, imagen)
        self.posicion = -1  # índice dentro del buffer
        if not self.avanzar(1):
            raise SystemExit("El video no tiene cuadros legibles.")

    @property
    def actual(self):
        indice, _, imagen = self.buffer[self.posicion]
        return indice, imagen

    @property
    def tiempo(self):
        return self.buffer[self.posicion][1]

    def avanzar(self, n):
        """Avanza n cuadros; devuelve False si llegó al final antes."""
        for _ in range(n):
            if self.posicion < len(self.buffer) - 1:
                self.posicion += 1
                continue
            ok, imagen = self.captura.read()
            if not ok:
                return False
            indice = self.buffer[-1][0] + 1 if self.buffer else 0
            self.buffer.append((indice, self.captura.get(cv2.CAP_PROP_POS_MSEC) / 1000, imagen))
            self.posicion = len(self.buffer) - 1
        return True

    def retroceder(self, n):
        """Retrocede hasta n cuadros, sin pasar del más viejo guardado."""
        self.posicion = max(0, self.posicion - n)


def navegar(navegador, tecla, fps):
    """Aplica una tecla de navegación; devuelve False si la tecla no navega."""
    salto = round(SALTO_S * fps)
    if tecla == ord("a"):
        navegador.retroceder(salto)
    elif tecla == ord(","):
        navegador.retroceder(1)
    elif tecla == ord("d"):
        navegador.avanzar(salto)
    elif tecla == ord("."):
        navegador.avanzar(1)
    else:
        return False
    return True


def sha(ruta):
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


def preparar_salida(salida, continuar):
    """Devuelve el documento a completar; rechaza sobrescrituras accidentales y la referencia protegida."""
    if not salida.exists():
        return {"notas": [], "eventos": []}
    if sha(salida) in PROTEGIDAS:
        raise SystemExit(f"{salida} es una referencia histórica protegida: usá otra --salida.")
    if not continuar:
        raise SystemExit(f"{salida} ya existe: usá --continuar para seguirla u otra --salida.")
    return json.loads(salida.read_text(encoding="utf-8"))


def guardar(salida, documento, eventos, video, linea, anotador):
    documento = dict(documento)
    documento.setdefault("capacidad", 60)
    documento.setdefault("carga_inicial", 0)
    documento.setdefault("paradas", [{"nombre": Path(video).stem, "inicio_s": 0}])
    documento.setdefault("anotado_por", f"{anotador}, a mano con anotar_cruces.py")
    documento.setdefault("criterio", f"Cruce de la línea {linea} (píxeles del cuadro completo) por el centro del torso; "
                                     "tiempo = segundos desde el primer cuadro del video.")
    documento["video_sha256"] = documento.get("video_sha256") or sha(video)
    documento.setdefault("sesiones", []).append(datetime.now().astimezone().isoformat(timespec="minutes"))
    documento["eventos"] = sorted(eventos, key=lambda e: e["tiempo_s"])
    for i, evento in enumerate(documento["eventos"], 1):
        evento["track_id"] = i
    salida.write_text(json.dumps(documento, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Guardado {salida}: {len(eventos)} cruces. Agregá en «notas» lo que haga falta aclarar.")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True, type=Path)
    parser.add_argument("--salida", required=True, type=Path)
    geometria = parser.add_mutually_exclusive_group(required=True)
    geometria.add_argument("--linea-y", type=int, help="Línea horizontal a esta altura del cuadro completo.")
    geometria.add_argument("--linea", help="X1,Y1,X2,Y2 en píxeles del CUADRO COMPLETO (el panel muestra estos valores).")
    parser.add_argument("--continuar", action="store_true", help="Seguir una anotación existente.")
    parser.add_argument("--anotador", default="Álvaro")
    args = parser.parse_args(argv)
    documento = preparar_salida(args.salida, args.continuar)
    if documento.get("video_sha256") and documento["video_sha256"] != sha(args.video):
        raise SystemExit("La anotación existente es de otro video.")
    captura, fps, _ = abrir(args.video)
    ancho = int(captura.get(cv2.CAP_PROP_FRAME_WIDTH))
    linea = (tuple(int(float(v)) for v in args.linea.split(",")) if args.linea
             else (0, args.linea_y, ancho - 1, args.linea_y))
    eventos = list(documento.get("eventos", []))
    navegador = Navegador(captura, fps)
    pausa, velocidad = False, 1.0
    while True:
        _, imagen = navegador.actual
        vista = imagen.copy()
        cv2.line(vista, linea[:2], linea[2:], (0, 0, 255), 1)
        subidas = sum(e["sentido"] == "subida" for e in eventos)
        texto = f"{navegador.tiempo:6.2f} s  x{velocidad:g}  subidas {subidas}  bajadas {len(eventos) - subidas}"
        cv2.putText(vista, texto + ("  [PAUSA]" if pausa else ""), (5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)
        cv2.imshow("anotar cruces (S subida, B bajada, G guarda)", vista)
        tecla = cv2.waitKey(0 if pausa else max(1, int(1000 / fps / velocidad))) & 0xFF
        if tecla in (ord("s"), ord("b")):
            eventos.append({"tiempo_s": round(navegador.tiempo, 2), "track_id": 0,
                            "sentido": "subida" if tecla == ord("s") else "bajada"})
        elif tecla == ord("z") and eventos:
            eventos.pop()
        elif tecla == ord(" "):
            pausa = not pausa
        elif tecla == ord("+"):
            velocidad = min(8.0, velocidad * 2)
        elif tecla == ord("-"):
            velocidad = max(0.25, velocidad / 2)
        elif tecla == ord("g"):
            guardar(args.salida, documento, eventos, args.video, ",".join(map(str, linea)), args.anotador)
            break
        elif tecla in (ord("q"), 27):
            break
        if not navegar(navegador, tecla, fps) and not pausa and not navegador.avanzar(1):
            pausa = True  # fin del video: queda en pausa en el último cuadro
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
