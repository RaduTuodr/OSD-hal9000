
## Setup

Download and install:

- qemu.
- Visual Studio 2022 (if you are on Windows), ImageCreator needs to be built for your system (HAL crashes now with MSVC).
- CMake 3.30.2.
- ninja.
- nasm (yasm cannot produce ELF from what I observed).
- python3 (3.10 on Windows and macOS 3.12 also works, blame lldb) and some required packages if the script fails to run.
- llvm toolchain, in tools/llvm; more specifically you need clang, ld.lld, lld-link, lldb, llvm-objcopy, llvm-strip; llvm-readelf is strongly recommended; the simplest
way to get clang is to download the release binaries from github and just copy-paste the contents in tools/llvm

## Bootstrap

1. Run `HAL9000.py --bootstrap`, it will download OVMF (UEFI implementation for QEMU).
2. If it succeeds run `HAL9000.py --configure`, otherwise contact support.
3. If it fails contact support.
4. If it still fails go and watch 2001: A Space Odyssey.

## Build

<!-- Visual Studio: 
To build the project, open **"Developer Powershell for Visual Studio 2022"** (can be found in the start menu, under the "Visual Studio 2022" folder) and run `Build.ps1`. -->

LLVM:
Run `HAL9000.py --build_all` to compile everything, prepare the debug information and generate the QEMU image.

Run `HAL9000.py --build` to build just HAL.

## Run

<!-- Visual Studio:
Run using `Run.ps1`. -->

LLVM:
Run with `HAL9000.py --run`, use the `-d` flag if you want QEMU to wait for the debugger.

## Clean

To clean the build directory of all projects run `HAL9000.py --clean_all`.

To clean the build directory of HAL run `HAL9000.py --clean`.

To start with a clean slate run `HAL9000.py --deep_clean` (this will delete the build directories), then you need to configure again.

## Help

Run `HAL9000.py -h` or `HAL9000.py --help` to see all options.
