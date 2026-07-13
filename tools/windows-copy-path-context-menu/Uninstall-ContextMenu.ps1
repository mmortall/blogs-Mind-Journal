[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$shellRoots = @(
    'Software\Classes\Directory\shell',
    'Software\Classes\*\shell'
)

$registry = [Microsoft.Win32.Registry]::CurrentUser
foreach ($shellRoot in $shellRoots) {
    foreach ($name in @('CopyPathAsWindows', 'CopyPathAsWsl')) {
        $menuKeyPath = "$shellRoot\$name"
        $existingKey = $registry.OpenSubKey($menuKeyPath)

        if ($null -ne $existingKey) {
            $existingKey.Close()
            $registry.DeleteSubKeyTree($menuKeyPath, $false)
        }
    }
}

Write-Host 'Context-menu items removed for the current Windows user.'
