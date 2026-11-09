# Revisión humana de las referencias de Kaggle y PAMELA A (8 nov., 18:46, Álvaro)

Álvaro revisó las dos referencias de Claude **sin cambios**. Los archivos originales no se modificaron:

```
6ebd660e0ce0831f9d4e718e1a534f2ccd7cf7e1f10973c2f8eeafbc406aaf8e  data/annotations/kaggle-people-boarding-bus-cruces.json
def143dcf329e496fb21bea2a939912e72b29d9664d6e11ecacffb524fe92244  data/annotations/pamela-A-cruces.json
```

- **Kaggle:** «se suben exactamente 6 personas, tus tiempos están bien».
- **PAMELA-UANDES `A_d800mm_sample`, 0–30 s:** «está correcto las 28 bajadas y los tiempos».

## Consecuencias

- **Las referencias pasan a estar revisadas por una persona.** Como no cambiaron, sus hashes son los mismos que registran `tarea11/linux/resumen-*.json` y `resultados-exploratorios/resultados.json`.
- **Tarea 12:** el prerregistro preveía recalcular con las referencias revisadas. Con los mismos insumos el cálculo da lo mismo, así que **su conclusión deja de ser exploratoria**: la supresión temporal global no se justifica. La carpeta conserva su nombre original.
- **Tarea 11:** la selección de `yolo11l` calibrado (21 contra 28 errores) queda con referencias revisadas. La prueba final ya la descartó (18 contra 13).
- **Alcance:** la revisión confirma conteos y tiempos a la escala de la tolerancia (±1 s). No es una anotación independiente cuadro a cuadro.
