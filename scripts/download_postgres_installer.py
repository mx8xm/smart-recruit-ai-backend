from __future__ import annotations

import argparse
import urllib.request
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_INSTALLER_NAME = "postgresql-18.3-2-windows-x64.exe"
DEFAULT_INSTALLER_URL = "https://sbp.enterprisedb.com/getfile.jsp?fileid=1260118"


def main() -> int:
    parser = argparse.ArgumentParser(description="Download the PostgreSQL Windows installer into the local data folder.")
    parser.add_argument("--url", default=DEFAULT_INSTALLER_URL)
    parser.add_argument("--output", default=str(DEFAULT_DATA_DIR / DEFAULT_INSTALLER_NAME))
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists():
        print(f"Installer already exists: {output_path}")
        return 0

    print(f"Downloading PostgreSQL installer to: {output_path}")
    try:
        with urllib.request.urlopen(args.url) as response, output_path.open("wb") as handle:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                handle.write(chunk)
    except Exception as exc:
        print(f"Installer download failed: {exc}")
        return 1

    print(f"Installer downloaded successfully: {output_path}")
    print("Optional next step: scripts\\install_postgres_silent.bat")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
