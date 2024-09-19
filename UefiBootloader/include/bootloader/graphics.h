#pragma once

#include <Uefi.h>
#include <Protocol/GraphicsOutput.h>

#define UINT32_MAX 4294967295U

typedef struct
{
    UINT64 Address;
    UINT32 Pitch;
    UINT32 Width;
    UINT32 Height;
    UINT32 BitsPerPixel;
    UINT32 Type;
    UINT32 RedFieldPosition;
    UINT32 RedMaskSize;
    UINT32 GreenFieldPosition;
    UINT32 GreenMaskSize;
    UINT32 BlueFieldPosition;
    UINT32 BlueMaskSize;
} FRAMEBUFFER;

EFI_GRAPHICS_OUTPUT_PROTOCOL*
GetGraphicsProtocol(
    EFI_SYSTEM_TABLE *ST
    );

UINT32 ObtainClosestGraphicsMode(
    EFI_GRAPHICS_OUTPUT_PROTOCOL *GOP,
    UINT32 Width,
    UINT32 Height,
    FRAMEBUFFER *Framebuffer
    );
 
EFI_STATUS
SetGraphicsMode(
    EFI_GRAPHICS_OUTPUT_PROTOCOL *GOP,
    UINT32 Mode
    );
