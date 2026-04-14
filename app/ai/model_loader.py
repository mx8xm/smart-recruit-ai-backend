import logging
import os
from functools import lru_cache
from pathlib import Path

import torch
from sentence_transformers import SentenceTransformer

from app.core.config import PROJECT_ROOT, get_settings


logger = logging.getLogger(__name__)
settings = get_settings()


def _resolve_cache_dir() -> Path:
    cache_dir = os.getenv("HF_HOME") or os.getenv("TRANSFORMERS_CACHE") or "./.cache"
    path = Path(cache_dir)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    path.mkdir(parents=True, exist_ok=True)
    return path


def configure_model_cache() -> Path:
    cache_dir = _resolve_cache_dir()

    os.environ["HF_HOME"] = str(cache_dir)
    os.environ["TRANSFORMERS_CACHE"] = str(cache_dir)
    os.environ["SENTENCE_TRANSFORMERS_HOME"] = str(cache_dir)
    os.environ["TORCH_HOME"] = str(cache_dir)

    return cache_dir


@lru_cache(maxsize=1)
def get_scoring_model():
    cache_dir = configure_model_cache()
    logger.info("Loading Scoring Model: %s", settings.SCORING_MODEL)

    model = SentenceTransformer(
        settings.SCORING_MODEL,
        cache_folder=str(cache_dir),
    )

    logger.info("Scoring Model loaded successfully")
    return model


@lru_cache(maxsize=1)
def get_gliner_model():
    cache_dir = configure_model_cache()
    from gliner import GLiNER

    logger.info("Loading GLiNER Model: %s", settings.GLINER_MODEL)
    model = GLiNER.from_pretrained(
        settings.GLINER_MODEL,
        cache_dir=str(cache_dir),
    ).to("cuda" if torch.cuda.is_available() else "cpu")

    logger.info("GLiNER Model loaded successfully")
    return model


def preload_all_models() -> bool:
    cache_dir = configure_model_cache()
    logger.info("Using model cache directory: %s", cache_dir)

    get_scoring_model()
    get_gliner_model()

    logger.info("All models are downloaded/cached and ready")
    return True


if __name__ == "__main__":
    preload_all_models()
