"""Recorre el panel con Playwright y guarda capturas y valores. Uso: python recorrer_panel.py CASOS SALIDA"""
import json, os, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

casos, salida = Path(sys.argv[1]), Path(sys.argv[2])
salida.mkdir(parents=True, exist_ok=True)
registro = []

def esperar(p):
    p.wait_for_timeout(600)
    p.wait_for_selector('[data-testid="stStatusWidget"]', state="detached", timeout=15000)
    p.wait_for_timeout(600)

def anotar(p, nombre):
    esperar(p)
    p.screenshot(path=str(salida / f"{nombre}.png"), full_page=True)
    fila = {"captura": f"{nombre}.png",
            "metricas": p.locator('[data-testid="stMetricValue"]').all_inner_texts(),
            "segundo": p.locator('[data-testid="stSliderThumbValue"]').all_inner_texts(),
            "controles": [i.input_value() for i in p.locator('input[type="number"]').all()],
            "errores": p.locator('[data-testid="stAlertContentError"]').all_inner_texts(),
            "avisos": p.locator('[data-testid="stAlertContentWarning"]').all_inner_texts()}
    registro.append(fila); print(json.dumps(fila, ensure_ascii=False))

def tecla(p, k, veces=1):
    p.locator('[role="slider"]').focus()
    for _ in range(veces):
        p.keyboard.press(k); esperar(p)

def subir(p, archivo):
    p.locator('input[type="file"]').set_input_files(str(casos / archivo))

def quitar(p):
    p.locator('[data-testid="stFileUploaderDeleteBtn"] button').click()

with sync_playwright() as pw:
    p = pw.chromium.launch().new_page(viewport={"width": 900, "height": 1200}, device_scale_factor=1)
    p.goto(os.getenv("PANEL_URL", "http://localhost:8501")); p.wait_for_selector('[data-testid="stMetricValue"]', timeout=30000)
    anotar(p, "01-demo-final")
    subir(p, "segunda-parada-22_5.json"); anotar(p, "02-22_5-final")
    tecla(p, "ArrowLeft"); anotar(p, "03-22_5-en-22")
    tecla(p, "ArrowRight"); anotar(p, "04-22_5-vuelve-a-22_5")
    quitar(p); anotar(p, "05-demo-de-nuevo")
    tecla(p, "ArrowLeft", 15); anotar(p, "06-demo-en-0")
    capacidad = p.locator('input[type="number"]').first
    capacidad.fill("10"); capacidad.press("Enter"); anotar(p, "07-demo-capacidad-10")
    subir(p, "sin-eventos.json"); anotar(p, "08-sin-eventos-final")
    tecla(p, "ArrowLeft", 15); anotar(p, "09-sin-eventos-en-0")
    quitar(p); subir(p, "json-ilegible.json"); anotar(p, "10-json-ilegible")
    quitar(p); subir(p, "datos-invalidos.json"); anotar(p, "11-datos-invalidos")
    quitar(p); subir(p, "eventos-desordenados.json"); anotar(p, "12-eventos-desordenados")
    quitar(p); subir(p, "una-parada-sin-eventos.json"); anotar(p, "13-una-parada-sin-eventos")
    quitar(p); subir(p, "segunda-parada-22_5.json"); anotar(p, "14-otro-archivo-tras-error")

(salida / "valores.json").write_text(json.dumps(registro, ensure_ascii=False, indent=2), encoding="utf-8")
