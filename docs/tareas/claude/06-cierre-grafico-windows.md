# 06 · Verificar el gráfico en Windows y actualizar la figura 2

Trabajá sobre la copia local de `tareas-03-04-panel-informe`, con los cambios de la tarea 05. Guardá la nueva evidencia en `docs/relevo/2026-11-06-claude-tarea06/`. El [relevo de Linux](../../relevo/2026-11-06-claude-tarea05/README.md) contiene el resultado de referencia.

1. Desde PowerShell en la raíz, con Docker Desktop iniciado, ejecutá:

   ```powershell
   docker compose up --build -d
   docker compose ps
   $t05 = 'docs/relevo/2026-11-06-claude-tarea05'
   $t06 = 'docs/relevo/2026-11-06-claude-tarea06'
   $env:PANEL_URL = 'http://127.0.0.1:8502'
   $env:PYTHONUTF8 = '1'
   .\.venv\Scripts\python.exe "$t05/scripts/verificar_grafico.py" "$t05/casos/oficina-00-06-prediccion.json" "$t05/casos" "$t06/windows"
   ```

2. Confirmá código de salida 0 y abrí `windows/resultado.json`. Debe registrar **45 estados, 32 transiciones de la predicción y cero fallos**. Inspeccioná una captura a 2,16 s: indicador, tabla, barra y rótulo deben coincidir en 5 %. Conservá resultados y capturas. Si solo tenés acceso a Linux, entregale el bloque PowerShell a Álvaro y marcá Windows pendiente hasta recibir la salida.
3. Capturá el gráfico corregido de la **demo a 10 s**, con capacidad 20 y carga inicial 3. Usá una captura que conserve ejes, nombres de paradas, valores **25 % y 20 %** y la referencia del 100 %. Actualizá `docs/informe/grafico-demo.png` y recompilá `informe-borrador.pdf` siguiendo el README del informe. Abrí el PDF, confirmá exactamente tres páginas y verificá que la figura 2 se lea a tamaño de columna. Esta parte también puede realizarse en Linux con el gráfico ya verificado allí.
4. Documentá entorno, comandos, resultados, archivos modificados y pendientes en el README de la devolución. Actualizá `resumen.md` con lo efectivamente verificado y dejá los cambios sin commit para revisión.
