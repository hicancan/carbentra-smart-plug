[CmdletBinding()]
param([string]$OutputDirectory='D:\Temp\codex\carbentra-localize-20261001\plug\rebuild')
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
$OutputDirectory=[IO.Path]::GetFullPath($OutputDirectory)
if ($OutputDirectory.StartsWith($root,[StringComparison]::OrdinalIgnoreCase)) { throw 'Rebuild must be outside the source checkout' }
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
$files=@(& git -C $root ls-files --cached --others --exclude-standard) | Sort-Object -Unique
foreach ($file in $files) {
    $source=Join-Path $root $file
    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { continue }
    $destination=Join-Path $OutputDirectory $file
    New-Item -ItemType Directory -Path (Split-Path $destination -Parent) -Force | Out-Null
    Copy-Item -LiteralPath $source -Destination $destination -Force
}
$launcher=Join-Path $OutputDirectory 'scripts\engineering.ps1'
foreach($name in @('build_manifest.py','build_assembly.py','build_schematic.py')) {
    & $launcher -Runtime kicad -Script "electronics/rev_b/integrated/scripts/$name"
}
& $launcher -Runtime kicad -Script electronics/rev_b/integrated/scripts/build_pcb.py
& $launcher -Runtime kicad -Script electronics/rev_b/scripts/replay_routing.py -ScriptArguments @((Join-Path $OutputDirectory 'electronics/rev_b/integrated/integrated.kicad_pcb'))
& $launcher -Runtime freecad -Script electronics/rev_b/integrated/scripts/export_geometry.py -ScriptArguments @('--bodies-only')
foreach($name in @('build_base.py','export_release.py','verify_exports.py','validate_integrated_fit.py','validate_contact_engagement.py','validate_shutter.py','audit_connectivity.py')) {
    & $launcher -Runtime freecad -Script "mechanical/rev_b/$name"
}
& "$PSScriptRoot\engineering.ps1" -Runtime freecad -Script scripts/verify_hardware_rebuild.py -ScriptArguments @('--rebuilt-root',$OutputDirectory)
& "$PSScriptRoot\engineering.ps1" -Runtime kicad -Script scripts/verify_rebuilt_ecad.py -ScriptArguments @('--rebuilt-root',$OutputDirectory)
