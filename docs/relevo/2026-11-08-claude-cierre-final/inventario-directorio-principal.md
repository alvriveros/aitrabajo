# Inventario del directorio principal (`TpFinal`, rama `tareas-03-04-panel-informe`) · 9 nov., 01:25

Solo se inventaría: no se incorporó, no se descartó y no se borró nada. Decide el equipo.

## Ramas

Todas las ramas locales y remotas están contenidas en `cierre-final`: `main`, `integracion-video`, `tareas-03-04-panel-informe`, `vision` y sus `origin/*`. Se comprobó con `git merge-base --is-ancestor`. `main` está 0 commits por delante y 36 por detrás de `cierre-final`, así que la integración es un avance directo (*fast-forward*).

## Cambios sin commit en el directorio principal

| Ruta | Estado | ¿Está en `cierre-final`? | Comentario |
|---|---|---|---|
| `docs/informe/grafico-demo.png` | Modificado (28 → 72 KB) | No con este contenido | Gráfico del borrador anterior (tarea 06). El informe final no lo usa. |
| `docs/informe/informe-borrador.pdf` | Modificado (148 → 192 KB) | No con este contenido | Borrador compilado en la tarea 06. El PDF vigente es `informe.pdf` en `cierre-final`. |
| `docs/tareas/claude/README.md` | Modificado (+4 líneas) | No | Prioridades del 7 nov. (tareas 08 y 09). Histórico. |
| `resumen.md` | Modificado (+11 líneas) | No | Notas de revisión del 7 nov. (tarea 08 y Codex). Histórico. |
| `docs/relevo/2026-11-06-claude-tarea06/` (README, `pytest.txt`, `verificacion-linux.txt`, `linux/`, `revision-pdf/`, `grafico-demo.png`) | Sin seguimiento | No | Evidencia de la tarea 06: capturas y páginas del borrador. Incluye PNG. |
| `docs/tareas/claude/06-cierre-grafico-windows.md` | Sin seguimiento | No | Consigna de la tarea 06. |
| `docs/tareas/claude/08-cierre-integracion-windows.md`, `09-evaluacion-windows.md` | Sin seguimiento | **Sí, idénticos** | Ya versionados en `cierre-final`. |
| `.claude/launch.json`, `.mcp.json` | Sin seguimiento | No | Configuración local de herramientas. `.mcp.json` define el gateway MCP de Docker con rutas de Windows. **No conviene versionarlos.** |

## Sugerencia, sin ejecutar

1. **Ya están en `cierre-final`:** los documentos 08 y 09. Se pueden dejar como están o borrar en el directorio principal.
2. **Si interesa conservar la evidencia histórica de la tarea 06** (`docs/relevo/2026-11-06-claude-tarea06/` y `docs/tareas/claude/06-…`): incorporarla en un commit aparte sobre `cierre-final`, después de revisar que las capturas no incluyan material con licencia dudosa.
3. **Los cambios a `resumen.md`, `docs/tareas/claude/README.md` y los binarios del borrador** quedaron reemplazados por la documentación vigente de `cierre-final`. Si se quieren conservar, conviene guardarlos con `git stash` antes de cambiar de rama.
4. **`.claude/` y `.mcp.json`:** agregarlos a `.gitignore` o dejarlos sin seguimiento.
