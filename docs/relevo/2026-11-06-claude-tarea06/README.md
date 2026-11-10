# Devolución · Tarea 06 · Gráfico en Windows y figura 2

6 de noviembre de 2026. [Ficha de la tarea](../../tareas/claude/06-cierre-grafico-windows.md). Rama `tareas-03-04-panel-informe` (`5c3155a`). Los cambios quedan sin commit.

**Resultado:** la figura 2 se actualizó y se lee a ancho de columna, y el PDF sigue en 3 páginas. **Windows sigue pendiente:** no tengo terminal en Windows. A las 19:30, el panel en 8502 todavía mostraba el gráfico anterior, sin reconstruir.

## Windows · pendiente para Álvaro

Desde PowerShell en la raíz, con Docker Desktop iniciado:

```powershell
docker compose up --build -d
docker compose ps
$t05 = 'docs/relevo/2026-11-06-claude-tarea05'
$t06 = 'docs/relevo/2026-11-06-claude-tarea06'
$env:PANEL_URL = 'http://127.0.0.1:8502'
$env:PYTHONUTF8 = '1'
.\.venv\Scripts\python.exe "$t05/scripts/verificar_grafico.py" "$t05/casos/oficina-00-06-prediccion.json" "$t05/casos" "$t06/windows"
echo "salida: $LASTEXITCODE"
```

Esperado: salida 0 y `windows/resultado.json` con 45 estados, 32 transiciones de la predicción y `"fallos": []`. Después revisar `windows/capturas/003-pred-v1-2.16s.png`: barra y rótulo en 5 %. Si la `.venv` no tiene `vl-convert-python`, no importa: el script solo usa el navegador.

## Cambio adicional en el gráfico

Con el gráfico de la tarea 05, el texto de la figura quedaba en unos 4 pt a ancho de columna. Álvaro eligió agrandar la letra del panel. Cambios en `ui/app.py`, dentro de `graficar`:

- Letra de 15 px (`LETRA`) en ejes, títulos, rótulos de barras y "Capacidad 100 %".
- Área de datos de 380 × 280 px, antes 520 × 340, y margen derecho de 150 px para el rótulo de capacidad.
- `labelLimit` de 220 a 400 px. Con la letra grande, la primera verificación detectó que el nombre "Puerta de oficina · 0-6 s" se cortaba con "…". Se corrigió y se volvió a verificar.

## Verificación en Linux

Ubuntu 24.04, Docker 29.9.2 con la base local sustituta `python:3.12-slim`, Chromium 153 con Playwright.

| Comprobación | Resultado |
|---|---|
| `verificar_grafico.py` (tarea 05), con el código final | 45 estados, 32 transiciones, 0 fallos, salida 0 ([verificacion-linux.txt](verificacion-linux.txt), [linux/resultado.json](linux/resultado.json)) |
| Primera corrida con letra grande | 35 fallos, todos por el nombre cortado; corregidos con `labelLimit` |
| `pytest tests -v` | 7 passed ([pytest.txt](pytest.txt)) |
| Captura a 2,16 s | Barra y rótulo en 5 %, nombre completo ([linux/capturas/003-pred-v1-2.16s.png](linux/capturas/003-pred-v1-2.16s.png)) |

Después de esa verificación solo cambié un comentario en `ui/app.py`, de "unos 7 pt" a "unos 6 pt". La copia probada y la de Álvaro tienen el mismo sha256: `e8b042b0…`.

## Figura 2

- Captura del SVG del panel corregido, sin archivo cargado: demo sintética, capacidad 20, carga inicial 3, 10 s, 4 pasajeros y 20 %. Tomada a escala 3 y recortada al dibujo ([grafico-demo.png](grafico-demo.png)).
- Conserva los ejes, "1 · Parada 1", "2 (parcial) · Parada 2", 25 %, 20 % y la línea "Capacidad 100 %".
- Copiada a `docs/informe/grafico-demo.png`. `informe.tex` no cambió.
- Tamaño de la letra en la columna: unos 6,2 pt, antes unos 4 pt. Revisada a 300 ppp ([revision-pdf/figura2-300dpi-2.png](revision-pdf/figura2-300dpi-2.png)): se leen ejes, nombres, valores y rótulo de capacidad.

## PDF

```sh
cd docs/informe
pdflatex informe.tex && bibtex informe && pdflatex informe.tex && pdflatex informe.tex
```

3 páginas A4, sin desbordes, resumen de 138 palabras. Páginas renderizadas en [revision-pdf/](revision-pdf/). Compilado en Linux con TeX Live 2023; no se compiló en Windows.

## Archivos modificados

- `ui/app.py`: letra, tamaño y `labelLimit` del gráfico.
- `docs/informe/grafico-demo.png` y `docs/informe/informe-borrador.pdf`.
- `resumen.md`.
- Nuevo: esta carpeta.

## Pendientes

1. Ejecutar el bloque de PowerShell en Windows y guardar `windows/`.
2. Los demás pendientes del informe y de visión siguen sin cambios.
