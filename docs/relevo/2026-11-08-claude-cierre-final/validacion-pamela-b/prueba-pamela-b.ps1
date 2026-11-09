# Validación única con PAMELA B-No y B-Oy (ver prerregistro.md). Ejecutar desde cualquier carpeta:
#   powershell -ExecutionPolicy Bypass -File <worktree>\docs\relevo\2026-11-08-claude-cierre-final\validacion-pamela-b\prueba-pamela-b.ps1
$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
$wt = (Resolve-Path "$PSScriptRoot\..\..\..\..").Path
Set-Location $wt
$py = '.\.venv\Scripts\python.exe'
$out = 'docs\relevo\2026-11-08-claude-cierre-final\validacion-pamela-b\resultado'
if (Test-Path $out) { Write-Host "$out ya existe: la validación no se repite." -ForegroundColor Red; exit 1 }

$videos = @{ 'B-No' = '58d945ab2a876d563dcbdfe07b9cf9697aa842c9999458e061b5d8a3530ec650';
             'B-Oy' = '00151d75110b95fe4d1d8aff61dc5bfadaf10b83b6808acd2251c7d3802d43ea' }
foreach ($v in $videos.Keys) {
  if (-not (Test-Path "data\annotations\pamela-$v-cruces.json")) { Write-Host "Falta la referencia de $v." -ForegroundColor Red; exit 1 }
  if ((Get-FileHash "data\raw\puerta-tren-d800-$v.mp4").Hash.ToLower() -ne $videos[$v]) { Write-Host "Hash distinto en $v." -ForegroundColor Red; exit 1 }
}
if ((Get-FileHash 'yolo11n.pt').Hash.ToLower() -ne '0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1') { Write-Host 'Pesos distintos.' -ForegroundColor Red; exit 1 }

New-Item -ItemType Directory -Force $out | Out-Null
New-Item -ItemType Directory -Force 'runs\evaluacion\pamela-b' | Out-Null
Get-FileHash data\annotations\pamela-B-*-cruces.json | Format-List | Out-File "$out\referencias-sha256.txt"
git rev-parse HEAD | Out-File "$out\commit.txt"
foreach ($v in 'B-No', 'B-Oy') {
  & $py -m vision.pipeline --video "data\raw\puerta-tren-d800-$v.mp4" --recorte 96,64,160,224 --linea 0,96,159,96 `
      --interior arriba --rastreador vision/bytetrack-cenital.yaml --conf 0.05 --confirmacion 2 --dispositivo cpu `
      --pesos yolo11n.pt --salida "$out\$v-prediccion.json" --video-anotado "runs\evaluacion\pamela-b\$v-anotado.mp4"
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  & $py -m evaluation.evaluate --referencia "data\annotations\pamela-$v-cruces.json" --prediccion "$out\$v-prediccion.json" `
      --tolerancia 1 --salida "$out\$v-evaluacion.json"
}
Write-Host "Listo: $out" -ForegroundColor Green
