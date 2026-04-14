import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import PROJECT_ROOT, get_settings
from app.database import Base, engine
import app.models  # noqa: F401


settings = get_settings()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("docling").setLevel(logging.WARNING)
logging.getLogger("rapidocr").setLevel(logging.WARNING)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
logging.getLogger("transformers").setLevel(logging.ERROR)


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
