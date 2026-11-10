# Tarea 10 - entrenar el "ajustado reproducido en Windows" y compararlo con el base en Kaggle y PAMELA A.
# Ejecutar en PowerShell, desde cualquier carpeta:
#   powershell -ExecutionPolicy Bypass -File C:\Users\Alvaro\Desktop\Facultad\4to\IA\TpFinal\.worktrees\integracion-video\docs\relevo\2026-11-08-claude-tarea10\entrenar-y-evaluar.ps1
# Sigue preregistro.md. No toca los videos youtube-* (reservados), no escribe en evaluation/results ni en Git.

$ErrorActionPreference = 'Continue'  # Ultralytics escribe en stderr; los fallos se detectan por codigo de salida
$env:PYTHONUTF8 = '1'
[Console]::OutputEncoding = [Text.UTF8Encoding]::new()
$wt = (Resolve-Path "$PSScriptRoot\..\..\..").Path
Set-Location $wt
$py = "$wt\.venv\Scripts\python.exe"
$t10 = 'docs\relevo\2026-11-08-claude-tarea10'
$out = "$t10\windows"
New-Item -ItemType Directory -Force $out | Out-Null
function Paso($n) { Write-Host "`n== $n" -ForegroundColor Cyan }
function Guardar($archivo) { $input | Out-File -Encoding utf8 -FilePath $archivo }

Paso '1. Insumos y entorno'
$esperado = @{
  'data\raw\oficina.mp4' = '02666C2E567F45015A2E73FE802DB8F39C6C568D41EF42EFC63997DE4D15FC95'
  'yolo11n.pt' = '0EBBC80D4A7680D14987A577CD21342B65ECFD94632BD9A8DA63AE6417644EE1'
  'data\annotations\oficina-cajas.json' = '95CE9391B939B5F9561819A1353E0317BCB8F4C396D3CFEAD76092BE38B7C2FF'
}
& {
  Get-Date -Format o
  (Get-CimInstance Win32_OperatingSystem).Caption + ' ' + (Get-CimInstance Win32_OperatingSystem).Version
  (Get-CimInstance Win32_Processor).Name
  & $py --version
  & $py -m pip list 2>$null | Select-String -Pattern '^(ultralytics|torch|torchvision|opencv-python|lap|numpy) '
  foreach ($f in $esperado.Keys) {
    $h = (Get-FileHash $f -Algorithm SHA256).Hash
    "$f  $h  " + $(if ($h -eq $esperado[$f]) { 'OK' } else { 'NO COINCIDE' })
  }
} 2>&1 | Guardar "$out\01-entorno.txt"
Get-Content "$out\01-entorno.txt"
if (Select-String -Path "$out\01-entorno.txt" -Pattern 'NO COINCIDE' -Quiet) { throw 'Un insumo no coincide con su SHA-256: se detiene antes de entrenar.' }

Paso '2. Entrenamiento (puede tardar 15-40 min)'
$inicio = Get-Date
& $py -m vision.train --anotaciones data/annotations/oficina-cajas.json --salida runs/oficina-ajuste-windows --resumen "$out/entrenamiento.json" --pesos yolo11n.pt --epocas 40 --tamano 640 --lote 16 --semilla 0 --dispositivo cpu 2>&1 | Guardar "$out\02-entrenamiento.txt"
if ($LASTEXITCODE -ne 0) { throw "El entrenamiento fallo (codigo $LASTEXITCODE). Ver $out\02-entrenamiento.txt" }
"duracion total (s): $([math]::Round(((Get-Date) - $inicio).TotalSeconds, 1))" | Add-Content "$out\02-entrenamiento.txt"
Get-Content "$out\02-entrenamiento.txt" -Tail 4

Paso '3. Registrar pesos antes de evaluar'
$pesos = 'runs/oficina-ajuste-windows/oficina-ajustado.pt'
$sha = (Get-FileHash $pesos -Algorithm SHA256).Hash.ToLower()
@{ nombre = 'ajustado reproducido en Windows'; ruta = $pesos; sha256 = $sha; bytes = (Get-Item $pesos).Length;
   registrado = (Get-Date -Format o); configuraciones = @('base-defecto','base-calibrado','ajustado-defecto','ajustado-calibrado') } |
  ConvertTo-Json | Guardar "$out\pesos-registrados.json"
Get-Content "$out\pesos-registrados.json"

Paso '4. Evaluar (Kaggle, PAMELA A y control en oficina)'
$t09 = 'docs\relevo\2026-11-07-claude-tarea09'
& $py "$t09\prueba-kaggle\evaluar_kaggle.py" "$out\kaggle" --ajustado $pesos --sha-ajustado $sha 2>&1 | Guardar "$out\03-kaggle.txt"
& $py "$t09\prueba-pamela\evaluar_pamela.py" "$out\pamela" --ajustado $pesos --sha-ajustado $sha 2>&1 | Guardar "$out\04-pamela.txt"
& $py "$t09\scripts\evaluar_oficina.py" "$out\oficina-control" --ajustado $pesos --sha-ajustado $sha 2>&1 | Guardar "$out\05-oficina-control.txt"
foreach ($f in '03-kaggle.txt', '04-pamela.txt', '05-oficina-control.txt') { Write-Host "-- $f"; Get-Content "$out\$f" -Tail 6 }

Paso '5. Pruebas'
& $py -m pytest tests -v 2>&1 | Guardar "$out\06-pytest.txt"
"codigo de salida: $LASTEXITCODE" | Add-Content "$out\06-pytest.txt"
Get-Content "$out\06-pytest.txt" -Tail 4
Paso "Listo. Resultados en $wt\$out. Videos anotados en runs\evaluacion\windows-amd64\."
