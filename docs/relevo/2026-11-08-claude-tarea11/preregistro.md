# Tarea 11 · Detectores más grandes sin entrenar · prerregistro

Registrado el 8 nov. 2026 a la 01:10 (Paraguay), **antes de ejecutar ningún detector grande**. Álvaro lo autorizó («Haz la prueba») tras ver que anotar cajas para entrenar no era confiable (ver más abajo).

## Pregunta

¿Un detector más grande de la misma familia, sin entrenar, cuenta mejor que `yolo11n` con el mismo pipeline y la misma regla de conteo?

## Modelos

Pesos oficiales de Ultralytics, release v8.4.0, sin ajustar. Están fuera de Git y se verifica su SHA-256 antes de usarlos.

| Modelo | SHA-256 |
|---|---|
| `yolo11n.pt` (el actual) | `0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1` |
| `yolo11l.pt` | `9ebd0e09d59811db4b1d61e2bc6730649608b1ac47f8dd01e2da6bca7c20023f` |
| `yolo11x.pt` | `7bc158aa95c0ebfdd87f70f01653c1131b93e92522dbe15c228bcd742e773a24` |

## Configuraciones

Cada modelo se ejecuta con los dos rastreadores de `evaluation/comparar_oficina.py`: por defecto, y calibrado (`bytetrack-cenital.yaml`, `conf 0.05`, `confirmacion 2`). Son 6 configuraciones. Todo lo demás queda igual al pipeline actual: punto en el centro de la caja, margen de 5 px, y las geometrías y referencias de las tareas 09 y 10.

## Escenas y papel de cada una

- **Kaggle y PAMELA A: selección.** El detector y el rastreador se eligen con estas dos escenas. Sus referencias son de Claude y **siguen pendientes de revisión humana**. Ya se usaron para medir `yolo11n`, así que sirven para comparar, pero **no son una prueba final**.
- **Oficina: diagnóstico.** Se usó para calibrar el rastreador; se informa aparte.
- **Prueba final, reservada:** `youtube-bus-real-0y08Jtqtkys.mp4`, de 9 min. No se ejecuta en esta tarea. Se anotará antes de usarla, solo con la configuración elegida.
- **Fuera de esta tarea:** `youtube-bus-demo-UYKQ1sQOIwo.mp4`, de 32 s. Se descartó como validación porque sus cruces, un grupo amontonado entre 14 y 27 s con cambios de exposición, no se pueden anotar con confianza a ojo. Queda como ejemplo cualitativo y no se ejecuta.

## Criterio de elección, fijado ahora

1. **Primero:** el menor número total de errores, sumando omisiones y eventos extra en Kaggle y PAMELA A, en los dos sentidos.
2. **Desempate:** el menor error de conteo absoluto, sumado por sentido.
3. **Segundo desempate:** el mayor FPS.

La elección se informa como candidata. **No se cambia la configuración de la API** sin revisión, y la prueba final decide si se propone.

## Entorno

Contenedor Linux de Claude, en CPU: Álvaro no estaba disponible para correrlo en su GPU. Los FPS de CPU no representan los de la RTX 2050. En Kaggle, Linux y Windows ya dieron eventos algo distintos con `yolo11n`; por eso los tres modelos se ejecutan en el mismo entorno.

## Por qué no se entrenó con más videos

Con `yolo11n`, y también con `yolo11x`, las propuestas de cajas no detectaban a buena parte de las personas en PAMELA, más o menos 6 de cada 10 a 352×288. En Kaggle, varias personas tampoco tenían caja. Dibujar a ojo unas 450 cajas habría dado etiquetas imprecisas, y entrenar con personas sin caja enseña al modelo a no detectarlas. Se descartó hasta tener mejores etiquetas: las oficiales de PAMELA o anotaciones hechas por una persona.
