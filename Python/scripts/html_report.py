"""HTML report and dashboard generator.

Generates interactive HTML dashboard and report from analysis results.
Templates are loaded from the html/ directory and populated with data.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from config import (
    HTML_DIR,
    OUTPUT_DIR,
    PROJECT_ROOT,
    VISUALIZATION_DIR,
    get_logger,
)

logger = get_logger(__name__)


def _get_skill_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _find_template(name: str) -> Path:
    candidates = [
        _get_skill_root() / "html" / name,
        HTML_DIR / name,
        _get_skill_root().parent / "Ai Skill" / "html" / name,
        Path(__file__).resolve().parent.parent.parent / "Ai Skill" / "html" / name,
        Path(__file__).resolve().parent.parent / "html" / name,
    ]
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]


def _fmt_number(value: Any, decimals: int = 2) -> str:
    try:
        return f"{float(value):,.{decimals}f}"
    except (TypeError, ValueError):
        return str(value)


def _get_metric(df: pd.DataFrame, candidates: list[str]) -> Any:
    for col in candidates:
        if col in df.columns:
            return df[col]
    return None


def _build_dashboard_context(
    df: pd.DataFrame,
    quality: dict | None = None,
    stats: pd.DataFrame | None = None,
    customer: dict | None = None,
    product: dict | None = None,
    geo: dict | None = None,
    model: dict | None = None,
    ts: dict | None = None,
) -> dict:
    ctx: dict[str, Any] = {
        "generated_at": datetime.now().isoformat(),
        "total_records": len(df),
        "date_range": None,
        "total_sales": None,
        "total_profit": None,
        "margin": None,
        "unique_customers": None,
        "unique_products": None,
        "unique_orders": None,
        "kpi_cards": [],
        "charts": [],
        "tables": {},
    }

    date_col = next((c for c in ["Order Date", "order_date", "date"] if c in df.columns), None)
    sales_col = next((c for c in ["Sales", "sales", "revenue"] if c in df.columns), None)
    profit_col = next((c for c in ["Profit", "profit", "net"] if c in df.columns), None)
    cust_col = next((c for c in ["Customer ID", "customer_id"] if c in df.columns), None)
    prod_col = next((c for c in ["Product ID", "product_id"] if c in df.columns), None)
    order_col = next((c for c in ["Order ID", "order_id"] if c in df.columns), None)

    if date_col:
        ctx["date_range"] = f"{df[date_col].min():%Y-%m-%d} to {df[date_col].max():%Y-%m-%d}"
    if sales_col:
        ctx["total_sales"] = _fmt_number(df[sales_col].sum())
    if profit_col:
        ctx["total_profit"] = _fmt_number(df[profit_col].sum())
    if sales_col and profit_col and df[sales_col].sum() != 0:
        ctx["margin"] = _fmt_number(100 * df[profit_col].sum() / df[sales_col].sum())
    if cust_col:
        ctx["unique_customers"] = _fmt_number(df[cust_col].nunique(), 0)
    if prod_col:
        ctx["unique_products"] = _fmt_number(df[prod_col].nunique(), 0)
    if order_col:
        ctx["unique_orders"] = _fmt_number(df[order_col].nunique(), 0)

    ctx["kpi_cards"] = [
        {"title": "Total Records", "value": _fmt_number(ctx["total_records"], 0), "icon": "bi-table", "color": "primary"},
        {"title": "Total Sales", "value": ctx["total_sales"] or "--", "icon": "bi-currency-dollar", "color": "success"},
        {"title": "Total Profit", "value": ctx["total_profit"] or "--", "icon": "bi-graph-up", "color": "info"},
        {"title": "Margin", "value": f"{ctx['margin'] or '--'}%", "icon": "bi-percent", "color": "warning"},
    ]

    viz_dir = VISUALIZATION_DIR
    chart_map = [
        ("sales_trend.png", "Sales Trend", "Daily sales trend over time"),
        ("monthly_sales.png", "Monthly Sales", "Monthly aggregated sales"),
        ("category_sales_donut.png", "Category Sales", "Sales distribution by category"),
        ("correlation_heatmap.png", "Correlation Heatmap", "Numeric feature correlations"),
        ("subcategory_sales_bar.png", "Sub-Category Performance", "Top sub-categories by sales"),
        ("market_performance.png", "Market Performance", "Sales by market"),
        ("region_analysis.png", "Regional Analysis", "Sales by region"),
        ("ship_mode_analysis.png", "Ship Mode Analysis", "Sales by shipping mode"),
        ("discount_vs_profit_scatter.png", "Discount vs Profit", "Relationship between discount and profit"),
        ("rfm_segments.png", "Customer Segments", "RFM customer segmentation"),
        ("pareto_chart.png", "Pareto Analysis", "80/20 product concentration"),
        ("bubble_chart.png", "Bubble Chart", "Sales vs Profit vs Quantity"),
    ]

    charts = []
    for filename, title, desc in chart_map:
        path = viz_dir / filename
        if path.exists():
            charts.append({
                "title": title,
                "description": desc,
                "path": f"../../Visualizations/{filename}",
            })
    ctx["charts"] = charts

    if customer:
        ctx["tables"]["rfm"] = customer.get("rfm", pd.DataFrame()).head(10).to_dict(orient="records")
        ctx["tables"]["top_customers"] = customer.get("top_sales", pd.DataFrame()).head(10).to_dict(orient="records")

    if product:
        ctx["tables"]["category_performance"] = product.get("category", pd.DataFrame()).to_dict(orient="records")

    if geo:
        ctx["tables"]["top_countries"] = geo.get("country", pd.DataFrame()).head(10).to_dict(orient="records")

    return ctx


def _build_report_context(
    df: pd.DataFrame,
    quality: dict | None = None,
    stats: pd.DataFrame | None = None,
    customer: dict | None = None,
    product: dict | None = None,
    geo: dict | None = None,
    model: dict | None = None,
    ts: dict | None = None,
) -> dict:
    ctx: dict[str, Any] = {
        "generated_at": datetime.now().isoformat(),
        "total_records": len(df),
        "date_range": None,
        "total_sales": None,
        "total_profit": None,
        "margin": None,
        "unique_customers": None,
        "unique_products": None,
        "unique_orders": None,
        "quality_score": None,
        "model_metrics": {},
        "statistical_tests": [],
        "segments": [],
        "recommendations": [],
    }

    date_col = next((c for c in ["Order Date", "order_date", "date"] if c in df.columns), None)
    sales_col = next((c for c in ["Sales", "sales", "revenue"] if c in df.columns), None)
    profit_col = next((c for c in ["Profit", "profit", "net"] if c in df.columns), None)
    cust_col = next((c for c in ["Customer ID", "customer_id"] if c in df.columns), None)
    prod_col = next((c for c in ["Product ID", "product_id"] if c in df.columns), None)
    order_col = next((c for c in ["Order ID", "order_id"] if c in df.columns), None)

    if date_col:
        ctx["date_range"] = f"{df[date_col].min():%Y-%m-%d} to {df[date_col].max():%Y-%m-%d}"
    if sales_col:
        ctx["total_sales"] = _fmt_number(df[sales_col].sum())
    if profit_col:
        ctx["total_profit"] = _fmt_number(df[profit_col].sum())
    if sales_col and profit_col and df[sales_col].sum() != 0:
        ctx["margin"] = _fmt_number(100 * df[profit_col].sum() / df[sales_col].sum())
    if cust_col:
        ctx["unique_customers"] = _fmt_number(df[cust_col].nunique(), 0)
    if prod_col:
        ctx["unique_products"] = _fmt_number(df[prod_col].nunique(), 0)
    if order_col:
        ctx["unique_orders"] = _fmt_number(df[order_col].nunique(), 0)

    if quality and isinstance(quality, dict):
        profile = quality.get("profile", pd.DataFrame())
        if not profile.empty:
            missing_pct = profile.get("missing_pct", pd.Series())
            if not missing_pct.empty:
                ctx["quality_score"] = _fmt_number(100 - missing_pct.mean(), 1)

    if model and isinstance(model, dict):
        for m_name in ["rf_model", "xgb_model"]:
            m = model.get(m_name)
            if m and hasattr(m, "metrics"):
                ctx["model_metrics"][m_name] = m.metrics

    if stats is not None and not stats.empty:
        for _, row in stats.iterrows():
            ctx["statistical_tests"].append({
                "name": row.get("test", ""),
                "statistic": row.get("statistic", ""),
                "p_value": row.get("p_value", ""),
                "conclusion": row.get("conclusion", ""),
            })

    if customer and isinstance(customer, dict):
        rfm = customer.get("rfm", pd.DataFrame())
        if not rfm.empty and "Segment" in rfm.columns:
            ctx["segments"] = rfm["Segment"].value_counts().to_dict()

    ctx["recommendations"] = [
        "Reduce discount depth on low-margin products where correlation is significant.",
        "Focus inventory and marketing on top-performing categories and Pareto products.",
        "Target high-value customer segments with retention programs.",
        "Optimize shipping modes by region to balance cost and satisfaction.",
        "Review loss-making products for discontinuation or repricing.",
        "Implement seasonal planning based on time-series decomposition.",
    ]

    return ctx


def _render_template(template_name: str, context: dict) -> str:
    template_path = _find_template(template_name)
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    html = template_path.read_text(encoding="utf-8")
    for key, value in context.items():
        placeholder = f"{{{{{key}}}}}"
        if isinstance(value, (dict, list)):
            html = html.replace(placeholder, json.dumps(value, default=str))
        else:
            html = html.replace(placeholder, str(value) if value is not None else "--")
    return html


def _build_data_payload(
    df: pd.DataFrame,
    quality: dict | None = None,
    stats: pd.DataFrame | None = None,
    customer: dict | None = None,
    product: dict | None = None,
    geo: dict | None = None,
    model: dict | None = None,
    ts: dict | None = None,
) -> dict:
    """Build the JSON payload consumed by assets/js/charts.js."""
    import numpy as np

    date_col = next((c for c in ["Order Date", "order_date", "date"] if c in df.columns), None)
    sales_col = next((c for c in ["Sales", "sales", "revenue"] if c in df.columns), None)
    profit_col = next((c for c in ["Profit", "profit", "net"] if c in df.columns), None)
    cust_col = next((c for c in ["Customer ID", "customer_id", "Customer Name"] if c in df.columns), None)
    order_col = next((c for c in ["Order ID", "order_id"] if c in df.columns), None)
    cat_col = next((c for c in ["Category", "category"] if c in df.columns), None)
    mkt_col = next((c for c in ["Market", "market"] if c in df.columns), None)
    region_col = next((c for c in ["Region", "region"] if c in df.columns), None)

    payload: dict[str, Any] = {"generated_at": datetime.now().isoformat()}

    total_sales = float(df[sales_col].sum()) if sales_col else 0.0
    total_profit = float(df[profit_col].sum()) if profit_col else 0.0
    margin = round(100 * total_profit / total_sales, 2) if total_sales else None
    payload["kpis"] = {
        "records": len(df),
        "total_sales": round(total_sales, 2),
        "total_profit": round(total_profit, 2),
        "margin": margin,
        "orders": int(df[order_col].nunique()) if order_col else len(df),
        "customers": int(df[cust_col].nunique()) if cust_col else None,
    }

    # Monthly trend
    monthly = []
    if date_col and sales_col:
        d = df.copy()
        d[date_col] = pd.to_datetime(d[date_col], errors="coerce")
        d = d.dropna(subset=[date_col])
        agg_spec = {"sales": (sales_col, "sum")}
        if profit_col:
            agg_spec["profit"] = (profit_col, "sum")
        grp = d.set_index(date_col).resample("MS").agg(**agg_spec)
        for idx, row in grp.iterrows():
            monthly.append({
                "label": idx.strftime("%Y-%m"),
                "sales": round(float(row["sales"]), 2),
                "profit": round(float(row.get("profit", 0) or 0), 2),
            })
    payload["monthly"] = monthly

    def _agg_by(col, top_n=15):
        if not col or col not in df.columns or not sales_col:
            return []
        g = df.groupby(col)[sales_col].sum().sort_values(ascending=False).head(top_n)
        return [{"label": str(k), "sales": round(float(v), 2)} for k, v in g.items()]

    payload["category"] = _agg_by(cat_col)
    payload["market"] = _agg_by(mkt_col)
    payload["geo"] = _agg_by(region_col)

    # Scatter sample (Sales vs Profit)
    if sales_col and profit_col:
        sample = df[[sales_col, profit_col]].dropna()
        if len(sample) > 1000:
            sample = sample.sample(1000, random_state=42)
        payload["scatter"] = [
            {"x": round(float(r[0]), 2), "y": round(float(r[1]), 2)}
            for r in sample.itertuples(index=False)
        ]

    # Data explorer rows (cap at 500 for page weight)
    rows = []
    if order_col:
        cols_map = {
            "order_id": order_col,
            "date": date_col,
            "customer": cust_col,
            "category": cat_col,
            "sales": sales_col,
            "profit": profit_col,
            "region": region_col,
        }
        use_cols = list({v for v in cols_map.values() if v})
        sub = df[use_cols].copy()
        if date_col:
            sub[date_col] = pd.to_datetime(sub[date_col], errors="coerce").dt.strftime("%Y-%m-%d")
        sub = sub.head(500)
        inv = {v: k for k, v in cols_map.items() if v}
        for rec in sub.to_dict(orient="records"):
            out_row = {}
            for col, val in rec.items():
                key = inv[col]
                if key in ("sales", "profit") and val is not None:
                    try:
                        val = round(float(val), 2)
                    except (TypeError, ValueError):
                        pass
                out_row[key] = None if pd.isna(val) else val
            rows.append(out_row)
    payload["rows"] = rows

    # Data quality summary
    if quality and isinstance(quality, dict):
        profile = quality.get("profile", pd.DataFrame())
        missing_cells = duplicate_rows = score = None
        if isinstance(profile, pd.DataFrame) and not profile.empty:
            mp = profile.get("missing_pct")
            mc = profile.get("missing_count", profile.get("missing"))
            if mp is not None and hasattr(mp, "empty") and not mp.empty:
                score = round(100 - float(mp.mean()), 1)
            if mc is not None:
                try:
                    missing_cells = int(pd.to_numeric(mc, errors="coerce").fillna(0).sum())
                except Exception:
                    missing_cells = None
        duplicate_rows = quality.get("duplicate_rows")
        payload["quality"] = {
            "score": score,
            "missing_cells": missing_cells,
            "duplicate_rows": int(duplicate_rows) if duplicate_rows is not None else None,
        }

    # Statistical tests
    tests = []
    if stats is not None and hasattr(stats, "iterrows"):
        try:
            for _, row in stats.iterrows():
                tests.append({
                    "name": row.get("test", ""),
                    "statistic": row.get("statistic", ""),
                    "p_value": row.get("p_value", ""),
                    "conclusion": row.get("conclusion", ""),
                })
        except Exception:
            pass
    payload["statistical_tests"] = tests

    # Customer analytics
    if customer and isinstance(customer, dict):
        rfm = customer.get("rfm", pd.DataFrame())
        if isinstance(rfm, pd.DataFrame) and not rfm.empty and "Segment" in rfm.columns:
            payload["segments"] = {str(k): int(v) for k, v in rfm["Segment"].value_counts().items()}
    if cust_col and order_col:
        orders_per_cust = df.groupby(cust_col)[order_col].nunique()
        repeat = int((orders_per_cust > 1).sum())
        total_c = int(orders_per_cust.size)
        payload["repeat_customers"] = {
            "total_customers": total_c,
            "repeat_customers": repeat,
            "repeat_rate": round(100 * repeat / total_c, 1) if total_c else None,
            "avg_orders": round(float(orders_per_cust.mean()), 2),
        }

    # Product Pareto
    prod_col = next((c for c in ["Product ID", "product_id", "Product Name", "Sub-Category"]
                     if c in df.columns), None)
    if prod_col and sales_col:
        g = df.groupby(prod_col)[sales_col].sum().sort_values(ascending=False).head(15)
        cum_total = float(g.sum()) or 1.0
        cum = 0.0
        pareto = []
        for k, v in g.items():
            cum += float(v)
            pareto.append({"label": str(k), "sales": round(float(v), 2),
                           "cum_pct": round(100 * cum / cum_total, 1)})
        payload["pareto"] = pareto

    # Time series + forecast
    if ts and isinstance(ts, dict):
        hist = ts.get("monthly_sales", ts.get("history"))
        if isinstance(hist, (pd.Series, pd.DataFrame)) and not getattr(hist, "empty", True):
            s = hist if isinstance(hist, pd.Series) else hist.iloc[:, 0]
            payload["ts_trend"] = [
                {"label": idx.strftime("%Y-%m") if hasattr(idx, "strftime") else str(idx),
                 "sales": round(float(v), 2)}
                for idx, v in s.items()
            ]
        fc = ts.get("forecast")
        if isinstance(fc, (pd.Series, pd.DataFrame)) and not getattr(fc, "empty", True):
            s = fc if isinstance(fc, pd.Series) else fc.iloc[:, 0]
            payload["ts_forecast"] = [
                {"label": idx.strftime("%Y-%m") if hasattr(idx, "strftime") else str(idx),
                 "actual": None, "forecast": round(float(v), 2)}
                for idx, v in s.items()
            ]
            if payload.get("ts_trend"):
                actual_map = {t["label"]: t["sales"] for t in payload["ts_trend"]}
                for pt in payload["ts_forecast"]:
                    pt["actual"] = actual_map.get(pt["label"])

    # Model outputs
    if model and isinstance(model, dict):
        fi = model.get("feature_importance")
        items = []
        if fi is not None and hasattr(fi, "items"):
            items = list(fi.items())[:12]
        elif fi is not None and hasattr(fi, "iterrows"):
            try:
                items = [(r.iloc[0], r.iloc[1]) for _, r in fi.iterrows()][:12]
            except Exception:
                items = []
        payload["feature_importance"] = [
            {"label": str(k), "value": round(float(v), 4)} for k, v in items
        ]
        ap = model.get("actual_vs_predicted")
        if isinstance(ap, (pd.DataFrame, pd.Series)) and not getattr(ap, "empty", True):
            adf = ap if isinstance(ap, pd.DataFrame) else ap.to_frame()
            cols = list(adf.columns)
            if len(cols) >= 2:
                a_col, p_col = adf[cols[0]], adf[cols[1]]
                if len(adf) > 300:
                    idxs = np.random.RandomState(42).choice(len(adf), 300, replace=False)
                    a_col, p_col = a_col.iloc[idxs], p_col.iloc[idxs]
                payload["actual_vs_predicted"] = [
                    {"actual": round(float(x), 2), "predicted": round(float(y), 2)}
                    for x, y in zip(a_col, p_col)
                ]

    return payload


def _inject_report_data(html: str, payload: dict) -> str:
    """Embed the payload as an inline JSON script so charts work from file://."""
    json_str = json.dumps(payload, default=str).replace("</", "<\\/")
    tag = f'<script id="report-data" type="application/json">{json_str}</script>'
    marker = '<script id="report-data"'
    start = html.find(marker)
    if start != -1:
        end_tag = "</script>"
        end = html.find(end_tag, start)
        if end != -1:
            return html[:start] + tag + html[end + len(end_tag):]
    if "</head>" in html:
        return html.replace("</head>", tag + "\n</head>", 1)
    return html + tag


def _write_data_json(payload: dict) -> Path:
    out = HTML_DIR / "data.json"
    out.write_text(json.dumps(payload, default=str), encoding="utf-8")
    return out


def generate_dashboard(
    df: pd.DataFrame,
    quality: dict | None = None,
    stats: pd.DataFrame | None = None,
    customer: dict | None = None,
    product: dict | None = None,
    geo: dict | None = None,
    model: dict | None = None,
    ts: dict | None = None,
    output_name: str = "dashboard.html",
) -> str:
    context = _build_dashboard_context(df, quality, stats, customer, product, geo, model, ts)
    html = _render_template("dashboard.html", context)
    payload = _build_data_payload(df, quality, stats, customer, product, geo, model, ts)
    html = _inject_report_data(html, payload)
    _write_data_json(payload)
    out_path = HTML_DIR / output_name
    out_path.write_text(html, encoding="utf-8")
    logger.info("Dashboard saved to %s", out_path)
    return str(out_path)


def generate_report(
    df: pd.DataFrame,
    quality: dict | None = None,
    stats: pd.DataFrame | None = None,
    customer: dict | None = None,
    product: dict | None = None,
    geo: dict | None = None,
    model: dict | None = None,
    ts: dict | None = None,
    output_name: str = "report.html",
) -> str:
    context = _build_report_context(df, quality, stats, customer, product, geo, model, ts)
    html = _render_template("report.html", context)
    payload = _build_data_payload(df, quality, stats, customer, product, geo, model, ts)
    html = _inject_report_data(html, payload)
    _write_data_json(payload)
    out_path = HTML_DIR / output_name
    out_path.write_text(html, encoding="utf-8")
    logger.info("Report saved to %s", out_path)
    return str(out_path)


def generate_html(
    df: pd.DataFrame,
    quality: dict | None = None,
    stats: pd.DataFrame | None = None,
    customer: dict | None = None,
    product: dict | None = None,
    geo: dict | None = None,
    model: dict | None = None,
    ts: dict | None = None,
) -> dict:
    dash_path = generate_dashboard(df, quality, stats, customer, product, geo, model, ts)
    rep_path = generate_report(df, quality, stats, customer, product, geo, model, ts)
    return {"dashboard": dash_path, "report": rep_path}
