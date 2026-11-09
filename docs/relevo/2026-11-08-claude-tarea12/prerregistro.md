# Tarea 12 · Prerregistro de la supresión temporal de duplicados

Escrito el 8 nov., alrededor de las 05:10, **antes de calcular ningún resultado con filtro**.

## Qué se sabía al escribirlo

- **Tarea 11:** se conocen los eventos sin filtro de Kaggle y PAMELA A y sus métricas.
- **Prueba final de la tarea 11:** también se conocen sus eventos. Ahí surgió el umbral de 1,5 s: es una **hipótesis posterior a ver esa prueba**, no una predicción previa.
- **Contra el filtro:** Kaggle tiene subidas a 13,2 y 14,4 s. PAMELA A tiene dos bajadas a 19,8 s y muchas otras separadas por menos de 1,5 s. Un filtro global puede borrar pasajeros reales.

## Datos

- **Solo Kaggle y PAMELA A.** No se usan oficina ni `youtube-bus-real` (consumido) para elegir.
- **Eventos ya guardados en Linux:** `tarea11/linux/{kaggle,pamela-A}/eventos/{yolo11n,yolo11l}-calibrado.json`. No se repite ninguna inferencia.
- **Referencias:** las originales de Claude, `kaggle-people-boarding-bus-cruces.json` y `pamela-A-cruces.json`, **sin revisión humana**. Por eso todo resultado es **exploratorio** y la elección definitiva queda pendiente. Si Álvaro revisa las referencias, se guardan en archivos nuevos y se recalcula con el mismo script y la misma regla, sin cambiar nada más.

## Regla (una sola variante, fijada ahora)

Para cada sentido por separado:

1. Ordenar los eventos de ese sentido por `tiempo_s`. Los empates se mantienen en el orden original del archivo.
2. Aceptar el primero.
3. Para cada evento siguiente, calcular `d = tiempo_s − tiempo del último evento ACEPTADO de ese sentido`.
   - Si `d < u`, el evento se **descarta**: la condición es estricta, así que con `d = u` el evento se conserva.
   - Si no, se acepta.
4. Se conserva siempre el evento más temprano.

Los sentidos no interactúan: una subida nunca suprime una bajada. Con `u = 0` no se descarta nada, porque `d ≥ 0`. Los eventos descartados se guardan con el evento que los suprimió.

La distancia se mide desde el último **aceptado** y no desde el último observado. Así, una cadena larga de eventos cercanos no se borra entera: con `u = 1,5` y eventos a 0, 1, 2 y 3 s, quedan 0 y 2.

**Límite.** El filtro usa solo tiempo y sentido; el `track_id` no interviene. **No es un filtro espacial ni identifica a la misma persona.**

## Umbrales (lista cerrada)

`u ∈ {0; 0,5; 1,0; 1,5}` s. No se agregan otros después de medir.

## Medición

- **Evaluación:** `evaluation.evaluate.evaluar` con tolerancia ±1 s, la misma de siempre.
- **Por escena y sentido:** TP, FP, FN y error absoluto de conteo.
- **Errores totales:** FN + FP sumados en Kaggle y PAMELA A.
- **Comparación:** cada variante se compara con su mismo detector con `u = 0` y con la API actual (`yolo11n` calibrado, `u = 0`).

**Diagnóstico, que no decide nada:** cuántos eventos de la propia referencia borraría cada `u` si se le aplicara la regla. Es la cota de cuántos pasajeros reales puede quitar el filtro.

## Criterio de elección

1. **Condición:** la variante no puede tener **más omisiones (FN)** que su mismo detector con `u = 0` en **ninguna** combinación de escena y sentido.
2. **Entre las que cumplen:**
   - menos errores totales;
   - después, menor suma de errores absolutos de conteo por escena y sentido;
   - después, menor `u`.
3. **Resultado nulo:** si ninguna variante con `u > 0` tiene menos errores totales que su detector sin filtro cumpliendo la condición, se concluye que **la supresión temporal global no se justifica**. Es un resultado válido.

Si alguna variante gana, sigue siendo exploratoria y solo es candidata para la validación nueva (`protocolo-validacion-nueva.md`). No se cambia la API.

## Fuera de la elección

Para `youtube-bus-real` solo se clasifican los errores que ya se conocen, de forma descriptiva: fragmentación, oscilación, errores de tiempo y omisiones. **No se calcula una nueva puntuación con filtro** en ese video.
