cmake_minimum_required(VERSION 3.30.2 FATAL_ERROR)

if (CMAKE_C_COMPILER_ID STREQUAL "MSVC")
    set(APP_DEBUG_FLAGS
        /fp:except-
        /Gy-
    )

    set(APP_RELEASE_FLAGS
        /fp:except-
        /Gy
        /GL
    )

    set(APP_C_LINK_FLAGS
        /ALIGN:4096
        /FILEALIGN:4096
        /IGNORE:4108
        /NXCOMPAT
        /INCREMENTAL:NO
        /ENTRY:__start
        /ERRORREPORT:PROMPT
        /FIXED
        /MANIFEST:NO
        /NODEFAULTLIB
        /DYNAMICBASE:NO
        /SUBSYSTEM:NATIVE
        /NOLOGO
        /MACHINE:X64
        /WX
        /DEBUG:FULL
    )
else()
    set(APP_DEBUG_FLAGS)

    set(APP_RELEASE_FLAGS
        -ffunction-sections
    )

    set(APP_C_LINK_FLAGS
        -static
        -ffreestanding
        -nostdlib
        -nodefaultlibs
        -Wl,--gc-sections
        -Wall
        -Wextra
        -fno-zero-initialized-in-bss
        -T ${CMAKE_CURRENT_LIST_DIR}/Applications.ld
    )
endif()

set(APP_FLAGS
    ${GLOBAL_FLAGS}
    $<$<CONFIG:Debug>:${APP_DEBUG_FLAGS}>
    $<$<CONFIG:Release>:${APP_RELEASE_FLAGS}>
)

set(APP_LINK_FLAGS
    $<$<COMPILE_LANGUAGE:C>:${APP_C_LINK_FLAGS}>
    $<$<NOT:$<STREQUAL:"GNU",$<C_COMPILER_ID>>>:$<$<CONFIG:Release>:/LTCG>>
)

add_subdirectory(AppHelloWorld)
# add_subdirectory(Args)
# add_subdirectory(BadJumpKernel)
# add_subdirectory(BadJumpNoncanonical)
# add_subdirectory(BadJumpNull)
# add_subdirectory(BadReadIoPort)
# add_subdirectory(BadReadKernel)
# add_subdirectory(BadReadMsr)
# add_subdirectory(BadReadNonCanonical)
# add_subdirectory(BadReadNull)
# add_subdirectory(BadWriteIoPort)
# add_subdirectory(BadWriteKernel)
# add_subdirectory(BadWriteMsr)
# add_subdirectory(BadWriteNonCanonical)
# add_subdirectory(BadWriteNull)
# add_subdirectory(Dummy)
# add_subdirectory(DummyFail)
# add_subdirectory(FileCloseBad)
# add_subdirectory(FileCloseNormal)
# add_subdirectory(FileCloseStdout)
# add_subdirectory(FileCloseTwice)
# add_subdirectory(FileCreateBadPointer)
# add_subdirectory(FileCreateEmptyPath)
# add_subdirectory(FileCreateExistent)
# add_subdirectory(FileCreateMissing)
# add_subdirectory(FileCreateNormal)
# add_subdirectory(FileCreateNull)
# add_subdirectory(FileCreateTwice)
# add_subdirectory(FileReadBadHandle)
# add_subdirectory(FileReadBadPointer)
# add_subdirectory(FileReadKernel)
# add_subdirectory(FileReadNormal)
# add_subdirectory(FileReadStdout)
# add_subdirectory(FileReadZero)
# add_subdirectory(ProcessCloseFile)
# add_subdirectory(ProcessCloseNormal)
# add_subdirectory(ProcessCloseParentHandle)
# add_subdirectory(ProcessCloseTwice)
# add_subdirectory(ProcessCreateBadPointer)
# add_subdirectory(ProcessCreateMissingFile)
# add_subdirectory(ProcessCreateMultiple)
# add_subdirectory(ProcessCreateOnce)
# add_subdirectory(ProcessCreateWithArguments)
# add_subdirectory(ProcessExit)
# add_subdirectory(ProcessGetPid)
# add_subdirectory(ProcessQuotaGood)
# add_subdirectory(ProcessQuotaJustRight)
# add_subdirectory(ProcessQuotaMore)
# add_subdirectory(ProcessWaitBadHandle)
# add_subdirectory(ProcessWaitClosedHandle)
# add_subdirectory(ProcessWaitNormal)
# add_subdirectory(ProcessWaitTerminated)
# add_subdirectory(StackGrowthRecursiveFunction)
# add_subdirectory(StackGrowthVariables)
# add_subdirectory(SwapLinear)
# add_subdirectory(SwapMultipleShared)
# add_subdirectory(SwapZeros)
# add_subdirectory(SwapZerosWritten)
# add_subdirectory(TestApp)
# add_subdirectory(ThreadCloseTwice)
# add_subdirectory(ThreadCreateBadPointer)
# add_subdirectory(ThreadCreateMultiple)
# add_subdirectory(ThreadCreateOnce)
# add_subdirectory(ThreadCreateWithArguments)
# add_subdirectory(ThreadExit)
# add_subdirectory(ThreadGetTid)
# add_subdirectory(ThreadWaitBadHandle)
# add_subdirectory(ThreadWaitClosedHandle)
# add_subdirectory(ThreadWaitNormal)
# add_subdirectory(ThreadWaitTerminated)
# add_subdirectory(VirtualAllocAccessFail)
# add_subdirectory(VirtualAllocHugeEager)
# add_subdirectory(VirtualAllocHugeLazy)
# add_subdirectory(VirtualAllocNormal)
# add_subdirectory(VirtualAllocWriteExec)
# add_subdirectory(VirtualAllocZeros)
# add_subdirectory(VirtualFreeInvalid)
# add_subdirectory(VirtualFreeMore)
# add_subdirectory(VirtualSharedNormal)
