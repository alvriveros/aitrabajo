# Protocolo de validación nueva (preparado el 8 nov., pendiente de video)

Es para la próxima prueba ciega. **No se descargó ni se eligió ningún video.** Hace falta una grabación nueva, que ningún modelo ni Claude hayan procesado.

## 1. Material (lo consigue Álvaro)

- **Cámara:** cenital o alta sobre una puerta, idealmente de un bus o colectivo real. Si no es posible, una puerta de aula u oficina con gente que la cruce a propósito.
- **Duración:** al menos 3 minutos.
- **Qué tiene que tener:**
  - subidas y bajadas;
  - al menos tres pares de personas que crucen en el mismo sentido con menos de 1,5 s de diferencia (ponen a prueba la supresión);
  - alguien que se detenga sobre la línea y retroceda (oscilación);
  - momentos en que una persona tape a otra;
  - por lo menos 30 s seguidos sin cruces.
- **Dónde va:** `data/raw/validacion-nueva-<fecha>.mp4`, fuera de Git. Se registra su SHA-256 apenas se copia.
- **Privacidad:** las personas grabadas tienen que saber que se las graba. El video no se publica.

## 2. Antes de abrir cualquier modelo

1. **Geometría:** fijar recorte, línea y sentido interior mirando cuadros sueltos, y anotarlos en `prerregistro-validacion.md`.
2. **Referencia humana:** anotarla con `anotar_cruces.py --video … --salida data/annotations/validacion-nueva-cruces.json --linea-y …`. Agregar en `notas` las dudas y cualquier diferencia con contadores externos. Registrar su SHA-256.
3. **Congelar el candidato** con su configuración exacta: detector, rastreador, `u` del filtro si alguno se justificó y SHA de los pesos. Si la tarea 12 no justificó ningún filtro, el candidato es `yolo11l` calibrado sin filtro.
4. **Fijar:**
   - tolerancia de ±1 s;
   - el entorno: misma máquina y misma GPU para candidato y API;
   - una carpeta de salida nueva (el arnés rechaza las que ya tienen resultados).

## 3. Ejecución

- **Una sola vez,** candidato contra API actual (`yolo11n` calibrado), con `evaluar_detectores.py` y una escena nueva agregada antes de ejecutar.
- **Si hay filtro:** se aplica con `supresion.suprimir` sobre los eventos guardados, con la `u` congelada.

## 4. Criterio de decisión

- **El candidato es mejor si tiene menos FN + FP que la API y procesa al menos 10 FPS en la RTX 2050.**
- **Además,** se informan TP, FP, FN y error de conteo **por sentido**. Una mejora del total que aumente las omisiones en algún sentido se informa como tal y no cuenta como mejora.
- **Ningún resultado cambia la API por sí solo:** es evidencia para que Álvaro y Codex la revisen.

## Pendiente

El video y la referencia, a cargo de Álvaro. Sin ellos, esta fase queda preparada pero sin ejecutar.

## Agregado posterior (8 nov., noche, tarea 13): ejecución desde el panel

La ejecución del paso 3 se puede hacer desde el panel, en «Video nuevo». Usa las mismas opciones de modelo de la API y guarda el SHA del video, la geometría y la configuración en `runs/panel/<id>/entrada.json`.

La geometría se fija primero en la vista previa del panel, que no ejecuta el modelo, porque el anotador necesita la línea; después se anota con `anotar_cruces.py --linea X1,Y1,X2,Y2`, en coordenadas del cuadro completo. Los pasos exactos están en `docs/relevo/2026-11-08-claude-tarea13/README.md`.
