
## Setup

Download and install:

- qemu
- Visual Studio 2022 (2019 should also work)
- CMake 3.30.2

Download <https://www.kraxel.org/repos/jenkins/edk2/edk2.git-ovmf-x64-0-20220719.209.gf0064ac3af.EOL.no.nore.updates.noarch.rpm> and unzip the files in `/usr/share/edk2.git/ovmf-x64` to `./ovmf-x64`

## Build

To build the project, open **"Developer Powershell for Visual Studio 2022"** (can be found in the start menu, under the "Visual Studio 2022" folder) and run `Build.ps1`.

## Run

Run using `Run.ps1`.
