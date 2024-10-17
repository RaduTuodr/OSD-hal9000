cmake_minimum_required(VERSION 3.30.2 FATAL_ERROR)

project(YasmHAL)

include(ExternalProject)

ExternalProject_Add(Yasm
    GIT_REPOSITORY https://github.com/yasm/yasm.git
    SOURCE_DIR ${CMAKE_SOURCE_DIR}/yasm_repo
    BINARY_DIR ${CMAKE_BINARY_DIR}/yasm_repo
    CMAKE_ARGS
        -DCMAKE_INSTALL_PREFIX:PATH=${CMAKE_SOURCE_DIR}/../tools/yasm
        -DBUILD_SHARED_LIBS=OFF
)
