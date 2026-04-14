import logging

from app.ai.model_loader import configure_model_cache, preload_all_models


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    cache_dir = configure_model_cache()

    logger.info("=" * 70)
    logger.info("Smart Recruit AI - Downloading AI Models")
    logger.info("=" * 70)
    logger.info("This is a one-time cache warmup step, not API startup")

    preload_all_models()

    logger.info("=" * 70)
    logger.info("ALL MODELS DOWNLOADED SUCCESSFULLY")
    logger.info("Cache directory: %s", cache_dir)
    logger.info("Application is ready to use cached models")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
