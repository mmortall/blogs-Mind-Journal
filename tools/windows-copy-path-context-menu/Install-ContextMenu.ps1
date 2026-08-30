[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$shellRoots = @(
    'Software\Classes\Directory\shell',
    'Software\Classes\*\shell'
)
$scriptPath = Join-Path $PSScriptRoot 'Copy-SelectedPath.ps1'

if (-not (Test-Path -LiteralPath $scriptPath -PathType Leaf)) {
    throw "Copy-SelectedPath.ps1 was not found at '$scriptPath'."
}

function Install-MenuItem {
    param(
        [Parameter(Mandatory)] [string] $ShellRoot,
        [Parameter(Mandatory)] [string] $Name,
        [Parameter(Mandatory)] [string] $Label,
        [Parameter(Mandatory)] [ValidateSet('Windows', 'Wsl')] [string] $Mode
    )

    $command = 'powershell.exe -NoLogo -NoProfile -NonInteractive -Sta -ExecutionPolicy Bypass -WindowStyle Hidden -File "{0}" -Mode {1} -Path "%1"' -f $scriptPath, $Mode
    $menuKeyPath = "$ShellRoot\$Name"
    $registry = [Microsoft.Win32.Registry]::CurrentUser
    $menuKey = $registry.CreateSubKey($menuKeyPath)

    try {
        $menuKey.SetValue('', $Label, [Microsoft.Win32.RegistryValueKind]::String)
        $menuKey.SetValue('MUIVerb', $Label, [Microsoft.Win32.RegistryValueKind]::String)
        $menuKey.SetValue('Icon', 'shell32.dll,261', [Microsoft.Win32.RegistryValueKind]::String)

        $commandKey = $menuKey.CreateSubKey('command')
        try {
            $commandKey.SetValue('', $command, [Microsoft.Win32.RegistryValueKind]::String)
        }
        finally {
            $commandKey.Close()
        }
    }
    finally {
        $menuKey.Close()
    }
}

foreach ($shellRoot in $shellRoots) {
    Install-MenuItem -ShellRoot $shellRoot -Name 'CopyPathAsWindows' -Label 'Copy path as Windows' -Mode Windows
    Install-MenuItem -ShellRoot $shellRoot -Name 'CopyPathAsWsl' -Label 'Copy path as WSL (Unix)' -Mode Wsl
}

Write-Host 'Context-menu items installed for the current Windows user.'
Write-Host 'The items apply to both directories and files.'
Write-Host 'Restart Explorer only if the new items do not appear immediately.'
