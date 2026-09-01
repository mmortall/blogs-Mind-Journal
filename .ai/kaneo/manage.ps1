param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$hostRoot = if ($env:KNOWLEDGE_ROOT_PLATFORM) {
    (Resolve-Path -LiteralPath $env:KNOWLEDGE_ROOT_PLATFORM).Path
} else {
    "C:\Projects\all-knowledge-platform"
}
$python = Join-Path $hostRoot ".conda-env\python.exe"

if (-not (Test-Path -LiteralPath $python)) {
    throw "Global Knowledge Platform Miniconda environment is missing: $python"
}

& $python -m knowledge_router.kaneo_cli --repo-root $repoRoot @Arguments
exit $LASTEXITCODE
