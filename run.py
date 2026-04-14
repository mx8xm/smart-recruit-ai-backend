import os
import sys

import uvicorn
from pydantic import ValidationError

from app.core.config import get_settings
from app.core.logging_setup import configure_logging


def _load_settings_or_exit():
    try:
        return get_settings()
    except ValidationError as exc:
        print("Configuration is missing.")
        print("Create a .env.local file next to the executable, or copy .env.local.example and edit it.")
        print("Required values include DATABASE_URL and SECRET_KEY.")
        raise SystemExit(1) from exc


settings = _load_settings_or_exit()


if __name__ == "__main__":
    os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")

    packaged_mode = bool(getattr(sys, "frozen", False) or os.getenv("SMART_RECRUIT_PACKAGED") == "1")
    configure_logging(debug=settings.DEBUG)
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=settings.DEBUG and not packaged_mode,
        log_level="info",
        access_log=False,
        log_config=None,
    )
