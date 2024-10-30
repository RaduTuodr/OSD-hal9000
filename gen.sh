#!/bin/zsh
ROOT_DIR=`pwd`
BUILD_DIR="${ROOT_DIR}/artifacts"

echo 'Stripping debug information'

./tools/elfgcc/bin/x86_64-elf-objcopy --only-keep-debug artifacts/bin/HAL9000.bin artifacts/bin/HAL9000.dbg
./tools/elfgcc/bin/x86_64-elf-strip --strip-debug --strip-unneeded artifacts/bin/HAL9000.bin
./tools/elfgcc/bin/x86_64-elf-objcopy --add-gnu-debuglink="artifacts/bin/HAL9000.dbg" artifacts/bin/HAL9000.bin

echo 'Generating hard disk image...'
cd $BUILD_DIR
dd if=/dev/zero of=bin/bootloader.img bs=512 count=187500
mformat -i bin/bootloader.img -f 2880 -F -v BOOT ::
mmd -i bin/bootloader.img ::/EFI
mmd -i bin/bootloader.img ::/EFI/BOOT
mmd -i bin/bootloader.img ::/EFI/OS
mmd -i bin/bootloader.img ::/EFI/MODULES
mmd -i bin/bootloader.img ::/APPS
# mcopy -i bin/bootloader.img ../Tests ::/EFI/MODULES
mcopy -i bin/bootloader.img bin/HAL9000.bin ::/EFI/OS
# mcopy -i bin/bootloader.img ../acpidump.efi ::/EFI/
mcopy -i bin/bootloader.img bin/BOOTX64.EFI ::/EFI/BOOT
# mcopy -i bin/bootloader.img bin/AppHelloWorld.exe ::/APPS
# mcopy -i bin/bootloader.img bin/app ::/APPS
# mcopy -i bin/bootloader.img bin/Test ::/APPS
# mcopy -i bin/bootloader.img bin/elf.exe ::/APPS
# mcopy -i bin/bootloader.img bin/HAL9000.ini ::
