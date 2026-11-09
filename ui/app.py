import json
import math
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
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


def pedir(ruta, metodo="GET", timeout=10, datos=None, json_=None, aviso_si=()):
    """Llama a la API y devuelve el cuerpo en bytes. Ante un error muestra el detalle y detiene el panel,
    salvo los códigos de `aviso_si`, que se muestran como aviso y devuelven None."""
    cabeceras = {}
    if json_ is not None:
        datos, cabeceras = json.dumps(json_).encode(), {"Content-Type": "application/json"}
    elif datos is not None:
        cabeceras = {"Content-Type": "application/octet-stream"}
    try:
        with urlopen(Request(url + ruta, data=datos, headers=cabeceras, method=metodo), timeout=timeout) as respuesta:
            return respuesta.read()
    except HTTPError as error:
        try:
            detalle = json.load(error)["detail"]
        except (ValueError, KeyError):
            detalle = str(error)
        if error.code in aviso_si:
            st.warning(detalle)
            return None
        st.error(f"La API respondió {error.code}: {detalle}")
    except (URLError, TimeoutError) as error:
        st.error(f"No se pudo consultar la API en {url}. Comprobá que esté ejecutándose. {error}")
    st.stop()


def eventos_en_tabla(eventos):
    return [{"tiempo (s)": e["tiempo_s"], "sentido": e["sentido"], "track": e["track_id"]} for e in eventos]


def mostrar_ejecucion(elegida, referencia_oficina):
    """Video anotado, eventos, descargas y configuración de una ejecución. Devuelve (recorrido, origen, fin_tramo)."""
    ejecucion = json.loads(pedir(f"/procesamientos/{elegida}"))
    recorrido, config = ejecucion["recorrido"], ejecucion["configuracion"]
    video = pedir(f"/procesamientos/{elegida}/video")
    # Los recortes chicos se ampliarían a todo el ancho; en videos nuevos se limita el tamaño.
    st.video(video, format="video/webm", width="stretch" if referencia_oficina else 480)
    medicion = config["medicion"]
    tramo = config["tramo_s"]
    # Misma base que tiempo_s: segundos desde el inicio del tramo. Sin --fin, hasta el último cuadro leído.
    fin_tramo = (tramo["fin"] - tramo["inicio"] if tramo["fin"] is not None
                 else medicion["cuadros"] / config["propiedades_del_video"]["fps"])
    st.caption(f"Video anotado por el modelo · pesos `{config['pesos']}` · {medicion['cuadros']} cuadros en "
               f"{medicion['segundos']:g} s ({medicion['fps_procesados']:g} FPS).")
    entrada = ejecucion["entrada"]
    if entrada:
        st.caption(f"Ejecución `{elegida}` · pedida {entrada['pedido']} · "
                   + ("**repetición para demostración** (no reemplaza a la primera)"
                      if entrada.get("proposito") == "repeticion para demostracion" else "primera ejecución"))
    reproducible = {"entrada": entrada, "configuracion": config}
    json_, webm, conf = st.columns(3)
    json_.download_button("Descargar eventos (JSON)", json.dumps(recorrido, ensure_ascii=False, indent=2),
                          f"{elegida}-eventos.json", "application/json", key=f"json-{elegida}")
    webm.download_button("Descargar video anotado", video, f"{elegida}-anotado.webm", "video/webm", key=f"webm-{elegida}")
    conf.download_button("Descargar configuración", json.dumps(reproducible, ensure_ascii=False, indent=2),
                         f"{elegida}-configuracion.json", "application/json", key=f"conf-{elegida}")
    if referencia_oficina:
        prediccion, referencia = st.columns(2)
        prediccion.markdown("**Predicción automática** (ejecución del modelo)")
        prediccion.dataframe(eventos_en_tabla(recorrido["eventos"]), hide_index=True)
        manual = json.loads(MANUAL.read_text(encoding="utf-8"))
        referencia.markdown("**Referencia manual** (aprox., solo para comparar)")
        referencia.dataframe(eventos_en_tabla(manual["eventos"]), hide_index=True)
        st.caption("La ocupación de abajo usa únicamente la predicción automática.")
    else:
        st.markdown(f"**Eventos detectados:** {len(recorrido['eventos'])}")
        st.dataframe(eventos_en_tabla(recorrido["eventos"]), hide_index=True)
    return recorrido, f"video-{elegida}", fin_tramo


def elegir_ejecucion(ejecuciones, clave):
    elegida = st.session_state.get(clave)
    return st.selectbox("Ejecución", ejecuciones, index=ejecuciones.index(elegida) if elegida in ejecuciones else 0,
                        key=f"selector-{clave}")


def geometria_de_video(info):
    """Controles de recorte, línea e interior para un video subido; devuelve la geometría elegida."""
    ancho, alto, clave = info["ancho"], info["alto"], info["id"]
    st.markdown(
        f"**Coordenadas:** píxeles enteros con origen **arriba a la izquierda**, x hacia la derecha, y hacia abajo. "
        f"El cuadro mide {ancho}×{alto}. El **recorte** se mide en el cuadro completo; la **línea**, dentro del "
        "recorte (su 0,0 es la esquina superior izquierda del recorte). Cruzar la línea hacia el **interior** es "
        "una subida; hacia afuera, una bajada.")
    c1, c2, c3, c4 = st.columns(4)
    x = c1.number_input("Recorte X", 0, ancho - 32, 0, key=f"rx-{clave}")
    y = c2.number_input("Recorte Y", 0, alto - 32, 0, key=f"ry-{clave}")
    w = c3.number_input("Recorte ancho", 32, ancho, ancho, key=f"rw-{clave}")
    h = c4.number_input("Recorte alto", 32, alto, alto, key=f"rh-{clave}")
    l1, l2, l3, l4 = st.columns(4)
    x1 = l1.number_input("Línea X1", 0, ancho - 1, 0, key=f"lx1-{clave}")
    y1 = l2.number_input("Línea Y1", 0, alto - 1, alto // 2, key=f"ly1-{clave}")
    x2 = l3.number_input("Línea X2", 0, ancho - 1, ancho - 1, key=f"lx2-{clave}")
    y2 = l4.number_input("Línea Y2", 0, alto - 1, alto // 2, key=f"ly2-{clave}")
    interior = st.selectbox("Interior del vehículo (hacia dónde se sube)", ["arriba", "abajo", "izquierda", "derecha"],
                            key=f"int-{clave}")
    st.caption(f"En el cuadro completo, la línea va de ({x + x1}, {y + y1}) a ({x + x2}, {y + y2}).")
    return {"recorte": [x, y, w, h], "linea": [x1, y1, x2, y2], "interior": interior}


fin_tramo = None  # los JSON no declaran duración: el selector termina en su última marca
fuente = st.radio("Origen de los eventos",
                  ["Archivo JSON o demo", "Predicción automática del video de oficina", "Video nuevo"], horizontal=True)
if fuente == "Archivo JSON o demo":
    subido = st.file_uploader("Recorrido en JSON (sin archivo se usa la demo)", type="json")
    origen = subido.file_id if subido else "demo"
    st.caption(f"Recorrido: {subido.name if subido else 'demo sintética · docs/demo/recorrido.json'}")
    try:
        recorrido = json.loads(subido.getvalue() if subido else DEMO.read_text(encoding="utf-8"))
    except ValueError as error:  # incluye JSON mal formado y texto que no es UTF-8
        st.error(f"No se pudo leer el archivo como JSON ({error}). Corregilo o cargá otro.")
        st.stop()
elif fuente == "Predicción automática del video de oficina":
    st.caption("Clip `data/raw/oficina.mp4`, tramo 0–6 s, cuadrante superior derecho y línea de "
               "`evaluation/results/oficina-00-06-prediccion.config.json`.")
    if st.button("Procesar clip de oficina (0–6 s)"):
        with st.spinner("Detectando y siguiendo personas…"):
            st.session_state["ejecucion"] = json.loads(pedir("/procesamientos", "POST", timeout=660))["id"]
    ejecuciones = json.loads(pedir("/procesamientos?origen=demo"))
    if not ejecuciones:
        st.info("Todavía no hay ejecuciones. Procesá el clip para ver el video anotado y su ocupación.")
        st.stop()
    recorrido, origen, fin_tramo = mostrar_ejecucion(elegir_ejecucion(ejecuciones, "ejecucion"), True)
else:
    st.markdown("**1. Subí el video.** Formatos mp4, avi, mov, mkv o webm; hasta 200 MB y 5 minutos. Se procesa "
                "completo y el tiempo de cada cruce se cuenta en segundos **desde el primer cuadro del video**.")
    archivo = st.file_uploader("Video", type=["mp4", "avi", "mov", "mkv", "webm"])
    if archivo is None:
        st.stop()
    clave = f"subida-{archivo.file_id}"
    if clave not in st.session_state:  # se sube una sola vez por archivo, no en cada actualización del panel
        with st.spinner("Subiendo y validando el video…"):
            st.session_state[clave] = json.loads(
                pedir(f"/videos?nombre={quote(archivo.name)}", "POST", timeout=300, datos=archivo.getvalue()))
    info = st.session_state[clave]
    st.caption(f"`{info['nombre_original']}` · {info['ancho']}×{info['alto']} · {info['fps']:g} FPS · "
               f"{info['cuadros']} cuadros · {info['duracion_s']:g} s · SHA-256 `{info['sha256'][:16]}…`")

    st.markdown("**2. Ubicá el recorte y la línea de conteo.** La vista previa no ejecuta ningún modelo.")
    geometria = geometria_de_video(info)
    segundo_previa = st.slider("Cuadro de vista previa (s, aproximado)", 0.0, float(info["duracion_s"]), 0.0, 0.5,
                               key=f"previa-{info['id']}")
    consulta = urlencode({"t": segundo_previa, "interior": geometria["interior"],
                          "recorte": ",".join(map(str, geometria["recorte"])),
                          "linea": ",".join(map(str, geometria["linea"]))})
    st.image(pedir(f"/videos/{info['id']}/cuadro?{consulta}"),
             caption="Azul: recorte · amarillo: línea de conteo · verde: hacia el interior (subida)")

    st.markdown("**3. Procesá el video.** Usa la configuración de la API: `yolo11n` con el rastreador calibrado "
                "(ByteTrack cenital, confianza 0,05, confirmación de 2 cuadros), sin filtros adicionales. "
                "Se ejecuta solo al pulsar un botón. «Procesar video» no repite una configuración ya procesada: muestra "
                "el resultado guardado. Para ejecutar de nuevo en vivo, usá «Reprocesar en vivo para demostración».")
    p1, p2, p3 = st.columns(3)
    parada = p1.text_input("Nombre de la parada", "Puerta", key=f"parada-{info['id']}")
    capacidad = p2.number_input("Capacidad", 1, 500, 20, key=f"cap-{info['id']}")
    carga = p3.number_input("Pasajeros al inicio", 0, 500, 0, key=f"carga-{info['id']}")
    pedido = {**geometria, "parada": parada or "Puerta", "capacidad": capacidad, "carga_inicial": carga}
    procesar, repetir = st.columns(2)
    accion = None
    if procesar.button("Procesar video", type="primary"):
        accion = False
    if repetir.button("Reprocesar en vivo para demostración"):
        accion = True
    repetir.caption("Vuelve a ejecutar el modelo con la misma configuración y lo guarda como ejecución aparte; "
                    "la primera evaluación no se modifica.")
    if accion is not None:  # solo con un clic: las actualizaciones del panel no vuelven a procesar
        with st.spinner("Procesando en vivo: detectando y siguiendo personas… no cierres la página."):
            cuerpo = pedir(f"/videos/{info['id']}/procesamientos", "POST", timeout=1860,
                           json_={**pedido, "repetir_para_demostracion": accion}, aviso_si=(409,))
            if cuerpo:
                st.session_state[f"ejecucion-{info['id']}"] = st.session_state[f"en-vivo-{info['id']}"] = json.loads(cuerpo)["id"]
    ejecuciones = json.loads(pedir(f"/procesamientos?video={info['id']}"))
    if not ejecuciones:
        st.info("Todavía no se procesó este video.")
        st.stop()
    elegida = elegir_ejecucion(ejecuciones, f"ejecucion-{info['id']}")
    if elegida == st.session_state.get(f"en-vivo-{info['id']}"):
        st.markdown("**4. Resultado procesado en vivo** (recién ejecutado en esta sesión).")
    else:
        st.markdown("**4. Resultado guardado** (ejecución anterior; no se volvió a ejecutar el modelo).")
    recorrido, origen, fin_tramo = mostrar_ejecucion(elegida, False)
consultar(recorrido)  # valida el recorrido completo antes de filtrarlo por tiempo

# Las claves llevan el origen para que los controles tomen los valores de cada archivo nuevo.
recorrido["capacidad"] = st.number_input("Capacidad del bus", min_value=1,
                                         value=int(recorrido["capacidad"]), key=f"capacidad-{origen}")
recorrido["carga_inicial"] = st.number_input("Pasajeros al inicio", min_value=0,
                                             value=int(recorrido["carga_inicial"]), key=f"carga-{origen}")
marcas = {float(p["inicio_s"]) for p in recorrido["paradas"]} | {float(e["tiempo_s"]) for e in recorrido["eventos"]}
if fin_tramo is not None:
    marcas.add(float(fin_tramo))
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
