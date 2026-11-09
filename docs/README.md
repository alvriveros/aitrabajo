# Documentación del proyecto

Índice de `docs/`.

- **Vigente:** describe la versión de entrega (rama `cierre-final`).
- **Histórico:** se conserva tal como se escribió en su fecha. Puede mencionar estados ya superados y no debe leerse como estado actual.

## Vigente

| Qué | Dónde |
|---|---|
| Informe IEEE final (PDF y fuente) | [`informe/`](informe/): `informe.pdf`, `informe.tex`, `referencias.bib` y `README.md` |
| Estado del proyecto frente a la consigna | [`relevo/2026-11-08-claude-cierre-final/matriz.md`](relevo/2026-11-08-claude-cierre-final/matriz.md) y [`auditoria-final.md`](relevo/2026-11-08-claude-cierre-final/auditoria-final.md) |
| Resumen para revisión externa | [`relevo/2026-11-08-claude-cierre-final/ESTADO-PARA-CODEX.md`](relevo/2026-11-08-claude-cierre-final/ESTADO-PARA-CODEX.md) |
| Evidencia del cierre (experimentos, GPU, Docker, PAMELA B) | [`relevo/2026-11-08-claude-cierre-final/`](relevo/2026-11-08-claude-cierre-final/) |
| Defensa: guion, checklist y ensayo técnico | [`demo/`](demo/): `guion.md`, `checklist-ensayo.md` y `ensayo-tecnico-codex-2026-11-09.md` |
| Recorridos de demo (JSON) | [`demo/recorrido.json`](demo/recorrido.json) (2 paradas) y [`demo/recorrido-linea.json`](demo/recorrido-linea.json) (8 paradas, simulado) |
| Casos de detección documentados | [`casos-deteccion/`](casos-deteccion/): bajada omitida en oficina y comparación de repositorios |

La presentación y la guía del orador para la defensa se mantienen **fuera del repositorio**, a pedido del equipo.

## Histórico

| Qué | Dónde |
|---|---|
| Registros de trabajo por fecha y tarea (relevos) | [`relevo/`](relevo/): una carpeta por tarea, con la fecha en el nombre (`2026-11-04-…` a `2026-11-08-…`), además de `vision-primer-clip/` y `vision-ajuste-detector/` |
| Consignas de cada tarea | [`tareas/claude/`](tareas/claude/) y [`tareas/vision/`](tareas/vision/) |
| Plan inicial de entrega | [`PLAN.md`](PLAN.md) |
| Borrador anterior del informe y aportes de visión | [`informe/informe-borrador.pdf`](informe/informe-borrador.pdf) y [`informe/aportes-vision.md`](informe/aportes-vision.md) |

Los registros no se movieron ni se reescribieron, porque tienen enlaces cruzados entre sí y con el código. Cuando uno quedó desactualizado, se le agregó una aclaración fechada en lugar de cambiar lo que había ocurrido.
