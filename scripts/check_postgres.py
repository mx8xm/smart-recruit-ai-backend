from __future__ import annotations

import argparse
import asyncio
import textwrap
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import get_settings
from app.core.logging_setup import configure_logging
from app.database import Base


POSTGRES_INSTALLER_NAME = "postgresql-18.3-2-windows-x64.exe"
POSTGRES_INSTALLER_URL = "https://sbp.enterprisedb.com/getfile.jsp?fileid=1260118"
DEFAULT_DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_INSTALLER_PATH = DEFAULT_DATA_DIR / POSTGRES_INSTALLER_NAME


def find_psql() -> str | None:
    direct = shutil.which("psql")
    if direct:
        return direct

    common_paths = [
        Path(r"C:\Program Files\PostgreSQL\18\bin\psql.exe"),
        Path(r"C:\Program Files\PostgreSQL\17\bin\psql.exe"),
        Path(r"C:\Program Files\PostgreSQL\16\bin\psql.exe"),
    ]
    for candidate in common_paths:
        if candidate.exists():
            return str(candidate)
    return None


def installer_hint() -> str:
    return textwrap.dedent(
        f"""
        PostgreSQL was not detected locally.
        Suggested next steps:
        1. Download installer with:
           python scripts/download_postgres_installer.py
        2. Or download manually:
           {POSTGRES_INSTALLER_URL}
        3. Saved installer target:
           {DEFAULT_INSTALLER_PATH}
        4. Optional silent installer helper:
           scripts\\install_postgres_silent.bat
        5. After install, run:
           python scripts/check_postgres.py --ensure-tables
        """
    ).strip()


def print_bootstrap_sql_help() -> None:
    print("Use pgql.txt for the local bootstrap SQL example:")
    print('cd "C:\\Program Files\\PostgreSQL\\18\\bin"')
    print("psql -U postgres")
    print("CREATE DATABASE smart_recruit_db;")
    print('CREATE USER "user" WITH PASSWORD \'password123\';')
    print('GRANT ALL PRIVILEGES ON DATABASE smart_recruit_db TO "user";')
    print('ALTER DATABASE smart_recruit_db OWNER TO "user";')


async def inspect_database(ensure_tables: bool) -> int:
    settings = get_settings()
    logger_dir = configure_logging(log_name_prefix="postgres_setup", debug=settings.DEBUG)
    print(f"Log files: {logger_dir}")

    psql_path = find_psql()
    if psql_path:
        print(f"psql detected: {psql_path}")
    else:
        print("psql was not found in PATH. SQL commands may need to be run manually.")
        print(installer_hint())

    engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
            print("Database connection: OK")

            table_names = await connection.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())
            if table_names:
                print(f"Existing tables: {', '.join(sorted(table_names))}")
            else:
                print("No tables were found.")
                if ensure_tables and settings.AUTO_CREATE_TABLES:
                    await connection.run_sync(Base.metadata.create_all)
                    print("Tables created using SQLAlchemy Base.metadata.create_all().")
                elif ensure_tables:
                    print("AUTO_CREATE_TABLES is disabled, so tables were not created.")
                    return 1
    except Exception as exc:
        print(f"Database preflight failed: {exc}")
        print_bootstrap_sql_help()
        return 1
    finally:
        await engine.dispose()

    print("PostgreSQL preflight completed successfully.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate PostgreSQL access for Smart Recruit AI.")
    parser.add_argument("--ensure-tables", action="store_true", help="Create tables when missing using the project-safe path.")
    args = parser.parse_args()

    print(f"Project root: {PROJECT_ROOT}")
    return asyncio.run(inspect_database(ensure_tables=args.ensure_tables))


if __name__ == "__main__":
    raise SystemExit(main())
