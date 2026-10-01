[CmdletBinding(SupportsShouldProcess)]
param([switch]$Apply)
$ErrorActionPreference='Stop'
$root=[IO.Path]::GetFullPath((Split-Path $PSScriptRoot -Parent)).TrimEnd('\','/')
$manifest=Get-Content -LiteralPath (Join-Path $root 'release\windows-cleanup.json') -Raw | ConvertFrom-Json
$reachable=[Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
foreach($line in @(& git -C $root rev-list --objects --all)) { [void]$reachable.Add(($line -split ' ',2)[0]) }
if($LASTEXITCODE -ne 0){throw 'Unable to inspect preservation history'}
$validated=@()
foreach($entry in $manifest.entries){
    if([IO.Path]::IsPathRooted($entry.path)){throw 'Manifest path must be relative'}
    $path=[IO.Path]::GetFullPath((Join-Path $root $entry.path))
    if(-not $path.StartsWith($root+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw "Path escapes checkout: $($entry.path)"}
    if(-not (Test-Path -LiteralPath $path)){continue}
    $item=Get-Item -LiteralPath $path
    if($item.PSIsContainer){throw "File required: $($entry.path)"}
    $parent=$item
    while($parent.FullName -ne $root){
        if($parent.Attributes -band [IO.FileAttributes]::ReparsePoint){throw "Reparse point refused: $($entry.path)"}
        $parent=Get-Item -LiteralPath (Split-Path $parent.FullName -Parent)
    }
    if($item.Length -ne $entry.bytes -or (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash -ne $entry.sha256){throw "Candidate changed: $($entry.path)"}
    $tracked=@(& git -C $root ls-files -- $entry.path)
    if($tracked.Count){throw "Tracked source refused: $($entry.path)"}
    if($entry.artifact_kind -eq 'blend_backup'){
        $blob=& git -C $root hash-object -- $path
        if($blob -ne $entry.git_blob -or -not $reachable.Contains($blob)){throw "Backup is not retained in reachable history: $($entry.path)"}
    } elseif($entry.artifact_kind -in @('render_frame','host_build')){
        if(-not $entry.rebuild_sources.PSObject.Properties.Count){throw 'Rebuild inputs missing'}
        foreach($source in $entry.rebuild_sources.PSObject.Properties){
            $inputPath=[IO.Path]::GetFullPath((Join-Path $root $source.Name))
            if(-not $inputPath.StartsWith($root+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw 'Rebuild input escapes checkout'}
            if((Get-FileHash -LiteralPath $inputPath -Algorithm SHA256).Hash -ne $source.Value){throw "Rebuild input changed: $($source.Name)"}
        }
    } else {throw "Unrecognized artifact kind: $($entry.path)"}
    $validated+=[pscustomobject]@{Path=$entry.path;Bytes=$item.Length;AbsolutePath=$path}
}
$validated | Select-Object Path,Bytes | Format-Table -AutoSize
Write-Host "$($validated.Count) validated files; $([math]::Round(($validated|Measure-Object Bytes -Sum).Sum/1MB,2)) MiB. Apply=$Apply"
if($Apply){
    foreach($item in $validated){
        if($PSCmdlet.ShouldProcess($item.AbsolutePath,'Remove exact verified ignored output')){Remove-Item -LiteralPath $item.AbsolutePath -Force}
    }
} else {Write-Host 'Read-only inventory. Run again with -Apply to remove only these verified files.'}
