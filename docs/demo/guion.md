# Guion de la defensa · 10 minutos más 2 de preguntas

Versión del cierre final (9 nov.; actualizada el 9 nov. a la noche con la Fig. 2 del informe y las respuestas breves). **El ensayo oral del equipo no está hecho**: el registro de Codex es solo técnico. Lo que está entre comillas es una propuesta para decir en voz alta: adaptalo a tus palabras. **Regla de la demo: primero lo que se ejecuta en vivo; después, rotuladas como tales, las métricas históricas.** Nunca presentes un resultado guardado como si fuera inferencia nueva.

## Preparación · 30 minutos antes

1. **Rama y entorno.** En la raíz del repositorio, con la rama `main`.
2. **Insumos fuera de Git:** `data\raw\prueba-bus.mp4` y `data\raw\oficina.mp4` (no se redistribuyen). Los pesos se preparan y verifican con `.\.venv\Scripts\python.exe vision\pesos.py` (si `yolo11n.pt` ya está, solo comprueba su SHA-256).
3. **Arranque con GPU** (recomendado: en CPU no hay tiempo real, ver más abajo). En una terminal:
   ```powershell
   $env:VISION_DISPOSITIVO = "cuda:0"
   ..\venv-gpu\Scripts\python.exe -m uvicorn api.main:app --port 8000
   ```
   En otra:
   ```powershell
   .\.venv\Scripts\python.exe -m streamlit run ui/app.py
   ```
   **Alternativa con Docker** (solo CPU, **no** sirve para mostrar tiempo real): `docker compose up --build -d` y el panel en http://127.0.0.1:8502.
4. **Ensayo:** procesá una vez `prueba-bus` con «Simular cámara en vivo» tildada y anotá el FPS y el retraso que muestra el panel. Esa ejecución queda guardada como **respaldo**.
5. **Pestañas abiertas:** el informe (Tablas II y III), el panel en «Archivo JSON o demo» y la carpeta `runs\panel\20261108-200805-374934` (la primera evaluación de `prueba-bus`).

## 0:00–1:30 · Problema y objetivo

> "En diciembre de 2025 se sancionó la reforma del transporte público metropolitano, y en mayo se reglamentó. Para planificar frecuencias y controlar el hacinamiento hace falta saber cuánta gente lleva cada unidad en cada parada, no solo cuántos boletos se vendieron. Nuestro sistema cuenta subidas y bajadas con una cámara en la puerta y calcula la ocupación a lo largo del recorrido."

Pantalla: panel → «Archivo JSON o demo» → **Línea simulada de 8 paradas**. Mové el selector hasta la parada 4 y mostrá el **105 %**.

> "Este recorrido es simulado, y así lo indica el panel. Lo usamos para mostrar el reporte que recibiría la empresa: carga acumulada y sobreocupación por parada."

## 1:30–3:00 · Arquitectura

Pantalla: Fig. 1 del informe.

> "Cada cuadro pasa por YOLO11n, que detecta personas. ByteTrack les asigna un identificador, y una regla decide cuándo un identificador cruza la línea de un lado confirmado al otro. Cada cruce es un evento con su instante y su sentido. La API calcula la ocupación con esos eventos. El procesamiento corre fuera de la petición HTTP, uno por vez, y el panel consulta su estado cada segundo sin reiniciar el modelo."

## 3:00–6:30 · Demo en vivo

1. «Video nuevo» → subí `prueba-bus.mp4`. Mostrá resolución, FPS, duración y hash.
2. **Geometría:** recorte 0, 0, 768, 432; línea X1 274, Y1 431, X2 467, Y2 242; interior arriba. Apretá Enter después de cada número. Mové la vista previa:
   > "La vista previa no ejecuta el modelo."
3. Tildá **«Simular cámara en vivo»**, cargá 30 de capacidad y 20 pasajeros iniciales, y pulsá **«Reprocesar en vivo para demostración»**.
   - Si es la primera vez con esa configuración, alcanza con «Procesar video».
   - Si la página avisa «No se repite», es que ya existe esa ejecución: usá «Reprocesar en vivo».
4. **Mientras corre,** señalá:
   - cómo aumentan las subidas y las bajadas;
   - cómo baja la ocupación;
   - el FPS y el retraso respecto del video, que no debe crecer;
   - los cuadros descartados.

   > "Esto se está calculando ahora. Si el equipo no alcanzara la velocidad del video, descartaría cuadros en lugar de atrasarse, como una cámara."
5. **Al terminar,** mostrá el video anotado, la tabla de eventos y las descargas (eventos, video y configuración).
6. **Opcional:** recargá la página durante un procesamiento y mostrá que se retoma; o pulsá «Cancelar» y mostrá que no se publica.

**Qué esperar:** las ejecuciones en GPU verificadas produjeron **25 eventos** (12/13/0, F1 0,65), distintos de los **24** de la evaluación ciega en CPU (12/12/0, F1 0,67). Al terminar el conteo, el panel queda cerca del 99 % mientras convierte el video anotado: en el ensayo técnico fueron unos **22 s** más (unos 59 s desde la aceptación hasta el estado final); reservá 20–30 s sin prometerlo como constante. No se garantiza que toda ejecución futura sea idéntica: antes de leer cifras, mirá el id de la ejecución y presentá las que muestre el panel. Si cambian el plan de energía a máximo rendimiento, hagan una comprobación breve antes de presentar.

**Respaldo, si algo falla en vivo:** en «Ejecución», elegí la del ensayo o `20261108-200805-374934`. Decilo explícitamente:

> "Esto es un resultado guardado, no inferencia en vivo."

## 6:30–9:00 · Resultados medidos (históricos, del informe)

Pantalla: Tabla II del informe.

- **Evaluación ciega de `prueba-bus`** (primera evaluación, **CPU de Windows**, ejecución `20261108-200805-374934`; después el video se usó para desarrollo):
  - 12 de 12 cruces detectados, pero 12 eventos falsos: precisión 0,50, exhaustividad 1,00 y F1 0,67;
  - al revisar el video, 8 de los falsos son una segunda caja sobre una persona ya contada.
  > "Es exactamente el problema de oclusiones de la consigna, y no lo resolvimos."
- **Efecto sobre la carga** (Fig. 2 del informe, misma ejecución CPU): cambio acumulado de pasajeros, referencia contra estimación, cada 0,1 s. MAE 2,68 y RMSE 3,31 pasajeros, **solo para este clip**. El F1 mira eventos; esto, cuánto se desvía la carga en el tiempo.
- **Bus real de YouTube** (prueba final, GPU): se contaron 6 de 18 cruces. Predominan las omisiones. **Esa prueba influyó en elegir YOLO11n en vez de YOLO11l**, así que ya no es independiente.
- **Validación prerregistrada con PAMELA B** (subidas densas, nunca procesadas antes, pero **de la misma puerta y cámara que PAMELA A**, usada para seleccionar): F1 de 0,36 y 0,45.
  > "Detecta 34 de 41 subidas, pero en la fila que espera sobre la línea las identidades van y vienen: 93 eventos falsos. Este es el resultado más honesto que tenemos sobre oclusiones."

- **Modelo ajustado:** 20 de 20 en su propia grabación, pero 0 de 6 en Kaggle y 1 de 28 en PAMELA.
  > "Por eso desplegamos el preentrenado: no vamos a usar un modelo peor solo porque lo entrenamos nosotros."
- **Tiempo real** (Tabla III):
  - en CPU, 8,8 FPS; con ritmo real, el retraso no crece, pero se descarta el 70 % de los cuadros y en oficina se cuentan 4 de 20 cruces;
  - con la GPU, en ejecución nativa y ritmo real, **emulando la cámara con un archivo**: 680 de 686 cuadros (6 descartados), latencia interna media de 32 ms que no crece, y el mismo conteo que procesando todos los cuadros. El panel suma hasta 1 s, porque consulta cada segundo.
  - Docker usa CPU: empaqueta el sistema, pero no demuestra tiempo real.

## 9:00–10:00 · Conclusiones

> "Es un prototipo funcional de extremo a extremo, en vivo con GPU y empaquetado en Docker. La calidad del conteo todavía no alcanza para auditar un servicio. Lo siguiente es grabar colectivos locales con permiso, reservar una parte para la prueba y entrenar con cabezas vistas desde arriba."

## Preguntas probables

| Pregunta | Respuesta corta |
|---|---|
| ¿Por qué no entrenaron con más datos? | Con YOLO11x faltaban unas 6 de cada 10 personas en PAMELA, y había que dibujar unas 450 cajas a mano. Entrenar con personas sin anotar le enseña al modelo a ignorarlas. |
| ¿Por qué no filtran las cajas duplicadas? | Se probaron dos opciones. El filtro de cajas encimadas eliminaba pasajeros reales. El IoU 0,5 de NMS mejoró Kaggle y empeoró PAMELA, con el mismo total. Elegir mirando `prueba-bus` exigiría otra prueba ciega. |
| ¿Es tiempo real? | En ejecución nativa con GPU: 680 de 686 cuadros a 24,75 FPS, con 32 ms de latencia interna que no crece. En CPU y en Docker, no: se descartan cuadros y se pierden cruces. |
| ¿De dónde sale `prueba-bus`? | Es una vista previa de iStock (ID 1457518529) con marca de agua. No tenemos la licencia, por eso no publicamos capturas. |
| ¿El 20 de 20 de oficina? | Es la grabación de entrenamiento: no mide generalización. |
| ¿Datos de Paraguay? | No tenemos. Es la primera limitación del informe. |
| ¿24 o 25 eventos? | 24 (12/12/0) es la evaluación ciega en CPU, la del informe. Las ejecuciones en GPU revisadas dieron 25 (12/13/0), también procesando los 686 cuadros: una bajada falsa más que depende de la plataforma. No se identificó el mecanismo. |
| ¿Hay una cámara? | No. Se emula leyendo un archivo a su velocidad. El tiempo real demostrado es en GPU nativa con ese archivo. |

### Respuestas breves de repaso

- **YOLO:** detector de una sola pasada; YOLO11n es la versión más chica, preentrenada en COCO. Usamos solo la clase persona y bajamos la confianza mínima a 0,05 porque desde arriba la confianza es baja.
- **ByteTrack:** asocia detecciones entre cuadros para darle a cada persona un identificador; también usa las de baja confianza para no perder a alguien tapado. No usa apariencia (DeepSORT sí).
- **Línea virtual:** cuenta cuando un identificador pasa de un lado confirmado (2 cuadros a más de 5 px) al otro. El sentido dice si es subida o bajada.
- **F1:** media armónica de precisión y exhaustividad, con cruces emparejados por sentido dentro de ±1 s. No hay verdaderos negativos definidos, por eso no informamos accuracy ni matriz de confusión clásica: informamos TP, FP y FN.
- **Sobreajuste:** el detector ajustado da 20 de 20 en oficina, su propia grabación, y casi nada en Kaggle y PAMELA. Por eso se despliega el preentrenado.
- **Particiones:** cada grabación en una sola. Oficina, para ajustar y seleccionar; Kaggle y PAMELA A, para seleccionar; bus real, prueba final (que influyó en la elección); `prueba-bus`, evaluación ciega y después desarrollo; PAMELA B, validación de la misma escena que A.
- **Errores:** en `prueba-bus`, falsos por cajas duplicadas sobre una persona; en PAMELA B, identificadores que oscilan sobre la línea; en bus real, oficina y PAMELA A, omisiones cuando la detección se corta en la puerta.
- **CPU/GPU:** en CPU, 8,8 FPS; con ritmo real descarta el 70 % de los cuadros y pierde cruces. En GPU nativa, 680 de 686 cuadros con 32 ms de latencia interna. Docker usa CPU.
