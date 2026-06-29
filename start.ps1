# V.A.U.L.T. — Claude Code Dashboard launcher
$port = 5000
$url = "http://localhost:$port"

# Kill any previous instance on this port
$old = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
if ($old) {
    Stop-Process -Id ($old | Select-Object -First 1 -ExpandProperty OwningProcess) -Force -ErrorAction SilentlyContinue
    Start-Sleep -Milliseconds 500
}

Write-Host "Iniciando V.A.U.L.T. en $url ..." -ForegroundColor Magenta

# Start Flask in background
$proc = Start-Process python -ArgumentList "$PSScriptRoot\app.py $port" `
    -WorkingDirectory $PSScriptRoot `
    -PassThru -WindowStyle Minimized

# Wait for server
$ready = $false
for ($i = 0; $i -lt 20; $i++) {
    Start-Sleep -Milliseconds 300
    try {
        $null = Invoke-WebRequest $url -UseBasicParsing -TimeoutSec 1 -ErrorAction Stop
        $ready = $true
        break
    } catch {}
}

if ($ready) {
    Write-Host "Listo! Abriendo $url" -ForegroundColor Green
    Start-Process $url
} else {
    Write-Host "El servidor tardó demasiado. Abre $url manualmente." -ForegroundColor Yellow
}

Write-Host "Presiona Ctrl+C para cerrar el servidor." -ForegroundColor DarkGray
Wait-Process -Id $proc.Id
