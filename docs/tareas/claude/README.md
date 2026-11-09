# Tareas para Claude · 5 de noviembre de 2026

Trabajás con Álvaro sobre la copia de `main` del repositorio privado [aitrabajo](https://github.com/alvriveros/aitrabajo). Su compañero lleva detección y seguimiento en `vision`. La entrega interna es el domingo 8 a las 18:00 de Paraguay.

La API calcula la ocupación por parada y sus siete pruebas pasan en Linux y Windows. El panel carga recorridos JSON, muestra el gráfico y arranca junto con la API usando Docker. El siguiente avance es preparar el borrador del informe y el guion de defensa.

1. **Completada y verificada.** [Carga de un recorrido en el panel](01-cargar-recorrido.md), comprobada en Linux y Windows.
2. **Disponible para ejecutar el 6 de noviembre.** [Verificación del primer clip](02-verificar-clip.md). Ya existe una referencia manual aproximada del video de oficina.
3. **Completada y revisada.** [Gráfico del panel y arranque con Docker](03-panel-docker.md). Once registros del panel coinciden en Windows y Linux.
4. **Borrador entregado.** Consultá [el informe IEEE y el guion de demo](04-informe-demo.md). Documentá el sistema disponible y los resultados que falta recibir de visión.

Leé [el resumen del proyecto](../../../resumen.md) antes de editar. Guardá tu devolución en una carpeta nueva bajo `docs/relevo/` con la tarea realizada, archivos cambiados, entorno, comando y salida de las pruebas, diferencias observadas y pendientes. Dejá los cambios listos para que Álvaro los revise y publique.

**Prioridad tras el ensayo del 6 de noviembre:** la tarea 02 verificó los eventos y la API, y detectó una discrepancia en el gráfico. Continuá con la [tarea 05 · Sincronizar las barras](05-actualizacion-grafico.md).

**Prioridad vigente:** continuá con la [tarea 07 · Conectar el video con el conteo automático](07-demo-video.md). El informe académico se retoma al finalizar el proyecto.

**Prioridad vigente · 7 de noviembre:** [Tarea 08 · Cierre de integración en Windows](08-cierre-integracion-windows.md). Reemplaza la prioridad 07: revisar el final temporal del clip, las ejecuciones incompletas y guardar evidencia Windows. Informes aplazados.

**Siguiente tarea:** [09 · Evaluación en Windows](09-evaluacion-windows.md). Comparar modelos y preparar datos independientes; informes aplazados.

**Estado 09 (Claude, 7 nov.):** comparación del modelo base hecha en Linux y Windows (eventos idénticos); pesos ajustados pendientes. Ver [la devolución](../../relevo/2026-11-07-claude-tarea09/README.md).

**Estado 10 (Claude, 8 nov.):** el ajuste reproducido con oficina no se transfiere: 0 de 6 subidas en Kaggle y 0 o 1 de 28 bajadas en PAMELA. No hay base para cambiar de modelo. Ver [la devolución](../../relevo/2026-11-08-claude-tarea10/README.md).

**Estado 11 (actualizado tras la prueba final, 8 nov.):** `yolo11l` fue seleccionado con 21 errores en Kaggle y PAMELA A frente a 28 de la API. En la prueba final con referencia de Álvaro produjo 18 errores frente a 13 de `yolo11n`: la API no cambia. YouTube ya no está reservado como prueba ciega. Ver [la devolución](../../relevo/2026-11-08-claude-tarea11/README.md).

**Prioridad vigente · 8 de noviembre:** [Tarea 12 · Evaluar supresión de duplicados sin cambiar la API](12-duplicados-y-prueba-nueva.md). Corregir trazabilidad, evaluar la hipótesis temporal solo en Kaggle/PAMELA y preparar una prueba nueva. Sin staging, commit, push ni merge; informes aplazados.

**Estado 12 (Claude, 8 nov.):** exploratorio, con referencias de Claude sin revisar. **La supresión temporal global no se justifica:** toda variante que baja el total borra cruces reales de PAMELA. Casi todos los falsos de Kaggle y PAMELA son oscilaciones del mismo ID. Se corrigieron el anotador y el arnés, y quedan preparados el protocolo de validación nueva y el manifiesto. API sin cambios. Ver [la devolución](../../relevo/2026-11-08-claude-tarea12/README.md).

**Estado 13 (Claude, 8 nov., noche):** el panel ya permite subir y procesar un video nuevo («Video nuevo»), con vista previa de la geometría sin inferencia, la configuración de la API, sin duplicados y con descargas. Siguen funcionando la demo de oficina y la carga de JSON. Sin commit. Ver [la devolución](../../relevo/2026-11-08-claude-tarea13/README.md).

**Estado 14 (Claude, 8 nov., noche):** de los 12 falsos de `prueba-bus`, inspeccionados uno por uno, 8 son cajas encimadas o de grupo sobre una persona ya contada y el resto, saltos de ID u oscilación. No vienen de la regla de cruce. Un filtro de cajas encimadas bajó los falsos positivos, pero borró cruces reales (PAMELA A y `prueba-bus`), así que **quedó fuera de la entrega**. La limitación queda visible como *xfail*. La demo en la página está verificada, sin reprocesar al recargar. Sin commit. Ver [la devolución](../../relevo/2026-11-08-claude-tarea14/README.md).

**Cierre (Claude, 8 nov., noche):**
- **Versión de entrega:** sin filtros, sin cambios en `vision/`.
- **Demo principal:** `prueba-bus` desde la página, con sus errores medidos.
- **Oficina:** queda como caso documentado de bajada omitida.
- **Tests en Windows:** 129 aprobados, **1 fallido** (oficina), **1 omitido** (pesos ajustados) y **1 xfail** (cajas encimadas).

Ver [el cierre](../../relevo/2026-11-08-claude-cierre/README.md).
