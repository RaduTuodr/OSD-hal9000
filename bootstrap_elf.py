import os
import sys
import time
from urllib import request
from tarfile import TarFile
import warnings
import subprocess
import shutil
import json
import platform
import lzma

def reporthook(count, block_size, total_size):
    global start_time
    if count == 0:
        start_time = time.time()
        return
    duration = time.time() - start_time
    progress_size = int(count * block_size)
    speed = int(progress_size / (1024 * duration))
    percent = int(count * block_size * 100 / total_size)
    sys.stdout.write('\r   %d%%, %d MB, %d KB/s, %d seconds passed' %
                    (percent, progress_size / (1024 * 1024), speed, duration))
    sys.stdout.flush()

def download_lfs_file(github_url, filename, temp_dir):
    request.urlretrieve(f'{github_url}/{filename}', f'temp/{filename}.info')
    f = open(f'temp/{filename}.info')
    lines = f.readlines()
    f.close()
    sha = lines[1].split()[1].replace('sha256:', '')
    size = lines[2].split()[1]
    json_body =f'{{"operation": "download", "transfer": ["basic"], "objects": [{{"oid": "{sha}", "size": {size}}}]}}'
    req = f"curl -X POST -H \"Accept: application/vnd.git-lfs+json\" -H \"Content-type: application/json\" -d '{json_body}' https://github.com/davidsipos1002/UefiHAL9000Tools.git/info/lfs/objects/batch"
    get_download = subprocess.Popen(req, stdout=subprocess.PIPE, shell=True)
    get_download.wait()
    response_json = json.load(get_download.stdout)
    download_link = response_json['objects'][0]['actions']['download']['href']
    request.urlretrieve(download_link, f'temp/{filename}', reporthook=reporthook)

def main():
    warnings.filterwarnings('ignore')
    github_url = 'https://raw.githubusercontent.com/davidsipos1002/UefiHAL9000Tools/master/archives'

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

    os.makedirs('temp', exist_ok=True)

    if not os.path.exists('tools/mingw_gcc'):
        print(f'Downloading {mingw_archive}...')
        download_lfs_file(github_url, mingw_archive, 'temp')
        print('Done.')

        print(f'Decompressing {mingw_archive}...')
        xz_file = lzma.LZMAFile(f'temp/{mingw_archive}')
        tar_file = TarFile.open(mode='r', fileobj=xz_file)
        tar_file.extractall(f'tools/mingw_gcc')
        xz_file.close()
        print('Done.')

    if not os.path.exists('tools/elf_gcc'):
        print(f'Downloading {elf_archive}...')
        download_lfs_file(github_url, elf_archive, 'temp')
        print('Done.')

        print(f'Decompressing {elf_archive}...')
        xz_file = lzma.LZMAFile(f'temp/{elf_archive}')
        tar_file = TarFile.open(mode='r', fileobj=xz_file)
        tar_file.extractall(f'tools/elf_gcc')
        xz_file.close()
        print('Done.')

    if not os.path.exists('tools/OVMF'):
        os.makedirs('tools/OVMF', exist_ok=True)
        print(f'Downloading OVMF.fd...')
        request.urlretrieve('https://github.com/davidsipos1002/UefiHAL9000Tools/raw/refs/heads/master/OVMF/OVMF.fd', f'tools/OVMF/OVMF.fd')
        print('Done.')

    shutil.rmtree('temp', ignore_errors=True)


if __name__ == '__main__':
    main()