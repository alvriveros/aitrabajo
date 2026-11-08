"""Verifica que el gráfico dibujado coincida con la tabla después de cada cambio.

Uso:
  PANEL_URL=http://127.0.0.1:8502 python verificar_grafico.py PREDICCION.json CASOS/ SALIDA/

CASOS/ debe contener nombres-repetidos.json, sobreocupacion.json y conteo-negativo.json.
Para cada estado compara, barra por barra y en orden:
  - el rótulo de valor dibujado en el SVG,
  - el valor que resulta de la altura de la barra medida contra el eje (0 y 100),
  - el color de la barra en la captura de pantalla,
con la fila de la tabla y, en el recorrido predicho, con el valor esperado.
Termina con código 1 ante cualquier desacuerdo.
"""
import json
import os
import sys
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

prediccion, casos, salida = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
(salida / "capturas").mkdir(parents=True, exist_ok=True)
registro, fallos = [], []

LEER = """() => {
  const svg = document.querySelector('.grafico-ocupacion svg');
  if (!svg) return null;
  const caja = e => { const r = e.getBoundingClientRect(); return {x: r.x, y: r.y, w: r.width, h: r.height}; };
  const textos = [...svg.querySelectorAll('text')].map(t => ({t: t.textContent.trim(), ...caja(t)}));
  const barras = [...svg.querySelectorAll('g.mark-rect path')].map(caja);
  const regla = [...svg.querySelectorAll('g.mark-rule.role-mark line, g.mark-rule.role-mark path')].map(caja);
  const lienzo = caja(svg);
  return {textos, barras, regla, lienzo};
}"""


def esperar(p):
    p.wait_for_timeout(600)
    p.wait_for_selector('[data-testid="stStatusWidget"]', state="detached", timeout=20000)
    p.wait_for_timeout(900)


def tabla(p):
    celdas = [c.strip() for c in p.locator('[data-testid="stDataFrame"] table td').all_inner_texts()]
    return [dict(parada=celdas[i], pct=float(celdas[i + 4])) for i in range(0, len(celdas), 5)]


def medir(p, nombre, esperado=None):
    esperar(p)
    # tarea07: el selector de origen alarga la página; sin desplazar antes de medir, la captura
    # (que sí desplaza) y las coordenadas del SVG quedan corridas cuando el gráfico sale de la vista.
    p.locator(".grafico-ocupacion").scroll_into_view_if_needed()
    g = p.evaluate(LEER)
    filas = tabla(p)
    indicador = p.locator('[data-testid="stMetricValue"]').all_inner_texts()[1]
    segundo = p.locator('[data-testid="stSliderThumbValue"]').all_inner_texts()
    captura = salida / "capturas" / f"{len(registro) + 1:03d}-{nombre}.png"
    p.locator(".grafico-ocupacion").screenshot(path=str(captura))
    errores = []
    if g is None:
        errores.append("no hay gráfico SVG")
        g = {"textos": [], "barras": [], "regla": [], "lienzo": {}}
    # Eje: posición vertical de las marcas 0 y 100 (el texto está centrado en la marca).
    eje = {t["t"]: t["y"] + t["h"] / 2 for t in g["textos"] if t["t"] in ("0", "100") and t["x"] < g["lienzo"].get("x", 0) + 45}
    rotulos = [t for t in g["textos"] if t["t"].endswith(" %") and not t["t"].startswith("Capacidad")]
    rotulos.sort(key=lambda t: t["x"])
    etiquetas = [t["t"] for t in g["textos"] if " · " in t["t"]]
    barras = sorted(g["barras"], key=lambda b: b["x"])
    if "0" not in eje or "100" not in eje:
        errores.append("no se encontraron las marcas 0 y 100 del eje")
    if not any(t["t"] == "Capacidad 100 %" for t in g["textos"]):
        errores.append("falta el rótulo de capacidad")
    if not g["regla"]:
        errores.append("falta la línea de capacidad")
    elif "100" in eje and abs(g["regla"][0]["y"] + g["regla"][0]["h"] / 2 - eje["100"]) > 2:
        errores.append("la línea de capacidad no está en 100")
    if not etiquetas or "(parcial)" not in etiquetas[-1] or any("(parcial)" in e for e in etiquetas[:-1]):
        errores.append(f"marca parcial incorrecta: {etiquetas}")
    if [e.split(" · ", 1)[1] for e in etiquetas] != [f["parada"] for f in filas]:
        errores.append(f"orden de paradas {etiquetas} frente a tabla {[f['parada'] for f in filas]}")
    if len(barras) != len(filas) or len(rotulos) != len(filas):
        errores.append(f"{len(barras)} barras y {len(rotulos)} rótulos para {len(filas)} filas")
    im = Image.open(captura).convert("RGB")
    caja = p.locator(".grafico-ocupacion").bounding_box()
    medidas = []
    for i, fila in enumerate(filas):
        if i >= len(barras) or i >= len(rotulos) or "0" not in eje:
            break
        b, y0, y100 = barras[i], eje["0"], eje["100"]
        arriba, abajo = b["y"], b["y"] + b["h"]
        negativo = abs(arriba - y0) < abs(abajo - y0) and b["h"] > 1
        valor = (-(abajo - y0) if negativo else (y0 - arriba)) / (y0 - y100) * 100
        rotulo = rotulos[i]["t"]
        # Color dibujado en el centro de la barra: azul si tiene altura, blanco o grilla si no.
        cx, cy = b["x"] + b["w"] / 2 - caja["x"], b["y"] + b["h"] / 2 - caja["y"]
        r, gg, bb = im.getpixel((int(cx), int(cy)))
        pintada = bb > r + 40
        medidas.append(dict(tabla=fila["pct"], rotulo=rotulo, altura=round(valor, 2), pintada=pintada))
        if rotulo != f"{fila['pct']:g} %":
            errores.append(f"barra {i + 1}: rótulo {rotulo} frente a tabla {fila['pct']:g}")
        if abs(valor - fila["pct"]) > 1.5:
            errores.append(f"barra {i + 1}: altura {valor:.1f} frente a tabla {fila['pct']:g}")
        if b["h"] >= 3 and not pintada:
            errores.append(f"barra {i + 1}: sin color en la captura")
    if filas and indicador != f"{filas[-1]['pct']:g} %":
        errores.append(f"indicador {indicador} frente a tabla {filas[-1]['pct']:g}")
    if esperado is not None and filas and filas[-1]["pct"] != esperado:
        errores.append(f"tabla {filas[-1]['pct']:g} frente a esperado {esperado:g}")
    fila = dict(paso=len(registro) + 1, nombre=nombre, segundo=segundo, indicador=indicador,
                esperado=esperado, barras=medidas, captura=captura.name, errores=errores)
    registro.append(fila)
    fallos.extend(f"{nombre}: {e}" for e in errores)
    print(f"{fila['paso']:3d} {nombre:28s} {indicador:>6s} {[ (m['rotulo'], m['altura']) for m in medidas]} {'OK' if not errores else errores}")


def recorrido_cargado(p, texto):
    p.wait_for_function(
        "t => [...document.querySelectorAll('[data-testid=stCaptionContainer]')].some(e => e.innerText.startsWith('Recorrido: ' + t))",
        arg=texto, timeout=20000)


def subir(p, archivo):
    # Vaciar el campo: si conserva el mismo archivo, el navegador no avisa del cambio.
    p.evaluate("document.querySelector('input[type=file]').value = ''")
    p.locator('input[type="file"]').set_input_files(str(archivo))
    recorrido_cargado(p, Path(archivo).name)


def quitar(p):
    p.locator('[data-testid="stFileUploaderDeleteBtn"] button').click()
    recorrido_cargado(p, "demo")


def mover(p, pasos):
    p.locator('[role="slider"]').focus()
    for _ in range(abs(pasos)):
        p.keyboard.press("ArrowRight" if pasos > 0 else "ArrowLeft")
        esperar(p)


with sync_playwright() as pw:
    navegador = pw.chromium.launch()
    p = navegador.new_page(viewport={"width": 900, "height": 1300})
    p.goto(os.getenv("PANEL_URL", "http://127.0.0.1:8502"))
    p.wait_for_selector('[data-testid="stMetricValue"]', timeout=30000)
    # tarea08: los indicadores pueden aparecer antes que el selector de archivo; esperar también a este.
    p.wait_for_selector('input[type="file"]', state="attached", timeout=30000)

    # 1. Recorrido predicho: 0 → 2 → 2,16 → 4 → 4,60 y vuelta, hasta superar 30 transiciones.
    subir(p, prediccion)
    esperar(p)
    instantes = [0, 1, 2, 2.16, 3, 4, 4.6]           # marcas del selector
    objetivo = [(0, 0), (2, 0), (2.16, 5), (4, 5), (4.6, 0)]  # instante, % esperado
    actual = len(instantes) - 1                     # al cargar, el selector queda al final
    ruta = objetivo + objetivo[-2::-1]
    transiciones = 0
    vuelta = 0
    while transiciones < 32:
        vuelta += 1
        for t, pct in (ruta if vuelta == 1 else ruta[1:]):
            destino = instantes.index(t)
            if destino != actual or transiciones == 0:
                mover(p, destino - actual)
                actual = destino
                transiciones += 1
                medir(p, f"pred-v{vuelta}-{t:g}s", pct)
            if transiciones >= 32:
                break

    # 2. Capacidad 10 en el archivo predicho a 2,16 s: 1 pasajero = 10 %.
    mover(p, instantes.index(2.16) - actual)
    actual = instantes.index(2.16)
    capacidad = p.locator('input[type="number"]').first
    capacidad.fill("10")
    capacidad.press("Enter")
    medir(p, "pred-capacidad10-2.16s", 10)

    # 3. Demo, y alternar demo ↔ predicción.
    quitar(p)
    medir(p, "demo-10s", 20)
    mover(p, -11)
    medir(p, "demo-0s", 15)
    mover(p, 6)
    medir(p, "demo-5s", 25)
    mover(p, 5)
    medir(p, "demo-10s-otra-vez", 20)
    capacidad = p.locator('input[type="number"]').first
    capacidad.fill("40")
    capacidad.press("Enter")
    medir(p, "demo-capacidad40", 10)
    for i in range(2):
        subir(p, prediccion)
        medir(p, f"alternar-{i + 1}-pred", 0)
        quitar(p)
        medir(p, f"alternar-{i + 1}-demo", 20)

    # 4. Casos de borde.
    for archivo, nombre, pct in (("nombres-repetidos.json", "nombres-repetidos", None),
                                 ("sobreocupacion.json", "sobreocupacion-150", 150),
                                 ("conteo-negativo.json", "conteo-negativo", -5)):
        subir(p, casos / archivo)
        medir(p, nombre, pct)
        quitar(p)
        esperar(p)
    navegador.close()

resumen = dict(estados=len(registro), transiciones_prediccion=transiciones, fallos=fallos)
(salida / "resultado.json").write_text(json.dumps(dict(resumen=resumen, registro=registro), ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(resumen, ensure_ascii=False))
sys.exit(1 if fallos else 0)
