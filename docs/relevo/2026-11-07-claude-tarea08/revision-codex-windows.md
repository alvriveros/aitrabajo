# Revisión de Codex · tarea 08 · Windows · 7 de noviembre de 2026

Se revisaron api/main.py, ui/app.py, tests/test_procesamientos.py y el script verificar-windows.ps1 antes de ejecutarlo. No se modificó código de aplicación. Se ejecutó el script entregado por Claude desde la copia local, con permisos para procesos, Git y navegador.

- Worktree: al comenzar ya apuntaba a Windows; git worktree repair fue idempotente. Rama integracion-video, HEAD b511d91, cambios de Claude sin commit. La carpeta principal conserva su rama y modificaciones.
- API: 15 pruebas aprobadas.
- Visión: 84 aprobadas, 1 omitida (pesos ajustados ausentes) y 1 fallida (bajada omitida del modelo base). Total: 99 aprobadas, 1 omitida, 1 fallida. No declarar la batería completa aprobada.
- Video: ejecución nueva 20261107-204212-090885. Verificador exit 0, sin fallos. Video de 6 s, 222x176, avanzó 1,5158 s, sin error. Selector hasta 6 s: a 0 / 2,16 / 4 / 6, muestra 0 / 1 / 1 / 1 pasajeros. La captura a 6 s fue inspeccionada: indicador, barra y tabla coinciden en 1 pasajero, 5 %.
- Inferencia: 150 cuadros en 7,644 s (19,62 FPS), con video anotado. Predicción: una subida a 2,16 s. La omisión de bajada permanece.
- Entorno: Windows 11, Ryzen 5 7535HS, Python 3.12.10; versiones y hashes en windows/02-entorno.txt.

La ejecución reemplaza archivos de windows/ del script; para identificar esta revisión usar el ID de ejecución anterior y windows/01-worktree.txt. No se ejecutó el experimento externo de cabezas ni se verificó PCDS desde Windows. El caso sintético sin eventos tiene evidencia Linux de Claude, no una nueva comprobación Windows de Codex.

Siguiente tarea: docs/tareas/claude/09-evaluacion-windows.md. Priorizar evaluación y pesos ajustados, conservar el error del modelo explícito y aplazar informes académicos. Sin commit ni push en esta revisión.

Gráfico: finalizó con exit 0, 45 estados, 32 transiciones de predicción y cero fallos. El script completo terminó y ejecutó su limpieza de procesos temporales. Integración de tarea 08 aceptada para la demo fija de 0–6 s; el fallo del detector sigue abierto.
