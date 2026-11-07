"""Recorre en el panel el procesamiento del clip de oficina y guarda capturas y valores observados.

Uso:
  PANEL_URL=http://127.0.0.1:8501 python verificar_video.py SALIDA/

Pulsa «Procesar clip de oficina (0–6 s)», comprueba que el navegador reproduzca el video anotado y lee
las tablas de predicción y referencia. Luego mueve el selector a 0 s y a cada cruce predicho y registra
pasajeros y ocupación. No compara con valores esperados: solo registra lo observado. Si la API no puede
procesar, guarda el mensaje del panel y termina con código 1.
"""
import json
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

salida = Path(sys.argv[1])
salida.mkdir(parents=True, exist_ok=True)


def esperar(p):
    p.wait_for_timeout(600)
    p.wait_for_selector('[data-testid="stStatusWidget"]', state="detached", timeout=700000)
    p.wait_for_timeout(900)


def tablas(p):
    """Filas de cada tabla del panel como listas de celdas."""
    resultado = []
    for tabla in p.locator('[data-testid="stDataFrame"]').all():
        encabezado = [c.strip() for c in tabla.locator("thead th").all_inner_texts() if c.strip()]
        celdas = [c.strip() for c in tabla.locator("tbody td").all_inner_texts()]
        ancho = len(encabezado) or 1
        resultado.append([dict(zip(encabezado, celdas[i:i + ancho])) for i in range(0, len(celdas), ancho)])
    return resultado


with sync_playwright() as pw:
    navegador = pw.chromium.launch()
    p = navegador.new_page(viewport={"width": 900, "height": 1300})
    p.goto(os.getenv("PANEL_URL", "http://127.0.0.1:8501"))
    p.wait_for_selector('[data-testid="stMetricValue"]', timeout=30000)
    p.get_by_text("Predicción automática del video de oficina").click()
    esperar(p)
    p.get_by_role("button", name="Procesar clip de oficina (0–6 s)").click()
    esperar(p)
    errores = p.locator('[data-testid="stAlert"]').all_inner_texts()
    p.screenshot(path=str(salida / "01-tras-procesar.png"), full_page=True)
    if not p.locator("video").count():
        (salida / "resultado.json").write_text(json.dumps({"procesado": False, "mensajes": errores},
                                                          ensure_ascii=False, indent=2), encoding="utf-8")
        print("Sin video anotado:", errores)
        sys.exit(1)

    video = p.evaluate("""async () => {
      const v = document.querySelector('video');
      v.muted = true;
      await v.play();
      await new Promise(r => setTimeout(r, 1500));
      return {duracion_s: v.duration, reproducido_s: v.currentTime, error: v.error && v.error.code,
              ancho: v.videoWidth, alto: v.videoHeight};
    }""")
    p.locator("video").screenshot(path=str(salida / "02-video-reproduciendo.png"))
    ejecucion = p.locator('[data-testid="stSelectbox"]').inner_text().split("\n")[-1]
    prediccion, referencia = tablas(p)[:2]

    # El selector usa las marcas exactas de cada evento; se recorre con el teclado.
    deslizador = p.locator('[data-testid="stSlider"] [role="slider"]')
    for _ in range(50):  # vuelve al primer instante; el selector arranca en el último
        antes = p.locator('[data-testid="stSliderThumbValue"]').inner_text()
        deslizador.focus()
        p.keyboard.press("ArrowLeft")
        esperar(p)
        if p.locator('[data-testid="stSliderThumbValue"]').inner_text() == antes:
            break
    estados = []
    for paso in range(20):
        esperar(p)
        segundo = p.locator('[data-testid="stSliderThumbValue"]').inner_text()
        valores = p.locator('[data-testid="stMetricValue"]').all_inner_texts()
        estados.append({"segundo": segundo, "pasajeros": valores[0], "ocupacion": valores[1]})
        p.screenshot(path=str(salida / f"03-ocupacion-{paso:02d}-{segundo.replace(' ', '')}.png"), full_page=True)
        deslizador.focus()
        p.keyboard.press("ArrowRight")
        esperar(p)
        if p.locator('[data-testid="stSliderThumbValue"]').inner_text() == segundo:
            break

    resultado = {"procesado": True, "ejecucion": ejecucion, "video": video, "prediccion": prediccion,
                 "referencia_manual": referencia, "estados": estados, "mensajes": errores}
    (salida / "resultado.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    navegador.close()
