## Introduction

Repository structure:
- `.vscode` &rarr; contains `launch.json`.
- `artifacts` &rarr; will contain the final build artifacts.
- `cmake` &rarr; `CMake` toolchain configuration files. 
- `config`:
    - `HAL9000.ini` &rarr; indicates which is the system partition.
    - `HAL9000.json` &rarr; describes the disk layout and contents.
    - `QEMU.json` &rarr; contains all arguments passed to `QEMU`.
    - `Tests` &rarr; the boot module used for running commands after `HAL` boots.
- `ConfigGen` &rarr; scripts used to generate some of the configuration files.
- `HAL` &rarr; `HAL's` source code.
- `HalDbg` &rarr; `python` scripts for the custom commands.
- `ImageCreator` &rarr; sources of the program which generates the disk image.
- `tools`:
    - `OVMF` &rarr; `UEFI` firmware implementation for `QEMU`, built using `EDK2`.
    - `ImageCreator` &rarr; will contain the executable of `ImageCreator`.
- `UefiBootloader` &rarr; source code of the `UEFI` bootloader used for loading `HAL` and its boot modules.
- `yasm` &rarr; not used anymore.
- `HAL9000.py` &rarr; utility script. 

## Debugger commands

- `hal_commands`
- `list_threads`
- `dump_thread`
- `list_processes`
- `dump_process`
- `list_running_threads`
- `list_file_objects`
- `dump_file_object`
- `list_cpus`
- `dump_cpu`

Run `help <command>` in `lldb` to see description.

## Prerequisites

Install `Visual Studio Code` and the `CodeLLDB` extensions.
Install `python3`.

Tools used by `HAL`:
- `qemu` &rarr; the emulator.
- `CMake` &rarr; build configuration generator.
- `ninja` &rarr; build tool.
- `nasm` &rarr; x86_64 assembler (`yasm` cannot be used, it is not capable of producing `ELF` binaries).
- `llvm toolchain` &rarr; all code in this repository is built using LLVM.
- `python3` &rarr; used for interacting with `HAL` and the debugger (3.10 should be fine but if you get errors try another version).
- `CodeLLDB` &rarr; Visual Studio Code debugging extension for `LLDB`; a `launch.json` is already provided for attaching to `QEMU`.

Useful tools for development:
- `lldb` &rarr; the debugger.
- `qemu monitor` &rarr; lets you peek into the running VM.
- `llvm-addr2line` &rarr; converts an address to a location in the code.
- `llvm-readelf` &rarr; provides detailed information about `ELF` binaries and static libraries.

## Bootstrap

The `HAL9000.py` installs for you the required packages, provided you have `python3`.

1. Run `HAL9000.py --bootstrap`, downloads the necessary software.
2. If it succeeds run `HAL9000.py --configure`, this will configure `CMake`.

**NOTE**:
- If you have problems installing `LLVM` on `Windows` using the script, download and run the installer 
  used by `winget` (the link is displayed during bootstrap).
- Configure must be run if you add new files to the project.

## Build

<!-- Visual Studio: 
To build the project, open **"Developer Powershell for Visual Studio 2022"** (can be found in the start menu, under the "Visual Studio 2022" folder) and run `Build.ps1`. -->

Run `HAL9000.py --build_all` to compile everything, prepare the debug information and generate the `QEMU` image.

Run `HAL9000.py --build` to build just HAL, prepare the debug information and generate the `QEMU` image.

## Run

<!-- Visual Studio:
Run using `Run.ps1`. -->

Run with `HAL9000.py --run`, use the `-d` flag if you want to attach the debugger to the virtual machine.

**TODO**:
`HAL9000.py --run-tests Module`

## Clean

To clean the build directory of all projects run `HAL9000.py --clean_all`, runs every `clean` target.

To clean the build directory of HAL run `HAL9000.py --clean`, runs HAL's `clean` target.

To start with a clean slate run `HAL9000.py --deep_clean` (this will delete the build directories), then you need to configure again.

## Help

Run `HAL9000.py -h` or `HAL9000.py --help` to see all options.
