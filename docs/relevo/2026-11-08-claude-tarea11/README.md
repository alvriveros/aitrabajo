# Tarea 11 · Detectores más grandes sin entrenar · devolución (8 nov., madrugada)

> **Estado vigente (agregado en la tarea 12, 8 nov.).**
> - **Prueba final:** se ejecutó una vez (ver *Prueba final · resultado*, al final). **La API no cambia.**
> - **Videos ya usados:** Kaggle y PAMELA A sirvieron para seleccionar, y `youtube-bus-real` se consumió. No vuelve a usarse para elegir parámetros ni como prueba ciega.
> - **Herramientas:** los scripts de esta carpeta se corrigieron en la tarea 12. Las versiones que produjeron esta evidencia están en `../2026-11-08-claude-tarea12/historico/`.
> - **Secciones históricas:** las que dicen «pendiente» o «reservado» describen el estado antes de la prueba final.

Rama `integracion-video`, sin commit, push ni merge. No se cambió la API, el panel ni Docker, y no se entrenó nada. Se siguió el [prerregistro](preregistro.md), escrito antes de ejecutar.

## Por qué no se entrenó con más videos

Álvaro pidió entrenar con todos los videos. Antes había que anotar cajas de persona en Kaggle y PAMELA:

- Con `yolo11n` como propuesta, faltaban muchas personas y aparecían cajas duplicadas.
- Con `yolo11x`, en PAMELA (352×288) seguían sin detectarse unas 6 de cada 10 personas.

Habría que dibujar a ojo unas 450 cajas. Entrenar con personas sin caja le enseña al modelo a ignorarlas. Álvaro aceptó primero probar detectores más grandes sin entrenar.

## Resultados

Contenedor Linux de Claude, CPU. Tolerancia ±1 s. Cada celda es TP / FP / FN. Las referencias son de Claude y **siguen pendientes de revisión humana**.

| Configuración | PAMELA A, bajadas | PAMELA A, subidas | Kaggle, subidas | Kaggle, bajadas | **Errores totales** (FN + FP) | Error de conteo | FPS en CPU |
|---|---|---|---|---|---|---|---|
| yolo11n por defecto | 1 / 0 / 27 | 0 / 1 / 0 | 1 / 0 / 5 | 0 / 1 / 0 | 34 | 34 | 13 / 11 |
| **yolo11n calibrado (API actual)** | 10 / 0 / 18 | 0 / 1 / 0 | 5 / 4 / 1 | 0 / 4 / 0 | 28 | 26 | 13 / 11 |
| yolo11l por defecto | 2 / 0 / 26 | 0 / 0 / 0 | 3 / 0 / 3 | 0 / 1 / 0 | 30 | 30 | 1,5 |
| **yolo11l calibrado** | 13 / 0 / 15 | 0 / 2 / 0 | **6 / 2 / 0** | 0 / 2 / 0 | **21** | **21** | 1,5 |
| yolo11x por defecto | 2 / 0 / 26 | 0 / 0 / 0 | 2 / 0 / 4 | 0 / 0 / 0 | 30 | 30 | 0,8 |
| yolo11x calibrado | 13 / 0 / 15 | 0 / 6 / 0 | 5 / 2 / 1 | 0 / 2 / 0 | 26 | 24 | 0,8 |

Con `yolo11n`, los resultados coinciden con los de la tarea 09 en Linux, así que el arnés es consistente. En oficina, solo de diagnóstico, se ejecutó `yolo11n` con los dos rastreadores, con los mismos resultados de antes. `yolo11l` y `yolo11x` no se ejecutaron en oficina: se cortaron por tiempo (eran una hora y media más), lo que no afecta la elección.

**Candidato según el criterio prerregistrado: `yolo11l` con el rastreador calibrado.** Suma 21 errores contra 28 de la API actual.

## Lectura

- **Mejora, pero poco:**
  - en Kaggle cuenta las 6 subidas, con 4 eventos falsos en lugar de 8;
  - en PAMELA cuenta 13 de 28 bajadas en lugar de 10, así que **todavía pierde 15**.
- **`yolo11x` no aporta sobre `yolo11l`:** cuenta lo mismo y agrega más falsos, como 6 subidas falsas en PAMELA.
- **Con el rastreador por defecto, los tres modelos casi no cuentan nada.** Los umbrales bajos del calibrado siguen siendo necesarios en estas escenas.
- **Velocidad:** en CPU, `yolo11l` va a 1,5 FPS, lejos de tiempo real. En la RTX 2050 de Álvaro debería ser bastante más rápido, pero no está medido.
- **Alcance:** Kaggle y PAMELA son dos clips cortos, con referencia de Claude. Ya se usaron con `yolo11n`, y aquí sirvieron para **elegir**. No son una prueba final.

## Prueba final: pendiente *(histórico: estado antes de ejecutarla)*

`youtube-bus-real-0y08Jtqtkys.mp4`, de 9 min 13 s, 586×480, sigue reservado: **no se ejecutó ningún modelo sobre él**.

- **Lo preparado:** SHA-256 `15a9d7c3…`, 25 FPS y 13.836 cuadros. Se leyó el contador comercial sobreimpreso: las entradas pasan de 97 a 111 (14 subidas) y las salidas de 31 a 33 (2 bajadas), con los momentos aproximados de cada cambio (36, 42, 60, 114–120, 144, 170, 180, 192, 210, 366 y 372 s). Es un **control**, no la referencia.
- **Por qué no se anotó:** varias personas se quedan paradas decenas de segundos sobre la escalera, justo en la línea de conteo, y el texto del contador tapa la zona de la calle. Fijar a ojo el instante de cada cruce no sería confiable.
- **Lo que hace falta:** que una persona anote los cruces, por ejemplo viendo el video en la zona de 30 a 215 s y de 360 a 375 s. El criterio está en [prerregistro-final.md](prerregistro-final.md).
- **Después:** ejecutar una vez `prueba-final.ps1` en la GPU. Compara la API actual (`yolo11n` calibrado) con el candidato (`yolo11l` calibrado) y no arranca si falta la referencia.

## Conclusión *(histórico: antes de la prueba final)*

- **Un detector más grande ayuda algo, pero no lo suficiente** para afirmar que el sistema cuenta bien: sigue perdiendo más de la mitad de las bajadas de PAMELA.
- **`yolo11l` calibrado queda como candidato,** a confirmar en la prueba final con una referencia hecha por una persona. No se recomienda cambiar la API todavía.
- **El cuello de botella son los datos:** un detector entrenado con escenas cenitales variadas y bien anotadas, como las cabezas oficiales de PAMELA si llegan las credenciales, es el siguiente paso con más probabilidad de mejora real.

## Archivos

- `preregistro.md` y `evaluar_detectores.py`, el script de esta tarea. El script ahora acepta `--rastreadores` y la escena `final`, que no se ejecuta por defecto.
- `prerregistro-final.md` y `prueba-final.ps1`, para la prueba final.
- `linux/`: eventos y métricas por escena y configuración, resúmenes y `resultados.txt`.
- **Videos anotados** en el contenedor de Claude (`runs/evaluacion/tarea11-linux/`, 406 MB): no se copiaron. Se regeneran con el script.
- **Pesos** `yolo11l.pt` y `yolo11x.pt`, de Ultralytics v8.4.0, fuera de Git. En la máquina de Álvaro hay que descargarlos para repetir (hashes en el prerregistro).

## Prueba final · resultado (8 nov., 04:37)

Referencia de Álvaro, a mano con `anotar_cruces.py`, antes de ejecutar los modelos: 15 subidas y 3 bajadas (el contador comercial marca 14 y 2). La ejecución fue una sola vez, en la RTX 2050, y la salida está en `final-windows/`.

| Configuración | Subidas TP / FP / FN | Bajadas TP / FP / FN | Errores | FPS en GPU |
|---|---|---|---|---|
| `yolo11n` calibrado (API) | 5 / 0 / 10 | 1 / 1 / 2 | **13** | 65,9 |
| `yolo11l` calibrado | 11 / 7 / 4 | 1 / 5 / 2 | 18 | 23,9 |

**Decisión prerregistrada: la API no cambia.** `yolo11l` comete más errores (18 contra 13), aunque supera los 10 FPS.

**Diagnóstico.** Esto es posterior a la prueba, así que no cambia la decisión:

- **Los dos modelos fallan de forma distinta:**
  - `yolo11n` casi no inventa eventos, pero pierde 2 de cada 3 subidas;
  - `yolo11l` encuentra 12 de 18 cruces, pero cuenta dos o tres veces a la misma persona (33,3 y 34,1 s; 158,2, 158,8 y 159,8 s; dos veces 189,5 s; 149,4 y 149,6 s).
- **Algunos falsos de `yolo11l` caen justo fuera de la tolerancia de ±1 s** (170,4 contra 171,96 s, y 173,7 contra 174,96 s).
- **El cuello de botella del candidato ya no es la detección, sino el rastreo:** pierde el identificador y vuelve a contar a la misma persona. Un siguiente paso posible sería no contar dos cruces en el mismo sentido en menos de unos 1,5 s en la misma zona. Habría que elegir ese umbral en Kaggle y PAMELA, nunca en este video, y validarlo con otra prueba ciega.
  - *Aclaración posterior (tarea 12): esto se afirmó de más. La clasificación de la tarea 12 muestra también errores de tiempo, oscilaciones del mismo ID y omisiones puras. No está demostrado que todo sea rastreo.*
- **Ninguna configuración cuenta bien:** la API actual registra 6 de 18 cruces en un bus real.
