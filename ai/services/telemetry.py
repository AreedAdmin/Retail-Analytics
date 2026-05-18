"""
AI telemetry — prompt categorisation + performance logging.
============================================================
Every AI call routed through narrative_service records one JSON line to
ai/services/telemetry_log.jsonl with:

    timestamp, source (chat/summarise/narrative), category (intent bucket),
    backend, ttft_ms, tps, total_ms, prompt_tokens, completion_tokens,
    success, prompt_excerpt

Module 11 (AI Analytics) reads this log to show prompt-mix and AI
performance (TTFT, TPS, latency, success rate) by category/backend/source.

Recording is best-effort and never raises into the request path.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

logger = logging.getLogger(__name__)

LOG_PATH = Path(__file__).resolve().parent / "telemetry_log.jsonl"

# ── Prompt categorisation (rule-based, deterministic) ────────────────────────

CATEGORIES = [
    "Pricing & Elasticity",
    "Scenario / What-if",
    "Promotion",
    "Forecasting",
    "Model Reliability",
    "Overview / KPIs",
    "General / Other",
]

_KEYWORDS = [
    ("Scenario / What-if",
     ("what if", "what-if", "scenario", "simulate", "price change",
      "increase price", "decrease price", "raise price", "cut price",
      "+10", "-10", "%")),
    ("Pricing & Elasticity",
     ("elasticity", "elastic", "inelastic", "price sensitiv", "log-log",
      "pricing power", "demand curve", "price point")),
    ("Promotion",
     ("promo", "promotion", "lift", "discount", "deal", "feature",
      "incremental sales", "responder")),
    ("Forecasting",
     ("forecast", "predict", "future", "demand forecast", "next week",
      "projection", "trend", "seasonal")),
    ("Model Reliability",
     ("reliable", "reliability", "accuracy", "accurate", "trust", "mae",
      "rmse", "smape", "mape", "r2", "r²", "error", "confidence",
      "overfit", "valid")),
    ("Overview / KPIs",
     ("overview", "kpi", "total revenue", "how many", "number of",
      "summary", "sku count", "average price", "dataset", "headline")),
]

# Map AI scopes/sources directly to a category when there is no free text.
SCOPE_CATEGORY = {
    "price_elasticity": "Pricing & Elasticity",
    "scenario_simulator": "Scenario / What-if",
    "promotion_lift": "Promotion",
    "module_7": "Promotion",
    "demand_forecasting": "Forecasting",
    "overview": "Overview / KPIs",
}


def categorize(text: str) -> str:
    """Bucket a free-text prompt into one intent category."""
    t = (text or "").lower()
    if not t.strip():
        return "General / Other"
    for cat, kws in _KEYWORDS:
        if any(k in t for k in kws):
            return cat
    return "General / Other"


def categorize_scope(scope: str, fallback_text: str = "") -> str:
    """Category for a scope-driven call (chat scope / summarise / narrative)."""
    if scope in SCOPE_CATEGORY:
        return SCOPE_CATEGORY[scope]
    base = scope.split(":")[-1] if scope else ""
    if base in SCOPE_CATEGORY:
        return SCOPE_CATEGORY[base]
    return categorize(fallback_text or scope)


# ── Recording ────────────────────────────────────────────────────────────────

def record(source: str, category: str, metrics: Dict[str, Any],
           prompt_excerpt: str = "") -> None:
    """Append one telemetry event. Best-effort; never raises."""
    try:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "source": source,
            "category": category,
            "backend": metrics.get("backend"),
            "success": metrics.get("success"),
            "ttft_ms": metrics.get("ttft_ms"),
            "tps": metrics.get("tps"),
            "total_ms": metrics.get("total_ms"),
            "prompt_tokens": metrics.get("prompt_tokens"),
            "completion_tokens": metrics.get("completion_tokens"),
            "native_timing": metrics.get("native_timing", False),
            "prompt_excerpt": (prompt_excerpt or "")[:200],
        }
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:  # pragma: no cover - telemetry must never break a call
        logger.exception("telemetry record failed")


# ── Reading / aggregation ────────────────────────────────────────────────────

def load_events() -> pd.DataFrame:
    """All recorded events as a DataFrame (empty if none yet)."""
    if not LOG_PATH.exists():
        return pd.DataFrame()
    rows: List[dict] = []
    for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    df = pd.DataFrame(rows)
    if not df.empty and "timestamp" in df:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    return df


def _agg(df: pd.DataFrame) -> Dict[str, Any]:
    def _med(col):
        s = pd.to_numeric(df.get(col), errors="coerce").dropna()
        return round(float(s.median()), 1) if not s.empty else None

    def _mean(col):
        s = pd.to_numeric(df.get(col), errors="coerce").dropna()
        return round(float(s.mean()), 2) if not s.empty else None

    succ = df.get("success")
    return {
        "n_calls": int(len(df)),
        "success_rate": (round(100.0 * succ.mean(), 1)
                         if succ is not None and len(df) else None),
        "median_ttft_ms": _med("ttft_ms"),
        "median_total_ms": _med("total_ms"),
        "avg_tps": _mean("tps"),
        "avg_completion_tokens": _mean("completion_tokens"),
    }


def summary_stats(df: pd.DataFrame = None) -> Dict[str, Any]:
    """Headline KPIs + breakdowns by category / backend / source."""
    if df is None:
        df = load_events()
    if df.empty:
        return {"overall": {"n_calls": 0}, "by_category": {},
                "by_backend": {}, "by_source": {}}
    out: Dict[str, Any] = {"overall": _agg(df)}
    for dim in ("category", "backend", "source"):
        if dim in df:
            out[f"by_{dim}"] = {
                str(k): _agg(g) for k, g in df.groupby(dim)
            }
        else:
            out[f"by_{dim}"] = {}
    return out
