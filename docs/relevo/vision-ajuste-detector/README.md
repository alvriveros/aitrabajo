# Relevo de visión · ajuste del detector

**Resultado: con el detector ajustado, el video de oficina da 10 de 10 subidas y 10 de 10 bajadas, sin falsos positivos. Eso no mide cuánto generaliza.** Todo sale de una sola grabación, con una sola persona, y el ajuste empeoró la detección de personas de frente. Estas cifras no sirven como métricas del informe.

El texto listo para el informe, con estos resultados y sus advertencias, está en [`aportes-vision.md`](../../informe/aportes-vision.md).

## Comparación

Con [`evaluation/comparar_oficina.py`](../../../evaluation/comparar_oficina.py) y tolerancia de ±1 s. Cada celda es aciertos sobre cruces de referencia.

| Configuración | Ensayo, 0–6 s | Entrenamiento, 6–43 s | Reserva, 43–52,6 s | Video completo | Falsos positivos | F1 |
|---|---|---|---|---|---|---|
| Base, ByteTrack por defecto | 0/2 | 0/14 | 0/4 | 0/20 | 0 | 0,00 |
| Base, ByteTrack calibrado | 2/2 | 9/14 | 1/4 | 12/20 | 0 | 0,75 |
| **Ajustado, ByteTrack por defecto** | 2/2 | 14/14 | 4/4 | **20/20** | **0** | **1,00** |
| Ajustado, ByteTrack calibrado | 2/2 | 14/14 | 4/4 | 20/20 | 2 | 0,95 |

- **Tramos.** El ensayo y la reserva no se usaron para entrenar. Son cuadros y pasos nuevos, pero de la misma grabación.
- **Configuración elegida.** Ajustado con ByteTrack por defecto, por F1 en el tramo de entrenamiento (1,00 frente a 0,97). Los umbrales bajos de `bytetrack-cenital.yaml` agregan falsos positivos con este modelo, a los 2,68 s y a los 17,8 s; solo tenían sentido para el detector base.
- **Por cuadro.** En la reserva, mAP50 0,995 y mAP50-95 0,819, en [`oficina-ajuste.json`](../../../evaluation/results/oficina-ajuste.json). En 37 cuadros del ensayo con la persona visible, el detector ajustado supera 0,25 de confianza en los 37; el base, en 8.
- **Velocidad.** Unos 41 FPS con CPU en un Apple M4, con entrada de 640 px y sin video anotado. Falta medirla en la máquina de defensa.

## Por qué no sirve para el informe

1. **Una sola grabación.** Misma persona, ropa, cámara y alfombra en todos los tramos. El modelo puede estar aprendiendo esa escena y no a reconocer personas vistas desde arriba. Según [el relevo](../../tareas/vision/README.md), todos los fragmentos de una grabación van a la misma partición.
2. **Se especializó.** Con conf ≥ 0,25, en las imágenes de ejemplo de Ultralytics, con personas de frente, el modelo pasa de 4 a 2 personas en `bus.jpg` y de 2 a 1 en `zidane.jpg`. Si la demo o la evaluación usan otro ángulo, puede rendir peor que el modelo base.
3. **Nadie cruza a la vez.** El clip tiene una sola persona. **El desafío de oclusiones de la consigna sigue sin probarse.**
4. **La referencia no es independiente.** Los 20 cruces salen del centro de las mismas cajas revisadas usadas para entrenar. Sus totales coinciden con el contador comercial del video (10 y 10) y alternan subida y bajada, pero falta que una persona los revise. Por eso el error medio de tiempo, de 0,03 s, no es una medida confiable.

## Anotaciones

[`oficina-cajas.json`](../../../data/annotations/oficina-cajas.json) tiene 165 cuadros. **Las revisó Claude, y falta la revisión de una persona.**

| Partición | Con persona | Sin persona |
|---|---|---|
| Entrenamiento, 6–43 s | 113 | 18 |
| Reserva, 43–52,6 s | 30 | 4 |

- 20 cajas se corrigieron a mano, casi todas de personas bajando sobre la alfombra, donde la propuesta automática se confundía.
- 3 cuadros se descartaron por ser ambiguos: 768, 891 y 1158.
- Los cuadros sin persona son fondo o sombra sola. La propuesta automática parte de la resta de fondo: `vision/proponer_cajas.py`.

Para revisarlas, generá las hojas y compará cada imagen con su número de cuadro:

```sh
python -m vision.revisar_cajas --anotaciones data/annotations/oficina-cajas.json --hojas runs/revision-cajas
```

Si cambiás una caja, repetí el entrenamiento y la comparación.

## Reproducir

Desde la raíz, con el entorno de [`vision/README.md`](../../../vision/README.md) y el clip en `data/raw/`:

```sh
python -m vision.train --anotaciones data/annotations/oficina-cajas.json --salida runs/oficina-ajuste --resumen evaluation/results/oficina-ajuste.json --pesos yolo11n.pt --epocas 40 --tamano 640 --lote 16 --semilla 0 --dispositivo cpu
python -m evaluation.comparar_oficina
```

Video anotado con el detector elegido:

```sh
python -m vision.pipeline --video data/raw/oficina.mp4 --recorte 228,2,222,176 --linea 0,90,221,90 --interior arriba --dispositivo cpu --pesos runs/oficina-ajuste/oficina-ajustado.pt --parada "Puerta de oficina · video completo" --salida runs/oficina-ajustado-completo.json --video-anotado runs/oficina-ajustado-completo.mp4
```

- **Entrenamiento.** 40 épocas en 8,6 minutos con CPU en un Apple M4. Se conservan los pesos de la última época, así que la reserva no eligió el modelo.
- **Pesos.** `runs/oficina-ajuste/oficina-ajustado.pt`, 5.497.434 bytes, SHA-256 `783d16c01b9dc4995ac4809dcbd0bd794fd96ad2edaf509aa296f682622d93e1`. Git los ignora. En otra máquina el entrenamiento puede dar pesos distintos, así que para la defensa conviene copiar este archivo y comprobar su huella.
- **Resultados.** Predicciones y configuración de cada corrida en `evaluation/results/oficina-completo-*.json`, y el resumen en [`oficina-comparacion.json`](../../../evaluation/results/oficina-comparacion.json).
- **Integración.** Las predicciones pasan el contrato de `POST /ocupacion` en las pruebas. No se volvieron a cargar en el panel.

## Próximo pendiente

1. Revisar las cajas y los 20 cruces. Confirmar la línea.
2. **Conseguir grabaciones independientes**, idealmente propias y con varias personas cruzando a la vez. Sin ellas no hay métricas válidas para el informe. Hay dos videos candidatos en `docs/tareas/vision/videos-candidatos.md`, en la rama `tareas-03-04-panel-informe`.
3. Decidir con qué cámara se hace la demo. Si no es cenital, este modelo no está preparado.
4. Probar el pipeline y los pesos ajustados en la máquina de defensa.
