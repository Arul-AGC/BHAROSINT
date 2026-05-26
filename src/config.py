# src/config.py
"""
Centralized configuration loader for BHAROSINT.

Loads settings from config.yaml with sensible defaults when the file
is missing or incomplete. Every module imports from here instead of
hardcoding values.
"""

import os
import yaml

_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")

_DEFAULTS = {
    "search": {
        "request_delay": 0.8,
        "max_retries": 3,
        "results_per_lang": 8,
    },
    "languages": {
        "English": "en",
        "Hindi": "hi",
        "Tamil": "ta",
        "Telugu": "te",
        "Malayalam": "ml",
        "Bengali": "bn",
    },
    "api_keys": {
        "shodan": "",
        "virustotal": "",
    },
    "export": {
        "default_format": "html",
        "default_directory": "reports",
    },
    "logging": {
        "level": "INFO",
        "file": "",
    },
}


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override into base, preferring override values."""
    merged = base.copy()
    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config() -> dict:
    """Load config.yaml and merge with defaults."""
    if os.path.isfile(_CONFIG_PATH):
        try:
            with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
                user_config = yaml.safe_load(f) or {}
            return _deep_merge(_DEFAULTS, user_config)
        except Exception:
            pass
    return _DEFAULTS.copy()


# Singleton — loaded once at import time, reused everywhere.
CFG = load_config()
