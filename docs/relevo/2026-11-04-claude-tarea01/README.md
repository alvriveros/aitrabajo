# Relevo de Claude · Tarea 01 · 4 de noviembre de 2026

Tarea: [01 · Probar otro recorrido desde el panel](../../tareas/claude/01-cargar-recorrido.md). Se hizo sobre `main` en el commit `2815409`. No hice commit; los cambios quedan para que Álvaro los revise.
La tarea 02 sigue pendiente hasta que estén el clip, la salida de visión y el conteo manual.

## Archivos cambiados

- `ui/app.py` (único archivo de código). Diff en [cambios.diff](cambios.diff).
  - Selector de archivo JSON. Sin archivo se usa `docs/demo/recorrido.json`.
  - Al cambiar de archivo, la capacidad, la carga y el selector toman los valores del recorrido nuevo, porque sus claves incluyen el `file_id` del archivo.
  - El selector de tiempo recorre los segundos enteros desde 0 hasta el último instante, más el inicio exacto de cada parada y de cada evento (por ejemplo 4.2 y 22.5). Arranca en el final. Con un solo instante (una parada en 0 y sin eventos) no se muestra selector.
  - Validación: primero se envía el recorrido completo a `POST /ocupacion`. Si la API responde 422, el panel lista los problemas y se detiene, pero el selector de archivo sigue disponible. El JSON ilegible se informa antes de consultar la API. No se duplicaron reglas: el contrato y el cálculo siguen solo en `api/main.py`.
- Nuevo: esta carpeta, con los casos de prueba en `casos/`, las capturas, los valores observados y el script que recorre el panel.
- Sin cambios: `api/main.py`, `tests/`, `requirements.txt`, `docs/demo/recorrido.json`.

## Entorno

- **Pruebas automatizadas:** Linux (la VM de Cowork en la máquina de Álvaro), Python 3.10.12, fastapi 0.116.1, pytest 8.4.1 y httpx 0.28.1.
- **Comprobación del panel:** contenedor Linux con las mismas versiones de `requirements.txt` (streamlit 1.48.1, uvicorn 0.35.0). Se levantó `uvicorn api.main:app --port 8000` y `streamlit run ui/app.py`, y se recorrió el panel con Chromium y Playwright ([recorrer_panel.py](recorrer_panel.py)). Así se ejercitan la carga real del archivo, el teclado sobre el selector y la consulta HTTP a la API.
- **Windows (verificación posterior).** En la .venv del proyecto pasaron las 7 pruebas de la API. Con Playwright 1.58.0 y Chromium, los 14 registros del navegador coincidieron campo por campo con los de Linux. [Valores de Windows](valores-windows.json).

## Pruebas automatizadas

```
python -m pytest tests -v
```

Resultado: 7 passed (salida completa en [pytest.txt](pytest.txt)). Cubren solo el contrato de la API, es decir, el cálculo por parada, los avisos y los 422. No cubren el panel.

## Comprobación manual del panel

Todos los valores están en [capturas/valores.json](capturas/valores.json) y cada fila tiene su captura.

| # | Acción | Observado | Esperado |
|---|---|---|---|
| 01 | Abrir el panel | demo, selector en 10 s, 4 pasajeros, 20 % | ✔ |
| 02 | Cargar [segunda-parada-22_5.json](casos/segunda-parada-22_5.json) | selector en 22.5 s, 4 pasajeros, 20 % | ✔ |
| 03 | Mover a 22 s | 5 pasajeros, 25 %, solo Parada 1 | ✔ |
| 04 | Volver a 22.5 s | 4 pasajeros, 20 %, bajada en Parada 2 | ✔ |
| 05 | Quitar el archivo (volver a la demo) | selector en 10 s, bajada en Parada 2 con 4 pasajeros | ✔ |
| 06 | Demo a 0 s | 3 pasajeros, 15 % | ✔ |
| 07 | Demo con capacidad 10 | 3 pasajeros, 30 % | ✔ |
| 08 | Cargar [sin-eventos.json](casos/sin-eventos.json) (capacidad 30, carga 6) | los controles pasan de 10/3 a 30/6, selector en 10 s, 6 pasajeros, 20 % | ✔ |
| 09 | Sin eventos a 0 s | 6 pasajeros, 20 % | ✔ |
| 10 | Cargar [json-ilegible.json](casos/json-ilegible.json) | «No se pudo leer el archivo como JSON (…line 2 column 1…). Corregilo o cargá otro.» | ✔ |
| 11 | Cargar [datos-invalidos.json](casos/datos-invalidos.json) | lista con «capacidad: Input should be greater than 0» y «eventos.0.sentido: Input should be 'subida' or 'bajada'» | ✔ |
| 12 | Cargar [eventos-desordenados.json](casos/eventos-desordenados.json) | «Los eventos deben estar en orden temporal.» | ✔ |
| 13 | Cargar [una-parada-sin-eventos.json](casos/una-parada-sin-eventos.json) | sin selector, 3 pasajeros, 15 % | ✔ |
| 14 | Cargar un archivo válido después de un error | panel normal, 22.5 s, 4 pasajeros, 20 % | ✔ |

## Diferencias observadas

- Ningún resultado se apartó de lo esperado.
- Comportamiento a tener en cuenta:
  - Los mensajes de validación de Pydantic llegan en inglés («Input should be…»). Los de la API propia llegan en español.
  - Si se edita la capacidad y después se cambia de archivo, el valor editado se pierde y se toma el del archivo nuevo. Eso es lo que pide la ficha.
  - Streamlit no permite volver a cargar el mismo archivo ya seleccionado sin quitarlo antes.

## Pendientes

- En la revisión se probaron también un evento a mil millones de segundos y un número no finito. El selector conserva los instantes de eventos y paradas y espacia las marcas intermedias en recorridos largos. El panel informa el número no finito antes de enviar el JSON.
- No hay prueba automatizada del panel. Para repetir esta comprobación se puede correr [recorrer_panel.py](recorrer_panel.py) con la API y Streamlit levantados (necesita `playwright` y Chromium, que no están en `requirements.txt`).
- Tarea 02: esperar el clip, la orientación de la línea, los eventos de visión y el conteo manual.
