Set-StrictMode -Version Latest

function Normalize-WindowsInputPath {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [AllowEmptyString()]
        [string] $Path
    )

    $value = $Path

    if ($value.Length -ge 2 -and $value.StartsWith('"') -and $value.EndsWith('"')) {
        $value = $value.Substring(1, $value.Length - 2)
    }

    if ([string]::IsNullOrWhiteSpace($value)) {
        throw 'The selected path is empty.'
    }

    $value = $value.Replace('/', '\')

    if ($value.StartsWith('\\?\UNC\', [System.StringComparison]::OrdinalIgnoreCase)) {
        $value = '\\' + $value.Substring(8)
    }
    elseif ($value.StartsWith('\\?\', [System.StringComparison]::OrdinalIgnoreCase)) {
        $value = $value.Substring(4)
    }

    return $value
}

function ConvertTo-WindowsPath {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string] $Path
    )

    return (Normalize-WindowsInputPath -Path $Path)
}

function ConvertTo-WslPath {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string] $Path
    )

    $windowsPath = Normalize-WindowsInputPath -Path $Path

    if ($windowsPath -match '^\\\\wsl(?:\.localhost|\$)\\(?<distro>[^\\]+)(?:\\(?<wslPath>.*))?$') {
        $wslPath = $Matches['wslPath']

        if ([string]::IsNullOrEmpty($wslPath)) {
            return '/'
        }

        return '/' + $wslPath.TrimStart('\').Replace('\', '/')
    }

    if ($windowsPath -match '^(?<drive>[A-Za-z]):(?:\\(?<drivePath>.*))?$') {
        $result = '/mnt/' + $Matches['drive'].ToLowerInvariant()
        $drivePath = $Matches['drivePath']

        if (-not [string]::IsNullOrEmpty($drivePath)) {
            $result += '/' + $drivePath.TrimStart('\').Replace('\', '/')
        }

        return $result
    }

    if ($windowsPath -match '^\\\\(?<server>[^\\]+)\\(?<share>[^\\]+)(?:\\(?<uncPath>.*))?$') {
        $result = '//' + $Matches['server'] + '/' + $Matches['share']
        $uncPath = $Matches['uncPath']

        if (-not [string]::IsNullOrEmpty($uncPath)) {
            $result += '/' + $uncPath.TrimStart('\').Replace('\', '/')
        }

        return $result
    }

    throw "Unsupported Windows path '$Path'. Expected a drive path or a WSL UNC path."
}

Export-ModuleMember -Function ConvertTo-WindowsPath, ConvertTo-WslPath
