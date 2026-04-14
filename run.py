import os
import sys

import uvicorn

from app.core.config import get_settings
from app.core.logging_setup import configure_logging


settings = get_settings()


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
