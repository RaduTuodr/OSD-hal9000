cmake_minimum_required(VERSION 3.30.2 FATAL_ERROR)

set(APP_INCLUDES
    ${PROJECT_SOURCE_DIR}/Shared/common
)

set(APP_PDB_FLAG
    $<$<COMPILE_LANGUAGE:C>:/Fd:$<TARGET_FILE_DIR:FileReadBadHandle.exe>/FileReadBadHandle.pdb>
)

file(GLOB_RECURSE APP_HELLOWORLD_SOURCES src/*.c src/*.yasm)

add_executable(FileReadBadHandle.exe ${APP_HELLOWORLD_SOURCES})
target_include_directories(FileReadBadHandle.exe PUBLIC $<$<COMPILE_LANGUAGE:C>:${APP_INCLUDES}>)
target_compile_options(FileReadBadHandle.exe PRIVATE ${APP_FLAGS} PRIVATE ${APP_PDB_FLAG})
target_compile_definitions(FileReadBadHandle.exe PRIVATE ${GLOBAL_DEFINES} PRIVATE ${MBCS_DEFINE})
target_link_libraries(FileReadBadHandle.exe PRIVATE CommonLibNoLocks UsermodeLibrary)
target_link_options(FileReadBadHandle.exe PRIVATE ${APP_LINK_FLAGS})

install(TARGETS FileReadBadHandle.exe DESTINATION apps/FileReadBadHandle)
install(FILES $<TARGET_FILE_DIR:FileReadBadHandle.exe>/FileReadBadHandle.pdb DESTINATION apps/FileReadBadHandle OPTIONAL)
