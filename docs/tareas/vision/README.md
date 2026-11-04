# Relevo para la IA del compañero · rama `vision`

Tu responsabilidad es convertir un video de una puerta en una secuencia de subidas y bajadas, medir qué tan bien funciona y entregar el resultado a Álvaro. Álvaro mantiene la API y el panel en `main`. **Primer hito: entregar un JSON generado desde el video y su video anotado para la integración del jueves 5 de noviembre.** El cierre interno del TP es el domingo 8 a las 18:00 de Paraguay.

Trabajá en una copia del repositorio privado `alvriveros/aitrabajo` con la cuenta del compañero. Para una copia nueva:

```sh
git clone --branch vision https://github.com/alvriveros/aitrabajo.git
cd aitrabajo
git status -sb
```

Si ya hay una copia, revisá los cambios locales antes de cambiar de rama. Confirmá que estás en `vision`. Leé la [consigna](../../../contexto.md), el [plan de ambos](../../PLAN.md), el [contrato de la API](../../../api/main.py) y las [instrucciones de arranque](../../../README.md).

## 1. Preparar el primer clip

- Fuente: [Fast Run Test in Office – Automatic Passenger Counter System](https://www.youtube.com/watch?v=L1fkyVQbHOg). Usá los primeros 6 segundos como ensayo de una puerta de bus. Es una oficina. El repositorio contiene la referencia manual; el archivo de video se obtiene aparte.
- Buscá la copia local en `data/raw/`. Si falta, pedile al compañero una copia que pueda usar o su ruta local. Mientras llega, prepará la interfaz del módulo, la lógica de cruce y su comprobación con trayectorias de ejemplo. Para afirmar que procesaste el clip necesitás ejecutarlo sobre sus imágenes.
- Las dos vistas superiores muestran a la misma persona. **Procesá solamente el cuadrante superior derecho** y excluí el tablero de contadores. Trazá la línea de lado a lado sobre el umbral visible. En ese recorte, abajo → arriba es `subida`; arriba → abajo es `bajada`. Guardá extremos de la línea, coordenadas del recorte y sistema de coordenadas para repetir la ejecución.
- [Referencia manual del ensayo](../../demo/oficina-00-06-manual.json): una subida cerca de 2 s y una bajada cerca de 4 s. Con capacidad 20, carga inicial 0 y una sola parada, el panel debe pasar de 0 a 1 pasajero (5 %) y volver a 0. **Estos tiempos son aproximados y sirven para comparar después de la inferencia.** Los IDs del rastreador pueden diferir de los manuales.

## 2. Implementar y ejecutar el conteo

1. Creá el punto de entrada en `vision/pipeline.py`. Debe aceptar video local, tramo, recorte, línea, orientación y destino de los resultados. Documentá en `vision/README.md` el comando exacto que ejecutaste desde la raíz, versión de Python, dependencias de visión y cómo obtener los pesos utilizados.
2. Empezá con un detector de personas preentrenado y ByteTrack. Conservá el ID entre cuadros. Usá un punto consistente del cuerpo para decidir de qué lado está. Emití un evento al pasar de un lado confirmado al otro. Permanecer o temblar sobre la línea conserva el estado; un regreso confirmado genera un nuevo evento. Una aparición junto a la línea por sí sola no alcanza para contar.
3. Guardá tiempos en segundos desde el inicio del tramo, derivados de los fotogramas o marcas temporales del video. Exportá **las predicciones observadas**, incluso si faltan cruces. Anotá el video con línea, ID y sentido para poder revisar discrepancias.
4. Entregá `evaluation/results/oficina-00-06-prediccion.json` con el mismo esquema del JSON manual: `capacidad`, `carga_inicial`, `paradas` y `eventos`. Cada evento lleva `tiempo_s` numérico, `track_id` entero y `sentido` igual a `subida` o `bajada`. Ordená por tiempo. Conservá por separado las predicciones y la referencia. Guardá el video anotado localmente e indicá cómo Álvaro puede acceder a él o regenerarlo.

## 3. Comprobar la integración con Álvaro

Arrancá la API según el README. Desde PowerShell, en la raíz:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/ocupacion -ContentType 'application/json' -InFile evaluation/results/oficina-00-06-prediccion.json | ConvertTo-Json -Depth 6
```

Cargá **ese mismo archivo de predicciones** en el panel. Registrá tiempos, sentido y carga tras cada cruce junto al valor manual. Dos eventos omitidos pueden dar el mismo total final de cero. Revisá el fotograma de cada discrepancia. Ejecutá también `python -m pytest tests -v` para confirmar que la integración conserva el contrato de la API.

**Primer PR a `main`:** código ejecutable, configuración de la escena, JSON predicho, acceso al video anotado y comparación real con las dos anotaciones. Incluí comandos y resultados en `docs/relevo/vision-primer-clip/README.md`. Si falta un insumo, identificá cuál y qué sí llegaste a verificar. Álvaro revisa e integra el PR.

## 4. Completar la parte de visión del TP

- **Datos y entrenamiento (jueves 5).** En `data/README.md` documentá origen, condiciones de uso, contexto real o simulado, duración y partición de cada grabación. Anotá cajas de personas para ajustar el detector y cruces manuales para evaluar el sistema. Mantené todos los fragmentos de una grabación en la misma partición. El clip de oficina usado para calibrar es un ensayo de integración. Reservá grabaciones independientes para prueba, idealmente con escenas locales y cruces simultáneos. Implementá el ajuste reproducible en `vision/train.py`; guardá parámetros, versiones y acceso a pesos.
- **Evaluación (viernes 6).** Elegí la configuración usando validación. Compará detector base y ajustado en clips reservados con el mismo evaluador en `evaluation/evaluate.py`. Emparejá cada cruce manual con una única predicción de igual sentido dentro de ±1 s. Reportá aciertos, omisiones, falsos positivos y F1 por sentido, error absoluto medio del conteo por clip y FPS medidos. Registrá hardware, resolución y FPS del video. Documentá al menos un caso de oclusión o pérdida de ID con el instante y su efecto en el conteo. Si faltan datos para una medición, dejala pendiente.
- **Informe y defensa (sábado 7 y domingo 8).** Entregá a Álvaro la metodología, una tabla o figura obtenida de los resultados, las limitaciones y las referencias del detector, rastreador y datos. Prepará tu explicación del seguimiento y un error observado. Antes del cierre, repetí la ejecución desde una copia limpia y verificá que los pesos, los clips y la demo estén disponibles en la máquina de defensa.

Usá commits descriptivos en `vision` y PR pequeños hacia `main`. Al cerrar cada entrega, dejá en el relevo el commit, comando de reproducción, resultados, ubicación de los archivos y próximo pendiente. El historial de pruebas del panel y los datos sintéticos ya están en `main`; la evidencia que falta producir es la de visión.
