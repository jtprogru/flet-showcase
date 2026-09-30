# Downloads the Windows build of flet-showcase from GitHub Releases, verifies
# its checksum and unpacks it into %LOCALAPPDATA%\Programs\flet-showcase.
#
#   .\install.ps1                    latest release
#   .\install.ps1 -Version v2.1.0    specific release
#
# Windows on ARM64 gets the x64 build: the built-in emulation runs it.
#
# The file is ASCII-only on purpose: Windows PowerShell 5.1 reads scripts
# without a BOM in the ANSI code page, which mangles Cyrillic string literals.

param(
    [string]$Version = "latest",
    [string]$InstallDir = (Join-Path $env:LOCALAPPDATA "Programs\flet-showcase"),
    [string]$Repo = "jtprogru/flet-showcase"
)

$ErrorActionPreference = "Stop"
# The progress bar makes Invoke-WebRequest several times slower in PowerShell 5.1.
$ProgressPreference = "SilentlyContinue"

$app = "flet-showcase"
$asset = "$app-windows-x64.zip"

if ($Version -eq "latest") {
    $base = "https://github.com/$Repo/releases/latest/download"
} else {
    if (-not $Version.StartsWith("v")) { $Version = "v$Version" }
    $base = "https://github.com/$Repo/releases/download/$Version"
}

$tmp = Join-Path ([IO.Path]::GetTempPath()) ([Guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path $tmp | Out-Null
try {
    Write-Host "Downloading $asset ($Version)"
    $archive = Join-Path $tmp $asset
    $sums = Join-Path $tmp "SHA256SUMS.txt"
    Invoke-WebRequest -UseBasicParsing -Uri "$base/$asset" -OutFile $archive
    Invoke-WebRequest -UseBasicParsing -Uri "$base/SHA256SUMS.txt" -OutFile $sums

    $expected = Get-Content $sums |
        ForEach-Object { $parts = $_ -split "\s+"; if ($parts[1] -eq $asset) { $parts[0] } } |
        Select-Object -First 1
    if (-not $expected) { throw "SHA256SUMS.txt has no entry for $asset" }
    $actual = (Get-FileHash -Algorithm SHA256 -Path $archive).Hash
    if ($actual -ne $expected) { throw "Checksum mismatch for $asset" }

    $unpacked = Join-Path $tmp "unpacked"
    Expand-Archive -Path $archive -DestinationPath $unpacked
    if (Test-Path $InstallDir) { Remove-Item -Recurse -Force $InstallDir }
    New-Item -ItemType Directory -Force -Path (Split-Path $InstallDir) | Out-Null
    Move-Item -Path (Join-Path $unpacked $app) -Destination $InstallDir

    Write-Host "Installed: $(Join-Path $InstallDir "$app.exe")"
} finally {
    Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
}
