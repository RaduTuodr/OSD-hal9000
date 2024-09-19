#include <Uefi.h>

#include <bootloader/loader.h>

// Loader expects kernel in \EFI\OS
// Loader expects modules in \EFI\MODULES
// Max Boot Module count is 128
// Max Boot Module name length 32
// We return closest resolution to the requested one,
// if no match return a larger one, i.e more width and height

EFI_STATUS 
EfiEntry(
    EFI_HANDLE ImageHandle,
    EFI_SYSTEM_TABLE *SystemTable
    )
{
    LoaderPreInit(SystemTable, ImageHandle);

    LoaderInit();
    
    LoadOperatingSystem();

    StartOperatingSystem();

    return EFI_SUCCESS;
}
