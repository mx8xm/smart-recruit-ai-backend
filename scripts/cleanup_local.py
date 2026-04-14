from __future__ import annotations

import argparse
import fnmatch
import os
import shutil
from pathlib import Path


PROTECTED_NAMES = {
    "app",
    "alembic",
    "tests",
    "README.md",
    "requirements.txt",
    "requirements-old.txt",
    "Procfile",
    "run.py",
    "download_models.py",
    "find_origin_app.py",
}

ROOT_TARGETS = [
    "venv",
    ".venv",
    ".cache",
    "logs",
    "build",
    "dist",
    "artifacts",
    "output",
]

FILE_PATTERNS = [
    "*.tmp",
    "*.temp",
    "*.bak",
    "*.old",
    "*.orig",
    "*.dump",
    "*.pid",
    "server_*.log",
    "temp_invalid.txt",
]


def _is_protected(path: Path, project_root: Path) -> bool:
    try:
        relative = path.resolve().relative_to(project_root.resolve())
    except ValueError:
        return True
    return relative.parts and relative.parts[0] in PROTECTED_NAMES


def collect_targets(project_root: Path) -> list[Path]:
    targets: list[Path] = []
    skip_roots: list[Path] = []

    for name in ROOT_TARGETS:
        candidate = project_root / name
        if candidate.exists() and not _is_protected(candidate, project_root):
            targets.append(candidate)
            skip_roots.append(candidate.resolve())

    for current_root, dir_names, file_names in os.walk(project_root):
        current_path = Path(current_root)
        resolved_current = current_path.resolve()

        if any(
            resolved_current == skip_root or skip_root in resolved_current.parents
            for skip_root in skip_roots
        ):
            dir_names[:] = []
            continue

        dir_names[:] = [
            name
            for name in dir_names
            if name not in PROTECTED_NAMES and name not in {".git"}
        ]

        for dir_name in list(dir_names):
            if dir_name == "__pycache__":
                folder = current_path / dir_name
                if not _is_protected(folder, project_root):
                    targets.append(folder)

        for file_name in file_names:
            if any(fnmatch.fnmatch(file_name, pattern) for pattern in FILE_PATTERNS):
                file_path = current_path / file_name
                if not _is_protected(file_path, project_root):
                    targets.append(file_path)

    unique_targets = []
    seen = set()
    for target in targets:
        key = str(target.resolve())
        if key in seen:
            continue
        seen.add(key)
        unique_targets.append(target)
    return unique_targets


def remove_path(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Safely clean local runtime junk.")
    parser.add_argument("--apply", action="store_true", help="Actually delete the matched paths.")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    targets = collect_targets(project_root)

    if not targets:
        print("No cleanup targets found.")
        return 0

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"[{mode}] Cleanup candidates:")
    for target in targets:
        print(f" - {target}")

    if not args.apply:
        print("Dry-run only. Re-run with --apply to remove these paths.")
        return 0

    for target in targets:
        remove_path(target)
        print(f"Removed: {target}")

    print("Cleanup completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
