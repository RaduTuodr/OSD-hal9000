#include "HAL9000.h"
#include "ex.h"
#include "log.h"
#include "mmu.h"
#include "pe_exports.h"
#include "pe_parser.h"
#include "status.h"
#include "exe_loader.h"

typedef union
{
    PE_NT_HEADER_INFO PeHeaderInfo;
} _EXE_HEADER;

typedef struct
{
    PVOID Image;
    DWORD ImageSize;
    EXE_FORMAT Format; 
    _EXE_HEADER Header;
} _EXE_LOADER_CONTEXT;

static
EXE_FORMAT
_ExecutableLoaderDetermineFormat(
    PVOID Image
    );

STATUS
ExecutableLoaderPreinit(
    EXE_LOADER_CONTEXT *Context
    )
{
    if (NULL == Context)
    {
        return STATUS_INVALID_PARAMETER1;
    }

    _EXE_LOADER_CONTEXT *context = ExAllocatePoolWithTag(PoolAllocateZeroMemory,
                                                         sizeof(_EXE_LOADER_CONTEXT),
                                                         HEAP_PROCESS_TAG,
                                                         0);
    if (NULL == context)
    {
        LOG_FUNC_ERROR_ALLOC("ExAllocatePoolWithTag", sizeof(_EXE_LOADER_CONTEXT));
        *Context = NULL;
        return STATUS_HEAP_INSUFFICIENT_RESOURCES;
    }

    *Context = context;

    return STATUS_SUCCESS;
}

STATUS
ExecutableLoaderInit(
    EXE_LOADER_CONTEXT Context,
    PVOID Image,
    DWORD ImageSize
    )
{
    STATUS status;
    EXE_FORMAT format;
    _EXE_LOADER_CONTEXT *context;
    
    status = STATUS_SUCCESS;
    format = ExecutableFormatUnknown;
    context = (_EXE_LOADER_CONTEXT *) Context;

    if (NULL == Context)
    {
        return STATUS_INVALID_PARAMETER1;
    }

    if (NULL == Image)
    {
        return STATUS_INVALID_PARAMETER2;
    }

    if (0 == ImageSize)
    {
        return STATUS_INVALID_PARAMETER3;
    }
    
    format = _ExecutableLoaderDetermineFormat(Image);
    if (format == ExecutableFormatUnknown || format == ExecutableFormatELF)
    {
        return STATUS_UNSUPPORTED;
    }

    status = PeRetrieveNtHeader(Image, ImageSize, &(context->Header.PeHeaderInfo));
    if (!SUCCEEDED(status))
    {
        return status;
    }

    context->Image = Image;
    context->ImageSize = ImageSize;
    context->Format = format;
    
    return STATUS_SUCCESS;
}

STATUS
ExectuableLoaderInitFromPEHeader(
    EXE_LOADER_CONTEXT *Context,
    PPE_NT_HEADER_INFO HeaderInfo
    )
{
    STATUS status;
    _EXE_LOADER_CONTEXT *context;

    status = STATUS_SUCCESS;
    context = NULL;

    if (NULL == Context)
    {
        return STATUS_INVALID_PARAMETER1;
    }

    if (NULL == HeaderInfo)
    {
        return STATUS_INVALID_PARAMETER2;
    }

    status = ExecutableLoaderPreinit(Context);
    if (!SUCCEEDED(status))
    {
        return status;
    }

    context = (_EXE_LOADER_CONTEXT *) *Context;
    context->Format = ExecutableFormatPE;
    context->Image = HeaderInfo->ImageBase;
    context->ImageSize = HeaderInfo->Size;
    memcpy(&(context->Header.PeHeaderInfo), HeaderInfo, sizeof(PE_NT_HEADER_INFO));
  
    return STATUS_SUCCESS;
}

STATUS
ExecutableLoaderGetFormat(
    EXE_LOADER_CONTEXT Context,
    EXE_FORMAT *Format
    )
{
    if (NULL == Context)
    {
        return STATUS_INVALID_PARAMETER1;
    }

    if (NULL == Format)
    {
        return STATUS_INVALID_PARAMETER2;
    }

    *Format = ((_EXE_LOADER_CONTEXT *) Context)->Format;

    return STATUS_SUCCESS;
}

STATUS
ExecutableLoaderGetPhysicalImageBase(
    EXE_LOADER_CONTEXT Context,
    PVOID *ImageBase
    )
{
    _EXE_LOADER_CONTEXT *context;

    context = (_EXE_LOADER_CONTEXT *) Context;

    if (NULL == Context)
    {
        return STATUS_INVALID_PARAMETER1;
    }
    
    if (NULL == ImageBase)
    {
        return STATUS_INVALID_PARAMETER2;
    }

    if (context->Format == ExecutableFormatUnknown || context->Format == ExecutableFormatELF)
    {
        return STATUS_UNSUPPORTED;
    }

    *ImageBase = context->Image;

    return STATUS_SUCCESS;
}

STATUS
ExecutableLoaderGetVirtualImageBase(
    EXE_LOADER_CONTEXT Context,
    PVOID *ImageBase
    )
{
    _EXE_LOADER_CONTEXT *context;

    context = (_EXE_LOADER_CONTEXT *) Context;

    if (NULL == Context)
    {
        return STATUS_INVALID_PARAMETER1; 
    }

    if (NULL == ImageBase)
    {
        return STATUS_INVALID_PARAMETER2;
    }

    if (context->Format == ExecutableFormatUnknown || context->Format == ExecutableFormatELF)
    {
        return STATUS_UNSUPPORTED;
    }

    *ImageBase = context->Header.PeHeaderInfo.Preferred.ImageBase;

    return STATUS_SUCCESS; 
}

STATUS
ExecutableLoaderGetImageSize(
    EXE_LOADER_CONTEXT Context,
    DWORD *Size 
    )
{
    _EXE_LOADER_CONTEXT *context;

    context = (_EXE_LOADER_CONTEXT *) Context;

    if (NULL == Context)
    {
        return STATUS_INVALID_PARAMETER1; 
    }

    if (NULL == Size)
    {
        return STATUS_INVALID_PARAMETER2;
    }

    if (context->Format == ExecutableFormatUnknown || context->Format == ExecutableFormatELF)
    {
        return STATUS_UNSUPPORTED;
    }

    *Size = context->ImageSize;

    return STATUS_SUCCESS; 
}

STATUS
ExecutableLoaderGetEntryPoint(
    EXE_LOADER_CONTEXT Context,
    PVOID *EntryPoint
    )
{
    _EXE_LOADER_CONTEXT *context;

    context = (_EXE_LOADER_CONTEXT *) Context;

    if (NULL == Context)
    {
        return STATUS_INVALID_PARAMETER1; 
    }

    if (NULL == EntryPoint)
    {
        return STATUS_INVALID_PARAMETER2;
    }

    if (context->Format == ExecutableFormatUnknown || context->Format == ExecutableFormatELF)
    {
        return STATUS_UNSUPPORTED;
    }

    *EntryPoint = context->Header.PeHeaderInfo.Preferred.AddressOfEntryPoint;

    return STATUS_SUCCESS; 
}

STATUS
ExecutableLoaderMemoryMap(
    EXE_LOADER_CONTEXT Context,
    PPAGING_LOCK_DATA PagingData
    )
{
    _EXE_LOADER_CONTEXT *context;

    context = (_EXE_LOADER_CONTEXT *) Context;

    if (NULL == Context)
    {
        return STATUS_INVALID_PARAMETER1;
    }

    if (NULL == PagingData)
    {
        return STATUS_INVALID_PARAMETER2;
    }

    if (context->Format == ExecutableFormatUnknown || context->Format == ExecutableFormatELF)
    {
        return STATUS_UNSUPPORTED;
    }

    return MmuLoadPe(&(context->Header.PeHeaderInfo), PagingData);
}

STATUS
ExecutableLoaderUninit(
    EXE_LOADER_CONTEXT *Context
    )
{
    if (NULL == Context)
    {
        return STATUS_INVALID_PARAMETER1;
    }

    if (NULL == *Context)
    {
        return STATUS_INVALID_PARAMETER1;
    }

    ExFreePoolWithTag(*Context, HEAP_PROCESS_TAG);
    *Context = NULL;

    return STATUS_SUCCESS;
}

static
EXE_FORMAT
_ExecutableLoaderDetermineFormat(
    PVOID Image
    )
{
    WORD *potentialMzSignature = (WORD *) Image;
    DWORD *potentialElfSignature = (DWORD *) Image;

    if (0x5A4D == *potentialMzSignature)
    {
        return ExecutableFormatPE;
    }

    if (0x464C457F == *potentialElfSignature)
    {
        return ExecutableFormatELF;
    }

    return ExecutableFormatUnknown;
}
