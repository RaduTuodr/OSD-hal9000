import shutil 

def main():
    print('Deep cleaning UefiBootloader...')
    shutil.rmtree('UefiBooloader/build', ignore_errors=True)
    print('Done.')

    print('Deep cleaning HAL...')
    shutil.rmtree('HAL/build', ignore_errors=True)
    print('Done.')
    
    print('Installing UefiBootloader...')
    shutil.rmtree('artifacts', ignore_errors=True)
    print('Done.')

    print('Configure must be run now!')

if __name__ == '__main__':
    main()