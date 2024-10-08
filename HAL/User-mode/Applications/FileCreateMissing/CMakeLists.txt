cmake_minimum_required(VERSION 3.30.2 FATAL_ERROR)

set(APP_INCLUDES
    ${PROJECT_SOURCE_DIR}/Shared/common
)

set(APP_PDB_FLAG
    $<$<COMPILE_LANGUAGE:C>:/Fd:$<TARGET_FILE_DIR:FileCreateMissing.exe>/FileCreateMissing.pdb>
)

file(GLOB_RECURSE APP_HELLOWORLD_SOURCES src/*.c src/*.yasm)

add_executable(FileCreateMissing.exe ${APP_HELLOWORLD_SOURCES})
target_include_directories(FileCreateMissing.exe PUBLIC $<$<COMPILE_LANGUAGE:C>:${APP_INCLUDES}>)
target_compile_options(FileCreateMissing.exe PRIVATE ${APP_FLAGS} PRIVATE ${APP_PDB_FLAG})
target_compile_definitions(FileCreateMissing.exe PRIVATE ${GLOBAL_DEFINES} PRIVATE ${MBCS_DEFINE})
target_link_libraries(FileCreateMissing.exe PRIVATE CommonLibNoLocks UsermodeLibrary)
target_link_options(FileCreateMissing.exe PRIVATE ${APP_LINK_FLAGS})

install(TARGETS FileCreateMissing.exe DESTINATION apps/FileCreateMissing)
install(FILES $<TARGET_FILE_DIR:FileCreateMissing.exe>/FileCreateMissing.pdb DESTINATION apps/FileCreateMissing OPTIONAL)
