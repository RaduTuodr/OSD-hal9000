cmake_minimum_required(VERSION 3.30.2 FATAL_ERROR)

set(APP_INCLUDES
    ${PROJECT_SOURCE_DIR}/Shared/common
)

set(APP_PDB_FLAG
    $<$<COMPILE_LANGUAGE:C>:/Fd:$<TARGET_FILE_DIR:VirtualFreeInvalid.exe>/VirtualFreeInvalid.pdb>
)

file(GLOB_RECURSE APP_HELLOWORLD_SOURCES src/*.c src/*.yasm)

add_executable(VirtualFreeInvalid.exe ${APP_HELLOWORLD_SOURCES})
target_include_directories(VirtualFreeInvalid.exe PUBLIC $<$<COMPILE_LANGUAGE:C>:${APP_INCLUDES}>)
target_compile_options(VirtualFreeInvalid.exe PRIVATE ${APP_FLAGS} PRIVATE ${APP_PDB_FLAG})
target_compile_definitions(VirtualFreeInvalid.exe PRIVATE ${GLOBAL_DEFINES} PRIVATE ${MBCS_DEFINE})
target_link_libraries(VirtualFreeInvalid.exe PRIVATE CommonLibNoLocks UsermodeLibrary)
target_link_options(VirtualFreeInvalid.exe PRIVATE ${APP_LINK_FLAGS})

install(TARGETS VirtualFreeInvalid.exe DESTINATION apps/VirtualFreeInvalid)
install(FILES $<TARGET_FILE_DIR:VirtualFreeInvalid.exe>/VirtualFreeInvalid.pdb DESTINATION apps/VirtualFreeInvalid OPTIONAL)
