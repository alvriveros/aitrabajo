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

**Estado (9 nov., 01:22, commit `8ffa96c`):** `informe.pdf` es el PDF final, con las correcciones del cierre documental. Lo compiló Álvaro con MiKTeX: 3 páginas A4, sin desbordes ni errores, 16 referencias y resumen de 150 palabras. Claude revisó las tres páginas. `informe-borrador.pdf` es el borrador anterior y se conserva como histórico.
