cmake_minimum_required(VERSION 3.30.2 FATAL_ERROR)

set(APP_INCLUDES
    ${PROJECT_SOURCE_DIR}/Shared/common
)

set(APP_PDB_FLAG
    $<$<COMPILE_LANGUAGE:C>:/Fd:$<TARGET_FILE_DIR:ProcessWaitTerminated.exe>/ProcessWaitTerminated.pdb>
)

file(GLOB_RECURSE APP_HELLOWORLD_SOURCES src/*.c src/*.yasm)

add_executable(ProcessWaitTerminated.exe ${APP_HELLOWORLD_SOURCES})
target_include_directories(ProcessWaitTerminated.exe PUBLIC $<$<COMPILE_LANGUAGE:C>:${APP_INCLUDES}>)
target_compile_options(ProcessWaitTerminated.exe PRIVATE ${APP_FLAGS} PRIVATE ${APP_PDB_FLAG})
target_compile_definitions(ProcessWaitTerminated.exe PRIVATE ${GLOBAL_DEFINES} PRIVATE ${MBCS_DEFINE})
target_link_libraries(ProcessWaitTerminated.exe PRIVATE CommonLibNoLocks UsermodeLibrary)
target_link_options(ProcessWaitTerminated.exe PRIVATE ${APP_LINK_FLAGS})

install(TARGETS ProcessWaitTerminated.exe DESTINATION apps/ProcessWaitTerminated)
install(FILES $<TARGET_FILE_DIR:ProcessWaitTerminated.exe>/ProcessWaitTerminated.pdb DESTINATION apps/ProcessWaitTerminated OPTIONAL)
