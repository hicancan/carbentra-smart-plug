[CmdletBinding()]
param(
    [string]$PlatformRoot=$env:CARBENTRA_PLATFORM_ROOT,
    [string]$SwitchRoot=$env:CARBENTRA_SWITCH_ROOT,
    [string]$IdfRoot='D:\Dev\esp-idf-v5.4.3',
    [string]$SwitchCommandTestBinary=$env:CARBENTRA_SWITCH_COMMAND_TEST_BINARY,
    [string]$OutputDirectory=(Join-Path 'D:\Temp\codex' ('carbentra-plug-check-' + [guid]::NewGuid().ToString('N'))),
    [switch]$BuildTarget,
    [switch]$CheckNativeCAD,
    [switch]$RenderGPU
)
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
if (-not $PlatformRoot) { $PlatformRoot=Join-Path (Split-Path $root -Parent) 'carbentra-campus-platform' }
if (-not $SwitchRoot) { $SwitchRoot=Join-Path (Split-Path $root -Parent) 'carbentra-smart-switch' }
$OutputDirectory=[IO.Path]::GetFullPath($OutputDirectory)
$temporaryRoot=[IO.Path]::GetFullPath('D:\Temp\codex')+[IO.Path]::DirectorySeparatorChar
if (-not $OutputDirectory.StartsWith($temporaryRoot,[StringComparison]::OrdinalIgnoreCase)) {
    throw 'Use a task-specific OutputDirectory below D:\Temp\codex for disposable validation files.'
}
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
$environmentNames=@('TEMP','TMP','PYTHONUTF8','CARBENTRA_PLATFORM_ROOT','CARBENTRA_STARTUP_TEST_BINARY','CARBENTRA_TIME_TEST_BINARY','CARBENTRA_CERT_TEST_BINARY','CARBENTRA_SWITCH_COMMAND_TEST_BINARY')
$previousEnvironment=@{}
foreach ($name in $environmentNames) { $previousEnvironment[$name]=[Environment]::GetEnvironmentVariable($name,'Process') }
function Run([string[]]$Command, [string]$LogName) {
    $exe=$Command[0]; $arguments=$Command[1..($Command.Count-1)]
    if ($LogName) { & $exe @arguments 2>&1 | Tee-Object -FilePath (Join-Path $OutputDirectory $LogName) }
    else { & $exe @arguments }
    if ($LASTEXITCODE -ne 0) { throw "Failed: $exe $($arguments -join ' ')" }
}
Push-Location $root
try {
    $env:CARBENTRA_PLATFORM_ROOT=$PlatformRoot
    $env:TEMP=$OutputDirectory; $env:TMP=$OutputDirectory; $env:PYTHONUTF8='1'
    if (-not $SwitchCommandTestBinary) {
        Run @('pwsh','-NoProfile','-File','firmware/tests/build_switch_command_test.ps1','-PlatformRoot',$PlatformRoot,'-SwitchRoot',$SwitchRoot,'-IdfRoot',$IdfRoot,'-OutputDirectory',"$OutputDirectory\switch-command") 'switch-command-build.log'
        $SwitchCommandTestBinary="$OutputDirectory\switch-command\switch_command_decoder.exe"
    }
    if (-not (Test-Path -LiteralPath $SwitchCommandTestBinary -PathType Leaf)) {
        throw 'Switch command decoder binary was not built or the explicitly supplied path does not exist.'
    }
    $env:CARBENTRA_SWITCH_COMMAND_TEST_BINARY=(Resolve-Path -LiteralPath $SwitchCommandTestBinary).Path
    Run @('pwsh','-NoProfile','-File','firmware/tests/run_host_tests.ps1','-AddressSanitizer','-OutputDirectory',"$OutputDirectory\host") 'host-results.txt'
    Run @('pwsh','-NoProfile','-File','firmware/tests/run_crypto_tests.ps1','-PlatformRoot',$PlatformRoot,'-IdfRoot',$IdfRoot,'-OutputDirectory',"$OutputDirectory\crypto") 'crypto-results.txt'
    $env:CARBENTRA_STARTUP_TEST_BINARY="$OutputDirectory\host\test_startup\test_startup.exe"
    $env:CARBENTRA_TIME_TEST_BINARY="$OutputDirectory\crypto\time_signature\test_time_signature.exe"
    $env:CARBENTRA_CERT_TEST_BINARY="$OutputDirectory\crypto\certificate_dates\test_certificate_dates.exe"
    Run @((Join-Path $PlatformRoot '.venv\Scripts\python.exe'),(Join-Path $PlatformRoot 'edge\tools\run_checks.py'),'--release','--output',"$OutputDirectory\shared-edge-validation.json") 'shared-edge-results.txt'
    Run @('.venv\Scripts\python.exe','-m','unittest','discover','-s','tests/hardware','-v')
    if ($BuildTarget) { Run @('pwsh','-NoProfile','-File','scripts/build_firmware.ps1','-IdfRoot',$IdfRoot,'-OutputDirectory',"$OutputDirectory\idf-build") 'target-build.log' }
    if ($CheckNativeCAD) {
        foreach ($script in @('verify_exports.py','validate_integrated_fit.py','validate_contact_engagement.py','validate_shutter.py','audit_connectivity.py','insulation_domain_audit.py')) {
            & "$PSScriptRoot\engineering.ps1" -Runtime freecad -Script "mechanical/rev_b/$script" -TemporaryDirectory $OutputDirectory
        }
        & "$PSScriptRoot\engineering.ps1" -Runtime freecad -Script 'electronics/rev_b/integrated/scripts/audit_rear_termination.py' -TemporaryDirectory $OutputDirectory
        foreach ($script in @('test_native_rules.py','test_projected_isolation.py','finalize_validation.py')) {
            & "$PSScriptRoot\engineering.ps1" -Runtime kicad -Script "electronics/rev_b/integrated/scripts/$script" -TemporaryDirectory $OutputDirectory
        }
    }
    if ($RenderGPU) {
        & "$PSScriptRoot\engineering.ps1" -Runtime blender -Script 'visuals/scripts/verify_native_scene.py' -TemporaryDirectory $OutputDirectory -ScriptArguments @((Join-Path $root 'visuals/rev_b/carbentra_studio.blend'),"$OutputDirectory\blender")
    }
    Write-Host 'Selected Windows checks passed. Physical fabrication/energization gates remain HOLD.'
    Write-Host "Validation outputs: $OutputDirectory"
} finally {
    Pop-Location
    foreach ($name in $environmentNames) {
        $value=$previousEnvironment[$name]
        if ($null -eq $value) { [Environment]::SetEnvironmentVariable($name,[NullString]::Value,'Process') }
        else { [Environment]::SetEnvironmentVariable($name,$value,'Process') }
    }
}
