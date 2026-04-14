import logging
import os
from functools import lru_cache
from pathlib import Path

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")

import torch
from huggingface_hub import snapshot_download
from sentence_transformers import SentenceTransformer

from app.core.config import PROJECT_ROOT, get_settings


logger = logging.getLogger(__name__)
settings = get_settings()


def _resolve_model_repo_id(model_name: str, default_namespace: str | None = None) -> str:
    cleaned = model_name.strip()
    if "/" in cleaned or not default_namespace:
        return cleaned
    return f"{default_namespace}/{cleaned}"


def _resolve_cache_dir() -> Path:
    cache_dir = (
        os.getenv("MODEL_CACHE_DIR")
        or os.getenv("HF_HOME")
        or os.getenv("TRANSFORMERS_CACHE")
        or str(settings.model_cache_path)
    )
    path = Path(cache_dir)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    path.mkdir(parents=True, exist_ok=True)
    return path


def configure_model_cache() -> Path:
    cache_dir = _resolve_cache_dir()

    os.environ["MODEL_CACHE_DIR"] = str(cache_dir)
    os.environ["HF_HOME"] = str(cache_dir)
    os.environ["TRANSFORMERS_CACHE"] = str(cache_dir)
    os.environ["SENTENCE_TRANSFORMERS_HOME"] = str(cache_dir)
    os.environ["TORCH_HOME"] = str(cache_dir)

    return cache_dir


@lru_cache(maxsize=1)
def get_scoring_model():
    cache_dir = configure_model_cache()
    scoring_repo_id = _resolve_model_repo_id(
        settings.SCORING_MODEL,
        default_namespace="sentence-transformers",
    )
    logger.info("Loading Scoring Model: %s", scoring_repo_id)

    model = SentenceTransformer(
        scoring_repo_id,
        cache_folder=str(cache_dir),
    )

    logger.info("Scoring Model loaded successfully")
    return model


@lru_cache(maxsize=1)
def get_gliner_model():
    cache_dir = configure_model_cache()
    from gliner import GLiNER

    gliner_repo_id = _resolve_model_repo_id(settings.GLINER_MODEL)
    logger.info("Loading GLiNER Model: %s", gliner_repo_id)
    model = GLiNER.from_pretrained(
        gliner_repo_id,
        cache_dir=str(cache_dir),
    ).to("cuda" if torch.cuda.is_available() else "cpu")

    logger.info("GLiNER Model loaded successfully")
    return model


def _snapshot_repo_id(model_name: str, cache_dir: Path, local_only: bool) -> bool:
    try:
        snapshot_download(
            repo_id=model_name,
            cache_dir=str(cache_dir),
            local_files_only=local_only,
        )
        return True
    except Exception:
        return False


def get_model_status() -> dict[str, bool]:
    cache_dir = configure_model_cache()
    return {
        "scoring_model": _snapshot_repo_id(
            _resolve_model_repo_id(settings.SCORING_MODEL, default_namespace="sentence-transformers"),
            cache_dir,
            local_only=True,
        ),
        "gliner_model": _snapshot_repo_id(
            _resolve_model_repo_id(settings.GLINER_MODEL),
            cache_dir,
            local_only=True,
        ),
    }


def ensure_model_snapshots(download_missing: bool = True) -> dict[str, bool]:
    cache_dir = configure_model_cache()
    targets = {
        "scoring_model": _resolve_model_repo_id(
            settings.SCORING_MODEL,
            default_namespace="sentence-transformers",
        ),
        "gliner_model": _resolve_model_repo_id(settings.GLINER_MODEL),
    }
    status: dict[str, bool] = {}

    for label, model_name in targets.items():
        available_locally = _snapshot_repo_id(model_name, cache_dir, local_only=True)
        if available_locally:
            logger.info("%s is already cached: %s", label, model_name)
            status[label] = True
            continue

        if not download_missing:
            logger.warning("%s is missing from cache: %s", label, model_name)
            status[label] = False
            continue

        logger.info("Downloading missing model snapshot for %s: %s", label, model_name)
        snapshot_download(repo_id=model_name, cache_dir=str(cache_dir), local_files_only=False)
        status[label] = True

    return status


def preload_all_models() -> bool:
    cache_dir = configure_model_cache()
    logger.info("Using model cache directory: %s", cache_dir)
    ensure_model_snapshots(download_missing=True)

    get_scoring_model()
    get_gliner_model()

    logger.info("All models are downloaded/cached and ready")
    return True


if __name__ == "__main__":
    preload_all_models()
