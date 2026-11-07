"""Propone cajas de personas en una cámara fija, para revisarlas antes de entrenar.

Resta el fondo de la grabación. Una sombra cambia el brillo pero casi no deja bordes, así que se
exigen bordes nuevos, una diferencia de brillo muy fuerte o algo casi negro donde el fondo no lo
es, como una cabeza sobre una alfombra oscura. El resultado no es una anotación: cada caja debe
revisarse en las hojas que genera este programa.

Se ejecuta desde la raíz: python -m vision.proponer_cajas --help
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import numpy as np

from vision.pipeline import guardar_json, leer_cuadros, leer_recorte

UMBRAL_BORDES = 60
UMBRAL_BRILLO = 80
UMBRAL_OSCURO = 55  # En el clip de oficina, una cabeza sobre la alfombra ronda 45-60 y casi toda sombra supera 60.
LADO_MINIMO = 30
AREA_MINIMA_PIEZA = 100
DISTANCIA_PIEZAS = 20
ABRIR = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
CERRAR = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))


def a_gris(imagen):
    return cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)


def calcular_fondo(grises):
    """Mediana de una muestra de cuadros: vale si cada píxel está libre la mayor parte del tiempo."""
    return np.median(np.stack(grises[::5]), axis=0).astype("uint8")


def bordes(gris):
    suave = cv2.GaussianBlur(gris.astype("float32"), (3, 3), 0)
    return cv2.magnitude(cv2.Sobel(suave, cv2.CV_32F, 1, 0, ksize=3), cv2.Sobel(suave, cv2.CV_32F, 0, 1, ksize=3))


def proponer_caja(gris, fondo, lado_minimo=LADO_MINIMO):
    """Devuelve [x1, y1, x2, y2] del mayor objeto nuevo, o None si no hay uno suficientemente grande."""
    bordes_nuevos = np.abs(bordes(gris) - bordes(fondo)) > UMBRAL_BORDES
    muy_distinto = np.abs(gris.astype("int16") - fondo.astype("int16")) > UMBRAL_BRILLO
    muy_oscuro = (gris < UMBRAL_OSCURO) & (fondo > UMBRAL_OSCURO + 20)
    mascara = (bordes_nuevos | muy_distinto | muy_oscuro).astype("uint8") * 255
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, ABRIR)
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, CERRAR)
    total, _, estadisticas, _ = cv2.connectedComponentsWithStats(mascara)
    if total < 2:
        return None
    piezas = sorted(
        ((int(area), [int(x), int(y), int(x + ancho), int(y + alto)])
         for x, y, ancho, alto, area in estadisticas[1:]),
        key=lambda pieza: -pieza[0],
    )
    caja = unir_piezas_cercanas(piezas)
    if caja[2] - caja[0] < lado_minimo or caja[3] - caja[1] < lado_minimo:
        return None
    return caja


def unir_piezas_cercanas(piezas):
    """Parte de la pieza mayor y le suma las cercanas: la cabeza y el torso suelen quedar separados.

    Por eso sirve para una persona a la vez: si dos pasan juntas, la caja debe corregirse a mano.
    """
    caja = list(piezas[0][1])
    pendientes = [pieza for area, pieza in piezas[1:] if area >= AREA_MINIMA_PIEZA]
    hubo_cambios = True
    while hubo_cambios:
        hubo_cambios = False
        for pieza in list(pendientes):
            separada = (pieza[0] - DISTANCIA_PIEZAS > caja[2] or pieza[2] + DISTANCIA_PIEZAS < caja[0]
                        or pieza[1] - DISTANCIA_PIEZAS > caja[3] or pieza[3] + DISTANCIA_PIEZAS < caja[1])
            if not separada:
                caja = [min(caja[0], pieza[0]), min(caja[1], pieza[1]), max(caja[2], pieza[2]), max(caja[3], pieza[3])]
                pendientes.remove(pieza)
                hubo_cambios = True
    return caja


def guardar_hojas(entradas, imagenes, carpeta, nombre="hoja", por_hoja=36, por_fila=6, escala=1.5):
    """Guarda hojas con cada cuadro numerado y su caja. Devuelve las rutas creadas."""
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    rutas = []
    for inicio in range(0, len(entradas), por_hoja):
        fotos = []
        for entrada in entradas[inicio:inicio + por_hoja]:
            foto = cv2.resize(imagenes[entrada["cuadro"]], None, fx=escala, fy=escala)
            if entrada["caja"]:
                x1, y1, x2, y2 = (int(valor * escala) for valor in entrada["caja"])
                cv2.rectangle(foto, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(foto, str(entrada["cuadro"]), (4, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            fotos.append(foto)
        while len(fotos) % por_fila:
            fotos.append(np.zeros_like(fotos[0]))
        filas = [np.hstack(fotos[i:i + por_fila]) for i in range(0, len(fotos), por_fila)]
        ruta = carpeta / f"{nombre}-{inicio // por_hoja + 1:02d}.png"
        cv2.imwrite(str(ruta), np.vstack(filas))
        rutas.append(ruta)
    return rutas


def main(argv=None):
    parser = argparse.ArgumentParser(description="Propone cajas de personas para revisarlas a mano.")
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--recorte", type=leer_recorte, help="X,Y,ANCHO,ALTO en píxeles del cuadro completo.")
    parser.add_argument("--paso", type=int, default=3, help="Toma uno de cada PASO cuadros.")
    parser.add_argument("--salida", type=Path, required=True, help="JSON con las propuestas.")
    parser.add_argument("--hojas", type=Path, help="Carpeta para las hojas de revisión.")
    args = parser.parse_args(argv)
    if args.paso < 1:
        parser.error("--paso debe ser al menos 1.")

    tiempos, imagenes = zip(*leer_cuadros(args.video, recorte=args.recorte))
    grises = [a_gris(imagen) for imagen in imagenes]
    fondo = calcular_fondo(grises)
    entradas = [
        {"cuadro": indice, "tiempo_s": round(tiempos[indice], 3), "caja": proponer_caja(grises[indice], fondo)}
        for indice in range(0, len(imagenes), args.paso)
    ]
    guardar_json(args.salida, {"video": str(args.video), "paso": args.paso, "entradas": entradas})
    con_caja = [entrada for entrada in entradas if entrada["caja"]]
    print(f"{len(entradas)} cuadros: {len(con_caja)} con caja y {len(entradas) - len(con_caja)} sin caja.")
    if args.hojas:
        rutas = guardar_hojas(con_caja, imagenes, args.hojas)
        print(f"{len(rutas)} hojas en {args.hojas}")


if __name__ == "__main__":
    main()
