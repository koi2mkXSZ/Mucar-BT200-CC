# Export authored static-analysis reports for manual review, not for GitHub.
# No APK / DEX / ELF / GGP / original QIRUI binary is included.
[CmdletBinding()]
param(
    [string]$ProjectRoot = "C:\REA\Project\DollarFix",
    [string]$ResearchRepository = "",
    [string]$SnapshotName = "DollarFix-installed-20261122_112739"
)
$ErrorActionPreference = "Stop"
if (-not $ResearchRepository) {
    $ResearchRepository = Join-Path $ProjectRoot "research-tooling"
}
$docsDir = Join-Path $ResearchRepository "reverse\docs"
$reportDir = Join-Path $ProjectRoot ("reverse\reports\" + $SnapshotName)

$documentNames = @(
    "APK_ARCHITECTURE.md",
    "BLUETOOTH_DPU.md",
    "DELPHI_DATA_STREAM.md",
    "PATCH_PROPOSAL.md"
)
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$staging = Join-Path $reportDir ("share-review-" + $stamp)
New-Item -ItemType Directory -Path $staging -Force | Out-Null

foreach ($name in $documentNames) {
    $source = Join-Path $docsDir $name
    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
        throw "Missing Codex report: $source"
    }
    Copy-Item -LiteralPath $source -Destination (Join-Path $staging $name)
}
$todo = Join-Path $ResearchRepository "TODO.md"
if (Test-Path -LiteralPath $todo -PathType Leaf) {
    Copy-Item -LiteralPath $todo -Destination (Join-Path $staging "TODO.md")
}

$jadxLog = Join-Path $reportDir "jadx-base.log"
if (Test-Path -LiteralPath $jadxLog -PathType Leaf) {
    # Restrict diagnostic excerpt to last 200 lines; never include full decompiled code.
    Get-Content -LiteralPath $jadxLog -Tail 200 |
      Set-Content -LiteralPath (Join-Path $staging "jadx-base-last200.txt") -Encoding UTF8
}
$runStatus = Join-Path $reportDir "tool-status.json"
if (Test-Path -LiteralPath $runStatus -PathType Leaf) {
    Copy-Item -LiteralPath $runStatus -Destination (Join-Path $staging "tool-status.json")
}

$zip = Join-Path $reportDir ("DollarFix-review-" + $stamp + ".zip")
Compress-Archive -Path (Join-Path $staging "*") -DestinationPath $zip -CompressionLevel Optimal
Write-Host "Review ZIP ready: $zip"
Write-Host "Only authored reports, TODO, tool status, and last 200 JADX log lines are included."
Write-Host "Review document text and diagnostic log for personal paths/device IDs before sharing."
Write-Host "No APK, QIRUI, native library or complete decompiled sources are included."
