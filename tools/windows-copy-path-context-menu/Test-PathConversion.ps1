[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Import-Module (Join-Path $PSScriptRoot 'PathConversion.psm1') -Force

function Assert-Equal {
    param(
        [Parameter(Mandatory)] [string] $Expected,
        [Parameter(Mandatory)] [string] $Actual,
        [Parameter(Mandatory)] [string] $Case
    )

    if ($Expected -cne $Actual) {
        throw "[$Case] Expected '$Expected', got '$Actual'."
    }
}

$windowsCases = @(
    @{ Name = 'Windows folder'; Input = 'C:\Users\Sergey\Projects'; Expected = 'C:\Users\Sergey\Projects' },
    @{ Name = 'Windows symlink path'; Input = 'D:\Links\UbuntuHome'; Expected = 'D:\Links\UbuntuHome' },
    @{ Name = 'WSL localhost path'; Input = '\\wsl.localhost\Ubuntu-24.04\home'; Expected = '\\wsl.localhost\Ubuntu-24.04\home' },
    @{ Name = 'Legacy WSL path'; Input = '\\wsl$\Ubuntu-24.04\home'; Expected = '\\wsl$\Ubuntu-24.04\home' }
)

foreach ($case in $windowsCases) {
    Assert-Equal -Case $case.Name -Expected $case.Expected -Actual (ConvertTo-WindowsPath -Path $case.Input)
}

$wslCases = @(
    @{ Name = 'Windows folder to WSL'; Input = 'C:\Users\Sergey\Projects'; Expected = '/mnt/c/Users/Sergey/Projects' },
    @{ Name = 'Windows symlink path to WSL'; Input = 'D:\Links\UbuntuHome'; Expected = '/mnt/d/Links/UbuntuHome' },
    @{ Name = 'WSL localhost home'; Input = '\\wsl.localhost\Ubuntu-24.04\home'; Expected = '/home' },
    @{ Name = 'WSL localhost nested path'; Input = '\\wsl.localhost\Ubuntu-24.04\home\sergey\blog'; Expected = '/home/sergey/blog' },
    @{ Name = 'WSL distro root'; Input = '\\wsl.localhost\Ubuntu-24.04'; Expected = '/' },
    @{ Name = 'Legacy WSL nested path'; Input = '\\wsl$\Ubuntu-24.04\var\www'; Expected = '/var/www' },
    @{ Name = 'Extended Windows path'; Input = '\\?\C:\Users\Sergey'; Expected = '/mnt/c/Users/Sergey' },
    @{ Name = 'Generic UNC path'; Input = '\\server\share\folder'; Expected = '//server/share/folder' }
)

foreach ($case in $wslCases) {
    Assert-Equal -Case $case.Name -Expected $case.Expected -Actual (ConvertTo-WslPath -Path $case.Input)
}

Write-Host ("Passed {0} path-conversion cases." -f ($windowsCases.Count + $wslCases.Count))
