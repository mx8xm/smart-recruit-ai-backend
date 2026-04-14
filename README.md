# Smart Recruit AI Backend

FastAPI backend for job management, CV uploads, AI-based CV processing, and candidate scoring.

## What This Project Is Today

- Local-first Python backend
- PostgreSQL + SQLAlchemy async
- JWT authentication
- Job CRUD APIs
- Bulk CV upload with background processing
- AI-based extraction and scoring

This repo is now prepared for cleaner local setup, controlled model downloads, Windows-friendly helper scripts, structured logs, and future packaging readiness.

## Current Startup Flow

1. `run.py` loads settings through `app.core.config.get_settings()`.
2. The app reads `ENV_FILE` if provided; otherwise it auto-uses `.env.local` when present.
3. `app.main` configures logging, ensures runtime folders exist, and starts FastAPI.
4. If `AUTO_CREATE_TABLES=True`, the app creates missing tables using SQLAlchemy `Base.metadata.create_all()`.
5. AI models are not downloaded during normal API startup; they should be prepared with `download_models.py` or the helper scripts.

## Project Structure

```text
app/
alembic/
scripts/
tests/
uploads/
run.py
download_models.py
README.md
requirements.txt
Procfile
```

Support/runtime directories used locally:

- `logs/` for setup, runner, and backend logs
- `.cache/` for local model caches
- `uploads/` for uploaded CV files
- `data/` reserved for future local installer/runtime assets

## Local Setup

### Option A: One-command setup on Windows PowerShell

```powershell
.\scripts\setup_env.ps1
```

This will:

- create `venv/`
- upgrade `pip`, `setuptools`, and `wheel`
- install `requirements.txt`
- write a full setup log to `logs/setup_env.log`

### Option B: Manual setup

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

## Environment Files

Tracked examples:

- `.env.example`
- `.env.local.example`
- `.env.deploy.example`

Untracked local files:

- `.env`
- `.env.local`
- `.env.deploy`

### Recommended local flow

```powershell
Copy-Item .env.local.example .env.local
```

Then update `.env.local` with your local PostgreSQL credentials and any local paths you want to override.

### Important config keys

- `DATABASE_URL`: async PostgreSQL connection string
- `UPLOAD_FOLDER`: local upload storage
- `LOG_FOLDER`: log output folder
- `MODEL_CACHE_DIR`: project-local cache root for AI models
- `HF_HOME`, `TRANSFORMERS_CACHE`, `SENTENCE_TRANSFORMERS_HOME`, `TORCH_HOME`: model cache env vars
- `AUTO_CREATE_TABLES`: keep `True` for current local bootstrap behavior
- `ENABLE_PRETTY_LOGS`: colored console logs for local use
- `SCORING_MODEL`: use the full Hugging Face repo id, for example `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

## PostgreSQL Setup

The current project-safe DB bootstrap path is:

- connect using `DATABASE_URL`
- create missing tables with SQLAlchemy `create_all()` when `AUTO_CREATE_TABLES=True`

Alembic files exist, but the active local bootstrap flow currently relies on `create_all()` for normal startup.

### Quick local preflight

```powershell
.\scripts\check_postgres.ps1
```

To create tables if the database exists but the tables are missing:

```powershell
.\scripts\check_postgres.ps1 -EnsureTables
```

If PostgreSQL is not installed or your database/user is missing, see `pgql.txt` for a manual SQL bootstrap example.

### If PostgreSQL Is Missing

This backend keeps PostgreSQL outside the app package by default.

Optional local helpers:

```powershell
.\scripts\download_postgres_installer.ps1
.\scripts\install_postgres_silent.bat
```

Installer target:

- `data/postgresql-18.3-2-windows-x64.exe`

Notes:

- PostgreSQL is not auto-installed by the backend
- the installer helper is user-controlled and optional
- use `pgql.txt` as the local SQL bootstrap reference after install

## Model Download Management

Models are kept outside source control and should not be committed.

### Check whether required models already exist

```powershell
.\scripts\download_models.ps1 -CheckOnly
```

### Download missing models

```powershell
.\scripts\download_models.ps1
```

What happens:

- the project resolves a controlled local cache path
- already cached model snapshots are skipped
- missing model snapshots are downloaded
- the actual models are then loaded once to warm the cache
- logs are saved to `logs/download_models_pretty.log` and `logs/download_models_raw.log`

This keeps normal API startup lighter and supports a future first-run download flow.

## Run The Backend Locally

### Recommended local runner

```powershell
.\scripts\run_local.ps1
```

This runner:

- checks config
- checks PostgreSQL connectivity
- checks whether required models are already cached
- starts the backend only if the preflight is OK
- tells you how to download PostgreSQL if it is missing

Optional flags:

```powershell
.\scripts\run_local.ps1 -SkipModelCheck
.\scripts\run_local.ps1 -SkipDbCheck
```

### Direct startup still works

```powershell
python run.py
```

## Terminal Launcher

For future desktop-app integration and nicer local UX, a launcher helper is included:

```powershell
.\scripts\launch_backend_terminal.ps1
```

Behavior:

- prefers `wt.exe` when Windows Terminal is available
- falls back to PowerShell if Windows Terminal is not found
- can later be reused by a frontend app

## Logging

The backend now uses a safer local logging strategy:

- cleaner console output
- request lines like `GET /api/v1/jobs -> 200`
- reduced SQLAlchemy/Uvicorn access log noise
- full raw technical logs kept in files

Typical local logs:

- `logs/backend_pretty.log`
- `logs/backend_raw.log`
- `logs/run_local.log`
- `logs/setup_env.log`
- `logs/postgres_setup_pretty.log`
- `logs/postgres_setup_raw.log`
- `logs/download_models_pretty.log`
- `logs/download_models_raw.log`

## Safe Local Cleanup

Preview removable local junk:

```powershell
.\scripts\cleanup_local.ps1
```

Actually remove matched local junk:

```powershell
.\scripts\cleanup_local.ps1 -Apply
```

This cleanup helper is intentionally conservative. It targets local runtime artifacts such as:

- `venv/`
- `.venv/`
- `.cache/`
- `logs/`
- `build/`
- `dist/`
- `artifacts/`
- `__pycache__/`
- temporary files like `*.tmp`, `*.bak`, `*.dump`

It is designed not to remove source folders like `app/`, `alembic/`, or `tests/`.

## Tests

The test suite exists under `tests/`, but it still needs cleanup work for full reproducible execution on a fresh machine.

Known gap:

- the current tests need fixture/database wiring cleanup before they can be treated as a stable CI gate

This repo preparation work intentionally avoided risky refactors to endpoint/business logic.

## Deploy Notes

`Procfile` remains:

```txt
web: python run.py
```

For deploy environments:

- keep model caches outside git
- set deploy-specific env vars using `.env.deploy.example` as a template
- keep secrets out of tracked files

## Future Packaging Direction

Recommended future path:

- frontend EXE
- backend runner/package
- model download on first run
- project-local cache and logs
- launcher that prefers Windows Terminal and falls back cleanly

For large Python backends with AI dependencies, `onedir`-style packaging is usually a better next step than forcing everything into one huge file immediately.

## Windows Packaging

This backend is prepared for a Windows-first PyInstaller build with:

- `onedir` as the main recommended artifact
- `onefile` as an extra optional artifact
- `.env.local` as the local runtime convention
- first-run model download kept separate from the main package by default

### Local packaging

```powershell
.\scripts\build_local.ps1 -Mode both
```

Artifacts are written to:

- `output/artifacts/smart-recruit-backend-onedir.zip`
- `output/artifacts/smart-recruit-backend-onefile.zip`
- `output/artifacts/smart-recruit-backend-onefile.exe`

### GitHub Actions packaging

Workflow file:

- `.github/workflows/build-backend-windows.yml`

The workflow:

- runs on `windows-latest`
- installs Python 3.10
- installs project dependencies
- builds the main `onedir` package
- optionally builds the extra `onefile` package
- uploads downloadable artifacts

### Packaged startup

Recommended launcher flow:

- `launchers/windows_terminal_launcher.ps1`
- `scripts/start_backend.ps1`
- `scripts/start_backend.cmd`

Priority:

- use `wt.exe` if available
- otherwise PowerShell
- otherwise `cmd.exe`

The packaged backend still expects PostgreSQL to exist locally and uses `.env.local` as the primary local configuration file.

## Troubleshooting

### Python not found

- install Python 3.10+
- ensure `python` is available in `PATH`
- rerun `.\scripts\setup_env.ps1`

### PostgreSQL connection failed

- verify `DATABASE_URL` in `.env.local`
- make sure PostgreSQL is installed and running
- run `.\scripts\check_postgres.ps1`
- use `pgql.txt` for manual DB/user creation help

### Models missing

- run `.\scripts\download_models.ps1`
- confirm the cache path in `.env.local`
- check `logs/download_models_raw.log`

### Backend starts but feels noisy

- leave `ENABLE_PRETTY_LOGS=True` locally
- keep `DEBUG=False` unless you really need verbose debugging
- inspect `logs/backend_raw.log` for the full technical trace

## Notes

- Do not commit secrets.
- Do not commit downloaded model caches.
- Do not commit local uploads unless you intentionally want sample runtime artifacts in the repo.
- Do not package PostgreSQL inside the backend itself by default.
- The current business logic, routes, auth flow, AI processing flow, and DB schema were intentionally kept intact.
