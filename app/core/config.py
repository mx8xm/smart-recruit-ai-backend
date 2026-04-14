from functools import lru_cache
import json
import os
from pathlib import Path
import sys

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _resolve_project_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


PROJECT_ROOT = _resolve_project_root()


def _resolve_env_file() -> str | None:
    env_file = os.getenv("ENV_FILE")
    if env_file:
        candidate = Path(env_file)
        if not candidate.is_absolute():
            candidate = PROJECT_ROOT / candidate
        if candidate.exists():
            return str(candidate)

    candidates = [
        PROJECT_ROOT / ".env.local",
        PROJECT_ROOT / ".env",
    ]

    # Packaged builds ship examples; allow them as a local-first fallback.
    if getattr(sys, "frozen", False) or os.getenv("SMART_RECRUIT_PACKAGED") == "1":
        candidates.extend(
            [
                PROJECT_ROOT / ".env.local.example",
                PROJECT_ROOT / ".env.example",
            ]
        )

    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    return None


class Settings(BaseSettings):
    APP_NAME: str = "Smart Recruit AI"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    UPLOAD_FOLDER: str = "./uploads"
    MAX_FILE_SIZE: int = 10485760
    MAX_FILES_PER_UPLOAD: int = 1000
    ALLOWED_EXTENSIONS: list[str] = Field(default_factory=lambda: [".pdf", ".docx", ".doc"])

    GLINER_MODEL: str = "urchade/gliner_multi-v2.1"
    SCORING_MODEL: str = "paraphrase-multilingual-MiniLM-L12-v2"
    ACCEPTANCE_THRESHOLD: float = 0.45
    MODEL_CACHE_DIR: str = "./.cache"

    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    AUTO_CREATE_TABLES: bool = True
    LOG_FOLDER: str = "./logs"
    ENABLE_PRETTY_LOGS: bool = True

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    @field_validator("ALLOWED_EXTENSIONS", mode="before")
    @classmethod
    def parse_allowed_extensions(cls, value: object) -> object:
        if isinstance(value, str):
            cleaned = value.strip()
            if not cleaned:
                return []
            if cleaned.startswith("["):
                return json.loads(cleaned)
            return [item.strip() for item in cleaned.split(",") if item.strip()]
        return value

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    @property
    def upload_folder_path(self) -> Path:
        path = Path(self.UPLOAD_FOLDER)
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        return path

    @property
    def model_cache_path(self) -> Path:
        path = Path(self.MODEL_CACHE_DIR)
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        return path

    @property
    def log_folder_path(self) -> Path:
        path = Path(self.LOG_FOLDER)
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        return path


@lru_cache
def get_settings() -> Settings:
    env_file = _resolve_env_file()
    if env_file:
        return Settings(_env_file=env_file)
    return Settings()
