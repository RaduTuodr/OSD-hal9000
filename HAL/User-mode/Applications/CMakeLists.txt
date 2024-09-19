cmake_minimum_required(VERSION 3.30.2 FATAL_ERROR)

set(APP_DEBUG_FLAGS
    /fp:except-
    /Gy-
)

set(APP_RELEASE_FLAGS
    /fp:except-
    /Gy
    /GL
)

set(APP_FLAGS
    ${GLOBAL_FLAGS}
    $<IF:$<CONFIG:Release>, ${APP_RELEASE_FLAGS}, ${APP_DEBUG_FLAGS}>
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

set(APP_LINK_FLAGS
    $<$<COMPILE_LANGUAGE:C>:${APP_C_LINK_FLAGS}>
    $<$<CONFIG:Release>:/LTCG>
)

add_subdirectory(AppHelloWorld)
