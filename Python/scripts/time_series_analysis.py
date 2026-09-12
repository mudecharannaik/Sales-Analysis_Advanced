"""Time series analysis: decomposition, forecasting and anomaly detection."""

from __future__ import annotations

import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose

from config import PROPHET_AVAILABLE, get_logger

logger = get_logger(__name__)


def monthly_sales_series(df: pd.DataFrame) -> pd.Series:
    """Build a monthly Sales time series indexed by period."""
    if "Order Date" not in df.columns:
        raise KeyError("Order Date required")
    ts = df.set_index("Order Date")["Sales"].resample("ME").sum()
    ts = ts.asfreq("ME").interpolate()
    logger.info("Monthly sales series: %d points", len(ts))
    return ts


def decompose_series(series: pd.Series, period: int = 12, model: str = "additive"):
    """Seasonal decomposition (trend/seasonal/residual)."""
    result = seasonal_decompose(series, model=model, period=period, extrapolate_trend="freq")
    logger.info("Decomposition complete (model=%s, period=%d)", model, period)
    return result


def forecast_arima(series: pd.Series, steps: int = 12, order: tuple = (1, 1, 1)):
    """Fit an ARIMA model and produce a forward forecast with CI."""
    from statsmodels.tsa.arima.model import ARIMA

    model = ARIMA(series, order=order).fit()
    forecast = model.get_forecast(steps=steps)
    mean = forecast.predicted_mean
    ci = forecast.conf_int()
    future_index = pd.date_range(series.index[-1] + pd.offsets.MonthEnd(1), periods=steps, freq="ME")
    out = pd.DataFrame(
        {
            "forecast": mean.values,
            "lower": ci.iloc[:, 0].values,
            "upper": ci.iloc[:, 1].values,
        },
        index=future_index,
    )
    logger.info("ARIMA%s forecast produced for %d steps", order, steps)
    return out, model


def forecast_prophet(series: pd.Series, steps: int = 12):
    """Fit a Prophet model (requires the optional ``prophet`` package)."""
    if not PROPHET_AVAILABLE:
        raise ImportError("prophet is not installed; install it to use this forecast.")
    from prophet import Prophet

    dfp = pd.DataFrame({"ds": series.index, "y": series.values}).reset_index(drop=True)
    m = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
    m.fit(dfp)
    future = m.make_future_dataframe(periods=steps, freq="ME")
    fc = m.predict(future)
    out = fc[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(steps).reset_index(drop=True)
    logger.info("Prophet forecast produced for %d steps", steps)
    return out, m


def detect_anomalies(series: pd.Series, z_threshold: float = 3.0) -> pd.Series:
    """Flag time-series anomalies from decomposition residuals."""
    decomp = decompose_series(series)
    resid = decomp.resid.dropna()
    z = (resid - resid.mean()).abs() / resid.std(ddof=0)
    flags = z > z_threshold
    logger.info("Detected %d anomalies in %d points", int(flags.sum()), len(resid))
    return flags


def run_time_series_pipeline(df: pd.DataFrame, steps: int = 12) -> dict:
    """Convenience orchestrator returning all time-series artefacts."""
    series = monthly_sales_series(df)
    decomp = decompose_series(series)
    arima_fc, arima_model = forecast_arima(series, steps=steps)
    anomalies = detect_anomalies(series)
    result = {
        "series": series,
        "decomposition": decomp,
        "arima_forecast": arima_fc,
        "arima_model": arima_model,
        "anomalies": anomalies,
    }
    if PROPHET_AVAILABLE:
        try:
            prophet_fc, prophet_model = forecast_prophet(series, steps=steps)
            result["prophet_forecast"] = prophet_fc
            result["prophet_model"] = prophet_model
        except Exception as exc:  # noqa: BLE001
            logger.warning("Prophet forecast failed: %s", exc)
    return result
