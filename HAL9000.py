from dataclasses import dataclass
import sys
import os
import argparse
import shutil
import platform
import subprocess
import multiprocessing
import json
import time
from tests.testing import Tester


@dataclass
class Package:
    name: str
    version: str | None = None


HOMEBREW_PACKAGES: list[Package] = [
    Package("qemu"),
    Package("cmake"),
    Package("ninja"),
    Package("nasm"),
    Package("llvm"),
]

APT_PACKAGES: list[Package] = [
    Package("qemu-system"),
    Package("cmake"),
    Package("ninja-build"),
    Package("nasm"),
    Package("llvm"),
    Package("clang"),
    Package("clang-tools"),
    Package("lld"),
    Package("lldb"),
]

DNF_PACKAGES: list[Package] = [
    Package("qemu"),
    Package("cmake"),
    Package("ninja-build"),
    Package("nasm"),
    Package("llvm"),
    Package("clang"),
    Package("clang-tools-extra"),
    Package("lld"),
    Package("lldb"),
]

WINGET_PACKAGES: list[Package] = [
    Package("SoftwareFreedomConservancy.QEMU", version="10.1.0"),
    Package("Kitware.CMake"),
    Package("Ninja-build.Ninja"),
    Package("NASM.NASM"),
    Package("LLVM.LLVM", version="19.1.7"),
    Package("Microsoft.WindowsSDK.10.0.22621"),
]


def prRed(str):
    print("\033[91m {}\033[00m".format(str))


def prGreen(str):
    print("\033[92m {}\033[00m".format(str))


def prYellow(str):
    print("\033[93m {}\033[00m".format(str))


def prLightPurple(str):
    print("\033[94m {}\033[00m".format(str))


def prPurple(str):
    print("\033[95m {}\033[00m".format(str))


def prCyan(str):
    print("\033[96m {}\033[00m".format(str))


def prLightGray(str):
    print("\033[97m {}\033[00m".format(str))


def prBlack(str):
    print("\033[98m {}\033[00m".format(str))


def get_exe_name(path: str, quote: bool = False):
    if str(platform.system()).lower() == "windows":
        path = path.replace("/", "\\")
        path = path + ".exe"
    return f'"{path}"' if quote else path


def get_build_env():
    env = os.environ.copy()
    plat_system = str(platform.system()).lower()
    if plat_system == "darwin":
        paths = [
            "/opt/homebrew/opt/llvm/bin",
            "/usr/local/opt/llvm/bin",
            os.path.abspath("tools/llvm/bin"),
            env["PATH"],
        ]
        env["PATH"] = os.pathsep.join(paths)
    elif plat_system == "windows":
        paths = [
            os.path.join(os.getenv("LOCALAPPDATA", ""), "bin", "NASM"),
            env["PATH"],
        ]
        env["PATH"] = os.pathsep.join(paths)

    return env


def deep_clean(**kwargs):
    prCyan("Deep cleaning ImageCreator...")
    shutil.rmtree("ImageCreator/build", ignore_errors=True)
    prGreen("Done.")

    prCyan("Deep cleaning UefiBootloader...")
    shutil.rmtree("UefiBootloader/build", ignore_errors=True)
    prGreen("Done.")

    prCyan("Deep cleaning HAL...")
    shutil.rmtree("HAL/build", ignore_errors=True)
    prGreen("Done.")

    prCyan("Deep cleaning artifacts...")
    shutil.rmtree("artifacts", ignore_errors=True)
    prGreen("Done.")

    prYellow("Configure must be run now!")


def run_cmd_with_echo_and_wait(cmd: list[str]):
    prYellow(f"Will run: {cmd}. Press any key to continue.")
    input()
    p = subprocess.run(cmd)
    return p.returncode == 0


def bootstrap_generic(
    pkg_manager_cmd: list[str], packages: list[Package], ignore=False
):
    prYellow("The following packages will be installed:")
    for package in packages:
        prLightGray(package.name)

    for package in packages:
        prCyan(f"Installing {package.name}...")
        if (
            not run_cmd_with_echo_and_wait(pkg_manager_cmd + [package.name])
            and not ignore
        ):
            prRed(f"Error installing {package.name}!")
            return False
        prGreen("Done.")

    return True


def bootstrap_darwin():
    prCyan("Bootrapping for macOS")

    prCyan("Checking for Homebrew...")
    p = subprocess.run(
        ["which", "brew"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL
    )
    if p.returncode != 0:
        prRed("Homebrew not found. Install Homebrew to continue.")
        return False
    prGreen("Done.")

    return bootstrap_generic(["brew", "install"], HOMEBREW_PACKAGES)


def bootstrap_linux():
    assert str(platform.system()).lower() == "linux"
    import distro

    distro_id = distro.id().lower()
    if distro_id == "ubuntu":
        pkg_manager_cmd = ["sudo", "apt-get", "install", "-y"]
        packages = APT_PACKAGES
    elif distro_id == "fedora":
        pkg_manager_cmd = ["sudo", "dnf", "install", "-y"]
        packages = DNF_PACKAGES
    elif distro_id == "debian":
        prRed(
            "HAL was not tested on debian!. Because debian usually has older versions of packages, you might need to install the packages manually."
        )
        return False
    else:
        prRed(
            f"HAL was not tested on {distro_id}!. You need to install the packages manually."
        )
        return False

    return bootstrap_generic(pkg_manager_cmd, packages)


def bootstrap():
    plat_system = str(platform.system()).lower()
    if plat_system == "darwin":
        result = bootstrap_darwin()
    elif plat_system == "linux":
        result = bootstrap_linux()
    elif plat_system == "windows":
        result = bootstrap_generic(["winget", "install"], WINGET_PACKAGES, True)
    else:
        raise Exception(f"Unknown platform {plat_system}")

    if result:
        prGreen("Successful bootstrap!")
    else:
        prRed("Failed bootstrap!")


def configure():
    generator = "Ninja"

    prCyan("Configuring ImageCreator...")
    p = subprocess.run(
        [
            "cmake",
            "-S",
            ".",
            "-B",
            "build",
            "-G",
            generator,
            "-DCMAKE_INSTALL_PREFIX:PATH=../tools/ImageCreator",
            "-DCMAKE_TOOLCHAIN_FILE:PATH=../cmake/ImageCreatorToolchain.cmake",
        ],
        cwd="ImageCreator",
        env=get_build_env(),
    )
    if p.returncode != 0:
        prRed("Error configuring ImageCreator!")
        return
    prGreen("Done.")

    prCyan("Configuring UefiBootloader...")
    p = subprocess.run(
        [
            "cmake",
            "-S",
            ".",
            "-B",
            "build",
            "-G",
            generator,
            "-DCMAKE_BUILD_TYPE=Debug",
            "-DCMAKE_TOOLCHAIN_FILE:PATH=../cmake/UefiBootloaderToolchain.cmake",
            "-DCMAKE_INSTALL_PREFIX:PATH=../artifacts",
            '-DUEFI_BUILD:BOOL="TRUE"',
            '-DFORCE_ELF:BOOL="TRUE"',
        ],
        cwd="UefiBootloader",
        env=get_build_env(),
    )
    if p.returncode != 0:
        prRed("Error configuring UefiBootloader!")
        return
    prGreen("Done.")

    prCyan("Configuring HAL9000...")
    p = subprocess.run(
        [
            "cmake",
            "-S",
            ".",
            "-B",
            "build",
            "-G",
            generator,
            "-DCMAKE_BUILD_TYPE=Debug",
            "-DCMAKE_TOOLCHAIN_FILE:PATH=../cmake/HalToolchain.cmake",
            "-DCMAKE_INSTALL_PREFIX:PATH=../artifacts",
            '-DFORCE_ELF:BOOL="TRUE"',
        ],
        cwd="HAL",
        env=get_build_env(),
    )
    if p.returncode != 0:
        prRed("Error configuring HAL9000!")
        return
    prGreen("Done.")


def clean_hal(job_count):
    prCyan("Cleaning HAL9000...")
    p = subprocess.run(
        [
            "cmake",
            "--build",
            "build",
            f"-j{job_count}",
            "--target",
            "clean",
        ],
        cwd="HAL",
        env=get_build_env(),
    )
    if p.returncode != 0:
        prRed("Error cleaning HAL9000!")
        return False
    prGreen("Done.")
    return True


def clean_all(job_count: int):
    prCyan("Cleaning ImageCreator...")
    p = subprocess.run(
        [
            "cmake",
            "--build",
            "build",
            f"-j{job_count}",
            "--target",
            "clean",
        ],
        cwd="ImageCreator",
        env=get_build_env(),
    )
    if p.returncode != 0:
        prRed("Error cleaning ImageCreator!")
        return
    prGreen("Done.")

    prCyan("Cleaning UefiBootloader...")
    p = subprocess.run(
        [
            "cmake",
            "--build",
            "build",
            f"-j{job_count}",
            "--target",
            "clean",
        ],
        cwd="UefiBootloader",
        env=get_build_env(),
    )
    if p.returncode != 0:
        prRed("Error cleaning UefiBootloader!")
        return
    prGreen("Done.")

    clean_hal(job_count)


def clean(job_count: int):
    clean_hal(job_count)


def build_hal(job_count):
    prCyan("Building HAL9000...")
    p = subprocess.run(
        ["cmake", "--build", "build", f"-j{job_count}"],
        cwd="HAL",
        env=get_build_env(),
    )
    if p.returncode != 0:
        prRed("Error building HAL9000!")
        return False
    prGreen("Done.")
    return True


def clear_tests_module():
    f = open("artifacts/Tests", "w")
    f.truncate(0)
    f.write("/vol\n")
    f.close()


def install_hal():
    prCyan("Installing HAL9000...")
    p = subprocess.run(
        ["cmake", "--install", "build"],
        cwd="HAL",
        env=get_build_env(),
        stdout=subprocess.DEVNULL,
    )
    if p.returncode != 0:
        prRed("Error installing HAL9000!")
        return False
    prGreen("Done.")
    return True


def separate_debug_information():
    prCyan("Separating debug information...")
    subprocess.run(
        [
            get_exe_name("llvm-objcopy"),
            "--only-keep-debug",
            "artifacts/bin/HAL9000.bin",
            "artifacts/bin/HAL9000.dbg",
        ],
        env=get_build_env(),
    )

    subprocess.run(
        [
            get_exe_name("llvm-strip"),
            "--strip-debug",
            "--strip-unneeded",
            "artifacts/bin/HAL9000.bin",
        ],
        env=get_build_env(),
    )

    subprocess.run(
        [
            get_exe_name("llvm-objcopy"),
            "--add-gnu-debuglink=artifacts/bin/HAL9000.dbg",
            "artifacts/bin/HAL9000.bin",
        ],
        env=get_build_env(),
    )
    prGreen("Done.")


def generate_qemu_image():
    prCyan("Generating QEMU image...")
    cmd = [
        get_exe_name("tools/ImageCreator/bin/ImageCreator"),
        "config/HAL9000.json",
    ]
    p = subprocess.run(
        cmd,
        env=get_build_env(),
    )
    if p.returncode != 0:
        prRed("Error generating QEMU image!")
        return False
    prGreen("Done.")
    return True


def build_all(job_count: int):
    if str(platform.system()).lower() == "windows":
        build_type = ["--config", "Release"]
    else:
        build_type = []

    prCyan("Building ImageCreator...")
    p = subprocess.run(
        ["cmake", "--build", "build", f"-j{job_count}"] + build_type,
        cwd="ImageCreator",
        env=get_build_env(),
    )
    if p.returncode != 0:
        prRed("Error building ImageCreator!")
        return
    prGreen("Done.")

    prCyan("Building UefiBootloader...")
    p = subprocess.run(
        ["cmake", "--build", "build", f"-j{job_count}"],
        cwd="UefiBootloader",
        env=get_build_env(),
    )
    if p.returncode != 0:
        prRed("Error building UefiBootloader!")
        return
    prGreen("Done.")

    if not build_hal(job_count):
        return

    prCyan("Installing ImageCreator...")
    p = subprocess.run(
        ["cmake", "--install", "build"] + build_type,
        cwd="ImageCreator",
        env=get_build_env(),
        stdout=subprocess.DEVNULL,
    )
    if p.returncode != 0:
        prRed("Error installing ImageCreator!")
        return
    prGreen("Done.")

    prCyan("Installing UefiBootloader...")
    p = subprocess.run(
        ["cmake", "--install", "build"],
        cwd="UefiBootloader",
        env=get_build_env(),
        stdout=subprocess.DEVNULL,
    )
    if p.returncode != 0:
        prRed("Error installing UefiBootloader!")
        return
    prGreen("Done.")

    if not install_hal():
        return

    clear_tests_module()

    separate_debug_information()


def build(j, **kwargs):
    if not build_hal(j):
        return

    if not install_hal():
        return

    clear_tests_module()

    separate_debug_information()


def parse_qemu_options(debug: bool):
    f = open("config/QEMU.json", "r")
    qemu_config = json.load(f)
    f.close()

    qemu_options: list[str] = []
    for option, param in qemu_config.items():
        if isinstance(param, list):
            for p in param:
                qemu_options.extend([f"-{option}", str(p)])
        else:
            qemu_options.extend([f"-{option}", str(param)])

    qemu_options.append("-s")
    if debug:
        qemu_options.append("-S")

    return qemu_options


def run(wait_debugger: bool):
    if not generate_qemu_image():
        return

    prCyan("Starting QEMU...")
    qemu_options = parse_qemu_options(wait_debugger)
    subprocess.run(
        [get_exe_name("qemu-system-x86_64")] + qemu_options,
    )


def run_async(wait_debugger: bool) -> subprocess.Popen:
    prCyan("Starting QEMU...")
    qemu_options = parse_qemu_options(wait_debugger)
    return subprocess.Popen(
        [get_exe_name("qemu-system-x86_64")] + qemu_options,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
    )


def run_tests(
    tests: list[str], timeout: int, job_count: int, wait_debugger: bool, **kwargs
):
    prCyan(f"Running tests matching: {tests}")

    if not build_hal(job_count):
        return

    if not install_hal():
        return

    separate_debug_information()

    if not generate_qemu_image():
        return

    tester = Tester(
        "config/Tests.json", tests, "tests", "artifacts/Tests", "HAL9000.log", timeout
    )

    prCyan("Generating tests module...")
    err = tester.generate_tests_module()
    if err:
        prRed(f"Error: {err}")
        return
    prGreen("Done.")

    timeout = tester.timeout

    p = run_async(wait_debugger)

    if timeout == 0:
        prYellow("There is no timeout. Waiting for QEMU to finish...")
        p.wait()
    else:
        prYellow(f"Timeout is {timeout}s. Sleeping...")
        time.sleep(timeout)

    if p.poll() is None:
        prRed("Error: QEMU did not finish in time.")
        p.terminate()
        clear_tests_module()
        return

    prCyan("Evaluating results...")

    print(tester.evaluate_results())

    clear_tests_module()

    prGreen("Done.")


def main():
    def job_count_arg(parser: argparse.ArgumentParser):
        parser.add_argument(
            "-j",
            "--job-count",
            help="Job count, use it for parallel build (default: number of CPUs)",
            type=int,
            required=False,
            default=multiprocessing.cpu_count(),
        )

    parser = argparse.ArgumentParser(
        prog="HAL9000.py",
        description="Script for working with HAL9000",
        epilog="'The 9000 series is the most reliable computer ever made. \
                                             No 9000 computer has ever made a mistake or distorted \
                                             information. We are all, by any practical definition of the words, \
                                             foolproof and incapable of error.' - 2001: A Space Odyssey",
        add_help=True,
    )

    subparsers = parser.add_subparsers(required=True)

    deep_clean_parser = subparsers.add_parser(
        "deep_clean", help="Remove all build directories and start with a clean slate"
    )
    deep_clean_parser.set_defaults(dispatch=deep_clean)

    bootstrap_parser = subparsers.add_parser(
        "bootstrap", help="Bootstrap HAL9000, it will install the required packages"
    )
    bootstrap_parser.set_defaults(dispatch=bootstrap)

    configure_parser = subparsers.add_parser("configure", help="Configure the projects")
    configure_parser.set_defaults(dispatch=configure)

    clean_all_parser = subparsers.add_parser(
        "clean_all", help="Run the clean target for all projects"
    )
    clean_all_parser.set_defaults(dispatch=clean_all)
    job_count_arg(clean_all_parser)

    clean_parser = subparsers.add_parser(
        "clean", help="Run the clean target for HAL9000"
    )
    clean_parser.set_defaults(dispatch=clean)
    job_count_arg(clean_parser)

    build_all_parser = subparsers.add_parser("build_all", help="Build all projects")
    build_all_parser.set_defaults(dispatch=build_all)
    job_count_arg(build_all_parser)

    build_parser = subparsers.add_parser("build", help="Build HAL9000")
    build_parser.set_defaults(dispatch=build)
    job_count_arg(build_parser)

    run_parser = subparsers.add_parser("run", help="Run HAL9000")
    run_parser.set_defaults(dispatch=run)
    run_parser.add_argument(
        "-d",
        "--wait-debugger",
        help="Make QEMU wait for the debugger",
        action="store_true",
        required=False,
    )

    run_tests_parser = subparsers.add_parser(
        "run_tests",
        help="Run the matching tests, regular expressions are also accepted",
    )
    run_tests_parser.set_defaults(dispatch=run_tests)
    run_tests_parser.add_argument("-t", "--tests", help="Tests to run", nargs="+")
    run_tests_parser.add_argument(
        "--timeout", help="Timeout in seconds", type=int, required=False, default=0
    )
    job_count_arg(run_tests_parser)
    run_tests_parser.add_argument(
        "-d",
        "--wait-debugger",
        help="Make QEMU wait for the debugger",
        action="store_true",
        required=False,
    )

    args = vars(parser.parse_args())
    dispatch = args.pop("dispatch")
    dispatch(**args)


if __name__ == "__main__":
    main()
