import subprocess 

def main():
    print('Building UefiBootloader...')
    p = subprocess.run(f'cmake --build build -j4',
                       cwd='UefiBootloader',
                       shell=True)
    print('Done.')

    print('Building HAL...')
    p = subprocess.run(f'cmake --build build -j4',
                       cwd='HAL',
                       shell=True)
    print('Done.')
    
    print('Installing UefiBootloader...')
    p = subprocess.run(f'cmake --install build',
                       cwd='UefiBootloader',
                       shell=True)
    print('Done.')

    print('Installing HAL...')
    p = subprocess.run(f'cmake --install build',
                       cwd='HAL',
                       shell=True)
    print('Done.')

    print('Separating debug information...')
    p = subprocess.run(f'./tools/elf_gcc/bin/x86_64-elf-objcopy --only-keep-debug artifacts/bin/HAL9000.bin artifacts/bin/HAL9000.dbg',
                       shell=True)

    p = subprocess.run(f'./tools/elf_gcc/bin/x86_64-elf-strip --strip-debug --strip-unneeded artifacts/bin/HAL9000.bin',
                       shell=True)
    
    p = subprocess.run(f'./tools/elf_gcc/bin/x86_64-elf-objcopy --add-gnu-debuglink="artifacts/bin/HAL9000.dbg" artifacts/bin/HAL9000.bin',
                       shell=True)
    print('Done.')

if __name__ == '__main__':
    main()