import argparse
import contextlib
import io
import logging
import os
import warnings
from pathlib import Path

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
warnings.filterwarnings("ignore")

with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
    from app.ai.model_loader import (
        configure_model_cache,
        ensure_model_snapshots,
        get_model_status,
        preload_all_models,
    )
from app.core.logging_setup import configure_logging


configure_logging(log_name_prefix="download_models", debug=False)
logger = logging.getLogger(__name__)
DOCLING_MARKER = "docling_ocr_models.ready"


def _docling_marker_path(cache_dir: Path) -> Path:
    return cache_dir / DOCLING_MARKER


def get_docling_status(cache_dir: Path) -> bool:
    return _docling_marker_path(cache_dir).exists()


def ensure_docling_models(cache_dir: Path) -> None:
    marker_path = _docling_marker_path(cache_dir)
    if marker_path.exists():
        logger.info("docling_ocr_models: READY")
        return

    logger.info("[1/3] Downloading Docling & OCR models...")
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            from docling.document_converter import DocumentConverter, PdfFormatOption
            from docling.datamodel.base_models import InputFormat
            from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode

            pipeline_options = PdfPipelineOptions()
            pipeline_options.do_ocr = True
            pipeline_options.do_table_structure = True
            pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE

            DocumentConverter(
                format_options={
                    InputFormat.PDF: PdfFormatOption(
                        pipeline_options=pipeline_options
                    )
                }
            )

        marker_path.write_text("ready\n", encoding="utf-8")
        logger.info("Docling & OCR models ready")
    except Exception as exc:
        logger.error("Failed to download Docling models: %s", exc)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description="Download or verify Smart Recruit AI models.")
    parser.add_argument("--check-only", action="store_true", help="Only check whether required models exist.")
    args = parser.parse_args()

    cache_dir = configure_model_cache()

    logger.info("=" * 70)
    logger.info("Smart Recruit AI - Downloading AI Models")
    logger.info("=" * 70)
    logger.info("This is a one-time cache warmup step, not API startup")

    if args.check_only:
        status = get_model_status()
        docling_ready = get_docling_status(cache_dir)
        logger.info("docling_ocr_models: %s", "READY" if docling_ready else "MISSING")
        for name, available in status.items():
            logger.info("%s: %s", name, "READY" if available else "MISSING")
        if not all(status.values()) or not docling_ready:
            raise SystemExit(1)
        return

    ensure_docling_models(cache_dir)
    ensure_model_snapshots(download_missing=True)
    preload_all_models()

    logger.info("=" * 70)
    logger.info("ALL MODELS DOWNLOADED SUCCESSFULLY")
    logger.info("Cache directory: %s", cache_dir)
    logger.info("Application is ready to use cached models")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
