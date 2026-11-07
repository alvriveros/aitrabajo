import json
import math
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import altair as alt
import streamlit as st
import vl_convert as vlc

st.set_page_config(page_title="Ocupación del bus")
st.title("Ocupación del bus")
DEMO = Path(__file__).resolve().parents[1] / "docs/demo/recorrido.json"
MANUAL = DEMO.with_name("oficina-00-06-manual.json")
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


LETRA = 15  # px; con el ancho de columna del informe equivale a unos 6 pt


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
              axis=alt.Axis(labelAngle=-30, labelLimit=400)),
        eje_y,
    )
    barras = base.mark_bar().encode(opacity=alt.condition("datum.parcial", alt.value(0.55), alt.value(1)))
    rotulos = base.mark_text(baseline=alt.expr("datum.ocupacion_pct < 0 ? 'top' : 'bottom'"),
                             dy=alt.expr("datum.ocupacion_pct < 0 ? 4 : -4"),
                             color="#7a7a7a", fontWeight="bold", fontSize=LETRA).encode(text="texto:N")  # legible en ambos temas
    capacidad = alt.Chart(alt.Data(values=[{"ocupacion_pct": 100}])).encode(eje_y)
    linea = capacidad.mark_rule(color="#d62728", strokeDash=[6, 4], strokeWidth=2)
    # El rótulo va fuera del área de barras para que ninguna lo tape.
    rotulo = capacidad.mark_text(x=alt.expr("width"), align="left", dx=6, color="#d62728", fontSize=LETRA).encode(
        text=alt.value("Capacidad 100 %"))
    # Letra grande y área de datos acotada: el texto sigue legible al reducir el gráfico en el informe.
    return ((barras + rotulos + linea + rotulo)
            .properties(width=380, height=280, padding={"right": 150})
            .configure_axis(labelFontSize=LETRA, titleFontSize=LETRA))


def svg_del_grafico(filas):
    """Dibuja el gráfico en el servidor y devuelve el SVG completo.

    El componente de gráficos de Streamlit a veces conservaba los valores anteriores al mover el
    selector. Con el SVG, cada ejecución entrega al navegador el dibujo terminado del instante elegido.
    """
    version = alt.SCHEMA_VERSION.lstrip("v").rsplit(".", 1)[0].replace(".", "_")  # p. ej. 5_20
    svg = vlc.vegalite_to_svg(graficar(filas).to_json(), vl_version=version)
    # Ocupa el ancho de la columna sin deformarse.
    return svg.replace("<svg ", '<svg style="width:100%;max-width:720px;height:auto" ', 1)


def pedir(ruta, metodo="GET", timeout=10):
    """Llama a la API y devuelve el cuerpo en bytes. Ante un error muestra el detalle y detiene el panel."""
    try:
        with urlopen(Request(url + ruta, method=metodo), timeout=timeout) as respuesta:
            return respuesta.read()
    except HTTPError as error:
        try:
            detalle = json.load(error)["detail"]
        except (ValueError, KeyError):
            detalle = str(error)
        st.error(f"La API respondió {error.code}: {detalle}")
    except (URLError, TimeoutError) as error:
        st.error(f"No se pudo consultar la API en {url}. Comprobá que esté ejecutándose. {error}")
    st.stop()


def eventos_en_tabla(eventos):
    return [{"tiempo (s)": e["tiempo_s"], "sentido": e["sentido"], "track": e["track_id"]} for e in eventos]


fuente = st.radio("Origen de los eventos", ["Archivo JSON o demo", "Predicción automática del video de oficina"],
                  horizontal=True)
if fuente == "Archivo JSON o demo":
    subido = st.file_uploader("Recorrido en JSON (sin archivo se usa la demo)", type="json")
    origen = subido.file_id if subido else "demo"
    st.caption(f"Recorrido: {subido.name if subido else 'demo sintética · docs/demo/recorrido.json'}")
    try:
        recorrido = json.loads(subido.getvalue() if subido else DEMO.read_text(encoding="utf-8"))
    except ValueError as error:  # incluye JSON mal formado y texto que no es UTF-8
        st.error(f"No se pudo leer el archivo como JSON ({error}). Corregilo o cargá otro.")
        st.stop()
else:
    st.caption("Clip `data/raw/oficina.mp4`, tramo 0–6 s, cuadrante superior derecho y línea de "
               "`evaluation/results/oficina-00-06-prediccion.config.json`.")
    if st.button("Procesar clip de oficina (0–6 s)"):
        with st.spinner("Detectando y siguiendo personas…"):
            st.session_state["ejecucion"] = json.loads(pedir("/procesamientos", "POST", timeout=660))["id"]
    ejecuciones = json.loads(pedir("/procesamientos"))
    if not ejecuciones:
        st.info("Todavía no hay ejecuciones. Procesá el clip para ver el video anotado y su ocupación.")
        st.stop()
    elegida = st.session_state.get("ejecucion")
    elegida = st.selectbox("Ejecución", ejecuciones, index=ejecuciones.index(elegida) if elegida in ejecuciones else 0)
    ejecucion = json.loads(pedir(f"/procesamientos/{elegida}"))
    recorrido, config = ejecucion["recorrido"], ejecucion["configuracion"]
    origen = f"video-{elegida}"
    st.video(pedir(f"/procesamientos/{elegida}/video"), format="video/webm")
    medicion = config["medicion"]
    st.caption(f"Video anotado por el modelo · pesos `{config['pesos']}` · {medicion['cuadros']} cuadros en "
               f"{medicion['segundos']:g} s ({medicion['fps_procesados']:g} FPS).")
    prediccion, referencia = st.columns(2)
    prediccion.markdown("**Predicción automática** (ejecución del modelo)")
    prediccion.dataframe(eventos_en_tabla(recorrido["eventos"]), hide_index=True)
    manual = json.loads(MANUAL.read_text(encoding="utf-8"))
    referencia.markdown("**Referencia manual** (aprox., solo para comparar)")
    referencia.dataframe(eventos_en_tabla(manual["eventos"]), hide_index=True)
    st.caption("La ocupación de abajo usa únicamente la predicción automática.")
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
st.markdown(f'<div class="grafico-ocupacion">{svg_del_grafico(resultado["paradas"])}</div>', unsafe_allow_html=True)
st.caption(f"Conteo parcial en la parada {len(resultado['paradas'])} ({actual['parada']}): "
           f"incluye los cruces hasta los {segundo:g} s.")
st.subheader("Conteo por parada")
st.dataframe(resultado["paradas"], hide_index=True)
