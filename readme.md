
## Setup

Download and install:

- qemu, it must be in your PATH.
- Visual Studio 2022 (if you are on Windows), ImageCreator needs to be built for your system (HAL crashes now with MSVC).
- CMake 3.28.3 or higher.
- ninja, it must in your PATH.
- nasm (yasm cannot produce ELF from what I observed), it must be in your PATH.
- python3 (3.10 on Windows and macOS 3.12 also works, blame lldb on Windows it searches for python310.dll) and some required packages if the script fails to run.
- llvm toolchain, in tools/llvm (it might work if you have it in your PATH); more specifically you need clang, ld.lld, lld-link, lldb, llvm-objcopy, llvm-strip; llvm-readelf and llvm-addr2line are strongly recommended; the simplest
way to get clang is to download the release binaries from github and just copy-paste the contents in tools/llvm
- CodeLLDB, Visual Studio Code extension for debugging; a launch.json is already provided

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
