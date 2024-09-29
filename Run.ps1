[CmdletBinding()]
param (
    [ValidateScript({ Test-Path -PathType Container $_ })]
    [Parameter()]
    [System.IO.DirectoryInfo]
    $BootDriveFolder = "./bootdrive",
    [ValidateScript({ Test-Path -PathType Container $_ })]
    [Parameter()]
    [System.IO.DirectoryInfo]
    $OvmfFolder = "./ovmf-x64",
    [Parameter()]
    [System.IO.FileInfo]
    $SerialOutFile = "./serial1.log",
    [ValidateScript({ Test-Path -PathType Leaf $_ })]
    [Parameter()]
    [System.IO.FileInfo]
    $DiskFile,
    [switch]
    $Monitor,
    [switch]
    $GdbServer
)

if (-not (Test-Path -PathType Leaf "$OvmfFolder/OVMF-pure-efi.fd")) {
    throw "Missing OVMF file"
}

if (-not (Test-Path -PathType Leaf "$BootDriveFolder/efi/os/HAL9000.bin")) {
    throw "Missing file '$BootDriveFolder/efi/os/HAL9000.bin'"
}

if (-not (Test-Path -PathType Leaf "$BootDriveFolder/efi/boot/BOOTX64.EFI")) {
    throw "Missing file '$BootDriveFolder/efi/boot/BOOTX64.EFI'"
}

$Options = @{
    "cpu"     = "max"
    "machine" = "q35"
    "L"       = $OvmfFolder
    "bios"    = 'OVMF-pure-efi.fd'
    "m"       = "4G"
    "smp"     = 4
    "chardev" = "file,id=char0,path=$SerialOutFile"
    "serial"  = "chardev:char0"
    "device"  = [System.Collections.ArrayList]@("e1000e")
    "drive"   = [System.Collections.ArrayList]@("file=fat:rw:$BootDriveFolder,format=raw")
}

$Flags = [System.Collections.ArrayList]@()

if ($Monitor) {
    $Options["monitor"] = "stdio"
}

if ($GdbServer)
{
    $Flags.Add("s") | Out-Null;
    $Flags.Add("S") | Out-Null;
}

if ($DiskFile -and (Test-Path -PathType Leaf $DiskFile)) {
    $Options["device"].add("piix3-ide,id=ide") | Out-Null;
    $Options["device"].add("ide-hd,drive=disk,bus=ide.0") | Out-Null;
    $Options["drive"].add("id=disk,file=$DiskFile,if=none") | Out-Null;
}

$FlattenedOptions = @($Options.Keys | ForEach-Object { 
        $Value = $Options[$_]
        if ($Value.GetType() -eq [string]) {
            "-$_"; $Value
        }
        else {
            $Key = $_;
            $Value | ForEach-Object { "-$Key"; $_ }
        }
    })

$FlattenedFlags = @($Flags | ForEach-Object { "-$_" })

Write-Host "qemu-system-x86_64.exe" @FlattenedOptions @FlattenedFlags

qemu-system-x86_64.exe @FlattenedOptions @FlattenedFlags