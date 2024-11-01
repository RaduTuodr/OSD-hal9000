set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR x86_64)
set(CMAKE_CONFIGURATION_TYPES Debug Release)

# Set C compile commands

set(CMAKE_C_COMPILER_WORKS 1)

if (CMAKE_HOST_SYSTEM_NAME STREQUAL "Windows")

      set(CMAKE_C_COMPILE_OBJECT
            "<CMAKE_C_COMPILER> <DEFINES> <INCLUDES> <FLAGS> /c /Fo:<OBJECT> <SOURCE>"
      )

      set(CMAKE_C_LINK_EXECUTABLE
            "<CMAKE_LINKER> <CMAKE_C_LINK_FLAGS> <LINK_FLAGS> /OUT:<TARGET> <OBJECTS> <LINK_LIBRARIES>"
      )

      set(CMAKE_C_CREATE_STATIC_LIBRARY
            "<CMAKE_AR> <FLAGS> <LINK_FLAGS> /NOLOGO /OUT:<TARGET> <OBJECTS>"
      )

else()
      find_program(CMAKE_C_COMPILER
            NAMES "x86_64-w64-mingw32-gcc"
            HINTS ${CMAKE_SOURCE_DIR}/tools/pegcc/bin
            REQUIRED
      )

      find_program(CMAKE_LINKER
            NAMES "x86_64-w64-mingw32-gcc"
            HINTS ${CMAKE_SOURCE_DIR}/tools/pegcc/bin
            REQUIRED
      )

      find_program(CMAKE_AR
            NAMES "x86_64-w64-mingw32-ar"
            HINTS ${CMAKE_SOURCE_DIR}/tools/pegcc/bin
            REQUIRED
      )

      set(CMAKE_C_COMPILE_OBJECT
            "<CMAKE_C_COMPILER> <DEFINES> <INCLUDES> <FLAGS> -c -o <OBJECT> <SOURCE>"
      )

      set(CMAKE_C_LINK_EXECUTABLE
            "<CMAKE_LINKER> <CMAKE_C_LINK_FLAGS> <LINK_FLAGS> -o <TARGET> <OBJECTS> <LINK_LIBRARIES>"
      )

      set(CMAKE_C_CREATE_STATIC_LIBRARY
            "<CMAKE_AR> rcs <TARGET> <OBJECTS>"
      )
endif()

set(CMAKE_C_FLAGS_INIT)
set(CMAKE_C_LINK_FLAGS_INIT)

# Set filenames
set(CMAKE_STATIC_LIBRARY_PREFIX_C "")
set(CMAKE_STATIC_LIBRARY_SUFFIX_C .lib)
set(CMAKE_C_OUTPUT_EXTENSION .obj)
set(CMAKE_EXECUTABLE_SUFFIX_C "")
