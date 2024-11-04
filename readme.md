
## Setup

Download and install:

- qemu
- Visual Studio 2022 (2019 should also work), if you want to build with MSVC (HAL crashes now with MSVC)
- CMake 3.30.2
- ninja
- nasm
- python and the requests package

## Bootstrap

1. Run bootstrap_elf.py, it will download the needed compilers (x86_64-w64-mingw32-gcc for the bootloader and x86_64-elf-gcc for HAL) and OVMF
2. If it succeeds run configure_elf.py, otherwise contact support
3. If it fails contact support

## Build

Visual Studio: 
To build the project, open **"Developer Powershell for Visual Studio 2022"** (can be found in the start menu, under the "Visual Studio 2022" folder) and run `Build.ps1`.

GCC:
Run build_elf.py to compile everything and prepare the debug information for GDB

## Run

TBD
Run using `Run.ps1`.

## Clean

To clean the build directory run the clean_elf.py script, this will build the clean target 
To start with a clean slate run deepclean_elf.py (this will delete the build directories), then you need to bootstrap again.
