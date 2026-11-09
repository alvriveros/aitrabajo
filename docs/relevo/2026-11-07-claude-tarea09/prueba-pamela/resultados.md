# Prueba independiente · PAMELA-UANDES `A_d800mm_sample` · resultados

Se ejecutó **una sola vez** lo que fija el [prerregistro](preregistro.md).

- **Referencia:** [`data/annotations/pamela-A-cruces.json`](../../../../data/annotations/pamela-A-cruces.json), con 28 bajadas y 0 subidas.
  - **Quién la hizo:** Claude, antes de ejecutar ningún modelo. **Falta la revisión de una persona.**
  - **Precisión:** ±0,4 s.
  - **No es la referencia oficial** del dataset; ya se pidió acceso a ella.
- **Entorno:** contenedor Linux x86_64 de Claude, Python 3.12.3, ultralytics 8.4.203 y torch 2.15.0.
- **Comando:**
  ```sh
  python docs/relevo/2026-11-07-claude-tarea09/prueba-pamela/evaluar_pamela.py <SALIDA>
  ```
- **Archivos:** [`linux/`](linux/). Los videos anotados quedan en `runs/evaluacion/`, fuera de Git.

## Resultados (tolerancia ±1 s)

| Configuración | Bajadas TP / FP / FN | Subidas TP / FP / FN | Eventos | FPS |
|---|---|---|---|---|
| Referencia | 28 | 0 | 28 | — |
| Base, ByteTrack por defecto | **1 / 0 / 27** | 0 / 1 / 0 | 2 | 15,3 |
| Base calibrado (configuración de la API) | **10 / 0 / 18** | 0 / 1 / 0 | 11 | 16,1 |
| Ajustado | pendiente: faltan los pesos | | | |

Los FPS se midieron con el recorte de 160×224, con video anotado, en CPU.

## Lectura

- **Primera medición de bajadas en una escena nueva.** El base calibrado cuenta **10 de 28**. No inventa bajadas, pero omite 18.
  - Agrega una subida falsa a 2,44 s: el track 6 da bajada y enseguida subida.
  - Sin calibrar, el modelo base casi no detecta nada: 1 de 28.
- **El error dominante cambia con la escena.**
  - En Kaggle, a 1080p y con amontonamiento, sobraban eventos.
  - Acá, a 352×288 y con un flujo continuo de personas por una puerta angosta, faltan: el sistema pierde a la mayoría.
- **Sin pasajeros extra en el saldo:** el calibrado termina con 10 bajadas contra 28. Aquí el saldo sí muestra la omisión, pero no la subida falsa.
- **No se diagnosticó la causa.** Las omisiones pueden venir de detecciones débiles a baja resolución, de la vista cenital, de personas que pasan pegadas o de cortes de ID cerca de la línea. Revisarlo exigiría mirar el video anotado y **no se ajustó nada**: esta toma es de prueba.

## Alcance

- **Medición:** es una muestra de 30 s de una sola fuente, en laboratorio, con un vagón de tren y no un bus, y con referencia de Claude.
- **Lo que sí suma:** junto con Kaggle muestra que la configuración calibrada sobre la oficina no se transfiere bien a escenas nuevas, en un caso por exceso de eventos y en el otro por falta.
- **Ajustado:** queda pendiente hasta tener los pesos.
- **Referencia oficial:** si llega el acceso a PAMELA-UANDES, se repite con su referencia y con los videos de prueba completos (R5 a R8).
