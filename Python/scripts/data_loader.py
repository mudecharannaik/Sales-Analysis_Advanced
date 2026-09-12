"""Data ingestion utilities for the Superstore dataset.

Provides functions to load the raw CSV, apply a stable parse schema (typing the
date columns, coercing numerics and trimming text) and to persist the cleaned
frame back to disk. Every function is logged for auditability.
"""

from __future__ import annotations

import os
from typing import Tuple

import pandas as pd

from config import (
    CLEAN_DATA_PATH,
    NUMERIC_COLUMNS,
    RAW_DATA_PATH,
    get_logger,
)

logger = get_logger(__name__)


def load_raw_data(path: str | os.PathLike | None = None) -> pd.DataFrame:
    """Load the raw Superstore CSV with a fixed parsing schema.

    Args:
        path: Optional override for the raw data path. Defaults to the path
            configured in :mod:`config`.

    Returns:
        A :class:`pandas.DataFrame` with correctly typed date and numeric
        columns. No cleaning beyond type coercion is performed here.
    """
    source = path or RAW_DATA_PATH
    logger.info("Loading raw dataset from %s", source)

    df = pd.read_csv(
        source,
        dtype={
            "Postal Code": "float64",
            "Order ID": "string",
            "Customer ID": "string",
            "Product ID": "string",
        },
        low_memory=False,
    )

    # Parse dates defensively (handles both m/d/Y and already-parsed formats).
    for col in ("Order Date", "Ship Date"):
        df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=False)

    # Coerce known numeric columns.
    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Normalise whitespace on common text columns.
    text_cols = [
        "Customer Name",
        "Segment",
        "City",
        "State",
        "Country",
        "Market",
        "Region",
        "Category",
        "Sub-Category",
        "Ship Mode",
        "Order Priority",
        "Product Name",
    ]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype("string").str.strip()

    logger.info("Raw dataset loaded: %d rows x %d columns", *df.shape)
    return df


def save_clean_data(df: pd.DataFrame, path: str | os.PathLike | None = None) -> str:
    """Persist a cleaned/transformed DataFrame to CSV.

    Args:
        df: DataFrame to persist.
        path: Optional destination; defaults to ``CLEAN_DATA_PATH``.

    Returns:
        The absolute string path of the written file.
    """
    destination = path or CLEAN_DATA_PATH
    os.makedirs(os.path.dirname(str(destination)), exist_ok=True)
    df.to_csv(destination, index=False)
    logger.info("Cleaned data written to %s (%d rows)", destination, len(df))
    return str(destination)


def get_train_test_split(
    df: pd.DataFrame, date_col: str = "Order Date", test_size: float = 0.2
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Chronologically split a frame into train/test by a date column.

    Args:
        df: Sorted-by-time DataFrame.
        date_col: Name of the date column used for ordering.
        test_size: Fraction of the most recent rows to allocate to the test set.

    Returns:
        A tuple ``(train_df, test_df)``.
    """
    if date_col not in df.columns:
        raise KeyError(f"{date_col} not present in DataFrame")

    ordered = df.sort_values(date_col)
    split_idx = int(len(ordered) * (1 - test_size))
    train = ordered.iloc[:split_idx].copy()
    test = ordered.iloc[split_idx:].copy()
    logger.info("Train/test split: %d / %d rows", len(train), len(test))
    return train, test
