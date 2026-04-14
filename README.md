# Smart Recruit AI Backend

FastAPI backend for job management, CV uploads, AI-based CV processing, and candidate scoring.

## Features

- JWT authentication
- Job CRUD APIs
- Bulk CV upload
- Background CV processing
- PostgreSQL with SQLAlchemy async
- Local development with `.env.local`
- Choreo deploy with environment variables

## Tech Stack

- FastAPI
- SQLAlchemy Async
- PostgreSQL
- asyncpg
- Docling
- GLiNER
- Sentence Transformers

## Local Setup

### 1. Create and activate a virtual environment

```powershell
python -m venv venv
venv\Scripts\activate
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Prepare environment file

```powershell
copy .env.local.example .env.local
```

Update `.env.local` with your local PostgreSQL credentials if needed.

### 4. Download AI models once

```powershell
python download_models.py
```

This warms the Hugging Face cache. It is not part of normal API startup.

### 5. Run the API

```powershell
python run.py
```

Local API URLs:

- `http://localhost:8000/health`
- `http://localhost:8000/docs`

## Environment Files

- `.env.local.example`: local development example
- `.env.deploy.example`: deploy example for Choreo
- `.env.local`: local file used by the app automatically if present

If `ENV_FILE` is set, the app uses that file instead.

## Model Loading

- `Docling` extracts the full CV text
- `PyMuPDF` is only used as a helper for fast raw text extraction
- `GLiNER` extracts names and other entities
- `Sentence Transformers` calculates the match score

## Choreo Deploy

### Procfile

```txt
web: python run.py
```

### Required Environment Variables

```env
APP_NAME=Smart Recruit AI
VERSION=1.0.0
DEBUG=False
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@db.ezhwwebjkhjsxbykvwsf.supabase.co:5432/postgres
SECRET_KEY=CHANGE_ME_STRONG_SECRET
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
UPLOAD_FOLDER=./uploads
MAX_FILE_SIZE=10485760
MAX_FILES_PER_UPLOAD=1000
GLINER_MODEL=urchade/gliner_multi-v2.1
SCORING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
ACCEPTANCE_THRESHOLD=0.45
ALLOWED_ORIGINS=https://YOUR-FRONTEND-DOMAIN
HF_HOME=/app/.cache
TRANSFORMERS_CACHE=/app/.cache
SENTENCE_TRANSFORMERS_HOME=/app/.cache
TORCH_HOME=/app/.cache
AUTO_CREATE_TABLES=True
```

### Deploy Steps

1. Push this repository to GitHub.
2. Create a `Service` in Choreo from the repo.
3. Keep the `Procfile` in the project root.
4. Add the environment variables in Choreo Configs and Secrets.
5. Deploy and test `/health`.

## Notes

- Do not put secrets in tracked files.
- Do not put `download_models.py` in `Procfile`.
- Choreo should provide `PORT`; locally the app defaults to `8000`.
- Old failed CV processing records stay failed until you re-upload or reprocess them.
