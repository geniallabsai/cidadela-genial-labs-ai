# Genial Labs - desinstalador (Windows nativo; funciona tambem em PowerShell no Linux/macOS)
# Uso: iwr https://raw.githubusercontent.com/geniallabsai/genial-labs/main/uninstall.ps1 -OutFile $env:TEMP\u.ps1
#      powershell -ExecutionPolicy Bypass -File $env:TEMP\u.ps1 [-y]
param([switch]$y)
$IsWinOS = ($env:OS -eq "Windows_NT")
if (-not $env:USERPROFILE)  { $env:USERPROFILE  = $env:HOME }
if (-not $env:LOCALAPPDATA) { $env:LOCALAPPDATA = [System.IO.Path]::Combine($env:HOME, ".local", "share") }
$targets = @(
  (Join-Path $env:USERPROFILE ".genial-labs"),
  ([System.IO.Path]::Combine($env:LOCALAPPDATA, "GenialLabs")),
  ([System.IO.Path]::Combine($env:USERPROFILE, ".agents", "skills", "cidadela")),
  ([System.IO.Path]::Combine($env:USERPROFILE, ".claude", "skills", "cidadela"))
)
$existem = @($targets | Where-Object { Test-Path $_ })
if ($existem.Count -eq 0) { Write-Host "Nada instalado (ou ja removido)."; return }
foreach ($t in $existem) { Write-Host "Remover: $t" }
if (-not $y) {
    $r = Read-Host "Confirmar? [s/N]"
    if ($r -notin @("s","sim","y","yes")) { Write-Host "Cancelado."; return }
}
foreach ($t in $existem) { Remove-Item -Recurse -Force $t; Write-Host "  removido: $t" }
if ($IsWinOS) {
    $p = [Environment]::GetEnvironmentVariable("Path","User")
    if ($p -and $p -like "*GenialLabs*") {
        $parts = @($p -split ';' | Where-Object { $_ -and ($_ -notlike "*GenialLabs*") })
        [Environment]::SetEnvironmentVariable("Path", ($parts -join ';'), "User")
        Write-Host "  PATH (usuario) limpo."
    }
}
Write-Host "Genial Labs removido." -ForegroundColor Green
