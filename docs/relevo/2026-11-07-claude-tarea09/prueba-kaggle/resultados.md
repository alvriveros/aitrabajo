# Prueba independiente · `kaggle-people-boarding-bus.mp4` · resultados

Se ejecutó **una sola vez** lo que fija el [prerregistro](preregistro.md), sin cambiar recorte, línea ni parámetros después de ver los resultados.

- **Referencia:** [`data/annotations/kaggle-people-boarding-bus-cruces.json`](../../../../data/annotations/kaggle-people-boarding-bus-cruces.json), con 6 subidas y 0 bajadas.
  - **Quién la hizo:** **Claude**, a pedido de Álvaro, mirando los cuadros antes de ejecutar ningún modelo. **Falta la revisión de una persona.**
  - **Precisión:** los tiempos tienen unos ±0,4 s.
  - **Contador comercial:** el que trae el video marca 5 subidas.
- **Entorno:** contenedor Linux x86_64 de Claude, Python 3.12.3, ultralytics 8.4.203 y torch 2.15.0. En el clip de oficina, este entorno dio los mismos eventos que Windows.
- **Comando:**
  ```sh
  python docs/relevo/2026-11-07-claude-tarea09/prueba-kaggle/evaluar_kaggle.py <SALIDA>
  ```
- **Archivos:** [`linux/`](linux/) tiene eventos, configuración, métricas y `resumen.json`. Los videos anotados quedan en `runs/evaluacion/linux-x86_64/`, fuera de Git.

## Resultados (tolerancia ±1 s)

| Configuración | Subidas TP / FP / FN | Bajadas TP / FP / FN | Eventos predichos | Saldo final | FPS |
|---|---|---|---|---|---|
| Referencia | 6 | 0 | 6 | +6 | — |
| Base, ByteTrack por defecto | **1 / 0 / 5** | 0 / **1** / 0 | 2 | 0 | 13,7 |
| Base calibrado (configuración de la API) | **5 / 4 / 1** | 0 / **4** / 0 | 13 | **+5** | 13,5 |
| Ajustado (por defecto y calibrado) | pendiente: faltan los pesos | | | | |

Los FPS se midieron con el recorte de 840×1080, con video anotado, en CPU.

## Lectura

- **El base por defecto casi no detecta:** cuenta 1 de 6 subidas y agrega una bajada falsa.
- **El base calibrado detecta 5 de 6 subidas,** y omite la de 21,4 s, **pero inventa 8 eventos:**
  - 4 subidas extra: 15,0, 15,32, 25,76 y 25,92 s.
  - 4 bajadas falsas: 14,68, 14,92, 26,48 y 27,72 s.
  - Los extra vienen de tracks que «cruzan» varias veces. El track 7 da subida, bajada y subida; el 37, lo mismo; el 63, subida, bajada, subida y bajada.
- **El saldo engaña.** El calibrado termina con +5 pasajeros, casi igual a los +6 reales, pero sumando 14 errores entre aciertos falsos y omisiones. Por eso se informan los errores por sentido y no solo el saldo.
- **Lo que se ve en el video anotado:** en los momentos de amontonamiento (14,6–15,4 s y 26,4–27,8 s) aparecen cajas grandes que abarcan a dos personas o casi todo el recorte, y su centro salta de un lado al otro de la línea. Es compatible con dos cosas:
  - los umbrales bajos de la configuración calibrada (`conf 0.05`), que aceptan cajas de mala calidad;
  - el margen de 5 px, calibrado para un recorte de 176 px de alto y que aquí, con 1080 px, es una banda casi nula alrededor de la línea.

  Son **hipótesis**: no se probaron cambios, porque esta toma es de prueba.

## Alcance

- **Medición:** es un solo video de 60 s con 6 subidas, la referencia es de Claude y no hay bajadas reales. Con eso solo se puede decir que **en una escena nueva y concurrida, la configuración calibrada sobre la oficina no se transfiere bien:** cuenta casi todas las subidas, pero inventa tantos eventos como acierta.
- **Generalización:** no alcanza para afirmar nada general.
- **Bajadas:** quedan sin medir, salvo los falsos positivos.
- **Sin cambios:** nada de esto modifica la configuración de la API.

## Pendientes

1. Que una persona revise la anotación: tiempos de las 6 subidas y ausencia de bajadas.
2. Pesos ajustados del compañero, para correr `--ajustado` con la misma referencia.
3. Si se ajusta el margen o el umbral para escenas de alta resolución, elegirlo con **otro** video de validación y volver a probar en una toma nueva. No se puede ajustar sobre esta.
