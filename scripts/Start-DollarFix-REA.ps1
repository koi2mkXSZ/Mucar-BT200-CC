# Requires Windows PowerShell 5.1+ and Python 3.
# APK and extracted material are stored under git-ignored reverse/input, work and reports.
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$ApkPath,
    [string]$QiruiZipPath = "",
    [switch]$SkipCodex
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$reverseRoot = Join-Path $repoRoot "reverse"
$inputDir = Join-Path $reverseRoot "input"
$workDir = Join-Path $reverseRoot "work"
$reportDir = Join-Path $reverseRoot "reports"
foreach ($dir in @($inputDir,$workDir,$reportDir)) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
}

function ToolPath {
    param([string[]]$Names)
    foreach ($name in $Names) {
        $found = Get-Command $name -ErrorAction SilentlyContinue
        if ($found) { return $found.Source }
    }
    return $null
}
function RunRecorded {
    param([string]$Tool, [string[]]$Arguments, [string]$ReportName)
    $log = Join-Path $reportDir $ReportName
    try {
        & $Tool @Arguments *> $log
        return @{ found = $true; exit_code = $LASTEXITCODE; log = $log }
    }
    catch {
        $_ | Out-File -FilePath $log -Append -Encoding UTF8
        return @{ found = $true; exit_code = -1; log = $log; error = $_.Exception.Message }
    }
}

$inputApk = (Resolve-Path -LiteralPath $ApkPath).Path
$sourceHash = (Get-FileHash -LiteralPath $inputApk -Algorithm SHA256).Hash
$localApk = Join-Path $inputDir "DollarFix-original.apk"
if ($inputApk -ine $localApk) { Copy-Item -LiteralPath $inputApk -Destination $localApk -Force }
$localHash = (Get-FileHash -LiteralPath $localApk -Algorithm SHA256).Hash
if ($sourceHash -ne $localHash) { throw "Original APK copy hash mismatch" }

$python = ToolPath @("python.exe","python","py.exe","py")
if (-not $python) { throw "Python 3 is required for APK inventory" }
$pythonPrefix = @()
if ([IO.Path]::GetFileNameWithoutExtension($python) -eq "py") { $pythonPrefix = @("-3") }

$inventoryScript = Join-Path $reverseRoot "tools\inventory_apk.py"
$inventoryJson = Join-Path $reportDir "inventory.json"
$inventoryArgs = @() + $pythonPrefix + @(
    $inventoryScript,
    $localApk,
    "--output", $inventoryJson,
    "--extract-native", (Join-Path $workDir "native\apk")
)
$inventoryResult = RunRecorded $python $inventoryArgs "inventory.log"
if ($inventoryResult.exit_code -ne 0) {
    throw "Inventory failed; inspect reverse/reports/inventory.log"
}

$status = [ordered]@{
    source_apk = $inputApk
    original_sha256 = $localHash
    inventory = $inventoryResult
    optional_tools = [ordered]@{}
}

if ($QiruiZipPath) {
    $qiruiInput = (Resolve-Path -LiteralPath $QiruiZipPath).Path
    $qiruiLocal = Join-Path $inputDir "DollarFix_QIRUI_FULL.zip"
    if ($qiruiInput -ine $qiruiLocal) { Copy-Item -LiteralPath $qiruiInput -Destination $qiruiLocal -Force }
    $qiruiArgs = @() + $pythonPrefix + @(
        $inventoryScript,
        $qiruiLocal,
        "--output", (Join-Path $reportDir "qirui-inventory.json"),
        "--extract-native", (Join-Path $workDir "native\qirui")
    )
    $status.optional_tools.qirui_inventory = RunRecorded $python $qiruiArgs "qirui-inventory.log"
}

$jadx = ToolPath @("jadx.bat","jadx")
if ($jadx) {
    $status.optional_tools.jadx = RunRecorded $jadx @(
        "-d", (Join-Path $workDir "jadx"), $localApk
    ) "jadx.log"
} else { $status.optional_tools.jadx = @{ found = $false } }

$apktool = ToolPath @("apktool.bat","apktool")
if ($apktool) {
    $status.optional_tools.apktool = RunRecorded $apktool @(
        "d", "-f", "-o", (Join-Path $workDir "apktool"), $localApk
    ) "apktool.log"
} else { $status.optional_tools.apktool = @{ found = $false } }

$rea = ToolPath @("rea.cmd","rea")
if ($rea) {
    $status.optional_tools.rea_doctor = RunRecorded $rea @(
        "doctor","--json"
    ) "rea-doctor.json"
    $status.optional_tools.rea_providers = RunRecorded $rea @(
        "providers","--json"
    ) "rea-providers.json"
} else { $status.optional_tools.rea = @{ found = $false } }

$statusPath = Join-Path $reportDir "tool-status.json"
$status | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $statusPath -Encoding UTF8

$codex = ToolPath @("codex.cmd","codex")
if (-not $SkipCodex -and $codex) {
    $promptPath = Join-Path $reverseRoot "docs\CODEX_RE_TASK.md"
    $summaryPath = Join-Path $reportDir "codex-summary.md"
    Push-Location $repoRoot
    try {
        # Local Codex reads the prompt from stdin and has REA MCP if already registered.
        Get-Content -LiteralPath $promptPath -Raw | & $codex exec -C $repoRoot -o $summaryPath - 
        if ($LASTEXITCODE -ne 0) { Write-Warning "Codex exited with $LASTEXITCODE" }
    }
    finally { Pop-Location }
}
elseif (-not $SkipCodex) {
    Write-Warning "Codex CLI not found: only local static analysis was performed."
}

$finalHash = (Get-FileHash -LiteralPath $localApk -Algorithm SHA256).Hash
if ($finalHash -ne $localHash) { throw "Safety failure: original APK was modified" }
Write-Host "Original SHA256: $localHash"
Write-Host "Reports: $reportDir"
Write-Host "Local decompiled sources: $workDir"
Write-Host "No original APK was modified and no APK was uploaded."
