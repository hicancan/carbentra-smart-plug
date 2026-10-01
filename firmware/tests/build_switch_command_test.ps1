[CmdletBinding()]
param(
    [string]$PlatformRoot = $env:CARBENTRA_PLATFORM_ROOT,
    [string]$SwitchRoot = $env:CARBENTRA_SWITCH_ROOT,
    [string]$IdfRoot = 'D:\Dev\esp-idf-v5.4.3',
    [string]$OutputDirectory = (Join-Path 'D:\Temp\codex' ('carbentra-switch-command-' + [guid]::NewGuid().ToString('N')))
)
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$suiteRoot = Split-Path $repoRoot -Parent
if (-not $PlatformRoot) { $PlatformRoot = Join-Path $suiteRoot 'carbentra-campus-platform' }
if (-not $SwitchRoot) { $SwitchRoot = Join-Path $suiteRoot 'carbentra-smart-switch' }
$PlatformRoot = (Resolve-Path -LiteralPath $PlatformRoot).Path
$SwitchRoot = (Resolve-Path -LiteralPath $SwitchRoot).Path
$IdfRoot = (Resolve-Path -LiteralPath $IdfRoot).Path
$OutputDirectory = [IO.Path]::GetFullPath($OutputDirectory)
$temporaryRoot = [IO.Path]::GetFullPath('D:\Temp\codex') + [IO.Path]::DirectorySeparatorChar
if (-not $OutputDirectory.StartsWith($temporaryRoot, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Use a task-specific OutputDirectory below D:\Temp\codex for the compiled integration gate.'
}
$sdkCommit = & git -C $IdfRoot rev-parse HEAD
if ($LASTEXITCODE -ne 0 -or $sdkCommit -ne 'ea1c174c1cbb7348bd8ba0ff1eb306246938dd80') {
    throw 'The Switch integration gate requires the reviewed ESP-IDF 5.4.3 source checkout.'
}
$cjsonRoot = Join-Path $IdfRoot 'components\json\cJSON'
$inputs = [ordered]@{
    'platform/edge/tests/c/switch_command_decoder.c' = Join-Path $PlatformRoot 'edge\tests\c\switch_command_decoder.c'
    'switch/firmware/core/switch_core.c' = Join-Path $SwitchRoot 'firmware\core\switch_core.c'
    'switch/firmware/core/switch_core.h' = Join-Path $SwitchRoot 'firmware\core\switch_core.h'
    'switch/firmware/main/command_json.c' = Join-Path $SwitchRoot 'firmware\main\command_json.c'
    'switch/firmware/main/command_json.h' = Join-Path $SwitchRoot 'firmware\main\command_json.h'
    'esp-idf/components/json/cJSON/cJSON.c' = Join-Path $cjsonRoot 'cJSON.c'
    'esp-idf/components/json/cJSON/cJSON.h' = Join-Path $cjsonRoot 'cJSON.h'
}
function Get-InputHashes {
    $hashes = [ordered]@{}
    foreach ($entry in $inputs.GetEnumerator()) {
        $hashes[$entry.Key] = (Get-FileHash -LiteralPath $entry.Value -Algorithm SHA256).Hash.ToLowerInvariant()
    }
    return $hashes
}
$before = Get-InputHashes
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
$oldTemp, $oldTmp = $env:TEMP, $env:TMP
try {
    $env:TEMP = $OutputDirectory; $env:TMP = $OutputDirectory
    if (-not (Get-Command cl.exe -ErrorAction SilentlyContinue)) {
        $vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
        $vsRoot = & $vswhere -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
        if (-not $vsRoot) { throw 'MSVC C compiler is required for the Switch integration gate.' }
        & (Join-Path $vsRoot 'Common7\Tools\Launch-VsDevShell.ps1') -Arch amd64 -HostArch amd64 -SkipAutomaticLocation
    }
    $exe = Join-Path $OutputDirectory 'switch_command_decoder.exe'
    $flags = @('/nologo', '/TC', '/std:c11', '/W3', '/D_CRT_SECURE_NO_WARNINGS', '/Od', '/Zi', '/fsanitize=address',
        "/Fo$OutputDirectory\", "/Fd$OutputDirectory\", "/Fe$exe",
        "/I$SwitchRoot\firmware\core", "/I$SwitchRoot\firmware\main", "/I$cjsonRoot")
    $sources = @($inputs.GetEnumerator() | Where-Object { $_.Key.EndsWith('.c') } | ForEach-Object Value)
    & cl.exe @flags @sources
    if ($LASTEXITCODE -ne 0) { throw 'Compilation of the real Switch command decoder failed.' }
    $asanRuntime = Join-Path (Split-Path (Get-Command cl.exe).Source -Parent) 'clang_rt.asan_dynamic-x86_64.dll'
    if (-not (Test-Path -LiteralPath $asanRuntime -PathType Leaf)) { throw 'MSVC AddressSanitizer runtime is missing.' }
    Copy-Item -LiteralPath $asanRuntime -Destination $OutputDirectory -Force
    $after = Get-InputHashes
    if (($before | ConvertTo-Json -Compress) -ne ($after | ConvertTo-Json -Compress)) {
        throw 'Switch integration sources changed during compilation; rebuild before using the binary.'
    }
    [ordered]@{
        schema_version = 1
        recorded_at_utc = [DateTime]::UtcNow.ToString('o')
        scope = 'Compiled real Switch decoder for shared Edge tests; no network, GPIO or physical actuation'
        platform = 'Windows MSVC x64'
        address_sanitizer = $true
        undefined_behavior_sanitizer = $false
        compiled = $true
        tests = 'Executed by the shared Edge release runner, not by this build step'
        sdk_commit = $sdkCommit
        source_sha256 = $after
        executable = $exe
        executable_sha256 = (Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash.ToLowerInvariant()
        asan_runtime_sha256 = (Get-FileHash -LiteralPath $asanRuntime -Algorithm SHA256).Hash.ToLowerInvariant()
    } | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $OutputDirectory 'build-validation.json') -Encoding utf8
    Write-Host "Built Switch C integration gate: $exe"
} finally {
    $env:TEMP = $oldTemp; $env:TMP = $oldTmp
}
