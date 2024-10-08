cmake_minimum_required(VERSION 3.30.2 FATAL_ERROR)

set(APP_INCLUDES
    ${PROJECT_SOURCE_DIR}/Shared/common
)

set(APP_PDB_FLAG
    $<$<COMPILE_LANGUAGE:C>:/Fd:$<TARGET_FILE_DIR:FileCloseTwice.exe>/FileCloseTwice.pdb>
)

file(GLOB_RECURSE APP_SOURCES src/*.c src/*.yasm)

add_executable(FileCloseTwice.exe ${APP_SOURCES})
target_include_directories(FileCloseTwice.exe PUBLIC $<$<COMPILE_LANGUAGE:C>:${APP_INCLUDES}>)
target_compile_options(FileCloseTwice.exe PRIVATE ${APP_FLAGS} PRIVATE ${APP_PDB_FLAG})
target_compile_definitions(FileCloseTwice.exe PRIVATE ${GLOBAL_DEFINES} PRIVATE ${MBCS_DEFINE})
target_link_libraries(FileCloseTwice.exe PRIVATE CommonLibNoLocks UsermodeLibrary)
target_link_options(FileCloseTwice.exe PRIVATE ${APP_LINK_FLAGS})

install(TARGETS FileCloseTwice.exe DESTINATION apps/FileCloseTwice)
install(FILES $<TARGET_FILE_DIR:FileCloseTwice.exe>/FileCloseTwice.pdb DESTINATION apps/FileCloseTwice OPTIONAL)
