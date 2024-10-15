cmake_minimum_required(VERSION 3.30.2 FATAL_ERROR)

project(HAL LANGUAGES C)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake/yasm")
list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")
enable_language(YASM)

include(Flags)

set(HAL9000_HEADERS
    ${CMAKE_CURRENT_LIST_DIR}/HAL/HAL9000/headers/apps
    ${CMAKE_CURRENT_LIST_DIR}/HAL/HAL9000/headers/base
    ${CMAKE_CURRENT_LIST_DIR}/HAL/HAL9000/headers/boot
    ${CMAKE_CURRENT_LIST_DIR}/HAL/HAL9000/headers/core
    ${CMAKE_CURRENT_LIST_DIR}/HAL/HAL9000/headers/core/cpu
    ${CMAKE_CURRENT_LIST_DIR}/HAL/HAL9000/headers/core/io
    ${CMAKE_CURRENT_LIST_DIR}/HAL/HAL9000/headers/core/memory
    ${CMAKE_CURRENT_LIST_DIR}/HAL/HAL9000/headers/crt
    ${CMAKE_CURRENT_LIST_DIR}/HAL/HAL9000/headers/debug/dump
    ${CMAKE_CURRENT_LIST_DIR}/HAL/HAL9000/headers/debug/test
    ${CMAKE_CURRENT_LIST_DIR}/HAL/HAL9000/headers/debug/test/threads
    ${CMAKE_CURRENT_LIST_DIR}/HAL/HAL9000/headers/debug/test/userprog
    ${CMAKE_CURRENT_LIST_DIR}/HAL/HAL9000/headers/devices/apic
    ${CMAKE_CURRENT_LIST_DIR}/HAL/HAL9000/headers/devices/keyboard
    ${CMAKE_CURRENT_LIST_DIR}/HAL/HAL9000/headers/devices/serial
    ${CMAKE_CURRENT_LIST_DIR}/HAL/HAL9000/headers/executive
    ${CMAKE_CURRENT_LIST_DIR}/HAL/HAL9000/headers/usermode
)

add_subdirectory(CompilerAbstraction)

add_subdirectory(UefiBootloader)

add_subdirectory(HAL)
