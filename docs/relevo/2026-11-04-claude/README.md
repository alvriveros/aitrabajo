# Relevo de Claude · 4 de noviembre de 2026

Tarea: la «Primera tarea para Claude» de [resumen.md](../../../resumen.md), es decir, pruebas de contrato para `POST /ocupacion`.
Rama: `main`, sobre el commit `062742d`. No hice commit; los cambios están en la copia local de Álvaro.

## Qué cambió

- Nuevo: `tests/test_ocupacion.py` (7 pruebas).
- `requirements.txt`: se agregan `pytest==8.4.1` y `httpx==0.28.1`. `TestClient` necesita httpx.
- `resumen.md`: nueva sección «Verificado el 4 de noviembre».
- No toqué `api/main.py` ni la rama `vision`.

## Qué cubre cada prueba (cálculo manual)

| Punto | Prueba | Entrada | Esperado |
|---|---|---|---|
| 1 | `test_ejemplo_coincide_con_calculo_manual` | `docs/demo/recorrido.json` (carga 3, capacidad 20) | P1: 3+2 = 5 (25 %); P2: 5-1 = 4 (20 %). La bajada a los 10 s cae en P2 |
| 2 | `test_cruces_simultaneos_y_parada_vacia` | dos subidas a los 3 s (track 1 y 2), paradas A/B/C | A: 5, B: 5, C: 5, sin avisos |
| 3 | `test_bajada_con_bus_vacio_deja_aviso_aunque_se_recupere` | carga 0, bajada a 1 s, subida a 2 s | pasajeros 0 al final, aviso «Conteo negativo en Parada 1 a los 1 s.» |
| 4 | `test_entradas_invalidas_dan_422[...]` | capacidad 0 / sentido «lateral» / eventos 5 s → 2 s / dos paradas en 0 s | HTTP 422 en los cuatro casos |

## Resultado

7 de 7 pruebas pasan y no apareció ningún defecto. La salida completa está en [pytest.txt](pytest.txt) y el diff de los archivos modificados en [cambios.diff](cambios.diff) (los archivos nuevos no aparecen en el diff).

Las ejecuté en Linux (Python 3.10, fastapi 0.116.1) y no en el `.venv` de Windows. Para repetirlas en Windows:

```
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m pytest tests -v
```

## Pendiente

- Verificación de Windows completada en la `.venv` con Python 3.12.14. Pasaron las 7 pruebas con el mismo aviso de Starlette que en Linux. [Salida completa](pytest-windows.txt).
- Próxima tarea: pasar los eventos reales del primer clip por estas pruebas antes de conectarlos al panel.
