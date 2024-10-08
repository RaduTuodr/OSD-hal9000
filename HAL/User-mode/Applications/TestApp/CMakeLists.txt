cmake_minimum_required(VERSION 3.30.2 FATAL_ERROR)

set(APP_HELLOWORLD_INCLUDES
    ${PROJECT_SOURCE_DIR}/Shared/common
)

set(APP_HELLOWORLD_PDB_FLAG
    $<$<COMPILE_LANGUAGE:C>:/Fd:$<TARGET_FILE_DIR:TestApp.exe>/TestApp.pdb>
)

file(GLOB_RECURSE APP_HELLOWORLD_SOURCES src/*.c src/*.yasm)

add_executable(TestApp.exe ${APP_HELLOWORLD_SOURCES})
target_include_directories(TestApp.exe PUBLIC $<$<COMPILE_LANGUAGE:C>:${APP_HELLOWORLD_INCLUDES}>)
target_compile_options(TestApp.exe PRIVATE ${APP_FLAGS} PRIVATE ${APP_HELLOWORLD_PDB_FLAG})
target_compile_definitions(TestApp.exe PRIVATE ${GLOBAL_DEFINES} PRIVATE ${MBCS_DEFINE})
target_link_libraries(TestApp.exe PRIVATE CommonLibNoLocks UsermodeLibrary)
target_link_options(TestApp.exe PRIVATE ${APP_LINK_FLAGS})

install(TARGETS TestApp.exe DESTINATION apps/TestApp)
install(FILES $<TARGET_FILE_DIR:TestApp.exe>/TestApp.pdb DESTINATION apps/TestApp OPTIONAL)
