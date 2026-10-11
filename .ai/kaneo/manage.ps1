param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$runtimeRoot = Join-Path $PSScriptRoot "runtime"

# REST credentials belong to each machine, never to Git.
foreach ($name in @("KANEO_API_KEY", "CF_ACCESS_CLIENT_ID", "CF_ACCESS_CLIENT_SECRET")) {
    if (-not [Environment]::GetEnvironmentVariable($name, "Process")) {
        $value = [Environment]::GetEnvironmentVariable($name, "User")
        if (-not $value) { $value = [Environment]::GetEnvironmentVariable($name, "Machine") }
        if ($value) { [Environment]::SetEnvironmentVariable($name, $value, "Process") }
    }
}

# Client uses only standard library; central checkout and local Kaneo are unnecessary.
$python = $env:KANEO_PYTHON
$pythonArgs = @()
if (-not $python) {
    foreach ($relative in @(".conda-env\python.exe", ".venv\Scripts\python.exe", ".venv/bin/python")) {
        $candidate = Join-Path $repoRoot $relative
        if (Test-Path -LiteralPath $candidate -PathType Leaf) { $python = $candidate; break }
    }
}
if (-not $python) {
    foreach ($name in @("py", "python3", "python")) {
        $command = Get-Command $name -ErrorAction SilentlyContinue
        if ($command) {
            $python = $command.Source
            if ($name -eq "py") { $pythonArgs = @("-3") }
            break
        }
    }
}
if (-not $python) { throw "Python 3.11+ required for bundled REST client. Set KANEO_PYTHON; no local Kaneo server is needed." }
& $python @pythonArgs -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)'
if ($LASTEXITCODE -ne 0) { throw "Bundled REST client requires Python 3.11+. Set KANEO_PYTHON to compatible interpreter." }

$previousPath = $env:PYTHONPATH
try {
    $env:PYTHONPATH = $runtimeRoot
    & $python @pythonArgs -m knowledge_router.kaneo_cli --repo-root $repoRoot @Arguments
    $resultCode = $LASTEXITCODE
} finally {
    $env:PYTHONPATH = $previousPath
}
exit $resultCode
