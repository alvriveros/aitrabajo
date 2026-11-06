"""Reproduce el desfase del gráfico (tarea 02) con el panel de Streamlit.

Uso: PANEL_URL=http://127.0.0.1:8502 python reproducir.py RECORRIDO.json SALIDA/
Guarda una captura del gráfico por paso y termina con código 1 si el gráfico
(barra dibujada) no coincide con el indicador de ocupación.
"""
import os
import sys
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

recorrido, salida = sys.argv[1], Path(sys.argv[2])
salida.mkdir(parents=True, exist_ok=True)


def esperar(p):
    p.wait_for_timeout(700)
    p.wait_for_selector('[data-testid="stStatusWidget"]', state="detached", timeout=15000)
    p.wait_for_timeout(1500)


def hay_barra(png):
    """Píxeles azules de una barra con ocupación positiva."""
    im = Image.open(png).convert("RGB")
    px, (w, h) = im.load(), im.size
    return any(px[x, y][2] > 180 and px[x, y][0] < 160 for x in range(0, w, 2) for y in range(0, h, 2))


desacuerdos = 0
with sync_playwright() as pw:
    p = pw.chromium.launch().new_page(viewport={"width": 772, "height": 923})
    p.goto(os.getenv("PANEL_URL", "http://127.0.0.1:8502"))
    p.wait_for_selector('[data-testid="stMetricValue"]', timeout=30000)
    p.locator('input[type="file"]').set_input_files(recorrido)
    esperar(p)
    p.locator('[role="slider"]').focus()
    for tecla, veces, nombre in (("ArrowLeft", 6, "0"), ("ArrowRight", 2, "2"), ("ArrowRight", 1, "2_16"),
                                 ("ArrowRight", 2, "4"), ("ArrowRight", 1, "4_6")):
        for _ in range(veces):
            p.keyboard.press(tecla)
            esperar(p)
        captura = salida / f"grafico-{nombre}.png"
        p.locator('[data-testid="stVegaLiteChart"]').first.screenshot(path=str(captura))
        indicador = p.locator('[data-testid="stMetricValue"]').all_inner_texts()[1]
        barra = hay_barra(captura)
        ok = (indicador != "0 %") == barra
        desacuerdos += not ok
        print(nombre, "indicador", indicador, "barra", "sí" if barra else "no", "" if ok else "DESACUERDO")
print("desacuerdos", desacuerdos)
sys.exit(1 if desacuerdos else 0)
