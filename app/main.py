import logging
import os
from contextlib import asynccontextmanager
from time import perf_counter
from pathlib import Path

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import PROJECT_ROOT, get_settings
from app.core.logging_setup import configure_logging
from app.database import Base, engine
import app.models  # noqa: F401


settings = get_settings()
configure_logging(debug=settings.DEBUG)
logger = logging.getLogger(__name__)


def _ensure_runtime_directories() -> None:
    settings.upload_folder_path.mkdir(parents=True, exist_ok=True)
    for key in ("HF_HOME", "TRANSFORMERS_CACHE", "SENTENCE_TRANSFORMERS_HOME", "TORCH_HOME"):
        value = os.getenv(key)
        if not value:
            continue
        cache_path = Path(value)
        if not cache_path.is_absolute():
            cache_path = PROJECT_ROOT / cache_path
        cache_path.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Starting %s v%s", settings.APP_NAME, settings.VERSION)
    logger.info("Debug mode: %s", settings.DEBUG)
    logger.info("Auto create tables: %s", settings.AUTO_CREATE_TABLES)
    _ensure_runtime_directories()

    if settings.AUTO_CREATE_TABLES:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        logger.info("Database tables checked/created successfully")

    yield

    logger.info("Shutting down %s", settings.APP_NAME)
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="AI-Powered CV Filtering System for HR Recruitment",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.middleware("http")
async def log_requests(request, call_next):
    started_at = perf_counter()
    response = await call_next(request)
    elapsed_ms = (perf_counter() - started_at) * 1000
    logger.info(
        "%s %s -> %s (%.1f ms)",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


@app.get("/", tags=["Root"])
async def root() -> dict[str, str | bool]:
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "running",
        "docs": "/docs",
        "debug": settings.DEBUG,
    }


@app.get("/health", tags=["Root"])
async def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "version": settings.VERSION,
    }
