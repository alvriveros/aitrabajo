# 01 · Probar otro recorrido desde el panel

**Objetivo.** Que Álvaro pueda abrir un JSON desde Streamlit y revisar la ocupación a lo largo de ese recorrido. El punto de entrada es `ui/app.py`. El contrato vigente está en `api/main.py` y hay un ejemplo válido en `docs/demo/recorrido.json`.

- Conservá la demo al abrir el panel y permití seleccionar un archivo con capacidad, carga inicial, paradas y eventos. Al cambiar de archivo, inicializá los controles con los valores del recorrido elegido.
- Ajustá el selector de tiempo para incluir la última parada y el último evento, aun si ocurre después de los 15 s o en una fracción de segundo. Incluí recorridos sin eventos.
- Validá el recorrido completo antes de filtrarlo por tiempo. Ante JSON ilegible o datos inválidos, mostrá qué debe corregirse y permití cargar otro archivo. Reutilizá el contrato de la API y mantené allí el cálculo de ocupación.

**Comprobación manual.** En una copia del ejemplo, cambiá el inicio de la segunda parada y la bajada a 22,5 s (`22.5` en JSON). A los 22 s deben verse 5 pasajeros y 25 %. Al llegar a 22,5 s deben verse 4 pasajeros y 20 %, con la bajada en la segunda parada. Al volver a la demo original, la bajada debe volver al segundo 10. Comprobá también una lista de eventos vacía y un archivo inválido.

**Entrega.** Registrá los valores observados en el panel y ejecutá `python -m pytest tests -v` desde la raíz. Indicá qué comprobaste manualmente y qué cubren las pruebas automatizadas.
