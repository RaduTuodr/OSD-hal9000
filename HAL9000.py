from dataclasses import dataclass
from pathlib import Path
import re
import sys
import os
import argparse
import shutil
import platform
import subprocess
import multiprocessing
import json
from tests.testing import Tester

if (sys.version_info.major, sys.version_info.minor) < (3, 10):
    print(
        "This script requires at least Python 3.10, your current version is: {}.{}.{}".format(
            sys.version_info.major, sys.version_info.minor, sys.version_info.micro
        )
    )
    sys.exit(-1)

ARTIFACTS_DIR = Path("artifacts")
TEST_MODULE_PATH = ARTIFACTS_DIR / "Tests"
HAL_DIRECTORY = Path("HAL")


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


@dataclass
class Executable:
    name: str


REQUIRED_EXECUTABLES = [
    Executable("git"),
    Executable("cmake"),
    Executable("ninja"),
    Executable("qemu-system-x86_64"),
    Executable("clang"),
    Executable("clang++"),
    Executable("llvm-strip"),
    Executable("llvm-objcopy"),
    Executable("nasm"),
    Executable("lld"),
    Executable("lldb"),
]


def check_env_cmd():
    build_env = get_build_env()
    missing = False
    for exe in REQUIRED_EXECUTABLES:
        exe_path = get_exe_name(exe.name)
        print(f"{exe_path}:", end="")
        if path := shutil.which(exe_path, path=build_env["PATH"]):
            prGreen(f"OK, found at: {path}")
        else:
            missing = True
            prRed("Missing!")

    sys.exit(-1 if missing else 0)


def check_env(fail_with_message: bool = True):
    build_env = get_build_env()
    missing = []
    for exe in REQUIRED_EXECUTABLES:
        exe_path = get_exe_name(exe.name)
        if not shutil.which(exe_path, path=build_env["PATH"]):
            missing.append(exe_path)

    if not missing:
        return True

    if fail_with_message:
        prRed("The following required executables are missing from the system:")
        for exe_name in missing:
            print("  ", exe_name)
        print("Note: Run the setup command to install required dependencies.")
        print(
            "Note: If you already ran the setup command, make sure the installed dependencies are in PATH."
        )

    return False


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

VSCODE_EXTENSIONS: list[str] = [
    "ms-python.python",
    "ms-vscode.cpptools",
    "ms-vscode.cmake-tools",
    "vadimcn.vscode-lldb",
]


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


def prompt_yes_no():
    i = input("[Y]es/[N]o: ")
    return i.lower() in ["y", "yes"]


def run_cmd_with_echo_and_wait(
    cmd: list[str], shell: bool = False, assume_yes: bool = False
):
    if assume_yes:
        prYellow(f"Running command: {cmd}")
    else:
        prYellow(f"Will run: {cmd}. Press any key to continue.")
        input()
    p = subprocess.run(cmd, shell=shell)
    return p.returncode == 0


def install_packages(
    pkg_manager_cmd: list[str],
    packages: list[Package],
    ignore: bool = False,
    assume_yes: bool = False,
):
    prYellow("The following packages will be installed:")
    for package in packages:
        prLightGray(package.name)

    for package in packages:
        prCyan(f"Installing {package.name}...")
        if (
            not run_cmd_with_echo_and_wait(
                pkg_manager_cmd + [package.name], assume_yes=assume_yes
            )
            and not ignore
        ):
            prRed(f"Error installing {package.name}!")
            return False
        prGreen("Done.")

    return True


def setup_darwin(assume_yes: bool):
    prCyan("Running setup for macOS")

    prCyan("Checking for Homebrew")
    p = shutil.which("brew")
    if p is None:
        prRed("Homebrew not found. Install Homebrew to continue.")
        return False
    prGreen("Done.")

    return install_packages(
        ["brew", "install"], HOMEBREW_PACKAGES, assume_yes=assume_yes
    )


def setup_linux(assume_yes: bool):
    assert str(platform.system()).lower() == "linux"
    import distro

    prCyan("Running setup for linux")

    prCyan("Checking distro")
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
    prGreen(f"Done. Detected distro: {distro_id}")

    return install_packages(pkg_manager_cmd, packages, assume_yes=assume_yes)


def setup_windows(assume_yes: bool):
    prCyan("Running setup for Windows")

    prCyan("Checking for winget")
    p = shutil.which("winget")
    if p is None:
        prRed("winget is required to install dependencies on Windows.")
        return False
    prGreen("Done.")

    return install_packages(
        ["winget", "install"], WINGET_PACKAGES, ignore=True, assume_yes=assume_yes
    )


def setup_vscode(system: str, assume_yes: bool):
    code_path = shutil.which("code")
    if code_path is None:
        prRed("VSCode not found.")
        return False

    code_exe = "code.cmd" if system == "windows" else "code"
    for ext_name in VSCODE_EXTENSIONS:
        ok = run_cmd_with_echo_and_wait(
            [code_exe, "--install-extension", ext_name],
            shell=True,
            assume_yes=assume_yes,
        )
        if not ok:
            prRed(f"Failed to install extension {ext_name}")
            return False

    prGreen("Successfully installed VSCode extensions.")


def setup_packages(system: str, assume_yes: bool, force: bool):
    env_ok = check_env(fail_with_message=False)

    if env_ok and not force:
        prYellow(
            "The environment already contains all required tools. Do you want to run the install commands anyway?"
        )
        if not prompt_yes_no():
            print("Exiting.")
            return

    if system == "darwin":
        result = setup_darwin(assume_yes)
    elif system == "linux":
        result = setup_linux(assume_yes)
    elif system == "windows":
        result = setup_windows(assume_yes)
    else:
        raise Exception(f"Unknown platform {system}")

    if not result:
        prRed("Setup failed!")
        return False

    prGreen("Successful setup.")
    print("Hint: You might need to manually add some tools to PATH.")
    print(
        "Hint: After adding the tools to PATH, you need to close the current terminal and open a new one for the tools to be usable."
    )
    return True


def setup(assume_yes: bool, force: bool, vscode: bool):
    plat_system = str(platform.system()).lower()

    if vscode:
        setup_vscode(plat_system, assume_yes)
        return

    setup_packages(plat_system, assume_yes, force)


def cmake_configure(
    project_name: str,
    generator: str,
    project_cwd: Path | None = None,
    definitions: dict[str, str] | None = None,
):
    prCyan(f"Configuring {project_name}...")
    args = ["cmake", "-S", ".", "-B", "build", "-G", generator]
    for name, value in (definitions or {}).items():
        args.append(f"-D{name}={value}")
    p = subprocess.run(
        args,
        cwd=project_cwd if project_cwd else project_name,
        env=get_build_env(),
    )
    if p.returncode != 0:
        prRed(f"Error configuring {project_name}!")
        return False
    prGreen("Done.")
    return True


def configure():
    generator = "Ninja"

    ok = cmake_configure(
        "ImageCreator",
        generator,
        definitions={
            "CMAKE_INSTALL_PREFIX:PATH": "../tools/ImageCreator",
            "CMAKE_TOOLCHAIN_FILE:PATH": "../cmake/ImageCreatorToolchain.cmake",
        },
    )
    if not ok:
        return

    ok = cmake_configure(
        "UefiBootloader",
        generator,
        definitions={
            "CMAKE_BUILD_TYPE": "Debug",
            "CMAKE_TOOLCHAIN_FILE:PATH": "../cmake/UefiBootloaderToolchain.cmake",
            "CMAKE_INSTALL_PREFIX:PATH": "../artifacts",
            "UEFI_BUILD:BOOL": '"TRUE"',
            "FORCE_ELF:BOOL": '"TRUE"',
        },
    )
    if not ok:
        return

    cmake_configure(
        "HAL9000",
        generator,
        project_cwd=HAL_DIRECTORY,
        definitions={
            "CMAKE_BUILD_TYPE": "Debug",
            "CMAKE_TOOLCHAIN_FILE:PATH": "../cmake/HalToolchain.cmake",
            "CMAKE_INSTALL_PREFIX:PATH": "../artifacts",
            "FORCE_ELF:BOOL": '"TRUE"',
        },
    )


def cmake_clean(
    project_name: str,
    project_cwd: Path | None = None,
    job_count: int | None = None,
):
    prCyan(f"Cleaning {project_name}...")
    args = [
        "cmake",
        "--build",
        "build",
        "--target",
        "clean",
    ]

    if j := job_count:
        args.append(f"-j{j}")

    p = subprocess.run(
        args,
        cwd=project_cwd if project_cwd else project_name,
        env=get_build_env(),
    )
    if p.returncode != 0:
        prRed(f"Error cleaning {project_name}!")
        return False
    prGreen("Done.")
    return True


def clean(job_count: int, clean_all: bool):
    if clean_all:
        ok = cmake_clean("ImageCreator", job_count=job_count)
        if not ok:
            return

        ok = cmake_clean("UefiBootloader", job_count=job_count)
        if not ok:
            return

    return cmake_clean("HAL9000", project_cwd=HAL_DIRECTORY, job_count=job_count)


def cmake_install(
    project_name: str,
    project_cwd: Path | None = None,
    build_type: str | None = None,
):
    prCyan(f"Installing {project_name}...")
    args = ["cmake", "--install", "build"]
    if t := build_type:
        args.append("--config")
        args.append(t)
    p = subprocess.run(
        args,
        cwd=project_cwd if project_cwd else project_name,
        env=get_build_env(),
        stdout=subprocess.DEVNULL,
    )
    if p.returncode != 0:
        prRed(f"Error installing {project_name}!")
        return False
    prGreen("Done.")
    return True


def cmake_build(
    project_name: str,
    project_cwd: Path | None = None,
    job_count: int | None = None,
    build_type: str | None = None,
):
    prCyan(f"Building {project_name}...")
    args = ["cmake", "--build", "build"]
    if j := job_count:
        args.append(f"-j{j}")
    if t := build_type:
        args.append("--config")
        args.append(t)
    p = subprocess.run(
        args,
        cwd=project_cwd if project_cwd else project_name,
        env=get_build_env(),
    )
    if p.returncode != 0:
        prRed(f"Error building {project_name}!")
        return False
    prGreen("Done.")
    return True


def build_hal(job_count: int):
    return cmake_build("HAL9000", project_cwd=HAL_DIRECTORY, job_count=job_count)


def clear_tests_module():
    TEST_MODULE_PATH.write_text("/vol\n")


def install_hal():
    return cmake_install("HAL9000", HAL_DIRECTORY)


def separate_debug_information():
    prCyan("Separating debug information...")
    p = subprocess.run(
        [
            get_exe_name("llvm-objcopy"),
            "--only-keep-debug",
            "artifacts/bin/HAL9000.bin",
            "artifacts/bin/HAL9000.dbg",
        ],
        env=get_build_env(),
    )
    if p.returncode != 0:
        prRed("Failed to generate debug information")
        return False

    p = subprocess.run(
        [
            get_exe_name("llvm-strip"),
            "--strip-debug",
            "--strip-unneeded",
            "artifacts/bin/HAL9000.bin",
        ],
        env=get_build_env(),
    )
    if p.returncode != 0:
        prRed("Failed to strip debug information")
        return False

    p = subprocess.run(
        [
            get_exe_name("llvm-objcopy"),
            "--add-gnu-debuglink=artifacts/bin/HAL9000.dbg",
            "artifacts/bin/HAL9000.bin",
        ],
        env=get_build_env(),
    )
    if p.returncode != 0:
        prRed("Failed to link debug information")
        return False

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


def build(job_count: int, build_all: bool):
    if str(platform.system()).lower() == "windows":
        build_type = "Release"
    else:
        build_type = None

    if build_all:
        ok = cmake_build("ImageCreator", job_count=job_count, build_type=build_type)
        if not ok:
            return

        ok = cmake_build("UefiBootloader", job_count=job_count)
        if not ok:
            return

    if not build_hal(job_count):
        return

    if build_all:
        ok = cmake_install("ImageCreator", build_type=build_type)
        if not ok:
            return

        ok = cmake_install("UefiBootloader")
        if not ok:
            return

    if not install_hal():
        return

    clear_tests_module()

    separate_debug_information()


def rebuild(job_count: int, build_all: bool):
    if not clean(job_count, build_all):
        return
    build(job_count, build_all)


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


def run(wait_debugger: bool, job_count: int):
    if not TEST_MODULE_PATH.is_file():
        clear_tests_module()

    if not build_hal(job_count):
        return

    if not install_hal():
        return

    separate_debug_information()

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
    tests: list[str], job_count: int, wait_debugger: bool, timeout: int | None = None
):
    prCyan(f"Running tests matching: {tests}")

    if not build_hal(job_count):
        return

    if not install_hal():
        return

    separate_debug_information()

    tester = Tester(
        "config/Tests.json", tests, "tests", "artifacts/Tests", "HAL9000.log", timeout
    )

    prCyan("Generating tests module...")
    err = tester.generate_tests_module()
    if err:
        prRed(f"Error: {err}")
        return
    prGreen("Done.")

    if not generate_qemu_image():
        return

    p = run_async(wait_debugger)

    timeout = tester.timeout
    time_limit_exceeded = False
    if timeout == 0:
        prYellow("Timeout set to 0. Waiting for QEMU to finish...")
        p.wait()
    elif wait_debugger:
        prYellow(
            "Debugger attached, won't enforce timeout. Waiting for QEMU to finish..."
        )
        p.wait()
    else:
        prYellow(f"Timeout is {timeout}s.")
        try:
            p.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            time_limit_exceeded = True

    if time_limit_exceeded:
        prRed("Error: QEMU did not finish in time.")
        print(
            "Note: Attach debugger on start with --wait-debugger or use --timeout 0 to wait indefinitely."
        )
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

    check_env_parser = subparsers.add_parser(
        "check_env",
        help="Check if required dependencies (tools) are installed properly.",
    )
    check_env_parser.set_defaults(dispatch=check_env_cmd)

    setup_parser = subparsers.add_parser(
        "setup",
        help="Install the dependencies (tools) required to build and run HAL9000",
    )
    setup_parser.set_defaults(dispatch=setup)
    setup_parser.add_argument(
        "-y",
        "--yes",
        dest="assume_yes",
        help="Don't prompt before running commands",
        action="store_true",
        required=False,
    )
    setup_parser.add_argument(
        "--force",
        help="Run all install commands even if the dependencies are already installed.",
        action="store_true",
        required=False,
    )
    setup_parser.add_argument(
        "--vscode",
        help="Check for VSCode and install the required extensions. Will not install other dependencies.",
        action="store_true",
        required=False,
    )

    deep_clean_parser = subparsers.add_parser(
        "deep_clean", help="Remove all build directories and start with a clean slate"
    )
    deep_clean_parser.set_defaults(dispatch=deep_clean)

    configure_parser = subparsers.add_parser("configure", help="Configure the projects")
    configure_parser.set_defaults(dispatch=configure, pre_check=check_env)

    clean_parser = subparsers.add_parser(
        "clean", help="Run the clean target for HAL9000"
    )
    clean_parser.set_defaults(dispatch=clean, pre_check=check_env)
    clean_parser.add_argument(
        "-a",
        "--all",
        dest="clean_all",
        help="Clean all projects",
        action="store_true",
        required=False,
    )
    job_count_arg(clean_parser)

    build_parser = subparsers.add_parser("build", aliases="b", help="Build HAL9000")
    build_parser.set_defaults(dispatch=build, pre_check=check_env)
    build_parser.add_argument(
        "-a",
        "--all",
        dest="build_all",
        help="Build all projects",
        action="store_true",
        required=False,
    )
    job_count_arg(build_parser)

    rebuild_parser = subparsers.add_parser("rebuild", help="Clean, then build HAL9000")
    rebuild_parser.set_defaults(dispatch=rebuild, pre_check=check_env)
    rebuild_parser.add_argument(
        "-a",
        "--all",
        dest="build_all",
        help="Rebuild all projects",
        action="store_true",
        required=False,
    )
    job_count_arg(rebuild_parser)

    run_parser = subparsers.add_parser("run", aliases="r", help="Run HAL9000")
    run_parser.set_defaults(dispatch=run, pre_check=check_env)
    run_parser.add_argument(
        "-d",
        "--wait-debugger",
        help="Make QEMU wait for the debugger",
        action="store_true",
        required=False,
    )
    job_count_arg(run_parser)

    run_tests_parser = subparsers.add_parser(
        "test",
        aliases="t",
        help="Run the tests for the HAL9000 project",
    )
    run_tests_parser.set_defaults(dispatch=run_tests, pre_check=check_env)
    run_tests_parser.add_argument(
        "-t",
        "--tests",
        help="Tests to run. Tests are given in the format Project[:Component[:TestName]]. For example: "
        "'Threads' - run all tests for the Threads project; "
        "'UserProg:Arguments' - run all argument passing tests from the UserProg project; "
        "'VirtualMemory:Swap:SwapZeros' - run the SwapZeroes test from the VirtualMemory project; ",
        nargs="+",
    )
    run_tests_parser.add_argument(
        "--timeout", help="Timeout in seconds", type=int, required=False
    )
    job_count_arg(run_tests_parser)
    run_tests_parser.add_argument(
        "-d",
        "--wait-debugger",
        help="Make QEMU wait for the debugger. Prevents timeout to allow debugging.",
        action="store_true",
        required=False,
    )

    args = vars(parser.parse_args())

    if pre_check := args.pop("pre_check", None):
        if not pre_check():
            return

    dispatch = args.pop("dispatch")
    dispatch(**args)


if __name__ == "__main__":
    main()
