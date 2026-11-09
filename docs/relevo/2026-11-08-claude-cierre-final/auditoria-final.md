# Auditoría final contra `contexto.md` · 9 nov. 2026, 01:50

Auditoría independiente de Claude sobre `cierre-final` (`e7fe1a5` y esta corrección). Se releyó la consigna y se contrastó cada punto con el repositorio y la evidencia, no solo con la matriz.

## Veredicto

**Entregable como prototipo funcional con limitaciones medidas. No están resueltos todos los objetivos.** Se cumplen los 6 entregables de ingeniería. El objetivo técnico del Proyecto 10 se cumple solo en parte: el conteo y la ocupación funcionan, pero no se superan las oclusiones y la adaptación al contexto local quedó limitada por los datos. Falta el ensayo oral.

## Directivas generales y entregables

| Punto de `contexto.md` | Veredicto | Evidencia comprobada en esta auditoría |
|---|---|---|
| Trabajo en parejas | **Cumple** | Autores en el informe: Maldonado Riveros y Porath Ramirez. En Git: 49 commits de Álvaro y 3 de Ander Porath (en `vision/`). La mayor parte del cierre está a nombre de Álvaro, con coautoría de Claude. |
| 1. Investigación e ingesta: dataset relevante para el entorno local | **Parcial** | `data/README.md`: 7 grabaciones con origen, hash, licencia o permisos, partición y referencias revisadas por personas. **No se consiguió material suficiente, accesible y adecuado de buses, en especial paraguayo**; se usaron oficina y puertas de tren, además de los pocos videos de bus disponibles. |
| 2. Modelo con métricas formales | **Parcial, justificado** | Hubo entrenamiento (YOLO11n ajustado, mAP50 de 0,995 en una reserva de la misma grabación). No generaliza (Kaggle 0 de 6, PAMELA A 1 de 28), así que se despliega el preentrenado con ByteTrack calibrado. Métricas formales: P, R y F1 por sentido (`evaluation/evaluate.py`), además de FPS y latencia. |
| 3. API REST (FastAPI) | **Cumple** | `api/main.py`: ocupación, videos, procesamientos en segundo plano, estado, cancelación y descargas. Tests aprobados en Windows. |
| 4. Interfaz para pruebas en tiempo real | **Cumple** | `ui/app.py`: subida, geometría, procesamiento con resultados en vivo y recorrido de 8 paradas. Ensayo técnico en el navegador realizado (`docs/demo/ensayo-tecnico-codex-2026-11-09.md`). |
| 5. Docker con un solo comando | **Cumple el empaquetado** | `docker compose up --build` (requiere `yolo11n.pt` en la raíz, como dice el README). Álvaro lo verificó en Windows. Corre en **CPU**: no demuestra tiempo real. |
| 6. Git con commits descriptivos | **Cumple** | Ningún mensaje genérico; ningún video, peso ni `runs/` versionado; `main` está contenida en `cierre-final`. |
| Informe IEEE de dos columnas, exactamente 3 páginas | **Cumple** | `informe.pdf` (`8ffa96c`): 3 páginas A4 y 16 referencias. |
| Resumen de hasta 150 palabras | **Cumple** | 150 palabras (justo en el límite). |
| I. Introducción enfocada en Paraguay y estado del arte | **Cumple** | Reforma de 2025, Decreto 5969 y cinco trabajos citados. |
| II. Metodología: pipeline, preprocesamiento, entrenamiento, API y UI | **Cumple** | II-A a II-D y Fig. 1. |
| III. Resultados con métricas, tablas o gráficos y tiempos de inferencia | **Cumple** | Tablas II y III. **Se recalcularon todas las cifras de la Tabla II desde los JSON de evidencia y coinciden.** No hay matriz de confusión; la consigna la da como ejemplo, no como obligación. |
| IV. Conclusiones, limitaciones y trabajo futuro | **Cumple** | Sección IV. |
| Referencias en formato IEEE | **Cumple** | `IEEEtran.bst`; URL, DOI y fecha de acceso. |
| Defensa de 10 + 2 minutos con demo en vivo | **Preparada; ensayo oral pendiente** | Guion, checklist y ensayo técnico (GPU, 682 de 686 cuadros, 24,84 FPS). Falta el ensayo oral cronometrado del equipo. |

## Proyecto 10

| Punto | Veredicto | Evidencia |
|---|---|---|
| Contar ingreso y egreso en la puerta | **Cumple** (funcional) | Prueba ciega en un bus: 12 de 12 cruces detectados, pero 12 eventos falsos (F1 de 0,67). |
| Porcentaje de ocupación en tiempo real | **Cumple con GPU nativa; no en CPU ni en Docker** | 680 de 686 cuadros a 24,75 FPS, con latencia interna media de 32 ms que no crece; el panel consulta cada 1 s. En CPU se descartan cuadros y se pierden cruces. |
| Seguimiento (ByteTrack) cruzando una línea virtual | **Cumple** | `vision/cruces.py` y `pipeline.py`, con tests de cruce, regreso, oscilación, dos personas, cambio de ID y oclusión con recuperación. |
| Superar oclusiones cuando varias personas suben a la vez | **No cumple** | Validación prerregistrada con PAMELA B: F1 de 0,36 y 0,45. El 83 % de los eventos sale de ID que cruzan varias veces. Las correcciones probadas no mejoraron el conjunto de selección. |
| Módulo de visualización simulado de la carga a lo largo del recorrido | **Cumple** | `docs/demo/recorrido-linea.json`: 8 paradas, rotulado como simulado, con sobreocupación del 105 %. |

## Correcciones hechas en esta auditoría (solo documentación)

- **`docs/informe/README.md`:** el estado del PDF citaba la compilación de las 00:36; ahora cita la de las 01:22 (`8ffa96c`).
- **Matriz (R12):** el mismo dato, más la verificación de la Tabla II.
- **Estado para Codex:** la fila de Kaggle (Linux, 5/4/1 y 0/4/0) ahora aclara que el informe usa la cifra de Windows (5/5/1 y 0/3/0). Las dos son reales y tienen el mismo F1.

## Riesgos para la defensa

1. **Oclusiones:** es la pregunta más probable. Hay que responderla con la validación de PAMELA B.
2. **«Modelo entrenado»:** el modelo desplegado es el preentrenado. Hay que mostrar la comparación con el ajustado de la tabla II.
3. **Tiempo real:** usar la GPU nativa. Docker no lo demuestra.
4. **Cifras de `prueba-bus`:** en GPU dio 25 eventos; las históricas, en CPU, son 24. Hay que leer el id de la ejecución.
5. **Licencia de `prueba-bus`:** no está verificada. No se proyectan capturas fuera de la demo local.
6. **Margen de tiempo:** el resumen tiene 150 palabras y la tercera página está llena. Cualquier agregado obliga a recortar.

## Pendiente real

- **Ensayo oral y firma del checklist.** Después, con autorización, push de `cierre-final` y PR hacia `main`; el merge es una decisión aparte.
- **Limitaciones técnicas, no tareas de esta versión:** oclusiones y duplicados, y datos de buses (en especial paraguayos).
