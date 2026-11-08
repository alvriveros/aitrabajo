# Tarea 08 - verificacion en Windows. Ejecutar desde cualquier carpeta:
#   powershell -ExecutionPolicy Bypass -File C:\Users\Alvaro\Desktop\Facultad\4to\IA\TpFinal\.worktrees\integracion-video\docs\relevo\2026-11-07-claude-tarea08\verificar-windows.ps1
# Repara el vinculo del worktree, registra entorno y hashes, ejecuta las pruebas y los dos verificadores
# del panel en puertos libres, y guarda todo en docs\relevo\2026-11-07-claude-tarea08\windows\.
# Usa la .venv existente del worktree (solo agrega playwright si falta). No usa prune, reset ni borra nada.
# Solo detiene la API y el panel que este script inicia.

$ErrorActionPreference = 'Continue'
$env:PYTHONUTF8 = '1'
[Console]::OutputEncoding = [Text.UTF8Encoding]::new()  # salida de Python en UTF-8
$wt = (Resolve-Path "$PSScriptRoot\..\..\..").Path
$principal = (Resolve-Path "$wt\..\..").Path
$t08 = "$wt\docs\relevo\2026-11-07-claude-tarea08"
$out = "$t08\windows"
New-Item -ItemType Directory -Force $out | Out-Null
$py = "$wt\.venv\Scripts\python.exe"
function Paso($nombre) { Write-Host "`n== $nombre" -ForegroundColor Cyan }
function Guardar($archivo) { $input | Out-File -Encoding utf8 -FilePath $archivo }
Set-Location $wt

Paso '1. Reparar el worktree'
& {
  "principal: $principal"; "worktree: $wt"
  "--- antes"; Get-Content "$wt\.git"; Get-Content "$principal\.git\worktrees\integracion-video\gitdir"
  git -C $principal worktree repair $wt 2>&1
  "--- despues"; Get-Content "$wt\.git"; Get-Content "$principal\.git\worktrees\integracion-video\gitdir"
  "--- comprobacion"
  git -C $principal worktree list
  git -C $wt rev-parse --abbrev-ref HEAD
  git -C $wt log --oneline -4
  git -C $wt status --short
  git -C $principal cat-file -t b511d91
  git -C $principal status --short
} 2>&1 | Guardar "$out\01-worktree.txt"
Get-Content "$out\01-worktree.txt"
Copy-Item "$principal\docs\tareas\claude\08-cierre-integracion-windows.md" "$wt\docs\tareas\claude\" -Force

Paso '2. Entorno, versiones y hashes'
& {
  Get-Date -Format o
  (Get-CimInstance Win32_OperatingSystem).Caption + ' ' + (Get-CimInstance Win32_OperatingSystem).Version
  (Get-CimInstance Win32_Processor).Name
  'RAM GB: ' + [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 1)
  & $py --version
  & $py -m pip list 2>$null | Select-String -Pattern '^(ultralytics|torch|torchvision|opencv-python|lap|fastapi|uvicorn|streamlit|vl-convert-python|pytest|httpx|playwright) '
  foreach ($f in 'data\raw\oficina.mp4', 'yolo11n.pt') {
    $i = Get-Item "$wt\$f"; $h = (Get-FileHash $i.FullName -Algorithm SHA256).Hash
    "$f  $($i.Length) bytes  SHA256 $h"
  }
} 2>&1 | Guardar "$out\02-entorno.txt"
Get-Content "$out\02-entorno.txt"

Paso '3. Pruebas: API por un lado, vision por otro'
& $py -m pytest tests\test_ocupacion.py tests\test_procesamientos.py -v 2>&1 | Guardar "$out\03-pytest-api.txt"
"codigo de salida: $LASTEXITCODE" | Add-Content "$out\03-pytest-api.txt"
& $py -m pytest tests -v --ignore=tests\test_ocupacion.py --ignore=tests\test_procesamientos.py 2>&1 | Guardar "$out\04-pytest-vision.txt"
"codigo de salida: $LASTEXITCODE" | Add-Content "$out\04-pytest-vision.txt"
Get-Content "$out\03-pytest-api.txt" -Tail 3; Get-Content "$out\04-pytest-vision.txt" -Tail 6

Paso '4. Servicios activos y puertos'
$escucha = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue
& {
  foreach ($c in $escucha | Where-Object { $_.LocalPort -in 8000, 8001, 8010, 8501, 8502, 8511 }) {
    $proc = Get-CimInstance Win32_Process -Filter "ProcessId = $($c.OwningProcess)"
    "puerto $($c.LocalPort): PID $($c.OwningProcess) $($proc.CommandLine)"
  }
} 2>&1 | Guardar "$out\05-servicios.txt"
$puertoApi = (8010..8099 | Where-Object { $_ -notin $escucha.LocalPort } | Select-Object -First 1)
$puertoPanel = (8511..8599 | Where-Object { $_ -notin $escucha.LocalPort } | Select-Object -First 1)
"usados por esta verificacion: API $puertoApi, panel $puertoPanel" | Add-Content "$out\05-servicios.txt"
Get-Content "$out\05-servicios.txt"

Paso '5. Playwright (solo si falta)'
& $py -c "import playwright" 2>$null
if ($LASTEXITCODE -ne 0) {
  & { & $py -m pip install playwright; & $py -m playwright install chromium } 2>&1 | Guardar "$out\06-playwright.txt"
}

Paso '6. API y panel del worktree'
$api = Start-Process $py -ArgumentList '-m', 'uvicorn', 'api.main:app', '--port', $puertoApi -WorkingDirectory $wt -PassThru -WindowStyle Hidden -RedirectStandardOutput "$out\api-stdout.txt" -RedirectStandardError "$out\api-stderr.txt"
$env:API_URL = "http://127.0.0.1:$puertoApi"
$panel = Start-Process $py -ArgumentList '-m', 'streamlit', 'run', 'ui/app.py', '--server.port', $puertoPanel, '--server.headless', 'true', '--browser.gatherUsageStats', 'false' -WorkingDirectory $wt -PassThru -WindowStyle Hidden -RedirectStandardOutput "$out\panel-stdout.txt" -RedirectStandardError "$out\panel-stderr.txt"
foreach ($u in "http://127.0.0.1:$puertoApi/openapi.json", "http://127.0.0.1:$puertoPanel") {
  for ($i = 0; $i -lt 60; $i++) { try { Invoke-WebRequest $u -UseBasicParsing -TimeoutSec 2 | Out-Null; break } catch { Start-Sleep 1 } }
}
$env:PANEL_URL = "http://127.0.0.1:$puertoPanel"
try {
  Paso '7. Procesar el clip desde el panel y aceptar el resultado'
  $s = Get-Date
  & $py "$t08\scripts\verificar_video.py" "$out\video" 2>&1 | Guardar "$out\07-verificar-video.txt"
  "codigo de salida: $LASTEXITCODE  segundos: $([math]::Round(((Get-Date) - $s).TotalSeconds, 1))" | Add-Content "$out\07-verificar-video.txt"
  Get-Content "$out\07-verificar-video.txt" -Tail 4

  Paso '8. Grafico: 45 estados con carga de JSON'
  $t05 = "$wt\docs\relevo\2026-11-06-claude-tarea05"
  & $py "$t08\scripts\verificar_grafico.py" "$t05\casos\oficina-00-06-prediccion.json" "$t05\casos" "$out\grafico" 2>&1 | Guardar "$out\08-verificar-grafico.txt"
  "codigo de salida: $LASTEXITCODE" | Add-Content "$out\08-verificar-grafico.txt"
  Get-Content "$out\08-verificar-grafico.txt" -Tail 2
}
finally {
  Stop-Process -Id $api.Id, $panel.Id -ErrorAction SilentlyContinue
}
Paso "Listo. Resultados en $out"
