# Copy selected path for Windows and WSL

This is a small, per-user Windows Explorer context-menu tool. It adds two menu items for selected files and directories:

- Copy path as Windows - copies the selected path using Windows separators.
- Copy path as WSL (Unix) - converts local drive paths to /mnt/<drive>/... and WSL UNC paths to /....

Examples:

```text
\\wsl.localhost\Ubuntu-24.04\home  ->  \\wsl.localhost\Ubuntu-24.04\home  (Windows)
\\wsl.localhost\Ubuntu-24.04\home  ->  /home                              (WSL)
C:\Users\Sergey\Projects           ->  C:\Users\Sergey\Projects           (Windows)
C:\Users\Sergey\Projects           ->  /mnt/c/Users/Sergey/Projects       (WSL)
```

## Install

Run Install-ContextMenu.ps1 from this directory in Windows PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\Install-ContextMenu.ps1
```

The registration is stored under HKCU\Software\Classes, so administrator rights are not required. The menu command points to this directory; keep it in place after installation.

The scripts intentionally do not call Resolve-Path. A symlink is therefore copied as the path selected in Explorer, rather than being replaced with its target path.

## Uninstall

```powershell
.\Uninstall-ContextMenu.ps1
```

## Test conversion logic

```powershell
.\Test-PathConversion.ps1
```

The context menu is registered for Directory and *, which covers ordinary folders, files, symlinks, and items exposed by Explorer through \\wsl.localhost or \\wsl$.
