# Tarea 09 · Comparar modelos en Windows y preparar evaluación independiente

Trabajar en integracion-video, conservando los cambios de la tarea 08. Sin commit, push ni merge durante esta tarea. Informes académicos aplazados. No añadir funciones al panel mientras el pendiente principal sea el detector.

## Primero: cerrar la evidencia 08

Leer docs/relevo/2026-11-07-claude-tarea08/ y la revisión Windows de Codex. Actualizar las secciones que todavía dicen pendiente de Windows con resultados comprobados, sin confundir la prueba de integración con calidad del conteo. Los resultados experimentales de cabezas siguen siendo de Linux y de una única grabación.

## Trabajo que puede avanzar sin el compañero

1. Preparar la comparación reproducible del modelo base en Windows sobre el video completo de oficina: mismos recorte, línea, configuración y referencia existentes. Guardar eventos, configuración, tiempo, FPS, versiones y hashes. Evaluar con evaluation.evaluate y conservar TP, FP, FN y error de conteo separados por sentido. No cambiar umbrales ni pruebas para mejorar cifras.
2. Revisar la referencia existente: indicar cómo se obtuvo y qué revisión humana falta. No llamar evaluación independiente al video de oficina usado para ajustes.
3. Preparar una ficha breve para una grabación nueva: cámara fija arriba de una puerta, toma continua, ambas direcciones, pausas sin cruces y, si es viable, dos personas y oclusiones. Registrar consentimiento de participantes, duración, FPS, resolución, orientación interior/exterior y tiempos manuales. No usar fragmentos de la misma toma en entrenamiento y prueba. Es una ficha de adquisición y anotación, no un informe académico.
4. PCDS permanece bloqueado: no repetir descargas bloqueadas ni cambiar de dataset sin comprobar acceso y correspondencia entre videos RGB y etiquetas.

## Cuando lleguen los pesos ajustados

Usar el pedido-vision.md de la tarea 08: localizar el archivo y comprobar hash, configuración recomendada y procedencia. Si falta, pedir a Álvaro la ruta exacta una vez; continuar el trabajo independiente y dejar la comparación ajustada pendiente. No descargar pesos de origen desconocido ni volver a entrenar por defecto.

Ejecutar base y ajustado en Windows, tanto en 0–6 s como en el video completo, con configuraciones declaradas y sin mezclar resultados. Si cambia el rastreador, aclarar que se comparan sistemas completos, no solo detectores. Conservar JSON, videos locales y métricas por sentido. En una grabación realmente nueva, reservar la prueba antes de ajustar parámetros y medir también omisiones y eventos extra; no basta el saldo final de pasajeros.

Recomendar un modelo/configuración solo con el alcance demostrado. No reemplazar aún la configuración usada por la API: entregar la propuesta y sus evidencias para revisión. No incorporar TensorFlow ni el SSD externo a producción. Si no hay datos independientes o pesos, dejarlo explícito sin presentar como concluida esa parte.

## Entrega

Crear docs/relevo/2026-11-07-claude-tarea09/ con comandos, resultados por entorno, archivos cambiados y pendientes concretos. Actualizar resumen.md y el índice. No guardar pesos o videos en Git. Dejar un mensaje listo para el compañero con los insumos que aún faltan, sin enviarlo automáticamente.
