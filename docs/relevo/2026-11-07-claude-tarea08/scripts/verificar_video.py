"""Procesa el clip de oficina desde el panel y acepta o rechaza el resultado (amplía el script de la tarea 07).

Uso:
  PANEL_URL=http://127.0.0.1:8501 API_URL=http://127.0.0.1:8000 python verificar_video.py SALIDA/

Pulsa «Procesar clip de oficina (0–6 s)» y comprueba:
  - video: el navegador lo reproduce sin error, avanza, dura lo mismo que el tramo y mide lo mismo que el recorte;
  - selector: incluye 0 s, cada evento, 4 s y el final del tramo, y termina en ese final;
  - en cada instante, indicadores y tabla iguales a la ocupación derivada de los eventos de la propia
    ejecución (GET /procesamientos/<id>), sin usar la referencia manual.
Guarda capturas, la respuesta de la API y resultado.json. Termina con código 1 ante cualquier fallo.
"""
import json
import os
import sys
from pathlib import Path
from urllib.request import urlopen

from playwright.sync_api import sync_playwright

salida = Path(sys.argv[1])
salida.mkdir(parents=True, exist_ok=True)
api = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")
fallos = []


def esperar(p):
    p.wait_for_timeout(600)
    p.wait_for_selector('[data-testid="stStatusWidget"]', state="detached", timeout=700000)
    p.wait_for_timeout(900)


def esperado(recorrido, t):
    """Pasajeros y ocupación a los t s según los eventos (misma regla que POST /ocupacion)."""
    n = recorrido["carga_inicial"] + sum(1 if e["sentido"] == "subida" else -1
                                         for e in recorrido["eventos"] if e["tiempo_s"] <= t)
    return n, round(100 * n / recorrido["capacidad"], 2)


def valor(texto):
    return float(texto.replace("%", "").strip())


with sync_playwright() as pw:
    navegador = pw.chromium.launch()
    p = navegador.new_page(viewport={"width": 900, "height": 1300})
    p.goto(os.getenv("PANEL_URL", "http://127.0.0.1:8501"))
    p.wait_for_selector('[data-testid="stMetricValue"]', timeout=30000)
    p.get_by_text("Predicción automática del video de oficina").click()
    esperar(p)
    antes = json.load(urlopen(api + "/procesamientos"))
    p.get_by_role("button", name="Procesar clip de oficina (0–6 s)").click()
    esperar(p)
    mensajes = p.locator('[data-testid="stAlert"]').all_inner_texts()
    p.screenshot(path=str(salida / "01-tras-procesar.png"), full_page=True)
    nuevas = [e for e in json.load(urlopen(api + "/procesamientos")) if e not in antes]
    if len(nuevas) != 1 or not p.locator("video").count():
        fallos.append(f"no hay una ejecución nueva publicada con video (nuevas: {nuevas}; mensajes: {mensajes})")
        (salida / "resultado.json").write_text(json.dumps({"fallos": fallos}, ensure_ascii=False, indent=2), encoding="utf-8")
        print(fallos)
        sys.exit(1)
    ejecucion = nuevas[0]
    respuesta = json.load(urlopen(f"{api}/procesamientos/{ejecucion}"))
    (salida / "respuesta-api.json").write_text(json.dumps(respuesta, ensure_ascii=False, indent=2), encoding="utf-8")
    recorrido, config = respuesta["recorrido"], respuesta["configuracion"]
    tramo = config["tramo_s"]
    fin = tramo["fin"] - tramo["inicio"]
    seleccionada = p.locator('[data-testid="stSelectbox"]').inner_text().split("\n")[-1]
    if seleccionada != ejecucion:
        fallos.append(f"el panel muestra la ejecución {seleccionada}, no la nueva {ejecucion}")

    video = p.evaluate("""async () => {
      const v = document.querySelector('video');
      v.muted = true;
      if (v.readyState < 1) await new Promise(r => v.addEventListener('loadedmetadata', r, {once: true}));
      await v.play();
      await new Promise(r => setTimeout(r, 1500));
      return {duracion_s: v.duration, avanzado_s: v.currentTime, error: v.error && v.error.code,
              ancho: v.videoWidth, alto: v.videoHeight};
    }""")
    p.locator("video").screenshot(path=str(salida / "02-video-reproduciendo.png"))
    recorte = config["recorte"]
    if video["error"] is not None:
        fallos.append(f"error de reproducción {video['error']}")
    if video["avanzado_s"] < 0.5:
        fallos.append(f"el video no avanzó: {video['avanzado_s']} s")
    if abs(video["duracion_s"] - fin) > 0.1:
        fallos.append(f"duración {video['duracion_s']} s frente a tramo de {fin} s")
    if (video["ancho"], video["alto"]) != (recorte["ancho"], recorte["alto"]):
        fallos.append(f"video de {video['ancho']}x{video['alto']} frente a recorte {recorte['ancho']}x{recorte['alto']}")

    # Recorre el selector entero con el teclado, desde la primera marca.
    deslizador = p.locator('[data-testid="stSlider"] [role="slider"]')
    for _ in range(60):
        previo = p.locator('[data-testid="stSliderThumbValue"]').inner_text()
        deslizador.focus()
        p.keyboard.press("ArrowLeft")
        esperar(p)
        if p.locator('[data-testid="stSliderThumbValue"]').inner_text() == previo:
            break
    estados = []
    for paso in range(60):
        segundo = valor(p.locator('[data-testid="stSliderThumbValue"]').inner_text().replace(" s", ""))
        metricas = p.locator('[data-testid="stMetricValue"]').all_inner_texts()
        tabla = [c.strip() for c in p.locator('[data-testid="stDataFrame"]').last.locator("tbody td").all_inner_texts()]
        n, pct = esperado(recorrido, segundo)
        estado = {"segundo": segundo, "pasajeros": metricas[0], "ocupacion": metricas[1],
                  "tabla_pasajeros": tabla[3], "tabla_ocupacion": tabla[4], "esperado": [n, pct]}
        if (int(metricas[0]), valor(metricas[1]), int(tabla[3]), valor(tabla[4])) != (n, pct, n, pct):
            fallos.append(f"a {segundo:g} s: panel {estado} frente a esperado {n} y {pct:g} %")
        estados.append(estado)
        p.screenshot(path=str(salida / f"03-ocupacion-{paso:02d}-{segundo:g}s.png"), full_page=True)
        deslizador.focus()
        p.keyboard.press("ArrowRight")
        esperar(p)
        if valor(p.locator('[data-testid="stSliderThumbValue"]').inner_text().replace(" s", "")) == segundo:
            break

    vistos = [e["segundo"] for e in estados]
    requeridos = sorted({0.0, 4.0, fin} | {e["tiempo_s"] for e in recorrido["eventos"]})
    faltan = [t for t in requeridos if not any(abs(t - v) < 1e-6 for v in vistos)]
    if faltan:
        fallos.append(f"el selector no ofrece los instantes {faltan}")
    if not vistos or abs(vistos[-1] - fin) > 1e-6:
        fallos.append(f"el selector termina en {vistos[-1] if vistos else None} s, no en {fin} s")

    resultado = {"ejecucion": ejecucion, "eventos": recorrido["eventos"], "video": video, "estados": estados,
                 "instantes_requeridos": requeridos, "mensajes": mensajes, "fallos": fallos}
    (salida / "resultado.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    navegador.close()
sys.exit(1 if fallos else 0)
