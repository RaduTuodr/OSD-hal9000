import subprocess

def main():
    print('Cleaning UefiBootloader...')
    p = subprocess.run(f'cmake --build build -j4 --target clean',
                       cwd='UefiBootloader',
                       shell=True)
    print('Done.')

    print('Cleaning HAL...')
    p = subprocess.run(f'cmake --build build -j4 --target clean',
                       cwd='HAL',
                       shell=True)
    print('Done.')
    
if __name__ == '__main__':
    main()