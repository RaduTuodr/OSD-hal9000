import subprocess

def main():
    print('Configuring UefiBootloader...')
    p = subprocess.run(f'cmake -S . -B build -G "Ninja" -DCMAKE_BUILD_TYPE=Debug -DCMAKE_TOOLCHAIN_FILE:PATH="../cmake/UefiBootloaderToolchain.cmake" -DCMAKE_INSTALL_PREFIX:PATH="../artifacts" -DUEFI_BUILD:BOOL="TRUE" -DFORCE_ELF:BOOL="TRUE"',
                       cwd='UefiBootloader',
                       shell=True)
    print('Done.')

    print('Configuring HAL...')
    p = subprocess.run(f'cmake -S . -B build -G "Ninja" -DCMAKE_BUILD_TYPE=Debug -DCMAKE_TOOLCHAIN_FILE:PATH="../cmake/HalToolchain.cmake" -DCMAKE_INSTALL_PREFIX:PATH="../artifacts" -DFORCE_ELF:BOOL="TRUE"',
                       cwd='HAL',
                       shell=True)
    print('Done.')

if __name__ == '__main__':
    main()