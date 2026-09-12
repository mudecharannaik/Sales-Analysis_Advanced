"""Configuration module for the Superstore Sales Analysis project.

This module centralises every path, constant and shared utility used across the
pipeline. Importing it guarantees that the required output directories exist and
exposes a consistent logging factory used by all other scripts.
"""

from __future__ import annotations

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# --------------------------------------------------------------------------- #
# Project layout
# --------------------------------------------------------------------------- #
ENV_ROOT = os.environ.get("SUPERSTORE_PROJECT_ROOT")

if ENV_ROOT:
    PROJECT_ROOT = Path(ENV_ROOT)
else:
    # SalesAnalysis/ is two levels above this file (Python/config.py -> SalesAnalysis/)
    PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "Data"
RAW_DATA_PATH = DATA_DIR / "superstore_raw.csv"
CLEAN_DATA_PATH = DATA_DIR / "superstore_clean.csv"

PYTHON_DIR = PROJECT_ROOT / "Python"
SCRIPTS_DIR = PYTHON_DIR / "scripts"
NOTEBOOKS_DIR = PYTHON_DIR / "notebooks"

LOG_DIR = PROJECT_ROOT / "Logs"
OUTPUT_DIR = PROJECT_ROOT / "Outputs"
SQL_DIR = PROJECT_ROOT / "SQL"
REPORT_DIR = OUTPUT_DIR / "reports"
EXCEL_DIR = OUTPUT_DIR / "Excel"
VISUALIZATION_DIR = OUTPUT_DIR / "Visualizations"
DOCS_DIR = OUTPUT_DIR / "Documentation"
HTML_DIR = OUTPUT_DIR / "HTML"

# Ensure required directories exist.
for _d in (
    DATA_DIR,
    LOG_DIR,
    OUTPUT_DIR,
    SQL_DIR,
    REPORT_DIR,
    EXCEL_DIR,
    VISUALIZATION_DIR,
    DOCS_DIR,
    HTML_DIR,
):
    _d.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------- #
# Pipeline constants
# --------------------------------------------------------------------------- #
RANDOM_SEED = 42
DATE_FORMAT = "%m/%d/%Y"  # e.g. 1/1/2011
TARGET_COLUMN = "Profit"

NUMERIC_COLUMNS = [
    "Sales",
    "Quantity",
    "Discount",
    "Profit",
    "Shipping Cost",
]

CATEGORICAL_COLUMNS = [
    "Ship Mode",
    "Segment",
    "Category",
    "Sub-Category",
    "Region",
    "Market",
    "Order Priority",
]

ID_COLUMNS = [
    "Row ID",
    "Order ID",
    "Customer ID",
    "Product ID",
]

GEO_COLUMNS = ["Country", "Region", "Market", "State", "City", "Postal Code"]

ZSCORE_THRESHOLD = 3.0
IQR_MULTIPLIER = 1.5

PROPHET_AVAILABLE = False
DOCX_AVAILABLE = False
MLXTEND_AVAILABLE = False
WORDCLOUD_AVAILABLE = False
XGBOOST_AVAILABLE = False


def _safe_import(name: str, global_name: str) -> bool:
    """Attempt to import an optional dependency and record availability."""
    try:
        __import__(name)
        globals()[global_name] = True
        return True
    except Exception:
        globals()[global_name] = False
        return False


_safe_import("prophet", "PROPHET_AVAILABLE")
_safe_import("docx", "DOCX_AVAILABLE")
_safe_import("mlxtend", "MLXTEND_AVAILABLE")
_safe_import("wordcloud", "WORDCLOUD_AVAILABLE")
_safe_import("xgboost", "XGBOOST_AVAILABLE")


# --------------------------------------------------------------------------- #
# Logging
# --------------------------------------------------------------------------- #
def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Create (or fetch) a logger that writes to the central log directory.

    Args:
        name: Logger name, conventionally the module name.
        level: Logging level (defaults to ``logging.INFO``).

    Returns:
        A configured :class:`logging.Logger` instance with both a console and a
        timestamped file handler.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if getattr(logger, "handlers", []):
        # Already configured - avoid duplicate handlers.
        return logger

    log_file = LOG_DIR / f"{datetime.now():%Y-%m-%d}_{name}.log"
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(level)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.propagate = False
    return logger


def data_path() -> Path:
    """Return the path to the raw dataset, validating existence."""
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Raw dataset not found at {RAW_DATA_PATH}. "
            "Set SUPERSTORE_PROJECT_ROOT or place the file accordingly."
        )
    return RAW_DATA_PATH
