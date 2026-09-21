# Genial Labs - desinstalador (Windows)
# Uso: iwr https://raw.githubusercontent.com/brunao23/genial-labs/main/uninstall.ps1 -OutFile $env:TEMP\u.ps1; powershell -ExecutionPolicy Bypass -File $env:TEMP\u.ps1 [-y]
param([switch]$y)
$targets = @(
  (Join-Path $env:USERPROFILE ".genial-labs"),
  (Join-Path $env:LOCALAPPDATA "GenialLabs"),
  (Join-Path $env:USERPROFILE ".agents\skills\cidadela"),
  (Join-Path $env:USERPROFILE ".claude\skills\cidadela")
)
$existem = @($targets | Where-Object { Test-Path $_ })
if ($existem.Count -eq 0) { Write-Host "Nada instalado (ou ja removido)."; return }
foreach ($t in $existem) { Write-Host "Remover: $t" }
if (-not $y) {
    $r = Read-Host "Confirmar? [s/N]"
    if ($r -notin @("s","sim","y","yes")) { Write-Host "Cancelado."; return }
}
foreach ($t in $existem) { Remove-Item -Recurse -Force $t; Write-Host "  removido: $t" }
$p = [Environment]::GetEnvironmentVariable("Path","User")
if ($p -and $p -like "*GenialLabs\bin*") {
    $parts = @($p -split ';' | Where-Object { $_ -and ($_ -notlike "*GenialLabs\bin") })
    [Environment]::SetEnvironmentVariable("Path", ($parts -join ';'), "User")
    Write-Host "  PATH (usuario) limpo."
}
Write-Host "Genial Labs removido." -ForegroundColor Green
