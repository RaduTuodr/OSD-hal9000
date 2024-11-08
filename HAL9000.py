import sys
import os
import argparse
import shutil
import time
from urllib import request
import warnings
import platform
import tempfile
from tarfile import TarFile
import lzma
import subprocess
import multiprocessing
import json

tools_url = 'https://raw.githubusercontent.com/davidsipos1002/UefiHAL9000Tools/master'

def prRed(str): print("\033[91m {}\033[00m" .format(str))

def prGreen(str): print("\033[92m {}\033[00m" .format(str))

def prYellow(str): print("\033[93m {}\033[00m" .format(str))

def prLightPurple(str): print("\033[94m {}\033[00m" .format(str))

def prPurple(str): print("\033[95m {}\033[00m" .format(str))

def prCyan(str): print("\033[96m {}\033[00m" .format(str))

def prLightGray(str): print("\033[97m {}\033[00m" .format(str))

def prBlack(str): print("\033[98m {}\033[00m" .format(str))

def get_build_env():
    env = os.environ.copy()
    if str(platform.system()).lower() == 'windows':
        env['PATH'] = f'{os.path.abspath('tools/mingw_gcc/bin')}{os.pathsep}{env['PATH']}'
    return env

def deep_clean():
    prCyan('Deep cleaning ImageCreator...')
    shutil.rmtree('ImageCreator/build', ignore_errors=True)
    prGreen('Done.')

    prCyan('Deep cleaning UefiBootloader...')
    shutil.rmtree('UefiBootloader/build', ignore_errors=True)
    prGreen('Done.')

    prCyan('Deep cleaning HAL...')
    shutil.rmtree('HAL/build', ignore_errors=True)
    prGreen('Done.')
    
    prCyan('Deep cleaning artifacts...')
    shutil.rmtree('artifacts', ignore_errors=True)
    prGreen('Done.')

    prYellow('Configure must be run now!')

def reporthook(count, block_size, total_size):
    global start_time
    if count == 0:
        start_time = time.time()
        return
    duration = time.time() - start_time
    progress_size = int(count * block_size)
    if duration:
        speed = int(progress_size / (1024 * duration))
    else:
        speed = 0
    percent = int(count * block_size * 100 / total_size)
    sys.stdout.write('\r   \033[97m %d%%, %d MB, %d KB/s, %d seconds passed \033[00m' %
                    (percent, progress_size / (1024 * 1024), speed, duration))
    sys.stdout.flush()

def bootstrap():
    warnings.filterwarnings('ignore')

    arch = str(platform.machine()).lower()
    os_name = str(platform.system()).lower()

    if arch == 'x64' or arch == 'x86_64':
        arch = 'amd64'
    elif arch == 'aarch64':
        arch = 'arm64'

    if os_name == 'windows':
        arch='amd64'
    
    mingw_archive = f'{arch}-{os_name}-mingw-gcc.tar.xz'
    elf_archive = f'{arch}-{os_name}-elf-gcc.tar.xz'

    with tempfile.TemporaryDirectory() as temp_dir:
        if not os.path.exists('tools/mingw_gcc'):
            prCyan(f'Downloading {mingw_archive}...')
            request.urlretrieve(f'{tools_url}/archives/{mingw_archive}', f'{temp_dir}/{mingw_archive}', reporthook=reporthook)
            prGreen('Done.')

            prCyan(f'Decompressing {mingw_archive}...')
            xz_file = lzma.LZMAFile(f'{temp_dir}/{mingw_archive}')
            tar_file = TarFile.open(mode='r', fileobj=xz_file)
            tar_file.extractall(f'tools/mingw_gcc')
            xz_file.close()
            prGreen('Done.')

        if not os.path.exists('tools/elf_gcc'):
            prCyan(f'Downloading {elf_archive}...')
            request.urlretrieve(f'{tools_url}/archives/{elf_archive}', f'{temp_dir}/{elf_archive}', reporthook=reporthook)
            prGreen('Done.')

            prCyan(f'Decompressing {elf_archive}...')
            xz_file = lzma.LZMAFile(f'{temp_dir}/{elf_archive}')
            tar_file = TarFile.open(mode='r', fileobj=xz_file)
            tar_file.extractall(f'tools/elf_gcc')
            xz_file.close()
            prGreen('Done.')

        if not os.path.exists('tools/OVMF'):
            os.makedirs('tools/OVMF', exist_ok=True)
            prCyan(f'Downloading OVMF.fd...')
            request.urlretrieve(f'{tools_url}/OVMF/OVMF.fd', f'tools/OVMF/OVMF.fd', reporthook=reporthook)
            prGreen('Done.')
        
def configure():
    prCyan('Configuring ImageCreator...')
    p = subprocess.run(f'cmake -S . -B build -G "Ninja" -DCMAKE_BUILD_TYPE=Release \
                        -DCMAKE_INSTALL_PREFIX:PATH="../tools/ImageCreator"',
                        cwd='ImageCreator',
                        env=get_build_env(),
                        shell=True)
    if p.returncode != 0:
        prRed('Error configuring ImageCreator!')
        return
    prGreen('Done.')

    prCyan('Configuring UefiBootloader...')
    p = subprocess.run(f'cmake -S . -B build -G "Ninja" -DCMAKE_BUILD_TYPE=Debug \
                        -DCMAKE_TOOLCHAIN_FILE:PATH="../cmake/UefiBootloaderToolchain.cmake" \
                        -DCMAKE_INSTALL_PREFIX:PATH="../artifacts" -DUEFI_BUILD:BOOL="TRUE" -DFORCE_ELF:BOOL="TRUE"',
                        cwd='UefiBootloader',
                        shell=True)
    if p.returncode != 0:
        prRed('Error configuring UefiBootloader!')
        return
    prGreen('Done.')

    prCyan('Configuring HAL9000...')
    p = subprocess.run(f'cmake -S . -B build -G "Ninja" -DCMAKE_BUILD_TYPE=Debug \
                        -DCMAKE_TOOLCHAIN_FILE:PATH="../cmake/HalToolchain.cmake" \
                        -DCMAKE_INSTALL_PREFIX:PATH="../artifacts" -DFORCE_ELF:BOOL="TRUE"',
                        cwd='HAL',
                        shell=True)
    if p.returncode != 0:
        prRed('Error configuring HAL9000!')
        return
    prGreen('Done.')

def clean_all(job_count):
    prCyan('Cleaning ImageCreator...')
    p = subprocess.run(f'cmake --build build -j{job_count} --target clean',
                        cwd='ImageCreator',
                        env=get_build_env(),
                        shell=True)
    if p.returncode != 0:
        prRed('Error cleaning ImageCreator!')
        return
    prGreen('Done.')

    prCyan('Cleaning UefiBootloader...')
    p = subprocess.run(f'cmake --build build -j{job_count} --target clean',
                        cwd='UefiBootloader',
                        shell=True)
    if p.returncode != 0:
        prRed('Error cleaning UefiBootloader!')
        return
    prGreen('Done.')

    prCyan('Cleaning HAL9000...')
    p = subprocess.run(f'cmake --build build -j{job_count} --target clean',
                        cwd='HAL',
                        shell=True)
    if p.returncode != 0:
        prRed('Error cleaning HAL9000!')
        return
    prGreen('Done.')

def clean(job_count):
    prCyan('Cleaning HAL...')
    p = subprocess.run(f'cmake --build build -j{job_count} --target clean',
                    cwd='HAL',
                    shell=True)
    if p.returncode != 0:
        prRed('Error cleaning HAL9000!')
        return
    prGreen('Done.')

def build_all(job_count):
    prCyan('Building ImageCreator...')
    p = subprocess.run(f'cmake --build build -j{job_count}',
                        cwd='ImageCreator',
                        env=get_build_env(),
                        shell=True)
    if p.returncode != 0:
        prRed('Error building ImageCreator!')
        return
    prGreen('Done.')

    prCyan('Building UefiBootloader...')
    p = subprocess.run(f'cmake --build build -j{job_count}',
                        cwd='UefiBootloader',
                        shell=True)
    if p.returncode != 0:
        prRed('Error building UefiBootloader!')
        return
    prGreen('Done.')

    prCyan('Building HAL9000...')
    p = subprocess.run(f'cmake --build build -j{job_count}',
                        cwd='HAL',
                        shell=True)
    if p.returncode != 0:
        prRed('Error building HAL9000!')
        return
    prGreen('Done.')
    
    prCyan('Installing ImageCreator...')
    p = subprocess.run(f'cmake --install build',
                        cwd='ImageCreator',
                        env=get_build_env(),
                        shell=True)
    if p.returncode != 0:
        prRed('Error installing ImageCreator!')
        return
    prGreen('Done.')

    prCyan('Installing UefiBootloader...')
    p = subprocess.run(f'cmake --install build',
                        cwd='UefiBootloader',
                        shell=True)
    if p.returncode != 0:
        prRed('Error installing UefiBootloader!')
        return
    prGreen('Done.')

    prCyan('Installing HAL9000...')
    p = subprocess.run(f'cmake --install build',
                    cwd='HAL',
                    shell=True)
    if p.returncode != 0:
        prRed('Error installing HAL9000!')
        return
    prGreen('Done.')

    prCyan('Separating debug information...')
    subprocess.run(f'"tools/elf_gcc/bin/x86_64-elf-objcopy" --only-keep-debug artifacts/bin/HAL9000.bin artifacts/bin/HAL9000.dbg',
                    shell=True)

    subprocess.run(f'"tools/elf_gcc/bin/x86_64-elf-strip" --strip-debug --strip-unneeded artifacts/bin/HAL9000.bin',
                    shell=True)
    
    subprocess.run(f'"tools/elf_gcc/bin/x86_64-elf-objcopy" --add-gnu-debuglink="artifacts/bin/HAL9000.dbg" artifacts/bin/HAL9000.bin',
                    shell=True)
    prGreen('Done.')

    prCyan('Generating QEMU image...')
    p = subprocess.run(f'"tools/ImageCreator/bin/ImageCreator{'.exe' if str(platform.system()).lower() == 'windows' else ''}" "config/HAL9000.json"',
                       shell=True)
    if p.returncode != 0:
        prRed('Error generating QEMU image!')
    prGreen('Done.')

def build(job_count):
    prCyan('Building HAL9000...')
    p = subprocess.run(f'cmake --build build -j{job_count}',
                    cwd='HAL',
                    shell=True)
    if p.returncode != 0:
        prRed('Error building HAL9000!')
        return
    prGreen('Done.') 

    prCyan('Installing HAL9000...')
    p = subprocess.run(f'cmake --install build',
                        cwd='HAL',
                        shell=True)
    if p.returncode != 0:
        prRed('Error installing HAL9000!')
        return
    prGreen('Done.')

    prCyan('Separating debug information...')
    subprocess.run(f'"tools/elf_gcc/bin/x86_64-elf-objcopy" --only-keep-debug artifacts/bin/HAL9000.bin artifacts/bin/HAL9000.dbg',
                    shell=True)

    subprocess.run(f'"tools/elf_gcc/bin/x86_64-elf-strip" --strip-debug --strip-unneeded artifacts/bin/HAL9000.bin',
                    shell=True)
    
    subprocess.run(f'"tools/elf_gcc/bin/x86_64-elf-objcopy" --add-gnu-debuglink="artifacts/bin/HAL9000.dbg" artifacts/bin/HAL9000.bin',
                    shell=True)
    prGreen('Done.')

    prCyan('Generating QEMU image...')
    p = subprocess.run(f'"tools/ImageCreator/bin/ImageCreator{'.exe' if str(platform.system()).lower() == 'windows' else ''}" "config/HAL9000.json"',
                       shell=True)
    if p.returncode != 0:
        prRed('Error generating QEMU image!')
    prGreen('Done.')

def parse_qemu_options(debug):
    f = open('config/QEMU.json', 'r')
    qemu_config = json.load(f)
    f.close()

    qemu_options = ''
    for option, param in qemu_config.items():
        if isinstance(param, list):
            for p in param:
                qemu_options += f'-{option} {p} '
        else:
            qemu_options += f'-{option} {param} '

    if debug:
        qemu_options += '-s -S'

    return qemu_options

def run(debug):
    prCyan('Starting QEMU...')
    qemu_options = parse_qemu_options(debug)
    subprocess.run(f'qemu-system-x86_64{'.exe' if str(platform.system()).lower() == 'windows' else ''} \
                    {qemu_options}',
                    shell=True)

def main():
    parser = argparse.ArgumentParser(prog='HAL9000.py',
                                     description='Script for working with HAL9000',
                                     epilog='\'The 9000 series is the most reliable computer ever made. \
                                             No 9000 computer has ever made a mistake or distorted \
                                             information. We are all, by any practical definition of the words, \
                                             foolproof and incapable of error.\' - 2001: A Space Odyssey',
                                     add_help=True)

    parser.add_argument('--deep_clean',
                        help='Remove all build directories and start with a clean slate',
                        action='store_true',
                        default=False)
    parser.add_argument('--bootstrap',
                        help='Bootstrap HAL9000, use it when setting up a new project',
                        action='store_true',
                        default=False)
    parser.add_argument('--configure',
                        help='Configure the projects',
                        action='store_true',
                        default=False)
    parser.add_argument('--clean_all',
                        help='Run the clean target for all projects',
                        action='store_true',
                        default=False)
    parser.add_argument('--clean',
                        help='Run the clean target for HAL9000',
                        action='store_true',
                        default=False)
    parser.add_argument('--build_all',
                        help='Build all projects',
                        action='store_true',
                        default=False)
    parser.add_argument('--build',
                        help='Build HAL9000',
                        action='store_true',
                        default=False)
    parser.add_argument('--run',
                        help='Run HAL9000',
                        action='store_true',
                        default=False)
    parser.add_argument('-j',
                        help='Job count, use it for parallel build (default: number of CPUs)',
                        type=int,
                        required=False,
                        default=multiprocessing.cpu_count())
    parser.add_argument('-d',
                        help='Make QEMU wait for the debugger',
                        action='store_true',
                        required=False,
                        default=False)

    args = vars(parser.parse_args())

    if args['deep_clean']:
        deep_clean()
        return

    if args['bootstrap']:
        bootstrap()
        return

    if args['configure']:
        configure()
        return

    if args['clean_all']:
        clean_all(args['j'])
        return

    if args['clean']:
        clean(args['j'])
        return
    
    if args['build_all']:
        build_all(args['j'])
        return

    if args['build']:
        build(args['j'])
        return

    if args['run']:
        run(args['d'])
        return

if __name__ == '__main__':
    main()
