"""Regla de conteo: de la posición de cada persona a eventos de subida y bajada.

No depende del detector ni del rastreador: recibe por cada track un punto del cuerpo
y el tiempo de su fotograma, así que se puede comprobar con trayectorias escritas a mano.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import hypot
from typing import Optional

DIRECCIONES = {"arriba": (0, -1), "abajo": (0, 1), "izquierda": (-1, 0), "derecha": (1, 0)}


@dataclass(frozen=True)
class Evento:
    tiempo_s: float
    track_id: int
    sentido: str


@dataclass(frozen=True)
class Linea:
    """Línea de conteo en píxeles del recorte: origen arriba a la izquierda, y hacia abajo.

    `interior` es la dirección en la que queda el interior del bus; cruzar hacia ahí es una
    subida. Se trata como una recta infinita porque se traza de lado a lado del recorte.
    """

    x1: float
    y1: float
    x2: float
    y2: float
    interior: str

    def __post_init__(self):
        if self.interior not in DIRECCIONES:
            raise ValueError(f"Interior desconocido: {self.interior}. Opciones: {', '.join(DIRECCIONES)}.")
        if self._producto_con_interior() == 0:
            raise ValueError("La línea debe tener largo y no puede ser paralela a la dirección del interior.")

    def _producto_con_interior(self) -> float:
        ix, iy = DIRECCIONES[self.interior]
        return (self.x2 - self.x1) * iy - (self.y2 - self.y1) * ix

    def distancia(self, x: float, y: float) -> float:
        """Distancia perpendicular a la línea: positiva hacia el interior, negativa hacia afuera."""
        dx, dy = self.x2 - self.x1, self.y2 - self.y1
        producto = dx * (y - self.y1) - dy * (x - self.x1)
        return (1 if self._producto_con_interior() > 0 else -1) * producto / hypot(dx, dy)


@dataclass
class _EstadoTrack:
    lado_confirmado: int = 0  # +1 interior, -1 exterior, 0 todavía sin confirmar.
    candidato: int = 0
    racha: int = 0
    signo: int = 0
    tiempo_paso: float = 0.0


class ContadorCruces:
    """Emite un evento cada vez que un track pasa de un lado confirmado al otro.

    Un lado se confirma con `confirmacion` cuadros seguidos a más de `margen_px` de la línea.
    Dentro de ese margen el estado no cambia, así que temblar sobre la línea no cuenta. El
    primer lado confirmado de un track tampoco: aparecer junto a la línea no es cruzarla.
    """

    def __init__(self, linea: Linea, margen_px: float = 5.0, confirmacion: int = 3):
        if margen_px < 0 or confirmacion < 1:
            raise ValueError("El margen no puede ser negativo y la confirmación requiere al menos un cuadro.")
        self.linea = linea
        self.margen_px = margen_px
        self.confirmacion = confirmacion
        self.eventos: list[Evento] = []
        self._tracks: dict[int, _EstadoTrack] = {}

    def actualizar(self, track_id: int, x: float, y: float, tiempo_s: float) -> Optional[Evento]:
        """Registra la posición de un track en un cuadro y devuelve el evento si confirmó un cruce."""
        estado = self._tracks.setdefault(track_id, _EstadoTrack())
        distancia = self.linea.distancia(x, y)

        # El evento lleva el instante en que el punto pasó la línea, no el de la confirmación.
        signo = (distancia > 0) - (distancia < 0)
        if signo and signo != estado.signo:
            estado.signo, estado.tiempo_paso = signo, tiempo_s

        if abs(distancia) <= self.margen_px:
            estado.candidato, estado.racha = 0, 0
            return None
        estado.racha = estado.racha + 1 if signo == estado.candidato else 1
        estado.candidato = signo
        if estado.racha < self.confirmacion or signo == estado.lado_confirmado:
            return None

        anterior, estado.lado_confirmado = estado.lado_confirmado, signo
        if not anterior:
            return None
        evento = Evento(estado.tiempo_paso, track_id, "subida" if signo > 0 else "bajada")
        self.eventos.append(evento)
        return evento

    def eventos_ordenados(self) -> list[Evento]:
        return sorted(self.eventos, key=lambda evento: (evento.tiempo_s, evento.track_id))


def superposicion(a, b) -> float:
    """Intersección de dos cajas xyxy dividida por el área de la menor: 1 si una está dentro de la otra."""
    ancho = min(a[2], b[2]) - max(a[0], b[0])
    alto = min(a[3], b[3]) - max(a[1], b[1])
    if ancho <= 0 or alto <= 0:
        return 0.0
    menor = min((a[2] - a[0]) * (a[3] - a[1]), (b[2] - b[0]) * (b[3] - b[1]))
    return ancho * alto / menor if menor > 0 else 0.0


class FiltroSuperpuestas:
    """Descarta el cruce de un track cuya caja está casi encimada con la de otro track que ya contó un cruce
    en el mismo sentido hace menos de `ventana_s`.

    Corrige un fallo observado (tarea 14): con confianza baja, el detector pone dos o tres cajas sobre la misma
    persona (una parcial, una entera, a veces una que abarca a dos) y cada una cruza la línea con su propio ID.
    No es una supresión temporal global: dos personas que cruzan a la vez sin cajas encimadas cuentan las dos,
    y una misma persona puede cruzar y volver (su propio track nunca se filtra, ni el sentido opuesto).
    """

    def __init__(self, umbral: float = 0.6, ventana_s: float = 1.0):
        self.umbral = umbral
        self.ventana_s = ventana_s
        self._cajas: dict[int, tuple] = {}
        self._aceptados: list[tuple[float, int, str]] = []
        self.descartados: list[dict] = []

    def observar(self, observaciones) -> None:
        """Registra la caja de cada track visible en el cuadro actual."""
        for track_id, caja in observaciones:
            self._cajas[track_id] = tuple(caja)

    def aceptar(self, evento: Evento, tiempo_s: float) -> bool:
        caja = self._cajas[evento.track_id]
        for momento, otro, sentido in self._aceptados:
            if (sentido == evento.sentido and otro != evento.track_id and tiempo_s - momento <= self.ventana_s
                    and superposicion(caja, self._cajas[otro]) >= self.umbral):
                self.descartados.append({"tiempo_s": round(evento.tiempo_s, 3), "track_id": evento.track_id,
                                         "sentido": evento.sentido, "encimado_con": otro})
                return False
        self._aceptados.append((tiempo_s, evento.track_id, evento.sentido))
        return True
