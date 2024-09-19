#include <bootloader/loader.h>

#include <bootloader/acpi.h>
#include <bootloader/console.h>
#include <bootloader/filesystem.h>
#include <bootloader/graphics.h>
#include <bootloader/memory.h>
#include <bootloader/memory_map.h>
#include <bootloader/multiboot.h>

#pragma pack(push, 1)

typedef struct
{
    UINT64 Null;
    UINT64 Code;
    UINT64 Data;
} _GDT;

typedef struct
{
    UINT16 Limit;
    UINT32 Address;
} _GDT_DESCRIPTOR;

typedef struct
{
    UINT16 Limit;
    UINT64 Address;
} _GDT_DESCRIPTOR_64;

typedef struct
{
    UINT64 JumpAddress;
    UINT32 JumpAddressPm;
    _GDT_DESCRIPTOR *GdtDescriptor;
    _GDT_DESCRIPTOR_64 *GdtDescriptor64;
} _TRANSITION;

#pragma pack(pop)

typedef void (*StartOS) (UINT64 EntryAddress, UINT64 BootInfo, UINT64 Transition);

typedef struct
{
    EFI_SYSTEM_TABLE *ST;
    EFI_HANDLE ImageHandle;
    EFI_FILE_HANDLE RootDirectory; 
    EFI_FILE_HANDLE OsBinary; 
    UINT64 MultibootHeaderOffset;
    MULTIBOOT_HEADER MultibootHeader;
    UINT8 AlignBootModules;
    UINT8 ProvideMemoryMap;
    UINT8 ProvideVideoInformation;
    UINT64 OsTextOffset;
    UINT64 OsPageCount;
    UINT32 BootModuleCount;
    UINT32 BootModuleAddress;
    StartOS StartOsRoutine;
    UINT64 AcpiRsdp;
    EFI_GRAPHICS_OUTPUT_PROTOCOL *GOP;
    UINT32 GopModeIndex;
    FRAMEBUFFER Framebuffer;
    UINTN MemoryMapKey;
    MEMORY_MAP MemoryMap;
    UINT32 MemoryMapPointer;
    UINT32 MemoryMapSize;
    MULTIBOOT_INFORMATION BootInfo;
} _LOADER;

static _LOADER gLoader;
static char loaderName[] = "UEFI Loader";
static UINT8 MemoryMapMemory[SIZE_16KB]; 
static UINT8 BootModulesStringPool[SIZE_4KB];
static MULTIBOOT_BOOT_MODULE BootModules[128];

extern char __start_os[];
extern char __start_os_bits32[];
extern char __start_os_pm[];

__declspec(align(8)) static _GDT gdt = { .Null = 0x0, .Code = 0x00CF9A000000FFFF, .Data = 0x00CF92000000FFFF }; 
__declspec(align(8)) static _GDT_DESCRIPTOR gdtDescriptor;
__declspec(align(8)) static _GDT_DESCRIPTOR_64 gdtDescriptor64;
static _TRANSITION transition;

static void
_Die(
    CHAR16 *Message
    )
{
    PrintString(gLoader.ST, EFI_RED, Message);
    WaitForKeyPress(gLoader.ST);
    gLoader.ST->BootServices->Exit(gLoader.ImageHandle, EFI_LOAD_ERROR, 0, NULL);
}

void
LoaderPreInit(
    EFI_SYSTEM_TABLE *SystemTable,
    EFI_HANDLE ImageHandle
    )
{
    gLoader.ST = SystemTable;
    gLoader.ImageHandle = ImageHandle; 

    gLoader.ST->BootServices->SetWatchdogTimer(0, 0, 0, 0);
    PrepareConsole(gLoader.ST);
    ClearScreen(gLoader.ST);

    PrintString(gLoader.ST, EFI_GREEN, L"Loader preinitialized\r\n");
}

void
LoaderInit(
    void
    )
{
    gLoader.RootDirectory = GetRootDirectory(gLoader.ST, gLoader.ImageHandle);
    if (!gLoader.RootDirectory)
        _Die(L"Failed to open root directory\r\n");
    PrintString(gLoader.ST, EFI_GREEN, L"Loader initialized\r\n");
}

static void
_SearchForOperatingSystem(
    void
    )
{
    static CHAR16 osFilename[512] = L"\\EFI\\OS\\";

    EFI_STATUS status;
    EFI_FILE_INFO **dirEntries;
    UINT64 dirCount;
    
    status = ListDirectory(gLoader.ST,
                           gLoader.RootDirectory,
                           osFilename,
                           &dirEntries,
                           &dirCount);

    if (EFI_ERROR(status))
        _Die(L"Failed to list \\EFI\\OS\\\r\n");

    if (dirCount < 3 || (dirEntries[2]->Attribute & EFI_FILE_DIRECTORY))
        _Die(L"No Operating System found\r\n");

    // First two entries are . and .. in a directory
    EFI_FILE_INFO *osFileInfo = dirEntries[2];
    // See EFI_FILE_INFO struct
    UINT64 filenameLength = osFileInfo->Size - (4 * sizeof(UINT64) + 3 * sizeof(EFI_TIME));
    CopyMemory(&osFilename[8], &(osFileInfo->FileName), filenameLength);

    status = OpenFileForRead(gLoader.RootDirectory, osFilename, &(gLoader.OsBinary));
    if (EFI_ERROR(status))
        _Die(L"Could not open Operating System image\r\n");

    for (UINT64 i = 0;i < dirCount; i++)
        FreeFromPool(gLoader.ST, dirEntries[i]);
    FreeFromPool(gLoader.ST, dirEntries);

    PrintString(gLoader.ST, EFI_LIGHTGRAY, L"Found Operating System Image at ");
    PrintString(gLoader.ST, EFI_LIGHTGRAY, osFilename);
    PrintString(gLoader.ST, EFI_LIGHTGRAY, L"\r\n");
}

static void
_DumpMultibootHeader(
    void)
{
    PrintIntegerWithName(gLoader.ST, EFI_LIGHTGRAY,
                         L"Offset", gLoader.MultibootHeaderOffset);
    PrintIntegerWithName(gLoader.ST, EFI_LIGHTGRAY,
                         L"Magic", gLoader.MultibootHeader.Magic);
    PrintIntegerWithName(gLoader.ST, EFI_LIGHTGRAY,
                         L"Flags", gLoader.MultibootHeader.Flags);
    PrintIntegerWithName(gLoader.ST, EFI_LIGHTGRAY,
                         L"Checksum", gLoader.MultibootHeader.Checksum);
    PrintIntegerWithName(gLoader.ST, EFI_LIGHTGRAY,
                         L"HeaderAddress", gLoader.MultibootHeader.HeaderAddress);
    PrintIntegerWithName(gLoader.ST, EFI_LIGHTGRAY,
                         L"LoadAddress", gLoader.MultibootHeader.LoadAddress);
    PrintIntegerWithName(gLoader.ST, EFI_LIGHTGRAY,
                         L"LoadEndAddress", gLoader.MultibootHeader.LoadEndAddress);
    PrintIntegerWithName(gLoader.ST, EFI_LIGHTGRAY,
                         L"BssEndAddress", gLoader.MultibootHeader.BssEndAddress);
    PrintIntegerWithName(gLoader.ST, EFI_LIGHTGRAY,
                         L"EntryAddress", gLoader.MultibootHeader.EntryAddress);
    PrintIntegerWithName(gLoader.ST, EFI_LIGHTGRAY,
                         L"ModeType", gLoader.MultibootHeader.ModeType);
    PrintIntegerWithName(gLoader.ST, EFI_LIGHTGRAY,
                         L"Width", gLoader.MultibootHeader.Width);
    PrintIntegerWithName(gLoader.ST, EFI_LIGHTGRAY,
                         L"Height", gLoader.MultibootHeader.Height);
    PrintIntegerWithName(gLoader.ST, EFI_LIGHTGRAY,
                         L"Depth", gLoader.MultibootHeader.Depth);
}

static void
_SearchForMultibootHeader(
    void
    )
{
    EFI_STATUS status;

    // Search for Multiboot Header in the first 8 KB
    UINT8 *buffer = AllocateFromPool(gLoader.ST, SIZE_8KB);
    UINT64 bufferSize = SIZE_8KB;
    SetMemory(buffer, 0, SIZE_8KB);
    status = gLoader.OsBinary->Read(gLoader.OsBinary, &bufferSize, buffer); 
    if (EFI_ERROR(status))
        _Die(L"Failed to read from the image\r\n");

    MULTIBOOT_HEADER *header;
    UINT8 *pos = (UINT8 *) buffer;
    UINT32 magic = MULTIBOOT_HEADER_MAGIC;
    UINT8 found = 0;
    while (pos < buffer + SIZE_8KB)
    {
        header = (MULTIBOOT_HEADER *) pos;
        if (MemoryEquals(&(header->Magic), &magic, sizeof(UINT32)))
        {
            found = 1;
            break;
        }
        pos++;
    }
    if (!found)
        _Die(L"Multiboot header not found\r\n");

    gLoader.MultibootHeaderOffset = ((UINT8 *) (header)) - buffer;
    CopyMemory(&(gLoader.MultibootHeader), header, sizeof(MULTIBOOT_HEADER));
    FreeFromPool(gLoader.ST, buffer);

    UINT32 sum = gLoader.MultibootHeader.Magic +
                 gLoader.MultibootHeader.Flags +
                 gLoader.MultibootHeader.Checksum;
    if (sum)
        _Die(L"Multiboot Checksum is invalid");
}

static void
_ParseMultibootHeaderInfo(
    void
    )
{
    MULTIBOOT_HEADER *header = &(gLoader.MultibootHeader);

    if (!(header->Flags & MULTIBOOT_FLAGS_LOAD_INFO))
        _Die(L"Cannot load Operating System, please provide flags bit 16");

    if (header->Flags & MULTIBOOT_FLAGS_MODULE_PAGE_ALIGN)
        gLoader.AlignBootModules = 1;
    else
        gLoader.AlignBootModules = 0;
    
    if (header->Flags & MULTIBOOT_FLAGS_MEMORY_MAP)
        gLoader.ProvideMemoryMap = 1;
    else
        gLoader.ProvideMemoryMap = 0;
    
    if (header->Flags & MULTIBOOT_FLAGS_VIDEO_MODE)
        gLoader.ProvideVideoInformation = 1;
    else
        gLoader.ProvideVideoInformation = 0;
    
    gLoader.OsTextOffset = gLoader.MultibootHeaderOffset - (header->HeaderAddress - header->LoadAddress);
}

static void
_CopyOperatingSystem(
    void
    )
{
    EFI_STATUS status;

    UINT64 pageCount = 0;
    UINT64 address = LoadFileToMemoryAt(gLoader.ST,
                                gLoader.OsBinary,
                                gLoader.OsTextOffset,
                                gLoader.MultibootHeader.LoadAddress,
                                &pageCount);
    if (!address)
        _Die(L"Failed to load Operating System at specified address");
    
    gLoader.OsPageCount = pageCount;
    CloseFileHandle(gLoader.OsBinary);
}

static void
_LoadBootModules(
    void
    )
{
    static CHAR16 osFilename[512] = L"\\EFI\\MODULES\\";

    EFI_STATUS status;
    EFI_FILE_INFO **dirEntries;
    UINT64 dirCount;
    
    status = ListDirectory(gLoader.ST,
                           gLoader.RootDirectory,
                           osFilename,
                           &dirEntries,
                           &dirCount);
    if (EFI_ERROR(status))
        return;

    UINT8 *stringPoolPos = BootModulesStringPool;
    // First two are . and ..
    UINT64 count = dirCount > 130 ? 130 : dirCount;
    for (UINT64 i = 2; i < count; i++)
    {
        PrintString(gLoader.ST, EFI_LIGHTGRAY, L"Loading module: ");
        PrintString(gLoader.ST, EFI_LIGHTGRAY, dirEntries[i]->FileName);
        PrintString(gLoader.ST, EFI_LIGHTGRAY, L"\r\n");

        UINT64 filenameLength = dirEntries[i]->Size - (4 * sizeof(UINT64) + 3 * sizeof(EFI_TIME));
        CopyMemory(&osFilename[13], dirEntries[i]->FileName, filenameLength);
        EFI_FILE_HANDLE fileHandle;
        if(EFI_ERROR(OpenFileForRead(gLoader.RootDirectory, osFilename, &fileHandle)))
            _Die(L"Could not open for read Boot Module\r\n");
        UINT64 pageCount;
        UINT64 address = LoadFileToMemory(gLoader.ST, fileHandle, 0, &pageCount);
        if (!address)
            _Die(L"Could not load Boot Module\r\n");
        CloseFileHandle(fileHandle);

        filenameLength /= sizeof(CHAR16);
        CopyWcharAsChar(stringPoolPos, dirEntries[i]->FileName, filenameLength);
        BootModules[i - 2].ModuleStart = address;
        BootModules[i - 2].ModuleEnd = address + pageCount * PAGE_SIZE;
        // Do not do this
        BootModules[i - 2].StringAddr = (UINT32) ((UINT64) stringPoolPos);
        BootModules[i - 2].Reserved = 0;
        stringPoolPos += filenameLength;
        
        PrintString(gLoader.ST, EFI_LIGHTGRAY, L"Loaded module ");
        PrintString(gLoader.ST, EFI_LIGHTGRAY, dirEntries[i]->FileName);
        PrintString(gLoader.ST, EFI_LIGHTGRAY, L" at address ");
        PrintIntegerInHexadecimal(gLoader.ST, EFI_LIGHTGRAY, address);
        PrintString(gLoader.ST, EFI_LIGHTGRAY, L"\r\n");
    }

    for (UINT64 i = 0;i < dirCount; i++)
        FreeFromPool(gLoader.ST, dirEntries[i]);
    FreeFromPool(gLoader.ST, dirEntries);

    if (count)
    {
        // Do not do this
        gLoader.BootModuleCount = (UINT32) (count - 2);
        gLoader.BootModuleAddress = (UINT32) ((UINT64) BootModules);
    }
}

static void
_PrepareAssembly(
    void
    )
{
    gdtDescriptor.Limit = 23;
    gdtDescriptor.Address = (UINT32) ((UINT64) &gdt);
    
    gdtDescriptor64.Limit = 23;
    gdtDescriptor64.Address = (UINT64) &gdt;

    transition.JumpAddress = (UINT64) &(__start_os_bits32[0]);
    transition.JumpAddressPm = (UINT32) ((UINT64) &(__start_os_pm[0]));
    transition.GdtDescriptor = &gdtDescriptor;
    transition.GdtDescriptor64 = &gdtDescriptor64;

    gLoader.StartOsRoutine = (StartOS) &(__start_os[0]);
}

static void
_DumpFramebuffer(
    void
    )
{
    FRAMEBUFFER *buff = (FRAMEBUFFER *) &(gLoader.Framebuffer);
    PrintIntegerWithName(gLoader.ST, EFI_LIGHTGRAY, L"Address", buff->Address);
    PrintIntegerWithName(gLoader.ST, EFI_LIGHTGRAY, L"Pitch", buff->Pitch);
    PrintIntegerWithName(gLoader.ST, EFI_LIGHTGRAY, L"Width", buff->Width);
    PrintIntegerWithName(gLoader.ST, EFI_LIGHTGRAY, L"Height", buff->Height);
    PrintIntegerWithName(gLoader.ST, EFI_LIGHTGRAY, L"BitsPerPixel", buff->BitsPerPixel);
    PrintIntegerWithName(gLoader.ST, EFI_LIGHTGRAY, L"Type", buff->Type);
    PrintIntegerWithName(gLoader.ST, EFI_LIGHTGRAY, L"RedFieldPosition", buff->RedFieldPosition);
    PrintIntegerWithName(gLoader.ST, EFI_LIGHTGRAY, L"RedMaskSize", buff->RedMaskSize);
    PrintIntegerWithName(gLoader.ST, EFI_LIGHTGRAY, L"GreenFieldPosition", buff->GreenFieldPosition);
    PrintIntegerWithName(gLoader.ST, EFI_LIGHTGRAY, L"GreenMaskSize", buff->GreenMaskSize);
    PrintIntegerWithName(gLoader.ST, EFI_LIGHTGRAY, L"BlueFieldPosition", buff->BlueFieldPosition);
    PrintIntegerWithName(gLoader.ST, EFI_LIGHTGRAY, L"BlueMaskSize", buff->BlueMaskSize);
}

static void 
_GetDisplayMode(
    void
    )
{
    EFI_GRAPHICS_OUTPUT_PROTOCOL *gop = GetGraphicsProtocol(gLoader.ST);
    if (!gop)
        _Die(L"Could not obtain GOP\n\r");
    gLoader.GOP = gop;

    UINT32 mode = ObtainClosestGraphicsMode(gop,
                                            gLoader.MultibootHeader.Width,
                                            gLoader.MultibootHeader.Height,
                                            &(gLoader.Framebuffer));
    if (mode == UINT32_MAX)
        _Die(L"Could not obtain GOP mode\r\n");
    
    gLoader.GopModeIndex = mode;

    PrintString(gLoader.ST, EFI_LIGHTGRAY, L"Chosen graphics mode:\r\n");
    _DumpFramebuffer();
}

static UINT8
_IsMemoryUsable(
    EFI_MEMORY_TYPE MemoryType
    )
{
    return (// MemoryType == EfiLoaderCode ||
            // MemoryType == EfiLoaderData ||
            MemoryType == EfiBootServicesCode ||
            MemoryType == EfiBootServicesData ||
            MemoryType == EfiConventionalMemory ||
            MemoryType == EfiPersistentMemory);

}

static UINT8
_IsMemoryReserved(
    EFI_MEMORY_TYPE MemoryType
    )
{
    return (MemoryType == EfiReservedMemoryType ||
            MemoryType == EfiUnacceptedMemoryType ||
            MemoryType == EfiMemoryMappedIO ||
            MemoryType == EfiMemoryMappedIOPortSpace ||
            MemoryType == EfiPalCode);
}

static UINT8
_IsMemoryAcpiReclaimable(
    EFI_MEMORY_TYPE MemoryType
    )
{
    return MemoryType == EfiACPIReclaimMemory;
}

static UINT8
_IsMemoryAcpiNvs(
    EFI_MEMORY_TYPE MemoryType
    )
{
    return MemoryType == EfiACPIMemoryNVS;
}

static UINT32
_GetBiosMemoryType(
    EFI_MEMORY_TYPE MemoryType
    )
{
    if (_IsMemoryUsable(MemoryType))
        return 1;
    
    if (_IsMemoryReserved(MemoryType))
        return 2;
    
    if (_IsMemoryAcpiReclaimable(MemoryType))
        return 3;

    if (_IsMemoryAcpiNvs(MemoryType))
        return 4;
    
    return 5;
}

static void
_PrepareMemoryMap(
    void
    )
{
    UINTN mapKey = GetMemoryMap(gLoader.ST, &(gLoader.MemoryMap));
    if (mapKey == UINT64_MAX)
        _Die(L"Could not get memory map\r\n");
    gLoader.MemoryMapKey = mapKey;

    // Convert EFI Memory Map to BIOS memory map
    MEMORY_MAP *mmap = (MEMORY_MAP *) &(gLoader.MemoryMap);
    UINT8 *buffer = (UINT8 *) mmap->MapAddress;
    UINT8 *pos = MemoryMapMemory;
    for (UINT64 i = 0; i < mmap->Count; i++)
    {
        EFI_MEMORY_DESCRIPTOR *desc = (EFI_MEMORY_DESCRIPTOR *) buffer;

        UINT32 *sz = (UINT32 *) pos; 
        *sz = sizeof(MULTIBOOT_MEMORY_MAP);
        pos += sizeof(UINT32);
        MULTIBOOT_MEMORY_MAP *curr = (MULTIBOOT_MEMORY_MAP *) pos;
        pos += sizeof(MULTIBOOT_MEMORY_MAP);

        curr->BaseAddr = desc->PhysicalStart;
        curr->Length = desc->NumberOfPages * PAGE_SIZE;
        curr->Type = _GetBiosMemoryType(desc->Type);
        curr->ExtendedAttributes = 1;

        buffer += mmap->DescriptorSize;
    }

    gLoader.MemoryMapPointer = (UINT64) MemoryMapMemory;
    gLoader.MemoryMapSize = mmap->Count * (sizeof(UINT32) + sizeof(MULTIBOOT_MEMORY_MAP));
}

static void
_FillMultibootInformation(
    void
    )
{
    MULTIBOOT_INFORMATION *info = (MULTIBOOT_INFORMATION *) &(gLoader.BootInfo);

    SetMemory(info, 0, sizeof(MULTIBOOT_INFORMATION));

    if (gLoader.BootModuleCount)
    {
        info->Flags |= BIT3;
        info->ModuleCount = gLoader.BootModuleCount;
        info->ModuleAddress = gLoader.BootModuleAddress;
    }

    info->AcpiRdsp = gLoader.AcpiRsdp;

    info->Flags |= BIT6;
    info->MemoryMapLength = gLoader.MemoryMapSize;    
    info->MemoryMapAddress = gLoader.MemoryMapPointer;

    info->Flags |= BIT9;
    info->BootLoaderName = (UINT32) ((UINT64) loaderName);

    FRAMEBUFFER *buff = (FRAMEBUFFER *) &(gLoader.Framebuffer);
    info->Flags |= BIT12;
    info->FrameBufferAddress = buff->Address;
    info->FrameBufferPitch = buff->Pitch;
    info->FrameBufferWidth = buff->Width;
    info->FrameBufferHeight = buff->Height;
    info->FrameBufferBpp = buff->BitsPerPixel;
    info->FrameBufferType = buff->Type;
    info->FrameBufferRedFieldPosition = buff->RedFieldPosition;
    info->FrameBufferRedMaskSize = buff->RedMaskSize;
    info->FrameBufferGreenFieldPosition = buff->GreenFieldPosition;
    info->FrameBufferGreenMaskSize = buff->GreenMaskSize;
    info->FrameBufferBlueFieldPosition = buff->BlueFieldPosition;
    info->FrameBufferBlueMaskSize = buff->BlueMaskSize;
}

void 
LoadOperatingSystem(
    void
    )
{
    PrintString(gLoader.ST, EFI_GREEN, L"Loading Operating System\r\n");
    
    PrintString(gLoader.ST, EFI_LIGHTGRAY, L"Searching for an Operating System\r\n");
    _SearchForOperatingSystem();
    _SearchForMultibootHeader();

    PrintString(gLoader.ST, EFI_LIGHTGRAY, L"Found Multiboot header:\r\n");
    _DumpMultibootHeader();

    _ParseMultibootHeaderInfo();

    PrintString(gLoader.ST, EFI_LIGHTGRAY, L"Loading Operating System to ");
    PrintIntegerInHexadecimal(gLoader.ST, EFI_LIGHTGRAY, gLoader.MultibootHeader.LoadAddress);
    PrintString(gLoader.ST, EFI_LIGHTGRAY, L" starting from offset ");
    PrintIntegerInHexadecimal(gLoader.ST, EFI_LIGHTGRAY, gLoader.OsTextOffset);
    PrintString(gLoader.ST, EFI_LIGHTGRAY, L"\r\n");
    _CopyOperatingSystem();
    PrintString(gLoader.ST, EFI_LIGHTGRAY, L"Operating System Loaded\r\n");

    PrintString(gLoader.ST, EFI_LIGHTGRAY, L"Loading Boot Modules\r\n");
    _LoadBootModules();
    PrintString(gLoader.ST, EFI_LIGHTGRAY, L"Loaded Boot Modules\r\n");

    _PrepareAssembly();

    PrintString(gLoader.ST, EFI_LIGHTGRAY, L"Searching for ACPI RSDP\r\n");
    UINT64 rsdp = GetAcpiRsdp(gLoader.ST);    
    if (!rsdp)
        _Die(L"Could not find ACPI RSDP\r\n");
    gLoader.AcpiRsdp = rsdp;
    PrintIntegerWithName(gLoader.ST, EFI_LIGHTGRAY, L"ACPI RSDP", rsdp);

    PrintString(gLoader.ST, EFI_LIGHTGRAY, L"Obtaining a framebuffer\r\n");
    _GetDisplayMode();

    PrintString(gLoader.ST, EFI_LIGHTGRAY, L"Preparing memory map\r\n");
    _PrepareMemoryMap();
    PrintString(gLoader.ST, EFI_LIGHTGRAY, L"Prepared memory map\r\n");

    PrintString(gLoader.ST, EFI_LIGHTGRAY, L"Filling Multiboot Information\r\n");
    _FillMultibootInformation();
    PrintString(gLoader.ST, EFI_LIGHTGRAY, L"Filled Multiboot Information\r\n");

    PrintString(gLoader.ST, EFI_GREEN, L"Loaded Operating System\r\n");
}

static void 
_ExitBootServices(
    void
    )
{
    CloseFileHandle(gLoader.RootDirectory);
    UINTN mapKey = gLoader.MemoryMapKey;
    while(gLoader.ST->BootServices->ExitBootServices(gLoader.ImageHandle, mapKey) != EFI_SUCCESS)
        mapKey = GetMemoryMap(gLoader.ST, &(gLoader.MemoryMap));
}

void
StartOperatingSystem(
    void
    )
{
    PrintString(gLoader.ST, EFI_GREEN, L"To start the Operating System, press any key\r\n");
    PrintString(gLoader.ST, EFI_LIGHTGRAY, L"...\r\n");
    WaitForKeyPress(gLoader.ST);

    SetGraphicsMode(gLoader.GOP, gLoader.GopModeIndex);
    _ExitBootServices();
    
    // Signal that we are done
    UINT32 *buff = (UINT32 *) gLoader.Framebuffer.Address;
    for (int i = 0; i < 100; i++) 
        buff[i] = UINT32_MAX;

    (gLoader.StartOsRoutine)(gLoader.MultibootHeader.EntryAddress,
                             (UINT64) &(gLoader.BootInfo),
                             (UINT64) &transition);
}
