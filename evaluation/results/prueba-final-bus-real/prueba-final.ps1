# Prueba final (tarea 11): yolo11n calibrado (API actual) contra yolo11l calibrado en youtube-bus-real.
# Requiere antes la referencia humana data\annotations\youtube-bus-real-cruces.json (ver prerregistro-final.md).
# Ejecutar en PowerShell, desde cualquier carpeta:
#   powershell -ExecutionPolicy Bypass -File C:\Users\Alvaro\Desktop\Facultad\4to\IA\TpFinal\.worktrees\integracion-video\docs\relevo\2026-11-08-claude-tarea11\prueba-final.ps1

$ErrorActionPreference = 'Continue'  # Ultralytics escribe en stderr; los fallos se detectan por codigo de salida
$env:PYTHONUTF8 = '1'
[Console]::OutputEncoding = [Text.UTF8Encoding]::new()
$wt = (Resolve-Path "$PSScriptRoot\..\..\..").Path
Set-Location $wt
$py = 'C:\Users\Alvaro\Desktop\Facultad\4to\IA\venv-gpu\Scripts\python.exe'
$out = 'docs\relevo\2026-11-08-claude-tarea11\final-windows'

# Tarea 12: la prueba final ya se ejecuto una vez (final-windows\) y no se repite; nunca se sobrescribe un destino.
if (Test-Path $out) {
  Write-Host "$out ya existe: la prueba final no se vuelve a ejecutar ni se sobrescribe." -ForegroundColor Red
  exit 1
}
if (-not (Test-Path 'data\annotations\youtube-bus-real-cruces.json')) {
  Write-Host 'Falta data\annotations\youtube-bus-real-cruces.json: anota los cruces antes de ejecutar.' -ForegroundColor Red
  exit 1
}
& $py -c "import torch; assert torch.cuda.is_available(), 'sin CUDA'; print(torch.__version__, torch.cuda.get_device_name(0))"
if ($LASTEXITCODE -ne 0) { exit 1 }
if (-not (Test-Path 'yolo11l.pt')) {  # descarga oficial de Ultralytics; el script verifica el SHA-256 despues
  & $py -c "from ultralytics import YOLO; YOLO('yolo11l.pt')"
}

New-Item -ItemType Directory -Force $out | Out-Null
& $py docs\relevo\2026-11-08-claude-tarea11\evaluar_detectores.py $out --dispositivo cuda:0 `
  --escenas final --modelos yolo11n yolo11l --rastreadores calibrado 2>&1 | Tee-Object -FilePath "$out\salida.txt"
if ($LASTEXITCODE -ne 0) { Write-Host 'Fallo la evaluacion; ver salida.txt' -ForegroundColor Red; exit 1 }
Write-Host "`nListo. Resultados en $out (resumen-final-yolo11n-yolo11l.json)." -ForegroundColor Green
