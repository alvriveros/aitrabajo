# Estado del proyecto para revisión de Codex · 9 nov. 2026, 01:05

Lo redactó Claude a pedido de Álvaro. Resume el cierre hecho entre el 8 y el 9 de noviembre.

- **Rama:** `cierre-final` (16 commits sobre `24d873d`, sin push ni merge), en el worktree `TpFinal\.worktrees\integracion-video`.
- **Respaldo:** `integracion-video` (`24d873d`) quedó intacta.
- **Consigna:** [`contexto.md`](../../../contexto.md), proyecto 10.
- **Matriz detallada con evidencia:** [`matriz.md`](matriz.md).

**Estados.** Se distinguen cuatro, y no deben confundirse:

- **Cumple:** implementado, probado y con evidencia.
- **Implementado:** el código existe.
- **Probado:** hay una prueba que pasa.
- **Documentado:** está escrito.

## 0. Clasificación de la entrega

**Lista para entregar como prototipo funcional con limitaciones medidas.** El flujo completo funciona y tiene evidencia: video → detección y seguimiento → cruces → ocupación por parada → panel en vivo → Docker → informe.

**No están resueltos todos los objetivos:**

- El desafío de oclusiones de la consigna no se superó (F1 de 0,36 y 0,45 en la validación con subidas densas).
- **No se consiguieron grabaciones de buses de Paraguay accesibles para el proyecto.** Es una restricción central: impidió adaptar y evaluar el sistema en el contexto local y obligó a usar grabaciones de otras procedencias.
- El tiempo real se demostró solo en ejecución nativa con GPU, no en CPU ni en la imagen de Docker.

## 1. Resumen

| Requisito de la consigna | Estado | Por qué |
|---|---|---|
| Dataset relevante, limpio y documentado | **Parcial** | Siete grabaciones (cinco escenas), con origen, hash, licencia, partición y referencias anotadas o revisadas por personas. `prueba-bus` ya tiene su fuente documentada (iStock, ID 1457518529), pero la licencia no está verificada. **Ninguna es de Paraguay.** |
| Modelo entrenado con métricas formales | **Parcial, justificado** | Se entrenó y evaluó un YOLO11n ajustado, pero empeora fuera de su escena. Se despliega el preentrenado con ByteTrack calibrado. Las métricas formales están: P, R y F1 por sentido, y mAP del ajuste. |
| Seguimiento (ByteTrack) con línea virtual | **Cumple** | Implementado, con tests de cada caso de la regla. |
| Superar oclusiones con varias personas | **No cumple** | Medido en una validación prerregistrada: F1 de 0,36 y 0,45 con subidas densas. |
| Conteo y porcentaje de ocupación | **Cumple** (funcional) | La calidad depende del conteo (fila anterior). |
| Tiempo real | **Demostrado en ejecución nativa con GPU; no en CPU ni en Docker** | RTX 2050, `prueba-bus` a 25 FPS, con ritmo real: procesó 680 de 686 cuadros (**6 descartados**) a 24,75 FPS. La **latencia interna** del pipeline, desde que llega un cuadro hasta que se publica, fue de 32 ms de media, sin crecer. Hasta la visualización se suma hasta 1 s, porque el panel consulta cada segundo. El conteo observado coincidió con el de procesar todos los cuadros. En CPU se descartan cuadros y se pierden cruces. |
| Módulo simulado de carga a lo largo del recorrido | **Cumple** | Recorrido simulado de 8 paradas, rotulado como no medido. |
| API REST | **Cumple** | FastAPI, con tests. |
| Interfaz | **Cumple**; ensayo pendiente | Streamlit con resultados en vivo. Álvaro subió y procesó `prueba-bus` desde el navegador, en Docker y con la GPU. El recorrido completo del guion queda para el ensayo. |
| Docker | **Cumple el empaquetado; en CPU** | Verificado por Álvaro en Windows: servicios `healthy`, y `prueba-bus` procesado en el contenedor. La imagen usa CPU: con ritmo real descartó 354 de 686 cuadros. **El tiempo real no se demostró en Docker.** |
| Git con commits descriptivos | **Cumple** | Commits por tarea, sin artefactos pesados. |
| Informe IEEE, 3 páginas | **Cumple** | `docs/informe/informe.pdf`: compilado con MiKTeX, 3 páginas, sin desbordes y revisado página por página. |
| Defensa de 10 + 2 minutos con demo en vivo | **Preparada; sin ensayar** | Guion en `docs/demo/guion.md`. |

**El proyecto no está completo:** el desafío técnico central de la consigna, las oclusiones, no está resuelto. Sí está medido y explicado.

## 2. Qué se hizo (commits de `cierre-final`)

| Commit | Contenido |
|---|---|
| `a781402` | Recorrido simulado de 8 paradas (`docs/demo/recorrido-linea.json`), con selector en el panel y un test con la carga calculada a mano |
| `9814abb` | **Procesamiento progresivo**, en tres partes (detalle abajo) |
| `09e6f39` | El test del detector ajustado acepta los pesos reproducidos en Windows; antes se omitía |
| `405d523` | Docker con visión en CPU (torch, OpenCV, Ultralytics y `yolo11n.pt`), volúmenes `runs/` y `data/raw/`, y healthchecks |
| `457f59d` | Matriz, experimentos acotados, informe reescrito, READMEs y guion |
| `4e15b7c` | Registro de la verificación de Docker en Windows y autores |
| `1533328` | Prerregistro y script de la validación con PAMELA B; afiliación |
| `0320dee` | Nombre de la materia: Inteligencia Artificial |
| `5e0c810` | Resultados de la validación PAMELA B en informe, matriz y documentación; URL de las referencias que desbordaban |
| `7179890`, `98bb7ee` | Ancho de la Tabla I y PDF compilado |
| `c272311` | **Corrección del tiempo real** (detalle abajo) |
| `db262d6` | Medición de tiempo real en la RTX 2050; el progreso final se escribe antes de convertir el video |
| `c117b84`, `2dec91e` | Resumen de 147 palabras y PDF final |

**Detalle de `9814abb`:**

- **Pipeline:**
  - `--progreso` publica los cruces parciales y la medición, y se cancela si aparece un archivo `cancelar`;
  - `--ritmo-real` lee a velocidad de cámara y descarta cuadros viejos;
  - la configuración guarda los ms por etapa y la latencia.
- **API:** el trabajo corre fuera de la petición HTTP (responde 202), uno por vez (un segundo pedido recibe 409). Nuevos endpoints: `/procesamientos/{id}/estado`, `/procesamientos/{id}/cancelar` y `/procesamientos/actual`.
- **Panel:** consulta cada segundo, permite cancelar, retoma el procesamiento después de recargar y tiene la casilla «Simular cámara en vivo».

**Detalle de `c272311`:**

- el video anotado se escribe en mp4v durante el conteo y se convierte a VP8 al cerrar;
- se agrega una inferencia de precalentamiento con `predict`, que no toca el rastreador.

## 3. Evidencia y cifras (dónde verificarlas)

Todo está en `docs/relevo/2026-11-08-claude-cierre-final/` salvo indicación.

### Calidad del conteo (±1 s, TP/FP/FN)

| Evaluación | Subidas | Bajadas | F1 | Fuente |
|---|---|---|---|---|
| `prueba-bus`, prueba ciega (8 nov.) | 4/4/0 | 8/8/0 | 0,67 | `docs/relevo/2026-11-08-claude-tarea13/` |
| Bus real de YouTube, prueba final | 5/0/10 | 1/1/2 | 0,48 | `docs/relevo/2026-11-08-claude-tarea11/final-windows/` |
| **PAMELA B-No, validación prerregistrada** | 15/20/3 | 0/30/0 | 0,36 | `validacion-pamela-b/resultado/` |
| **PAMELA B-Oy, validación prerregistrada** | 19/13/4 | 0/30/0 | 0,45 | `validacion-pamela-b/resultado/` |
| Oficina (grabación de entrenamiento) | 7/0/3 | 4/0/6 | 0,71 | `resultados/experimentos/base--oficina.json` |
| Kaggle (selección) | 5/4/1 | 0/4/0 | 0,53 | `resultados/experimentos/base--kaggle.json` |
| PAMELA A (selección) | 0/1/0 | 10/0/18 | 0,51 | `resultados/experimentos/base--pamela-A.json` |

**Sobre las validaciones:**

- **Prueba ciega de `prueba-bus`:** de los 12 eventos falsos, 8 son cajas encimadas o de grupo sobre una persona ya contada (tarea 14).
- **Validación PAMELA B:**
  - **Referencias:** las anotó Álvaro (`data/annotations/pamela-B-*-cruces.json`, guardadas a las 00:16 y 00:18), antes de ejecutar (00:18–00:19) con el commit `1533328`.
  - **Causa principal:** el 83 % de los eventos sale de identificadores que cruzan varias veces, alternando subida y bajada. Es compatible con la fila que oscila sobre la línea. **No se revisó cada caso en el video anotado.**
  - **Alcance:** es la misma cámara y escena que PAMELA A, que se usó para selección. Son grabaciones nuevas, no una escena nueva.

### Modelo ajustado frente al preentrenado (tarea 10, mismo rastreador)

| Escena | Preentrenado | Ajustado |
|---|---|---|
| Oficina, su grabación de entrenamiento | 11 de 20 | 20 de 20 |
| Kaggle | 5 de 6 | 0 de 6 |
| PAMELA A | 10 de 28 | 1 de 28 |

**Decisión:** no se despliega el ajustado.

### Experimentos acotados (`experimentos.py`, un cambio por vez)

La línea base reproduce en Linux las cifras de Windows. Errores del conjunto de selección (FN + FP):

| Configuración | Errores |
|---|---|
| Línea base | 37 |
| NMS con IoU 0,5 | 37, con una regresión en PAMELA |
| 1 de cada 2 cuadros | 42 |
| 1 de cada 3 cuadros | 47 |

**Ninguno se adoptó.**

### Tiempo real (`resultados/gpu-windows/`)

**Máquina de defensa:** Ryzen 5 7535HS, RTX 2050, 16 GB, Windows 11; `prueba-bus` a 768×432 y 25 FPS.

| Ejecución | FPS | Descartados | Latencia media / p95 |
|---|---|---|---|
| GPU, panel, ritmo real, antes de `c272311` | 10,3 | 404 de 686 | 117 / 143 ms |
| GPU, todos los cuadros, sin video (diagnóstico b) | 58 | 0 | 17 / 19 ms |
| **GPU, panel, ritmo real, después de `c272311`** | **24,75** | **6 de 686** | **32 / 47 ms** (44 → 26 ms entre el primer y el último décimo) |
| CPU en Docker, ritmo real (antes de `c272311`) | 12,1 | 354 de 686 | 102 / 137 ms |

- **Conteo:** con la corrección, la GPU en ritmo real da el mismo conteo que procesando todos los cuadros.
- **En CPU:** en oficina, el ritmo real cuenta 4 de 20 cruces, frente a 11 de 20 procesando todos los cuadros.

### Tests

Linux (contenedor de Claude), con el código final: **139 aprobados, 1 fallido y 1 xfail.**

| Test | Estado | Motivo |
|---|---|---|
| `test_pipeline_modelo.py::test_ensayo_de_oficina_…` | Falla | Defecto conocido y visible a propósito: la bajada de oficina a los 4,68 s no se cuenta, porque la confianza cae a 0,02–0,09 en la puerta. No se cambió la expectativa. |
| `test_cajas_encimadas.py::…` | Xfail | Limitación conocida: varias cajas encimadas sobre una persona cuentan varios cruces. |

**Windows (verificación de Álvaro, 9 nov., 01:06, commit `b60b615`):** 139 aprobados, 1 fallido (oficina) y 1 xfail (cajas encimadas), ningún omitido, en 31,37 s. Coincide con Linux.

En la misma verificación se comprobaron otras dos cosas:

- PAMELA B-No da 15 aciertos, 3 omisiones, 50 falsos positivos y F1 de 0,3614, igual que lo informado.
- No hay videos, pesos ni contenido de `runs/` versionados.

**Esa verificación no repitió** Docker, la medición en GPU ni el recorrido manual del panel; esos resultados son los del 8 y 9 nov. citados arriba.

### Prueba de punta a punta por HTTP

Script `e2e_api.py`, salida en `resultados/e2e-api.txt`:

- la ocupación se actualizó durante la ejecución;
- un doble clic recibe 409;
- la cancelación funciona y no publica nada;
- el resultado final es idéntico a la primera evaluación.

## 4. Lo que no se hizo, y por qué

| Pendiente | Tipo | Motivo |
|---|---|---|
| Resolver oclusiones y duplicados | **No se pudo** con evidencia | Ningún cambio acotado mejoró el conjunto de selección sin regresiones. El filtro de cajas encimadas (tarea 14) eliminaba pasajeros reales. Ajustar mirando los videos de validación los invalidaría. Hacen falta datos anotados nuevos, idealmente cabezas en vista cenital. |
| Reentrenar con más escenas | **No se hizo** | Había que dibujar unas 450 cajas a mano en Kaggle y PAMELA. Las credenciales del dataset oficial de PAMELA requieren al Prof. Velastin, que no respondió. |
| Datos de Paraguay | **No se pudo** | No se consiguieron grabaciones de cámaras de buses de Paraguay accesibles para el proyecto. Es una restricción central, no un descuido. El protocolo de captura para hacerlo en el futuro está en `docs/relevo/2026-11-08-claude-tarea12/protocolo-validacion-nueva.md`. |
| Regla anti-oscilación (no contar a quien queda sobre la línea) | **No se hizo** | Diseñarla mirando PAMELA B la convertiría en desarrollo, y no queda otro conjunto reservado para validarla. |
| Construir Docker en el entorno de Claude | **No se pudo** | Docker Hub estaba bloqueado. **Lo verificó Álvaro en Windows.** |
| Compilar LaTeX en el entorno de Claude | **No se pudo** | Faltaban `IEEEtran` y `babel-spanish`, y no se permitió instalarlos. **Lo compiló Álvaro con MiKTeX.** |
| Prueba manual completa del panel en el navegador | **Parcial** | Álvaro subió y procesó `prueba-bus` en Docker y con la GPU. El recorrido completo del guion queda para el ensayo ([`docs/demo/checklist-ensayo.md`](../../demo/checklist-ensayo.md)). Claude usó `AppTest` y HTTP. |
| Suite completa en Windows con el código final | **Hecha** (9 nov., 01:06) | 139 aprobados, 1 fallido y 1 xfail, como en Linux (sección 3). |
| Origen de `prueba-bus.mp4` | **Documentado** (9 nov.) | iStock ID 1457518529, «LD Bus stopping at the station and passengers getting off it», `simonkr`, en `data/README.md` y en la referencia [16] del informe. La correspondencia se comprobó por contenido, no contra el archivo original. |
| Licencia de `prueba-bus.mp4` | **No verificada** | El archivo local es una vista previa con marca de agua. No consta una licencia adquirida, así que no se publican capturas ni se redistribuye. |
| Ensayo de la defensa | **No se hizo** | Le corresponde al equipo, con [`docs/demo/checklist-ensayo.md`](../../demo/checklist-ensayo.md). No se marca como hecho hasta que el equipo lo confirme. |
| Push o merge | **No se hizo** | Requiere autorización de Álvaro. |

## 5. Decisiones que conviene revisar

1. **No desplegar el modelo ajustado,** aunque la consigna pide un «modelo entrenado». Mostrar un modelo peor solo para cumplir la letra se descartó; el informe documenta el entrenamiento y la comparación.
2. **Las referencias de Kaggle y PAMELA A las hizo Claude** y Álvaro las revisó sin cambios. Las de PAMELA B, YouTube y `prueba-bus` las hizo Álvaro.
3. **`prueba-bus` y PAMELA B ya están consumidos:** cualquier ajuste que se haga mirándolos es desarrollo.
4. **El video anotado se convierte después de contar:** el resultado completo aparece unos 30 s después del fin del video, aunque los cruces y la ocupación se ven en vivo.
5. **El ritmo real descarta cuadros cuando el equipo no alcanza,** en lugar de acumular retraso. En CPU eso degrada el conteo, así que la demo debe usar la GPU.

## 6. Cómo verificar (sugerido para Codex)

```powershell
cd C:\Users\Alvaro\Desktop\Facultad\4to\IA\TpFinal\.worktrees\integracion-video
git log --oneline 24d873d..HEAD
.\.venv\Scripts\python.exe -m pytest -q -rxs
.\.venv\Scripts\python.exe -m evaluation.evaluate --referencia data\annotations\pamela-B-No-cruces.json --prediccion docs\relevo\2026-11-08-claude-cierre-final\validacion-pamela-b\resultado\B-No-prediccion.json
docker compose up --build -d; docker compose ps
```

**Qué debería salir:**

- `pytest`: 1 fallo (oficina) y 1 xfail (cajas encimadas); el resto aprobado.
- `evaluate`: F1 de 0,36.

**Qué revisar a mano:**

- que las cifras del informe coincidan con los JSON citados en la sección 3;
- que ningún video, peso o archivo de `runs/` esté versionado (`git ls-files | Select-String "\.(mp4|pt|webm)$"` no debe devolver nada).
