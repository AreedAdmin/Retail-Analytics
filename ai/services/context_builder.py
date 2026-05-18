"""
Context builder — grounds the AI in real model/data outputs.
============================================================
Every AI answer in the dashboard is built from an `AIContextPayload`
(see dashboard/analytics/common/schemas.py): a compact JSON snapshot of
*explicit numbers* the LLM is allowed to cite. The model is instructed to
use nothing else, which is the project's core anti-hallucination guardrail.

Sources read here (all already produced by the ML pods):
    - data/data_raw.csv                          (via DataLoader)
    - ml/promotions/sku_lift_summary.csv
    - ml/promotions/ai_context_module7.json
    - ml/ml_forecasting/outputs/test_summary.csv
    - ml/ml_forecasting/outputs/per_sku_metrics.csv

Nothing here calls an LLM; it only assembles structured context dicts.
"""

from __future__ import annotations

import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
PROMO_SUMMARY = REPO_ROOT / "ml" / "promotions" / "sku_lift_summary.csv"
PROMO_CONTEXT = REPO_ROOT / "ml" / "promotions" / "ai_context_module7.json"
FORECAST_SUMMARY = REPO_ROOT / "ml" / "ml_forecasting" / "outputs" / "test_summary.csv"
FORECAST_PER_SKU = REPO_ROOT / "ml" / "ml_forecasting" / "outputs" / "per_sku_metrics.csv"


def _safe_read_csv(path: Path) -> pd.DataFrame:
    try:
        if path.exists():
            return pd.read_csv(path)
    except Exception as e:  # pragma: no cover - defensive
        logger.warning("Could not read %s: %s", path, e)
    return pd.DataFrame()


# ── Per-module context builders ──────────────────────────────────────────────

def build_overview_context() -> Dict[str, Any]:
    """Headline KPIs from the raw dataset (Module 1 grounding)."""
    metrics: Dict[str, Any] = {}
    findings: List[str] = []
    try:
        from dashboard.analytics.common.data_loader import get_data_loader

        stats = get_data_loader().get_summary_stats()
        metrics = {
            "num_skus": int(stats["num_skus"]),
            "num_periods": int(stats["num_periods"]),
            "num_records": int(stats["num_records"]),
            "total_revenue": round(float(stats["total_revenue"]), 2),
            "total_demand_units": round(float(stats["total_demand_units"]), 2),
            "avg_price": round(float(stats["avg_price"]), 2),
            "num_promotions": int(stats["num_promotions"]),
            "price_min": round(float(stats["price_range"]["min"]), 2),
            "price_max": round(float(stats["price_range"]["max"]), 2),
        }
        findings = [
            f"Dataset covers {metrics['num_skus']} SKUs over "
            f"{metrics['num_periods']} weekly periods.",
            f"Total revenue is {metrics['total_revenue']:,} across "
            f"{metrics['total_demand_units']:,} demand units.",
            f"{metrics['num_promotions']} promoted SKU-weeks recorded.",
        ]
    except Exception as e:
        logger.warning("overview context failed: %s", e)
        findings = ["Overview metrics unavailable."]
    return {
        "module_name": "overview",
        "chart_id": "kpi_summary",
        "metrics": metrics,
        "key_findings": findings,
    }


def build_promotion_context() -> Dict[str, Any]:
    """Promotion-lift context from the Module 7 model outputs."""
    if PROMO_CONTEXT.exists():
        try:
            ctx = json.loads(PROMO_CONTEXT.read_text())
            kf = ctx.get("key_findings", {})
            if isinstance(kf, dict):  # flatten to list[str] per schema
                flat: List[str] = []
                for sku in kf.get("top_5_lift_skus", [])[:5]:
                    flat.append(
                        f"Top responder SKU {sku['sku_id']}: "
                        f"{sku['mean_lift_pct']}% lift "
                        f"({sku['n_promo_weeks']} promo weeks)."
                    )
                for sku in kf.get("bottom_5_lift_skus", [])[:5]:
                    flat.append(
                        f"Weak responder SKU {sku['sku_id']}: "
                        f"{sku['mean_lift_pct']}% lift."
                    )
                flat.append(
                    f"{kf.get('high_performers_n', 0)} high performers, "
                    f"{kf.get('moderate_lift_n', 0)} moderate, "
                    f"{kf.get('negligible_lift_n', 0)} negligible."
                )
                ctx["key_findings"] = flat
            return ctx
        except Exception as e:
            logger.warning("promo context json failed: %s", e)

    df = _safe_read_csv(PROMO_SUMMARY)
    if df.empty:
        return {
            "module_name": "promotion_lift",
            "chart_id": "lift_model_summary",
            "metrics": {},
            "key_findings": ["Promotion lift outputs unavailable."],
        }
    top = df.sort_values("mean_lift_pct", ascending=False).head(5)
    return {
        "module_name": "promotion_lift",
        "chart_id": "lift_model_summary",
        "metrics": {
            "num_skus": int(df["sku_id"].nunique()),
            "median_lift_pct": round(float(df["mean_lift_pct"].median()), 2),
            "max_lift_pct": round(float(df["mean_lift_pct"].max()), 2),
        },
        "key_findings": [
            f"SKU {r.sku_id}: {round(r.mean_lift_pct, 2)}% mean lift "
            f"({int(r.n_promo_weeks)} promo weeks)."
            for r in top.itertuples()
        ],
    }


def build_forecast_context() -> Dict[str, Any]:
    """Demand-forecast accuracy context from the Module 6 model outputs."""
    summary = _safe_read_csv(FORECAST_SUMMARY)
    per_sku = _safe_read_csv(FORECAST_PER_SKU)
    if summary.empty:
        return {
            "module_name": "demand_forecasting",
            "chart_id": "forecast_accuracy",
            "metrics": {},
            "key_findings": ["Forecast outputs unavailable."],
        }
    row = summary.iloc[0]
    metrics = {
        "model_name": str(row["model_name"]),
        "test_mae": round(float(row["MAE"]), 2),
        "test_rmse": round(float(row["RMSE"]), 2),
        "test_mape_pct": round(float(row["MAPE"]), 2),
        "coverage_80_pct": round(float(row["cov80"]), 2),
        "coverage_95_pct": round(float(row["cov95"]), 2),
        "n_test_points": int(row["n_test"]),
    }
    findings = [
        f"{metrics['model_name']} test MAE {metrics['test_mae']} units, "
        f"MAPE {metrics['test_mape_pct']}%.",
        f"95% prediction interval covers "
        f"{metrics['coverage_95_pct']}% of actuals.",
    ]
    if not per_sku.empty:
        best = per_sku.sort_values("MAE").head(3)
        findings.append(
            "Most accurate SKUs (lowest MAE): "
            + ", ".join(f"SKU {int(r.sku)} ({round(r.MAE, 1)})" for r in best.itertuples())
            + "."
        )
    return {
        "module_name": "demand_forecasting",
        "chart_id": "forecast_accuracy",
        "metrics": metrics,
        "key_findings": findings,
    }


# ── Registry / aggregation ───────────────────────────────────────────────────

_BUILDERS = {
    "overview": build_overview_context,
    "promotion_lift": build_promotion_context,
    "demand_forecasting": build_forecast_context,
}

SCOPE_LABELS = {
    "overview": "Overview KPIs",
    "promotion_lift": "Promotion Lift Model",
    "demand_forecasting": "Demand Forecasting",
}


def available_scopes() -> List[str]:
    return list(_BUILDERS.keys())


def build_context(scope: str) -> Dict[str, Any]:
    """Build a single module's context (scope key from `available_scopes`)."""
    builder = _BUILDERS.get(scope)
    if builder is None:
        return {
            "module_name": scope,
            "chart_id": "unknown",
            "metrics": {},
            "key_findings": [f"No context builder for scope '{scope}'."],
        }
    return builder()


def build_multi_context(scopes: List[str]) -> Dict[str, Any]:
    """Combine several modules' contexts into one payload (multi-select)."""
    scopes = [s for s in scopes if s in _BUILDERS] or list(_BUILDERS.keys())
    combined: Dict[str, Any] = {
        "module_name": "+".join(scopes),
        "chart_id": "multi_module",
        "metrics": {},
        "key_findings": [],
    }
    for s in scopes:
        c = build_context(s)
        combined["metrics"][s] = c.get("metrics", {})
        combined["key_findings"].extend(
            f"[{SCOPE_LABELS.get(s, s)}] {f}" for f in c.get("key_findings", [])
        )
    return combined
