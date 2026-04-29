from __future__ import annotations

import argparse
import os
import platform
import shutil
import stat
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"
VENV_DIR = ROOT / ".venv"
FRONTEND_NODE_MODULES = FRONTEND_DIR / "node_modules"
PYTHON_PLATFORM_MARKER = VENV_DIR / ".prepared-platform"
FRONTEND_PLATFORM_MARKER = FRONTEND_NODE_MODULES / ".prepared-platform"


def log(message: str = "") -> None:
    print(message, flush=True)


def host_platform() -> str:
    if os.name == "nt":
        return "windows"
    if sys.platform.startswith("linux"):
        return "linux"
    raise SystemExit(f"Unsupported host platform: {sys.platform}")


def normalized_machine() -> str:
    machine = platform.machine().lower()
    aliases = {
        "amd64": "x64",
        "x86_64": "x64",
        "aarch64": "arm64",
    }
    return aliases.get(machine, machine or "unknown")


def platform_key(target: str) -> str:
    return f"{target}-{normalized_machine()}"


def run(command: list[str | Path], *, cwd: Path = ROOT, check: bool = True) -> subprocess.CompletedProcess:
    printable = " ".join(str(part) for part in command)
    log(f"$ {printable}")
    return subprocess.run([str(part) for part in command], cwd=str(cwd), check=check)


def run_first(candidates: list[list[str | Path]], *, cwd: Path = ROOT) -> None:
    last_error: Exception | None = None
    for command in candidates:
        try:
            run(command, cwd=cwd)
            return
        except FileNotFoundError as error:
            last_error = error
        except subprocess.CalledProcessError as error:
            last_error = error
    raise SystemExit(f"Could not run any candidate command. Last error: {last_error}")


def npm_command(target: str) -> str:
    return "npm.cmd" if target == "windows" else "npm"


def venv_python(target: str) -> Path:
    if target == "windows":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def other_platform_venv_python(target: str) -> Path:
    if target == "windows":
        return VENV_DIR / "bin" / "python"
    return VENV_DIR / "Scripts" / "python.exe"


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def read_marker(path: Path) -> str:
    return read_text(path).strip()


def write_marker(path: Path, value: str) -> None:
    path.write_text(value + "\n", encoding="utf-8")


def pyvenv_cfg_text() -> str:
    return read_text(VENV_DIR / "pyvenv.cfg").lower()


def venv_needs_recreate(target: str, current_key: str) -> tuple[bool, str]:
    python = venv_python(target)
    other_python = other_platform_venv_python(target)

    if not python.exists():
        if other_python.exists():
            return True, "Python virtualenv belongs to the other platform"
        return True, f"{python.relative_to(ROOT)} is missing"

    if target != "windows" and not os.access(python, os.X_OK):
        return True, f"{python.relative_to(ROOT)} is not executable"

    cfg = pyvenv_cfg_text()
    if target == "linux" and ("executable = c:" in cfg or "\\python" in cfg or "\\scripts\\" in cfg):
        return True, "Python virtualenv was created on Windows"
    if target == "windows" and ("home = /" in cfg or "executable = /" in cfg or "/bin/python" in cfg):
        return True, "Python virtualenv was created on Linux"

    marker = read_marker(PYTHON_PLATFORM_MARKER)
    if marker and marker != current_key:
        return True, f"Python virtualenv marker is {marker}, expected {current_key}"

    result = subprocess.run(
        [str(python), "-c", "import sys; print(sys.version_info[:2])"],
        cwd=str(BACKEND_DIR),
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        return True, "Python virtualenv cannot run"

    return False, ""


def create_venv(target: str) -> None:
    log("Creating Python virtualenv...")
    if target == "linux":
        run_first(
            [
                ["python3.12", "-m", "venv", "--clear", VENV_DIR],
                ["python3", "-m", "venv", "--clear", VENV_DIR],
                ["python", "-m", "venv", "--clear", VENV_DIR],
            ]
        )
        return

    run_first(
        [
            ["py", "-3.12", "-m", "venv", "--clear", VENV_DIR],
            ["py", "-3", "-m", "venv", "--clear", VENV_DIR],
            ["python", "-m", "venv", "--clear", VENV_DIR],
        ]
    )


def ensure_venv(target: str, *, force: bool, current_key: str) -> Path:
    needs_recreate, reason = venv_needs_recreate(target, current_key)
    if force or needs_recreate:
        log("Forcing Python virtualenv recreation." if force else f"Recreating Python virtualenv: {reason}.")
        create_venv(target)
    else:
        log("Python virtualenv already matches this platform.")

    python = venv_python(target)
    if not python.exists():
        raise SystemExit(f"Python virtualenv was not created correctly: {python}")
    return python


def chmod_executable(path: Path) -> None:
    if not path.exists() or path.is_symlink():
        return
    mode = path.stat().st_mode
    path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def fix_linux_permissions() -> None:
    for path in (ROOT / "dev.sh", ROOT / "prepare.sh"):
        chmod_executable(path)

    for directory in (VENV_DIR / "bin", FRONTEND_NODE_MODULES / ".bin"):
        if not directory.exists():
            continue
        for entry in directory.iterdir():
            if entry.is_file():
                chmod_executable(entry)


def ensure_env_file(target: Path, source: Path) -> None:
    if target.exists():
        log(f"{target.relative_to(ROOT)} already exists.")
        return
    if not source.exists():
        raise SystemExit(f"Missing env example: {source.relative_to(ROOT)}")
    shutil.copyfile(source, target)
    log(f"Created {target.relative_to(ROOT)} from {source.relative_to(ROOT)}.")


def ensure_env_files() -> None:
    ensure_env_file(ROOT / ".env", ROOT / ".env.example")
    ensure_env_file(FRONTEND_DIR / ".env", FRONTEND_DIR / ".env.example")


def install_backend(python: Path, current_key: str) -> None:
    log("Installing backend dependencies...")
    run([python, "-m", "pip", "install", "-r", BACKEND_DIR / "requirements.txt"])
    write_marker(PYTHON_PLATFORM_MARKER, current_key)


def ensure_node_available(target: str) -> None:
    try:
        run([npm_command(target), "--version"])
    except FileNotFoundError:
        raise SystemExit("npm is not available. Install Node.js and npm first.")


def frontend_needs_clean_install(current_key: str, *, force: bool) -> tuple[bool, str]:
    if force:
        return True, "forced by --force-frontend"
    if not FRONTEND_NODE_MODULES.exists():
        return False, "node_modules is missing"

    marker = read_marker(FRONTEND_PLATFORM_MARKER)
    if marker and marker != current_key:
        return True, f"node_modules marker is {marker}, expected {current_key}"
    return False, ""


def install_frontend(target: str, *, force: bool, current_key: str) -> None:
    ensure_node_available(target)

    clean_install, reason = frontend_needs_clean_install(current_key, force=force)
    if clean_install:
        log(f"Removing frontend/node_modules: {reason}.")
        shutil.rmtree(FRONTEND_NODE_MODULES)

    if FRONTEND_NODE_MODULES.exists():
        log("Refreshing frontend dependencies for this platform...")
    else:
        log("Installing frontend dependencies...")
    run([npm_command(target), "install"], cwd=FRONTEND_DIR)
    write_marker(FRONTEND_PLATFORM_MARKER, current_key)


def apply_migrations(python: Path) -> None:
    log("Applying database migrations...")
    run([python, "-m", "flask", "--app", "wsgi", "db", "upgrade"], cwd=BACKEND_DIR)


def ensure_roles(python: Path) -> None:
    log("Ensuring default roles...")
    run([python, "-m", "flask", "--app", "wsgi", "ensure-roles"], cwd=BACKEND_DIR)


def build_frontend(target: str) -> None:
    log("Building frontend...")
    run([npm_command(target), "run", "build"], cwd=FRONTEND_DIR)


def run_dev_script(target: str) -> None:
    if target == "windows":
        run([ROOT / "dev.cmd"])
    else:
        run([ROOT / "dev.sh"])


def ensure_project_shape() -> None:
    missing = [path for path in (BACKEND_DIR, FRONTEND_DIR) if not path.exists()]
    if missing:
        joined = ", ".join(str(path.relative_to(ROOT)) for path in missing)
        raise SystemExit(f"Project folder is incomplete. Missing: {joined}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare this Flask/Vite project after moving it between Windows and Linux.")
    parser.add_argument(
        "target",
        nargs="?",
        default="current",
        choices=["current", "linux", "windows"],
        help="Target platform. Use 'current' to detect the current OS.",
    )
    parser.add_argument("--force-venv", action="store_true", help="Recreate .venv even if it looks usable.")
    parser.add_argument("--force-frontend", action="store_true", help="Remove frontend/node_modules before npm install.")
    parser.add_argument("--skip-env", action="store_true", help="Do not create .env files from examples.")
    parser.add_argument("--skip-backend", action="store_true", help="Do not install backend dependencies.")
    parser.add_argument("--skip-frontend", action="store_true", help="Do not install frontend dependencies.")
    parser.add_argument("--skip-migrations", action="store_true", help="Do not run Flask database migrations.")
    parser.add_argument("--skip-roles", action="store_true", help="Do not run the ensure-roles Flask command.")
    parser.add_argument("--build", action="store_true", help="Run frontend production build after preparing.")
    parser.add_argument("--run-dev", action="store_true", help="Start dev.sh or dev.cmd after preparing.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    host = host_platform()
    target = host if args.target == "current" else args.target
    current_key = platform_key(target)

    if target != host:
        raise SystemExit(
            f"Target '{target}' must be prepared on that OS. Current host is '{host}'. "
            "Move the project to the target machine and run this script there."
        )

    ensure_project_shape()

    log(f"Preparing project for {current_key}.")
    if not args.skip_env:
        ensure_env_files()

    python = ensure_venv(target, force=args.force_venv, current_key=current_key)

    if target == "linux":
        fix_linux_permissions()

    if not args.skip_backend:
        install_backend(python, current_key)

    if not args.skip_frontend:
        install_frontend(target, force=args.force_frontend, current_key=current_key)

    if not args.skip_migrations:
        apply_migrations(python)

    if not args.skip_roles:
        ensure_roles(python)

    if args.build:
        build_frontend(target)

    if target == "linux":
        fix_linux_permissions()

    log()
    log("Platform preparation complete.")
    log("Run dev: dev.cmd" if target == "windows" else "Run dev: ./dev.sh")

    if args.run_dev:
        run_dev_script(target)


if __name__ == "__main__":
    main()
