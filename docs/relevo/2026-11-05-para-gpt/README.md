# Cambios en aitrabajo · 5 de noviembre de 2026

## Comprobación posterior de GPT

Se ejecutó `docker compose up --build -d` en Windows y arrancaron ambos servicios con la API saludable. Chromium abrió el panel en 8502 y verificó 4 pasajeros y 20 %. La captura [panel-windows.png](panel-windows.png) confirma tema claro y rótulos legibles. Quedan resueltos los pendientes 1 y 2 de este relevo.

Los dos videos adicionales aportados por Álvaro quedaron documentados en [videos-candidatos.md](../../tareas/vision/videos-candidatos.md). Su inspección visual está pendiente por un fallo de acceso web y del navegador integrado. Esta comprobación revisó el panel y leyó el relevo; la revisión independiente del PDF sigue pendiente. Todos los cambios permanecen sin commit.

Repo: alvriveros/aitrabajo, rama main, último commit 3d92072.
Todos los cambios están en la copia local de Álvaro y SIN COMMIT.
Proyecto: conteo de pasajeros y ocupación por parada, con FastAPI, Streamlit y Docker.
La parte de visión la hace el compañero en la rama vision. Todavía no está integrada.

## Paso 1. Gráfico del panel (tarea 03)

- Archivo: ui/app.py.
- Agregué la función graficar(filas) con Altair y la usé en el panel.
- Muestra barras de ocupación (%) con los mismos resultados de POST /ocupacion que la tabla.
- Las paradas van numeradas y en orden, para distinguir nombres repetidos.
- La última parada visible se marca como parcial, por ejemplo "2 (parcial) · Parada 2".
- Hay una línea roja rotulada "Capacidad 100 %".
- La escala admite valores negativos y superiores a 100 %.
- Debajo del gráfico hay una nota con la parada parcial y el instante elegido.
- No cambié api/ ni tests/. El cálculo y la validación siguen en la API.

## Paso 2. Docker (tarea 03)

- Dockerfile: Python 3.12, instala requirements.txt y copia api/, ui/ y docs/demo/.
- docker-compose.yml: servicios api y panel con la misma imagen.
- Puertos: API en 127.0.0.1:8001 y panel en 127.0.0.1:8502.
- El panel usa API_URL=http://api:8000 y espera a que la API esté saludable.
- Healthcheck de la API con Python contra /openapi.json.
- .dockerignore: excluye .venv, .git, cachés, archivos de entorno, videos, pesos, datos crudos y capturas. De docs/ solo entran los JSON de docs/demo/.
- README.md: agregué el arranque, las URLs, los registros y el cierre con Docker.

## Paso 3. Verificación de la tarea 03

- Pasan las 7 pruebas de la API en Linux y Windows.
- 11 registros del panel coinciden campo por campo entre Linux y Windows.
- Docker Desktop construyó y arrancó con la imagen oficial python:3.12-slim.
- El panel volvió a consultar la API después de detener y arrancar los servicios.
- En Linux, Docker Hub estaba bloqueado, así que se usó una base local sustituta.
- Evidencias: docs/relevo/2026-11-05-claude-tarea03/.

## Paso 4. Informe IEEE (tarea 04)

- Carpeta nueva: docs/informe/.
- Archivos: informe.tex, referencias.bib, README.md, informe-borrador.pdf y grafico-demo.png.
- Clase IEEEtran, conference, A4 y dos columnas, marcado como borrador.
- Resultado: 3 páginas y resumen de 138 palabras.
- Documenta lo implementado y las pruebas funcionales. Aclara que verifican el software de ocupación, no la visión.
- Las métricas de visión figuran como "pendiente", sin cifras inventadas.
- docs/informe/README.md lista cada dato pendiente, su responsable y la sección a actualizar.

## Paso 5. Guion de la demo (tarea 04)

- Archivo nuevo: docs/demo/guion.md.
- Incluye preparación previa, cuatro bloques en 10 minutos, responsables, material del compañero y seis preguntas probables.

## Paso 6. Ensayo del bloque de Álvaro (tarea 04)

- Se ensayó contra el panel Docker en Windows.
- Demo: 3 → 5 → 4 pasajeros (15, 25 y 20 %).
- Capacidad 40: 4 pasajeros, 10 %.
- Oficina, referencia manual: 0 → 1 → 0 (0, 5 y 0 %).
- Fue automático y sin voz. Duración estimada del bloque: unos 160 s de 180.
- Falta cronometrar a Álvaro y hacer el ensayo completo con el compañero.

## Paso 7. Corrección del rótulo y tema claro

- Problema: en tema oscuro, el valor sobre las barras casi no se leía.
- ui/app.py: el rótulo usa color #7a7a7a en negrita.
- .streamlit/config.toml, archivo nuevo: base = "light".
- Dockerfile: copia .streamlit/config.toml a la imagen.
- .dockerignore: ya no excluye .streamlit completo; excluye .streamlit/secrets.toml.
- Actualicé el gráfico del informe. Sigue en 3 páginas.
- Comprobado en Linux en ambos temas: los 11 registros no cambiaron y pasan las 7 pruebas.

## Paso 8. Documentación

- resumen.md: quedó actualizado con el estado de las tareas 03 y 04, y corregí notas viejas.
- Evidencias de la tarea 04: docs/relevo/2026-11-05-claude-tarea04/.

## Pendientes

1. Ejecutar docker compose up --build -d en Windows. El panel en 8502 todavía usa la imagen anterior a la corrección del rótulo.
2. Comprobar en 8502 el tema claro, 4 pasajeros, 20 % y los rótulos legibles.
3. Recibir de visión las métricas, el caso de oclusión, los eventos reales y el JSON de predicciones.
4. Completar en el informe los nombres de los autores y la universidad.
5. Completar el autor y la fecha del video de oficina.
6. Volver a comprobar las 3 páginas al incorporar las métricas.
7. Revisar los cambios y hacer el commit. Nada está publicado.
8. La tarea 02 sigue esperando los eventos de visión.
