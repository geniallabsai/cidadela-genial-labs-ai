# Genial Labs - instalador nativo para WINDOWS (PowerShell 5.1+, Win10/Win11)
# Uso:   irm https://raw.githubusercontent.com/geniallabsai/genial-labs/main/install.ps1 | iex
# Ou:    iwr ... -OutFile $env:TEMP\ig.ps1; powershell -ExecutionPolicy Bypass -File $env:TEMP\ig.ps1
# Flag:  -Repo  instala a skill tambem nas pastas do repositorio atual (time inteiro)
param([switch]$Repo)

$ErrorActionPreference = "Stop"
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

$RepoUrl = "https://github.com/geniallabsai/genial-labs.git"
$ZipUrl  = "https://codeload.github.com/geniallabsai/genial-labs/zip/refs/heads/main"
$PkgDir  = Join-Path $env:USERPROFILE ".genial-labs"
$BinDir  = Join-Path $env:LOCALAPPDATA "GenialLabs\bin"

function Write-Banner {
    $art = @(
'██████╗   ██████╗  ███╗   ███╗  ███╗  █████╗  ██╗      ██████╗  ██████╗  ██████╗  ███████╗',
'██╔══██╗ ██╔═══██╗ ██╔██╗ ██╔╝  ████╗ ██╔══██╗██║     ██╔═══██╗██╔═══██╗██╔═══██╗ ██╔════╝',
'██████╔╝ ██║   ██║ ███████║    ██╔██╗ ███████║██║     ██║   ██║██║   ██║██║   ██║ ███████╗',
'██╔══██╗ ██║   ██║ ██╔══██║    ██║╚██╗ ██╔══██║██║     ██║   ██║██║   ██║██║   ██║ ██╔══╝  ',
'██║  ██║ ╚██████╔╝ ██║  ██║    ██║ ╚████╗██║  ██║██║   ╚██████╔╝╚██████╔╝╚██████╔╝ ███████╗',
'╚═╝  ╚═╝  ╚═════╝  ╚═╝  ╚═╝    ╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝   ╚═════╝  ╚═════╝  ╚═════╝  ╚══════╝')
    foreach ($l in $art) { Write-Host $l -ForegroundColor Cyan }
    Write-Host "    Genial Labs · arquitetura + dados + segurança + infra que guia seu código" -ForegroundColor DarkCyan
    Write-Host "    instalador v1.0 (Windows · PowerShell nativo)" -ForegroundColor DarkGray
    Write-Host ""
}

function Find-Python {
    foreach ($c in @("py","python","python3")) {
        $cmd = Get-Command $c -ErrorAction SilentlyContinue
        if ($cmd) {
            if ($c -eq "py") { return @{ exe = "py"; args = @("-3") } }
            else             { return @{ exe = $c;  args = @() } }
        }
    }
    return $null
}

Write-Banner

$PyInfo = Find-Python
if (-not $PyInfo) {
    Write-Host "AVISO: Python nao encontrado no PATH. O comando 'genial' precisa dele (3.7+, sem dependencias)." -ForegroundColor Yellow
    Write-Host "       Instale em https://www.python.org/downloads/ (marque 'Add to PATH') e reabra o terminal." -ForegroundColor Yellow
    Write-Host "       A skill cidadela continua funcionando normalmente no Codex/Claude Code." -ForegroundColor Yellow
}

$tmp = Join-Path $env:TEMP ("gl-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $tmp | Out-Null
$done = $false
try {
    Write-Host "[1/4] baixando o pacote..." -ForegroundColor White
    $git = Get-Command git -ErrorAction SilentlyContinue
    if ($git) {
        & git -c core.autocrlf=false -c core.eol=lf clone --depth 1 $RepoUrl (Join-Path $tmp "pacote") 2>$null
        if ($LASTEXITCODE -ne 0) { throw "falha no git clone." }
    } else {
        $zip = Join-Path $tmp "p.zip"
        Invoke-WebRequest -Uri $ZipUrl -OutFile $zip -UseBasicParsing
        $x = Join-Path $tmp "x"
        Expand-Archive -LiteralPath $zip -DestinationPath $x
        Get-ChildItem $x -Directory | Select-Object -First 1 | Move-Item -Destination (Join-Path $tmp "pacote")
    }
    if (-not (Test-Path (Join-Path $tmp "pacote\genial"))) { throw "pacote incompleto apos o download." }

    Write-Host "[2/4] instalando em ~\.genial-labs ..." -ForegroundColor White
    if (Test-Path $PkgDir) { Remove-Item -Recurse -Force $PkgDir }
    Copy-Item -Recurse (Join-Path $tmp "pacote") $PkgDir

    Write-Host "[3/4] instalando a skill cidadela (Codex + Claude Code)..." -ForegroundColor White
    $bases = @((Join-Path $env:USERPROFILE ".agents\skills"), (Join-Path $env:USERPROFILE ".claude\skills"))
    foreach ($base in $bases) {
        New-Item -ItemType Directory -Path $base -Force | Out-Null
        $dest = Join-Path $base "cidadela"
        if (Test-Path $dest) { Remove-Item -Recurse -Force $dest }
        Copy-Item -Recurse (Join-Path $PkgDir "skills\cidadela") $dest
    }
    if ($Repo) {
        foreach ($rel in @(".agents\skills",".claude\skills")) {
            $base = Join-Path (Get-Location) $rel
            New-Item -ItemType Directory -Path $base -Force | Out-Null
            $dest = Join-Path $base "cidadela"
            if (Test-Path $dest) { Remove-Item -Recurse -Force $dest }
            Copy-Item -Recurse (Join-Path $PkgDir "skills\cidadela") $dest
        }
        Write-Host "  + skill instalada tambem neste repositorio (.agents/skills e .claude/skills)." -ForegroundColor DarkGray
    }

    Write-Host "[4/4] instalando o comando 'genial' (wrapper no PATH do usuario)..." -ForegroundColor White
    New-Item -ItemType Directory -Path $BinDir -Force | Out-Null
    $prog = Join-Path $PkgDir "genial"
    $shimBody = @"
@echo off
rem Genial Labs - wrapper gerado pelo instalador (Windows)
setlocal
set "PYCMD="
where py >nul 2>nul && set "PYCMD=py -3"
if not defined PYCMD where python >nul 2>nul && set "PYCMD=python"
if not defined PYCMD where python3 >nul 2>nul && set "PYCMD=python3"
if not defined PYCMD ( echo Genial Labs: Python nao encontrado no PATH. Instale em python.org e reabra o terminal. & exit /b 127 )
%PYCMD% "$prog" %*
"@
    Set-Content -Path (Join-Path $BinDir "genial.cmd") -Value $shimBody -Encoding ASCII
    $userPath = [Environment]::GetEnvironmentVariable("Path","User")
    if ($userPath -notlike "*$BinDir*") {
        $newPath = $userPath
        if ($newPath -and -not $newPath.EndsWith(";")) { $newPath = $newPath + ";" }
        [Environment]::SetEnvironmentVariable("Path", ($newPath + $BinDir), "User")
        Write-Host "  + $BinDir adicionado ao PATH do usuario." -ForegroundColor DarkGray
    }
    $env:Path = "$env:Path;$BinDir"

    # ----- verificacao -----
    $ok = $true
    if ($PyInfo) {
        $argsVerify = @($PyInfo.args) + @($prog, "banner")
        & $PyInfo.exe $argsVerify | Out-Null
        if ($LASTEXITCODE -ne 0) { $ok = $false }
    }
    $shim = Join-Path $BinDir "genial.cmd"
    & cmd.exe /c "call `"$shim`" banner" | Out-Null
    if ($LASTEXITCODE -ne 0) { $ok = $false }
    if (-not $ok) { throw "verificacao do comando 'genial' falhou." }
    $selftest = Join-Path $tmp "selftest"
    & cmd.exe /c "call `"$shim`" init `"$selftest`" --stack py" | Out-Null
    if (-not (Test-Path (Join-Path $selftest "ARCHITETURA-DADOS.md"))) { throw "self-test 'genial init' incompleto." }

    $done = $true
    Write-Host ""
    Write-Host "✓ Genial Labs instalado." -ForegroundColor Green
    Write-Host ""
    Write-Host "  O que você ganhou:" -ForegroundColor Green
    Write-Host "   • skill 'cidadela' no Codex e no Claude Code (8 fases)"
    Write-Host "   • comando 'genial': init · doctor · deploy · skills"
    Write-Host "   • templates de Arquitetura de Dados + Docker/Compose/K8s + gates de CI"
    Write-Host ""
    Write-Host "  IMPORTANTE: abra um NOVO terminal para o PATH valer, e então:" -ForegroundColor DarkCyan
    Write-Host "   genial init meu-projeto --stack py     novo projeto guiado"
    Write-Host "   genial doctor                          auditar projeto existente"
    Write-Host "   genial deploy                          degrau na escada VPS->Docker->K8s->AWS"
    Write-Host ""
    Write-Host "  No Codex: /skills -> cidadela — ou escreva: `cidadela: audite este repositório`." -ForegroundColor DarkGray
    Write-Host ""
} finally {
    Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
}
if (-not $done) { exit 1 }
