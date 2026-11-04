# Relevo para Claude · 4 de noviembre de 2026

Álvaro trabaja en `main` y su compañero en `vision`. El cierre interno es el domingo 8 a las 18:00 (Paraguay). Lean [la consigna](contexto.md), [el plan](docs/PLAN.md) y [el arranque en Windows](README.md). La prioridad es integrar el primer clip el jueves 5.

## Punto de partida

- `api/main.py` expone `POST /ocupacion`. Recibe capacidad, carga inicial, paradas y eventos. Devuelve filas con subidas, bajadas, pasajeros y porcentaje, además de avisos si el conteo resulta negativo. El cálculo es independiente para cada solicitud.
- `docs/demo/recorrido.json` es un ejemplo sintético editable. Cada evento tiene segundo, ID de seguimiento y sentido. Los eventos llegan ordenados y pueden compartir segundo. Un cruce justo al comenzar una parada pertenece a esa parada.
- `ui/app.py` consulta la API por HTTP. Se puede cambiar la capacidad, la carga inicial y el segundo del recorrido. El panel representa los cruces ocurridos hasta ese instante. Falta la integración con video, el modelo, la evaluación, Docker y el informe.

Verificación realizada: con la API corriendo y el panel de Streamlit consultándola por HTTP, se movió el selector a los segundos 0, 5 y 10. Se observaron 3, 5 y 4 pasajeros respectivamente (15 %, 25 % y 20 %). La bajada quedó en la segunda parada.

## Primera tarea para Claude

Prepará pruebas de contrato para la API en `tests/test_ocupacion.py`. Usá el JSON de ejemplo como punto de partida y verificá los resultados contra cálculos manuales. Trabajá con Álvaro en su copia actualizada de main y dejá la rama vision al compañero.

1. Con carga 3 y capacidad 20, exigir 5 pasajeros al final de la primera parada y 4 (20 %) al final de la segunda. La bajada del segundo 10 debe aparecer en la segunda.
2. Probar dos cruces simultáneos de personas distintas y una parada sin cruces. Ambos eventos cuentan y la parada vacía conserva la carga.
3. Probar una bajada con el bus vacío: verificar que queda registrada la inconsistencia incluso si una subida posterior recupera la carga.
4. Comprobar que la API responde HTTP 422 a capacidad cero, sentido desconocido, eventos desordenados o inicios de parada repetidos.

Entregá el comando para ejecutar las pruebas y su resultado. Si una prueba descubre un defecto, indicá la entrada, el valor esperado y el obtenido. Después de integrar un cambio, actualizá este resumen con lo verificado y la próxima tarea.

## Verificado el 4 de noviembre

`tests/test_ocupacion.py` cubre los cuatro puntos de la primera tarea (7 pruebas, todas pasan). No apareció ningún defecto en la API. Se agregaron `pytest` y `httpx` a `requirements.txt`. Para ejecutar desde la raíz del repo: `python -m pytest tests -v`.

La ejecución se confirmó en Linux y en la `.venv` de Windows con Python 3.12.14. En ambos entornos pasaron las 7 pruebas con un aviso de obsolescencia de Starlette. [Evidencias](docs/relevo/2026-11-04-claude/README.md).

Próxima tarea: cuando llegue el primer clip, enviar sus eventos reales a `POST /ocupacion` y contrastar los resultados por parada con el conteo manual antes de conectarlos al panel.

## Cuando llegue el primer clip

El compañero aporta el video, la orientación de la línea y los eventos reales con el mismo formato que el ejemplo. Álvaro conecta esa salida al panel y ambos contrastan el contador con una anotación manual. Las cifras de esta demo sintética sirven para probar la integración. Las métricas del informe se calculan con clips reservados para evaluación.
