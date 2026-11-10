# Tarea 08 · Cerrar la integración de video en Windows

Prioridad del 7 de noviembre de 2026. Los informes académicos quedan para el final. Claude implementa; Codex revisa. No modificar main ni publicar cambios durante esta tarea.

## Punto de partida

La integración está en `integracion-video`, commit comunicado `b511d91`, en `.worktrees/integracion-video`. Leer su `resumen.md`, la devolución `docs/relevo/2026-11-07-claude-tarea07/README.md` y el caso `docs/casos-deteccion/oficina-bajada-omitida/README.md`.

La carpeta principal conserva cambios del informe: no descartarlos ni moverla de rama. La revisión encontró que `.git` del worktree y su registro apuntan a `/sessions/...` de Linux. Antes de editar, verificar los commits y reparar el vínculo con `git worktree repair` desde el repositorio principal, usando la ruta absoluta Windows. No usar prune, reset ni borrar directorios. Comprobar después rama, HEAD y cambios locales; si falta algún objeto, detener esa operación y describir qué falta. Copiar esta ficha al worktree una vez reparado.

## 1. Permitir consultar todo el tramo procesado

En `ui/app.py`, las marcas actuales se construyen solo con paradas y eventos. Con una subida a 2,16 s y ninguna bajada, el selector termina en 2,16 s aunque el video dure 6 s. Para la fuente de video, incorporar el final real del tramo desde su configuración, respetando la base temporal usada por el pipeline. Mantener la lógica de los JSON existentes, que no declaran duración.

Aceptar estos casos:

- Clip 0–6 s con una subida a 2,16 s: consultar 0, 2,16, 4 y 6 s; ocupación 0, 1, 1 y 1 pasajeros, respectivamente.
- Clip sin eventos: permitir consultar hasta el final, mostrando la carga inicial.
- No inventar la bajada ni sustituir la predicción por la referencia manual.
- Mantener instantes fraccionarios, gráfico y tabla sincronizados.

## 2. Publicar solo ejecuciones terminadas correctamente

Revisar `listar_procesamientos`: ahora basta con que exista `prediccion.json` para listar un resultado. La prueba de fallo ya simula un pipeline que escribe archivos y devuelve código distinto de cero. Evitar que una ejecución fallida o en progreso aparezca como utilizable; conservar sus registros para diagnóstico. Usar la solución mínima y probar éxito, fallo después de escribir archivos y timeout. Confirmar que JSON, configuración y video se pueden leer antes de ofrecer el resultado.

## 3. Verificar en Windows

Usar la .venv y los insumos del worktree, registrando versiones y hashes reales. No recrear un entorno que ya funciona ni detener servicios ajenos. Comprobar qué API y panel están activos y desde qué carpeta; usar puertos libres si hace falta.

- Ejecutar las pruebas de API y las de visión; separar fallos funcionales de la evaluación del detector. No debilitar ni omitir una prueba para ocultar la bajada ausente.
- Ejecutar el script `docs/relevo/2026-11-07-claude-tarea07/scripts/verificar_video.py` y ampliarlo para comprobar los instantes 4 y 6, los valores esperados derivados de los eventos reales, y la reproducción efectiva del video (duración, dimensiones, tiempo avanzado y ausencia de error). Su versión actual registra observaciones; `procesado: true` no basta como aceptación.
- Guardar la respuesta de la API y los eventos de la ejecución nueva. No presentar como propia la predicción guardada en macOS.
- Repetir la comprobación del gráfico de 45 estados si se modifica su flujo temporal. Registrar comandos, salidas y capturas.

## 4. Coordinar la omisión con visión

Preparar un pedido concreto para el compañero, sin enviar mensajes automáticamente: pesos ajustados y su hash, configuración, versiones y medición de confianza en macOS con el mismo clip. La diferencia numérica entre plataformas es una hipótesis, no una causa confirmada.

Si los pesos ajustados están disponibles, comparar base y ajustado en Windows con la misma referencia y registrar omisiones y eventos extra. Cualquier ajuste de umbral debe evaluarse en material distinto del usado para elegirlo. Si faltan insumos, completar los puntos independientes y entregar el pedido exacto; conservar el error del modelo como limitación visible. No prometer que el sistema detecta una omisión que no puede observar.

## Entrega

Guardar devolución en `docs/relevo/2026-11-07-claude-tarea08/`: archivos cambiados, comandos, resultados, evidencias Windows y pendientes separados entre integración y detector. Corregir la frase obsoleta «sin commit» de la devolución 07 según el historial verificado. Actualizar índice y resumen dentro de la rama de integración. Dejar cambios sin commit ni push para revisión. Docker sigue con el alcance declarado (JSON; visión manual); no ampliar contenedores en esta tarea. No editar el informe académico.

## Incorporación del análisis externo · 7 de noviembre

Antes de los cambios, conservar la investigación de los cuatro repositorios compartidos por Álvaro en `docs/casos-deteccion/comparacion-repositorios/`: URLs y commits, script propio usado, comandos, versiones, hashes de pesos, entradas y salidas por cuadro. Distinguir resultados medidos por Claude de afirmaciones de terceros. No copiar pesos ni código externo sin comprobar sus condiciones de uso. Esta evidencia técnica no es el informe académico.

La prueba comunicada de SSD MobileNetV2 para cabezas es prometedora, pero aún no verifica tracking ni conteo. Las confianzas de dos detectores no son probabilidades calibradas comparables. No afirmar que confirma la causa de fondo, la composición de COCO o la explicación Mac/x86 sin evidencia específica. Registrar también falsos positivos, continuidad de IDs y eventos finales antes de recomendar un reemplazo.

Mantener los puntos 1–3 de esta tarea como prioridad de Álvaro/Claude. Para el compañero de visión, preparar este orden: probar primero sus pesos YOLO ya ajustados; después evaluar si hay datos y tiempo para un detector de cabezas. Las cajas de personas existentes NO sirven directamente como etiquetas de cabeza: revisar y reanotar. Al cambiar de caja corporal a cabeza, revisar el punto de seguimiento y la posición de la línea; comparar eventos con una referencia manual independiente.

PCDS (`https://github.com/shijieS/people-counting-dataset`) es un candidato de evaluación, no un requisito que bloquee la tarea 08. Intentar obtener una muestra pequeña de color y registrar origen, licencia, identificadores y partición antes de usarla. Si no se consigue en 30 minutos, documentar el bloqueo y continuar; proponer una grabación nueva independiente como alternativa. Los totales por clip permiten error absoluto de subidas y bajadas por separado, pero no métricas temporales por cruce sin anotaciones adicionales. No usar solo el saldo neto, porque puede ocultar errores opuestos. Separar grabaciones/sesiones entre entrenamiento, validación y prueba; no repartir cuadros vecinos entre conjuntos. No atribuir a una muestra pequeña generalización ni independencia por escena que los metadatos no permitan demostrar.

No añadir TensorFlow ni cambiar el detector de producción en esta tarea. Conservar la prueba externa como experimento y entregar al compañero una ficha con los insumos faltantes, sin enviar mensajes automáticamente. Fuentes aportadas: darshan8850/bus_passanager_counter, PhanHuyy/Bus-Passenger-Counter y Mau-FTL/Bus-Passenger-Counter, además de PCDS. La implementación de cada propuesta de visión se decide después de revisar sus resultados.
