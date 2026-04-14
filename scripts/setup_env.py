from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(command: list[str], log_file: Path) -> int:
    with log_file.open("a", encoding="utf-8") as handle:
        handle.write(f"\n$ {' '.join(command)}\n")
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        assert process.stdout is not None
        for line in process.stdout:
            print(line, end="")
            handle.write(line)
        return process.wait()


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a local virtual environment and install dependencies.")
    parser.add_argument("--python", dest="python_executable", default=sys.executable)
    parser.add_argument("--venv-name", default="venv")
    parser.add_argument("--skip-upgrade", action="store_true")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    logs_dir = project_root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / "setup_env.log"
    log_file.write_text("Smart Recruit AI environment setup log\n", encoding="utf-8")

    python_path = shutil.which(args.python_executable) or args.python_executable
    if shutil.which(python_path) is None and not Path(python_path).exists():
        print("Python was not found. Install Python 3.10+ and retry.")
        print(f"Details logged to: {log_file}")
        return 1

    venv_path = project_root / args.venv_name
    print(f"[1/3] Creating virtual environment at {venv_path}")
    exit_code = run_command([python_path, "-m", "venv", str(venv_path)], log_file)
    if exit_code != 0:
        return exit_code

    venv_python = venv_path / "Scripts" / "python.exe"
    if not venv_python.exists():
        print("Virtual environment creation finished, but python.exe was not found inside Scripts.")
        return 1

    if not args.skip_upgrade:
        print("[2/3] Upgrading pip/setuptools/wheel")
        exit_code = run_command(
            [str(venv_python), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"],
            log_file,
        )
        if exit_code != 0:
            return exit_code

    print("[3/3] Installing project requirements")
    exit_code = run_command([str(venv_python), "-m", "pip", "install", "-r", "requirements.txt"], log_file)
    if exit_code != 0:
        return exit_code

    activate_ps1 = venv_path / "Scripts" / "Activate.ps1"
    print("")
    print("Environment setup completed.")
    print(f"Activate with: {activate_ps1}")
    print(f"Full log: {log_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
