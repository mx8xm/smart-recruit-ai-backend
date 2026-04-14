from __future__ import annotations

import argparse
import asyncio
import importlib
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import PROJECT_ROOT, get_settings


async def check_database() -> tuple[bool, str]:
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine

    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        return True, "Database connection OK"
    except Exception as exc:
        return False, f"Database connection failed: {exc}"
    finally:
        await engine.dispose()


def check_dependencies(skip_model_check: bool) -> tuple[bool, list[str]]:
    required_modules = ["fastapi", "sqlalchemy", "asyncpg", "uvicorn"]
    if not skip_model_check:
        required_modules.extend(["sentence_transformers", "gliner", "docling"])

    missing = []
    for module_name in required_modules:
        try:
            importlib.import_module(module_name)
        except Exception:
            missing.append(module_name)

    return (len(missing) == 0, missing)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Smart Recruit AI locally with preflight checks.")
    parser.add_argument("--skip-model-check", action="store_true")
    parser.add_argument("--skip-db-check", action="store_true")
    args = parser.parse_args()

    settings = get_settings()
    print("[1/5] Checking configuration")
    print(f"Environment file in use: {os.getenv('ENV_FILE', '.env.local if present')}")

    print("[2/5] Checking Python dependencies")
    deps_ok, missing_modules = check_dependencies(skip_model_check=args.skip_model_check)
    if not deps_ok:
        print("Missing Python dependencies: " + ", ".join(missing_modules))
        print("Run scripts/setup_env.ps1 and activate the virtual environment first.")
        return 1

    if not args.skip_db_check:
        print("[3/5] Checking PostgreSQL connectivity")
        ok, message = asyncio.run(check_database())
        print(message)
        if not ok:
            print("Run scripts/check_postgres.ps1 for more guidance.")
            print("If PostgreSQL is missing, use scripts/download_postgres_installer.ps1")
            return 1
    else:
        print("[3/5] Skipping PostgreSQL connectivity check")

    if not args.skip_model_check:
        print("[4/5] Checking model cache availability")
        from app.ai.model_loader import get_model_status

        model_status = get_model_status()
        missing = [name for name, ready in model_status.items() if not ready]
        for name, ready in model_status.items():
            print(f" - {name}: {'READY' if ready else 'MISSING'}")
        if missing:
            print("Some models are missing. Run scripts/download_models.ps1 first.")
            return 1
    else:
        print("[4/5] Skipping model cache check")

    print("[5/5] Starting backend")
    process = subprocess.Popen([sys.executable, str(PROJECT_ROOT / "run.py")], cwd=str(PROJECT_ROOT))
    return process.wait()


if __name__ == "__main__":
    raise SystemExit(main())
