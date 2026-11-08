# Ficha de adquisición y anotación · grabación independiente

Objetivo: tener **una toma nueva, no usada para calibrar ni entrenar**, con la que medir aciertos, omisiones y eventos extra por sentido. Es una ficha de trabajo, no parte del informe.

## Antes de grabar

- **Consentimiento.** Cada persona que aparezca firma o confirma por escrito que acepta ser grabada y que el video se use en el TP. Registrar nombre o seudónimo, fecha y alcance (solo uso académico interno, sin publicar). Si alguien no consiente, no se graba o se descarta la toma. No incluir menores.
- **Lugar.** Una puerta con paso claro: aula, pasillo o casa. Anotar el lugar de forma genérica (por ejemplo, «puerta de un aula»), sin datos personales.
- **Cámara fija arriba de la puerta**, mirando hacia abajo, con la mayor verticalidad posible. Puede ser un celular sujeto con cinta o trípode. Que no se mueva durante toda la toma.
- **Encuadre.** El umbral cruza la imagen de lado a lado. Tienen que verse aproximadamente 1 m de cada lado de la puerta, y no debe haber pantallas ni reflejos en el cuadro.
- **Formato.** Al menos 720p y 25 o 30 FPS, sin cámara lenta ni estabilización digital si se puede desactivar. Registrar modelo de cámara, resolución, FPS reales (`ffprobe`), duración y orientación.
- **Interior y exterior.** Decidir antes de grabar qué lado es «adentro» (subida = hacia adentro) y anotarlo con un croquis o una foto del lugar.

## Guion de la toma

Una sola toma continua de 2 a 4 minutos:

| Tramo | Qué pasa |
|---|---|
| 0–15 s | Puerta vacía, sin cruces: mide eventos extra con escena quieta. |
| Bloque 1 | Una persona entra y sale 4 a 6 veces, a ritmo normal, con pausas de 3 a 5 s sin nadie. |
| Bloque 2 | Otra persona, con otra ropa o altura, hace lo mismo. |
| Bloque 3, si es viable | Dos personas: una entra mientras la otra sale; luego dos seguidas en el mismo sentido, una detrás de la otra (oclusión). |
| Bloque 4 | Casos difíciles cortos: alguien se detiene sobre la línea y vuelve, alguien pasa con una mochila o una caja. |
| Final, 10 s | Puerta vacía otra vez. |

Anotar en papel, durante la grabación, el orden aproximado de lo que se hizo. Sirve para controlar después.

## Anotación

- **Instantes.** Una persona que no ejecutó el sistema sobre este video marca cada cruce: el **instante** (en segundos desde el inicio del archivo, con el cuadro exacto si se puede), el **sentido** (subida o bajada) y un ID manual de persona. Sigue el mismo criterio que la línea de conteo: el cruce ocurre cuando el centro del cuerpo pasa el umbral. Una segunda persona revisa una muestra.
- **Archivo de cruces.** Se guarda en el esquema de `POST /ocupacion`, igual que `data/annotations/oficina-cruces.json`, en `data/annotations/<nombre>-cruces.json`.
- **Recorte y línea.** Se definen **antes** de ejecutar el sistema y se guardan en un `.config.json`.

## Uso para evaluar

- **Toda la toma es de prueba.** No se usa ningún fragmento para entrenar ni para elegir umbrales. Si hace falta validar algo, se graba **otra** toma; no se reparten cuadros vecinos de la misma toma entre conjuntos.
- **Prueba reservada.** Se ejecutan las configuraciones ya elegidas (base y ajustado, con su rastreador declarado) **una sola vez**. Se evalúa con `python -m evaluation.evaluate` y tolerancia ±1 s, y se registran TP, FP y FN y el error de conteo **por sentido**. No alcanza con el saldo final de pasajeros.
- **Registro.** Se documenta en `data/README.md`: archivo, SHA-256, duración, FPS, resolución, consentimiento registrado (sin datos personales en el repositorio), partición «prueba» y quién anotó. El video no se versiona: va a `data/raw/`.
