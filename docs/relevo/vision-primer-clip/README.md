# Relevo de visión · primer clip

**Resultado: el ensayo de 0 a 6 s produce una subida y una bajada, y el panel pasa de 0 a 1 pasajero (5 %) y vuelve a 0. El detector todavía no es confiable.** En el video completo detecta 12 cruces donde el contador comercial registra 20, y la configuración se calibró sobre este mismo clip. Estas cifras no sirven como métricas del informe.

- **Clip:** [`data/raw/oficina.mp4`](../../../data/README.md), real, una oficina que hace de puerta de bus.
- **Predicción:** [`evaluation/results/oficina-00-06-prediccion.json`](../../../evaluation/results/oficina-00-06-prediccion.json), con su [configuración](../../../evaluation/results/oficina-00-06-prediccion.config.json).
- **Video anotado:** `runs/oficina-00-06-anotado.mp4`. Git lo ignora, así que se regenera con el comando de abajo.
- **Commit:** el que incorpora este archivo en la rama `vision`.

## Reproducir

Desde la raíz, con el entorno de [`vision/README.md`](../../../vision/README.md) y el clip en `data/raw/`:

```sh
python -m vision.pipeline --video data/raw/oficina.mp4 --inicio 0 --fin 6 --recorte 228,2,222,176 --linea 0,90,221,90 --interior arriba --rastreador vision/bytetrack-cenital.yaml --conf 0.05 --confirmacion 2 --dispositivo cpu --pesos yolo11n.pt --parada "Puerta de oficina · 0-6 s" --salida evaluation/results/oficina-00-06-prediccion.json --video-anotado runs/oficina-00-06-anotado.mp4
```

Recorte: el cuadrante entre los separadores verdes medidos en el cuadro. Línea: `y` = 90 en el recorte (92 en el cuadro), en la mitad de la banda del umbral. La eligió Claude mirando el cuadro; conviene que Álvaro y su compañero la confirmen.

## Comparación con la referencia manual

La columna "A ojo" se anotó mirando los cuadros **antes** de ver la salida del modelo.

| Cruce | Manual | A ojo | Predicho | Diferencia con el manual | Carga tras el cruce (manual / panel) |
|---|---|---|---|---|---|
| Subida | cerca de 2 s | entre 1,92 y 2,20 s | 2,16 s, ID 1 | +0,16 s | 1 (5 %) / 1 (5 %) |
| Bajada | cerca de 4 s | cerca de 4,6 s | 4,6 s, ID 5 | +0,6 s | 0 (0 %) / 0 (0 %) |

Ambos cruces quedan dentro de la tolerancia propuesta de ±1 s. Los IDs difieren porque la persona sale de la imagen entre un cruce y otro.

A los 4 s solo se ve un pie entrando por arriba, y la persona recién llega al umbral cerca de los 4,6 s. **Conviene revisar los 4 s de la referencia manual.** No se modificó ese archivo.

## Integración

Con la API y el panel corriendo en macOS, sin pasar por Docker:

- `POST /ocupacion` con el JSON por HTTP: `subidas 1, bajadas 1, pasajeros 0, ocupacion_pct 0.0`, sin avisos. Solo con el primer evento: `pasajeros 1, ocupacion_pct 5.0`. La referencia manual da el mismo resultado final.
- Panel con el mismo contenido de ese JSON, cargado por el selector de archivo:

| Selector | Pasajeros | Ocupación |
|---|---|---|
| 2 s | 0 | 0 % |
| 2,16 s | 1 | 5 % |
| 4 s | 1 | 5 % |
| 4,6 s | 0 | 0 % |

- `python -m pytest tests -v`: ver el resultado en [`vision/README.md`](../../../vision/README.md).

## Qué tan frágil es este resultado

- **Detector base.** Con `yolo11n.pt` y ByteTrack por defecto, el ensayo da **0 eventos**: hay tracks en 4 de 150 cuadros. Vista desde arriba, la persona rara vez supera 0,25 de confianza. En tres tramos vacíos revisados a ojo, la confianza máxima fue 0,068.
- **Calibración.** Se probaron 33 combinaciones de umbrales de ByteTrack y cuadros de confirmación sobre este clip. Solo 4 dieron los dos cruces. La elegida es la de umbrales más altos entre esas, con la confirmación más estricta que los produce (2 cuadros). Con 3 cuadros se pierde la bajada.
- **Detección intermitente.** Hay tracks en 29 de 150 cuadros. A los 4,56 s la persona está sobre el umbral y no tiene caja.
- **Video completo.** Con la misma configuración salen 7 subidas y 5 bajadas; el contador comercial termina en 10 y 10. Es una comparación de totales: no empareja cruces ni dice cuántos eventos son falsos positivos.
- **Resolución.** El clip es de 450×360 y el cuadrante de 222×176. Una copia de mayor resolución podría cambiar el resultado.

## Próximo pendiente

1. Confirmar la línea y revisar el tiempo manual de la bajada.
2. Anotar cajas de personas vistas desde arriba y ajustar el detector en `vision/train.py`, que es lo que más puede mejorar la detección.
3. Conseguir grabaciones independientes para validación y prueba, y escribir `evaluation/evaluate.py`. Hay dos videos candidatos en `docs/tareas/vision/videos-candidatos.md`, en la rama `tareas-03-04-panel-informe`.
4. Probar el pipeline en Windows, en la máquina de defensa.
