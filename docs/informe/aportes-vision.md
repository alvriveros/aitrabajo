# Aportes de visión para el informe

Fragmentos para pegar en `informe.tex`, de la rama `tareas-03-04-panel-informe`, con los datos reales de visión.

**Antes de usarlos:**

- **Estos números no son métricas en clips reservados.** Todo sale de una sola grabación, con una sola persona. El texto lo dice de forma explícita y conviene conservarlo. Si llegan clips independientes, hay que reemplazar la Tabla III y actualizar el resumen, III-B, III-C y las conclusiones.
- **El LaTeX no se compiló**, porque en la máquina donde se redactó no hay compilador. Se comprobó la estructura, pero hay que compilar y verificar que sigan siendo exactamente 3 páginas. El borrador tiene libre el equivalente a una columna, y estos fragmentos agregan unas 380 palabras, una figura de tamaño parecido al recuadro actual y dos referencias.
- **Las cajas y los cruces de referencia aún no los revisó una persona.** Si cambian, hay que repetir el entrenamiento y la comparación.

## Qué cubre de la lista de pendientes

| Dato de `docs/informe/README.md` | Estado |
|---|---|
| Aciertos, omisiones y falsos positivos por sentido | Listo para el video de oficina. **En clips reservados, pendiente** |
| F1 por sentido | Listo para el video de oficina. **En clips reservados, pendiente** |
| Error absoluto medio del conteo por clip | Con un solo clip, se reporta el error absoluto. **La media por clip sigue pendiente** |
| FPS en la máquina de defensa, hardware, resolución y FPS del video | Resolución y FPS del video, listos. FPS medidos en un Apple M4. **Máquina de defensa, pendiente** |
| Caso de oclusión o pérdida de ID | Pérdida de ID, lista (Fig. 3). **Oclusión entre personas, pendiente** |
| Detector, pesos, parámetros y ajuste | Listo (II-E) |
| Dataset: origen, condiciones, real o simulado, duración y particiones | Listo para el video de oficina (II-B) |
| Comparación de `oficina-00-06-prediccion.json` con la referencia manual | Lista (III-B) |
| Referencias del detector, el rastreador y los datos | Verificadas, ver abajo |
| Autor y fecha del video | Mike Niel, 23 de febrero de 2017 |

## Resumen

Reemplaza el contenido de `abstract`. Tiene menos de 150 palabras.

```latex
La auditoría de la ocupación del transporte público del Gran Asunción requiere datos de carga por parada. Este trabajo presenta un sistema que cuenta subidas y bajadas en una puerta y calcula la ocupación a lo largo de un recorrido simulado. YOLO11n y ByteTrack generan eventos al cruzar una línea virtual; una API REST los asigna a paradas y un panel web muestra el resultado, con arranque reproducible en Docker. En un video de oficina con 20 cruces de una sola persona, el detector preentrenado no contó ninguno con su configuración por defecto, mientras que el ajustado con cajas anotadas contó los 20 sin falsos positivos. Todo proviene de una sola grabación, por lo que esa cifra no mide generalización, y el ajuste empeoró la detección de personas de frente. Falta evaluar clips independientes y cruces simultáneos.
```

## II-B · Contrato de eventos y datos

Reemplaza el segundo párrafo, el que empieza con "Los datos disponibles".

```latex
Los datos disponibles son un recorrido sintético y un video público de 52,64~s (450$\times$360 píxeles, 25~FPS), con cámara cenital en una oficina~\cite{video}. No muestra un bus: simula la puerta, con una sola persona que cruza 20 veces. Sin licencia abierta declarada, no se versiona ni se redistribuye. El tramo de 6 a 43~s se usó para entrenar, desde los 43~s como reserva y los primeros 6~s como ensayo, con una referencia manual aproximada: subida cerca de 2~s y bajada cerca de 4~s. Todos pertenecen a la misma grabación, así que no son una evaluación independiente.
```

## II-E · Módulo de visión

Reemplaza toda la subsección "Integración prevista de visión".

```latex
\subsection{Módulo de visión}
El módulo procesa solo el cuadrante superior derecho del cuadro (222$\times$176 píxeles), con una línea virtual horizontal sobre el umbral. Usa Ultralytics~8.4.203~\cite{ultralytics} con YOLO11n~\cite{yolo11}, preentrenado con COCO~\cite{coco}, y ByteTrack~\cite{zhang2022} para conservar la identidad entre cuadros. El centro de cada caja indica de qué lado está la persona. Un lado se confirma con tres cuadros seguidos a más de 5~píxeles de la línea, y cada paso de un lado confirmado al otro emite un evento.

Se anotaron 165 cuadros de la misma escena: 131 para entrenar (113 con persona y 18 sin persona, incluidas sombras) y 34 de reserva. Las cajas se propusieron por resta de fondo y se revisaron cuadro por cuadro. El ajuste partió de los pesos preentrenados, con 40 épocas, entrada de 640~píxeles y semilla fija, y agregó volteos verticales y rotaciones. Se conservó la última época para que la reserva no eligiera el modelo.

El evaluador empareja cada cruce de referencia con una única predicción de igual sentido dentro de $\pm 1$~s.
```

## III-B · Mediciones de visión

Reemplaza toda la subsección, incluidas la Tabla III y la Fig. 3. Copiá también [`fig-perdida-id.png`](fig-perdida-id.png), que debe quedar junto a `informe.tex`.

```latex
\subsection{Mediciones de visión}
La Tabla~\ref{tab:vis} compara tres configuraciones en el video completo, con 10 subidas y 10 bajadas de referencia, obtenidas del centro de las cajas revisadas; sus totales coinciden con el contador comercial del video. El detector preentrenado con ByteTrack por defecto no cuenta ningún cruce. Con umbrales de seguimiento más bajos y dos cuadros de confirmación, calibrados sobre los primeros 6~s, llega a 12 de 20. El ajustado, con ByteTrack por defecto, cuenta los 20 sin falsos positivos.

\begin{table}[!t]
\caption{Conteo en el video de oficina: una sola grabación, sin evaluación independiente}
\label{tab:vis}
\centering\scriptsize
\begin{tabular}{@{}>{\raggedright\arraybackslash}p{0.49\columnwidth}ccc@{}}
\toprule
Métrica & Base & Calibrado & Ajustado\\
\midrule
Aciertos (de 20) & 0 & 12 & 20\\
Omisiones & 20 & 8 & 0\\
Falsos positivos & 0 & 0 & 0\\
F1 de subidas & 0,00 & 0,82 & 1,00\\
F1 de bajadas & 0,00 & 0,67 & 1,00\\
Error absoluto de subidas y bajadas & 10 y 10 & 3 y 5 & 0 y 0\\
Aciertos en la reserva (de 4) & 0 & 1 & 4\\
Carga final (referencia: 0) & 0 & 2 & 0\\
Cuadros por segundo, CPU Apple M4 & 41 & 41 & 41\\
\bottomrule
\end{tabular}
\end{table}

En el ensayo de 0 a 6~s, la configuración calibrada ubica la subida a los 2,16~s y la bajada a los 4,60~s, frente a cerca de 2 y 4~s de la referencia manual, y el panel muestra en ambos casos 0, 1 (5~\%) y 0 pasajeros. La diferencia de 0,6~s entra en la tolerancia: a los 4~s solo se ve un pie. Los 41~FPS con CPU en un Apple M4 superan los 25~FPS del video, pero falta medirlos en la máquina de defensa.

\begin{figure}[!t]
\centering
\includegraphics[width=\columnwidth]{fig-perdida-id.png}
\caption{Pérdida de identidad en la subida de los 43,8~s del video~\cite{video}: configuración calibrada a los 43,80~s (a) y 43,92~s (b); detector ajustado a los 43,92~s (c).}
\label{fig:oclusion}
\end{figure}

En la Fig.~\ref{fig:oclusion}, la configuración calibrada sigue a la persona como ID~59 debajo de la línea y continúa como ID~62 al pasar el umbral. Ningún ID confirma los dos lados y la subida se omite. De las 8 omisiones, 2 son cambios de ID como este, 4 son huecos de detección al cruzar y en 2 la persona se detecta de un solo lado. La carga final queda en 2 pasajeros en lugar de 0. El detector ajustado conserva el ID en los 20 cruces. Nunca cruzan dos personas a la vez, así que las oclusiones siguen sin evaluar.
```

## III-C · Discusión

Reemplaza desde "El resultado final de un clip" hasta el final de la subsección.

```latex
El resultado final de un clip no alcanza para validar: sin contar ningún cruce, el detector preentrenado termina con la carga correcta de 0 pasajeros. Por eso la evaluación compara cada cruce.

El acierto de 20 de 20 indica que el sistema funciona en esta escena, no que generalice: todos los tramos comparten persona, ropa, cámara y piso, y la referencia proviene de las mismas cajas anotadas. El ajuste además especializó al modelo: en dos imágenes de ejemplo con personas de frente pasa de 4 a 2 y de 2 a 1 detecciones. Los datos actuales no representan las condiciones reales de un bus.
```

## IV · Conclusiones y trabajo futuro

Reemplaza los tres párrafos de la sección.

```latex
La API, el contrato de eventos, el cálculo por parada, el panel, la carga de JSON y el arranque con Docker están implementados y verificados en Linux y Windows. El conteo desde video funciona de punta a punta en macOS sobre un video de oficina, pero el objetivo completo todavía no está demostrado, porque falta evaluarlo en grabaciones independientes.

Una lección del trabajo es que un contrato simple y probado permite avanzar en paralelo y mantiene visibles los errores. Otra es que una métrica perfecta en una sola grabación no prueba generalización. Las limitaciones actuales son una sola grabación con una sola persona, la ausencia de cruces simultáneos, un detector especializado en vista cenital, el análisis de una sola puerta y que el recorrido se consulta por archivo y no en tiempo real.

El trabajo futuro comprende evaluar ambos detectores en clips independientes con varias personas, documentar un caso de oclusión y conectar el video con el contador durante la reproducción. Con clips locales se podrá estimar el desempeño en condiciones cercanas a las del Gran Asunción.
```

## Referencias

Agregá estas dos entradas a `referencias.bib`:

```bibtex
@misc{yolo11,
  author       = {Jocher, Glenn and Qiu, Jing},
  title        = {Ultralytics {YOLO11}},
  howpublished = {Software, versión 11.0.0},
  year         = {2024},
  url          = {https://github.com/ultralytics/ultralytics},
  note         = {Licencia AGPL-3.0. Accedido: 6 nov. 2026}
}
@inproceedings{coco,
  author    = {Lin, Tsung-Yi and Maire, Michael and Belongie, Serge and Hays, James and Perona, Pietro and Ramanan, Deva and Doll{\'a}r, Piotr and Zitnick, C. Lawrence},
  title     = {Microsoft {COCO}: Common objects in context},
  booktitle = {Proc. Eur. Conf. Comput. Vis. (ECCV)},
  pages     = {740--755},
  year      = {2014},
  note      = {doi: 10.1007/978-3-319-10602-1\_48}
}
```

Reemplazá estas dos entradas:

```bibtex
@inproceedings{zhang2022,
  author    = {Zhang, Yifu and Sun, Peize and Jiang, Yi and Yu, Dongdong and Weng, Fucheng and Yuan, Zehuan and Luo, Ping and Liu, Wenyu and Wang, Xinggang},
  title     = {{ByteTrack}: Multi-object tracking by associating every detection box},
  booktitle = {Proc. Eur. Conf. Comput. Vis. (ECCV)},
  pages     = {1--21},
  year      = {2022},
  note      = {doi: 10.1007/978-3-031-20047-2\_1}
}
@misc{video,
  author       = {Niel, Mike},
  title        = {Fast Run Test in Office- Automatic Passenger Counter System},
  howpublished = {Video en YouTube, 23 feb. 2017},
  url          = {https://www.youtube.com/watch?v=L1fkyVQbHOg},
  note         = {Accedido: 6 nov. 2026}
}
```

En `ultralytics`, el título coincide con la página y solo cambia la fecha de acceso a 6 nov. 2026.

| Referencia | Cómo se verificó el 6 de noviembre de 2026 |
|---|---|
| YOLO11 | Cita recomendada en [la documentación de Ultralytics](https://docs.ultralytics.com/models/yolo11/). Según esa página, no hay un artículo formal revisado por pares |
| ByteTrack | [Crossref](https://api.crossref.org/works/10.1007/978-3-031-20047-2_1) y [arXiv](https://arxiv.org/abs/2110.06864) |
| COCO | [Crossref](https://api.crossref.org/works/10.1007/978-3-319-10602-1_48). La versión publicada tiene 8 autores; la de arXiv, 10 |
| Seguimiento en Ultralytics | [Página de la documentación](https://docs.ultralytics.com/modes/track/) |
| Video | Metadatos de YouTube leídos con `yt-dlp`: título, canal y fecha |

## Otros cambios que quedan para Álvaro

- **Título:** "arquitectura y verificación del software" ya no describe todo el trabajo.
- **Introducción:** el último párrafo, "La contribución actual", no menciona el conteo desde video.
- **Fig. 1:** pasar los tres nodos de visión de `pen` a `ok` y sus flechas de `fd` a `fl`, borrar el nodo "pendiente" y actualizar la leyenda.
- **Tabla I:** se puede agregar una fila con las pruebas de visión en macOS. Tomá la cifra de `python -m pytest tests -v` después de integrar.
- **Encabezado:** quitar "sin métricas de visión" y, para la entrega, la marca de borrador.
- **Fig. 3:** reproduce cuadros de un video de terceros, citado en la leyenda. Conviene confirmar con la cátedra que sea aceptable.

## De dónde sale cada cifra

| Dato | Fuente |
|---|---|
| Aciertos, omisiones, falsos positivos, F1, errores y FPS | [`oficina-comparacion.json`](../../evaluation/results/oficina-comparacion.json), con `python -m evaluation.comparar_oficina` |
| Parámetros del ajuste y conteo de cuadros | [`oficina-ajuste.json`](../../evaluation/results/oficina-ajuste.json) y [`oficina-cajas.json`](../../data/annotations/oficina-cajas.json) |
| Ensayo de 0 a 6 s | [`oficina-00-06-prediccion.json`](../../evaluation/results/oficina-00-06-prediccion.json) y [el relevo del primer clip](../relevo/vision-primer-clip/README.md) |
| Resultado de la Fig. 3 | `python -m evaluation.figura_perdida_id` |
| Clasificación de las 8 omisiones | Seguimiento por cuadro de los tracks de la configuración calibrada, a ±0,8 s de cada cruce omitido, resumido abajo |
| Detecciones con personas de frente | `bus.jpg` y `zidane.jpg` de Ultralytics 8.4.203, con confianza ≥ 0,25, con cada modelo |

| Cruce omitido | IDs observados | Tipo |
|---|---|---|
| Bajada, 9,6 s | ID 7 arriba hasta 9,36 s; ID 8 abajo desde 9,68 s | Hueco de detección |
| Subida, 11,88 s | ID 11 abajo; ID 12 arriba desde 11,84 s | Cambio de ID |
| Bajada, 14,52 s | ID 13 arriba hasta 14,16 s; ID 14 abajo desde 14,64 s | Hueco de detección |
| Bajada, 19,92 s | ID 20 arriba hasta 19,48 s; ID 21 abajo desde 20,08 s | Hueco de detección |
| Bajada, 30,36 s | ID 35 arriba hasta 30,04 s; ID 37 abajo desde 30,40 s | Hueco de detección |
| Subida, 43,8 s | ID 59 abajo; ID 62 arriba desde 43,84 s | Cambio de ID |
| Bajada, 45,96 s | Solo ID 68, abajo | Un solo lado |
| Subida, 48,36 s | Solo ID 77, arriba | Un solo lado |
