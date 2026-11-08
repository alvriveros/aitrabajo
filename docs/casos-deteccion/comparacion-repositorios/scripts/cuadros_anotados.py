"""Compara detecciones por cuadro con las cajas de persona anotadas (data/annotations/oficina-cajas.json).

Uso, desde la raíz: python cuadros_anotados.py DETECCIONES.json UMBRAL
Cuenta, en los cuadros anotados (6-52 s): cuadros con persona cuyo interior no contiene el centro de
ninguna detección (perdidas) y detecciones cuyo centro cae fuera de la caja anotada o en cuadros
sin persona (fuera de caja). Es una aproximación: la caja de persona no es una etiqueta de cabeza.
"""
import json
import sys

datos = {round(c["t"], 2): c["cajas"] for c in json.load(open(sys.argv[1]))["cuadros"]}
umbral = float(sys.argv[2])
anotados = json.load(open("data/annotations/oficina-cajas.json"))["cuadros"]
con_persona = perdidas = fuera = vacios = vacios_con_deteccion = 0
for cuadro in anotados:
    cajas = [c for c in datos[round(cuadro["tiempo_s"], 2)] if c[4] >= umbral]
    centros = [((c[0] + c[2]) / 2, (c[1] + c[3]) / 2) for c in cajas]
    caja = cuadro["caja"]
    if caja is None:
        vacios += 1
        vacios_con_deteccion += bool(cajas)
        fuera += len(cajas)
        continue
    x1, y1, x2, y2 = caja
    dentro = [x1 <= x <= x2 and y1 <= y <= y2 for x, y in centros]
    con_persona += 1
    perdidas += not any(dentro)
    fuera += dentro.count(False)
print(json.dumps({"detecciones": sys.argv[1], "umbral": umbral, "cuadros_con_persona": con_persona,
                  "cuadros_con_persona_sin_deteccion": perdidas, "cuadros_sin_persona": vacios,
                  "cuadros_sin_persona_con_deteccion": vacios_con_deteccion, "detecciones_fuera_de_caja": fuera}))
