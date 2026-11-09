# Tarea 12 · Supresión de duplicados y prueba nueva · devolución (8 nov., madrugada)

Rama `integracion-video`. No hubo staging, commit, push ni merge, y no se tocó la API, Docker ni el panel. No se entrenó ni se ejecutó ninguna inferencia: todo se calculó sobre eventos ya guardados.

## Respuesta corta

**La supresión temporal global no ayuda sin borrar cruces reales.** Con el criterio prerregistrado, ninguna variante gana. El resultado es **exploratorio**: las referencias de Kaggle y PAMELA A son de Claude y no tienen revisión humana.

- **Por qué no funciona:** casi todos los eventos falsos de Kaggle y PAMELA A no son duplicados del mismo sentido. Son **oscilaciones**: la misma persona (el mismo `track_id`) «sube» y «baja» en menos de 1,5 s. Un filtro por tiempo y sentido no puede eliminarlas sin quitar también cruces verdaderos de escenas densas como PAMELA.
- **Siguiente experimento propuesto, sin implementar:** registrar la posición y la trayectoria local de cada track alrededor de la línea, para estudiar oscilación y continuidad en el espacio.

## 1. Trazabilidad

- **Copias históricas:** antes de editar se guardaron en `historico/` las versiones de los scripts que produjeron la evidencia de la tarea 11, con su SHA-256 y su procedencia (`historico/README.md`).
  - La versión de `evaluar_detectores.py` usada en la selección Linux es una **reconstrucción**: se le quitaron los agregados documentados para la prueba final.
- **Evidencia sin cambios:** no se editaron eventos, métricas, referencias ni prerregistros. Las aclaraciones posteriores llevan fecha y procedencia.
- **Estado vigente actualizado** en `resumen.md`, `docs/tareas/claude/README.md`, `data/README.md`, el README de la tarea 11 (las secciones viejas quedan rotuladas como históricas) y `estado-para-codex.md`. Queda registrado esto:
  - la prueba final se ejecutó y la API no cambia;
  - Kaggle y PAMELA A se usaron para seleccionar;
  - `youtube-bus-real` ya se consumió.
- **La referencia final no explica la diferencia con el contador comercial:** Álvaro anotó 18 cruces y el contador del fabricante marca 16, pero `notas` está vacío. **Se le pidió la aclaración**; cuando la dé, se guarda en `aclaracion-referencia-final.md` sin tocar el JSON, cuyo SHA-256 `ad73d9d8…` identifica la ejecución.

## 2. Herramientas corregidas

Probadas sin inferencia, en `test_herramientas.py` (7 pruebas).

- **`anotar_cruces.py`:**
  - **Navegación:** `,` retrocedía dos cuadros, y A/D se movían 2 s menos un cuadro. Además, saltar con `CAP_PROP_POS_FRAMES` **cae en otro cuadro en el MP4 de Kaggle** (verificado: el cuadro 999 no coincide).
    - Ahora el anotador lee solo hacia adelante y guarda los últimos 4 s para retroceder, así que el tiempo es siempre índice secuencial / FPS.
    - Se probó con un MP4 sintético con cuadros intermedios, leyendo el número de cada cuadro de la imagen.
  - **La referencia final no se ve afectada:** en `youtube-bus-real`, el salto daba el cuadro correcto en 40 de 40 posiciones al azar, y el tiempo guardado siempre fue el del cuadro en pantalla. El error de la tecla `,` solo pudo correr alguna marca 40 ms.
  - **Otros cambios:**
    - ahora pide `--video`, `--salida` y `--linea-y`, y valida que el video abra y tenga FPS;
    - con `--continuar` conserva notas y metadatos;
    - ya no escribe «antes de ejecutar modelos»;
    - se niega a sobrescribir una salida existente y **nunca** escribe sobre la referencia final (protegida por su hash).
- **`evaluar_detectores.py`:** rechaza una carpeta de salida con resultados, o de videos anotados, antes de ejecutar nada. Los videos de cada ejecución van a `runs/evaluacion/tarea11-<so>/<salida>/`.
- **`prueba-final.ps1`:** si `final-windows\` existe, se niega a correr, así que la prueba final de la tarea 11 no se repite.

## 3. Experimento de supresión temporal (exploratorio)

- **Prerregistro:** `prerregistro.md`, SHA-256 `0643485e…`, guardado antes de calcular.
  - El encabezado dice «alrededor de las 05:10», **pero es un error**: el cálculo corrió a las 04:50:43 (hora del contenedor), después del prerregistro. No se corrigió el archivo para no alterarlo.
- **Regla:** para cada sentido, se descarta un evento si dista menos de `u` del último aceptado del mismo sentido, con condición estricta. Se conserva el más temprano y los sentidos opuestos no interactúan. Pruebas en `test_supresion.py` (6 casos).
- **Datos y salida:** umbrales `u ∈ {0; 0,5; 1; 1,5}`, sobre los eventos Linux de la tarea 11, con tolerancia ±1 s. Los resultados están en `resultados-exploratorios/`, incluidos los eventos descartados.

| Variante | Kaggle subidas TP/FP/FN | Kaggle bajadas | PAMELA subidas | PAMELA bajadas | Errores | FN no sube |
|---|---|---|---|---|---|---|
| **API: yolo11n, u = 0** | 5/4/1 | 0/4/0 | 0/1/0 | 10/0/18 | **28** | — |
| yolo11n, u = 0,5 | 5/1/1 | 0/3/0 | 0/1/0 | 9/0/19 | 25 | **no** |
| yolo11n, u = 1,0 | 5/0/1 | 0/3/0 | 0/1/0 | 9/0/19 | 24 | **no** |
| yolo11n, u = 1,5 | 5/0/1 | 0/2/0 | 0/1/0 | 9/0/19 | 23 | **no** |
| yolo11l, u = 0 | 6/2/0 | 0/2/0 | 0/2/0 | 13/0/15 | 21 | — |
| yolo11l, u = 0,5 | 6/2/0 | 0/2/0 | 0/2/0 | 13/0/15 | 21 | sí, sin mejora |
| yolo11l, u = 1,0 | 6/1/0 | 0/2/0 | 0/2/0 | 12/0/16 | 21 | **no** |
| yolo11l, u = 1,5 | 6/0/0 | 0/2/0 | 0/2/0 | 10/0/18 | 22 | **no** |

- **Los totales engañan:** con `yolo11n` y 1,5 s, el total baja de 28 a 23, pero **borra una bajada real de PAMELA**. Por eso no cuenta como mejora: es exactamente el caso de «mejora el total ocultando omisiones».
- **Aplicada a las propias referencias,** la regla con 1,5 s borraría 1 de 6 subidas de Kaggle y **13 de 28 bajadas de PAMELA**. Con 0,5 s borraría 3 y con 1 s, 6.
- **Conclusión prerregistrada:** ninguna variante con `u > 0` mejora a su detector sin aumentar omisiones. La supresión temporal global no se justifica.

## Errores clasificados (descriptivo, sin elegir nada)

`clasificar_errores.py` aplica estas definiciones en orden; los detalles están en el script y en `clasificacion-errores.json`:

- **Error de tiempo:** un FP con una omisión del mismo sentido a 2,5 s o menos.
- **Oscilación:** el mismo ID tiene un evento del sentido opuesto a 1,5 s o menos.
- **Fragmentación:** otro ID tiene un evento del mismo sentido a 1,5 s o menos.

| Escena · detector | Error de tiempo | Oscilación | Fragmentación | Otro FP | Omisión pura |
|---|---|---|---|---|---|
| Kaggle · yolo11n | 0 | 7 | 1 | 0 | 1 |
| Kaggle · yolo11l | 0 | 2 | 2 | 0 | 0 |
| PAMELA A · yolo11n | 0 | 1 | 0 | 0 | 18 |
| PAMELA A · yolo11l | 0 | 2 | 0 | 0 | 15 |
| YouTube (consumido) · yolo11n | 0 | 0 | 0 | 1 | 12 |
| YouTube (consumido) · yolo11l | 2 | 3 | 5 | 2 | 4 |

**Lectura:** no todo es rastreo.

- **Omisiones:** en PAMELA y con `yolo11n` en YouTube dominan las omisiones puras, es decir, personas que nunca generan un cruce. Eso es detección, o rastreo que nunca arranca.
- **Kaggle:** los falsos son sobre todo oscilaciones.
- **YouTube con `yolo11l`:** hay de todo; fragmentación, 5, y oscilación, 3, son lo más frecuente, más 2 errores de tiempo. Un ejemplo es el ID 10, que sube a 34,12 s y baja a 34,32 s.
- **Uso de YouTube:** sus filas solo describen, y no se usaron para elegir.

## 4. Validación nueva: preparada, pendiente

El protocolo está en `protocolo-validacion-nueva.md`:

- qué grabar;
- anotar con referencia humana antes de inferir;
- fijar la geometría, el hash y la tolerancia;
- congelar el candidato;
- ejecutar una vez en el mismo entorno;
- decidir con menos FN + FP, al menos 10 FPS y el desglose por sentido.

Como el filtro no se justificó, el candidato sería `yolo11l` calibrado sin filtro, aunque ya perdió la prueba final.

**Recomendación:** antes de gastar un video nuevo, hacer primero el experimento de trayectorias en Kaggle y PAMELA.

## 5. Qué versionar

Ver `manifiesto.md`. No se hizo staging.

## Pendientes humanos (Álvaro)

1. La aclaración de los 18 cruces contra los 16 del contador, que va a `aclaracion-referencia-final.md`.
2. La revisión de las referencias de Kaggle (6 cruces) y PAMELA A (28). Si se corrigen, van en archivos nuevos y se recalcula `supresion.py` en otra carpeta.
3. Una grabación nueva para el protocolo.
4. Aprobar el manifiesto antes de cualquier commit.

## Comandos y entorno

- **Entorno:** contenedor Linux de Claude, Python 3, OpenCV 5.0.0 y pytest, sin GPU y sin inferencia.
- **Comandos,** desde la raíz del worktree:

```
python -m pytest docs/relevo/2026-11-08-claude-tarea12/ -q              # 13 aprobadas
python docs/relevo/2026-11-08-claude-tarea12/supresion.py               # escribe resultados-exploratorios/
python docs/relevo/2026-11-08-claude-tarea12/clasificar_errores.py      # escribe clasificacion-errores.json
```

- **Suite completa:** no se volvió a correr; no se tocó código de producción.
