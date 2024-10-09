#pragma once

#include <Uefi.h>

#include <Bootloader/types.h>

#pragma pack(push, 1)

#define HAL_BOOT_HEADER_MAGIC 0xFEE1DEAD
#define HAL_BOOT_MAGIC 0xC00010FF 
#define CRC32_REVERSED_POLYNOMIAL 0xEDB88320
#define BIOS_MAX_SERIAL_PORTS 4

typedef struct
{
    UINT32 Magic;
    UINT32 Crc32; 
    UINT32 LoadOffset;
    UINT32 PreferredLoadAddress; 
    UINT32 EntryAddress;
    UINT32 FramebufferWidth;
    UINT32 FramebufferHeight;
} HAL_BOOT_HEADER;

typedef struct
{
    UINT32 Magic;
    UINT32 Crc32;

    // Kernel information
    UINT32 KernelBaseAddress;
    UINT32 KernelSize;
     
    // ACPI RSDP
    UINT64 AcpiRsdp;

    // HAL Memory Map
    HAL_MEMORY_MAP MemoryMap;

    // Boot modules
    UINT32 BootModuleCount;
    // HAL_BOOT_MODULE*
    UINT32 BootModules;

    // HAL_FRAMEBUFFER
    HAL_FRAMEBUFFER Framebuffer;

    // EFI_RUNTIME_SERVICES
    UINT64 EfiRuntimeServicesVirtualAddress;
    UINT64 EfiRuntimeServicesSize;
    EFI_RUNTIME_SERVICES EfiRuntimeServices;

    // Serial Ports
    UINT16 SerialPorts[BIOS_MAX_SERIAL_PORTS];
    
    // Virtual address information
    UINT64 VirtualToPhysicalOffset;
    UINT64 VirtualDisplayAddress;

} HAL_BOOT_INFORMATION;

#pragma pack(pop)
