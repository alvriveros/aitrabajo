"""Recorre el panel con Playwright y guarda capturas y valores.
Uso: PANEL_URL=... python recorrer_panel.py CASOS OFICINA_JSON SALIDA"""
import json, os, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

casos, oficina, salida = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
salida.mkdir(parents=True, exist_ok=True)
registro = []

def esperar(p):
    p.wait_for_timeout(700)
    p.wait_for_selector('[data-testid="stStatusWidget"]', state="detached", timeout=15000)
    p.wait_for_timeout(900)

def anotar(p, nombre):
    esperar(p)
    p.screenshot(path=str(salida / f"{nombre}.png"), full_page=True)
    fila = {"captura": f"{nombre}.png",
            "metricas": p.locator('[data-testid="stMetricValue"]').all_inner_texts(),
            "segundo": p.locator('[data-testid="stSliderThumbValue"]').all_inner_texts(),
            "tabla": [c.strip() for c in p.locator('[data-testid="stDataFrame"] table td').all_inner_texts()],
            "nota_parcial": [t for t in p.locator('[data-testid="stCaptionContainer"]').all_inner_texts() if "parcial" in t],
            "grafico": p.locator('[data-testid="stVegaLiteChart"] canvas, [data-testid="stVegaLiteChart"] svg').count(),
            "errores": p.locator('[data-testid="stAlertContentError"]').all_inner_texts(),
            "avisos": p.locator('[data-testid="stAlertContentWarning"]').all_inner_texts()}
    registro.append(fila); print(json.dumps(fila, ensure_ascii=False))

def tecla(p, k, veces=1):
    p.locator('[role="slider"]').focus()
    for _ in range(veces):
        p.keyboard.press(k); esperar(p)

def subir(p, archivo): p.locator('input[type="file"]').set_input_files(str(archivo))
def quitar(p): p.locator('[data-testid="stFileUploaderDeleteBtn"] button').click()
def caso(p, archivo, nombre):
    quitar(p); esperar(p); subir(p, archivo); anotar(p, nombre)

with sync_playwright() as pw:
    p = pw.chromium.launch().new_page(viewport={"width": 900, "height": 1300}, device_scale_factor=1)
    p.goto(os.getenv("PANEL_URL", "http://localhost:8501"))
    p.wait_for_selector('[data-testid="stMetricValue"]', timeout=30000)
    anotar(p, "01-demo-10s")
    tecla(p, "ArrowLeft", 5); anotar(p, "02-demo-5s")
    subir(p, casos / "segunda-parada-22_5.json"); anotar(p, "03-22_5-final")
    tecla(p, "ArrowLeft"); anotar(p, "04-22_5-en-22")
    tecla(p, "ArrowRight")
    capacidad = p.locator('input[type="number"]').first
    capacidad.fill("10"); capacidad.press("Enter"); anotar(p, "05-22_5-capacidad-10")
    caso(p, casos / "nombres-repetidos.json", "06-nombres-repetidos")
    caso(p, casos / "eventos-vacios.json", "07-eventos-vacios")
    caso(p, casos / "una-parada.json", "08-una-parada")
    caso(p, casos / "sobreocupacion.json", "09-sobreocupacion")
    caso(p, casos / "conteo-negativo.json", "10-conteo-negativo")
    caso(p, oficina, "11-oficina-manual")
(salida / "valores.json").write_text(json.dumps(registro, ensure_ascii=False, indent=2), encoding="utf-8")
