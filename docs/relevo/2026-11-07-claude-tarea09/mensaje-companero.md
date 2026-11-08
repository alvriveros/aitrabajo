# Mensaje para el compañero de visión

Listo para que Álvaro lo copie; no se envió automáticamente.

---

Hola. Integramos tu rama `vision` (`dd5a19a`) con la API y el panel en `integracion-video`, todavía local. Desde el panel se procesa el ensayo de oficina de 0–6 s y se ve el video anotado. Encontramos un problema y necesitamos estas cosas tuyas:

1. **Los pesos ajustados**, `runs/oficina-ajuste/oficina-ajustado.pt`. Tu relevo da 5.497.434 bytes y SHA-256 `783d16c0…2d93e1`. Si es otro archivo, pasá su tamaño y SHA-256. Además:
   - el commit de `vision` con el que entrenaste y el comando exacto de `vision.train`;
   - la configuración que recomendás (entendemos ByteTrack por defecto, sin `bytetrack-cenital.yaml`);
   - tus versiones de Python, ultralytics, torch, opencv-python y lap, y el sistema operativo y procesador.
2. **Una medición en tu Mac**, con el mismo clip (SHA-256 `02666c2e…15fc95`) y `yolo11n.pt`. Los comandos están en `docs/relevo/2026-11-07-claude-tarea08/pedido-vision.md`. Mandanos `runs/confianza-macos.json`, `runs/macos-00-06.json` y su `.config.json`.

**Por qué.** Con el modelo base y tu configuración calibrada, la bajada de ≈ 4 s del ensayo no se cuenta ni en Linux x86 ni en Windows (Ryzen 5 7535HS). En los dos queda solo la subida a 2,16 s, y tu `test_ensayo_de_oficina_…` falla. En el video completo, Linux da 7 de 10 subidas y 4 de 10 bajadas, contra tus 12 de 20 en macOS. Que la diferencia venga de la plataforma es una hipótesis: queremos medirlo con tu confianza cuadro a cuadro. El análisis está en `docs/casos-deteccion/oficina-bajada-omitida/`.

**Qué vamos a hacer con los pesos.** Comparar base y ajustado en Windows, de 0–6 s y en el video completo, con las configuraciones de `evaluation/comparar_oficina.py`, sin tocar umbrales y separando subidas y bajadas. Sabemos que en este video el ajustado no muestra generalización, porque se entrenó con la misma grabación.

**Lo que viene después**, si hay tiempo:
- **Grabación nueva independiente:** ficha en `docs/relevo/2026-11-07-claude-tarea09/ficha-grabacion-independiente.md`. Sería la única prueba real.
- **Revisión humana de `oficina-cruces.json`:** no está documentado cómo salieron los cruces de 2,16 y 4,68 s, porque no hay cajas antes de 6 s.
- **Detector de cabezas:** un experimento externo dio 19 de 20, pero sin licencia y en una sola grabación. Habría que reanotar cabezas, no reutilizar las cajas de persona.

PCDS quedó bloqueado: no pudimos descargarlo.

---
