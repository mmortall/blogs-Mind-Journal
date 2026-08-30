param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$configuredHostRoot = $env:KNOWLEDGE_ROOT_PLATFORM
if (-not $configuredHostRoot) {
    throw "Global Knowledge Platform runtime is unavailable. Set KNOWLEDGE_ROOT_PLATFORM to its checkout path."
}
$hostRoot = (Resolve-Path -LiteralPath $configuredHostRoot).Path
$python = Join-Path $hostRoot ".conda-env\python.exe"

if (-not (Test-Path -LiteralPath $python)) {
    throw "Global Knowledge Platform Miniconda environment is missing: $python"
}

& $python -m knowledge_router.kaneo_cli --repo-root $repoRoot @Arguments
exit $LASTEXITCODE
