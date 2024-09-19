cmake_minimum_required(VERSION 3.30.2 FATAL_ERROR)

set(NETWORK_PORT_INCLUDES
    ${HAL9000_HEADERS}
    ${CMAKE_CURRENT_LIST_DIR}/headers
    ${PROJECT_SOURCE_DIR}/CommonLib/inc
    ${PROJECT_SOURCE_DIR}/Shared/common
    ${PROJECT_SOURCE_DIR}/Shared/kernel
    ${PROJECT_SOURCE_DIR}/HAL/inc
)

set(NETWORK_PORT_PDB_FLAG
    $<$<COMPILE_LANGUAGE:C>:/Fd:$<TARGET_FILE_DIR:NetworkPort>/NetworkPort.pdb>
)

file(GLOB_RECURSE NETWORK_PORT_SOURCES src/*.c src/*.yasm)

add_library(NetworkPort STATIC ${NETWORK_PORT_SOURCES})
target_include_directories(NetworkPort PRIVATE $<$<COMPILE_LANGUAGE:C>:${NETWORK_PORT_INCLUDES}> PUBLIC $<$<COMPILE_LANGUAGE:C>:${CMAKE_CURRENT_LIST_DIR}/inc>)
target_compile_options(NetworkPort PRIVATE ${GLOBAL_FLAGS} PRIVATE ${GL_RELEASE_FLAG} PRIVATE ${NETWORK_PORT_PDB_FLAG})
target_compile_definitions(NetworkPort PRIVATE ${GLOBAL_DEFINES} PRIVATE ${MDBCS_DEFINE}) 

install(TARGETS NetworkPort DESTINATION lib)
install(FILES $<TARGET_FILE_DIR:NetworkPort>/NetworkPort.pdb DESTINATION lib OPTIONAL)
