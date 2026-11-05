import json
import math
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import altair as alt
import streamlit as st

st.set_page_config(page_title="Ocupación del bus")
st.title("Ocupación del bus")
DEMO = Path(__file__).resolve().parents[1] / "docs/demo/recorrido.json"
url = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")


def consultar(recorrido):
    """POST /ocupacion. Si la API rechaza el recorrido, muestra qué corregir y detiene el panel."""
    try:
        contenido = json.dumps(recorrido, allow_nan=False).encode()
    except ValueError:
        st.error("El recorrido contiene un número no finito. Corregí el archivo o cargá otro.")
        st.stop()
    pedido = Request(url + "/ocupacion", data=contenido,
                     headers={"Content-Type": "application/json"})
    try:
        with urlopen(pedido, timeout=5) as respuesta:
            return json.load(respuesta)
    except HTTPError as error:
        if error.code != 422:
            st.error(f"La API en {url} respondió con un error. {error}")
            st.stop()
        detalle = json.load(error)["detail"]
        problemas = [detalle] if isinstance(detalle, str) else [
            f"{'.'.join(map(str, e['loc'][1:])) or 'archivo'}: {e['msg']}" for e in detalle]
        st.error("El recorrido no es válido. Corregí el archivo o cargá otro.\n\n"
                 + "\n".join(f"- {p}" for p in problemas))
        st.stop()
    except (URLError, TimeoutError) as error:
        st.error(f"No se pudo consultar la API en {url}. Comprobá que esté ejecutándose. {error}")
        st.stop()


def graficar(filas):
    """Barras de ocupación en el orden del recorrido, con numeración para distinguir nombres repetidos."""
    # "(parcial)" va antes del nombre: el eje recorta los nombres largos por el final.
    datos = [dict(fila, etiqueta=f"{numero}{' (parcial)' if numero == len(filas) else ''} · {fila['parada']}",
                  parcial=numero == len(filas), texto=f"{fila['ocupacion_pct']:g} %")
             for numero, fila in enumerate(filas, start=1)]
    valores = [fila["ocupacion_pct"] for fila in filas]
    minimo, maximo = min(0, *valores), max(100, *valores)
    margen = (maximo - minimo) * 0.1  # deja lugar para el rótulo de cada barra
    eje_y = alt.Y("ocupacion_pct:Q", title="Ocupación (%)",
                  scale=alt.Scale(domain=[minimo - margen if minimo < 0 else 0, maximo + margen]))
    base = alt.Chart(alt.Data(values=datos)).encode(
        alt.X("etiqueta:N", title="Parada", sort=[d["etiqueta"] for d in datos],
              axis=alt.Axis(labelAngle=-30, labelLimit=220)),
        eje_y,
    )
    barras = base.mark_bar().encode(opacity=alt.condition("datum.parcial", alt.value(0.55), alt.value(1)))
    rotulos = base.mark_text(baseline=alt.expr("datum.ocupacion_pct < 0 ? 'top' : 'bottom'"),
                             dy=alt.expr("datum.ocupacion_pct < 0 ? 4 : -4"),
                             color="#7a7a7a", fontWeight="bold").encode(text="texto:N")  # legible en ambos temas
    capacidad = alt.Chart(alt.Data(values=[{"ocupacion_pct": 100}])).encode(eje_y)
    linea = capacidad.mark_rule(color="#d62728", strokeDash=[6, 4], strokeWidth=2)
    # El rótulo va fuera del área de barras para que ninguna lo tape.
    rotulo = capacidad.mark_text(x=alt.expr("width"), align="left", dx=6, color="#d62728").encode(
        text=alt.value("Capacidad 100 %"))
    return (barras + rotulos + linea + rotulo).properties(height=340, padding={"right": 115})


subido = st.file_uploader("Recorrido en JSON (sin archivo se usa la demo)", type="json")
origen = subido.file_id if subido else "demo"
st.caption(f"Recorrido: {subido.name if subido else 'demo sintética · docs/demo/recorrido.json'}")
try:
    recorrido = json.loads(subido.getvalue() if subido else DEMO.read_text(encoding="utf-8"))
except ValueError as error:  # incluye JSON mal formado y texto que no es UTF-8
    st.error(f"No se pudo leer el archivo como JSON ({error}). Corregilo o cargá otro.")
    st.stop()
consultar(recorrido)  # valida el recorrido completo antes de filtrarlo por tiempo

# Las claves llevan el origen para que los controles tomen los valores de cada archivo nuevo.
recorrido["capacidad"] = st.number_input("Capacidad del bus", min_value=1,
                                         value=int(recorrido["capacidad"]), key=f"capacidad-{origen}")
recorrido["carga_inicial"] = st.number_input("Pasajeros al inicio", min_value=0,
                                             value=int(recorrido["carga_inicial"]), key=f"carga-{origen}")
marcas = {float(p["inicio_s"]) for p in recorrido["paradas"]} | {float(e["tiempo_s"]) for e in recorrido["eventos"]}
ultimo_segundo = math.floor(max(marcas))
# En recorridos largos, limitar las marcas intermedias y conservar cada evento exacto.
paso = max(1, ultimo_segundo // 1000 + 1)
instantes = sorted(marcas | set(range(0, ultimo_segundo + 1, paso)))
if len(instantes) > 1:
    segundo = st.select_slider("Segundo del recorrido", instantes, value=instantes[-1],
                               format_func=lambda t: f"{t:g} s", key=f"segundo-{origen}")
else:
    segundo = 0
    st.caption("El recorrido termina en el segundo 0.")
recorrido["eventos"] = [e for e in recorrido["eventos"] if float(e["tiempo_s"]) <= segundo]
recorrido["paradas"] = [p for p in recorrido["paradas"] if float(p["inicio_s"]) <= segundo]

resultado = consultar(recorrido)
actual = resultado["paradas"][-1]
cantidad, porcentaje = st.columns(2)
cantidad.metric("Pasajeros a bordo", actual["pasajeros"])
porcentaje.metric("Ocupación", f"{actual['ocupacion_pct']:g} %")
for aviso in resultado["avisos"]:
    st.warning(aviso)
st.subheader("Ocupación por parada")
st.altair_chart(graficar(resultado["paradas"]), use_container_width=True)
st.caption(f"Conteo parcial en la parada {len(resultado['paradas'])} ({actual['parada']}): "
           f"incluye los cruces hasta los {segundo:g} s.")
st.subheader("Conteo por parada")
st.dataframe(resultado["paradas"], hide_index=True)
