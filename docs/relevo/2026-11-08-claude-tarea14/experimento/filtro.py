"""Tarea 14 · experimento NO incorporado a la entrega: filtro de cajas encimadas.

Mismo código que se probó dentro de vision/ (copias completas en cruces.con-filtro.py y pipeline.con-filtro.py),
aislado aquí para que el experimento se pueda repetir sin tocar el pipeline de producción.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from vision.cruces import Evento  # noqa: E402,F401
from vision.pipeline import punto_de_referencia  # noqa: E402


def superposicion(a, b) -> float:
    """Intersección de dos cajas xyxy dividida por el área de la menor: 1 si una está dentro de la otra."""
    ancho = min(a[2], b[2]) - max(a[0], b[0])
    alto = min(a[3], b[3]) - max(a[1], b[1])
    if ancho <= 0 or alto <= 0:
        return 0.0
    menor = min((a[2] - a[0]) * (a[3] - a[1]), (b[2] - b[0]) * (b[3] - b[1]))
    return ancho * alto / menor if menor > 0 else 0.0


class FiltroSuperpuestas:
    """Descarta el cruce de un track cuya caja está encimada (>= umbral) con la de otro track que ya contó
    el mismo sentido hace menos de `ventana_s`. Nunca filtra al propio track ni el sentido opuesto."""

    def __init__(self, umbral=0.6, ventana_s=1.0):
        self.umbral, self.ventana_s = umbral, ventana_s
        self._cajas, self._aceptados, self.descartados = {}, [], []

    def observar(self, observaciones):
        for track_id, caja in observaciones:
            self._cajas[track_id] = tuple(caja)

    def aceptar(self, evento, tiempo_s):
        caja = self._cajas[evento.track_id]
        for momento, otro, sentido in self._aceptados:
            if (sentido == evento.sentido and otro != evento.track_id and tiempo_s - momento <= self.ventana_s
                    and superposicion(caja, self._cajas[otro]) >= self.umbral):
                self.descartados.append({"tiempo_s": round(evento.tiempo_s, 3), "track_id": evento.track_id,
                                         "sentido": evento.sentido, "encimado_con": otro})
                return False
        self._aceptados.append((tiempo_s, evento.track_id, evento.sentido))
        return True


def procesar(cuadros, rastrear, contador, punto="centro", filtro=None):
    """vision.pipeline.procesar con el filtro: cajas chicas primero en cada cuadro."""
    total = 0
    for tiempo_s, imagen in cuadros:
        observaciones = rastrear(imagen)
        if filtro:
            filtro.observar(observaciones)
            observaciones = sorted(observaciones, key=lambda o: (o[1][2] - o[1][0]) * (o[1][3] - o[1][1]))
        for track_id, caja in observaciones:
            evento = contador.actualizar(track_id, *punto_de_referencia(caja, punto), tiempo_s)
            if evento and filtro and not filtro.aceptar(evento, tiempo_s):
                contador.eventos.remove(evento)
        total += 1
    return total
