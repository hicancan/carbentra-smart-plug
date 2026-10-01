[CmdletBinding()]
param(
    [string]$PlatformRoot=$env:CARBENTRA_PLATFORM_ROOT,
    [string]$SwitchCommandTestBinary=$env:CARBENTRA_SWITCH_COMMAND_TEST_BINARY,
    [string]$OutputDirectory='D:\Temp\codex\carbentra-localize-20261001\plug',
    [switch]$BuildTarget,
    [switch]$CheckNativeCAD,
    [switch]$RenderGPU
)
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
if (-not $PlatformRoot) { $PlatformRoot=Join-Path (Split-Path $root -Parent) 'carbentra-campus-platform' }
$env:CARBENTRA_PLATFORM_ROOT=$PlatformRoot
if (-not $SwitchCommandTestBinary -or -not (Test-Path -LiteralPath $SwitchCommandTestBinary -PathType Leaf)) {
    throw 'Supply -SwitchCommandTestBinary (or CARBENTRA_SWITCH_COMMAND_TEST_BINARY): the actual Switch C decoder gate built from the shared Edge harness and Switch sources'
}
$env:CARBENTRA_SWITCH_COMMAND_TEST_BINARY=(Resolve-Path -LiteralPath $SwitchCommandTestBinary).Path
$env:TEMP=$OutputDirectory; $env:TMP=$OutputDirectory; $env:PYTHONUTF8='1'
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
function Run([string[]]$Command) {
    $exe=$Command[0]; $arguments=$Command[1..($Command.Count-1)]
    & $exe @arguments
    if ($LASTEXITCODE -ne 0) { throw "Failed: $exe $($arguments -join ' ')" }
}
Push-Location $root
try {
    Run @('pwsh','-NoProfile','-File','firmware/tests/run_host_tests.ps1','-AddressSanitizer','-OutputDirectory',"$OutputDirectory\host")
    Run @('pwsh','-NoProfile','-File','firmware/tests/run_crypto_tests.ps1','-PlatformRoot',$PlatformRoot,'-OutputDirectory',"$OutputDirectory\crypto")
    $env:CARBENTRA_STARTUP_TEST_BINARY="$OutputDirectory\host\test_startup\test_startup.exe"
    $env:CARBENTRA_TIME_TEST_BINARY="$OutputDirectory\crypto\time_signature\test_time_signature.exe"
    $env:CARBENTRA_CERT_TEST_BINARY="$OutputDirectory\crypto\certificate_dates\test_certificate_dates.exe"
    Run @((Join-Path $PlatformRoot '.venv\Scripts\python.exe'),(Join-Path $PlatformRoot 'edge\tools\run_checks.py'),'--release','--output',"$OutputDirectory\shared-edge-validation.json")
    Run @('.venv\Scripts\python.exe','-m','unittest','discover','-s','tests/hardware','-v')
    if ($BuildTarget) { Run @('pwsh','-NoProfile','-File','scripts/build_firmware.ps1','-OutputDirectory',"$OutputDirectory\idf-build") }
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
} finally { Pop-Location }
