cmake_minimum_required(VERSION 3.30.2 FATAL_ERROR)

set(APP_INCLUDES
    ${PROJECT_SOURCE_DIR}/Shared/common
)

set(APP_PDB_FLAG
    $<$<COMPILE_LANGUAGE:C>:/Fd:$<TARGET_FILE_DIR:FileCreateNull.exe>/FileCreateNull.pdb>
)

file(GLOB_RECURSE APP_HELLOWORLD_SOURCES src/*.c src/*.yasm)

add_executable(FileCreateNull.exe ${APP_HELLOWORLD_SOURCES})
target_include_directories(FileCreateNull.exe PUBLIC $<$<COMPILE_LANGUAGE:C>:${APP_INCLUDES}>)
target_compile_options(FileCreateNull.exe PRIVATE ${APP_FLAGS} PRIVATE ${APP_PDB_FLAG})
target_compile_definitions(FileCreateNull.exe PRIVATE ${GLOBAL_DEFINES} PRIVATE ${MBCS_DEFINE})
target_link_libraries(FileCreateNull.exe PRIVATE CommonLibNoLocks UsermodeLibrary)
target_link_options(FileCreateNull.exe PRIVATE ${APP_LINK_FLAGS})

install(TARGETS FileCreateNull.exe DESTINATION apps/FileCreateNull)
install(FILES $<TARGET_FILE_DIR:FileCreateNull.exe>/FileCreateNull.pdb DESTINATION apps/FileCreateNull OPTIONAL)
