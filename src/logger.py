# src/logger.py
"""
Structured logging for BHAROSINT.

Replaces scattered print() calls with a proper logging system that:
  - Has severity levels (DEBUG / INFO / WARNING / ERROR)
  - Optionally writes to a log file for post-mortem analysis
  - Uses colour in terminal output for quick visual scanning
  - Prefixes every line with a timestamp and module name
"""

import logging
import sys
from src.config import CFG


def get_logger(name: str) -> logging.Logger:
    """
    Return a configured logger for the given module name.

    Usage in any module:
        from src.logger import get_logger
        log = get_logger(__name__)
        log.info("Search started for query: %s", query)
        log.warning("Rate limited by DuckDuckGo")
        log.error("Translation API unreachable: %s", err)
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if called multiple times
    if logger.handlers:
        return logger

    level_str = CFG.get("logging", {}).get("level", "INFO").upper()
    level = getattr(logging, level_str, logging.INFO)
    logger.setLevel(level)

    # ── Console handler (coloured via format) ──
    console = logging.StreamHandler(sys.stderr)
    console.setLevel(level)
    fmt = logging.Formatter(
        fmt="%(asctime)s │ %(levelname)-7s │ %(name)-20s │ %(message)s",
        datefmt="%H:%M:%S",
    )
    console.setFormatter(fmt)
    logger.addHandler(console)

    # ── Optional file handler ──
    log_file = CFG.get("logging", {}).get("file", "")
    if log_file:
        try:
            fh = logging.FileHandler(log_file, encoding="utf-8")
            fh.setLevel(logging.DEBUG)  # File always gets full detail
            fh.setFormatter(logging.Formatter(
                fmt="%(asctime)s │ %(levelname)-7s │ %(name)s │ %(message)s"
            ))
            logger.addHandler(fh)
        except Exception:
            logger.warning("Could not open log file: %s", log_file)

    return logger
