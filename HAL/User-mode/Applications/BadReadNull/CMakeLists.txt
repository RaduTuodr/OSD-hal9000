cmake_minimum_required(VERSION 3.30.2 FATAL_ERROR)

set(APP_INCLUDES
    ${PROJECT_SOURCE_DIR}/Shared/common
)

set(APP_PDB_FLAG
    $<$<COMPILE_LANGUAGE:C>:/Fd:$<TARGET_FILE_DIR:BadReadNull.exe>/BadReadNull.pdb>
)

file(GLOB_RECURSE APP_HELLOWORLD_SOURCES src/*.c src/*.yasm)

add_executable(BadReadNull.exe ${APP_HELLOWORLD_SOURCES})
target_include_directories(BadReadNull.exe PUBLIC $<$<COMPILE_LANGUAGE:C>:${APP_INCLUDES}>)
target_compile_options(BadReadNull.exe PRIVATE ${APP_FLAGS} PRIVATE ${APP_PDB_FLAG})
target_compile_definitions(BadReadNull.exe PRIVATE ${GLOBAL_DEFINES} PRIVATE ${MBCS_DEFINE})
target_link_libraries(BadReadNull.exe PRIVATE CommonLibNoLocks UsermodeLibrary)
target_link_options(BadReadNull.exe PRIVATE ${APP_LINK_FLAGS})

install(TARGETS BadReadNull.exe DESTINATION apps/BadReadNull)
install(FILES $<TARGET_FILE_DIR:BadReadNull.exe>/BadReadNull.pdb DESTINATION apps/BadReadNull OPTIONAL)
