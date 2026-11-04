from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Ocupación del bus")


class Evento(BaseModel):
    tiempo_s: float = Field(ge=0, allow_inf_nan=False)
    track_id: int
    sentido: Literal["subida", "bajada"]


class Parada(BaseModel):
    nombre: str = Field(min_length=1)
    inicio_s: float = Field(ge=0, allow_inf_nan=False)


class Recorrido(BaseModel):
    capacidad: int = Field(gt=0)
    carga_inicial: int = Field(ge=0)
    paradas: list[Parada] = Field(min_length=1)
    eventos: list[Evento]


@app.post("/ocupacion")
def calcular(recorrido: Recorrido):
    """Cada parada abarca desde su inicio hasta el inicio de la siguiente."""
    inicios = [p.inicio_s for p in recorrido.paradas]
    if inicios[0] != 0 or any(a >= b for a, b in zip(inicios, inicios[1:])):
        raise HTTPException(422, "Las paradas deben empezar en 0 y avanzar en el tiempo.")

    pasajeros = recorrido.carga_inicial
    filas = []
    avisos = []
    indice = 0
    for numero, parada in enumerate(recorrido.paradas):
        fin = inicios[numero + 1] if numero + 1 < len(inicios) else float("inf")
        subidas = bajadas = 0
        while indice < len(recorrido.eventos):
            evento = recorrido.eventos[indice]
            if indice and evento.tiempo_s < recorrido.eventos[indice - 1].tiempo_s:
                raise HTTPException(422, "Los eventos deben estar en orden temporal.")
            if evento.tiempo_s >= fin:
                break
            if evento.sentido == "subida":
                subidas += 1
                pasajeros += 1
            else:
                bajadas += 1
                pasajeros -= 1
                if pasajeros < 0:
                    avisos.append(f"Conteo negativo en {parada.nombre} a los {evento.tiempo_s:g} s.")
            indice += 1
        filas.append(dict(parada=parada.nombre, subidas=subidas, bajadas=bajadas,
                          pasajeros=pasajeros, ocupacion_pct=round(100 * pasajeros / recorrido.capacidad, 2)))
    return {"paradas": filas, "avisos": avisos}
