function BuildYasm {
    Write-Host "Building YASM"
    Push-Location "./yasm"
    cmake.exe -S ./ -B ./build
    cmake.exe --build ./build
    Pop-Location
}

function BuildProject {
    Write-Host "Building project"
    if (-not $env:__devinit_path)
    {
        throw "Not running in Visual Studio Developer Powershell!"
    }
    cmake.exe --toolchain ./cmake/Toolchain.cmake -G Ninja -B ./build
    cmake.exe --build ./build
    cmake.exe --install ./build --prefix artifacts
}

function CopyFiles {
    param (
        [string]
        $Artifacts,
        [string]
        $BootDriveFolder
    )

    $EfiFolder = Join-Path $BootDriveFolder "efi"
    New-Item $EfiFolder -ItemType Directory -Force | Out-Null
    $BootFolder = Join-Path $EfiFolder "boot"
    $OsFolder = Join-Path $EfiFolder "os"
    New-Item $BootFolder -ItemType Directory -Force | Out-Null
    New-Item $OsFolder -ItemType Directory -Force | Out-Null

    Copy-Item "$Artifacts\bin\HAL9000.bin" -Destination $OsFolder
    Copy-Item "$Artifacts\bin\BOOTX64.EFI" -Destination $BootFolder
}

if (Test-Path "./tools/bin/vsyasm.exe")
{
    Write-Host "Found vsyasm.exe"
}
else
{
    BuildYasm
    if (-not (Test-Path "./tools/bin/vsyasm.exe"))
    {
        throw "Failed to build yasm"
    }
}

BuildProject
CopyFiles "./artifacts" "./bootdrive"