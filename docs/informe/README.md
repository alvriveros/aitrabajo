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

**Resumen:** 147 palabras, contadas en la fuente.

**Estado de la compilación (9 nov.):** no se pudo compilar en el entorno de Claude. A ese TeX Live le faltan `IEEEtran` y `babel-spanish`, y la red no permite instalarlos. El texto tiene unas 2000 palabras, tres tablas y una figura TikZ. El borrador anterior tenía unas 1750 palabras, tres tablas y dos figuras, y ocupaba 3 páginas con casi una columna libre, así que la extensión debería cerrar en 3 páginas. **Igual hay que verificarlo compilando.** `informe-borrador.pdf` es el PDF del borrador anterior y no corresponde a este texto.
