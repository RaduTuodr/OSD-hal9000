from dataclasses import dataclass
import enum
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


class Color(enum.Enum):
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"


class Styled:
    END = "\033[0m"
    BOLD = "\033[1m"

    def __init__(self, s: str) -> None:
        self._string = s
        self._bold: bool = False
        self._color: Color | None = None

    def __str__(self) -> str:
        escapes = []
        if c := self._color:
            escapes.append(c.value)
        if self._bold:
            escapes.append(Styled.BOLD)
        return "".join(escapes) + self._string + Styled.END

    def bold(self):
        self._bold = True
        return self

    def color(self, color: Color):
        self._color = color
        return self

    @staticmethod
    def red(s: str):
        this = Styled(s)
        return this.color(Color.RED)

    @staticmethod
    def green(s: str):
        this = Styled(s)
        return this.color(Color.GREEN)

    @staticmethod
    def yellow(s: str):
        this = Styled(s)
        return this.color(Color.YELLOW)

    @staticmethod
    def blue(s: str):
        this = Styled(s)
        return this.color(Color.BLUE)

    @staticmethod
    def magenta(s: str):
        this = Styled(s)
        return this.color(Color.MAGENTA)

    @staticmethod
    def cyan(s: str):
        this = Styled(s)
        return this.color(Color.CYAN)


def print_success(msg: str):
    print(Styled.green(msg))


def print_progress_info(msg: str):
    print(Styled.cyan(msg))


def print_note(msg: str):
    print(Styled.yellow("Note:"), msg)


def print_important(msg: str):
    print(Styled.yellow(msg))


def print_warning(msg: str):
    print(Styled.yellow(msg))


def print_error(msg: str):
    print(Styled.red(msg))


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
        if path := shutil.which(exe_path, path=build_env["PATH"]):
            print(f"{exe_path:<24}: {Styled.green('OK')}, found at: {path}")
        else:
            missing = True
            print(f"{exe_path:<24}: {Styled.red('Missing')}")

    if missing:
        print_note("The following paths are currently in PATH:")
        for path in build_env["PATH"].split(";"):
            print("  ", path)

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
        print_error("The following required executables are missing from the system:")
        for exe_name in missing:
            print("  ", exe_name)
        print_note("Run the setup command to install required dependencies.")
        print_note(
            "If you already ran the setup command, make sure the installed dependencies are in PATH."
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
    print_progress_info("Deep cleaning ImageCreator...")
    shutil.rmtree("ImageCreator/build", ignore_errors=True)
    print_success("Done.")

    print_progress_info("Deep cleaning UefiBootloader...")
    shutil.rmtree("UefiBootloader/build", ignore_errors=True)
    print_success("Done.")

    print_progress_info("Deep cleaning HAL...")
    shutil.rmtree("HAL/build", ignore_errors=True)
    print_success("Done.")

    print_progress_info("Deep cleaning artifacts...")
    shutil.rmtree("artifacts", ignore_errors=True)
    print_success("Done.")


def prompt_yes_no():
    i = input("[Y]es/[N]o: ")
    return i.lower() in ["y", "yes"]


def run_cmd_with_echo_and_wait(
    cmd: list[str], shell: bool = False, assume_yes: bool = False
):
    if assume_yes:
        print_important(f"Running command: {cmd}")
    else:
        print_important(f"Will run: {cmd}. Press any key to continue.")
        input()
    p = subprocess.run(cmd, shell=shell)
    return p.returncode == 0


def install_packages(
    pkg_manager_cmd: list[str],
    packages: list[Package],
    ignore: bool = False,
    assume_yes: bool = False,
):
    print_important("The following packages will be installed:")
    for package in packages:
        print(package.name)

    for package in packages:
        print_progress_info(f"Installing {package.name}...")
        if (
            not run_cmd_with_echo_and_wait(
                pkg_manager_cmd + [package.name], assume_yes=assume_yes
            )
            and not ignore
        ):
            print_error(f"Error installing {package.name}!")
            return False
        print_success("Done.")

    return True


def setup_darwin(assume_yes: bool):
    print_progress_info("Running setup for macOS")

    print_progress_info("Checking for Homebrew")
    p = shutil.which("brew")
    if p is None:
        print_error("Homebrew not found. Install Homebrew to continue.")
        return False
    print_success("Done.")

    return install_packages(
        ["brew", "install"], HOMEBREW_PACKAGES, assume_yes=assume_yes
    )


def setup_linux(assume_yes: bool):
    assert str(platform.system()).lower() == "linux"
    import distro

    print_progress_info("Running setup for linux")

    print_progress_info("Checking distro")
    distro_id = distro.id().lower()
    if distro_id == "ubuntu":
        pkg_manager_cmd = ["sudo", "apt-get", "install", "-y"]
        packages = APT_PACKAGES
    elif distro_id == "fedora":
        pkg_manager_cmd = ["sudo", "dnf", "install", "-y"]
        packages = DNF_PACKAGES
    elif distro_id == "debian":
        print_error("HAL was not tested on debian!")
        print_note(
            "Because debian usually has older versions of packages, you might need to install the packages manually."
        )
        return False
    else:
        print_error(f"HAL was not tested on {distro_id}!.")
        print_note(
            "We recommend using Ubuntu, even if you might be able to install the packages manually."
        )
        return False
    print_success(f"Done. Detected distro: {distro_id}")

    return install_packages(pkg_manager_cmd, packages, assume_yes=assume_yes)


def setup_windows(assume_yes: bool):
    print_progress_info("Running setup for Windows")

    print_progress_info("Checking for winget")
    p = shutil.which("winget")
    if p is None:
        print_error("winget is required to install dependencies on Windows.")
        return False
    print_success("Done.")

    return install_packages(
        ["winget", "install"], WINGET_PACKAGES, ignore=True, assume_yes=assume_yes
    )


def setup_vscode(system: str, assume_yes: bool):
    code_path = shutil.which("code")
    if code_path is None:
        print_error("VSCode not found.")
        return False

    print_important("The following VSCode extensions will be installed:")
    for ext_name in VSCODE_EXTENSIONS:
        print(ext_name)

    code_exe = "code.cmd" if system == "windows" else "code"
    for ext_name in VSCODE_EXTENSIONS:
        print_progress_info(f"Installing {ext_name}...")
        ok = run_cmd_with_echo_and_wait(
            [code_exe, "--install-extension", ext_name],
            shell=True,
            assume_yes=assume_yes,
        )
        if not ok:
            print_error(f"Failed to install extension {ext_name}")
            return False

    print_success("Successfully installed VSCode extensions.")


def setup_packages(system: str, assume_yes: bool, force: bool):
    env_ok = check_env(fail_with_message=False)

    if env_ok and not force:
        print_important(
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
        print_error("Setup failed!")
        return False

    print_success("Successful setup.")
    print_note("You might need to manually add some tools to PATH.")
    print_note(
        "After adding the tools to PATH, you need to close the current terminal and open a new one for the tools to be usable."
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
    print_progress_info(f"Configuring {project_name}...")
    args = ["cmake", "-S", ".", "-B", "build", "-G", generator]
    for name, value in (definitions or {}).items():
        args.append(f"-D{name}={value}")
    p = subprocess.run(
        args,
        cwd=project_cwd if project_cwd else project_name,
        env=get_build_env(),
    )
    if p.returncode != 0:
        print_error(f"Error configuring {project_name}!")
        return False
    print_success("Done.")
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
    print_progress_info(f"Cleaning {project_name}...")
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
        print_error(f"Error cleaning {project_name}!")
        return False
    print_success("Done.")
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
    print_progress_info(f"Installing {project_name}...")
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
        print_error(f"Error installing {project_name}!")
        return False
    print_success("Done.")
    return True


def cmake_build(
    project_name: str,
    project_cwd: Path | None = None,
    job_count: int | None = None,
    build_type: str | None = None,
):
    print_progress_info(f"Building {project_name}...")
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
        print_error(f"Error building {project_name}!")
        return False
    print_success("Done.")
    return True


def build_hal(job_count: int):
    return cmake_build("HAL9000", project_cwd=HAL_DIRECTORY, job_count=job_count)


def clear_tests_module():
    TEST_MODULE_PATH.write_text("/vol\n")


def install_hal():
    return cmake_install("HAL9000", HAL_DIRECTORY)


def separate_debug_information():
    print_progress_info("Separating debug information...")
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
        print_error("Failed to generate debug information")
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
        print_error("Failed to strip debug information")
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
        print_error("Failed to link debug information")
        return False

    print_success("Done.")


def build(
    job_count: int,
    build_all: bool,
    run_configure: bool,
):
    if run_configure:
        configure()
    else:
        print_warning("Skipping configure")

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

    separate_debug_information()


def rebuild(
    job_count: int,
    build_all: bool,
    run_configure: bool,
):
    if not clean(job_count, build_all):
        return
    build(job_count, build_all, run_configure)


def parse_qemu_options(debug: bool, no_graphic: bool):
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

    if no_graphic:
        qemu_options.append("-nographic")

    return qemu_options


def generate_qemu_image():
    print_progress_info("Generating QEMU image...")
    image_creator = get_exe_name("tools/ImageCreator/bin/ImageCreator")
    cmd = [
        image_creator,
        "config/HAL9000.json",
    ]

    p = subprocess.run(
        cmd,
        env=get_build_env(),
    )
    if p.returncode != 0:
        print_error("Error generating QEMU image!")
        return False
    print_success("Done.")
    return True


def prepare_hal_for_run(
    job_count: int,
    run_configure: bool,
    run_build: bool,
):
    if not run_build:
        print_warning("Skipping build")
        return

    # If ImageCreator does not exist, build all projects
    image_creator_path = Path(get_exe_name("tools/ImageCreator/bin/ImageCreator"))
    build_all = not image_creator_path.is_file()

    build(job_count, build_all, run_configure=run_configure)


def run(
    wait_debugger: bool,
    no_graphic: bool,
    job_count: int,
    run_configure: bool,
    run_build: bool,
):
    prepare_hal_for_run(job_count, run_configure, run_build)

    if not TEST_MODULE_PATH.is_file():
        clear_tests_module()

    if not generate_qemu_image():
        return

    print_progress_info("Starting QEMU...")
    qemu_options = parse_qemu_options(wait_debugger, no_graphic=no_graphic)
    p = subprocess.run(
        [get_exe_name("qemu-system-x86_64")] + qemu_options,
    )
    if p.returncode != 0:
        print_important(f"QEMU returned with exit status: {p.returncode}")
        print_note(
            "If QEMU doesn't start because of gtk, use the -G option to run without graphics."
        )


def run_async(wait_debugger: bool, no_graphic: bool) -> subprocess.Popen:
    print_progress_info("Starting QEMU...")
    qemu_options = parse_qemu_options(wait_debugger, no_graphic=no_graphic)
    return subprocess.Popen(
        [get_exe_name("qemu-system-x86_64")] + qemu_options,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
    )


def run_tests(
    tests: list[str],
    job_count: int,
    wait_debugger: bool,
    no_graphic: bool,
    run_configure: bool,
    run_build: bool,
    timeout: int | None = None,
):
    prepare_hal_for_run(job_count, run_configure, run_build)

    print_progress_info(f"Running tests matching: {tests}")
    tester = Tester(
        "config/Tests.json", tests, "tests", "artifacts/Tests", "HAL9000.log", timeout
    )

    print_progress_info("Generating tests module...")
    err = tester.generate_tests_module()
    if err:
        print_error(f"Error: {err}")
        return
    print_success("Done.")

    if not generate_qemu_image():
        return

    p = run_async(wait_debugger, no_graphic=no_graphic)

    timeout = tester.timeout
    time_limit_exceeded = False
    if timeout == 0:
        print_important("Timeout set to 0. Waiting for QEMU to finish...")
        p.wait()
    elif wait_debugger:
        print_important(
            "Debugger attached, won't enforce timeout. Waiting for QEMU to finish..."
        )
        p.wait()
    else:
        print_important(f"Timeout is {timeout}s.")
        try:
            p.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            time_limit_exceeded = True

    if time_limit_exceeded:
        print_error("Error: QEMU did not finish in time.")
        print(
            "Note: Attach debugger on start with --wait-debugger or use --timeout 0 to wait indefinitely."
        )
        p.terminate()
        clear_tests_module()
        return

    if p.returncode != 0:
        print_important(f"QEMU returned with exit status: {p.returncode}")
        print_note(
            "If QEMU doesn't start because of gtk, use the -G option to run without graphics."
        )
        clear_tests_module()
        return

    print_progress_info("Evaluating results...")

    print(tester.evaluate_results())

    clear_tests_module()

    print_success("Done.")


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

    def no_configure_arg(parser: argparse.ArgumentParser):
        parser.add_argument(
            "-C",
            "--no-configure",
            dest="run_configure",
            help="Don't run configure (not recommended unless you known what you're doing)",
            action="store_false",
            default=True,
            required=False,
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
        help="Check if required dependencies (tools) are installed properly",
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

    configure_parser = subparsers.add_parser(
        "configure",
        help="Configure the projects (will be run automatically when needed)",
    )
    configure_parser.set_defaults(dispatch=configure, pre_check=check_env)

    clean_parser = subparsers.add_parser(
        "clean", help="Delete build artifacts (default target: HAL9000)"
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

    build_parser = subparsers.add_parser(
        "build", aliases="b", help="Build (default target: HAL9000)"
    )
    build_parser.set_defaults(dispatch=build, pre_check=check_env)
    build_parser.add_argument(
        "-a",
        "--all",
        dest="build_all",
        help="Build all projects",
        action="store_true",
        required=False,
    )
    no_configure_arg(build_parser)
    job_count_arg(build_parser)

    rebuild_parser = subparsers.add_parser(
        "rebuild", help="Clean, then build (default target: HAL9000)"
    )
    rebuild_parser.set_defaults(dispatch=rebuild, pre_check=check_env)
    rebuild_parser.add_argument(
        "-a",
        "--all",
        dest="build_all",
        help="Rebuild all projects",
        action="store_true",
        required=False,
    )
    no_configure_arg(rebuild_parser)
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
    run_parser.add_argument(
        "-G",
        "--no-graphic",
        help="Don't show QEMU display output",
        action="store_true",
        required=False,
    )
    no_configure_arg(run_parser)
    run_parser.add_argument(
        "-B",
        "--no-build",
        dest="run_build",
        help="Don't run configure and build (not recommended unless you known what you're doing)",
        action="store_false",
        default=True,
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
    run_tests_parser.add_argument(
        "-d",
        "--wait-debugger",
        help="Make QEMU wait for the debugger. Prevents timeout to allow debugging.",
        action="store_true",
        required=False,
    )
    run_tests_parser.add_argument(
        "-G",
        "--no-graphic",
        help="Don't show QEMU display output",
        action="store_true",
        required=False,
    )
    no_configure_arg(run_tests_parser)
    run_tests_parser.add_argument(
        "-B",
        "--no-build",
        dest="run_build",
        help="Don't run configure and build (not recommended unless you known what you're doing)",
        action="store_false",
        default=True,
        required=False,
    )
    job_count_arg(run_tests_parser)

    args = vars(parser.parse_args())

    if pre_check := args.pop("pre_check", None):
        if not pre_check():
            return

    dispatch = args.pop("dispatch")
    dispatch(**args)


if __name__ == "__main__":
    main()
