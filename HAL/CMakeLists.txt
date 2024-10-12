cmake_minimum_required(VERSION 3.30.2 FATAL_ERROR)

project(HAL9000 LANGUAGES C)

add_subdirectory(CommonLib)

add_subdirectory(Filesystems/FAT32)
add_subdirectory(Filesystems/SwapFS)

add_subdirectory(Misc/ELF_Parser)
add_subdirectory(Misc/PE_Parser)

add_subdirectory(Networking/Eth_82574L)
add_subdirectory(Networking/NetworkPort)
add_subdirectory(Networking/NetworkStack)

add_subdirectory(Storage/Ata)
add_subdirectory(Storage/Disk)
add_subdirectory(Storage/Volume)

add_subdirectory(User-mode/Utils/UsermodeLibrary)
add_subdirectory(User-mode/Applications)

add_subdirectory(ACPI)

add_subdirectory(HAL)
add_subdirectory(HAL9000)
