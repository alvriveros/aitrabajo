import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import streamlit as st

st.set_page_config(page_title="Ocupación del bus")
st.title("Ocupación del bus")
st.caption("Recorrido simulado · Dos paradas y tres cruces de ejemplo")
archivo = Path(__file__).resolve().parents[1] / "docs/demo/recorrido.json"
recorrido = json.loads(archivo.read_text(encoding="utf-8"))
recorrido["capacidad"] = st.number_input("Capacidad del bus", min_value=1, value=recorrido["capacidad"])
recorrido["carga_inicial"] = st.number_input("Pasajeros al inicio", min_value=0, value=recorrido["carga_inicial"])
segundo = st.slider("Segundo del recorrido", 0, 15, 15)
recorrido["eventos"] = [e for e in recorrido["eventos"] if e["tiempo_s"] <= segundo]
recorrido["paradas"] = [p for p in recorrido["paradas"] if p["inicio_s"] <= segundo]

url = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")
pedido = Request(url + "/ocupacion", data=json.dumps(recorrido).encode(),
                 headers={"Content-Type": "application/json"})
try:
    with urlopen(pedido, timeout=5) as respuesta:
        resultado = json.load(respuesta)
except (HTTPError, URLError, TimeoutError) as error:
    st.error(f"No se pudo consultar la API en {url}. Comprobá que esté ejecutándose. {error}")
    st.stop()

actual = resultado["paradas"][-1]
cantidad, porcentaje = st.columns(2)
cantidad.metric("Pasajeros a bordo", actual["pasajeros"])
porcentaje.metric("Ocupación", f"{actual['ocupacion_pct']:g} %")
for aviso in resultado["avisos"]:
    st.warning(aviso)
st.subheader("Conteo por parada")
st.dataframe(resultado["paradas"], hide_index=True)
