# Validación con PAMELA `B-No` y `B-Oy` · prerregistro (9 nov., 00:00 aprox.)

Lo escribió Claude a pedido de Álvaro, **antes de anotar y de ejecutar cualquier modelo** sobre estos videos. Según los registros de las tareas 09 a 14, nunca se procesaron: la tarea 09 los reservó («no se usarán para ajustar nada»).

Para fijar la geometría, Claude solo miró 8 cuadros sueltos de cada video, sin ningún modelo y sin anotar cruces.

## Qué valida y qué no

- **Valida:** grabaciones **nuevas**, con subidas muy densas. Es el caso de oclusiones de la consigna, que hasta ahora no tenía una prueba sin usar.
- **No valida una escena nueva:** usan la misma cámara, puerta y laboratorio que PAMELA A, que sirvió para elegir parámetros. En el informe se presenta como «grabaciones nuevas de la misma escena».

## Insumos

| Video | SHA-256 | Duración | Contenido |
|---|---|---|---|
| `data/raw/puerta-tren-d800-B-No.mp4` | `58d945ab2a876d563dcbdfe07b9cf9697aa842c9999458e061b5d8a3530ec650` | 750 cuadros, 25 FPS, 352×288 | Subida sin tarjeta |
| `data/raw/puerta-tren-d800-B-Oy.mp4` | `00151d75110b95fe4d1d8aff61dc5bfadaf10b83b6808acd2251c7d3802d43ea` | 748 cuadros, 25 FPS, 352×288 | Subida con tarjeta |

**Geometría,** la misma de PAMELA A en la tarea 11:

- recorte `96,64,160,224`;
- línea `0,96,159,96` dentro del recorte, que en el cuadro completo va de `96,160` a `255,160`, sobre el borde del andén frente a la puerta;
- interior **arriba**, porque el tren está arriba: cruzar hacia arriba es una subida.

## 1. Referencia humana (Álvaro, antes de ejecutar nada)

Desde la raíz del worktree, para cada video:

```powershell
.\.venv\Scripts\python.exe docs\relevo\2026-11-08-claude-tarea11\anotar_cruces.py --video data\raw\puerta-tren-d800-B-No.mp4 --salida data\annotations\pamela-B-No-cruces.json --linea 96,160,255,160
.\.venv\Scripts\python.exe docs\relevo\2026-11-08-claude-tarea11\anotar_cruces.py --video data\raw\puerta-tren-d800-B-Oy.mp4 --salida data\annotations\pamela-B-Oy-cruces.json --linea 96,160,255,160
```

**Teclas:**

| Tecla | Acción |
|---|---|
| Espacio | Pausa o sigue |
| S | Subida |
| B | Bajada |
| Z | Deshace la última marca |
| A / D | Retrocede o avanza 2 s |
| , / . | Un cuadro atrás o adelante |
| + / − | Más o menos velocidad |
| G | Guarda y sale |

Para seguir una anotación ya empezada, agregá `--continuar` al comando.

**Criterio:**

- **Qué se cuenta:** una persona cruza cuando su **cabeza** pasa la línea amarilla del andén.
  - Si vuelve a salir, se marca una bajada.
  - Quien queda parado sobre la línea sin pasarla no cuenta.
- **Dónde:** solo cuentan los cruces dentro del recorte, que ocupa todo el ancho de la puerta.
- **Cómo:** la densidad es alta, así que conviene ir cuadro a cuadro (`,` y `.`) cuando varias personas pasan juntas. El instante no tiene que ser exacto: la tolerancia es de ±1 s.
- **Dudas:** cuando no estés seguro, anotalo en `notas` del JSON. **No mires ninguna salida del modelo** sobre estos videos antes de terminar.

Al terminar, registrá el SHA-256 de cada referencia:

```powershell
Get-FileHash data\annotations\pamela-B-*-cruces.json
```

## 2. Configuración congelada (la de la API, sin cambios)

| Parámetro | Valor |
|---|---|
| Pesos | `yolo11n.pt`, SHA-256 `0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1` |
| Rastreador | `vision/bytetrack-cenital.yaml`, SHA-256 `1b547a4254ede161d37efb6ed6e5d3302e313559930953fc60d3be181e3b5c69` |
| Umbrales de la regla | `--conf 0.05`, `--confirmacion 2`, margen de 5 px, punto central |
| Procesamiento | Sin ritmo real (todos los cuadros) y sin filtros |
| Dispositivo | CPU. El resultado no debería depender del dispositivo, pero se fija para que sea comparable con las otras escenas |
| Commit del código | `4e15b7c` o posterior, siempre que no cambie `vision/` ni el rastreador |

## 3. Ejecución única

`prueba-pamela-b.ps1`, en esta carpeta:

- no arranca si falta una referencia o si ya existe la carpeta de salida;
- verifica los hashes de los videos y de los pesos;
- procesa cada video una vez y evalúa con tolerancia de ±1 s.

## 4. Qué se informa y criterio

- **Métricas:** por video y por sentido, TP, FP, FN, precisión, exhaustividad, F1 y error de conteo. Además, la ocupación neta predicha frente a la real.
- **Sin ajustes posteriores:** ningún resultado cambia parámetros. Si se prueba una corrección después de ver los resultados, estos videos pasan a ser de desarrollo y se rotulan así.
- **En el informe,** el resultado va en la Tabla II como «PAMELA B (validación, misma escena)», sea bueno o malo.
