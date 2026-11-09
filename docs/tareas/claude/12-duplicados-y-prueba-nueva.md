# Tarea 12 · Evaluar supresión de duplicados sin cambiar la API

Trabajá en `integracion-video`, conservando los cambios pendientes de las tareas 09–11. En Windows el worktree está en `.worktrees/integracion-video`; la raíz principal está en otra rama. No cambies de rama ni descartes trabajo.

**Restricciones de Álvaro:** no cambiar API, Docker ni panel; no entrenar en esta tarea; nada de staging, commit, push ni merge hasta su aprobación. Informes académicos aplazados. Videos, pesos, entornos y `runs/` quedan fuera de Git.

## Contexto y lectura

Leé `docs/relevo/2026-11-08-claude-tarea11/`, incluidos ambos prerregistros, `evaluar_detectores.py`, `anotar_cruces.py`, `prueba-final.ps1` y los resultados `linux/` y `final-windows/`. Consultá también la tarea 10, las tres referencias nuevas y `evaluation/evaluate.py`, `vision/cruces.py` y `vision/pipeline.py`.

Codex comprobó las 16 evaluaciones de tarea 11 desde los eventos: coinciden exactamente con los JSON guardados y los hashes de las referencias. Pasaron 31 tests de `test_evaluate.py` y `test_cruces.py`. Esto no sustituye la revisión visual ni la suite completa: el registro de tarea 10 conserva 99 aprobados, 1 omitido y 1 fallido por la bajada de oficina.

- Selección en Kaggle y PAMELA A: yolo11l calibrado, 21 errores; yolo11n calibrado, 28. Referencias de Claude pendientes de revisión humana.
- Prueba final con referencia de Álvaro: yolo11n, TP/FP/FN = 6/1/12, 65,88 FPS; yolo11l, 12/12/6, 23,94 FPS. **La API no cambia**, según el criterio prerregistrado.
- `youtube-bus-real` ya se utilizó. No volver a usarlo para elegir parámetros ni presentarlo como prueba ciega de una mejora.
- Hay indicios de duplicación por cambios de ID, pero no está demostrado que todo sea rastreo: el ID 10 sube a 34,12 s y baja a 34,32 s. Separar fragmentación, oscilación, errores temporales y omisiones; no afirmar que la detección está resuelta.

## 1. Conservar y aclarar la evidencia

No editar los eventos, métricas, referencias originales ni prerregistros históricos. Agregar aclaraciones posteriores con fecha y procedencia, sin hacerlas pasar por decisiones previas.

Actualizar el estado vigente en `resumen.md`, `docs/tareas/claude/README.md`, `data/README.md` y el README de tarea 11: prueba final ejecutada, API sin cambios, Kaggle/PAMELA A usados para selección y YouTube final consumido. Rotular las secciones históricas que dicen pendiente o reservado. No alterar retrospectivamente los prerregistros.

La referencia final tiene `notas: []`, aunque difiere del contador comercial (18 cruces frente a 16) y el prerregistro pedía explicar el motivo. Solicitar la aclaración a Álvaro y guardarla por separado como posterior; no inventarla ni modificar la referencia que identifica el hash de la ejecución.

## 2. Corregir las herramientas de experimentación

- En `anotar_cruces.py`, corregir el retroceso cuadro a cuadro: `ir(cuadro - 2)` retrocede dos cuadros; verificar también A/D con la posición real de OpenCV. Agregar una comprobación pequeña de navegación.
- Al continuar una anotación, preservar notas y metadatos. No volver a afirmar automáticamente que fue hecha antes de ejecutar modelos. Proteger la referencia histórica de YouTube: permitir otra salida y rechazar su sobrescritura accidental. Validar apertura del video y FPS antes de usarlos.
- En `prueba-final.ps1` y el arnés que vaya a reutilizarse, rechazar destinos con resultados existentes antes de ejecutar o escribir. Guardar futuras ejecuciones en carpetas nuevas. No volver a correr la prueba final de tarea 11.
- Mantener estas correcciones fuera de la API y del conteo de producción. Probarlas sin inferencia ni apertura de la referencia histórica para escritura.

## 3. Experimento mínimo de supresión temporal

La hipótesis de Álvaro es evitar dos cruces del mismo sentido separados por aproximadamente 1,5 s. **No asumir que ese umbral es válido:** Kaggle tiene subidas a 13,2 y 14,4 s; PAMELA tiene bajadas simultáneas a 19,8 s y muchas separadas por menos de 1,5 s. Un filtro global puede borrar pasajeros distintos.

Antes de calcular resultados filtrados, escribir un nuevo prerregistro bajo `docs/relevo/2026-11-08-claude-tarea12/`:

1. Usar exclusivamente Kaggle y PAMELA A para desarrollar y elegir. Pedir revisión humana de sus referencias; conservar originales y guardar revisiones en archivos nuevos con sus cambios y hashes. Si falta esa revisión, avanzar con las herramientas y, si se evalúa con las referencias de Claude, rotular todo como exploratorio y dejar la selección definitiva pendiente.
2. Probar solo yolo11n calibrado y yolo11l calibrado sobre los eventos ya guardados en Linux, sin repetir inferencias. Fijar una lista pequeña de umbrales antes de medir, incluyendo 0 (sin filtro) y 1,5 s. No ampliar la búsqueda para perseguir un resultado favorable.
3. Especificar la regla exacta: orden temporal, comparación por sentido, condición estricta o inclusiva, qué evento se conserva y si el intervalo se mide desde el último aceptado o desde el último observado. Elegir una sola variante antes de medir y probar cadenas de eventos, simultáneos, límite exacto y sentidos opuestos.
4. Mantener tolerancia de evaluación ±1 s. Informar TP, FP, FN y error absoluto por escena y sentido; conservar eventos descartados para inspección. No usar solo saldo o error de conteo.
5. Comparar cada variante con su mismo detector sin filtro y con la API actual. Elegir por errores totales, luego error absoluto por sentido, luego menor umbral. Exigir que no aumenten las omisiones en ninguna escena/sentido respecto del mismo detector sin filtro. Si ninguna variante mejora bajo esa condición, concluir que la supresión temporal global no se justifica; es un resultado válido.

No calcular una nueva puntuación de YouTube para elegir el filtro. El valor de 1,5 s surgió después de ver esa prueba y debe reconocerse como hipótesis posterior.

Los eventos actuales solo contienen tiempo, ID y sentido. No describir este filtro como espacial ni como identificación de la misma persona. Si fracasa, proponer como siguiente experimento registrar posiciones y trayectorias locales para estudiar continuidad espacial; no implementar de inmediato otro rastreador o una búsqueda de más parámetros.

## 4. Preparar una validación realmente nueva

Preparar el protocolo, sin descargar o elegir automáticamente material ya inspeccionado por modelos. Solicitar a Álvaro una grabación nueva con ambos sentidos, cruces próximos, oclusiones y pausas sin cruces. Anotar antes de inferir, fijar geometría, hash, tolerancia y criterio de decisión, y congelar el candidato antes de abrir sus resultados.

Comparar candidato contra API actual en el mismo entorno. El criterio debe exigir menos FN+FP y al menos 10 FPS, además de mostrar los resultados por sentido. Ningún resultado autoriza cambiar la API en esta tarea: entregar evidencia para revisión. Si falta video, referencia humana o candidato justificable, dejar esta fase pendiente y completar el resto.

## 5. Preparar qué se versionará, sin ejecutar Git de escritura

Entregar un manifiesto de rutas para revisión, agrupado así:

1. Referencias Kaggle/PAMELA y evaluación externa pendiente de tarea 09: prerregistros, scripts, eventos, configuraciones y métricas.
2. Tarea 10: reproducción, diagnóstico, registros de entrenamiento/pruebas y soporte `--sha-ajustado` en sus scripts dependientes. Mantener visible el test fallido.
3. Tarea 11: prerregistros, scripts originales, selección Linux, prueba Windows y referencia original de Álvaro.
4. Tarea 12: correcciones posteriores, experimento, tests y actualizaciones de estado. Distinguir estos cambios de las versiones de scripts usadas para producir la evidencia histórica; conservar una copia identificada de esas versiones antes de editarlas si aún no están versionadas.

Excluir videos, pesos, `runs/`, cachés, entornos e informes. Revisar imágenes individualmente: no incorporar capturas de Kaggle; no usar `git add .`. No hacer staging ni commits: Álvaro aprueba primero el contenido concreto.

## Entrega

Guardar en `docs/relevo/2026-11-08-claude-tarea12/` el prerregistro nuevo, scripts y pruebas pertinentes, comandos, entorno, hashes, resultados exploratorios o definitivos claramente separados, manifiesto de archivos y pendientes humanos. Una devolución breve debe decir si la supresión temporal ayuda sin borrar cruces reales y qué falta para validar. No presentar como solución un filtro que solo mejora el total ocultando omisiones.
