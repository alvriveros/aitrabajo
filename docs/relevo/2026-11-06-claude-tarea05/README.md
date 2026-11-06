# Devolución · Tarea 05 · Sincronizar las barras con el segundo seleccionado

6 de noviembre de 2026. [Ficha de la tarea](../../tareas/claude/05-actualizacion-grafico.md). Rama `tareas-03-04-panel-informe` (`5c3155a`). Los cambios quedan sin commit.

**Resultado:** corregido y verificado en Linux. En 32 transiciones del recorrido predicho, más 13 estados de otros casos, la barra dibujada y su rótulo coincidieron con la tabla, el indicador y el valor esperado. **Falta verificarlo en Windows** después de reconstruir la imagen.

## Corrección

El componente de gráficos de Streamlit 1.48.1 a veces conservaba en el navegador los valores de una ejecución anterior. Ahora el gráfico se dibuja en el servidor:

- `ui/app.py`: la especificación de Altair (`graficar`) no cambia. La nueva función `svg_del_grafico` la convierte a SVG con `vl-convert-python` usando las mismas filas que alimentan la tabla. El SVG se inserta con `st.markdown(..., unsafe_allow_html=True)` dentro de `<div class="grafico-ocupacion">`. Cada ejecución entrega el dibujo completo, sin componente de gráficos en el navegador.
- `requirements.txt`: `vl-convert-python==1.8.0`, compatible con Altair 5.5 y Vega-Lite 5.20. No necesita red: `render-sin-red.txt` muestra un render dentro del contenedor con `--network none`.
- El ancho del gráfico es fijo (520 px de área de datos) y el SVG se escala a la columna, con un máximo de 720 px.

`st.html` no sirvió: elimina el SVG al sanitizarlo. Diferencias visuales frente al gráfico anterior: colores y tipografía por defecto de Vega-Lite (azul `#4c78a8`, sans serif) y fondo blanco propio, también en tema oscuro. Se conservan la línea y el rótulo del 100 %, los rótulos de valor, la opacidad de la parada parcial, el orden, la numeración y los valores negativos o mayores que 100 %.

## Defecto antes de la corrección

`scripts/reproducir.py`, con salida configurable, contra la imagen sin corregir:

| Instante | Indicador | Barra dibujada |
|---|---|---|
| 2,16 s | 5 % | sin barra (desacuerdo) |
| 4 s | 5 % | sin barra (desacuerdo) |

Capturas en [antes/](antes/). El script terminó con código 1.

## Verificación después de la corrección

`scripts/verificar_grafico.py`, Chromium 153 con Playwright, en una sola sesión del navegador. Para cada estado, barra por barra y en orden:

- **Rótulo dibujado:** texto del SVG en el DOM, que es lo que pinta el navegador, comparado con la tabla.
- **Altura dibujada:** posición real de la barra (`getBoundingClientRect`) convertida a porcentaje con las marcas 0 y 100 del eje, con tolerancia ±1,5.
- **Color en la captura:** píxel del centro de cada barra con altura.
- También: indicador frente a tabla, valor esperado, línea de capacidad en 100, marca parcial solo en la última barra y orden de paradas frente a la tabla.

Cualquier desacuerdo hace terminar el script con código 1.

| Bloque | Estados | Resultado |
|---|---|---|
| Recorrido predicho 0 → 2 → 2,16 → 4 → 4,60 s y vuelta, 4 vueltas | 32 transiciones | Barra y rótulo: 0, 0, 5, 5, 0 % |
| Capacidad 10 a 2,16 s | 1 | 10 % |
| Demo a 10, 0, 5 y 10 s; capacidad 40 | 5 | 25 y 20; 15; 25; 25 y 20; 12,5 y 10 |
| Alternar predicción y demo, dos veces | 4 | 0 % y 25/20 % |
| Nombres repetidos | 1 | `1 · Centro`, `2 · Terminal`, `3 (parcial) · Centro`: 15, 20 y 15 % |
| Sobreocupación | 1 | 150 %, sobre la línea del 100 % |
| Conteo negativo | 1 | −5 %, bajo cero |

45 estados, 0 fallos ([verificacion.txt](verificacion.txt), [despues/resultado.json](despues/resultado.json)). Las capturas representativas están en [despues/capturas/](despues/capturas/).

**Prueba de la prueba:** cambié temporalmente el rótulo para que mostrara pasajeros en vez de porcentaje. El script falló en cada estado afectado ([mutacion.txt](mutacion.txt)). El cambio se revirtió.

Pruebas de la API: 7 passed ([pytest.txt](pytest.txt)).

## Entorno

| Elemento | Valor |
|---|---|
| Sistema | Ubuntu 24.04, espacio de trabajo en la nube de Claude. **No es Windows.** |
| Docker | Engine 29.9.2, Compose 5.7.0, con la base local sustituta `python:3.12-slim` (Python 3.12.3), porque Docker Hub no descarga capas aquí |
| Versiones | streamlit 1.48.1, altair 5.5.0, vl-convert-python 1.8.0 |
| Navegador | Chromium 153 con Playwright, ventana de 900 × 1300 |

## Comandos

```sh
docker compose up --build -d
PANEL_URL=http://127.0.0.1:8502 python scripts/reproducir.py casos/oficina-00-06-prediccion.json antes/
PANEL_URL=http://127.0.0.1:8502 python scripts/verificar_grafico.py casos/oficina-00-06-prediccion.json casos/ despues/
python -m pytest tests -v
docker run --rm --network none aitrabajo python -c "..."   # render sin red
```

Los scripts necesitan `playwright` y `pillow`, que no están en `requirements.txt`.

## Pendientes

1. **Windows:** ejecutar `docker compose up --build -d` y luego `verificar_grafico.py` con la `.venv` (Playwright ya está instalado) o en el navegador. La imagen crece por el paquete `vl-convert-python`.
2. Actualizar la Fig. 2 del informe: el gráfico ahora tiene los colores de Vega-Lite.
3. Siguen aparte la revisión visual del video, la reproducción de la inferencia y la evaluación independiente.
