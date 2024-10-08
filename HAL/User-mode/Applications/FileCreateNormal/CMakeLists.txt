cmake_minimum_required(VERSION 3.30.2 FATAL_ERROR)

set(APP_INCLUDES
    ${PROJECT_SOURCE_DIR}/Shared/common
)

set(APP_PDB_FLAG
    $<$<COMPILE_LANGUAGE:C>:/Fd:$<TARGET_FILE_DIR:FileCreateNormal.exe>/FileCreateNormal.pdb>
)

file(GLOB_RECURSE APP_HELLOWORLD_SOURCES src/*.c src/*.yasm)

add_executable(FileCreateNormal.exe ${APP_HELLOWORLD_SOURCES})
target_include_directories(FileCreateNormal.exe PUBLIC $<$<COMPILE_LANGUAGE:C>:${APP_INCLUDES}>)
target_compile_options(FileCreateNormal.exe PRIVATE ${APP_FLAGS} PRIVATE ${APP_PDB_FLAG})
target_compile_definitions(FileCreateNormal.exe PRIVATE ${GLOBAL_DEFINES} PRIVATE ${MBCS_DEFINE})
target_link_libraries(FileCreateNormal.exe PRIVATE CommonLibNoLocks UsermodeLibrary)
target_link_options(FileCreateNormal.exe PRIVATE ${APP_LINK_FLAGS})

install(TARGETS FileCreateNormal.exe DESTINATION apps/FileCreateNormal)
install(FILES $<TARGET_FILE_DIR:FileCreateNormal.exe>/FileCreateNormal.pdb DESTINATION apps/FileCreateNormal OPTIONAL)
