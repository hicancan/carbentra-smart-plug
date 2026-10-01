[CmdletBinding()]
param(
    [string]$IdfRoot = 'D:\Dev\esp-idf-v5.4.3',
    [string]$PlatformRoot = $env:CARBENTRA_PLATFORM_ROOT,
    [string]$OutputDirectory = 'D:\Temp\codex\carbentra-localize-20261001\plug\crypto'
)
$ErrorActionPreference='Stop'
$repoRoot=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
if (-not $PlatformRoot) { $PlatformRoot=Join-Path (Split-Path $repoRoot -Parent) 'carbentra-campus-platform' }
$platformPython=Join-Path $PlatformRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $platformPython)) { throw 'Sync the shared platform uv environment first.' }
if (-not (Get-Command cl.exe -ErrorAction SilentlyContinue)) {
    $vswhere=Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
    $vsRoot=& $vswhere -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
    & (Join-Path $vsRoot 'Common7\Tools\Launch-VsDevShell.ps1') -Arch amd64 -HostArch amd64 -SkipAutomaticLocation
}
$source=Join-Path $IdfRoot 'components\mbedtls\mbedtls'
$build=Join-Path $OutputDirectory 'mbedtls'
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
$env:TEMP=$OutputDirectory; $env:TMP=$OutputDirectory; $env:PYTHONUTF8='1'
& cmake -S $source -B $build -G Ninja -DENABLE_PROGRAMS=OFF -DENABLE_TESTING=OFF -DCMAKE_BUILD_TYPE=Release "-DPython3_EXECUTABLE=$platformPython"
if ($LASTEXITCODE -ne 0) { throw 'mbedTLS configuration failed' }
& cmake --build $build --parallel 12
if ($LASTEXITCODE -ne 0) { throw 'mbedTLS build failed' }
$firmware=Join-Path $repoRoot 'firmware'
$common=@('/nologo','/TC','/std:c11','/MD','/W3','/D_CRT_SECURE_NO_WARNINGS',"/I$source\include", "/I$firmware\core", "/I$firmware\third_party\cJSON")
$crypto=Join-Path $build 'library\mbedcrypto.lib'
$x509=Join-Path $build 'library\mbedx509.lib'
foreach ($kind in @('time_signature','certificate_dates')) {
    $caseDir=Join-Path $OutputDirectory $kind
    New-Item -ItemType Directory -Path $caseDir -Force | Out-Null
    $exe=Join-Path $caseDir ('test_'+$kind+'.exe')
    $files=@(Join-Path $firmware "tests\test_$kind.c")
    $libraries=@($crypto,'bcrypt.lib')
    if ($kind -eq 'time_signature') {
        $files+=@('core\carbentra_time_signature.c','core\carbentra_json.c','third_party\cJSON\cJSON.c') | ForEach-Object { Join-Path $firmware $_ }
    } else { $libraries=@($x509)+$libraries }
    & cl.exe @common "/Fo$caseDir\" "/Fe$exe" @files /link @libraries
    if ($LASTEXITCODE -ne 0) { throw "Crypto test compilation failed: $kind" }
}
$env:CARBENTRA_TIME_TEST_BINARY=Join-Path $OutputDirectory 'time_signature\test_time_signature.exe'
$env:CARBENTRA_CERT_TEST_BINARY=Join-Path $OutputDirectory 'certificate_dates\test_certificate_dates.exe'
& $platformPython -m pytest (Join-Path $PlatformRoot 'edge\tests\test_time_bootstrap.py') (Join-Path $PlatformRoot 'edge\tests\test_certificate_dates.py') -o addopts= -v --junitxml (Join-Path $OutputDirectory 'crypto-tests.xml')
if ($LASTEXITCODE -ne 0) { throw 'Real firmware signature/certificate regressions failed' }
