# Revisión de `data/annotations/oficina-cajas.json` antes de entrenar (tarea 10)

Revisión de Claude el 7 nov. 2026. **No se corrigió nada**: Álvaro eligió entrenar con el archivo tal como está (opción A), para reproducir el ajuste documentado.

## Validación de formato (automática)

- **Cuadros:** 165 en total, sin duplicados, del 150 al 1278. Ninguno antes de 6 s, así que el ensayo de 0–6 s queda fuera.
- **Particiones:** entrenamiento con 113 con persona y 18 sin persona; reserva con 30 con persona y 4 sin persona. Coincide con el resumen del ajuste documentado.
- **Tiempos:** `tiempo_s` = cuadro / 25 en todos.
- **Cajas:** todas dentro del recorte de 222×176. Solo los cuadros `vacio` y `sombra` no tienen caja.
- **Huellas:** el SHA-256 del archivo y del video coinciden con los registrados.

## Revisión visual

Se dibujaron las 143 cajas sobre sus cuadros. Casi todas encuadran bien a la persona. Quedan como **pendientes de revisión humana**:

| Cuadros | Anotación | Duda |
|---|---|---|
| 168, 549, 945, 1200 | Caja de persona en el borde inferior, sobre una forma oscura | Podrían ser manos o cabeza entrando por abajo, o sombra |
| 249 | Caja sobre piernas en el borde inferior | Persona cortada por el borde; la sombra queda encima |
| 159, 939, 1194 | `sombra`, sin caja | Coincide con lo visible |
| 768, 891, 1158 | Descartados por ambiguos | Se ve una pequeña forma oscura abajo; dejarlos fuera parece razonable |

Además, varias cajas encuadran a personas cortadas en los bordes superior e inferior: 441, 708, 867, 870, 1221, 1257, 1260 y 285, 288, 417, 810. El criterio («persona aunque esté parcialmente fuera») es coherente, pero conviene confirmarlo.

Imagen de los cuadros dudosos: `cuadros-a-revisar.jpg`, en esta carpeta.
