# Tarea 10 · Reproducir el ajuste del detector y evaluar su transferencia · devolución (8 nov.)

Rama `integracion-video`, sin commit, push ni merge. No se cambiaron el detector de la API, Docker ni el panel, y no se incorporaron modelos externos. **No se ejecutaron predicciones sobre los dos videos de YouTube reservados.** Se siguió el [prerregistro](preregistro.md), escrito antes de entrenar.

## Conclusión

**El ajuste con oficina no se transfiere: en las dos grabaciones nuevas el ajustado rinde peor que el base.** No hay evidencia para proponer el cambio de modelo.

| Video | Mejor base (calibrado) | Ajustado reproducido |
|---|---|---|
| Oficina (su propio material de entrenamiento) | 11 de 20 | 19 o 20 de 20, sin eventos extra |
| Kaggle (6 subidas) | 5 de 6, con 8 eventos extra | **0 de 6**: no produce ningún evento |
| PAMELA A (28 bajadas) | 10 de 28, con 1 extra | **0 o 1 de 28** |

El detector ajustado se especializó en la escena de oficina: una sola persona, la misma ropa, cámara y alfombra. Fuera de ella deja de ver personas.

**Detecciones sin rastreador** ([`diagnostico/`](diagnostico/)), mayor confianza de persona en uno de cada cinco cuadros:

| Video | Base: cuadros ≥ 0,25 | Ajustado: cuadros ≥ 0,25 | Ajustado: cuadros ≥ 0,05 |
|---|---|---|---|
| Oficina | 26 de 264 | **125 de 264** | 134 |
| Kaggle | 77 de 300 | **0 de 300** | **0** |
| PAMELA A | 32 de 152 | 19 de 152 | 47 |

## Entrenamiento: «ajustado reproducido en Windows»

- **Equipo:** Windows 11 IoT Enterprise LTSC 10.0.26200, AMD Ryzen 5 7535HS, Python 3.12.10, ultralytics 8.4.203, torch 2.15.0, torchvision 0.29.2, opencv-python 5.0.0.93, numpy 2.5.4.
- **Insumos:** clip, `yolo11n.pt` y anotaciones con el SHA-256 esperado. Las anotaciones no se modificaron (opción A); las dudas están en [`revision-anotaciones.md`](revision-anotaciones.md).
- **Comando:**
  ```
  python -m vision.train --anotaciones data/annotations/oficina-cajas.json --salida runs/oficina-ajuste-windows --resumen docs/relevo/2026-11-08-claude-tarea10/windows/entrenamiento.json --pesos yolo11n.pt --epocas 40 --tamano 640 --lote 16 --semilla 0 --dispositivo cpu
  ```
- **Parámetros:** semilla 0 y `deterministic`, el resto según `vision/train.py`.
- **Duración:** 1163 s de entrenamiento (unos 19,5 min); 1172 s el paso completo.
- **Pesos:** `runs/oficina-ajuste-windows/oficina-ajustado.pt`, fuera de Git. Pesa 5.497.114 bytes y su SHA-256 es `69958946ba6d38702566cb6dcc5f48dedde3fc345d8f8cf0ceca25636b32de32`. Se registraron antes de evaluar ([`windows/pesos-registrados.json`](windows/pesos-registrados.json), 00:17). Es **distinto** del ajustado del compañero (`783d16c0…`, macOS).
- **Reserva** (la misma grabación; solo orienta): mAP50 0,995, mAP50-95 0,753, precisión 1,0, exhaustividad 1,0. El compañero había obtenido mAP50-95 0,819.

## Resultados por configuración

En Windows y con tolerancia ±1 s. Cada celda es TP / FP / FN, más el error de conteo.

**Kaggle** (6 subidas, 0 bajadas; referencia de Claude):

| Configuración | Subidas | Error | Bajadas | Error | Eventos | FPS |
|---|---|---|---|---|---|---|
| base-defecto | 1 / 0 / 5 | 5 | 0 / 1 / 0 | 1 | 2 | 20,7 |
| base-calibrado (API) | 5 / 5 / 1 | 4 | 0 / 3 / 0 | 3 | 13 | 21,4 |
| ajustado-defecto | 0 / 0 / 6 | 6 | 0 / 0 / 0 | 0 | 0 | 22,1 |
| ajustado-calibrado | 0 / 0 / 6 | 6 | 0 / 0 / 0 | 0 | 0 | 22,4 |

**PAMELA A** (28 bajadas, 0 subidas; referencia de Claude):

| Configuración | Bajadas | Error | Subidas | Error | Eventos | FPS |
|---|---|---|---|---|---|---|
| base-defecto | 1 / 0 / 27 | 27 | 0 / 1 / 0 | 1 | 2 | 27,9 |
| base-calibrado (API) | 10 / 0 / 18 | 18 | 0 / 1 / 0 | 1 | 11 | 29,1 |
| ajustado-defecto | 0 / 0 / 28 | 28 | 0 / 0 / 0 | 0 | 0 | 30,1 |
| ajustado-calibrado | 1 / 0 / 27 | 27 | 0 / 0 / 0 | 0 | 1 | 28,6 |

**Oficina, control de la reproducción** (no es evaluación: es material de entrenamiento):

| Configuración | 0–6 s, subidas / bajadas | Video completo, subidas | Video completo, bajadas |
|---|---|---|---|
| base-defecto | 0/0/1 · 0/0/1 | 0 / 0 / 10 | 0 / 0 / 10 |
| base-calibrado | 1/0/0 · 0/0/1 | 7 / 0 / 3 | 4 / 0 / 6 |
| ajustado-defecto | 1/0/0 · 1/0/0 | 10 / 0 / 0 | 9 / 0 / 1 |
| ajustado-calibrado | 1/0/0 · 1/0/0 | 10 / 0 / 0 | 10 / 0 / 0 |

La reproducción se parece a la del compañero, que obtuvo 20 de 20 en las dos configuraciones del ajustado, aunque con 2 extra en la calibrada. Entonces el resultado de las pruebas externas no se explica por un entrenamiento fallido.

**Cómo leer las comparaciones:**
- **Detectores, con el mismo rastreador:** base-calibrado frente a ajustado-calibrado, y base-defecto frente a ajustado-defecto. En Kaggle y PAMELA el ajustado empeora en las dos parejas.
- **Sistemas completos:** la API actual (base-calibrado) frente a la propuesta del compañero (ajustado-defecto). La propuesta tampoco detecta nada en las dos pruebas.

**Plataforma:** en PAMELA, el base dio exactamente los mismos eventos en Windows que en Linux (tarea 09). En Kaggle no:
- base-calibrado en Linux: subidas 5/4/1 y bajadas 0/4/0;
- base-calibrado en Windows: subidas 5/5/1 y bajadas 0/3/0;
- base-defecto: la bajada falsa aparece a 14,72 s en Linux y a 14,96 s en Windows.

El sistema base es sensible a la plataforma en escenas de alta resolución concurridas. La causa no está medida.

## Pruebas

`pytest tests -v` en Windows ([`windows/06-pytest.txt`](windows/06-pytest.txt)): **99 aprobadas, 1 omitida y 1 fallida.**
- **Fallida:** `test_ensayo_de_oficina_…`, la bajada omitida del base, sin modificar.
- **Omitida:** `test_detector_ajustado_cuenta_el_ensayo…`, porque busca los pesos del compañero en `runs/oficina-ajuste/`. Los reproducidos están en otra carpeta a propósito, para no confundirlos.

## Archivos

- `preregistro.md`, `revision-anotaciones.md` y `cuadros-a-revisar.jpg`.
- `entrenar-y-evaluar.ps1`: el script ejecutado.
- `windows/`: entorno, entrenamiento, pesos registrados, eventos, métricas por configuración y pruebas.
- `diagnostico/`: confianza sin rastreador, con script y datos por video. Se calculó en el contenedor Linux con los mismos pesos, verificados por su hash.
- **Videos anotados para inspección local:** `runs/evaluacion/windows-amd64/`, fuera de Git.
- **Scripts de la tarea 09 modificados:** `evaluar_kaggle.py`, `evaluar_pamela.py` y `evaluar_oficina.py` ahora aceptan `--sha-ajustado`, para validar los pesos reproducidos.

## Qué mejoró, qué sigue fallando y qué sigue

- **Mejoró, solo en oficina:** el ajustado cuenta 19 o 20 de 20, sin extra, y resuelve la bajada del ensayo de 0–6 s. **Eso no demuestra generalización:** es el material con el que se entrenó.
- **Sigue fallando:**
  - **Base calibrado, el de la API:** en Kaggle inventa eventos (8 en Windows) y en PAMELA pierde 18 de 28.
  - **Ajustado:** en las dos pruebas externas no detecta a casi nadie.
  - **Prueba del ensayo:** `test_ensayo_de_oficina_…` sigue fallando.
- **¿Hay evidencia para cambiar de modelo?** **No.** Cambiar al ajustado empeoraría el sistema fuera de oficina. Mantener el base tampoco da un conteo confiable.
- **Siguiente paso:** entrenar con **varias escenas** y evaluar en otras distintas. Por ejemplo:
  - los videos de entrenamiento oficiales de PAMELA (R1–R4), si llegan las credenciales;
  - grabaciones propias.

  Siempre con la prueba reservada, como los dos videos de YouTube.
- **Advertencias:**
  - Las referencias de Kaggle y PAMELA las hizo Claude y **siguen pendientes de revisión humana**.
  - Ajustar con oficina no demuestra generalización, y estos resultados muestran que en este caso no la hay.
