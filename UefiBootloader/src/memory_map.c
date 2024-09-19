#include <bootloader/memory_map.h>

#include <bootloader/memory.h>

UINTN 
GetMemoryMap(
    EFI_SYSTEM_TABLE *ST,
    MEMORY_MAP *MemoryMap
    )
{
    UINTN memoryMapSize = PAGE_SIZE;
    EFI_MEMORY_DESCRIPTOR *memoryMapPointer = (EFI_MEMORY_DESCRIPTOR *) MemoryMap->MapAddress;
    if (!memoryMapPointer)
        memoryMapPointer = AllocateZeroedPages(ST, EfiLoaderData, 1);
    UINTN mapKey;
    UINTN descriptorSize;
    UINT32 descriptorVersion;
    UINT32 pageCount = 1;

    EFI_STATUS status;
    while ((status = ST->BootServices->GetMemoryMap(&memoryMapSize, memoryMapPointer, 
            &mapKey, &descriptorSize, &descriptorVersion)) == EFI_BUFFER_TOO_SMALL) 
    {
        FreePages(ST, (UINT64) memoryMapPointer, pageCount);
        memoryMapSize += PAGE_SIZE;
        pageCount++;
        memoryMapPointer = AllocateZeroedPages(ST, EfiLoaderData, pageCount);
    }

    if (status != EFI_SUCCESS || descriptorVersion != EFI_MEMORY_DESCRIPTOR_VERSION)
        return UINT64_MAX;

    MemoryMap->DescriptorSize = descriptorSize;
    MemoryMap->Count = memoryMapSize / descriptorSize;
    MemoryMap->MapAddress = (UINT64) memoryMapPointer;
    
    return mapKey;
}
