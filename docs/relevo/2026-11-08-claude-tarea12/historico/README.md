# Versiones de los scripts usadas en la tarea 11 (copias guardadas el 8 nov. en la tarea 12)

Antes de corregir los scripts de la tarea 11 se guardaron copias de las versiones que produjeron su evidencia. Ninguna estaba versionada en Git.

| Archivo | Qué produjo | Procedencia |
|---|---|---|
| `evaluar_detectores.seleccion-linux.py` | `tarea11/linux/`: la selección en Kaggle, PAMELA A y oficina | **Reconstruida.** Es la versión de la prueba final sin los cambios que Claude le agregó después de la selección y antes de la prueba final: la escena `final`, `--rastreadores`, la comprobación de la referencia y el valor por defecto de `--escenas`. Ese parche está documentado en la conversación y lo muestra el `diff` entre los dos archivos. No hay otra copia byte a byte de la versión original. |
| `evaluar_detectores.prueba-final.py` | `tarea11/final-windows/` | Copia exacta del archivo que ejecutó `prueba-final.ps1`. |
| `prueba-final.prueba-final.ps1` | `tarea11/final-windows/` | Copia exacta. |
| `anotar_cruces.prueba-final.py` | `data/annotations/youtube-bus-real-cruces.json` | Copia exacta de la versión con la que anotó Álvaro. Tiene el error de navegación que se corrige en la tarea 12: con `,` retrocede dos cuadros en lugar de uno, y con A/D se mueve 2 s menos un cuadro. |

SHA-256:

```
182e09ef20ca6e67a404e61951f35b1a5f4bf2273b3fbc4b093aa7b10bf21570  evaluar_detectores.seleccion-linux.py
3ed7a5d2df2361bac8e167a04ca37579b5d8cb2f1ba3a414d8f2c6e099745fe7  evaluar_detectores.prueba-final.py
021c6c9c1fd4108702a97b511f3fa701d0119869f66e48f65e87eeb4c599b419  prueba-final.prueba-final.ps1
48b89ebf591ba76b3c0e4e8f5f8fc824abb0bc8c5805ac240cc80b1fb581ee36  anotar_cruces.prueba-final.py
```

**Efecto del error del anotador sobre la referencia final.** El error solo cambia adónde salta la navegación: la tecla `,` muestra un cuadro antes del esperado. El tiempo que se guarda es el del cuadro que efectivamente está en pantalla, así que cada marca corresponde a lo que Álvaro veía. Lo que sí pudo pasar es que, al retroceder, saltara un cuadro y marcara 40 ms más tarde de lo que habría elegido. Ese error queda muy por debajo de la tolerancia de ±1 s.
