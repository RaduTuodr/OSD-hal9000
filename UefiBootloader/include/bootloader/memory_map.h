#pragma once

#include <Uefi.h>

#define UINT64_MAX 18446744073709551615ULL

typedef struct 
{
    UINT64 DescriptorSize;
    UINT64 Count;
    UINT64 MapAddress;
} MEMORY_MAP;

UINTN 
GetMemoryMap(
    EFI_SYSTEM_TABLE *ST,
    MEMORY_MAP *MemoryMap
    );
