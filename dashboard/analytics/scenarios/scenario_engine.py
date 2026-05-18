# AI-assisted: reviewed by team
"""What-if scenario engine from elasticity estimates."""

import json
from pathlib import Path

import pandas as pd

from dashboard.analytics.common.kpi_definitions import KPIThresholds

REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUTS_DIR = REPO_ROOT / "dashboard" / "analytics" / "scenarios" / "outputs"
CONTEXT_PATH = OUTPUTS_DIR / "ai_context_module5.json"

DEFAULT_SCENARIOS = KPIThresholds.DEFAULT_PRICE_SCENARIOS


def run_scenarios(
    elasticity_df: pd.DataFrame,
    df: pd.DataFrame,
    price_changes: list[float] | None = None,
) -> pd.DataFrame:
    """
    Project demand and revenue change per SKU for each price-change scenario.
    Uses constant-elasticity approximation: %ΔQ ≈ elasticity × %ΔP.
    """
    if price_changes is None:
        price_changes = DEFAULT_SCENARIOS

    baseline = (
        df.groupby("sku_id")
        .agg(baseline_demand=("demand_units", "mean"), baseline_price=("price", "mean"))
        .reset_index()
    )
    merged = elasticity_df.merge(baseline, on="sku_id", how="inner")

    rows = []
    for _, row in merged.iterrows():
        e = row["elasticity_value"]
        for pct in price_changes:
            demand_chg = e * pct
            revenue_chg = ((1 + demand_chg / 100) * (1 + pct / 100) - 1) * 100
            rows.append({
                "sku_id": int(row["sku_id"]),
                "scenario_name": f"price_change_{pct:+.0f}pct".replace("+", "plus").replace("-", "minus"),
                "price_change_pct": float(pct),
                "demand_change_pct": round(demand_chg, 2),
                "revenue_change_pct": round(revenue_chg, 2),
                "baseline_demand": round(row["baseline_demand"], 2),
                "baseline_price": round(row["baseline_price"], 2),
            })
    return pd.DataFrame(rows)


def aggregate_scenario(scenario_df: pd.DataFrame, price_change_pct: float) -> dict:
    """Portfolio-level totals for one scenario."""
    sub = scenario_df[scenario_df["price_change_pct"] == price_change_pct]
    if sub.empty:
        return {}
    w = sub["baseline_demand"] * sub["baseline_price"]
    w_sum = w.sum()
    if w_sum == 0:
        return {}
    avg_demand_chg = float((sub["demand_change_pct"] * w).sum() / w_sum)
    avg_revenue_chg = float((sub["revenue_change_pct"] * w).sum() / w_sum)
    return {
        "price_change_pct": price_change_pct,
        "weighted_demand_change_pct": round(avg_demand_chg, 2),
        "weighted_revenue_change_pct": round(avg_revenue_chg, 2),
        "num_skus": int(sub["sku_id"].nunique()),
    }


def write_scenario_context(scenario_df: pd.DataFrame) -> None:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    summaries = [
        aggregate_scenario(scenario_df, pct)
        for pct in DEFAULT_SCENARIOS
    ]
    summaries = [s for s in summaries if s]
    best = max(summaries, key=lambda s: s["weighted_revenue_change_pct"]) if summaries else {}
    worst = min(summaries, key=lambda s: s["weighted_revenue_change_pct"]) if summaries else {}
    payload = {
        "module_name": "module_5_scenarios",
        "chart_id": "scenario_summary",
        "metrics": {
            "scenarios_computed": len(summaries),
            "best_revenue_scenario_pct": best.get("price_change_pct"),
            "best_revenue_change_pct": best.get("weighted_revenue_change_pct"),
            "worst_revenue_scenario_pct": worst.get("price_change_pct"),
            "worst_revenue_change_pct": worst.get("weighted_revenue_change_pct"),
        },
        "key_findings": [
            f"Best portfolio revenue scenario: {best.get('price_change_pct')}% price change "
            f"→ {best.get('weighted_revenue_change_pct')}% revenue",
            f"Worst portfolio revenue scenario: {worst.get('price_change_pct')}% price change "
            f"→ {worst.get('weighted_revenue_change_pct')}% revenue",
        ],
    }
    with open(CONTEXT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
