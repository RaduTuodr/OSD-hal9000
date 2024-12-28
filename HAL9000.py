import sys
import os
import argparse
import shutil
import platform
import subprocess
import multiprocessing
import json

if str(platform.system()).lower() == 'linux':
    import distro

HOMEBREW_PACKAGES = [
    'qemu',
    'cmake',
    'ninja',
    'nasm',
    'llvm',
]

APT_PACKAGES = [
    'qemu-system',
    'cmake',
    'ninja-build',
    'nasm',
    'llvm',
    'clang',
    'clang-tools',
    'lld',
    'lldb'
]

DNF_PACKAGES = [
    'qemu',
    'cmake',
    'ninja-build',
    'nasm',
    'llvm',
    'clang',
    'clang-tools-extra',
    'lld',
    'lldb'
]

WINGET_PACKAGES = [
    'SoftwareFreedomConservancy.QEMU',
    'Kitware.CMake',
    'Ninja-build.Ninja',
    'NASM.NASM',
    'LLVM.LLVM'
]

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
    plat_system = str(platform.system()).lower()
    if plat_system == 'darwin':
        env['PATH'] = f'/opt/homebrew/opt/llvm/bin{os.pathsep}/usr/local/opt/llvm/bin{os.pathsep}{os.path.abspath("tools/llvm/bin")}{os.pathsep}{env["PATH"]}'
    elif plat_system == 'windows':
        env['PATH'] = f'{os.path.join(os.getenv("LOCALAPPDATA"), "bin", "NASM")}{os.pathsep}{env["PATH"]}'
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

def run_cmd_with_echo_and_wait(cmd):
    prYellow(f'Will run: {cmd}. Press any key to continue.')
    input()
    p = subprocess.run(cmd, shell=True)
    return p.returncode == 0

def bootstrap_generic(pkg_manager_cmd, packages, ignore=False):
    prYellow('The following packages will be installed:')
    for package in packages:
        prLightGray(package)

    for package in packages:
        prCyan(f'Installing {package}...')
        if not run_cmd_with_echo_and_wait(f'{pkg_manager_cmd} {package}') and not ignore:
            prRed(f'Error installing {package}!')
            return False
        prGreen('Done.')
    
    return True

def bootstrap_darwin():
    prCyan('Bootrapping for macOS')
    
    prCyan('Checking for Homebrew...')
    p = subprocess.run('which brew',
                       shell=True,
                       stderr=subprocess.DEVNULL,
                       stdout = subprocess.DEVNULL)
    if p.returncode != 0:
        prRed('Homebrew not found. Install Homebrew to continue.')
        return False
    prGreen('Done.')

    return bootstrap_generic('brew install', HOMEBREW_PACKAGES)

def bootstrap_linux():
    distro_id = distro.id().lower()
    if distro_id == 'ubuntu':
        pkg_manager_cmd = 'sudo apt-get install -y'
        packages = APT_PACKAGES
    elif distro_id == 'fedora':
        pkg_manager_cmd = 'sudo dnf install -y'
        packages = DNF_PACKAGES
    else:
        prRed(f'HAL was not tested on {distro_id}!. \
               You need to install the packages manually.')
        return False

    return bootstrap_generic(pkg_manager_cmd, packages)

def bootstrap():
    plat_system = str(platform.system()).lower()
    if plat_system == 'darwin':
        result = bootstrap_darwin()
    elif plat_system == 'linux':
        result = bootstrap_linux()
    elif plat_system == 'windows':
        result = bootstrap_generic('winget install', WINGET_PACKAGES, True)

    if result:
       prGreen('Successful bootstrap!')
    else:
       prRed('Failed bootstrap!')

def configure():
    generator = '\"Ninja\"'
    
    prCyan('Configuring ImageCreator...')
    p = subprocess.run(f'cmake -S . -B build -G {generator} \
                        -DCMAKE_INSTALL_PREFIX:PATH="../tools/ImageCreator" \
                        -DCMAKE_TOOLCHAIN_FILE:PATH="../cmake/ImageCreatorToolchain.cmake"',
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
                        env=get_build_env(),
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
                        env=get_build_env(),
                        shell=True)
    if p.returncode != 0:
        prRed('Error configuring HAL9000!')
        return
    prGreen('Done.')

def clean_hal(job_count):
    prCyan('Cleaning HAL9000...')
    p = subprocess.run(f'cmake --build build -j{job_count} --target clean',
                        cwd='HAL',
                        env=get_build_env(),
                        shell=True)
    if p.returncode != 0:
        prRed('Error cleaning HAL9000!')
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
                        env=get_build_env(),
                        shell=True)
    if p.returncode != 0:
        prRed('Error cleaning UefiBootloader!')
        return
    prGreen('Done.')

    clean_hal(job_count)

def build_hal(job_count):
    prCyan('Building HAL9000...')
    p = subprocess.run(f'cmake --build build -j{job_count}',
                        cwd='HAL',
                        env=get_build_env(),
                        shell=True)
    if p.returncode != 0:
        prRed('Error building HAL9000!')
        return
    prGreen('Done.')

def install_hal():
    prCyan('Installing HAL9000...')
    p = subprocess.run(f'cmake --install build',
                    cwd='HAL',
                    env=get_build_env(),
                    shell=True)
    if p.returncode != 0:
        prRed('Error installing HAL9000!')
        return
    prGreen('Done.')

def generate_qemu_image():
    prCyan('Separating debug information...')
    subprocess.run(f'"llvm-objcopy" --only-keep-debug artifacts/bin/HAL9000.bin artifacts/bin/HAL9000.dbg',
                    env=get_build_env(),
                    shell=True)

    subprocess.run(f'"llvm-strip" --strip-debug --strip-unneeded artifacts/bin/HAL9000.bin',
                    env=get_build_env(),
                    shell=True)
    
    subprocess.run(f'"llvm-objcopy" --add-gnu-debuglink="artifacts/bin/HAL9000.dbg" artifacts/bin/HAL9000.bin',
                    env=get_build_env(),
                    shell=True)
    prGreen('Done.')

    prCyan('Generating QEMU image...')
    p = subprocess.run(f'"tools/ImageCreator/bin/ImageCreator{".exe" if str(platform.system()).lower() == "windows" else ""}" "config/HAL9000.json"',
                        env=get_build_env(),
                        shell=True)
    if p.returncode != 0:
        prRed('Error generating QEMU image!')
    prGreen('Done.')

def build_all(job_count):
    if str(platform.system()).lower() == 'windows':
        build_type = '--config Release'
    else:
        build_type = ''

    prCyan('Building ImageCreator...')
    p = subprocess.run(f'cmake --build build -j{job_count} {build_type}',
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
                        env=get_build_env(),
                        shell=True)
    if p.returncode != 0:
        prRed('Error building UefiBootloader!')
        return
    prGreen('Done.')

    build_hal(job_count)
    
    prCyan('Installing ImageCreator...')
    p = subprocess.run(f'cmake --install build {build_type}',
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
                        env=get_build_env(),
                        shell=True)
    if p.returncode != 0:
        prRed('Error installing UefiBootloader!')
        return
    prGreen('Done.')

    install_hal()

    generate_qemu_image()

def build(job_count):
    build_hal(job_count)

    install_hal() 

    generate_qemu_image()

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
    subprocess.run(f'qemu-system-x86_64{".exe" if str(platform.system()).lower() == "windows" else ""} \
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
        clean_hal(args['j'])
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
