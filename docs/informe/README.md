# Informe IEEE · Borrador de trabajo

`informe.tex` usa la clase oficial IEEEtran (V1.8b) en formato conference, A4 y dos columnas. `informe-borrador.pdf` es el resultado compilado. El encabezado de cada página lo marca como borrador: quitá la línea `\AddToHook{shipout/foreground}` para la entrega.

## Compilar

Desde esta carpeta, con TeX Live o MiKTeX:

```sh
pdflatex informe.tex
bibtex informe
pdflatex informe.tex
pdflatex informe.tex
```

Después copiá `informe.pdf` a `informe-borrador.pdf`. Necesita los paquetes `IEEEtran`, `babel-spanish`, `pgf` (TikZ) y `booktabs`.

## Mediciones pendientes de visión

| Dato requerido | Responsable | Sección a actualizar |
|---|---|---|
| Aciertos, omisiones y falsos positivos por sentido, base y ajustado | Compañero | III-B, Tabla III |
| F1 de subidas y bajadas, base y ajustado | Compañero | III-B, Tabla III; resumen |
| Error absoluto medio del conteo por clip | Compañero | III-B, Tabla III; resumen |
| Cuadros por segundo en la máquina de defensa, hardware, resolución y FPS del video | Compañero | III-B, Tabla III |
| Caso de oclusión o pérdida de ID, con instante y efecto en el conteo | Compañero | III-B, Fig. 3 |
| Detector, pesos, parámetros y ajuste usados | Compañero | II-E |
| Dataset: origen, condiciones de uso, real o simulado, duración y particiones | Compañero | II-B |
| Comparación de `oficina-00-06-prediccion.json` con la referencia manual | Compañero y Álvaro | III-B, III-C |
| Referencias verificadas del detector, el rastreador y los datos | Compañero | Referencias |

## Otros datos pendientes

| Dato requerido | Responsable | Sección a actualizar |
|---|---|---|
| Apellido de Álvaro, nombre del compañero y universidad | Álvaro | Autores |
| Autor y fecha del video de oficina (YouTube no pudo abrirse para verificarlos) | Álvaro o compañero | Referencia [5] |
| Cifra local de demanda u ocupación, solo si se obtiene de la fuente primaria | Álvaro | I |

## Antes de la entrega final

1. Reescribí el resumen con los hallazgos reales, en 150 palabras o menos.
2. Reemplazá las secciones II-E y III-B: dejan de ser "prevista" y "pendiente". Actualizá las conclusiones, las limitaciones y el trabajo futuro.
3. Completá o eliminá la Tabla III y la Fig. 3. Ninguna celda debe decir "pendiente".
4. Actualizá la Tabla I si cambian las pruebas o el código.
5. Quitá la marca de borrador y traducí, si la cátedra lo pide, "[Online]. Available:" en las referencias.
6. **Compilá y comprobá de nuevo que sean exactamente 3 páginas.** La tercera tiene espacio libre, pensado para este contenido.

La versión actual: 3 páginas, resumen de 138 palabras y sin desbordes de línea.
