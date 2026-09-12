"""Predictive modelling: train/test split, model training and evaluation.

Provides a regression pipeline to predict Profit using Random Forest and
(optionally) XGBoost. Includes feature importance extraction and residual
analysis.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from config import RANDOM_SEED, XGBOOST_AVAILABLE, get_logger

logger = get_logger(__name__)


def chronological_train_test_split(
    df: pd.DataFrame,
    date_col: str = "Order Date",
    test_size: float = 0.2,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split data chronologically by date column.

    Args:
        df: Input DataFrame.
        date_col: Date column to sort by.
        test_size: Fraction allocated to the test set.

    Returns:
        Tuple of (train_df, test_df).
    """
    if date_col not in df.columns:
        raise KeyError(f"{date_col} not found in DataFrame")

    ordered = df.sort_values(date_col).reset_index(drop=True)
    split_idx = int(len(ordered) * (1 - test_size))
    train = ordered.iloc[:split_idx].copy()
    test = ordered.iloc[split_idx:].copy()

    logger.info(
        "Chronological split: %d train / %d test (%.0f%% / %.0f%%)",
        len(train),
        len(test),
        100 * (1 - test_size),
        100 * test_size,
    )
    return train, test


def prepare_features(
    df: pd.DataFrame,
    target_col: str = "Profit",
    feature_cols: list[str] | None = None,
) -> tuple[pd.DataFrame, pd.Series]:
    """Prepare feature matrix and target vector.

    Encodes categoricals via one-hot encoding and drops rows with NaN in
    the target.

    Args:
        df: Input DataFrame.
        target_col: Name of the target column.
        feature_cols: Explicit feature columns to use; if None, uses a
            sensible default set.

    Returns:
        Tuple of (X, y) ready for modelling.
    """
    if feature_cols is None:
        feature_cols = [
            "Sales", "Quantity", "Discount", "Shipping Cost",
            "Category", "Sub-Category", "Segment", "Region",
            "Market", "Ship Mode", "Order Priority",
        ]
        feature_cols = [c for c in feature_cols if c in df.columns and c != target_col]

    logger.info("Preparing features: %s", feature_cols)

    sub = df[feature_cols + [target_col]].dropna(subset=[target_col]).copy()
    X = pd.get_dummies(sub[feature_cols], drop_first=True)
    y = sub[target_col]

    # Drop any remaining NaN rows in features.
    valid = X.notna().all(axis=1)
    X = X[valid]
    y = y[valid]

    logger.info("Feature matrix shape: %s", X.shape)
    return X, y


def train_random_forest(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    n_estimators: int = 200,
    max_depth: int | None = 15,
    n_jobs: int = -1,
) -> RandomForestRegressor:
    """Train a Random Forest regressor.

    Args:
        X_train: Training features.
        y_train: Training target.
        n_estimators: Number of trees.
        max_depth: Maximum tree depth.
        n_jobs: Parallel jobs (-1 for all cores).

    Returns:
        Fitted RandomForestRegressor.
    """
    logger.info(
        "Training Random Forest (n_estimators=%d, max_depth=%s)",
        n_estimators,
        max_depth,
    )

    rf = RandomForestRegressor(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=RANDOM_SEED,
        n_jobs=n_jobs,
    )
    rf.fit(X_train, y_train)

    logger.info("Random Forest training complete")
    return rf


def train_xgboost(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    n_estimators: int = 200,
    max_depth: int = 8,
    learning_rate: float = 0.1,
) -> object | None:
    """Train an XGBoost regressor if the package is available.

    Args:
        X_train: Training features.
        y_train: Training target.
        n_estimators: Number of boosting rounds.
        max_depth: Maximum tree depth.
        learning_rate: Boosting learning rate.

    Returns:
        Fitted XGBoost model, or None if XGBoost is not installed.
    """
    if not XGBOOST_AVAILABLE:
        logger.warning("XGBoost not available; skipping")
        return None

    logger.info("Training XGBoost (n_estimators=%d, max_depth=%d)", n_estimators, max_depth)

    from xgboost import XGBRegressor

    model = XGBRegressor(
        n_estimators=n_estimators,
        max_depth=max_depth,
        learning_rate=learning_rate,
        random_state=RANDOM_SEED,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    logger.info("XGBoost training complete")
    return model


def evaluate_model(
    model: object,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> dict:
    """Compute regression metrics for a fitted model.

    Args:
        model: Fitted model with a ``predict`` method.
        X_test: Test features.
        y_test: True target values.

    Returns:
        Dictionary with MAE, RMSE and R2.
    """
    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    r2 = r2_score(y_test, predictions)

    metrics = {
        "MAE": round(float(mae), 4),
        "RMSE": round(float(rmse), 4),
        "R2": round(float(r2), 4),
    }

    logger.info("Model metrics: %s", metrics)
    return metrics


def get_feature_importance(
    model: object,
    feature_names: list[str],
) -> pd.DataFrame:
    """Extract feature importances from a tree-based model.

    Args:
        model: Fitted model with ``feature_importances_`` attribute.
        feature_names: Ordered list of feature names.

    Returns:
        DataFrame with Feature and Importance columns, sorted descending.
    """
    if not hasattr(model, "feature_importances_"):
        raise AttributeError("Model does not expose feature_importances_")

    importance = pd.DataFrame(
        {"Feature": feature_names, "Importance": model.feature_importances_}
    ).sort_values("Importance", ascending=False).reset_index(drop=True)

    logger.info("Extracted importance for %d features", len(importance))
    return importance


def actual_vs_predicted_df(
    y_test: pd.Series,
    predictions: np.ndarray,
) -> pd.DataFrame:
    """Build an actual-vs-predicted comparison DataFrame.

    Args:
        y_test: True target values.
        predictions: Model predictions.

    Returns:
        DataFrame with Actual, Predicted and Error columns.
    """
    out = pd.DataFrame(
        {
            "Actual": y_test.values,
            "Predicted": predictions,
        }
    )
    out["Error"] = out["Actual"] - out["Predicted"]
    out["Abs Error"] = out["Error"].abs()
    return out


def residual_analysis_df(
    y_test: pd.Series,
    predictions: np.ndarray,
) -> pd.DataFrame:
    """Build a residual analysis DataFrame.

    Args:
        y_test: True target values.
        predictions: Model predictions.

    Returns:
        DataFrame with Actual, Predicted, Residual and Standardized
        Residual columns.
    """
    residuals = y_test.values - predictions
    std = residuals.std(ddof=0)
    standardized = residuals / std if std > 0 else residuals

    out = pd.DataFrame(
        {
            "Actual": y_test.values,
            "Predicted": predictions,
            "Residual": residuals,
            "Standardized Residual": standardized,
        }
    )
    return out


def run_predictive_modeling(df: pd.DataFrame) -> dict:
    """Run the full predictive modelling pipeline.

    Args:
        df: Cleaned DataFrame.

    Returns:
        Dictionary with keys ``rf_model``, ``rf_metrics``, ``rf_importance``,
        ``actual_vs_predicted``, ``residuals``, and optionally ``xgb_model``
        and ``xgb_metrics``.
    """
    logger.info("Starting predictive modelling pipeline")

    train_df, test_df = chronological_train_test_split(df)
    X_train, y_train = prepare_features(train_df)
    X_test, y_test = prepare_features(test_df)

    # Align feature columns between train and test.
    common_cols = list(set(X_train.columns) & set(X_test.columns))
    X_train = X_train[common_cols]
    X_test = X_test[common_cols]

    rf_model = train_random_forest(X_train, y_train)
    rf_metrics = evaluate_model(rf_model, X_test, y_test)
    rf_importance = get_feature_importance(rf_model, common_cols)

    rf_predictions = rf_model.predict(X_test)
    avp = actual_vs_predicted_df(y_test, rf_predictions)
    residuals = residual_analysis_df(y_test, rf_predictions)

    result: dict = {
        "rf_model": rf_model,
        "rf_metrics": rf_metrics,
        "rf_importance": rf_importance,
        "actual_vs_predicted": avp,
        "residuals": residuals,
    }

    xgb_model = train_xgboost(X_train, y_train)
    if xgb_model is not None:
        xgb_metrics = evaluate_model(xgb_model, X_test, y_test)
        result["xgb_model"] = xgb_model
        result["xgb_metrics"] = xgb_metrics

    logger.info("Predictive modelling pipeline complete")
    return result
