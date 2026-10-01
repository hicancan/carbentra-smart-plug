[CmdletBinding()]
param(
    [string]$IdfRoot='D:\Dev\esp-idf-v5.4.3',
    [string]$IdfToolsRoot='D:\Dev\esp-tools-v5.4.3',
    [string]$OutputDirectory='D:\Temp\codex\carbentra-localize-20261001\plug\idf-build'
)
$ErrorActionPreference='Stop'
$repoRoot=Split-Path $PSScriptRoot -Parent
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
$env:TEMP=$OutputDirectory; $env:TMP=$OutputDirectory
$env:IDF_PATH=$IdfRoot; $env:IDF_TOOLS_PATH=$IdfToolsRoot
$env:IDF_PYTHON_ENV_PATH=Join-Path $IdfToolsRoot 'python_env\idf5.4_py3.12_env'
$env:PATH="$env:IDF_PYTHON_ENV_PATH\Scripts;$env:PATH"
. (Join-Path $IdfRoot 'export.ps1')
if ($LASTEXITCODE -ne 0) { throw 'ESP-IDF environment validation failed' }
$commit=& git -C $IdfRoot rev-parse HEAD
if ($commit -ne 'ea1c174c1cbb7348bd8ba0ff1eb306246938dd80') { throw 'Expected reviewed ESP-IDF 5.4.3 commit' }
Push-Location (Join-Path $repoRoot 'firmware')
try {
    & "$env:IDF_PYTHON_ENV_PATH\Scripts\python.exe" "$IdfRoot\tools\idf.py" -B $OutputDirectory build
    if ($LASTEXITCODE -ne 0) { throw 'ESP32-C3 build failed' }
    $config=Get-Content -LiteralPath sdkconfig -Raw
    if ($config -notmatch '(?m)^# CONFIG_CARBENTRA_ALLOW_ACTUATION is not set$' -or $config -notmatch '(?m)^CONFIG_MBEDTLS_HAVE_TIME_DATE=y$') { throw 'Development safety configuration changed' }
} finally { Pop-Location }
