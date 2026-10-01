[CmdletBinding(PositionalBinding=$false)]
param(
    [Parameter(Mandatory)][ValidateSet('python','kicad','freecad','blender')][string]$Runtime,
    [Parameter(Mandatory)][string]$Script,
    [string]$KiCadRoot = $env:CARBENTRA_KICAD_ROOT,
    [string]$FreeCADRoot = $env:CARBENTRA_FREECAD_ROOT,
    [string]$TemporaryDirectory = 'D:\Temp\codex\carbentra-localize-20261001\plug',
    [Parameter(ValueFromRemainingArguments)][string[]]$ScriptArguments
)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
if (-not $KiCadRoot) { $KiCadRoot = 'D:\Dev\KiCad\10.0' }
if (-not $FreeCADRoot) { $FreeCADRoot = 'D:\Dev\FreeCAD-1.1.4' }
$scriptPath = if ([IO.Path]::IsPathRooted($Script)) { $Script } else { Join-Path $projectRoot $Script }
if (-not (Test-Path -LiteralPath $scriptPath -PathType Leaf)) { throw "Missing script: $scriptPath" }
New-Item -ItemType Directory -Path $TemporaryDirectory -Force | Out-Null
$names=@('TEMP','TMP','PYTHONUTF8','PYTHONPATH','PATH','CARBENTRA_KICAD_SHARE','CARBENTRA_KICAD_PYTHON','CARBENTRA_FREECAD_LIB','CARBENTRA_NATIVE_DLL_DIRS','CARBENTRA_NATIVE_PYTHONPATH','KICAD_CONFIG_HOME','XDG_CONFIG_HOME','CARBENTRA_USE_GPU','KICAD10_FOOTPRINT_DIR','KICAD10_SYMBOL_DIR')
$previous=@{}; foreach ($name in $names) { $previous[$name]=[Environment]::GetEnvironmentVariable($name,'Process') }
try {
$env:TEMP=$TemporaryDirectory; $env:TMP=$TemporaryDirectory; $env:PYTHONUTF8='1'
$env:CARBENTRA_KICAD_SHARE=Join-Path $KiCadRoot 'share\kicad'
$env:CARBENTRA_KICAD_PYTHON=Join-Path $KiCadRoot 'bin\python.exe'
$env:CARBENTRA_FREECAD_LIB=Join-Path $FreeCADRoot 'bin'
$env:PYTHONPATH=$PSScriptRoot
$env:PATH=(Join-Path $KiCadRoot 'bin') + ';' + $env:PATH
$env:CARBENTRA_NATIVE_DLL_DIRS=(Join-Path $KiCadRoot 'bin')
$env:CARBENTRA_NATIVE_PYTHONPATH=(Join-Path $KiCadRoot 'bin\Lib\site-packages')
$env:KICAD_CONFIG_HOME=Join-Path $TemporaryDirectory 'kicad-config'
$env:XDG_CONFIG_HOME=Join-Path $TemporaryDirectory 'xdg-config'
$env:KICAD10_FOOTPRINT_DIR=Join-Path $env:CARBENTRA_KICAD_SHARE 'footprints'
$env:KICAD10_SYMBOL_DIR=Join-Path $env:CARBENTRA_KICAD_SHARE 'symbols'
$configDirectory=Join-Path $env:KICAD_CONFIG_HOME '10.0'
New-Item -ItemType Directory -Path $configDirectory -Force | Out-Null
foreach ($table in @('fp-lib-table','sym-lib-table')) {
    Copy-Item -LiteralPath (Join-Path $env:CARBENTRA_KICAD_SHARE "template\$table") -Destination (Join-Path $configDirectory $table) -Force
}
switch ($Runtime) {
    'python' { $executable=Join-Path $projectRoot '.venv\Scripts\python.exe' }
    'kicad' { $executable=Join-Path $KiCadRoot 'bin\python.exe' }
    'freecad' {
        $executable=Join-Path $FreeCADRoot 'bin\python.exe'
        $env:CARBENTRA_NATIVE_DLL_DIRS += ';' + (Join-Path $FreeCADRoot 'bin')
    }
    'blender' {
        $executable=(Get-Command blender.exe -ErrorAction Stop).Source
        $env:CARBENTRA_USE_GPU='1'
        & $executable --background --python $scriptPath -- @ScriptArguments
        if ($LASTEXITCODE -ne 0) { throw "Blender failed with exit code $LASTEXITCODE" }
        return
    }
}
if (-not (Test-Path -LiteralPath $executable)) { throw "Missing $Runtime interpreter: $executable" }
& $executable (Join-Path $PSScriptRoot 'run_engineering.py') $scriptPath @ScriptArguments
if ($LASTEXITCODE -ne 0) { throw "$Runtime script failed with exit code $LASTEXITCODE" }
} finally {
    foreach ($name in $names) { [Environment]::SetEnvironmentVariable($name,$previous[$name],'Process') }
}
