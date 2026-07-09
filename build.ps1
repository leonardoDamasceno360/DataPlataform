param(
    [string]$Version = "1.0.0",
    [switch]$BuildInstaller
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonExe = Join-Path $ProjectRoot "runtime\.venv\Scripts\python.exe"
$PyInstallerExe = Join-Path $ProjectRoot "runtime\.venv\Scripts\pyinstaller.exe"
$SpecFile = Join-Path $ProjectRoot "packaging\pyinstaller\DataPlatform.spec"
$DistDir = Join-Path $ProjectRoot "dist"
$BuildDir = Join-Path $ProjectRoot "build"
$ExePath = Join-Path $DistDir "DataPlatform.exe"
$DeliveryDir = "C:\Users\LeonardoDamasceno\OneDrive - Dicon Contabilidade\RH - Compliance\8. Automações - Executáveis\DataPlatform"
$DeliveryExePath = Join-Path $DeliveryDir "DataPlatform.exe"
$InstallerScript = Join-Path $ProjectRoot "packaging\installer\DataPlatform.iss"
$InnoCompiler = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"

if (-not (Test-Path $PythonExe)) {
    throw "Python do ambiente virtual nao encontrado em $PythonExe"
}

if (-not (Test-Path $PyInstallerExe)) {
    & $PythonExe -m pip install pyinstaller
}

Get-Process DataPlatform -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Milliseconds 500

Write-Host "Limpando artefatos anteriores..."
if (Test-Path $DistDir) {
    Remove-Item $DistDir -Recurse -Force
}
if (Test-Path $BuildDir) {
    Remove-Item $BuildDir -Recurse -Force
}

Write-Host "Gerando build com PyInstaller..."
& $PythonExe -m PyInstaller `
    --noconfirm `
    --clean `
    $SpecFile

if ($LASTEXITCODE -ne 0) {
    throw "Falha no build do PyInstaller."
}

if (-not (Test-Path $ExePath)) {
    throw "Executavel nao encontrado apos o build: $ExePath"
}

if (-not (Test-Path $DeliveryDir)) {
    New-Item -ItemType Directory -Path $DeliveryDir -Force | Out-Null
}

Copy-Item -Path $ExePath -Destination $DeliveryExePath -Force

if ($BuildInstaller) {
    if (-not (Test-Path $InnoCompiler)) {
        throw "ISCC.exe nao encontrado. Instale o Inno Setup 6."
    }

    Write-Host "Gerando instalador..."
    & $InnoCompiler `
        "/DAppVersion=$Version" `
        "/DProjectRoot=$ProjectRoot" `
        $InstallerScript

    if ($LASTEXITCODE -ne 0) {
        throw "Falha na geracao do instalador."
    }
}

Write-Host ""
Write-Host "Build concluido."
Write-Host "Executavel: $ExePath"
Write-Host "Copia atualizada em: $DeliveryExePath"

if ($BuildInstaller) {
    Write-Host "Instalador: $DistDir\installer\DataPlatform-Setup-$Version.exe"
}
