[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateSet('Windows', 'Wsl')]
    [string] $Mode,

    [Parameter(Mandatory, Position = 0)]
    [string] $Path
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Import-Module (Join-Path $PSScriptRoot 'PathConversion.psm1') -Force

try {
    $value = if ($Mode -eq 'Windows') {
        ConvertTo-WindowsPath -Path $Path
    }
    else {
        ConvertTo-WslPath -Path $Path
    }

    Add-Type -AssemblyName System.Windows.Forms
    [System.Windows.Forms.Clipboard]::SetText($value)
}
catch {
    try {
        Add-Type -AssemblyName System.Windows.Forms
        [System.Windows.Forms.MessageBox]::Show(
            $_.Exception.Message,
            'Copy selected path',
            [System.Windows.Forms.MessageBoxButtons]::OK,
            [System.Windows.Forms.MessageBoxIcon]::Error
        ) | Out-Null
    }
    catch {
        Write-Error $_
    }

    exit 1
}
