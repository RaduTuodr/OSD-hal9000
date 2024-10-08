cmake_minimum_required(VERSION 3.30.2 FATAL_ERROR)

set(APP_HELLOWORLD_INCLUDES
    ${PROJECT_SOURCE_DIR}/Shared/common
)

set(APP_HELLOWORLD_PDB_FLAG
    $<$<COMPILE_LANGUAGE:C>:/Fd:$<TARGET_FILE_DIR:Dummy.exe>/Dummy.pdb>
)

file(GLOB_RECURSE APP_HELLOWORLD_SOURCES src/*.c src/*.yasm)

add_executable(Dummy.exe ${APP_HELLOWORLD_SOURCES})
target_include_directories(Dummy.exe PUBLIC $<$<COMPILE_LANGUAGE:C>:${APP_HELLOWORLD_INCLUDES}>)
target_compile_options(Dummy.exe PRIVATE ${APP_FLAGS} PRIVATE ${APP_HELLOWORLD_PDB_FLAG})
target_compile_definitions(Dummy.exe PRIVATE ${GLOBAL_DEFINES} PRIVATE ${MBCS_DEFINE})
target_link_libraries(Dummy.exe PRIVATE CommonLibNoLocks UsermodeLibrary)
target_link_options(Dummy.exe PRIVATE ${APP_LINK_FLAGS})

install(TARGETS Dummy.exe DESTINATION apps/Dummy)
install(FILES $<TARGET_FILE_DIR:Dummy.exe>/Dummy.pdb DESTINATION apps/Dummy OPTIONAL)
