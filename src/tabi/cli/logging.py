"""Machine-readable diagnostics kept separate from command output."""

import json
import logging
import sys
from datetime import UTC, datetime


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps(
            {
                "time": datetime.fromtimestamp(record.created, UTC).isoformat(),
                "level": record.levelname.lower(),
                "event": record.getMessage(),
            },
            ensure_ascii=False,
        )


def configure_logging(level: str) -> logging.Logger:
    logger = logging.getLogger("tabi")
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JsonFormatter())
    logger.handlers[:] = [handler]
    logger.setLevel(level)
    logger.propagate = False
    return logger
