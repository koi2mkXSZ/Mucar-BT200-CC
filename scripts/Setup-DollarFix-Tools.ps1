# Install/verify pinned open-source JADX and Apktool for DollarFix RE.
# Downloads from official GitHub releases, checks SHA-256 before extraction.
# Nothing is installed system-wide and no proprietary APK is uploaded.
[CmdletBinding()]
param(
    [string]$ProjectRoot = "C:\REA\Project\DollarFix",
    [switch]$ForceDownload
)
$ErrorActionPreference = "Stop"

$toolRoot = Join-Path $ProjectRoot "tools\reverse"
New-Item -Path $toolRoot -ItemType Directory -Force | Out-Null

function Fetch-Checked {
    param([string]$Url, [string]$Destination, [string]$ExpectedHash)
    if ((Test-Path -LiteralPath $Destination -PathType Leaf) -and -not $ForceDownload) {
        $existing = (Get-FileHash -LiteralPath $Destination -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($existing -eq $ExpectedHash.ToLowerInvariant()) {
            Write-Host "Using verified existing: $Destination"
            return
        }
        Write-Warning "Existing download SHA-256 differs; re-downloading $Destination"
    }

    $tempFile = "$Destination.download"
    if (Test-Path -LiteralPath $tempFile) { Remove-Item -LiteralPath $tempFile -Force }
    Write-Host "Downloading from official release: $Url"
    [Net.ServicePointManager]::SecurityProtocol =
        [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest -Uri $Url -OutFile $tempFile -UseBasicParsing
    $actual = (Get-FileHash -LiteralPath $tempFile -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $ExpectedHash.ToLowerInvariant()) {
        Remove-Item -LiteralPath $tempFile -Force
        throw "SHA-256 mismatch for $Url. Expected $ExpectedHash; got $actual. Download removed."
    }
    Move-Item -LiteralPath $tempFile -Destination $Destination -Force
    Write-Host "SHA-256 verified: $actual"
}

# Official skylot/jadx v1.5.7 release asset, SHA-256 taken from GitHub release asset digest.
$jadxVersion = "1.5.7"
$jadxUrl = "https://github.com/skylot/jadx/releases/download/v1.5.7/jadx-1.5.7.zip"
$jadxDigest = "1755e4242ade71a077438723689f404079592ec7764a3a0572f98fef94ebcbf3"
$jadxZip = Join-Path $toolRoot "jadx-1.5.7.zip"
Fetch-Checked $jadxUrl $jadxZip $jadxDigest

$jadxDir = Join-Path $toolRoot "jadx"
$jadxCmd = Join-Path $jadxDir "bin\jadx.bat"
if (-not (Test-Path -LiteralPath $jadxCmd -PathType Leaf) -or $ForceDownload) {
    New-Item -Path $jadxDir -ItemType Directory -Force | Out-Null
    Expand-Archive -LiteralPath $jadxZip -DestinationPath $jadxDir -Force
}
if (-not (Test-Path -LiteralPath $jadxCmd -PathType Leaf)) {
    throw "JADX bundle did not contain bin\jadx.bat"
}
Write-Host "JADX installed: $jadxCmd"

# Official iBotPeaches/Apktool v3.0.3 asset, SHA-256 from GitHub release asset digest.
$apktoolVersion = "3.0.3"
$apktoolUrl = "https://github.com/iBotPeaches/Apktool/releases/download/v3.0.3/apktool_3.0.3.jar"
$apktoolDigest = "dbf930b076c6b9be08d57c449cacefc3bdd6b71ebd59b3066fc0e1f5b14f9423"
$apktoolDir = Join-Path $toolRoot "apktool"
New-Item -Path $apktoolDir -ItemType Directory -Force | Out-Null
$apktoolJar = Join-Path $apktoolDir "apktool.jar"
Fetch-Checked $apktoolUrl $apktoolJar $apktoolDigest

$wrapperPath = Join-Path $apktoolDir "apktool.bat"
$wrapper = '@echo off' + [Environment]::NewLine +
    'if defined JAVA_HOME (' + [Environment]::NewLine +
    '  "%JAVA_HOME%\bin\java.exe" -jar "%~dp0apktool.jar" %*' + [Environment]::NewLine +
    ') else (' + [Environment]::NewLine +
    '  java -jar "%~dp0apktool.jar" %*' + [Environment]::NewLine +
    ')' + [Environment]::NewLine
[IO.File]::WriteAllText($wrapperPath, $wrapper, [Text.Encoding]::ASCII)

Write-Host "Apktool installed: $wrapperPath"
$java = Get-Command java.exe -ErrorAction SilentlyContinue
$javaHomeBin = if ($env:JAVA_HOME) { Join-Path $env:JAVA_HOME "bin\java.exe" } else { $null }
if (-not $java -and -not ($javaHomeBin -and (Test-Path -LiteralPath $javaHomeBin))) {
    Write-Warning "Java 17+ not found in PATH or JAVA_HOME. Install Java/JDK 17+ before running JADX and Apktool."
    Write-Host "JADX/Apktool files are still ready on disk."
}
else {
    $javaExecutable = if ($java) { $java.Source } else { $javaHomeBin }
    Write-Host "Java executable: $javaExecutable"
    # java -version normally writes to stderr; do not convert it to a terminating PowerShell error.
    & $javaExecutable -version
    if ($LASTEXITCODE -ne 0) { Write-Warning "Java executable returned exit code $LASTEXITCODE" }
}
Write-Host "Prepared exact versions: JADX $jadxVersion; Apktool $apktoolVersion"
Write-Host "Local tool root: $toolRoot"
