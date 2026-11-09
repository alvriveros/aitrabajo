# Manifiesto para versionar (propuesta, sin staging)

Se basa en el estado de `integracion-video` del 8 de noviembre: último commit `27fd3ce` y 162 entradas en `git status`. **Álvaro aprueba antes de cualquier `git add`.** Hay que agregar archivo por archivo o carpeta por carpeta, nunca con `git add .`.

## Siempre fuera de Git

- Videos (`data/raw/`), pesos (`*.pt`), `runs/`, `.venv/`, `venv-gpu`, `__pycache__/`, `.pytest_cache/` e informes. Todo eso ya está en `.gitignore`, salvo `venv-gpu`, que está fuera del repositorio.
- `.worktrees/_to_delete/`: son archivos comprimidos de transferencia; se pueden borrar.
- Imágenes: ninguna de las propuestas abajo tiene cuadros de Kaggle.
  - `tarea10/cuadros-a-revisar.jpg` se revisó una por una: son solo cuadros de oficina.
  - Tampoco hay capturas de PAMELA ni de YouTube.

## 1. Referencias de Kaggle y PAMELA, y evaluación externa (tarea 09)

```
data/annotations/kaggle-people-boarding-bus-cruces.json
data/annotations/pamela-A-cruces.json
docs/relevo/2026-11-07-claude-tarea09/README.md                       (modificado)
docs/relevo/2026-11-07-claude-tarea09/prueba-kaggle/                  (preregistro, resultados, evaluar_kaggle.py, linux/)
docs/relevo/2026-11-07-claude-tarea09/prueba-pamela/                  (preregistro, resultados, evaluar_pamela.py, linux/)
```

`evaluar_kaggle.py` y `evaluar_pamela.py` ya incluyen `--sha-ajustado`, que se agregó en la tarea 10. Sus resultados `linux/` se generaron antes de ese agregado, que no cambia la ejecución del modelo base. Si se quiere separar, ese agregado puede ir en el commit 2.

## 2. Tarea 10

```
docs/relevo/2026-11-08-claude-tarea10/                                (todo: README, preregistro, revisión,
                                                                       cuadros-a-revisar.jpg, entrenar-y-evaluar.ps1,
                                                                       diagnostico/, windows/)
docs/relevo/2026-11-07-claude-tarea09/scripts/evaluar_oficina.py      (modificado: --sha-ajustado)
```

`windows/06-pytest.txt` conserva el registro de la suite: 99 aprobadas, 1 omitida y 1 fallida (la bajada de oficina). El fallo queda visible.

## 3. Tarea 11

```
docs/relevo/2026-11-08-claude-tarea11/preregistro.md
docs/relevo/2026-11-08-claude-tarea11/prerregistro-final.md
docs/relevo/2026-11-08-claude-tarea11/linux/                          (selección: eventos, métricas, resúmenes)
docs/relevo/2026-11-08-claude-tarea11/final-windows/                  (prueba final)
data/annotations/youtube-bus-real-cruces.json                         (referencia original de Álvaro, SHA ad73d9d8…)
docs/relevo/2026-11-08-claude-tarea12/historico/                      (scripts tal como produjeron esta evidencia)
```

## 4. Tarea 12: correcciones, experimento y estado

```
docs/relevo/2026-11-08-claude-tarea11/evaluar_detectores.py           (corregido en t12; original en historico/)
docs/relevo/2026-11-08-claude-tarea11/anotar_cruces.py                (corregido en t12; original en historico/)
docs/relevo/2026-11-08-claude-tarea11/prueba-final.ps1                (corregido en t12; original en historico/)
docs/relevo/2026-11-08-claude-tarea11/README.md                       (con secciones rotuladas como históricas)
docs/relevo/2026-11-08-claude-tarea12/README.md, prerregistro.md, protocolo-validacion-nueva.md, manifiesto.md
docs/relevo/2026-11-08-claude-tarea12/supresion.py, clasificar_errores.py, test_supresion.py, test_herramientas.py
docs/relevo/2026-11-08-claude-tarea12/resultados-exploratorios/, clasificacion-errores.json
docs/relevo/2026-11-07-claude-tarea09/estado-para-codex.md
docs/tareas/claude/12-duplicados-y-prueba-nueva.md
docs/tareas/claude/README.md, resumen.md, data/README.md              (modificados)
```

## Nota sobre el orden

Los scripts corregidos (grupo 4) reemplazan en el mismo archivo a los que generaron la evidencia del grupo 3. Hay dos formas de mantener la trazabilidad en el historial:

- **Opción a:** commitear el grupo 3 con las versiones originales de `historico/` en sus rutas originales y aplicar las correcciones en el commit del grupo 4. Exige restaurar los archivos antes del primer commit.
- **Opción b:** commitear todo con las versiones corregidas y dejar que `historico/` documente qué se usó.

**La opción b es más simple y no pierde información.**

## 5. Tarea 13: subir y procesar un video desde el panel (agregado el 8 nov., noche)

```
api/main.py, ui/app.py                                                (modificados)
tests/test_videos.py
docs/relevo/2026-11-08-claude-tarea13/README.md
docs/relevo/2026-11-08-claude-tarea11/anotar_cruces.py                (otra vez: tiempo según la marca del archivo y --linea)
```

También son de esta tarea `docs/relevo/2026-11-08-claude-tarea12/aclaracion-referencia-final.md` y `revision-humana-referencias.md`. Se escribieron el 8 nov. a la noche, con datos que dio Álvaro.

**Fuera de Git:** `runs/videos/` y `runs/panel/`, con los videos subidos y las ejecuciones; ya están ignorados.

## 6. Tarea 14 (agregado el 8 nov., noche)

```
tests/test_cajas_encimadas.py
docs/relevo/2026-11-08-claude-tarea14/                                (README, scripts, tracks/, resultados/, experimento/)
docs/relevo/2026-11-08-claude-tarea13/registro-prueba-bus.md, primera-evaluacion/
data/annotations/prueba-bus-cruces.json                               (referencia de Álvaro, SHA 0640f227…)
```

`data/raw/prueba-bus.mp4` queda fuera de Git, igual que los demás videos. Es un video de stock con marca de agua de iStock; habría que revisar su licencia antes de publicar capturas.

También va en el grupo 6: `docs/relevo/2026-11-08-claude-cierre/README.md` y la revisión del tramo agregada en `docs/casos-deteccion/oficina-bajada-omitida/README.md`.

**Aplicado el 8 nov., noche:** los grupos se commitearon por separado (ver la tabla de `docs/relevo/2026-11-08-claude-cierre/README.md`), con la opción b de la nota sobre el orden y sin convertir los line endings.
