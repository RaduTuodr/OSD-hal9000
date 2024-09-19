#pragma once

#include <Base.h>

// Source: https://www.gnu.org/software/grub/manual/multiboot/multiboot.html

#define MULTIBOOT_HEADER_MAGIC 0x1BADB002
#define MULTIBOOT_LOADER_MAGIC 0x2BADB002

#define MULTIBOOT_FLAGS_MODULE_PAGE_ALIGN BIT0
#define MULTIBOOT_FLAGS_MEMORY_MAP BIT1
#define MULTIBOOT_FLAGS_VIDEO_MODE BIT2
#define MULTIBOOT_FLAGS_LOAD_INFO BIT16

#pragma pack(push, 1)

typedef struct
{
    UINT32 Magic;
    UINT32 Flags; // we need 0 = bootmod align, 1 = mm, 2 = framebuff, 16 = addr set
    UINT32 Checksum;
    UINT32 HeaderAddress;
    UINT32 LoadAddress;
    UINT32 LoadEndAddress;
    UINT32 BssEndAddress;
    UINT32 EntryAddress;
    UINT32 ModeType;
    UINT32 Width;
    UINT32 Height;
    UINT32 Depth;
} MULTIBOOT_HEADER;

// To pass the ACPI RSDP to HAL we will use the field reserved for the symbol table

typedef struct
{
    UINT32 Flags;
    UINT32 MemLower; // flags 0
    UINT32 MemUpper; // flags 0
    UINT32 BootDevice; // flags 1
    UINT32 CommandLine; // flags 2
    UINT32 ModuleCount; //flags 3
    UINT32 ModuleAddress; // flags 3
    UINT64 AcpiRdsp; 
    UINT64 Reserved;
    UINT32 MemoryMapLength; // flags 6
    UINT32 MemoryMapAddress; // flags 6
    UINT32 DrivesLength; // flags 7
    UINT32 DrivesAddress; // flags 7
    UINT32 ConfigTable; // flags 8
    UINT32 BootLoaderName; // flags 9
    UINT32 ApmTable; // flags 10
    UINT8 Vbe[16]; // flags 11
    UINT64 FrameBufferAddress; // flags 12
    UINT32 FrameBufferPitch;
    UINT32 FrameBufferWidth;
    UINT32 FrameBufferHeight;
    UINT32 FrameBufferBpp;
    UINT32 FrameBufferType;
    UINT32 FrameBufferRedFieldPosition;
    UINT32 FrameBufferRedMaskSize;
    UINT32 FrameBufferGreenFieldPosition;
    UINT32 FrameBufferGreenMaskSize;
    UINT32 FrameBufferBlueFieldPosition;
    UINT32 FrameBufferBlueMaskSize;
} MULTIBOOT_INFORMATION;

typedef struct
{
    UINT32 ModuleStart;
    UINT32 ModuleEnd;
    UINT32 StringAddr;
    UINT32 Reserved;
} MULTIBOOT_BOOT_MODULE;

#define MULTIBOOT_FRAMEBUFFER_RGB 1

typedef struct
{
    // Hidden Size field, UINT32
    UINT64 BaseAddr;
    UINT64 Length;
    UINT32 Type;
    UINT32 ExtendedAttributes;
} MULTIBOOT_MEMORY_MAP;

#pragma pack(pop)

// Machine State:
// EAX: Magic
// EBX: Info Struct
// CS: RX Flat Segment
// Other Segment Registers: Read/Write Flat Segment
// A20 Enabled
// CR0: PG(31) unset PE(0) set
// EFLAGS: VM(17) unset, IF(9) unset
