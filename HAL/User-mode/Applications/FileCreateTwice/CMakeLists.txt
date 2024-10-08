cmake_minimum_required(VERSION 3.30.2 FATAL_ERROR)

set(APP_INCLUDES
    ${PROJECT_SOURCE_DIR}/Shared/common
)

set(APP_PDB_FLAG
    $<$<COMPILE_LANGUAGE:C>:/Fd:$<TARGET_FILE_DIR:FileCreateTwice.exe>/FileCreateTwice.pdb>
)

file(GLOB_RECURSE APP_HELLOWORLD_SOURCES src/*.c src/*.yasm)

add_executable(FileCreateTwice.exe ${APP_HELLOWORLD_SOURCES})
target_include_directories(FileCreateTwice.exe PUBLIC $<$<COMPILE_LANGUAGE:C>:${APP_INCLUDES}>)
target_compile_options(FileCreateTwice.exe PRIVATE ${APP_FLAGS} PRIVATE ${APP_PDB_FLAG})
target_compile_definitions(FileCreateTwice.exe PRIVATE ${GLOBAL_DEFINES} PRIVATE ${MBCS_DEFINE})
target_link_libraries(FileCreateTwice.exe PRIVATE CommonLibNoLocks UsermodeLibrary)
target_link_options(FileCreateTwice.exe PRIVATE ${APP_LINK_FLAGS})

install(TARGETS FileCreateTwice.exe DESTINATION apps/FileCreateTwice)
install(FILES $<TARGET_FILE_DIR:FileCreateTwice.exe>/FileCreateTwice.pdb DESTINATION apps/FileCreateTwice OPTIONAL)
