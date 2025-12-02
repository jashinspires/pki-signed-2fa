"""Shared logging configuration."""
from __future__ import annotations

import logging
import sys

_LOG_FORMAT = "%(asctime)sZ | %(levelname)s | %(name)s | %(message)s"

def configure_logging() -> None:
    """Configure root logger for the service."""

    logging.basicConfig(
        level=logging.INFO,
        format=_LOG_FORMAT,
        datefmt="%Y-%m-%dT%H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )


def get_logger(name: str) -> logging.Logger:
    configure_logging()
    return logging.getLogger(name)
