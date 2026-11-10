# Informe IEEE

`informe.tex` usa la clase oficial IEEEtran V1.8b (conference, A4, dos columnas) y describe el **sistema final** del 9 nov. Las cifras salen de los registros fechados de `docs/relevo/`. La fuente de cada una está en [`../relevo/2026-11-08-claude-cierre-final/README.md`](../relevo/2026-11-08-claude-cierre-final/README.md).

## Antes de entregar

1. **Autores.** Completá `\autores` (nombres completos) y `\afiliacion` (universidad y facultad) al principio del archivo.
2. **Compilar.** Desde esta carpeta, con MiKTeX o TeX Live completo. Hacen falta `IEEEtran`, `babel-spanish`, `pgf` (TikZ) y `booktabs`.
   ```sh
   pdflatex informe.tex
   bibtex informe
   pdflatex informe.tex
   pdflatex informe.tex
   ```
3. **Comprobar:**
   - que sean **exactamente 3 páginas**;
   - que ninguna línea desborde (buscá `Overfull` en `informe.log`);
   - que las tablas no queden fuera de su página.

   Si sobra o falta espacio, ajustá la sección III, la más larga.
4. **Revisar visualmente** las tres páginas y guardar el PDF como `informe.pdf`.

**Estado vigente (9 nov., noche, cierre acotado):** `informe.pdf` se recompiló con TeX Live 2023 e IEEEtran V1.8b en Linux (Claude): 3 páginas A4, sin `Overfull`, resumen de 147 palabras y 16 referencias. Cambios: la prueba final del bus real se declara como influyente en la selección de YOLO11n; la evaluación ciega de `prueba-bus` se rotula como CPU (24 eventos) y se distingue de las ejecuciones en GPU (25 eventos); PAMELA B se presenta como la misma escena que PAMELA A; la cámara se declara emulada con un archivo; la ley se cita por su fuente primaria (Ley 7617/2026) y el Decreto 5969 por la prensa, porque no se encontró su texto oficial; y se agrega la Fig. 2.

**Fig. 2 (`fig-ocupacion.png`)** se genera, sin ejecutar el modelo, con `python -m evaluation.curva_ocupacion`, desde la referencia de Álvaro y las predicciones originales de la evaluación ciega en CPU (copia versionada en `docs/relevo/2026-11-08-claude-tarea13/primera-evaluacion/`). Los valores quedan en `ocupacion-prueba-bus.json`: cambio acumulado (la carga inicial real no se conoce), grilla de 0,1 s sobre 0–27,4 s, MAE 2,68 y RMSE 3,31 pasajeros. Son métricas de ese clip, no de generalización. La prueba `tests/test_curva_ocupacion.py` verifica el cálculo con un caso de resultado conocido.

**Pendiente del equipo:** recompilar con MiKTeX y confirmar que sigan siendo 3 páginas (otra distribución puede mover una línea) y revisar visualmente.

**Estado anterior (9 nov., 01:22, commit `8ffa96c`, histórico):** `informe.pdf` es el PDF final, con las correcciones del cierre documental. Lo compiló Álvaro con MiKTeX: 3 páginas A4, sin desbordes ni errores, 16 referencias y resumen de 150 palabras. Claude revisó las tres páginas. `informe-borrador.pdf` es el borrador anterior y se conserva como histórico.
