from __future__ import annotations

import logging
import sys
from pathlib import Path

from app.core.config import get_settings


class _ColorFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: "\033[36m",
        logging.INFO: "\033[96m",
        logging.WARNING: "\033[93m",
        logging.ERROR: "\033[91m",
        logging.CRITICAL: "\033[95m",
    }
    RESET = "\033[0m"

    def __init__(self, fmt: str, use_colors: bool) -> None:
        super().__init__(fmt=fmt, datefmt="%H:%M:%S")
        self.use_colors = use_colors

    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        if not self.use_colors:
            return message
        color = self.COLORS.get(record.levelno, "")
        if not color:
            return message
        return f"{color}{message}{self.RESET}"


def _reset_root_logger() -> logging.Logger:
    root_logger = logging.getLogger()
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)
        handler.close()
    return root_logger


def configure_logging(log_name_prefix: str = "backend", debug: bool | None = None) -> Path:
    settings = get_settings()
    log_dir = settings.log_folder_path
    log_dir.mkdir(parents=True, exist_ok=True)

    if debug is None:
        debug = settings.DEBUG

    root_logger = _reset_root_logger()
    root_logger.setLevel(logging.DEBUG)

    use_colors = bool(settings.ENABLE_PRETTY_LOGS and sys.stdout.isatty())
    console_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(
        _ColorFormatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s", use_colors=use_colors)
    )

    pretty_file = log_dir / f"{log_name_prefix}_pretty.log"
    raw_file = log_dir / f"{log_name_prefix}_raw.log"

    pretty_handler = logging.FileHandler(pretty_file, encoding="utf-8")
    pretty_handler.setLevel(console_level)
    pretty_handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s"))

    raw_handler = logging.FileHandler(raw_file, encoding="utf-8")
    raw_handler.setLevel(logging.DEBUG)
    raw_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s %(filename)s:%(lineno)d %(message)s"
        )
    )

    root_logger.addHandler(console_handler)
    root_logger.addHandler(pretty_handler)
    root_logger.addHandler(raw_handler)

    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine.Engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("watchfiles.main").setLevel(logging.WARNING)
    logging.getLogger("docling").setLevel(logging.WARNING)
    logging.getLogger("rapidocr").setLevel(logging.WARNING)
    logging.getLogger("huggingface_hub").setLevel(logging.WARNING if debug else logging.ERROR)
    logging.getLogger("transformers").setLevel(logging.WARNING if debug else logging.ERROR)
    logging.getLogger("tensorflow").setLevel(logging.ERROR)
    logging.getLogger("absl").setLevel(logging.ERROR)

    return log_dir
