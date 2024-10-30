#!/bin/zsh
echo 'Starting QEMU...'
qemu-system-x86_64 -bios artifacts/bin/OVMF.fd \
                   -m 2G \
                   -device piix3-ide,id=ide \
                   -drive id=disk,file=artifacts/bin/bootloader.img,format=raw,if=none \
                   -device ide-hd,drive=disk,bus=ide.0 \
                   -device e1000e \
                   -smp 4 \
                   -machine q35 \
                   -monitor stdio \
                   -chardev file,id=char0,path=serial1.log \
                   -serial chardev:char0 \
                   -s -S