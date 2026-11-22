# Backup installed DollarFix APK(s) from connected Android device.
# Read-only on the phone: adb devices, pm path, dumpsys package, adb pull.
# Windows PowerShell 5.1+.
[CmdletBinding()]
param(
    [string]$ProjectRoot = "C:\REA\Project\DollarFix",
    [string]$Package = "com.dnd.dollarfix.df51",
    [string]$DeviceSerial = "",
    [string]$AdbPath = "",
    [switch]$InstallAdb
)

$ErrorActionPreference = "Stop"

# Search current PATH plus common local development locations.
$adb = $null
if ($AdbPath) {
    if (-not (Test-Path -LiteralPath $AdbPath -PathType Leaf)) {
        throw "Specified -AdbPath does not exist: $AdbPath"
    }
    $adb = (Resolve-Path -LiteralPath $AdbPath).Path
} else {
    $adbCommand = Get-Command adb.exe -ErrorAction SilentlyContinue
    if ($adbCommand) { $adb = $adbCommand.Source }
}

if (-not $adb) {
    $possible = @(
        (Join-Path $ProjectRoot "tools\android\platform-tools\adb.exe"),
        (Join-Path $ProjectRoot "platform-tools\adb.exe"),
        (Join-Path $ProjectRoot "tools\platform-tools\adb.exe"),
        (Join-Path $env:LOCALAPPDATA "Android\Sdk\platform-tools\adb.exe"),
        "C:\REA\platform-tools\adb.exe",
        "C:\REA\Tools\platform-tools\adb.exe",
        "C:\Tools\platform-tools\adb.exe",
        "C:\platform-tools\adb.exe"
    )
    foreach ($candidate in $possible) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            $adb = $candidate
            break
        }
    }
}

# Explicit opt-in download; no elevation or system-wide PATH mutation.
if (-not $adb -and $InstallAdb) {
    $sdkRoot = Join-Path $ProjectRoot "tools\android"
    $archive = Join-Path $sdkRoot "platform-tools-latest-windows.zip"
    $officialUrl = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
    New-Item -ItemType Directory -Path $sdkRoot -Force | Out-Null
    Write-Host "ADB was not found. Downloading official Google Android Platform-Tools ..."
    Write-Host "Source: $officialUrl"
    try {
        [Net.ServicePointManager]::SecurityProtocol =
            [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $officialUrl -OutFile $archive -UseBasicParsing
        if (-not (Test-Path -LiteralPath $archive -PathType Leaf)) {
            throw "Platform-Tools archive was not downloaded"
        }
        Write-Host ("Download SHA256: " + (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash)
        Expand-Archive -LiteralPath $archive -DestinationPath $sdkRoot -Force
        $candidate = Join-Path $sdkRoot "platform-tools\adb.exe"
        if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) {
            throw "Official archive does not contain expected platform-tools/adb.exe"
        }
        $adb = $candidate
    } catch {
        throw "Failed to download/extract Android Platform-Tools from Google: $($_.Exception.Message)"
    }
}

if (-not $adb) {
    throw "adb.exe not found. Re-run this script with -InstallAdb to download official Google Platform-Tools locally, or supply -AdbPath."
}
Write-Host "ADB: $adb"

$deviceLines = @(& $adb devices -l)
if ($LASTEXITCODE -ne 0) { throw "adb devices failed" }

$connected = @()
foreach ($line in $deviceLines) {
    if ($line -match '^(\S+)\s+device(?:\s|$)') {
        $connected += $Matches[1]
    }
}

if ($DeviceSerial) {
    if ($connected -notcontains $DeviceSerial) {
        throw "ADB device '$DeviceSerial' not authorized/connected. adb devices -l: $($deviceLines -join '; ')"
    }
    $serial = $DeviceSerial
} elseif ($connected.Count -eq 1) {
    $serial = $connected[0]
} else {
    throw "Expected exactly one authorized Android phone; found $($connected.Count). Specify -DeviceSerial. adb devices -l: $($deviceLines -join '; ')"
}

$pmLines = @(& $adb -s $serial shell pm path $Package)
if ($LASTEXITCODE -ne 0) { throw "adb shell pm path failed for $Package" }

$remotePaths = @()
foreach ($line in $pmLines) {
    $clean = ([string]$line).Trim()
    if ($clean.StartsWith("package:")) {
        $remotePaths += $clean.Substring(8).Trim()
    }
}
if ($remotePaths.Count -eq 0) {
    throw "Installed package '$Package' not found on '$serial'. Check package name: adb shell pm list packages dollarfix"
}
$remotePaths = @($remotePaths | Select-Object -Unique)

$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$saveDir = Join-Path $ProjectRoot ("reverse\input\DollarFix-installed-" + $stamp)
New-Item -ItemType Directory -Path $saveDir -Force | Out-Null
$files = @()

foreach ($remote in $remotePaths) {
    $filename = ($remote -split '/')[-1]
    if (-not $filename -or $filename -notmatch '\.apk$') {
        throw "Unexpected APK filename in pm path: $remote"
    }
    if ($filename -match '[\\/:*?"<>|]') {
        throw "Unsafe local APK filename: $filename"
    }
    $dest = Join-Path $saveDir $filename
    if (Test-Path -LiteralPath $dest) {
        throw "Duplicate APK filename in pm path: $filename"
    }

    Write-Host "Pulling $filename ..."
    & $adb -s $serial pull $remote $dest
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $dest -PathType Leaf)) {
        throw "Failed pulling $remote"
    }

    $fileInfo = Get-Item -LiteralPath $dest
    if ($fileInfo.Length -le 0) {
        throw "Downloaded APK is empty: $dest"
    }
    $files += [ordered]@{
        remote_path = $remote
        local_filename = $filename
        size_bytes = $fileInfo.Length
        sha256 = (Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash.ToLowerInvariant()
    }
}

$packageDump = @(& $adb -s $serial shell dumpsys package $Package)
if ($LASTEXITCODE -ne 0) { Write-Warning "dumpsys package failed; APK backup is still valid." }
$versionLines = @(
    $packageDump |
        Where-Object { $_ -match 'versionName=|versionCode=|minSdk=|targetSdk=' } |
        Select-Object -First 20
)
$versionLines | Set-Content -LiteralPath (Join-Path $saveDir "package-version.txt") -Encoding UTF8

$manifest = [ordered]@{
    capture_time_local = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssK")
    android_package = $Package
    adb_serial = $serial
    apk_count = $files.Count
    apk_files = $files
    version_details = $versionLines
}
$manifest | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $saveDir "manifest.json") -Encoding UTF8

$zipPath = Join-Path $saveDir "DollarFix-installed-apks.zip"
$apkLocalPaths = @($files | ForEach-Object { Join-Path $saveDir $_.local_filename })
Compress-Archive -LiteralPath $apkLocalPaths -DestinationPath $zipPath -CompressionLevel Optimal
if (-not (Test-Path -LiteralPath $zipPath -PathType Leaf)) {
    throw "Could not create APK bundle ZIP"
}
$bundleHash = (Get-FileHash -LiteralPath $zipPath -Algorithm SHA256).Hash.ToLowerInvariant()

Write-Host ""
Write-Host "SUCCESS: saved the installed DollarFix APK(s) without modifying the phone."
Write-Host "Device: $serial"
Write-Host "Package: $Package"
Write-Host "APK files: $($files.Count)"
Write-Host "Directory: $saveDir"
foreach ($item in $files) {
    Write-Host ("{0}  {1} bytes  SHA256={2}" -f $item.local_filename, $item.size_bytes, $item.sha256)
}
Write-Host "APK bundle: $zipPath"
Write-Host "Bundle SHA256: $bundleHash"
Write-Host "Metadata: $(Join-Path $saveDir 'manifest.json')"
Write-Host ""
Write-Host "Keep base.apk and every split APK. Do not uninstall the original app."
