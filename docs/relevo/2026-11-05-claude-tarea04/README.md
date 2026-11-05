# Devolución · Tarea 04 · Informe IEEE y guion de la demo

5 de noviembre de 2026. [Ficha de la tarea](../../tareas/claude/04-informe-demo.md). Los cambios quedan sin commit para la revisión de Álvaro.

**Resultado:** el borrador del informe compila en exactamente 3 páginas y el guion está listo. El bloque de Álvaro se ensayó contra Docker en Windows con los valores esperados. Las métricas de visión siguen pendientes, y el problema de legibilidad que encontró el ensayo ya está corregido.

## Corrección de legibilidad

El ensayo mostró que, en tema oscuro, el rótulo de valor de las barras casi no se leía ([antes](ensayo/ensayo-tema-oscuro.jpg)). Álvaro pidió corregirlo y dejar el tema claro.

- `ui/app.py`: el rótulo usa color `#7a7a7a` en negrita, legible en ambos temas.
- `.streamlit/config.toml`: tema claro predeterminado, en ejecución manual y en Docker.
- `Dockerfile` y `.dockerignore`: copian esa configuración a la imagen y siguen excluyendo `.streamlit/secrets.toml`.

Comprobación en Linux sobre la base local sustituta: los 11 registros dan valores idénticos a los anteriores en tema claro (Docker, 8502) y oscuro (panel local con `--theme.base dark`), pasan las 7 pruebas y la imagen contiene la configuración. Capturas y valores en [tema/](tema/).

**Pendiente en Windows:** el panel activo en 8502 sigue con la imagen anterior. Hay que ejecutar `docker compose up --build -d` y comprobar el rótulo y el tema claro con la imagen oficial.

## Archivos

Nuevos:

- `docs/informe/`: `informe.tex`, `referencias.bib`, `README.md`, `informe-borrador.pdf` y `grafico-demo.png`.
- `docs/demo/guion.md`.
- `docs/relevo/2026-11-05-claude-tarea04/`: esta carpeta.

Modificados: `resumen.md`, `ui/app.py`, `Dockerfile` y `.dockerignore`. Nuevo: `.streamlit/config.toml`. Los cambios sin commit de la tarea 03 se conservan.

## Entorno

| Elemento | Valor |
|---|---|
| Compilación | Ubuntu 24.04, TeX Live 2023 (pdfTeX), IEEEtran V1.8b, en el espacio de trabajo en la nube. **No se compiló en Windows.** |
| Ensayo | Panel Docker activo en Windows, `127.0.0.1:8502`, abierto desde el navegador integrado de la app de Claude |
| Fuentes | Consultadas por web el 5 de noviembre de 2026 |

## Comandos

```sh
pdflatex informe.tex && bibtex informe && pdflatex informe.tex && pdflatex informe.tex
pdfinfo informe.pdf
pdffonts informe.pdf
pdftoppm -r 110 -png informe.pdf pagina
```

## Comprobación del PDF

| Criterio | Observado |
|---|---|
| Páginas | 3, A4 |
| Resumen | 138 palabras en el PDF, 139 en la fuente; límite 150 |
| Secciones | Resumen, I a IV y Referencias, según la consigna |
| Registro de compilación | Sin desbordes ni referencias sin resolver |
| Fuentes | Todas incrustadas |
| Revisión visual | Páginas en `revision-pdf/`: diagrama, 3 tablas, 2 figuras, referencias y cortes de columna correctos |

La primera compilación mostró la tercera página casi vacía, una fila de tabla mal justificada, "Index Terms" en inglés y "p. Art. no." en las referencias. Se corrigieron. La tercera página conserva espacio libre a propósito para las métricas reales, por lo que hay que volver a comprobar las 3 páginas al incorporarlas.

## Ensayo del bloque de Álvaro

Estos tiempos **no son un ensayo completo**: lo hizo Claude, sin voz y sin el compañero. Falta cronometrar a Álvaro y el ensayo de 10 minutos con ambos.

- **Operación del panel:** 56 s del primer registro al último ([valores](ensayo/valores-ensayo.json)), con la latencia de las herramientas y esperas de 1,8 s por paso. No representa el ritmo de una persona.
- **Texto hablado:** bloque 5–8, 223 palabras, unos 103 s estimados a 130 palabras por minuto. Bloque 0–2, 175 palabras, unos 81 s.
- **Estimación del bloque 5–8:** unos 160 s de 180 disponibles.

| Paso | Instante | Pasajeros | Ocupación | Tabla |
|---|---|---|---|---|
| Abrir el panel, demo | 10 s | 4 | 20 % | Sin leer: la tabla no estaba cargada en la página |
| Selector | 0 s | 3 | 15 % | 3 y 15 |
| Selector | 5 s | 5 | 25 % | 5 y 25 |
| Selector | 10 s | 4 | 20 % | 5 y 25; 4 y 20 |
| Capacidad 40 | 10 s | 4 | 10 % | 5 y 12,5; 4 y 10 |
| Cargar oficina | 4 s | 0 | 0 % | 1 subida, 1 bajada, 0 y 0 |
| Selector | 0 s | 0 | 0 % | 0 y 0 |
| Selector | 2 s | 1 | 5 % | 1 y 5 |
| Selector | 4 s | 0 | 0 % | 0 y 0 |

No hubo errores ni avisos. El archivo de oficina se cargó por script en el selector de archivos, con el mismo contenido que el del repo, porque el navegador integrado no puede usar el diálogo de archivos. Falta probar esa acción a mano. Los servicios se usaron tal como estaban activos y no se detuvieron. El ensayo fue anterior a la corrección de legibilidad.

## Verificación de afirmaciones

Cada afirmación del borrador se contrastó con su fuente.

| Afirmación | Fuente |
|---|---|
| Contrato, intervalos, 422, fórmula y aviso negativo | `api/main.py` |
| 7 pruebas y sus entornos | `tests/test_ocupacion.py`, relevos del 4 de noviembre y tarea 03 |
| 14 registros en Linux y Windows | Relevo de la tarea 01 |
| 11 registros en Linux y Windows | Tarea 03, `revision-windows/valores.json` |
| Panel, gráfico y parcial | `ui/app.py` |
| Docker, imagen oficial y `service_healthy` | `Dockerfile`, `docker-compose.yml`, tarea 03 |
| Casos de la Tabla II | Tarea 03 y este ensayo |
| Visión como "prevista" | `docs/PLAN.md`, `docs/tareas/vision/README.md`; no hay módulo `vision/` en `main` |

Notas históricas reconciliadas en `resumen.md`: la frase que limitaba los valores a Linux ahora refleja la comparación de 11 registros en Windows, y la lista de faltantes ya no incluye Docker.

## Referencias

| Ref. | Verificación |
|---|---|
| [1] Hsu, Optik | Portal académico NYCU |
| [2] Seidel, NAPC | TU Berlin y DOAJ |
| [3] ByteTrack | arXiv y ECVA; DOI según ECVA |
| [4] DeepSORT | arXiv; datos de ICIP por catálogo bibliográfico, no por IEEE Xplore |
| [5] Video de oficina | **Parcial:** título y enlace del repo; YouTube no abrió, faltan autor y fecha |
| [6], [7], [9], [10] Documentación | Páginas oficiales, consultadas el 5 de noviembre de 2026 |
| [8] Altair | JOSS |

## Pendientes

1. Métricas y material de visión: lista completa en [docs/informe/README.md](../../informe/README.md).
2. Nombres de autores y universidad.
3. Autor y fecha del video de oficina.
4. Reconstruir la imagen en Windows y comprobar el rótulo y el tema claro.
5. Compilar en Windows si Álvaro lo necesita y volver a comprobar las 3 páginas tras incorporar métricas.
6. Ensayo cronometrado de Álvaro y ensayo completo de 10 minutos con el compañero, en la máquina de defensa.
7. La tarea 02 continúa pendiente de los eventos de visión.
