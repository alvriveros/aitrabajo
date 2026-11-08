# Revisión de la referencia del video de oficina

Hay dos referencias de cruces para `data/raw/oficina.mp4`. **Ninguna es una evaluación independiente:** la misma grabación se usó para calibrar el rastreador base (0–6 s) y para ajustar el detector (6–43 s).

## 1. `docs/demo/oficina-00-06-manual.json`: referencia manual de 0–6 s

- **Contenido:** una subida a 2 s y una bajada a 4 s, de la misma persona.
- **Origen:** Álvaro y su compañero contaron el clip a mano al principio del proyecto (`docs/PLAN.md` y `docs/tareas/vision/README.md`). Los tiempos son **aproximados**, redondeados al segundo, y no hay registro de quién marcó cada instante ni con qué criterio de cruce.
- **Uso:** la muestra el panel como «Referencia manual» y la usan las pruebas de tolerancia ±1 s. Con esa tolerancia sirve para comparar sentido y orden, no para medir el error temporal.

## 2. `data/annotations/oficina-cruces.json`: 20 cruces del video completo

- **Contenido:** 10 subidas y 10 bajadas alternadas, todas con `track_id` 1. La única persona entra y sale diez veces.
- **Origen, según `data/README.md` y `docs/relevo/vision-ajuste-detector/README.md`:**
  - Los cruces salen del **centro de las cajas** de `oficina-cajas.json`.
  - Esas cajas son propuestas automáticas por resta de fondo (`vision/proponer_cajas.py`) y 20 de ellas se corrigieron a mano.
  - Las **revisó Claude, no una persona**.
  - Sus totales coinciden con el contador comercial que muestra el propio video (10 y 10). Eso confirma los totales, no los instantes.
- **Lo que no está documentado:**
  - `oficina-cajas.json` no tiene cuadros antes de 6 s, porque el ensayo quedó fuera del entrenamiento. Sin embargo, la referencia incluye cruces a 2,16 y 4,68 s, y no está registrado cómo se obtuvieron esos dos.
  - Las cajas son 165 cuadros en 46 s, no todos los cuadros, así que la resolución temporal de los instantes depende de ese muestreo.
- **Dependencia con lo evaluado:** el detector ajustado se entrenó con esas mismas cajas, y la referencia sale de ellas. Por eso el error medio de tiempo del ajustado (0,03 s) no es confiable, como ya advierte el relevo del ajuste.

## Revisión humana que falta

1. **Cruces.** Una persona que no haya hecho las cajas mira el video a velocidad reducida y marca cada cruce de la línea y = 90 del recorte `228,2,222,176`: el cuadro en que el centro del cuerpo pasa la línea y el sentido. Lo hace sin ver las predicciones ni `oficina-cruces.json`. Después se comparan sus 20 instantes con los actuales y se registran las diferencias.
2. **Tramo 0–6 s.** Documentar cómo se obtuvieron 2,16 y 4,68 s, o reemplazarlos por la marca humana del punto 1.
3. **Cajas.** Revisar las 165 con `python -m vision.revisar_cajas`, sobre todo las 20 corregidas y los 3 cuadros descartados (768, 891 y 1158). Si cambia alguna, repetir el entrenamiento y la comparación.
4. **Registro.** Anotar en `data/README.md` quién revisó, cuándo y con qué criterio.

Mientras tanto, las cifras sobre este video **orientan** la comparación de configuraciones. No son métricas de generalización ni de independencia.
