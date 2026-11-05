# Guion de la demo · 10 minutos

Defensa: 10 minutos de exposición y 2 de preguntas. Los textos entre comillas son una propuesta para decir en voz alta. Adaptalos a tus palabras.

## Preparación previa · 30 minutos antes

Responsable: Álvaro, con el compañero para el material de visión.

1. Iniciá Docker Desktop y esperá a que el motor Linux esté disponible.
2. Desde la raíz del repo, arrancá los servicios:

   ```powershell
   docker compose up --build -d
   docker compose ps
   curl.exe http://127.0.0.1:8001/openapi.json -o NUL -w "API %{http_code}`n"
   curl.exe http://127.0.0.1:8502/_stcore/health
   ```

   Esperado: `api` en estado healthy, `API 200` y `ok`.
3. Abrí http://127.0.0.1:8502 y comprobá que el panel muestre la demo con 4 pasajeros y 20 %.
4. Confirmá que el panel se vea en tema claro, que es el predeterminado del proyecto. Si no, elegilo en menú ⋮ > Settings > Light.
5. Confirmá que estén disponibles sin internet los clips, los pesos, el video anotado y estos JSON: `docs/demo/recorrido.json`, `docs/demo/oficina-00-06-manual.json` y las predicciones de visión.
6. Recorré el bloque 5–8 una vez completo. Después recargá la página para volver a capacidad 20.
7. Dejá abiertos, en este orden: las diapositivas, el video anotado y el panel. Ampliá la ventana para que el gráfico quede a la vista junto a los indicadores.

**Respaldo:** si Docker falla, usá la ejecución manual del README (API en 8000, panel en 8501). Si tampoco funciona, mostrá las capturas de `docs/relevo/2026-11-05-claude-tarea03/capturas/`.

## 0:00–2:00 · Álvaro · Problema, objetivo y arquitectura

Pantalla: una diapositiva con el problema y la Fig. 1 del informe.

> "Para auditar la calidad del servicio de buses en el Gran Asunción, no alcanza con saber cuántas personas subieron en total. Hace falta saber cuánta gente lleva la unidad en cada parada y qué porcentaje de su capacidad representa.
>
> Nuestro objetivo es contar subidas y bajadas en la puerta de un bus y reconstruir la ocupación a lo largo de un recorrido simulado, como la vería una empresa de transporte.
>
> El sistema tiene dos partes unidas por un contrato. La primera mira el video: detecta personas, las sigue y decide cuándo cruzan una línea virtual. Cada cruce se convierte en un evento con su tiempo, su identificador y su sentido. La segunda parte recibe esos eventos. Una API en FastAPI los asigna a paradas y calcula pasajeros y porcentaje. Un panel en Streamlit muestra el resultado, y todo arranca con Docker.
>
> Esa separación nos permitió probar el cálculo con eventos conocidos antes de tener el modelo. Ahora mi compañero muestra la parte de visión, y después yo muestro cómo esos eventos se convierten en ocupación."

## 2:00–5:00 · Compañero · Detección, seguimiento y oclusión

Pantalla: video anotado con línea, ID y sentido.

Contenido:

1. Qué detector se usó y cómo se ajustó.
2. Cómo ByteTrack conserva el ID entre cuadros.
3. Cómo la línea decide un cruce y evita el doble conteo.
4. Un caso de oclusión, con su instante y su efecto en el conteo.

**Material que debe aportar el compañero:**

- Video anotado que se reproduzca sin internet, en la máquina de defensa.
- Configuración de la escena: recorte, línea y orientación.
- Detector, pesos y parámetros usados.
- Fotograma o tramo del caso de oclusión, con su instante y su efecto.
- JSON de predicciones generado por el pipeline.

## 5:00–8:00 · Álvaro · Panel en vivo

Ensayado contra Docker en Windows. Valores en [el relevo](../relevo/2026-11-05-claude-tarea04/README.md).

| Tiempo | Acción | Se debe ver |
|---|---|---|
| 5:00 | Mostrar el panel en 8502 con la demo | Recorrido: demo sintética; capacidad 20; carga 3 |
| 5:20 | Mover el selector a 0 s | 3 pasajeros, 15 % |
| 5:40 | Mover a 5 s | 5 pasajeros, 25 %; una barra, parcial |
| 6:00 | Mover a 10 s | 4 pasajeros, 20 %; dos barras |
| 6:15 | Revisar tabla y gráfico | Parada 1: 5 y 25 %. Parada 2: 4 y 20 % |
| 6:40 | Cambiar la capacidad a 40 | 4 pasajeros, 10 %; tabla 12,5 y 10 |
| 7:10 | Cargar `docs/demo/oficina-00-06-manual.json` | Recorrido de oficina; capacidad 20; carga 0 |
| 7:25 | Mover a 0, 2 y 4 s | 0 → 1 (5 %) → 0 |
| 7:50 | Si hay predicciones, cargarlas | Comparar con la referencia manual |

Para el selector: hacé clic en el control y usá las flechas ← y →. Desde 10 s son 11 pasos hasta 0 s, porque existe la marca de 4,2 s; desde 0 s son 6 pasos hasta 5 s.

> "Este panel está corriendo en Docker, con la API y la interfaz como servicios separados. Estos son eventos sintéticos: los usamos porque conocemos el resultado correcto.
>
> Al inicio hay 3 pasajeros, que con capacidad 20 son 15 %. A los 5 segundos subieron dos personas, así que hay 5, o sea 25 %. La barra aparece como parcial porque el conteo de esa parada llega solo hasta el instante elegido.
>
> A los 10 segundos empieza la segunda parada y baja una persona. Quedan 4 pasajeros, 20 %. El gráfico y la tabla usan el mismo resultado de la API: la primera parada cerró con 5 y la segunda va en 4.
>
> Si cambio la capacidad a 40, el conteo sigue en 4 pero la ocupación baja a 10 %, porque es 100 por pasajeros sobre capacidad. El conteo depende de los eventos; el porcentaje depende además de la capacidad.
>
> Ahora cargo el ensayo de oficina. Es una referencia manual aproximada, no una predicción del modelo: una oficina que simula la puerta de un bus, con una subida cerca de 2 segundos y una bajada cerca de 4. Pasamos de 0 a 1, que es 5 %, y volvemos a 0.
>
> Este mismo formato de archivo es el que produce el módulo de visión. Mi compañero compara ahora esas predicciones con el conteo manual."

**Si algo falla:** si aparece un aviso de la API, leelo en voz alta y seguí con la demo. Si el panel no conecta, usá `docker compose ps` y `docker compose logs api`. Si se pierde tiempo, omití el cambio de capacidad antes que la oficina.

## 8:00–10:00 · Compañero · Comparación con el conteo manual y limitaciones

Pantalla: tabla de resultados.

Contenido:

1. Comparación cruce por cruce: dos eventos omitidos pueden dar el mismo total que dos correctos.
2. Error observado y un fotograma que lo explique.
3. Limitaciones del sistema y de los datos.
4. Cierre con lo aprendido y el trabajo futuro.

**Mediciones pendientes:** aciertos, omisiones y falsos positivos por sentido; F1 por sentido; error absoluto medio por clip; cuadros por segundo; hardware, resolución y FPS del video. Deben salir del evaluador, en clips reservados. Para decir "tiempo real", comparen los cuadros procesados por segundo con los del video en la máquina de defensa.

## Preguntas probables

1. **¿Cómo calculan la ocupación?**
   Con carga inicial más subidas menos bajadas, dividido por la capacidad y multiplicado por 100. Lo calcula `POST /ocupacion`. Un evento justo al inicio de una parada pertenece a esa parada.

2. **¿Qué pasa si el conteo da negativo?**
   No se corrige. Queda registrado y el panel muestra un aviso, porque indica un error de conteo. Con carga 0, capacidad 20 y una bajada, da −1 pasajero y −5 %.

3. **¿Cómo verificaron que el software funciona?**
   Con siete pruebas de la API y recorridos del navegador en el panel, que coincidieron entre Linux y Windows. Esto verifica el software de ocupación con eventos conocidos, no el modelo de visión.

4. **¿Qué tan preciso es el conteo?**
   *Dato pendiente de visión.* Debe responderse con F1 por sentido y error absoluto medio por clip, medidos en clips reservados. Hoy no hay una cifra válida.

5. **¿Cómo manejan las oclusiones cuando suben varias personas juntas?**
   *Dato pendiente de visión.* El plan usa ByteTrack, que también asocia detecciones de baja confianza con trayectorias existentes. El compañero debe mostrar un caso real y su efecto en el conteo.

6. **¿Funciona en tiempo real?**
   *Dato pendiente de visión.* Hoy el panel consulta eventos ya generados y no procesa video. Para afirmarlo hay que medir los cuadros por segundo en la máquina de defensa y compararlos con los del video.
