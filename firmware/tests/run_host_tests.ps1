[CmdletBinding()]
param(
    [string]$OutputDirectory = 'D:\Temp\codex\carbentra-localize-20261001\plug\host',
    [switch]$AddressSanitizer
)
$ErrorActionPreference = 'Stop'
$firmwareRoot = Split-Path $PSScriptRoot -Parent
$OutputDirectory = [IO.Path]::GetFullPath($OutputDirectory)
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
if (-not (Get-Command cl.exe -ErrorAction SilentlyContinue)) {
    $vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
    $vsRoot = & $vswhere -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
    if (-not $vsRoot) { throw 'MSVC C compiler is required for Windows host tests.' }
    & (Join-Path $vsRoot 'Common7\Tools\Launch-VsDevShell.ps1') -Arch amd64 -HostArch amd64 -SkipAutomaticLocation
}
$cases = [ordered]@{
    test_policy = @('core/carbentra_policy.c', 'tests/test_policy.c')
    test_protocol = @('core/carbentra_command_json.c', 'core/carbentra_json.c', 'core/carbentra_meter_decode.c', 'third_party/cJSON/cJSON.c', 'tests/test_protocol.c')
    test_feedback = @('core/carbentra_feedback.c', 'tests/test_feedback.c')
    test_storage = @('main/carbentra_storage.c', 'tests/test_storage.c')
    test_calibration_execution = @('core/carbentra_calibration.c', 'core/carbentra_meter_decode.c', 'core/carbentra_execution.c', 'tests/test_calibration_execution.c')
    test_startup = @('main/carbentra_storage.c', 'core/carbentra_policy.c', 'core/carbentra_feedback.c', 'core/carbentra_execution.c', 'third_party/cJSON/cJSON.c', 'tests/test_startup.c')
}
$results = @()
foreach ($entry in $cases.GetEnumerator()) {
    $caseDir = Join-Path $OutputDirectory $entry.Key
    New-Item -ItemType Directory -Path $caseDir -Force | Out-Null
    $exe = Join-Path $caseDir ($entry.Key + '.exe')
    $flags = @('/nologo', '/TC', '/std:c11', '/W3', '/D_CRT_SECURE_NO_WARNINGS', '/Od', '/Zi', "/Fo$caseDir\", "/Fd$caseDir\", "/Fe$exe")
    if ($AddressSanitizer) { $flags += '/fsanitize=address' }
    $flags += @('core','main','tests/mocks','third_party/cJSON') | ForEach-Object { '/I' + (Join-Path $firmwareRoot $_) }
    $sources = $entry.Value | ForEach-Object { Join-Path $firmwareRoot $_ }
    & cl.exe @flags @sources
    if ($LASTEXITCODE -ne 0) { throw "Compilation failed: $($entry.Key)" }
    if ($AddressSanitizer) {
        # Integration fixtures run outside the VS development shell as well.
        $asanRuntime=Join-Path (Split-Path (Get-Command cl.exe).Source -Parent) 'clang_rt.asan_dynamic-x86_64.dll'
        if (-not (Test-Path -LiteralPath $asanRuntime)) { throw 'MSVC AddressSanitizer runtime is missing' }
        Copy-Item -LiteralPath $asanRuntime -Destination $caseDir -Force
    }
    $scenarios = if ($entry.Key -eq 'test_startup') { 0..6 } else { @('') }
    foreach ($scenario in $scenarios) {
        if ($scenario -ceq '') { & $exe } else { & $exe $scenario }
        if ($LASTEXITCODE -ne 0) { throw "Host regression failed: $($entry.Key) $scenario" }
    }
    $results += [ordered]@{ test=$entry.Key; scenarios=@($scenarios).Count; passed=$true; executable=$exe; sha256=(Get-FileHash $exe -Algorithm SHA256).Hash.ToLowerInvariant() }
}
$record = [ordered]@{ schema_version=1; platform='Windows MSVC x64'; address_sanitizer=[bool]$AddressSanitizer; undefined_behavior_sanitizer=$false; physical_hardware=$false; passed=$true; tests=$results }
$record | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $OutputDirectory 'host-validation.json') -Encoding utf8
