cmake_minimum_required(VERSION 3.28.3 FATAL_ERROR)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_SCAN_FOR_MODULES OFF)

project(ImageCreator LANGUAGES C CXX)

file(GLOB_RECURSE SOURCES src/*.cpp src/*.c)

add_executable(${PROJECT_NAME} ${SOURCES})
target_include_directories(${PROJECT_NAME} PRIVATE ${CMAKE_SOURCE_DIR}/include)

install(TARGETS ${PROJECT_NAME} DESTINATION bin)
