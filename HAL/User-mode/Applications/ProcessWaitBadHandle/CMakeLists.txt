cmake_minimum_required(VERSION 3.30.2 FATAL_ERROR)

set(APP_INCLUDES
    ${PROJECT_SOURCE_DIR}/Shared/common
)

set(APP_PDB_FLAG
    $<$<COMPILE_LANGUAGE:C>:/Fd:$<TARGET_FILE_DIR:ProcessWaitBadHandle.exe>/ProcessWaitBadHandle.pdb>
)

file(GLOB_RECURSE APP_HELLOWORLD_SOURCES src/*.c src/*.yasm)

add_executable(ProcessWaitBadHandle.exe ${APP_HELLOWORLD_SOURCES})
target_include_directories(ProcessWaitBadHandle.exe PUBLIC $<$<COMPILE_LANGUAGE:C>:${APP_INCLUDES}>)
target_compile_options(ProcessWaitBadHandle.exe PRIVATE ${APP_FLAGS} PRIVATE ${APP_PDB_FLAG})
target_compile_definitions(ProcessWaitBadHandle.exe PRIVATE ${GLOBAL_DEFINES} PRIVATE ${MBCS_DEFINE})
target_link_libraries(ProcessWaitBadHandle.exe PRIVATE CommonLibNoLocks UsermodeLibrary)
target_link_options(ProcessWaitBadHandle.exe PRIVATE ${APP_LINK_FLAGS})

install(TARGETS ProcessWaitBadHandle.exe DESTINATION apps/ProcessWaitBadHandle)
install(FILES $<TARGET_FILE_DIR:ProcessWaitBadHandle.exe>/ProcessWaitBadHandle.pdb DESTINATION apps/ProcessWaitBadHandle OPTIONAL)
