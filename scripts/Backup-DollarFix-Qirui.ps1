# Preserve the currently installed external QIRUI diagnostic package.
# Read-only Android operations: adb devices, shell ls, adb pull.
# No root, no signing bypass, no application data mutation.
[CmdletBinding()]
param(
    [string]$ProjectRoot = "C:\REA\Project\DollarFix",
    [string]$DeviceSerial = "",
    [string]$AdapterId = "",
    [string]$RemotePath = "",
    [string]$AdbPath = ""
)
$ErrorActionPreference = "Stop"
if (-not $AdbPath) {
    foreach ($candidate in @(
        (Join-Path $ProjectRoot "tools\android\platform-tools\adb.exe"),
        (Join-Path $env:LOCALAPPDATA "Android\Sdk\platform-tools\adb.exe"),
        "C:\platform-tools\adb.exe"
    )) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            $AdbPath = $candidate
            break
        }
    }
}
if (-not $AdbPath) {
    $command = Get-Command adb.exe -ErrorAction SilentlyContinue
    if ($command) { $AdbPath = $command.Source }
}
if (-not $AdbPath -or -not (Test-Path -LiteralPath $AdbPath -PathType Leaf)) {
    throw "ADB not found. Use -AdbPath or scripts/Backup-DollarFix-Apk.ps1 -InstallAdb."
}
$devices = @(& $AdbPath devices -l)
if ($LASTEXITCODE -ne 0) { throw "adb devices failed" }
$online = @()
foreach ($line in $devices) {
    if ($line -match '^(\S+)\s+device(?:\s|$)') { $online += $Matches[1] }
}
if ($DeviceSerial) {
    if ($online -notcontains $DeviceSerial) {
        throw "Phone is not authorized/online: $DeviceSerial"
    }
} elseif ($online.Count -eq 1) {
    $DeviceSerial = $online[0]
} else {
    throw "Specify -DeviceSerial; online device count: $($online.Count)"
}

# Use a supplied absolute Android path when the adapter identifier is unknown.
if (-not $RemotePath) {
    if (-not $AdapterId) { throw "Specify -AdapterId or -RemotePath for the diagnostic package." }
    if ($AdapterId -notmatch '^[0-9A-Za-z_-]+$') {
        throw "AdapterId contains invalid path characters"
    }
    $RemotePath = "/sdcard/Android/data/com.dnd.dollarfix.df51/files/DollarFix/ThinkDiag/$AdapterId/64/DIAGNOSTIC/VEHICLES/QIRUI_TY/V10.22"
}
if ($RemotePath -notmatch '^/(sdcard|storage/emulated/0)/Android/data/com\.dnd\.dollarfix\.df51/files/' -or
    $RemotePath -match '(\.\.|[\x00-\x1f])') {
    throw "RemotePath must be inside DollarFix external app files. Root access is not requested."
}

Write-Host "Checking package location on connected Android device..."
& $AdbPath -s $DeviceSerial shell ls -ld $RemotePath
if ($LASTEXITCODE -ne 0) {
    throw "QIRUI directory is not accessible via regular ADB shell. The app may store it elsewhere or Android access may be restricted. No root/bypass attempted."
}

$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$destination = Join-Path $ProjectRoot ("reverse\input\QIRUI-installed-" + $stamp)
New-Item -ItemType Directory -Force -Path $destination | Out-Null
Write-Host "Pulling QIRUI diagnostic package to local ignored storage..."
& $AdbPath -s $DeviceSerial pull $RemotePath $destination
if ($LASTEXITCODE -ne 0) {
    throw "adb pull failed. Check ADB permissions and package location."
}

# It is possible that remote contains empty directories; report actual files only.
$records = @()
foreach ($file in @(Get-ChildItem -LiteralPath $destination -File -Recurse)) {
    $rel = $file.FullName.Substring($destination.Length).TrimStart([char[]]@('\','/'))
    $records += [ordered]@{
        relative_path = $rel
        length = $file.Length
        sha256 = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    }
}
if ($records.Count -eq 0) { throw "ADB succeeded but no QIRUI files were found." }
$manifest = [ordered]@{
    package = "QIRUI_TY/V10.22"
    source_path = $RemotePath
    capture_date = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssK")
    file_count = $records.Count
    files = $records
}
$manifestPath = Join-Path $destination "qirui-manifest.json"
$manifest | ConvertTo-Json -Depth 6 |
    Set-Content -LiteralPath $manifestPath -Encoding UTF8

Write-Host "SUCCESS: QIRUI diagnostic package backed up read-only."
Write-Host "Files: $($records.Count)"
Write-Host "Directory: $destination"
Write-Host "Manifest: $manifestPath"
Write-Host "This folder stays out of the public Git repository."
