# 04 · Preparar el informe IEEE y el guion de la demo

Disponible el 5 de noviembre de 2026. Trabajá con Álvaro en su copia local de `main`. Hay cambios de la tarea 03 revisados y todavía sin commit. Conservá ese trabajo al preparar esta entrega. El cierre interno del proyecto es el domingo 8 a las 18:00 de Paraguay.

## Objetivo y fuentes

Preparar un borrador editable del informe y un ensayo de la defensa usando el sistema disponible. El informe vale 20 puntos y la defensa con demo 50. Leé `contexto.md`, `resumen.md`, el README y los relevos de las tareas 01 y 03. La referencia de oficina es un conteo manual aproximado. Los eventos sintéticos y manuales permiten verificar la aplicación; las métricas del detector y del seguimiento siguen pendientes de la entrega de `vision`.

## Informe en dos columnas

- En `docs/informe/`, entregá `informe.tex`, `referencias.bib`, `README.md` con el comando de compilación y `informe-borrador.pdf`. Usá la clase oficial IEEEtran en formato conference, A4 y dos columnas. Marcá el documento como borrador de trabajo.
- Organizá exactamente las secciones de la consigna: resumen de hasta 150 palabras, introducción y contexto, metodología y arquitectura, resultados y discusión, conclusiones y trabajo futuro, referencias IEEE.
- Explicá el problema del transporte público del Gran Asunción sin atribuir cifras que no tengan una fuente comprobada. Describí como implementados la API, el contrato de eventos, cálculo por parada, panel, carga de JSON y Docker.
- Mostrá un diagrama pequeño que distinga el módulo de visión pendiente de la ruta ya implementada: JSON de eventos → API → ocupación por parada → panel. Describí detector, seguimiento y línea como integración prevista.
- En resultados, documentá las pruebas funcionales realmente verificadas: siete pruebas de API y los casos de interfaz de los relevos. Indicá que verifican el software de ocupación. Para las mediciones de visión, creá una lista de pendientes en `docs/informe/README.md` con dato requerido, responsable y sección a actualizar.
- Citá fuentes primarias consultadas para la metodología propuesta y las herramientas. Verificá título, autores cuando existan, enlace y año. Registrá el video de oficina como fuente del ensayo y explicá su carácter simulado.
- Prepará una maqueta de exactamente tres páginas y comprobá el PDF renderizado, incluidas tablas, figura, referencias y cortes de columna. Si falta un compilador, entregá la fuente y registrá claramente la compilación pendiente. Tras incorporar las métricas reales habrá que comprobar nuevamente las tres páginas.

## Demo de diez minutos

En `docs/demo/guion.md`, escribí un guion ejecutable con tiempos y responsables:

1. Álvaro, 0–2 min: problema, objetivo y arquitectura.
2. Compañero, 2–5 min: detección, seguimiento y un caso de oclusión. Indicá qué material debe aportar para este bloque.
3. Álvaro, 5–8 min: abrir el panel Docker en 8502, cargar la demo, mostrar 3 → 5 → 4 pasajeros, revisar la tabla y el gráfico, y cambiar la capacidad para explicar el porcentaje. Prepará también el ensayo de oficina 0 → 1 → 0, identificándolo como referencia manual.
4. Compañero, 8–10 min: comparación con conteo manual, error observado y limitaciones. Indicá las mediciones pendientes.

Incluí una preparación previa breve: iniciar Docker Desktop, arrancar Compose, comprobar API y panel, disponer localmente de clips, pesos y JSON, y probar el recorrido antes de exponer. Prepará seis preguntas probables con respuestas basadas en lo implementado o con el dato que todavía debe aportar visión.

## Aceptación y devolución

- Verificá que las afirmaciones del borrador correspondan al código o a las evidencias citadas. Reconciliá las notas históricas del resumen: la revisión posterior ya comparó 11 registros del panel en Windows con Linux.
- Abrí el PDF, verificá tres páginas y el límite del resumen, y guardá evidencia de la revisión visual. Dejá explícito qué contenido requiere actualización para la entrega final.
- Ensayá el bloque de Álvaro contra la aplicación real y registrá duración, pasos y valores observados. Si el sistema está detenido, iniciá los servicios según el README. Separá ese tiempo del ensayo completo, que requiere al compañero.
- Guardá el relevo en `docs/relevo/2026-11-05-claude-tarea04/` con archivos nuevos y modificados, comandos, entorno, resultados y pendientes. Actualizá `resumen.md`.
- Dejá los cambios sin commit para revisión de Álvaro. La tarea 02 continúa pendiente de los eventos de visión.
