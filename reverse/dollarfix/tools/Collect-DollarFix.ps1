#Requires -Version 5.1
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$ApkPath,
    [string]$QiruiZipPath
)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$private = Join-Path $root "private"
$output = Join-Path $root "output"
New-Item -ItemType Directory -Force -Path $private, $output | Out-Null

function Copy-VerifiedInput {
    param([string]$Path, [string]$Name)
    $source = (Resolve-Path -LiteralPath $Path -ErrorAction Stop).Path
    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
        throw "Input is not a file: $source"
    }
    $destination = Join-Path $private $Name
    $sourceHash = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant()
    if (Test-Path -LiteralPath $destination) {
        $existingHash = (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($existingHash -ne $sourceHash) {
            throw "Existing private input differs: $destination. Review manually; nothing was overwritten."
        }
    } else {
        Copy-Item -LiteralPath $source -Destination $destination -ErrorAction Stop
    }
    $destinationHash = (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($destinationHash -ne $sourceHash) { throw "SHA-256 mismatch after copy: $Name" }
    return [pscustomobject]@{
        name = $Name
        original_path = $source
        private_copy = $destination
        sha256 = $destinationHash
        size_bytes = (Get-Item -LiteralPath $destination).Length
    }
}

$items = @()
$items += Copy-VerifiedInput -Path $ApkPath -Name "DollarFix.apk"
if ($QiruiZipPath) {
    $items += Copy-VerifiedInput -Path $QiruiZipPath -Name "QIRUI_FULL.zip"
}
$report = Join-Path $output "inputs.json"
$items | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $report -Encoding UTF8
Write-Host "Private inputs verified. Hash report: $report"
$items | Format-Table name, sha256, size_bytes -AutoSize
