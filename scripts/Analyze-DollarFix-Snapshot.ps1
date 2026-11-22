# DollarFix installed APK set: integrity validation and REA/Codex investigation.
# Reads only local backup files; does not touch the connected phone.
# Windows PowerShell 5.1+, Python 3 for the inventory helper.
[CmdletBinding()]
param(
    [string]$ProjectRoot = "C:\REA\Project\DollarFix",
    [string]$SnapshotDirectory = "",
    [string]$QiruiZipPath = "",
    [switch]$SkipJadx,
    [switch]$SkipApktool,
    [switch]$SkipCodex
)
$ErrorActionPreference = "Stop"

function Find-Tool {
    param([string[]]$Candidates)
    foreach ($candidate in $Candidates) {
        $found = Get-Command $candidate -ErrorAction SilentlyContinue
        if ($found) { return $found.Source }
    }
    return $null
}

function Run-Tool {
    param(
        [string]$Name,
        [string]$Executable,
        [string[]]$ToolArguments,
        [string]$LogFile
    )
    $exit = -1
    $errorText = $null
    try {
        # Capture both streams without suppressing exit codes.
        & $Executable @ToolArguments 1> $LogFile 2>&1
        $exit = $LASTEXITCODE
    }
    catch {
        $errorText = $_.Exception.Message
        [IO.File]::AppendAllText($LogFile, ([Environment]::NewLine + $errorText))
    }
    $result = [ordered]@{
        tool = $Name
        executable = $Executable
        exit_code = $exit
        log = $LogFile
    }
    if ($errorText) { $result.error = $errorText }
    return $result
}

$root = (Resolve-Path -LiteralPath $ProjectRoot).Path
$scriptRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$inventoryHelper = Join-Path $scriptRoot "reverse\tools\inventory_apk.py"
$codexInstructions = Join-Path $scriptRoot "reverse\docs\CODEX_RE_TASK.md"
if (-not (Test-Path -LiteralPath $inventoryHelper -PathType Leaf)) {
    throw "Missing helper: $inventoryHelper. Execute from a full repository checkout."
}

if (-not $SnapshotDirectory) {
    $snapshotsRoot = Join-Path $root "reverse\input"
    $snapshots = @(Get-ChildItem -LiteralPath $snapshotsRoot -Directory -Filter "DollarFix-installed-*" |
        Sort-Object Name -Descending)
    if ($snapshots.Count -eq 0) { throw "No installed APK backup found under $snapshotsRoot" }
    $SnapshotDirectory = $snapshots[0].FullName
}
$source = (Resolve-Path -LiteralPath $SnapshotDirectory).Path
$manifestPath = Join-Path $source "manifest.json"
if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    throw "Snapshot metadata missing: $manifestPath"
}
$manifest = Get-Content -LiteralPath $manifestPath -Encoding UTF8 -Raw | ConvertFrom-Json
$expectedFiles = @($manifest.apk_files)
if ($expectedFiles.Count -eq 0 -or $expectedFiles.Count -ne [int]$manifest.apk_count) {
    throw "Invalid backup manifest: APK count mismatch"
}

$reportDir = Join-Path $root ("reverse\reports\" + (Split-Path -Leaf $source))
$workDir = Join-Path $root ("reverse\work\" + (Split-Path -Leaf $source))
foreach ($dir in @($reportDir,$workDir)) {
    New-Item -Path $dir -ItemType Directory -Force | Out-Null
}
$verifiedFiles = @()
$seen = @{}
foreach ($entry in $expectedFiles) {
    $name = [string]$entry.local_filename
    if ([IO.Path]::GetFileName($name) -ne $name -or $name -notmatch '\.apk$') {
        throw "Unsafe APK filename in manifest: $name"
    }
    if ($seen.ContainsKey($name)) { throw "Duplicate APK filename: $name" }
    $seen[$name] = $true
    $fullPath = Join-Path $source $name
    if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) {
        throw "Missing APK: $fullPath"
    }
    $actualSize = (Get-Item -LiteralPath $fullPath).Length
    $actualHash = (Get-FileHash -LiteralPath $fullPath -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actualSize -ne [long]$entry.size_bytes) {
        throw "Size mismatch: $name"
    }
    if ($actualHash -ne ([string]$entry.sha256).ToLowerInvariant()) {
        throw "SHA-256 mismatch: $name. Stop analysis, preserve snapshot."
    }
    $verifiedFiles += [ordered]@{
        name = $name
        path = $fullPath
        size_bytes = $actualSize
        sha256 = $actualHash
    }
}
$baseEntry = @($verifiedFiles | Where-Object { $_.name -eq "base.apk" })
if ($baseEntry.Count -ne 1) { throw "Snapshot must contain exactly one base.apk" }
$baseApk = $baseEntry[0].path

$verification = [ordered]@{
    analysis_type = "installed-split-apk-snapshot"
    snapshot_directory = $source
    package = [string]$manifest.android_package
    expected_apk_count = $manifest.apk_count
    verified_apk_count = $verifiedFiles.Count
    verified_sha256 = $true
    files = $verifiedFiles
}
$verification | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $reportDir "snapshot-verification.json") -Encoding UTF8
Write-Host "Verified $($verifiedFiles.Count) installed APK files (byte sizes + SHA-256)."
foreach ($file in $verifiedFiles) {
    Write-Host (" {0}: {1}" -f $file.name, $file.sha256)
}

$toolResults = [ordered]@{}
$python = Find-Tool @("python.exe","py.exe","python","py")
if (-not $python) { throw "Python 3 not found. Install Python to run the local read-only inventory." }
$pythonPrefix = @()
if ([IO.Path]::GetFileNameWithoutExtension($python) -eq "py") { $pythonPrefix = @("-3") }

foreach ($file in $verifiedFiles) {
    $shortname = [IO.Path]::GetFileNameWithoutExtension($file.name)
    $inventoryOutput = Join-Path $reportDir ("inventory-" + $shortname + ".json")
    $nativeOutput = Join-Path (Join-Path $workDir "native") $shortname
    $arguments = @() + $pythonPrefix + @(
        $inventoryHelper, $file.path,
        "--output", $inventoryOutput,
        "--extract-native", $nativeOutput
    )
    $result = Run-Tool "python-inventory-$shortname" $python $arguments (Join-Path $reportDir ("inventory-" + $shortname + ".log"))
    $toolResults["inventory_" + $shortname] = $result
    if ($result.exit_code -ne 0) {
        throw "Inventory failed for $($file.name), see $($result.log)"
    }
}

if ($QiruiZipPath) {
    $qirui = (Resolve-Path -LiteralPath $QiruiZipPath).Path
    $arguments = @() + $pythonPrefix + @(
        $inventoryHelper, $qirui,
        "--output", (Join-Path $reportDir "inventory-qirui.json"),
        "--extract-native", (Join-Path $workDir "native\qirui")
    )
    $toolResults.qirui_inventory = Run-Tool "qirui-inventory" $python $arguments (Join-Path $reportDir "inventory-qirui.log")
}

$jadx = Find-Tool @("jadx.bat","jadx.exe","jadx")
if ($jadx -and -not $SkipJadx) {
    $toolResults.jadx = Run-Tool "jadx-base" $jadx @(
        "--no-res", "-j", "4", "-d", (Join-Path $workDir "jadx-base"), $baseApk
    ) (Join-Path $reportDir "jadx-base.log")
}
else { $toolResults.jadx = @{ found = $false; skipped = [bool]$SkipJadx } }

$apktool = Find-Tool @("apktool.bat","apktool.exe","apktool")
if ($apktool -and -not $SkipApktool) {
    foreach ($file in $verifiedFiles) {
        $shortname = [IO.Path]::GetFileNameWithoutExtension($file.name)
        $result = Run-Tool "apktool-$shortname" $apktool @(
            "d", "-f", "-o", (Join-Path $workDir ("apktool-" + $shortname)),
            $file.path
        ) (Join-Path $reportDir ("apktool-" + $shortname + ".log"))
        $toolResults["apktool_" + $shortname] = $result
    }
}
else { $toolResults.apktool = @{ found = $false; skipped = [bool]$SkipApktool } }

$rea = Find-Tool @("rea.cmd","rea.exe","rea")
if ($rea) {
    $toolResults.rea_doctor = Run-Tool "rea-doctor" $rea @("doctor","--json") (Join-Path $reportDir "rea-doctor.json")
    $toolResults.rea_providers = Run-Tool "rea-providers" $rea @("providers","--json") (Join-Path $reportDir "rea-providers.json")
}
else { $toolResults.rea = @{ found = $false } }

$toolResults | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $reportDir "tool-status.json") -Encoding UTF8

$codex = Find-Tool @("codex.cmd","codex.exe","codex")
if (-not $SkipCodex -and $codex) {
    $summary = Join-Path $reportDir "codex-summary.md"
    $task = Get-Content -LiteralPath $codexInstructions -Encoding UTF8 -Raw
    $task += [Environment]::NewLine
    $task += "IMPORTANT: This is a SPLIT-APK installation: analyze all files in snapshot-verification.json. "
    $task += "The arm64_v8a split contains architecture-dependent code and the ru split contains localization; do not ignore either."
    $task += [Environment]::NewLine
    $task += "Snapshot: $source"
    $task += [Environment]::NewLine
    $task += "Reports: $reportDir"
    $task += [Environment]::NewLine
    $task += "Work files: $workDir"
    $task += [Environment]::NewLine
    $task += "No APK modification, installation or ECU writes in this phase. "
    $task += "Do not claim REA tool activity unless an actual MCP call succeeded."
    $task += [Environment]::NewLine
    $task += "Create a redacted report in $reportDir and do not upload proprietary bytes or secrets."
    Push-Location $root
    try {
        $task | & $codex exec -C $root -o $summary -
        $toolResults.codex = @{ found = $true; exit_code = $LASTEXITCODE; summary = $summary }
    }
    catch {
        $toolResults.codex = @{ found = $true; exit_code = -1; error = $_.Exception.Message }
    }
    finally { Pop-Location }
}
else { $toolResults.codex = @{ found = [bool]$codex; skipped = [bool]$SkipCodex } }

$toolResults | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $reportDir "tool-status.json") -Encoding UTF8
foreach ($file in $verifiedFiles) {
    $newHash = (Get-FileHash -LiteralPath $file.path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($newHash -ne $file.sha256) {
        throw "SAFETY FAILURE: original APK changed during investigation: $($file.name)"
    }
}
Write-Host ""
Write-Host "PASS: all original APK hashes unchanged."
Write-Host "Reports: $reportDir"
Write-Host "Decompiled source/native output: $workDir"
Write-Host "Tools report: $(Join-Path $reportDir 'tool-status.json')"
